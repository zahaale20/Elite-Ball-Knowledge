# Sensor Fusion — Combining IMU, GNSS, Vision & LiDAR

> **Why this exists.** No single sensor is sufficient for autonomy. An IMU is
> fast and self-contained but drifts without bound in seconds. GNSS is globally
> referenced but slow, jammable, and silent indoors. A camera is rich but scaleless
> and light-dependent. LiDAR is geometrically precise but blind to semantics and
> useless in fog. Sensor fusion is the discipline of combining these complementary,
> imperfect streams into one state estimate that is better than any input — and,
> crucially, that *knows how uncertain it is*. Every flying, driving, or walking
> autonomous system is, at its core, a sensor-fusion engine.
>
> **What mastering it makes you.** The engineer who can diagnose why a
> vision-inertial estimate "walks away" when the vehicle stops (it's the
> observability collapse of an accelerometer at zero acceleration), who knows
> exactly which states an error-state filter should carry, and who treats time
> synchronization and extrinsic calibration as first-class problems rather than
> afterthoughts.

Fusion is where the perception of [11-autonomy-perception-deep.md](11-perception-deep.md)
and the maps of [12-autonomy-slam-and-mapping.md](12-slam-and-mapping.md)
meet the estimation core of [09-autonomy-gnc.md](09-gnc.md). The
factor-graph form of fusion (and why smoothing beats filtering) is developed in
[14-autonomy-state-estimation-advanced.md](14-state-estimation-advanced.md).
The probability and matrix calculus are from
[03-foundations-mathematics.md](../foundations/03-mathematics.md); the fused estimate
ultimately closes the loop of the controllers in
[06-autonomy-control-theory.md](06-control-theory.md). Validate every
fusion claim in simulation per
[06-foundations-simulation-test-verification.md](../foundations/06-simulation-test-verification.md).

---

## Table of Contents

