# Physics for Engineers — The Mechanics That Govern Real Systems

> **Why this exists.** Every controller you design, every estimator you tune, every trajectory you plan acts on a *physical plant* governed by Newton, Euler, and Lagrange. If you do not understand rigid-body dynamics in your bones, you will write quaternion code that gimbal-locks, size an actuator that cannot overcome inertia, or model a drone as a point mass and be baffled when it tumbles. Physics is the ground truth beneath the abstractions — the place where your simulation either matches reality or quietly lies to you. Mastering mechanics is what separates an engineer who *uses* a dynamics model from one who can *derive* and *trust* it.

> **What mastering it makes you.** The person who can write the equations of motion for a tilt-rotor from scratch, explain why a spinning body precesses, choose the right reference frame so the math collapses to something tractable, and predict resonances before they shake an airframe apart. You become the bridge between the clean linear models of control theory and the messy nonlinear reality of flight.

This module supplies the plant models that [07-foundations-control-advanced.md](07-control-advanced.md) controls and [06-autonomy-control-theory.md](../autonomy/06-control-theory.md) stabilizes. The dynamics here feed guidance and navigation in [09-autonomy-gnc.md](../autonomy/09-gnc.md) and the simulation fidelity discussed in [01_first_principles_systems_engineering.md](../foundations/01-first_principles_systems_engineering.md). The mathematical machinery — vector calculus, linear algebra, differential equations — is developed in [03-foundations-mathematics.md](../foundations/03-mathematics.md). Energy and continuum extensions live in [09-foundations-thermodynamics-and-fluids.md](09-thermodynamics-and-fluids.md); the field theory governing sensors and comms in [10-foundations-electromagnetics.md](10-electromagnetics.md).

---

## 1. Newton's laws — and why they are subtler than they look

Newton's second law $\mathbf{F} = m\mathbf{a}$ is deceptively simple. The subtleties that bite engineers:

1. It holds only in an **inertial frame**. Write it in a rotating body frame and fictitious forces (centrifugal, Coriolis) appear.
2. $\mathbf{a}$ is the acceleration of the **center of mass**; internal forces cancel by Newton's third law.
3. For variable-mass systems (rockets), the correct form is $\mathbf{F} = \dfrac{d\mathbf{p}}{dt}$, which produces the Tsiolkovsky equation, *not* $m\mathbf{a}$.

The momentum form is primary:

$$
\mathbf{F}_{\text{ext}} = \frac{d\mathbf{p}}{dt}, \qquad \mathbf{p} = m\mathbf{v}_{\text{cm}}.
$$

### 1.1 Worked example — the rocket equation

A rocket of mass $m$ ejects propellant at exhaust velocity $u$ (relative to the rocket) at rate $\dot m < 0$. Conservation of momentum in free space gives

$$
m\,\dot v = -u\,\dot m \;\Longrightarrow\; \Delta v = u \ln\!\frac{m_0}{m_f}.
$$

This single logarithm dictates the entire architecture of space launch: payload fraction falls *exponentially* in required $\Delta v$, which is why staging exists. Physics, not engineering preference, forces the design.

---

## 2. Rotational dynamics — where intuition fails

Translation has the clean analogy $\mathbf{F}=m\mathbf{a}$. Rotation is treacherous because the "mass" — the inertia tensor — is a $3\times3$ matrix, and angular velocity does not integrate to a meaningful "angle."

### 2.1 The inertia tensor

For a rigid body, angular momentum about the center of mass is

$$
\mathbf{L} = \mathbf{I}\,\boldsymbol\omega, \qquad
\mathbf{I} = \begin{bmatrix} I_{xx} & -I_{xy} & -I_{xz} \\ -I_{xy} & I_{yy} & -I_{yz} \\ -I_{xz} & -I_{yz} & I_{zz} \end{bmatrix},
$$

