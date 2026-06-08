# Module 03 — Guidance, Navigation & Control (GNC)

> The crown-jewel module. This is the mathematics that senior state-estimation
> and controls engineers at Anduril, Shield AI, Skydio, and Skunk Works carry in
> their heads. Everything else in autonomy — perception, planning, mission logic —
> exists to feed numbers *into* the GNC loop and to consume the trajectory it
> produces. If you master this module, you understand the load-bearing wall of the
> field.
>
> **How to read this.** Work it with a pencil. Re-derive every boxed equation.
> Where a concept maps onto this repo's real code, you'll see an
> **⚓ Anchor** callout tying the abstract math to a concrete file in
> [`navigation/`](../navigation). The anchors are not decoration — they are the
> proof that the theory is the code.
>
> **Prerequisites:** [Module 01 — First Principles & Systems Engineering](01_first_principles_systems_engineering.md).
> **Companions:** [ML/AI Perception & Autonomy](../ML_AI_AUTONOMY_GUIDE.md) ·
> [Module 06 — Simulation, Test & Verification](06_simulation_test_verification.md).

---

## Table of Contents

0. [What GNC actually is](#0-what-gnc-actually-is)
1. [Reference frames & rotations](#1-reference-frames--rotations)
2. [Rigid-body dynamics & the equations of motion](#2-rigid-body-dynamics--the-equations-of-motion)
3. [Sensors & their error models](#3-sensors--their-error-models)
4. [Estimation theory — the spine](#4-estimation-theory--the-spine)
5. [Sensor fusion in practice](#5-sensor-fusion-in-practice)
6. [GPS-denied / vision-aided navigation](#6-gps-denied--vision-aided-navigation)
7. [Control theory](#7-control-theory)
8. [Guidance](#8-guidance)
9. [Putting it together — the full GNC loop](#9-putting-it-together--the-full-gnc-loop)
10. [Worked error-budget example](#10-worked-error-budget-example)
11. [Practice this week](#11-practice-this-week)
12. [Cross-links & further study](#12-cross-links--further-study)

---

## 0. What GNC actually is

GNC is three coupled questions, asked tens to hundreds of times per second:

| Letter | Question | Output | Repo / PX4 piece |
|---|---|---|---|
| **N**avigation | *Where am I, how am I oriented, and how fast am I moving?* | State estimate $\hat{\mathbf{x}}$ + covariance $P$ | PX4 **EKF2**; this repo's [`nav_state.py`](../navigation/nav_state.py) |
| **G**uidance | *Where should I go next, and along what path?* | Reference trajectory / setpoint $\mathbf{x}_{\text{ref}}(t)$ | PX4 navigator + this repo's mission layer |
| **C**ontrol | *What actuator commands drive me from where I am to where I should be?* | Motor / servo commands $\mathbf{u}$ | PX4 cascaded controllers + mixer |

The canonical loop:

```
        ┌─────────────────────────────────────────────────────────┐
        │                                                         │
   ┌────▼─────┐   x_ref   ┌─────────┐   u    ┌──────────┐  forces  │
   │ GUIDANCE ├──────────►│ CONTROL ├───────►│  PLANT   │          │
   └──────────┘           └─────────┘        │ (airframe)│         │
        ▲                      ▲             └────┬─────┘          │
        │                      │ x̂                │ true motion    │
        │                 ┌────┴──────┐           │                │
        └─────────────────┤ NAVIGATION│◄──────────┘  sensors       │
              mission      │ (estimator)│   IMU/GPS/cam/baro        │
                          └───────────┘                            │
                                                                   │
```

Each block runs at a different rate and the rates *cascade* (Section 9). The
inner control loops are fast and dumb; the outer guidance loops are slow and
smart. Navigation feeds everything. **A controller is only ever as good as the
state estimate it's closing the loop on** — which is why estimation, not control,
is the deepest part of this module.

---

## 1. Reference frames & rotations

You cannot do navigation until you can say *with respect to what*. Half of all
real GNC bugs are frame bugs: a sign flip, a transposed rotation, NED vs ENU,
body vs world. This section makes the bookkeeping exact.

### 1.1 The frames you must know cold

| Frame | Origin | Axes | Use |
|---|---|---|---|
| **ECI** (Earth-Centered Inertial) | Earth's center | Fixed to stars; non-rotating | Newton's laws hold here; orbital mechanics, raw gyro integration |
| **ECEF** (Earth-Centered Earth-Fixed) | Earth's center | Rotates *with* Earth; $x$→0°N/0°E, $z$→North pole | GNSS solutions are natively ECEF (e.g. WGS84) |
| **Geodetic** (LLA) | — | latitude $\phi$, longitude $\lambda$, height $h$ | Human-readable position; what a GPS reports |
| **NED** (North-East-Down) | A *local* tangent point | $x$→North, $y$→East, $z$→**Down** | The standard local navigation frame in aerospace |
| **ENU** (East-North-Up) | A local tangent point | $x$→East, $y$→North, $z$→Up | ROS / robotics convention; **mind the mismatch** |
| **Body (FRD)** | Vehicle CG | $x$→Forward, $y$→Right, $z$→Down | IMU, thrust, aero forces live here |

> **The single most expensive convention fact in this field:** PX4 and most of
> aerospace use **NED** for the world and **FRD** (Forward-Right-Down) for the
> body. ROS uses **ENU**/**FLU**. Mixing them silently negates your $z$ and swaps
> $x{\leftrightarrow}y$. Every external-vision integration has been bitten by this.

**⚓ Anchor — local NED.**
[`nav_state.py`](../navigation/nav_state.py) carries its entire state in a **local
NED tangent frame** anchored at the first known position (`set_origin`):
$$
\mathbf{x} = [\,p_n,\ p_e,\ p_d,\ v_n,\ v_e,\ v_d\,]^\top \quad (\text{m},\ \text{m/s}).
$$
The down axis is *positive down*, so altitude-above-origin is $-p_d$. This is also
exactly the frame PX4's `VISION_POSITION_ESTIMATE` expects, which is why
`estimate()` can hand the bridge $(p_n, p_e, p_d)$ with **no second conversion**.

### 1.2 The geodetic → local-tangent-plane problem

The Earth is (very nearly) an oblate ellipsoid. **WGS84** defines it with
semi-major axis $a = 6\,378\,137\,\text{m}$ and flattening
$f = 1/298.257223563$, giving eccentricity $e^2 = 2f - f^2$. Geodetic latitude
$\phi$ is the angle of the *surface normal*, not the angle from center — this
distinction matters at the meter level.

The rigorous geodetic→ECEF transform:
$$
\begin{aligned}
N(\phi) &= \frac{a}{\sqrt{1 - e^2 \sin^2\phi}} \quad (\text{prime vertical radius})\\
x &= (N + h)\cos\phi\cos\lambda\\
y &= (N + h)\cos\phi\sin\lambda\\
z &= \big(N(1 - e^2) + h\big)\sin\phi.
\end{aligned}
$$
ECEF→NED at a reference $(\phi_0,\lambda_0)$ is then a rotation by the
local-tangent matrix
$$
R_{e}^{n} =
\begin{bmatrix}
-\sin\phi_0\cos\lambda_0 & -\sin\phi_0\sin\lambda_0 & \cos\phi_0\\
-\sin\lambda_0 & \cos\lambda_0 & 0\\
-\cos\phi_0\cos\lambda_0 & -\cos\phi_0\sin\lambda_0 & -\sin\phi_0
\end{bmatrix}.
$$

For a vehicle operating within a few kilometers of its origin, this full
machinery is overkill. The **equirectangular (flat-Earth) approximation** treats
a small lat/lon patch as a flat plane:
$$
\boxed{\;
\begin{aligned}
p_n &= (\phi - \phi_0)\cdot R_{\text{deg}}\\
p_e &= (\lambda - \lambda_0)\cdot R_{\text{deg}}\cdot \cos\phi_0
\end{aligned}\;}
\qquad R_{\text{deg}} = \frac{\pi}{180}\,R_\oplus \approx 111\,320\ \text{m/deg}.
$$

The $\cos\phi_0$ factor is the meridian-convergence correction: lines of
longitude crowd together toward the poles, so one degree of east-displacement is
fewer meters at high latitude.

**⚓ Anchor — exact-inverse equirectangular.**
[`nav_state.py`](../navigation/nav_state.py)'s `ned_from_ll` / `ll_from_ned` use
exactly this, with one careful design choice: **both directions use the *origin*
latitude** for the east scale:

```python
cos_lat = math.cos(math.radians(origin_lat))   # not the query latitude
north = (lat - origin_lat) * _EARTH_M_PER_DEG
east  = (lon - origin_lon) * _EARTH_M_PER_DEG * cos_lat
```

Using the origin (not the moving point's) latitude makes `ll_from_ned` the
*exact* algebraic inverse of `ned_from_ll`. The residual model error is
sub-millimeter over the sub-kilometer working radius this airframe flies —
utterly negligible next to the *meters* of map-matching noise the filter already
absorbs. This is a textbook example of **matching model fidelity to the dominant
error source** (Module 01's first-principles discipline): don't drag in a
projection library to chase millimeters when your measurement noise is meters.

### 1.3 Attitude: three ways to represent orientation

Orientation is a point on the rotation group $SO(3)$ — the set of $3\times3$
matrices $R$ with $R^\top R = I$ and $\det R = +1$. There are three working
representations, each with a use and a failure mode.

#### (a) Euler angles — roll $\phi$, pitch $\theta$, yaw $\psi$

Three sequential rotations (aerospace uses the **3-2-1 / Z-Y-X** sequence:
yaw, then pitch, then roll). The body-to-NED direction cosine matrix is
$$
R_b^n = R_z(\psi)\,R_y(\theta)\,R_x(\phi).
$$
- **Pro:** intuitive, human-readable, what a pilot thinks in.
- **Con — gimbal lock:** at $\theta = \pm90°$ the roll and yaw axes align, a
  degree of freedom collapses, and the kinematic equations blow up:
$$
\begin{bmatrix}\dot\phi\\\dot\theta\\\dot\psi\end{bmatrix}
=
\begin{bmatrix}
1 & \sin\phi\tan\theta & \cos\phi\tan\theta\\
0 & \cos\phi & -\sin\phi\\
0 & \sin\phi\sec\theta & \cos\phi\sec\theta
\end{bmatrix}
\begin{bmatrix}p\\q\\r\end{bmatrix}.
$$
The $\tan\theta$ and $\sec\theta$ terms $\to\infty$ at $\theta=\pm90°$. For a
VTOL drone that pitches through 90° during transition, **Euler angles are a
landmine** — never integrate attitude in Euler form.

#### (b) Direction Cosine Matrix (DCM) — the rotation matrix itself

$R_b^n$ rotates a body-frame vector into NED: $\mathbf{v}^n = R_b^n\,\mathbf{v}^b$.
- **Pro:** no singularities, direct vector transforms, composition is matrix
  multiply.
- **Con:** 9 numbers for 3 DOF (redundant), and numerical integration drifts off
  the $R^\top R = I$ manifold, requiring periodic re-orthonormalization.

The kinematic propagation uses the **skew-symmetric** cross-product matrix of the
body rate $\boldsymbol\omega = [p,q,r]^\top$:
$$
[\boldsymbol\omega]_\times =
\begin{bmatrix}0 & -r & q\\ r & 0 & -p\\ -q & p & 0\end{bmatrix},
\qquad
\dot R_b^n = R_b^n\,[\boldsymbol\omega]_\times .
$$

#### (c) Quaternions — the production representation

A unit quaternion $\mathbf q = q_0 + q_1 i + q_2 j + q_3 k$, $\|\mathbf q\|=1$,
encodes a rotation of angle $\vartheta$ about unit axis $\hat{\mathbf n}$:
$$
\mathbf q = \Big[\cos\tfrac{\vartheta}{2},\ \hat{\mathbf n}\sin\tfrac{\vartheta}{2}\Big].
$$

**Quaternion algebra you must know:**

- **Hamilton product** (composition of rotations), with
  $\mathbf q = (w,\mathbf v)$:
$$
\mathbf q_1 \otimes \mathbf q_2
= \big(w_1 w_2 - \mathbf v_1\!\cdot\!\mathbf v_2,\;
  w_1\mathbf v_2 + w_2\mathbf v_1 + \mathbf v_1\!\times\!\mathbf v_2\big).
$$
  *Non-commutative* — rotation order matters, just like matrices.
- **Conjugate / inverse:** $\mathbf q^* = (w, -\mathbf v)$; for unit quaternions
  $\mathbf q^{-1} = \mathbf q^*$.
- **Rotating a vector:** $\mathbf v' = \mathbf q \otimes (0,\mathbf v) \otimes \mathbf q^*$.
- **Kinematics:** $\dot{\mathbf q} = \tfrac12\,\mathbf q \otimes (0,\boldsymbol\omega)$.
  Linear in $\mathbf q$, **no trig, no singularities.**
- **DCM from quaternion:**
$$
R(\mathbf q) =
\begin{bmatrix}
1-2(q_2^2+q_3^2) & 2(q_1q_2 - q_0q_3) & 2(q_1q_3 + q_0q_2)\\
2(q_1q_2 + q_0q_3) & 1-2(q_1^2+q_3^2) & 2(q_2q_3 - q_0q_1)\\
2(q_1q_3 - q_0q_2) & 2(q_2q_3 + q_0q_1) & 1-2(q_1^2+q_2^2)
\end{bmatrix}.
$$

**Why quaternions win in production (and why EKF2 uses them):**
1. **No gimbal lock** — they cover all of $SO(3)$ smoothly.
2. **Cheap, well-conditioned integration** — 4 numbers, linear kinematics, one
   renormalization (`q /= ‖q‖`) per step instead of Gram–Schmidt on a matrix.
3. **Numerically stable interpolation** (SLERP) for smooth attitude blending.

The price: $\mathbf q$ and $-\mathbf q$ represent the *same* rotation
(double cover), and the unit-norm constraint means a quaternion has only 3 DOF.
In a Kalman filter you therefore don't estimate the 4 quaternion components
directly — you estimate a 3-element **error rotation** $\delta\boldsymbol\theta$
in the tangent space and inject it (the **multiplicative EKF / MEKF** trick used
by EKF2): $\mathbf q \leftarrow \mathbf q \otimes \delta\mathbf q(\delta\boldsymbol\theta)$.

> **⚓ Anchor.** [`nav_state.py`](../navigation/nav_state.py) deliberately does
> **not** estimate attitude — it's a *position/velocity* filter and trusts PX4's
> EKF2 for orientation ("PX4 estimates yaw well even GPS-denied, from gyro + mag",
> per `set_yaw`'s docstring). It carries a scalar `yaw_deg` only to tag the vision
> pose. This is a deliberate **separation of concerns**: let the autopilot's
> full quaternion MEKF own attitude; let the companion own the GPS-denied
> position fusion. Knowing *where the attitude problem lives* is itself senior-level judgment.

#### (d) Small-angle approximation

For the tiny corrections inside a filter update, $\sin\vartheta\approx\vartheta$,
$\cos\vartheta\approx1$, and a rotation linearizes to
$$
R(\delta\boldsymbol\theta) \approx I + [\delta\boldsymbol\theta]_\times,
\qquad
\delta\mathbf q \approx \big[1,\ \tfrac12\delta\boldsymbol\theta\big].
$$
This is what makes the *error-state* formulation work: errors stay small, so the
nonlinear $SO(3)$ manifold looks locally like flat $\mathbb R^3$, and ordinary
linear-Gaussian Kalman math applies to the rotation error.

---

## 2. Rigid-body dynamics & the equations of motion

To estimate and control a vehicle you need its **plant model** — the differential
equations mapping forces and moments to motion.

### 2.1 The 6-DOF Newton–Euler equations

A rigid body has 6 degrees of freedom: 3 translational + 3 rotational. Newton's
and Euler's laws, written in the **body frame** (where inertia is constant), are:

**Translation** (force = mass × acceleration, with the Coriolis term from
working in a rotating frame):
$$
m\,(\dot{\mathbf v}^b + \boldsymbol\omega^b \times \mathbf v^b) = \mathbf F^b.
$$

**Rotation** (Euler's equation, with the gyroscopic coupling term):
$$
\mathbf J\,\dot{\boldsymbol\omega}^b + \boldsymbol\omega^b \times (\mathbf J\,\boldsymbol\omega^b) = \mathbf M^b,
$$
where $\mathbf J$ is the $3\times3$ inertia tensor. The cross-product terms are
not optional — they are why a thrown phone tumbles unpredictably about its
intermediate axis (the *tennis-racket theorem*) and why a fast-spinning quad
resists pitch.

The full state for a 6-DOF sim is 13 numbers: position (3) + velocity (3) +
quaternion (4) + body rate (3). The complete model:
$$
\boxed{
\begin{aligned}
\dot{\mathbf p}^n &= R_b^n\,\mathbf v^b
&\quad& \text{(position kinematics)}\\
\dot{\mathbf v}^b &= \tfrac1m \mathbf F^b - \boldsymbol\omega^b\times\mathbf v^b
&\quad& \text{(translational dynamics)}\\
\dot{\mathbf q} &= \tfrac12\,\mathbf q\otimes(0,\boldsymbol\omega^b)
&\quad& \text{(attitude kinematics)}\\
\dot{\boldsymbol\omega}^b &= \mathbf J^{-1}\big(\mathbf M^b - \boldsymbol\omega^b\times \mathbf J\boldsymbol\omega^b\big)
&\quad& \text{(rotational dynamics)}
\end{aligned}}
$$

### 2.2 Forces and moments by airframe class

What goes into $\mathbf F^b$ and $\mathbf M^b$ is what *distinguishes* a quad from
a plane from a VTOL.

| | Multirotor | Fixed-wing | VTOL (the airframe) |
|---|---|---|---|
| **Lift** | Rotor thrust (always "up" in body) | Wing aerodynamic lift $\propto V^2 C_L(\alpha)$ | Both, regime-dependent |
| **Control authority** | Differential rotor thrust/torque | Aerodynamic surfaces (ailerons, elevator, rudder) | Both; blends across transition |
| **Underactuation** | 4 inputs, 6 DOF — must tilt to translate | Coordinated turns; can't hover | Mode-dependent |
| **Speed envelope** | Hover → ~20 m/s | Stall speed → cruise | Full range |
| **Dominant uncertainty** | Battery sag, wind gusts | Aero coefficients, wind | Transition aerodynamics (worst) |

**Multirotor.** Each rotor $i$ produces thrust $T_i = k_T \omega_i^2$ and reaction
torque $Q_i = k_Q \omega_i^2$. Total body thrust is purely along $-z_b$; moments
come from thrust *differences* across the arms. A quad is **underactuated**: to
move north it must first pitch, coupling translation to attitude — which is
exactly why control is *cascaded* (Section 7.5).

**Fixed-wing.** Aerodynamic forces dominate:
$$
L = \tfrac12\rho V^2 S\,C_L(\alpha),\quad
D = \tfrac12\rho V^2 S\,C_D(\alpha),\quad
\text{moments} \propto \tfrac12\rho V^2 S c\, C_{m}.
$$
Lift depends on angle of attack $\alpha$ and airspeed $V$; below stall speed there
is no lift. A plane cannot hover, must keep flying, and turns by banking.

**VTOL transition** is the hardest regime in all of fixed-wing autonomy: as the
aircraft accelerates and tilts, lift transfers from rotors to wing, control
authority migrates from thrust to surfaces, and the aerodynamics are *partially
stalled and unsteady* the entire time. Both the dynamics **and** the sensor
trustworthiness change (Section 5/6).

> **⚓ Anchor — phase-aware everything.** [`manager.py`](../navigation/manager.py)
> encodes this transition difficulty directly in its `NavPhase` enum
> (`HOVER`/`TRANSITION`/`CRUISE`) derived from `MAV_VTOL_STATE`. It changes *which
> sensors it trusts* by flight regime because the **dynamics that make transition
> hard to fly are the same dynamics that make its sensor data hard to trust**.

### 2.3 Control allocation (mixing)

The controller computes a desired **wrench**: total thrust $T$ and 3-axis moment
$\boldsymbol\tau$. The **mixer / control-allocation** problem is to find actuator
commands $\mathbf u$ (rotor speeds, servo deflections) that produce it:
$$
\begin{bmatrix} T \\ \boldsymbol\tau \end{bmatrix}
= \mathbf B\,\mathbf u,
\qquad
\mathbf u = \mathbf B^{\dagger}\begin{bmatrix} T \\ \boldsymbol\tau \end{bmatrix}
\ \text{(pseudo-inverse, then saturate)}.
$$
$\mathbf B$ is the **effectiveness matrix** (geometry + $k_T, k_Q$). For a VTOL it
is *time-varying* across transition — rotors fade out, surfaces fade in. Real
allocators handle actuator saturation (you can't command 110% throttle) by
constrained optimization or prioritized desaturation, preserving roll/pitch
authority at the expense of thrust when limits bind. PX4 implements this in its
control-allocation module.

---

## 3. Sensors & their error models

An estimator is a machine for combining imperfect sensors. To weight them
correctly you must model their errors *honestly*. "Garbage covariance in, garbage
estimate out."

### 3.1 The IMU — accelerometer + gyroscope

A MEMS IMU is the heartbeat of inertial navigation, and also a fountain of error.
Each axis of each sensor follows roughly:
$$
\tilde a = (1 + s)\,a + b(t) + n,\qquad
\tilde\omega = (1+s)\,\omega + b(t) + n.
$$

| Error term | Symbol | Nature | Consequence |
|---|---|---|---|
| **Bias** | $b(t)$ | Slowly time-varying, temp-dependent | Integrates: gyro bias → attitude drift → position drift $\propto t^3$ |
| **Scale factor** | $s$ | Multiplicative | Error grows with the signal magnitude |
| **Misalignment** | — | Axis non-orthogonality | Cross-axis coupling |
| **White noise** | $n$ | Zero-mean, broadband | "Velocity/angle random walk" after integration |
| **Bias instability** | — | $1/f$ flicker noise | The *noise floor* — the best you can ever do |

**The integration catastrophe.** A constant gyro bias $b_g$ produces attitude
error $\delta\theta = b_g t$. That tilts the gravity-subtraction in the
accelerometer channel by $g\,\delta\theta$, so horizontal acceleration error grows
linearly, velocity error as $t^2$, and **position error as $t^3$**. A 0.01°/s bias
yields hundreds of meters of drift in a minute. *This is the entire reason
aiding sensors exist.* Pure inertial nav is a countdown timer.

**Allan variance** is the standard tool to characterize these terms. Log a
stationary IMU, compute the variance of averaged samples vs. averaging time
$\tau$, and plot $\sigma(\tau)$ log–log:
$$
\sigma^2(\tau) = \underbrace{\frac{N^2}{\tau}}_{\text{white noise, slope }-1/2}
+ \underbrace{B^2}_{\text{bias instability, slope }0}
+ \underbrace{\frac{K^2\tau}{3}}_{\text{rate random walk, slope }+1/2}.
$$
The slope-$-\tfrac12$ region gives **angle/velocity random walk** $N$
(the $\sqrt{\text{Hz}}$ noise density that sets your process-noise $Q$); the
flat minimum gives **bias instability** $B$ (the ultimate floor). Reading an
Allan-deviation plot fluently is a senior-engineer party trick — and it directly
sets filter tuning.

### 3.2 The other sensors

| Sensor | Measures | Error model highlights | Failure modes |
|---|---|---|---|
| **Magnetometer** | Earth's field → heading | Hard-iron (constant offset) + soft-iron (scale/skew) from the airframe; needs calibration; declination correction | Corrupted by motors/currents, ferrous structures, magnetic anomalies |
| **Barometer** | Static pressure → altitude | Bias + slow drift with weather; ~0.1–1 m noise | Prop-wash pressure transients, cabin/airflow effects, weather fronts |
| **GNSS/GPS** | Pseudoranges → ECEF position+velocity | ~1–3 m horizontal (worse vertical); multipath; ionospheric delay | **Jamming, spoofing, urban canyon, indoors, foliage** — the whole reason for this repo |
| **Optical flow** | Apparent ground motion (px/frame) | Needs texture, lighting, known range; scale ambiguity without range | Featureless terrain, motion blur, low light, high AGL |
| **Camera (VIO/map-match)** | Pixels → features / image registration | Depends on texture, geometry, exposure | Same visual failure modes; map staleness |
| **Rangefinder/Lidar** | Slant/vertical range | Surface reflectivity, beam divergence | Water, glass, dropouts |

**Why GPS-denial is the motivating threat.** GNSS is a ~–125 dBm signal from
20,000 km away — trivially **jammed** by a few watts on the ground, and
**spoofable** by a transmitter that mimics the constellation to walk your position
solution off truth. In contested airspace you must assume GPS is unavailable or
*lying*. A defense-grade autonomy stack therefore treats GPS as **one optional
aiding source among many**, not as ground truth. That design stance is the spine
of this repo.

### 3.3 Building an error budget

An **error budget** allocates the total allowable position error across all
contributors so the system meets its requirement. Independent zero-mean errors
combine in quadrature (RSS):
$$
\sigma_{\text{total}} = \sqrt{\sum_i \sigma_i^2}.
$$
You work it *backwards* from the requirement: "I need < 10 m CEP for terminal
guidance; my map-match gives 5 m; therefore my dead-reckoning drift between fixes
must stay under $\sqrt{10^2 - 5^2}\approx 8.7$ m, which at my drift rate means I
need a fix at least every $T$ seconds." (Full worked example in Section 10.)

> **⚓ Anchor.** The repo's noise constants *are* an error budget made executable:
> `DEFAULT_INIT_POS_SIGMA = 50 m` (pre-fix ignorance), `GPS_FIX_SIGMA_M = 2.5 m`,
> `AIR_VEL_SIGMA_MPS = 4 m/s` (a *wind-uncertainty* budget — airspeed gives velocity
> through the air, wind is the error to ground velocity), and `DEFAULT_MAX_POS_SIGMA
> = 40 m` (the line past which the estimate is declared `LOST` and the aircraft must
> hold/RTL). Every one of these is a defensible row in a budget table.

---

## 4. Estimation theory — the spine

This is the heart of the module. We build from least squares to the Kalman filter
*from first principles*, then extend to nonlinear and modern variants — anchoring
every step to the real 6-state filter in
[`nav_state.py`](../navigation/nav_state.py).

### 4.1 Least squares — the foundation

Given measurements $\mathbf z = H\mathbf x + \mathbf v$ with noise covariance $R$,
the **weighted least-squares** estimate minimizes the Mahalanobis residual
$J(\mathbf x) = (\mathbf z - H\mathbf x)^\top R^{-1}(\mathbf z - H\mathbf x)$:
$$
\hat{\mathbf x} = (H^\top R^{-1} H)^{-1} H^\top R^{-1}\mathbf z,
\qquad
P = (H^\top R^{-1} H)^{-1}.
$$
**Insight:** weighting by $R^{-1}$ means *trust precise measurements more*. This
single idea — inverse-variance weighting — is the seed the Kalman filter grows
from.

### 4.2 Recursive least squares — process one measurement at a time

Batch LS needs all data at once. **RLS** updates incrementally as each
measurement arrives, with a *gain* $K_k$ that blends prior estimate and new data:
$$
\hat{\mathbf x}_k = \hat{\mathbf x}_{k-1} + K_k(\mathbf z_k - H_k\hat{\mathbf x}_{k-1}),
\qquad
K_k = P_{k-1}H_k^\top(H_k P_{k-1}H_k^\top + R_k)^{-1}.
$$
This is already the Kalman *update* equation. RLS = a Kalman filter for a *static*
state. Add a dynamics model and you have the full filter.

### 4.3 The Kalman filter from first principles

**Setup.** A linear-Gaussian system:
$$
\begin{aligned}
\mathbf x_k &= F_k\mathbf x_{k-1} + \mathbf w_k, &\quad \mathbf w_k\sim\mathcal N(0,Q_k) &\quad\text{(process)}\\
\mathbf z_k &= H_k\mathbf x_k + \mathbf v_k, &\quad \mathbf v_k\sim\mathcal N(0,R_k) &\quad\text{(measurement)}
\end{aligned}
$$
The KF is the **optimal** (minimum-mean-square-error, and for Gaussians the exact
Bayesian) estimator. It propagates the *full posterior* — which for linear-Gaussian
systems is exactly a Gaussian $\mathcal N(\hat{\mathbf x}, P)$, so tracking the mean
and covariance is sufficient.

**Predict (time update)** — push the Gaussian through the dynamics:
$$
\boxed{\;
\hat{\mathbf x}_k^- = F_k\hat{\mathbf x}_{k-1}^+,
\qquad
P_k^- = F_k P_{k-1}^+ F_k^\top + Q_k. \;}
$$
The covariance grows: $F P F^\top$ rotates/stretches the old uncertainty, $+Q$
adds new uncertainty from unmodeled dynamics. **Prediction always makes you less
certain.**

**Update (measurement update)** — fuse the measurement via Bayes:
$$
\boxed{\;
\begin{aligned}
\tilde{\mathbf y}_k &= \mathbf z_k - H_k\hat{\mathbf x}_k^-
&\quad& \textbf{innovation (what's new)}\\
S_k &= H_k P_k^- H_k^\top + R_k
&\quad& \textbf{innovation covariance}\\
K_k &= P_k^- H_k^\top S_k^{-1}
&\quad& \textbf{Kalman gain (optimal blend)}\\
\hat{\mathbf x}_k^+ &= \hat{\mathbf x}_k^- + K_k\tilde{\mathbf y}_k
&\quad& \text{state correction}\\
P_k^+ &= (I - K_k H_k)P_k^-
&\quad& \text{covariance shrinks}
\end{aligned} \;}
$$

**The Kalman gain as an optimal blend.** Look at the scalar case. If the state
variance is $P^-$ and the measurement variance is $R$, then
$K = \frac{P^-}{P^- + R}$. When the measurement is perfect ($R\to0$),
$K\to1$ and you snap entirely to the measurement. When the measurement is useless
($R\to\infty$), $K\to0$ and you ignore it. The gain is the **fraction of the way
you move toward the measurement, set by relative confidence.** Everything else is
this idea in matrix form. *This is the single most important intuition in
estimation* — internalize it.

**The covariance Riccati recursion.** Substituting the gain back gives the
update as a recursion on $P$ alone:
$$
P_k^+ = P_k^- - P_k^- H_k^\top(H_k P_k^- H_k^\top + R_k)^{-1}H_k P_k^-.
$$
Chained with predict ($P^- = FP^+F^\top + Q$), this is the **discrete Riccati
equation**. Remarkably, for time-invariant systems it converges to a *steady-state*
$P_\infty$ (and steady-state gain $K_\infty$) **independent of the data** — the
filter's confidence reaches equilibrium between $Q$ pumping uncertainty in and
measurements draining it out. (This steady-state gain, run open-loop, is the
classic *alpha-beta filter*.)

#### ⚓ Anchor — the real 6-state constant-velocity filter

[`nav_state.py`](../navigation/nav_state.py) is a textbook linear KF. State
$\mathbf x = [p_n,p_e,p_d,v_n,v_e,v_d]^\top$. **Constant-velocity** means the model
assumes velocity is constant and treats acceleration as random process noise (a
"white-noise-jerk on the velocity states", per its docstring).

**Predict** uses $F = I$ with the $dt$ coupling of velocity into position:
$$
F = \begin{bmatrix} I_3 & dt\,I_3 \\ 0 & I_3 \end{bmatrix},
\qquad \mathbf x \leftarrow F\mathbf x.
$$
```python
F = np.eye(6)
F[0, 3] = dt; F[1, 4] = dt; F[2, 5] = dt
self._x = F @ self._x
```
The process noise is the **discrete white-noise-acceleration** model: an
acceleration of PSD $q=\sigma_a^2$ acting over $dt$ produces the exact $Q$
$$
Q = q\begin{bmatrix} \tfrac{dt^4}{4}I_3 & \tfrac{dt^3}{2}I_3 \\[2pt] \tfrac{dt^3}{2}I_3 & dt^2 I_3 \end{bmatrix},
$$
which is precisely the code's `qpp = dt⁴/4·q`, `qpv = dt³/2·q`, `qvv = dt²·q`. The
off-diagonal $dt^3/2$ terms encode that position and velocity errors are
*correlated* (an unmodeled acceleration corrupts both) — getting that
cross-covariance right is what separates a real filter from a hand-rolled
low-pass.

**Update** is the canonical sequence, implemented once in `_kalman_update` and
reused by `correct_position` (rows 0,1 — map-match), `correct_velocity` (rows 3,4,5
— VO), and `correct_altitude` (row 2 — baro):
```python
y = z - H @ self._x                 # innovation
S = H @ self._P @ H.T + R           # innovation covariance
K = self._P @ H.T @ np.linalg.inv(S)  # Kalman gain
self._x = self._x + K @ y           # corrected state
self._P = (np.eye(6) - K @ H) @ self._P
self._P = 0.5 * (self._P + self._P.T)  # re-symmetrize vs round-off
```
$H$ is a **selector matrix** (1's on the measured rows) because every measurement
is a *direct* observation of a state component — that's what keeps this filter
linear and exact. The final re-symmetrization is a real-world numerics guard:
floating-point round-off makes $(I-KH)P$ slightly asymmetric, which over many
updates can break positive-definiteness; averaging with the transpose costs
nothing and prevents covariance divergence. (The gold-standard alternative is the
**Joseph-form** update $P^+ = (I-KH)P^-(I-KH)^\top + KRK^\top$, which is
symmetric-by-construction and more numerically robust at higher cost.)

### 4.4 The Extended Kalman Filter (EKF) — when the world is nonlinear

Real dynamics and measurements are nonlinear: $\mathbf x_k = f(\mathbf x_{k-1},\mathbf u)$,
$\mathbf z_k = h(\mathbf x_k)$. The EKF **linearizes about the current estimate** via
first-order Taylor — i.e., it uses the **Jacobians**
$$
F_k = \left.\frac{\partial f}{\partial \mathbf x}\right|_{\hat{\mathbf x}_{k-1}^+},
\qquad
H_k = \left.\frac{\partial h}{\partial \mathbf x}\right|_{\hat{\mathbf x}_k^-},
$$
then runs the linear KF covariance equations with these Jacobians, while
propagating the *mean* through the full nonlinear $f$ and $h$. 

**The catch — linearization error.** The Taylor expansion drops second-order and
higher terms. If the function is strongly curved over the span of the covariance,
the EKF's covariance becomes *inconsistent* (over-optimistic), the gain is wrong,
and the filter can diverge. EKFs are sensitive to initialization and to large
innovations. Mitigations: better initialization, the **iterated EKF** (relinearize
the update at the corrected state), or moving to the UKF.

> **⚓ Anchor.** PX4's **EKF2** is exactly this: a ~24-state error-state EKF
> estimating position, velocity, the quaternion attitude (via the MEKF error
> trick of §1.3), gyro & accel biases, earth/body magnetic field, and wind. Its
> measurement models for GPS, baro, mag, optical flow, and **external vision** are
> all nonlinear $h(\cdot)$ that get Jacobian-linearized each update. When this
> repo's [`vision_bridge.py`](../navigation/vision_bridge.py) sends a
> `VISION_POSITION_ESTIMATE`, it is feeding a measurement straight into EKF2's
> nonlinear update step — your companion-computer estimate becomes one $\mathbf z_k$
> in PX4's big EKF.

### 4.5 The Unscented Kalman Filter (UKF) — linearize the *distribution*, not the function

Instead of a Taylor Jacobian, the UKF deterministically samples **sigma points**
$\boldsymbol\chi_i$ around the mean (using the matrix square root of $P$), pushes each
through the *true* nonlinear $f$/$h$, and recomputes the mean and covariance from
the transformed points:
$$
\boldsymbol\chi_0 = \hat{\mathbf x},\quad
\boldsymbol\chi_i = \hat{\mathbf x} \pm \big(\sqrt{(n+\lambda)P}\big)_i,
\qquad
\hat{\mathbf x}' = \sum_i W_i^{(m)} f(\boldsymbol\chi_i),\quad
P' = \sum_i W_i^{(c)} (\cdot)(\cdot)^\top + Q.
$$
This **unscented transform** captures the mean to 3rd order and covariance to 2nd
order (vs the EKF's 1st) for any nonlinearity, with **no Jacobians to derive** —
a real engineering win when $h$ is a gnarly camera-projection model. Cost is
$2n{+}1$ function evaluations per step. For strongly nonlinear measurement models
(vision!) the UKF is often more consistent than the EKF.

### 4.6 Beyond Gaussian — particle filters & factor graphs

- **Particle filter (PF):** represent the posterior by a swarm of weighted samples;
  propagate each through $f$, weight by measurement likelihood, resample. Handles
  *arbitrary, multimodal* distributions (e.g., "I'm at one of three valleys") that
  no Gaussian filter can — at the cost of exponential samples in high dimension
  (the *curse of dimensionality*). Great for terrain-aided nav with ambiguous
  map matches; impractical for a full 24-state vehicle model.
- **Factor graphs / MAP smoothing (GTSAM-style):** instead of a forward filter,
  build a graph where nodes are states-over-time and edges (*factors*) are
  measurement/dynamics constraints, then solve for the trajectory that maximizes
  the joint posterior by sparse nonlinear least squares (Gauss–Newton /
  Levenberg–Marquardt over the whole window). This is **smoothing**, not filtering:
  it relinearizes past states with future information, so it's more accurate and
  more robust to bad linearization. Incremental variants (iSAM2) keep it real-time.
  Modern VIO (the kind Skydio/Shield AI run) is overwhelmingly factor-graph based.

| Estimator | Handles nonlinearity | Handles non-Gaussian | Cost | Typical use |
|---|---|---|---|---|
| KF | linear only | no | cheapest | `nav_state.py` CV filter |
| EKF | 1st-order | no | cheap | PX4 **EKF2**, classic INS/GNSS |
| UKF | 2nd/3rd-order | no | moderate | nasty measurement models |
| Particle | arbitrary | **yes** | expensive | terrain-aided, recovery |
| Factor graph | full (relinearized) | approx | moderate–high | modern **VIO/SLAM** |

---

## 5. Sensor fusion in practice

Theory says "run the update equations." Practice is everything that makes them
*not lie to you*.

### 5.1 Loosely vs. tightly coupled

- **Loosely coupled:** each sensor first computes its own solution (GPS → a
  position fix; the camera → a velocity), and the filter fuses these *derived
  estimates*. Simpler, modular, degrades gracefully.
- **Tightly coupled:** the filter ingests **raw** measurements (GPS pseudoranges,
  image features) directly. More information, works with *partial* data (e.g. 3
  satellites — not enough for a standalone fix but still constraining), but
  complex and brittle to model.

> **⚓ Anchor.** This repo is deliberately **loosely coupled**:
> [`visual_odometry.py`](../navigation/visual_odometry.py) emits a finished
> velocity estimate, [`map_match.py`](../navigation/map_match.py) emits a finished
> position fix, and [`manager.py`](../navigation/manager.py) fuses those products.
> The docstring's own framing — "marrying a high-rate **drifting** source with a
> low-rate **absolute** one" — is the loosely-coupled design pattern stated
> plainly. It keeps each driver pure and unit-testable with synthetic inputs.

### 5.2 Observability — can the data even pin down the state?

A state is **observable** if the measurements uniquely determine it. The linear
test is the rank of the observability matrix
$\mathcal O = [H;\,HF;\,HF^2;\dots;\,HF^{n-1}]$ — full rank $n$ ⇒ observable. If
not, some combination of states is invisible and its error will grow unchecked no
matter how good your filter is. **Observability is a property of the
sensor+motion geometry, not of the algorithm.** Classic example: IMU-only attitude
yaw is unobservable while sitting still (no specific force to align against) — you
need motion or a magnetometer. In VIO, scale and global position/yaw are
unobservable from a downward camera alone without an absolute fix; **that
unobservable drift is exactly what map-matching bounds** (Section 6).

### 5.3 Consistency — is the filter telling the truth about its own error?

A filter is **consistent** if its reported covariance matches its actual error
statistics. Two standard checks:

- **NEES** (Normalized Estimation Error Squared, needs ground truth):
$\epsilon_k = (\mathbf x_k - \hat{\mathbf x}_k)^\top P_k^{-1}(\mathbf x_k - \hat{\mathbf x}_k)$.
For a consistent $n$-state filter, $\mathbb E[\epsilon] = n$ and $\epsilon$ follows
$\chi^2_n$. Average NEES above $n$ ⇒ *over-confident* (covariance too small);
below ⇒ *conservative*.
- **NIS** (Normalized Innovation Squared, **needs no ground truth** — usable in
  flight): $\nu_k = \tilde{\mathbf y}_k^\top S_k^{-1}\tilde{\mathbf y}_k \sim \chi^2_m$.
  This is the *online* consistency monitor and the basis of gating.

### 5.4 The innovation / gating test — rejecting outliers

Before applying an update, check whether the innovation is statistically plausible
given $S$. The **Mahalanobis gate** rejects a measurement if
$$
\tilde{\mathbf y}^\top S^{-1}\tilde{\mathbf y} > \gamma,
\qquad \gamma = \chi^2_{m}(1-\alpha)\ \text{(e.g. } \alpha=0.01).
$$
A spoofed GPS jump, a bad map-match correlation peak, or a VO glitch produces a
huge innovation that fails the gate and is discarded — *this is your primary
defense against a single bad measurement poisoning the estimate.* PX4's EKF2 gates
every aiding source this way (the `*_innov_gate` parameters).

> **⚓ Anchor — gated absolute fixes.** [`manager.py`](../navigation/manager.py)'s
> `feed_fix` only fuses a map-match when `fix.valid` is true and carries the
> match's own `fix.sigma_m`; [`map_match.py`](../navigation/map_match.py) rejects
> low-confidence phase-correlation peaks *before* they ever reach the filter — a
> pre-filter outlier gate. And `feed_velocity` *inflates or drops* VO by flight
> phase (`CRUISE_VO_SIGMA_MULT`, `TRANSITION_USE_VO`), which is gating-by-prior:
> "I already know this source is unreliable right now, so widen its $R$ or refuse
> it." Robust fusion is as much about **what you refuse to believe** as what you fuse.

### 5.5 Tuning $Q$ and $R$ — the engineer's real job

- **$R$ (measurement noise):** comes from the sensor — characterize it (datasheet,
  Allan variance, bench test). Too small ⇒ filter over-trusts noisy data and
  jitters; too large ⇒ ignores good data and lags.
- **$Q$ (process noise):** how wrong your *model* is. The CV filter's
  `DRONE_NAV_ACCEL_SIGMA` is literally "how hard can the aircraft jerk?" Too small
  ⇒ filter trusts its stale prediction, lags maneuvers, and can diverge; too large
  ⇒ filter chases every measurement and never smooths. The repo's own comment nails
  it: *"Higher ⇒ filter trusts measurements more and reacts faster (but jitters
  more)."* You tune $Q/R$ until NIS sits in its $\chi^2$ band across representative
  flights. This *ratio* is the whole ballgame — it sets the steady-state gain.

### 5.6 Latency compensation & multi-rate fusion

Real measurements arrive **late** and at **different rates**: IMU at 200–1000 Hz,
baro at ~50 Hz, GPS at 5–10 Hz, a camera/VIO at 10–30 Hz — and the camera's
result corresponds to an image captured *tens of milliseconds ago*. Fusing a
delayed measurement at the *current* state time corrupts the estimate. Standard
fixes:

- **Measurement buffering / OOSM:** keep a ring buffer of past states+covariances;
  apply the delayed measurement at its true timestamp and re-propagate forward
  (EKF2 does exactly this with its sensor delay buffer and per-sensor `*_delay`
  parameters).
- **Multi-rate predict/update:** `predict` runs every tick; each `correct_*`
  fires only when its sensor delivers. The filter naturally handles asynchronous,
  multi-rate inputs because predict and update are decoupled.

> **⚓ Anchor.** [`nav_state.py`](../navigation/nav_state.py)'s API *is* a
> multi-rate fuser: one `predict(now)` integrates to the current time and inflates
> $P$; the three independent `correct_*` methods fire whenever their (different-rate)
> source produces data. The `last_fix_age_s` field and the `DEAD_RECKON` mode are
> the honest accounting of "how stale is my last absolute fix" — the operational
> face of latency awareness.

---

## 6. GPS-denied / vision-aided navigation

This is the repo's reason to exist and the most operationally valued skill in
defense autonomy: **navigate accurately when GPS is jammed, spoofed, or absent.**

### 6.1 The drift problem, stated precisely

Any *relative* sensor (IMU, optical flow, VO) measures **change**, so its position
error **accumulates** — an unbounded random walk (or worse; recall the IMU's $t^3$
growth). Any *absolute* sensor (GPS, map-match) measures **where you are**, so its
error is **bounded** but it's low-rate and may be unavailable. The art of
GPS-denied nav is to ride the high-rate relative source for smoothness and
responsiveness while **periodically pinning it with an absolute fix** so the drift
never escapes.

```
position
error      relative-only (drifts, unbounded)
  │              ╱╲      ╱╲
  │             ╱  ╲    ╱  ╲   ╱
  │   ╱╲   ╱╲  ╱    ╲  ╱    ╲ ╱
  │  ╱  ╲ ╱  ╲╱      ╲╱      V   ← drift between fixes
  │ ╱    V    │       │       │
  │╱     ↑    ↑       ↑       ↑   ← absolute fixes snap it back down
  └────────────────────────────────► time
         each fix bounds the accumulated drift
```

This is the entire philosophy of [`nav_state.py`](../navigation/nav_state.py)'s
opening docstring — *"A Kalman filter is exactly the right tool for marrying a
high-rate drifting source with a low-rate absolute one."*

### 6.2 Visual odometry & VIO

**Visual odometry** estimates motion from how the image moves. Track features (or
dense optical flow) between consecutive frames; the apparent pixel motion, given
the camera's range to the ground, converts to a metric velocity:
$$
v_{\text{ground}} = \frac{\Delta\text{(pixels)}}{\Delta t}\cdot\underbrace{\frac{\text{range}}{\,f_{\text{px}}}}_{\text{meters/pixel (GSD)}}.
$$
Range/scale is the crux — without it, monocular VO is scale-ambiguous.
**VIO (Visual-Inertial Odometry)** fuses the camera with the IMU: the IMU provides
metric scale and high-rate motion between frames; the camera bounds the IMU's
drift. VIO is the workhorse of modern GPS-denied nav (and what runs on Skydio).

> **⚓ Anchor.** [`visual_odometry.py`](../navigation/visual_odometry.py) computes
> **body-frame velocity** from frame-to-frame feature/optical flow, scaled by the
> **ground sample distance** (`meters_per_pixel`) from the **slant range** —
> precisely the equation above. The manager rotates that body velocity into NED by
> the autopilot's yaw and feeds it to `correct_velocity`. It's loosely-coupled
> VO providing the high-rate *relative* term; its drift is what the absolute fix
> must bound.

### 6.3 Terrain-relative / map-matching navigation

The **absolute** fix without GPS: register what the camera sees against a
*georeferenced* map (satellite tile + DEM). **Phase correlation** finds the
$(\Delta x,\Delta y)$ shift that best aligns the live image to a map tile by a
peak in the inverse-FFT of the normalized cross-power spectrum; a sharp peak ⇒
confident match ⇒ a position fix with a defensible $\sigma$. This is *terrain-aided
navigation*, used operationally by cruise missiles (TERCOM/DSMAC) for decades and
now by vision autonomy.

> **⚓ Anchor.** [`map_match.py`](../navigation/map_match.py) does exactly this —
> **phase correlation of camera vs satellite tile**, returning a `MapFix(lat, lon,
> sigma_m, valid)`. The `valid`/`sigma_m` fields are the confidence of the
> correlation peak; only confident matches pass the gate of §5.4 into
> `correct_position`. **This is the absolute fix that bounds the VO drift.**

### 6.4 Sending external vision to EKF2

The companion computer can run heavy vision the flight controller can't, then hand
the *result* to PX4's estimator via MAVLink. EKF2 fuses `VISION_POSITION_ESTIMATE`
(and `VISION_SPEED_ESTIMATE`/`ODOMETRY`) as another gated, Jacobian-linearized
measurement update — letting your companion-grade GPS-denied solution *actually
stabilize and fly the aircraft* through PX4's controllers.

> **⚓ Anchor.** [`vision_bridge.py`](../navigation/vision_bridge.py) packages a
> `NavEstimate` into a `VisionPose` (local NED + roll/pitch/yaw + an upper-triangular
> covariance) and emits `VISION_POSITION_ESTIMATE`. Two senior details: (1) only
> `usable` estimates (mode `AIDED`/`DEAD_RECKON`, $\sigma$ under the `LOST`
> threshold) are sent — **never feed the autopilot a fix you don't believe**; and
> (2) the covariance you send *is* the contract — EKF2 weights your fix by exactly
> the $R$ you advertise, so an honest `pos_sigma_m` is safety-critical. Lie low and
> EKF2 over-trusts a drifting estimate; lie high and it ignores a good one.

The complete GPS-denied data path in this repo:
```
 camera ─┬─► visual_odometry.py ──(body vel)──► manager.feed_velocity ─┐
         │                                                             ├─► nav_state KF ─► vision_bridge ─► VISION_POSITION_ESTIMATE ─► PX4 EKF2 ─► controllers
         └─► map_match.py ────────(abs fix)───► manager.feed_fix ──────┘                                     (gated, nonlinear update)
                      ▲                                                  ▲
              satellite tile + DEM                       GPS (when healthy) bootstraps origin & validates
```

---

## 7. Control theory

Navigation answers "where am I"; control answers "what do I command to get where I
should be." We build from PID to the modern methods.

### 7.1 PID — the workhorse

For error $e(t) = r(t) - y(t)$:
$$
u(t) = K_p\,e(t) + K_i\!\int_0^t e(\tau)\,d\tau + K_d\,\frac{de(t)}{dt}.
$$
- **$K_p$** — pushes proportional to current error (stiffness). Too high ⇒
  oscillation.
- **$K_i$** — eliminates steady-state error by accumulating it. Too high ⇒
  overshoot and **integral windup** (the integrator saturates during a sustained
  error — real controllers *clamp/back-calculate* to prevent it).
- **$K_d$** — damps by reacting to error *rate*. Amplifies noise, so it's usually
  applied to the *measurement* (derivative-on-measurement) and low-pass filtered.

**Real tuning** is not Ziegler–Nichols folklore; it's: get a clean rate estimate,
raise $K_p$ until you see the onset of oscillation then back off, add $K_d$ to damp,
add just enough $K_i$ to kill steady-state droop, and verify on **step responses**
and in wind. Most "bad tune" crashes are derivative noise or integral windup.

### 7.2 State-space — the modern language

$$
\dot{\mathbf x} = A\mathbf x + B\mathbf u,
\qquad
\mathbf y = C\mathbf x + D\mathbf u.
$$
Stability is governed by the **eigenvalues of $A$** (continuous: real parts < 0;
discrete: inside the unit circle). This framework scales to MIMO (coupled
multi-input/output) systems where PID's one-loop-per-channel view breaks down.

### 7.3 Controllability & observability (the control duals)

- **Controllable** if you can drive any state to any other in finite time —
  $\mathrm{rank}[B,\,AB,\,A^2B,\dots,A^{n-1}B] = n$. If not, some mode can't be
  influenced by the actuators.
- **Observable** (the §5.2 dual) if outputs determine the state —
  $\mathrm{rank}[C;\,CA;\dots;\,CA^{n-1}] = n$.

These are necessary conditions for *any* controller/estimator to work. Note the
beautiful **duality:** estimation (the Kalman filter) and control (LQR) are
mathematically mirror problems — same Riccati equation, transposed.

### 7.4 LQR — optimal linear control

Choose $\mathbf u = -K\mathbf x$ to minimize a quadratic cost trading off state
error against control effort:
$$
J = \int_0^\infty\big(\mathbf x^\top Q\mathbf x + \mathbf u^\top R\mathbf u\big)\,dt,
\qquad
K = R^{-1}B^\top P,
$$
where $P$ solves the **algebraic Riccati equation**
$A^\top P + PA - PBR^{-1}B^\top P + Q = 0$. $Q$ penalizes state error, $R$ penalizes
effort — tune their ratio for aggressive vs. gentle. LQR gives a *provably
optimal, stabilizing* gain for the linear model, and pairs with a Kalman filter as
the **LQG** controller (estimate the state, then control it — the separation
principle says you can design each independently for linear-Gaussian systems).

### 7.5 The cascade architecture — how a real flight stack is built

No one closes one giant MIMO loop on a drone. The controller is a **cascade** of
nested loops, fast on the inside, slow on the outside — each outer loop's output is
the inner loop's setpoint:

```
   position    ┌──────────┐ vel_sp  ┌──────────┐ att_sp ┌──────────┐ rate_sp ┌──────────┐ torque/thrust ┌───────┐
   setpoint───►│ POSITION ├────────►│ VELOCITY ├───────►│ ATTITUDE ├────────►│   RATE   ├──────────────►│ MIXER ├──► motors
       ▲       │  (P)     │         │  (PID)   │        │  (P/quat)│         │  (PID)   │               └───────┘
       │       └──────────┘         └──────────┘        └──────────┘         └──────────┘
   ~50 Hz                                                                      ~1 kHz
   (slow, smart)  ◄───────────────── increasing rate, decreasing abstraction ─────────►  (fast, dumb)
```

Why cascade? It **decouples timescales** (attitude dynamics are 10× faster than
position), makes each loop a simple SISO-ish problem you can tune independently,
and lets inner loops reject disturbances before they reach the slow outer loop.
The inner **rate loop** must run fastest because the rotational dynamics are the
quickest and least stable — it's the loop standing between you and a tumble.

> **⚓ Anchor — PX4 is literally this cascade.** PX4's multicopter stack is
> `MulticopterPositionControl` (P on position → velocity PID) →
> `MulticopterAttitudeControl` (quaternion attitude → rate setpoint) →
> `MulticopterRateControl` (rate PID → torque/thrust) → control allocation →
> ESCs. The fixed-wing stack mirrors it with TECS (total-energy) +
> attitude/rate loops. **The nav estimate from §4–6 enters at the top:** the
> position/velocity loops close on EKF2's fused state, which this repo's vision
> path feeds when GPS is denied. Bad estimate ⇒ the whole cascade controls toward
> the wrong place, confidently.

### 7.6 Feedforward, gain scheduling, and the advanced methods

- **Feedforward.** Don't wait for error to build — command the *known-required*
  input directly (e.g. the thrust to counter gravity, or the input predicted from
  the reference trajectory), and let feedback handle only the residual. Feedforward
  improves tracking without sacrificing stability margin; it's why a well-tuned
  drone follows an aggressive trajectory crisply.
- **Gain scheduling.** A single linear controller can't cover a VTOL's whole
  envelope (hover vs. cruise are different plants). Schedule gains against a
  parameter — airspeed, **VTOL transition state**, altitude — interpolating between
  designs. This is classical, robust, and ubiquitous; the §5 phase-awareness is
  gain-scheduling's estimation cousin.
- **MPC (Model Predictive Control).** Solve a finite-horizon optimal-control
  problem *online* each tick: predict the model forward over a horizon, optimize the
  input sequence subject to **constraints** (actuator limits, no-fly volumes,
  obstacle avoidance), apply the first input, repeat (*receding horizon*). MPC's
  superpower is handling constraints explicitly; its cost is solving an optimization
  in real time. Increasingly used for aggressive/agile flight.
- **L1 / adaptive control.** Estimate and cancel unmodeled dynamics and
  disturbances online with guaranteed fast adaptation and bounded transients —
  valued where the plant changes (payload, damage, the VTOL transition).
- **Geometric / nonlinear $SE(3)$ control.** Define the controller *directly on the
  rotation manifold* $SO(3)/SE(3)$ instead of on Euler angles, giving
  **almost-global** stability — the aircraft can recover from *any* attitude,
  including upside-down. This (Lee et al.) is the basis of aggressive quadrotor
  acrobatics and is the right tool precisely because it has no gimbal-lock
  singularity (recall §1.3) — geometry done right end-to-end.

---

## 8. Guidance

Guidance turns a mission ("visit these waypoints / track this target") into the
reference trajectory the controller chases.

### 8.1 Waypoint following & line-of-sight

The simplest guidance: steer toward the next waypoint, switch when within an
acceptance radius. Naïve "point at the waypoint" cuts corners and overshoots in
wind — hence path-following laws that track the *line between* waypoints, not just
the point.

### 8.2 L1 / pure-pursuit guidance

Pick a **lookahead point** on the desired path a distance $L_1$ ahead, and command
a **lateral acceleration** to arc onto it:
$$
a_{\text{cmd}} = \frac{2V^2}{L_1}\sin\eta,
$$
where $\eta$ is the angle between the velocity vector and the line to the lookahead
point. Elegant properties: it's **adaptive to speed** ($V^2$), gives a smooth
constant-radius capture, and rejects wind/disturbance naturally. L1 is the standard
fixed-wing path-follower (and PX4 uses an L1/NPFG lateral guidance for it);
pure-pursuit is its ground-robot twin.

### 8.3 Trajectory generation — minimum-snap polynomials

For agile multirotors you don't follow lines, you follow **smooth trajectories**.
Because a quadrotor is **differentially flat** in the outputs (position + yaw), any
smooth enough position trajectory is dynamically feasible — and the natural cost is
**snap** (the 4th derivative of position), because snap maps to angular acceleration
and thus to motor commands. Minimize
$$
J = \int_0^T \left\|\frac{d^4\mathbf p}{dt^4}\right\|^2 dt
$$
over piecewise polynomials through the waypoints with continuity constraints
(position, velocity, acceleration, jerk matched at segment boundaries). The result
is a polynomial spline that is smooth, feasible, and minimizes control effort — the
Mellinger–Kumar minimum-snap method that underpins modern agile flight.

### 8.4 VTOL transition guidance

Transition is its own guidance problem: command the acceleration/pitch schedule
that takes the aircraft from hover to wing-borne flight (or back) **safely** —
maintain enough airspeed to avoid stall while not exceeding structural/control
limits, sequencing the tilt or thrust transfer. The guidance must respect that the
plant, the controller gains (§7.6 scheduling), **and the nav sensor trust (§5)** are
all changing simultaneously. It is the regime where G, N, and C are most tightly
and dangerously coupled — and the one to study hardest.

---

## 9. Putting it together — the full GNC loop

### 9.1 The loop-rate hierarchy

| Loop | Rate | Lives in | Consumes | Produces |
|---|---|---|---|---|
| IMU integration / prediction | 200 Hz–1 kHz | EKF2 (FC) | gyro, accel | predicted state |
| Rate control | ~1 kHz | PX4 rate controller (FC) | rate setpoint, gyro | torque/thrust |
| Attitude control | ~250 Hz | PX4 attitude controller (FC) | attitude setpoint, $\hat{\mathbf q}$ | rate setpoint |
| Velocity/position control | ~50 Hz | PX4 position controller (FC) | pos/vel setpoint, EKF2 state | attitude+thrust setpoint |
| Aiding updates (GPS/baro/mag) | 5–50 Hz | EKF2 (FC) | absolute sensors | corrected state |
| **Vision velocity (VO)** | **10–30 Hz** | **`visual_odometry.py` (companion)** | **camera, range** | **body velocity** |
| **Vision position (map-match)** | **0.5–5 Hz** | **`map_match.py` (companion)** | **camera, sat tile** | **absolute fix** |
| Guidance / navigator | 1–10 Hz | PX4 navigator + mission | mission, state | pos/vel setpoints |
| Mission / autonomy | 1–10 Hz | this repo's onboard service | tasking, contacts | mission intent |

The rule: **the further out the loop, the slower and smarter; the further in, the
faster and dumber.** Each layer hides its complexity from the one above.

### 9.2 Where this repo plugs into PX4

```
┌──────────────────────── COMPANION COMPUTER (this repo) ─────────────────────────┐
│                                                                                  │
│  camera frames ─► visual_odometry.py ─(body vel)─┐                               │
│                                                  ├─► manager.py ─► nav_state.py  │
│  camera frames ─► map_match.py ──────(abs fix)───┘   (NavManager)   (6-state KF) │
│      ▲ sat tile+DEM                                       │                      │
│                                              NavEstimate  ▼                      │
│                                            vision_bridge.py                      │
│                                                  │ VISION_POSITION_ESTIMATE      │
└──────────────────────────────────────────────────┼──────────────────────────────┘
                                                    │ MAVLink
┌──────────────────────────── FLIGHT CONTROLLER (PX4) ▼ ───────────────────────────┐
│                                                                                  │
│  IMU/baro/mag/GPS ─► EKF2 (24-state error-state EKF) ◄── external vision update  │
│                          │ fused state x̂                                         │
│                          ▼                                                        │
│   navigator/guidance ─► position ctrl ─► attitude ctrl ─► rate ctrl ─► allocation │
│                                                                          │        │
│                                                                          ▼        │
│                                                                    motors/servos  │
└──────────────────────────────────────────────────────────────────────────────────┘
```

The companion computer is doing the **heavy GPS-denied navigation** PX4 can't, and
injecting its result as *one more measurement* into EKF2 — which then runs the
whole control cascade on a state that stays accurate even with GPS jammed. That is
the entire value proposition of this architecture, and of the field.

---

## 10. Worked error-budget example

**Requirement.** Hold position to **< 10 m CEP** (circular error probable, ≈ the
$1.18\sigma$ radius containing 50% of error) while GPS-denied.

**Contributors** (horizontal, 1-σ, assumed independent):

| Source | 1-σ | Notes |
|---|---|---|
| Map-match fix | $\sigma_{\text{fix}} = 5.0$ m | phase-correlation accuracy from `map_match.py` |
| VO drift between fixes | $\sigma_{\text{drift}}(T)$ | grows with time since last fix |
| Origin / frame error | $\sigma_{\text{frame}} \approx 0.5$ m | equirectangular model + origin uncertainty |

**Step 1 — convert the requirement to 1-σ.** $\text{CEP} \approx 1.18\,\sigma_{\text{total}}$,
so $\sigma_{\text{total}} \le 10/1.18 \approx 8.5$ m.

**Step 2 — solve for the allowable drift budget** (RSS):
$$
\sigma_{\text{drift}}^2 \le \sigma_{\text{total}}^2 - \sigma_{\text{fix}}^2 - \sigma_{\text{frame}}^2
= 8.5^2 - 5.0^2 - 0.5^2 \approx 46.5\ \Rightarrow\ \sigma_{\text{drift}} \le 6.8\ \text{m}.
$$

**Step 3 — relate drift to time.** Model VO velocity error as a random walk: with
per-axis velocity-error PSD from the CV process model (`accel_sigma` $= \sigma_a =
1.5\ \text{m/s}/\sqrt{\text{s}}$), the position drift std over time $T$ between
absolute fixes is approximately
$$
\sigma_{\text{drift}}(T) \approx \sigma_a\,\frac{T^{3/2}}{\sqrt{3}}.
$$
Set $\le 6.8$ m:
$$
T^{3/2} \le \frac{6.8\sqrt{3}}{1.5} = 7.85
\ \Rightarrow\ T \le 7.85^{2/3} \approx 3.9\ \text{s}.
$$

**Conclusion.** To hold 10 m CEP, **the map-matcher must deliver a valid fix at
least every ~3.9 s.** Cross-check against the repo: `DEFAULT_AIDING_TIMEOUT_S = 5 s`
(declare `DEAD_RECKON` past this) and `DEFAULT_MAX_POS_SIGMA = 40 m` (declare `LOST`)
— consistent margins, with the timeout slightly looser because the 40 m `LOST`
gate is the hard floor. **This is what a real error budget produces: a sensor-rate
requirement derived from an accuracy spec.** Tighten any row (better VO, better
map-match) and the required fix rate relaxes; that trade is the engineer's lever.

---

## 11. Practice this week

A concrete, hands-on checklist. Do the math *and* run the code.

- [ ] **Frames.** Implement geodetic→ECEF→NED by hand in a scratch script and verify
      it agrees with `ned_from_ll` from [`nav_state.py`](../navigation/nav_state.py)
      to sub-meter over a 1 km box. Then break it on purpose: swap to ENU and watch
      your altitude sign flip.
- [ ] **Quaternions.** Write `quat_mul`, `quat_rotate`, `quat_to_dcm` from scratch.
      Integrate a constant body rate through 720° and confirm no gimbal lock; do the
      same with Euler angles through pitch = 90° and watch it blow up.
- [ ] **Kalman, derived.** Re-derive the predict/update equations from the
      least-squares cost. Then read `_kalman_update` in
      [`nav_state.py`](../navigation/nav_state.py) line-by-line and identify each of
      $\tilde y, S, K$ in the code.
- [ ] **Kalman, simulated.** Generate a 1-D constant-velocity truth + noisy
      position measurements; implement the KF; plot estimate vs. truth vs.
      measurement and the shrinking covariance. Then sweep $Q/R$ and *watch* the
      lag-vs-jitter tradeoff of §5.5.
- [ ] **Consistency.** Add ground truth to your sim and compute **NEES**; tune until
      it sits near $n$. Then implement the **NIS gate** of §5.4 and inject a single
      outlier — confirm it's rejected.
- [ ] **Drift vs. fix.** Run [`nav_state.py`](../navigation/nav_state.py) with
      `correct_velocity` only (VO) and watch `pos_sigma_m` grow; then start feeding
      periodic `correct_position` and watch it bound. Reproduce the §10 fix-rate
      result empirically.
- [ ] **Read EKF2.** Skim the PX4 `ekf2` derivation/docs and find where
      `VISION_POSITION_ESTIMATE` enters the update; connect it to
      [`vision_bridge.py`](../navigation/vision_bridge.py).
- [ ] **Control.** Implement a 1-D double-integrator (point mass) with a cascade
      P(position)→PID(velocity) controller; tune it; then derive the LQR gain for the
      same plant and compare step responses.
- [ ] **Allan variance.** If you have any IMU (even a phone), log it stationary for
      an hour and plot the Allan deviation; read off the random-walk and
      bias-instability and turn them into a $Q$ and $R$.

---

## 12. Cross-links & further study

**Within this curriculum**
- [Module 01 — First Principles & Systems Engineering](01_first_principles_systems_engineering.md)
  — the modeling discipline and budget thinking that GNC stands on.
- [ML/AI Perception & Autonomy](../ML_AI_AUTONOMY_GUIDE.md) — where the camera
  *features* that feed VO and map-matching come from; perception is the front-end of
  vision-aided nav.
- [Module 06 — Simulation, Test & Verification](06_simulation_test_verification.md)
  — SITL, HITL, and how you *prove* a filter is consistent before it flies.

**Within this repo (read the code as primary text)**
- [`navigation/nav_state.py`](../navigation/nav_state.py) — the 6-state CV Kalman filter.
- [`navigation/manager.py`](../navigation/manager.py) — phase-aware multi-source fusion.
- [`navigation/visual_odometry.py`](../navigation/visual_odometry.py) — relative velocity from flow.
- [`navigation/map_match.py`](../navigation/map_match.py) — absolute fix by phase correlation.
- [`navigation/vision_bridge.py`](../navigation/vision_bridge.py) — the seam into PX4 EKF2.

**Canonical references**
- Farrell, *Aided Navigation: GPS with High Rate Sensors* — the bible of INS/GNSS fusion.
- Groves, *Principles of GNSS, Inertial, and Multisensor Integrated Navigation Systems*.
- Bar-Shalom, Li & Kirubarajan, *Estimation with Applications to Tracking and Navigation* — KF/EKF/consistency done rigorously.
- Thrun, Burgard & Fox, *Probabilistic Robotics* — filters, PFs, and SLAM.
- Beard & McLain, *Small Unmanned Aircraft: Theory and Practice* — the GNC stack end-to-end for fixed-wing/VTOL.
- Lee, Leok & McClamroch, *Geometric Tracking Control of a Quadrotor UAV on SE(3)*.
- Mellinger & Kumar, *Minimum Snap Trajectory Generation and Control for Quadrotors*.
- The PX4 **ECL/EKF2** source and dev docs — the production EKF you are feeding.

---

## Sources & Citations

> **Relocation note.** This module was moved out of `drone/MASTERY/` into the
> flat `learning/` folder. Sibling links that used to be relative now map to:
> the ML/perception companion → [20-autonomy-ml-ai.md](20-autonomy-ml-ai.md);
> control-theory deep dive → [25-autonomy-control-theory.md](25-autonomy-control-theory.md);
> the planning module → [29-autonomy-planning-decision.md](29-autonomy-planning-decision.md).
> Inline `../navigation/...` links point at the author's `pixhawk/drone/` source
> and are kept as code references. Modules 01/06 referenced above are planned,
> not yet written.

**Estimation, navigation & GNC (canonical)**
- Farrell, J. — *Aided Navigation: GPS with High Rate Sensors*, McGraw-Hill.
- Groves, P. — *Principles of GNSS, Inertial, and Multisensor Integrated Navigation Systems*, Artech House.
- Bar-Shalom, Li & Kirubarajan — *Estimation with Applications to Tracking and Navigation*, Wiley.
- Thrun, Burgard & Fox — *Probabilistic Robotics*, MIT Press.
- Beard & McLain — *Small Unmanned Aircraft: Theory and Practice*, Princeton.
- Stengel, R. — *Optimal Control and Estimation*, Dover.
- Sola, J. — *Quaternion kinematics for the error-state Kalman filter* (arXiv:1711.02508).
- Sola, Deray, Atchuthan — *A micro Lie theory for state estimation in robotics* (arXiv:1812.01537).

**Key papers**
- Lee, Leok & McClamroch — *Geometric Tracking Control of a Quadrotor UAV on SE(3)* (IEEE CDC 2010).
- Mellinger & Kumar — *Minimum Snap Trajectory Generation and Control for Quadrotors* (ICRA 2011).
- Qin, Li & Shen — *VINS-Mono: A Robust and Versatile Monocular Visual-Inertial State Estimator* (IEEE T-RO 2018).

**Official docs**
- PX4 ECL/EKF2 & state estimation: https://docs.px4.io
- IEEE/ION GNSS standards & WGS84 (NGA): https://earth-info.nga.mil

---

*End of Module 03. Re-derive the boxed equations until the Kalman gain feels
obvious; then the rest of autonomy is commentary.*