1. [Why fuse — the complementarity argument](#1-why-fuse--the-complementarity-argument)
2. [The complementary filter — fusion's simplest form](#2-the-complementary-filter--fusions-simplest-form)
3. [The Kalman filter family for fusion](#3-the-kalman-filter-family-for-fusion)
4. [The error-state (indirect) Kalman filter](#4-the-error-state-indirect-kalman-filter)
5. [IMU preintegration](#5-imu-preintegration)
6. [Time synchronization](#6-time-synchronization)
7. [Extrinsic and temporal calibration](#7-extrinsic-and-temporal-calibration)
8. [Observability — what the fused system can and cannot know](#8-observability--what-the-fused-system-can-and-cannot-know)
9. [Practice this week](#9-practice-this-week)
10. [Sources & further study](#10-sources--further-study)
11. [The Insider Layer — what the field knows but rarely writes down](#-the-insider-layer--what-the-field-knows-but-rarely-writes-down)

---

## 1. Why fuse — the complementarity argument

Fusion works because sensor error spectra are complementary. An IMU is accurate
*at high frequency* but drifts at low frequency; an absolute sensor (GNSS, vision,
LiDAR) is accurate *at low frequency* but noisy or slow at high frequency. Fuse
them so each covers the other's blind band.

| Sensor | Rate | Drifts? | Absolute? | Fails when |
|---|---|---|---|---|
| IMU (accel + gyro) | 100–1000 Hz | yes, unboundedly | no | always integrating error |
| GNSS | 1–10 Hz | no | yes (global) | indoors, jamming, urban canyon |
| Camera (VO/VIO) | 20–60 Hz | slowly | no (scaleless alone) | low light, low texture |
| LiDAR | 10–20 Hz | slowly | no | fog, rain, featureless tunnels |
| Magnetometer | 50 Hz | no | yes (heading) | near ferrous metal / motors |
| Barometer | 50 Hz | slowly | yes (altitude) | weather pressure changes |

The information-theoretic statement: the fused information is the **sum of the
individual Fisher informations** (for independent measurements),
$\Omega_\text{fused} = \sum_i \Omega_i$, so the fused covariance is always smaller
than any single sensor's — *provided the measurements are consistent and properly
weighted*. Mis-weight them and fusion makes things worse, not better.

---

## 2. The complementary filter — fusion's simplest form

Before reaching for a Kalman filter, understand the complementary filter — it is
fusion stripped to its essence and still runs on millions of flight controllers.
For attitude, fuse the high-frequency gyro integral with the low-frequency
accelerometer (which measures gravity direction):

$$
\hat\theta = \alpha\,(\hat\theta_{prev} + \dot\theta_\text{gyro}\,\Delta t) + (1-\alpha)\,\theta_\text{accel}.
$$

The gyro term passes through a high-pass, the accel term through a low-pass, with
crossover set by $\alpha$. The Mahony and Madgwick filters generalize this to
$SO(3)$ with a PI correction driven by the cross product of measured and predicted
gravity. The complementary filter *is* a steady-state Kalman filter with a
hand-chosen gain — useful to know when you need fusion with zero matrix algebra.

---

## 3. The Kalman filter family for fusion

The general tool is the Kalman filter (derived in
[09-autonomy-gnc.md](09-gnc.md)). For fusion the structure is:
**propagate** the state with the fast sensor (IMU as the *process model*, not a
measurement), and **update** with each absolute sensor as it arrives.

### 3.1 The EKF for nonlinear fusion

Most fusion is nonlinear (rotations, projection), so we linearize. The Extended
Kalman Filter propagates the mean through the true nonlinearity and the covariance
through the Jacobian:

$$
\hat{\mathbf{x}}_{k|k-1} = f(\hat{\mathbf{x}}_{k-1}, \mathbf{u}_k), \qquad
P_{k|k-1} = F_k P_{k-1} F_k^\top + Q_k, \quad F_k = \left.\frac{\partial f}{\partial \mathbf{x}}\right|_{\hat{\mathbf{x}}_{k-1}}.
$$

$$
K_k = P_{k|k-1} H_k^\top (H_k P_{k|k-1} H_k^\top + R_k)^{-1}, \qquad
\hat{\mathbf{x}}_k = \hat{\mathbf{x}}_{k|k-1} + K_k\big(\mathbf{z}_k - h(\hat{\mathbf{x}}_{k|k-1})\big).
$$

### 3.2 The UKF — when Jacobians are nasty

The Unscented Kalman Filter avoids Jacobians by propagating a deterministic set of
**sigma points** $\mathcal{X}^{(i)}$ through the true nonlinearity and recomputing
the mean and covariance:

$$
\mathcal{X}^{(i)} = \hat{\mathbf{x}} \pm \big(\sqrt{(n+\lambda)P}\big)_i, \qquad
\hat{\mathbf{x}}' = \sum_i W_m^{(i)} f(\mathcal{X}^{(i)}).
$$

The UKF captures the mean to second order and the covariance more faithfully than
the EKF's first-order linearization, at modest extra cost. It shines when $h$ or
$f$ are strongly nonlinear (e.g., bearing-only fusion).

---

## 4. The error-state (indirect) Kalman filter

The single most important idea in modern inertial fusion: **do not filter the
state directly — filter the *error* of a state that is integrated separately.**
This is the Error-State Kalman Filter (ESKF), the heart of PX4's EKF2, the MSCKF,
and most VIO systems.

The nominal state $\mathbf{x}$ (position, velocity, quaternion, biases) is
integrated open-loop from the IMU at full rate. The filter estimates the small
error $\delta\mathbf{x}$ between nominal and true:

$$
\mathbf{x}_\text{true} = \mathbf{x}_\text{nominal} \oplus \delta\mathbf{x},
$$

where $\oplus$ is additive for vectors and a small-angle rotation composition for
orientation: $\mathbf{q}_\text{true} = \mathbf{q}_\text{nom} \otimes \delta\mathbf{q}(\delta\boldsymbol\theta)$.

Why this is brilliant:
- The error state stays **small**, so its dynamics are **nearly linear** — the EKF
  linearization is excellent.
- Orientation error is a minimal **3-parameter** rotation vector $\delta\boldsymbol\theta$,
  avoiding the quaternion's overparameterization and singular covariance.
- The expensive nonlinear integration runs at IMU rate; the filter update runs
  only when an absolute measurement arrives.

The error-state continuous dynamics for the velocity/attitude block:

$$
\delta\dot{\mathbf{v}} = -R[\mathbf{a}_m - \mathbf{b}_a]_\times \delta\boldsymbol\theta - R\,\delta\mathbf{b}_a - R\,\mathbf{n}_a,
\qquad
\delta\dot{\boldsymbol\theta} = -[\boldsymbol\omega_m - \mathbf{b}_g]_\times \delta\boldsymbol\theta - \delta\mathbf{b}_g - \mathbf{n}_g.
$$

After each update, **inject** the estimated error into the nominal state and
**reset** $\delta\mathbf{x} \leftarrow 0$ — keeping the error perpetually small.

---

## 5. IMU preintegration

In a factor-graph back-end (see
[14-autonomy-state-estimation-advanced.md](14-state-estimation-advanced.md)),
you cannot re-integrate hundreds of IMU samples every time the optimizer relinearizes
a pose. **IMU preintegration** (Forster et al.) solves this by integrating the IMU
between two keyframes *in the body frame*, independent of the initial pose, into a
single relative-motion constraint:

$$
\Delta R_{ij} = \prod_{k=i}^{j-1} \mathrm{Exp}\big((\boldsymbol\omega_k - \mathbf{b}_g)\Delta t\big),
$$
$$
\Delta \mathbf{v}_{ij} = \sum_{k=i}^{j-1} \Delta R_{ik}(\mathbf{a}_k - \mathbf{b}_a)\Delta t,
\qquad
\Delta \mathbf{p}_{ij} = \sum_{k=i}^{j-1} \Big[\Delta \mathbf{v}_{ik}\Delta t + \tfrac{1}{2}\Delta R_{ik}(\mathbf{a}_k - \mathbf{b}_a)\Delta t^2\Big].
$$

These preintegrated $\Delta R, \Delta\mathbf{v}, \Delta\mathbf{p}$ become a single
factor with an analytically propagated covariance and a **bias-correction Jacobian**
$\partial \Delta R / \partial \mathbf{b}_g$ so the constraint can be cheaply
adjusted when the bias estimate changes — without re-integrating. This is the
enabling trick behind VINS-Mono, ORB-SLAM3's VI mode, and OKVIS.

---

## 6. Time synchronization

Fusion math assumes all measurements carry a *common, correct timestamp*. In
reality every sensor has its own clock, latency, and triggering jitter. Fuse a
GNSS fix stamped 40 ms late against an IMU and you inject a position error equal
to (velocity × 40 ms) — at 20 m/s that is 0.8 m of pure timing error.

Rules of the trade:
- **Hardware-timestamp at the source** (PPS from GNSS, trigger lines for cameras)
  whenever possible; software timestamps at receipt are last resort.
- Model each sensor's **constant latency** $t_d$ as a calibratable parameter and
  *predict the state forward to the measurement's true time* before updating.
- Use a single monotonic clock domain; convert all sensors into it with estimated
  offsets. ROS 2 and PTP/gPTP exist precisely for this.

The update with a known delay $t_d$:

$$
\hat{\mathbf{x}}_k = \hat{\mathbf{x}}(t_\text{meas} - t_d) + K_k\big(\mathbf{z}_k - h(\hat{\mathbf{x}}(t_\text{meas}-t_d))\big),
$$

i.e., compare the measurement to the state *as it was when the measurement was
taken*, not to "now."

---

## 7. Extrinsic and temporal calibration

Fusion requires the rigid transform $T_{BS} \in SE(3)$ from each sensor frame $S$
to the body frame $B$. A 1° camera-to-IMU rotation error rotates every visual
measurement and biases the entire estimate. Calibration estimates these
extrinsics — and often the time offset $t_d$ — jointly.

The standard tool is **Kalibr** (Furgale et al.), which solves a batch
maximum-likelihood problem over a continuous-time B-spline trajectory, the
extrinsics, and the time offset:

$$
\min_{T_{BS},\, t_d,\, \text{traj}} \sum \|\mathbf{r}_\text{visual}\|^2_{\Sigma_v} + \sum \|\mathbf{r}_\text{IMU}\|^2_{\Sigma_i}.
$$

A practical hierarchy: intrinsics first (per sensor), then extrinsics
(sensor-to-sensor), then temporal offset — each stage feeding the next. Treat
calibration as a recurring maintenance task, not a one-time event: thermal cycling
and vibration walk the extrinsics over a vehicle's life.

---

## 8. Observability — what the fused system can and cannot know

The deepest question in fusion: *which states are actually determined by the
measurements?* A state that is unobservable cannot be estimated no matter how good
the filter — and a filter that pretends otherwise becomes inconsistent.

### 8.1 The visual-inertial unobservable subspace

A monocular VIO system has **four** unobservable directions: global position (3)
and rotation about gravity / yaw (1). Roll and pitch *are* observable because the
accelerometer senses gravity. Metric scale is observable only because the IMU
provides an absolute acceleration reference — pure monocular vision alone leaves
scale unobservable too.

### 8.2 The degenerate-motion trap

Observability is **motion-dependent**. Critical cases:
- **Constant velocity / hover:** accelerometer reads only gravity, so accelerometer
  bias and scale become *temporarily unobservable*. This is why a VIO estimate can
  drift in a stationary hover — there is no excitation.
- **Constant acceleration:** gyro bias along certain axes loses observability.

The linear-algebraic test is the rank of the observability matrix (or, in the
nonlinear case, the Lie-derivative observability matrix). The practical lesson:
**excitation is information.** Wiggling the vehicle at initialization is not
superstition; it makes the biases and scale observable.

### 8.3 Consistency, again

Run NEES against simulated ground truth (as in
[12-autonomy-slam-and-mapping.md](12-slam-and-mapping.md) §8). A
first-estimates-Jacobian (FEJ) EKF or an observability-constrained filter keeps the
filter from injecting fake information into the unobservable subspace — the single
most common cause of a fusion estimate that is confident *and wrong*.

---

## 9. Practice this week

1. Implement a Madgwick/Mahony complementary filter on real IMU logs; compare its
   attitude to a full EKF.
2. Build an error-state Kalman filter fusing IMU + GNSS in simulation; inject a
   40 ms GNSS latency and watch the position error, then correct it with delayed
   updates.
3. Run Kalibr (or its tutorial dataset) to recover camera-IMU extrinsics and time
   offset; perturb the extrinsic by 1° and observe the estimate degrade.
4. Reproduce the hover-drift observability failure: run VIO on a stationary segment
   and watch the bias estimate wander.

---

## 10. Sources & further study

- **Sola — "Quaternion Kinematics for the Error-State Kalman Filter."** The clearest
  derivation of the ESKF; essential reading.
- **Forster, Carlone, Dellaert & Scaramuzza — "On-Manifold Preintegration for
  Real-Time Visual-Inertial Odometry"** (IEEE T-RO, 2017).
- **Mourikis & Roumeliotis — "A Multi-State Constraint Kalman Filter for
  Vision-Aided Inertial Navigation"** (MSCKF), ICRA 2007.
- **Qin, Li & Shen — "VINS-Mono."** A complete, readable VIO system.
- **Furgale, Rehder & Siegwart — "Unified Temporal and Spatial Calibration"** (Kalibr).
- **Barfoot — *State Estimation for Robotics*.** On-manifold estimation and
  observability.
- **Groves — *Principles of GNSS, Inertial, and Multisensor Integrated Navigation
  Systems*.** The integrated-navigation reference; pairs with
  [07-autonomy-gnss-jamming-spoofing.md](07-gnss-jamming-spoofing.md).

> Framing note: Sensor fusion is not "average the sensors." It is the disciplined
> propagation of *information* with honest uncertainty, anchored by correct time
> and calibration, and bounded by what the motion actually makes observable. The
> engineers who ship robust navigation are the ones who ask "is this state even
> observable right now?" before they ask "why is my filter wrong?"

---

## ⚡ The Insider Layer — What the Field Knows but Rarely Writes Down

Fusion is the discipline where the math is elegant and the bugs are physical.
Textbooks give you the Kalman update; the field gives you the reasons it diverges
in the parking lot. Here is what the second category looks like.

### Time synchronization is the silent killer, not the math

If you ask a seasoned navigation engineer where fusion bugs come from, the first
answer is *timestamps*, not algorithms. Every sensor stamps with a different
clock, a different latency, and a different jitter. A camera frame is timestamped
at end-of-exposure on some boards and at start-of-readout on others; USB and
Ethernet add tens of milliseconds of variable transport delay; the IMU's "now"
and the GPS's "now" differ by an unknown bias. At vehicle speeds a 10 ms sync
error is a centimeters-to-decimeters position error injected *every update*, and
it looks exactly like sensor noise so you tune $R$ up to hide it and quietly
destroy your accuracy. The professional move is **hardware time sync (PPS/PTP) or
estimating the temporal offset as a state** (Kalibr does this offline). The
heuristic: if your filter is consistent when stationary but degrades with
dynamics, suspect timing before you suspect the model.

### Extrinsic calibration ages, and nobody budgets for it

The lever-arm and rotation between IMU and camera/LiDAR are treated as constants
in every derivation. In the field they drift — thermal cycling, vibration, a
technician bumping the sensor pod, a chassis that flexes under load. A 1 cm
lever-arm error or a 0.5° rotation error produces a *velocity-dependent* bias
that no amount of noise tuning fixes. Shops that ship reliable navigation run
**online extrinsic estimation** (carry the calibration as slowly-varying states)
and **periodic recalibration as scheduled maintenance**. The unwritten rule:
calibration is not a one-time setup step, it is a consumable.

### The standstill paradox and observability you can feel

The classic counterintuitive failure: a visual-inertial estimate that is rock
solid while moving "walks away" the moment the vehicle stops. The reason is deep
— at zero acceleration the accelerometer bias and the gravity-aligned states
become **unobservable**, and the filter, getting no information, lets bias and
velocity estimates random-walk. Veterans recognize this signature instantly and
either inject a **zero-velocity update (ZUPT)** when they detect standstill or
constrain the unobservable subspace. The lesson textbooks underplay: *fusion
quality is a function of the motion, not just the sensors*. Excitation is
information. A figure-eight at startup is not superstition; it is making your
biases observable.

### Don't average sensors — propagate information, and watch for double-counting

The naïve mental model "fusion = weighted average" causes a specific, common bug:
**correlated measurements counted as independent**. If two estimators both
consumed the same GPS fix, fusing their outputs as if they were independent makes
the filter wildly over-confident (this is the whole reason covariance
intersection exists for decentralized fusion). The error-state/indirect KF and
factor graphs are popular precisely because they keep the information accounting
honest. If your covariance is shrinking faster than physics allows, you are
double-counting something.

### Tuning $Q$ and $R$ is empirical, and the diagnostic is NIS

No one derives the process-noise matrix $Q$ from first principles in production —
it is the knob that absorbs all your unmodeled dynamics, and it is tuned by
**making the Normalized Innovation Squared (NIS) sit inside its $\chi^2$ band**.
Too-small $Q$/$R$ → over-confident filter that rejects good measurements and
diverges; too-large → sluggish, noisy estimate. The pro skill is reading the NIS
trace like an EKG: a spike at every turn means your motion model (often constant-
velocity) is too weak — reach for an IMM or higher-order model rather than just
inflating noise.

### Gating, outliers, and the GPS that lies in cities

A single bad measurement can corrupt the estimate for seconds. Multipath GNSS in
urban canyons produces fixes that are *confidently wrong* by tens of meters —
the receiver reports a tight covariance for a reflected signal. Mahalanobis
gating (reject measurements with NIS above a $\chi^2$ threshold) is mandatory,
and chi-square innovation tests plus RAIM-style consistency checks are how the
field survives spoofing and multipath. Trusting a sensor's self-reported
covariance without an independent gate is a rookie mistake with expensive
consequences.

### Norms worth carrying

- **Build the error-state filter, not the direct one**, for anything with
  attitude — it keeps the covariance in the tangent space and avoids quaternion
  normalization headaches.
- **Log innovations and NIS always.** They are free and they are the truth serum
  of estimation.
- **Smoothing beats filtering** when latency allows; a fixed-lag smoother buys
  accuracy a filter cannot (see the factor-graph module).
- **The integration software is harder than the algorithm.** Most real fusion
  effort is buffering, interpolation to a common timestamp, and out-of-order
  measurement handling — not deriving a Jacobian.

The through-line: fusion fails for physical reasons — clocks, mounts, motion —
that hide behind clean equations. The engineers who ship robust navigation debug
the plumbing first and ask "is this state even observable right now?" before
they touch a gain.