with $I_{xx} = \int (y^2 + z^2)\,dm$ and products $I_{xy} = \int xy\,dm$. Crucially $\mathbf{L}$ and $\boldsymbol\omega$ are **not parallel** unless $\boldsymbol\omega$ lies along a principal axis. Diagonalizing $\mathbf{I}$ (an eigenvalue problem — see [03-foundations-mathematics.md](../foundations/03-mathematics.md)) yields the **principal axes** and principal moments $I_1, I_2, I_3$.

### 2.2 Euler's equations

In the body frame, Newton's rotational law $\boldsymbol\tau = d\mathbf{L}/dt$ must account for the rotating frame. Using the transport theorem $\left.\frac{d}{dt}\right|_{\text{inertial}} = \left.\frac{d}{dt}\right|_{\text{body}} + \boldsymbol\omega \times$:

$$
\boxed{\;
\begin{aligned}
I_1 \dot\omega_1 &= (I_2 - I_3)\,\omega_2 \omega_3 + \tau_1, \\
I_2 \dot\omega_2 &= (I_3 - I_1)\,\omega_3 \omega_1 + \tau_2, \\
I_3 \dot\omega_3 &= (I_1 - I_2)\,\omega_1 \omega_2 + \tau_3.
\end{aligned}\;}
$$

The gyroscopic coupling terms $(I_j - I_k)\omega_j\omega_k$ are the source of every counterintuitive spinning-body effect.

### 2.3 The tennis-racket (Dzhanibekov) theorem

Linearize Euler's equations about steady spin around each principal axis. Rotation about the axes of *largest* ($I_3$) and *smallest* ($I_1$) moment is stable; rotation about the **intermediate** axis ($I_2$) is unstable — the body flips chaotically. This is not a curiosity: spacecraft and tumbling debris obey it, and reaction-wheel sizing must respect it.

---

## 3. Attitude representations — and why quaternions win

Orientation seems like "three angles," but every minimal three-parameter representation has a singularity.

| Representation | Params | Singularity | Use |
|---|---|---|---|
| Euler angles | 3 | gimbal lock at $\pm 90°$ | human display |
| Rotation matrix | 9 (6 constraints) | none | composition |
| Axis-angle | 4 | $\theta = 0$ ambiguity | interpolation |
| **Unit quaternion** | 4 (1 constraint) | **none** | flight code |

The quaternion kinematics — the workhorse of every flight controller — is

$$
\dot{\mathbf{q}} = \tfrac12\, \mathbf{q} \otimes \begin{bmatrix} 0 \\ \boldsymbol\omega \end{bmatrix},
$$

a *linear* ODE in $\mathbf q$ given $\boldsymbol\omega$, free of trigonometric singularities. Gimbal lock — when two Euler axes align and a degree of freedom vanishes — is a pure artifact of the chart, not the physics; quaternions avoid it by living on the 3-sphere $S^3$.

---

## 4. The Lagrangian formulation — geometry over force

Newton needs every constraint force explicitly. Lagrange eliminates them. Define generalized coordinates $q_i$ and the **Lagrangian**

$$
\mathcal{L} = T - V \quad (\text{kinetic} - \text{potential energy}).
$$

The Euler–Lagrange equations follow from the **principle of stationary action** $\delta \int \mathcal{L}\,dt = 0$:

$$
\boxed{\;\frac{d}{dt}\!\left( \frac{\partial \mathcal{L}}{\partial \dot q_i} \right) - \frac{\partial \mathcal{L}}{\partial q_i} = Q_i,\;}
$$

with $Q_i$ the non-conservative generalized forces. Constraint forces that do no work vanish automatically — a colossal simplification for linkages, manipulators, and multi-body vehicles.

### 4.1 Worked example — the planar pendulum

With angle $\theta$, length $\ell$, mass $m$: $T = \tfrac12 m\ell^2\dot\theta^2$, $V = -mg\ell\cos\theta$. Then

$$
\frac{\partial \mathcal L}{\partial \dot\theta} = m\ell^2\dot\theta, \quad
\frac{\partial \mathcal L}{\partial \theta} = -mg\ell\sin\theta
\;\Longrightarrow\;
m\ell^2\ddot\theta + mg\ell\sin\theta = 0,
$$

i.e. $\ddot\theta + \tfrac{g}{\ell}\sin\theta = 0$. No tension force ever appeared. For small angles $\sin\theta \approx \theta$, recovering simple harmonic motion at $\omega = \sqrt{g/\ell}$.

For a manipulator with coordinates $\mathbf q$, the Lagrangian machinery yields the canonical robot equation

$$
M(\mathbf q)\ddot{\mathbf q} + C(\mathbf q, \dot{\mathbf q})\dot{\mathbf q} + G(\mathbf q) = \boldsymbol\tau,
$$

with mass matrix $M$, Coriolis/centrifugal $C$, and gravity $G$ — the starting point for computed-torque control.

---

## 5. The Hamiltonian formulation — and the bridge to optimal control

Define conjugate momenta $p_i = \partial \mathcal{L}/\partial \dot q_i$ and the **Hamiltonian** via Legendre transform:

$$
H(\mathbf q, \mathbf p) = \sum_i p_i \dot q_i - \mathcal{L} = T + V \;(\text{total energy, for natural systems}).
$$

Hamilton's equations are first-order and symmetric:

$$
\dot q_i = \frac{\partial H}{\partial p_i}, \qquad \dot p_i = -\frac{\partial H}{\partial q_i}.
$$

This phase-space view is the doorway to **Pontryagin's Maximum Principle** in optimal control (see [07-foundations-control-advanced.md](07-control-advanced.md)): the costate $\boldsymbol\lambda$ obeys exactly $\dot{\boldsymbol\lambda} = -\partial H/\partial \mathbf x$. Mechanics and optimal control are the *same mathematics*. Noether's theorem ties each continuous symmetry of $\mathcal L$ to a conserved quantity — time-invariance to energy, rotational symmetry to angular momentum — giving you free integrals of motion to validate simulations.

---

## 6. Oscillations, modes, and resonance

Linearize any conservative system about equilibrium and you get coupled oscillators:

$$
M\ddot{\mathbf x} + K\mathbf x = 0.
$$

Solving the generalized eigenproblem $K\mathbf v = \omega^2 M \mathbf v$ yields **natural frequencies** $\omega_i$ and **mode shapes** $\mathbf v_i$. Any motion decomposes into these modes. Add damping and forcing:

$$
m\ddot x + c\dot x + kx = F_0\cos\Omega t,
$$

with steady-state amplitude

$$
|X| = \frac{F_0/k}{\sqrt{(1 - r^2)^2 + (2\zeta r)^2}}, \qquad r = \Omega/\omega_n, \; \zeta = \frac{c}{2\sqrt{km}}.
$$

At $r=1$ the response peaks — **resonance** — limited only by damping. This is why every airframe undergoes modal/flutter analysis: a control loop or rotor harmonic that excites a structural mode at $\omega_n$ can destroy the vehicle (Tacoma Narrows, helicopter ground resonance). The flexible modes here are exactly what the $W_T$ robustness weighting in $\mathcal{H}_\infty$ control must roll off.

---

## 7. Reference frames — choosing the frame that makes math vanish

Half of dynamics is bookkeeping; the right frame collapses it.

Transport theorem (any vector $\mathbf a$, frame rotating at $\boldsymbol\Omega$):

$$
\left.\frac{d\mathbf a}{dt}\right|_{\text{inertial}} = \left.\frac{d\mathbf a}{dt}\right|_{\text{rot}} + \boldsymbol\Omega \times \mathbf a.
$$

Apply twice to position to get acceleration in a rotating frame:

$$
\mathbf a_{\text{in}} = \mathbf a_{\text{rot}} + 2\boldsymbol\Omega \times \mathbf v_{\text{rot}} + \boldsymbol\Omega \times (\boldsymbol\Omega \times \mathbf r) + \dot{\boldsymbol\Omega}\times\mathbf r.
$$

The terms are the **Coriolis**, **centrifugal**, and **Euler** accelerations. For flight near Earth, the standard hierarchy is ECI → ECEF → NED → body, each transformation a rotation matrix or quaternion. Choosing **body frame** for attitude (inertia tensor is constant there) and **NED** for navigation is what makes onboard estimation tractable — directly relevant to [09-autonomy-gnc.md](../autonomy/09-gnc.md).

```python
import numpy as np

def euler_step(omega, I, tau, dt):
    """One step of Euler's rigid-body equations in the body frame."""
    I1, I2, I3 = np.diag(I)               # principal moments
    w1, w2, w3 = omega
    dw = np.array([
        ((I2 - I3) * w2 * w3 + tau[0]) / I1,
        ((I3 - I1) * w3 * w1 + tau[1]) / I2,
        ((I1 - I2) * w1 * w2 + tau[2]) / I3,
    ])
    return omega + dw * dt

# Demonstrate intermediate-axis instability (Dzhanibekov effect).
I = np.diag([1.0, 2.0, 3.0])             # I2 is intermediate
omega = np.array([0.01, 1.0, 0.01])      # spin mostly about axis 2
for _ in range(2000):
    omega = euler_step(omega, I, np.zeros(3), 0.01)
print("omega grows/flips on the intermediate axis:", omega)
```

---

## 8. Dimensional analysis and scaling — sanity before simulation

Before any numerical model, the **Buckingham $\pi$ theorem** tells you how many independent dimensionless groups govern a problem. For a flapping or rotating wing, the Reynolds number $Re = \rho U L/\mu$ and Strouhal number $St = fL/U$ predict regime changes. Scaling laws explain why small drones behave qualitatively differently from large aircraft: inertia scales as $L^5$, aerodynamic forces as $L^2$, so agility *increases* as vehicles shrink. This dimensional reasoning is the first-principles check demanded by [01_first_principles_systems_engineering.md](../foundations/01-first_principles_systems_engineering.md) — if your simulation violates a scaling law, the simulation is wrong.

---

## 9. From physics to plant model — the engineering payoff

| Physics concept | Control/autonomy consequence |
|---|---|
| Inertia tensor diagonalization | decoupled axis controllers |
| Euler's gyroscopic coupling | cross-axis feedforward |
| Quaternion kinematics | singularity-free attitude estimation |
| Modal analysis | notch filters, flutter margins |
| Coriolis in rotating frame | navigation-grade IMU mechanization |
| Lagrangian robot equation | computed-torque / feedback linearization |

The clean linear state-space models of [07-foundations-control-advanced.md](07-control-advanced.md) are *linearizations* of the nonlinear equations derived here. Knowing the underlying physics tells you exactly when that linearization is valid — and when, mid-maneuver, it silently breaks.

---

## Sources & further study

- Goldstein, Poole & Safko, *Classical Mechanics* (3rd ed.) — the definitive graduate text; Lagrangian/Hamiltonian rigor.
- Taylor, *Classical Mechanics* — superb undergraduate bridge, especially noninertial frames.
- Greenwood, *Principles of Dynamics* — engineering-oriented rigid-body and rotational dynamics.
- Hughes, *Spacecraft Attitude Dynamics* — Euler equations, quaternions, and stability for vehicles.
- Featherstone, *Rigid Body Dynamics Algorithms* — computational multi-body for robotics/simulation.
- Strogatz, *Nonlinear Dynamics and Chaos* — oscillations, resonance, and stability intuition.
- Den Hartog, *Mechanical Vibrations* — the classic on resonance and damping.

> Framing note: Physics is the layer where your model is held accountable. Control theory assumes a plant; this module is where the plant comes from — and where, if you are honest, you discover all the nonlinearities your linear controller will eventually meet. Master the inertia tensor, the rotating-frame transport theorem, and the action principle, and you will never again be surprised by a vehicle that does the "impossible." It was always in the equations; you just had to derive them.
