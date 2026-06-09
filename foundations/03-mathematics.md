# Module 03 — Mathematics for Autonomy

> **Why this file exists.** The [ten-year mastery plan](02-ten-year-mastery-plan.md)
> keeps cashing checks the math has to honor. Every box in your autonomy loop —
> `sense → estimate → decide → act → log` — is, underneath, a linear-algebra
> operation, a probability update, a derivative, or an optimization step. The EKF
> in your GPS-denied navigation pipeline is *Bayes' rule on a Gaussian, linearized
> by a Jacobian, solved as a least-squares update*. Track fusion is *covariance
> arithmetic*. Visual odometry is *SVD plus Gauss-Newton on SE(3)*. If you cannot
> read those sentences and see the math underneath, you are a passenger in your own
> stack. Mastering this file makes you the person who can open
> [`navigation/`](../autonomy/28-gnc.md), see *why* the filter diverges, and fix it
> from first principles instead of twiddling tuning constants until the demo
> survives.
>
> **What "good enough" looks like.** You do not need to be a mathematician. You need
> to be an engineer who can (a) reach for the right tool without looking it up,
> (b) do the small numeric example on a whiteboard, and (c) connect each abstraction
> to the exact file in your stack where it earns its keep. That last skill — *math
> with a return address* — is what this module drills.

**Companion code.** Throughout we anchor to the real autonomy stack in this
repository — the VTOL tilt-tricopter (Pixhawk 6C + Raspberry Pi 5) running a FastAPI
onboard service over MAVSDK/pymavlink, with on-sensor IMX500 inference, a GPS-denied
navigation pipeline (visual odometry + map-matching), track fusion, a world-memory
store, a constitution-gated command policy, and a hash-chained tamper-evident decision
log. Key references: the `navigation/` EKF and VO modules, `perception/` track fusion,
`policy/constitution.py`, and `policy/decisions.py`. Read this alongside
[28-autonomy-gnc.md](../autonomy/28-gnc.md) (where the EKF lives),
[25-autonomy-control-theory.md](../autonomy/25-control-theory.md) (where the dynamics
live), and [20-autonomy-ml-ai.md](../autonomy/20-ml-ai.md) (where the statistics show up
again as learning).

---

## Table of Contents

1. [How to use this module](#1-how-to-use-this-module)
2. [Linear Algebra — the language of state](#2-linear-algebra--the-language-of-state)
3. [Probability & Statistics — the language of uncertainty](#3-probability--statistics--the-language-of-uncertainty)
4. [Calculus & Numerical Methods — the language of change](#4-calculus--numerical-methods--the-language-of-change)
5. [Optimization — the language of "best fit"](#5-optimization--the-language-of-best-fit)
6. [Rigid-Body Math — frames, Euler angles, quaternions](#6-rigid-body-math--frames-euler-angles-quaternions)
7. [Lie Groups SO(3)/SE(3) — pose on a manifold](#7-lie-groups-so3se3--pose-on-a-manifold)
8. [The map: which math runs which module](#8-the-map-which-math-runs-which-module)
9. [Practice this week](#9-practice-this-week)
10. [Sources & Citations](#sources--citations)

---

## 1. How to use this module

You learn this math by *needing* it, not by grinding a textbook front to back. The
order below is deliberate: each section is a prerequisite for the next, and the whole
chain terminates at the EKF and the pose graph — the two beating hearts of your
navigation stack.

```
   LINEAR ALGEBRA ───────────────┐
   (state is a vector,           │
    sensors are matrices)        ▼
                          PROBABILITY  ─────────────┐
                          (state is uncertain,      │
                           noise is Gaussian)       ▼
                                              CALCULUS / NUMERICS
                                              (linearize the nonlinear,
                                               integrate the dynamics)
                                                      │
                                                      ▼
                                              OPTIMIZATION
                                              (find the state that best
                                               explains the measurements)
                                                      │
                              ┌───────────────────────┴───────────────┐
                              ▼                                        ▼
                       RIGID-BODY MATH                          LIE GROUPS
                       (frames + rotations)                  (do all the above
                                                              *on the manifold*
                                                              of valid poses)
```

A senior tell: when something in the filter misbehaves, you do not start at the top of
this chain. You ask *which link broke* — bad frame convention? non-positive-definite
covariance? linearization error? a non-convex cost with a bad initial guess? Diagnosing
which math is failing is faster than re-deriving all of it.

> **Notation.** Vectors are lower-case bold in prose (`x`), matrices upper-case (`A`).
> A hat `x̂` is an estimate; a tilde `x̃` is an error. `Σ` (or `P`) is a covariance
> matrix. `Iₙ` is the n×n identity. We keep math mostly plain-text; occasional
> `$...$` is used only where it genuinely clarifies.

---

## 2. Linear Algebra — the language of state

Everything your drone "knows" is a **state vector**. Position, velocity, attitude,
sensor biases, the position of a tracked target — all of it is stacked into one column
of numbers `x ∈ ℝⁿ`. Every sensor that observes that state is, to first order, a
**matrix** that maps state to measurement. So linear algebra is not a topic you study;
it is the medium your entire stack swims in.

### 2.1 Vectors are not arrows; they are *coordinates in a chosen basis*

The single most important conceptual upgrade: a vector has no intrinsic numbers. The
triple `[3, 0, 0]` only means something once you say *in which frame*. The same physical
velocity is `[3, 0, 0]` in the body frame and something else entirely in NED. Half of
all navigation bugs are a vector expressed in the wrong basis. Hold this thought; it
returns with a vengeance in §6.

Operations you must own cold, with their physical meaning:

| Operation | Formula | What it *means* physically |
|---|---|---|
| Dot product | `a·b = ‖a‖‖b‖cosθ` | projection / "how aligned" — used to test if a target is in front of you |
| Norm | `‖a‖ = √(a·a)` | length — range to target, speed, error magnitude |
| Cross product | `a×b` | the axis ⟂ to both; angular velocity, torque, surface normals |
| Matrix–vector | `y = A x` | a linear map: rotate, project, or *measure* the state |
| Outer product | `a bᵀ` | rank-1 matrix; how covariance accumulates from samples |

### 2.2 A matrix is a verb

Stop seeing a matrix as a grid. See it as a **transformation**: it takes a vector and
returns a vector. `y = A x`. The columns of `A` are *where the basis vectors land*. That
one reframe makes rotations, projections, and sensor models obvious.

Three roles a matrix plays in your stack:

1. **Rotation / change of basis** — `R_ned_body` turns a body-frame vector into NED.
   Orthonormal (`RᵀR = I`), determinant `+1`. This is most of §6.
2. **Measurement model** — the `H` matrix in the Kalman filter. It says "if the true
   state is `x`, the sensor *should* read `H x`." For a GPS that measures position out
   of a position-velocity state, `H = [I₃ 0₃]` — it literally selects the position
   block.
3. **Covariance** — `P` is symmetric positive-definite (SPD). It is not a verb that
   moves things; it is the *shape of your ignorance*, an ellipsoid in state space.

### 2.3 Eigenvalues / eigenvectors — the directions a matrix *doesn't rotate*

For a square `A`, an eigenvector `v` satisfies `A v = λ v`: applying `A` only *scales*
`v` by `λ`, never turns it. Why you care:

- **Covariance ellipsoids.** Eigenvectors of `P` are the principal axes of your
  uncertainty ellipsoid; eigenvalues are the variances along those axes. When you draw
  the "1-σ ellipse" of your position estimate on the operator map, you are plotting the
  eigen-decomposition of the position block of `P`. A nearly-singular `P` (one tiny
  eigenvalue) means the filter is *overconfident* in one direction — a classic
  divergence precursor.
- **Stability.** A linear system `ẋ = A x` is stable iff every eigenvalue of `A` has
  negative real part. This is the bridge to [control theory](../autonomy/25-control-theory.md):
  pole placement *is* eigenvalue placement.
- **Observability / conditioning.** If the observability Gramian has a near-zero
  eigenvalue, some combination of states is effectively unobservable — the filter can
  never learn it. (Famous example: yaw is weakly observable from GPS+accel alone, which
  is exactly why your VO/magnetometer earn their keep.)

> **Numeric intuition.** Take `P = [[4, 0], [0, 1]]`. Eigenvalues 4 and 1; eigenvectors
> the x- and y-axes. Your uncertainty ellipse is 2× wider east than north (σ = √4 = 2 vs
> √1 = 1). Now rotate it 30°: the off-diagonal terms appear, x- and y-errors become
> *correlated*, and the ellipse tilts. Covariance correlation is just rotated variance.

### 2.4 Solving `A x = b` — and why you almost never invert a matrix

The naive instinct is `x = A⁻¹ b`. In real numerical code you **never form `A⁻¹`** — it
is slow, less accurate, and often the matrix isn't square. Instead:

- **Square, well-conditioned:** factor (LU). The EKF's innovation covariance `S` is
  solved this way, not inverted, even though textbooks write `K = P Hᵀ S⁻¹`.
- **Tall (more equations than unknowns) — the overdetermined case:** this is the
  **least-squares** problem, and it is everywhere in calibration and SLAM.

### 2.5 Least squares — the workhorse of every calibration in your stack

You have more measurements than unknowns and they disagree (noise). You want the `x`
that minimizes total squared error `‖A x − b‖²`. Setting the gradient to zero gives the
**normal equations**:

```
   AᵀA x = Aᵀb        ⇒        x̂ = (AᵀA)⁻¹ Aᵀ b   (conceptually)
```

In code you solve it via QR or SVD, never by forming `(AᵀA)⁻¹`, because `AᵀA` squares the
condition number and wrecks accuracy.

**Where this shows up in your stack:**

- **Magnetometer / accelerometer calibration.** Fitting the ellipsoid that maps raw mag
  readings to a unit sphere (hard-iron + soft-iron correction) is a least-squares fit.
- **Camera–IMU extrinsic calibration** for the VO pipeline: solve for the rigid
  transform that makes IMU-predicted motion agree with camera-observed motion.
- **VO / SLAM back-end.** Bundle adjustment is one giant nonlinear least-squares
  problem (§5).

### 2.6 SVD — the master tool

The Singular Value Decomposition factors *any* matrix: `A = U Σ Vᵀ`, with `U`, `V`
orthonormal and `Σ` diagonal (the singular values, ≥ 0, sorted). It is the Swiss-army
knife:

| SVD gives you | Used for in your stack |
|---|---|
| Rank (count nonzero singular values) | Is this calibration problem actually solvable, or degenerate? |
| Condition number `σ_max/σ_min` | Numerical health of a least-squares solve |
| Pseudo-inverse `A⁺ = V Σ⁺ Uᵀ` | Robust least-squares even when `AᵀA` is singular |
| Nearest orthonormal matrix | **Re-orthonormalizing a drifted rotation** `R` (project `R = U Vᵀ`) |
| Best low-rank approximation | PCA, dimensionality reduction in perception features |

> **Where this shows up.** Two places to remember. (1) After integrating a rotation over
> many steps, `R` drifts off the orthonormal manifold (rounding error). The fix is one
> SVD: replace `R` with `U Vᵀ`. (2) The classic **8-point algorithm** for estimating the
> essential matrix between two camera frames in VO ends with an SVD to enforce the rank-2
> constraint and recover relative pose. When the VO front-end "snaps" a pose, an SVD did it.

### 2.7 Positive-definiteness — the property that keeps the filter alive

A covariance `P` must stay **symmetric positive-definite**: `vᵀ P v > 0` for all `v ≠ 0`.
Physically, every direction must have positive variance — zero or negative variance is
nonsense. Floating-point arithmetic in the EKF update can silently break this and the
filter "explodes." The senior moves:

- Use the **Joseph form** of the covariance update (numerically stable, stays symmetric).
- Or run a **square-root / UD filter** that propagates a factor of `P`, making
  positive-definiteness automatic.
- Symmetrize each step: `P ← (P + Pᵀ)/2`.

This is not pedantry. A non-SPD `P` is the #1 cause of an EKF that "works in sim and
diverges on hardware."

---

## 3. Probability & Statistics — the language of uncertainty

Your drone never knows its state. It knows a *probability distribution* over states. The
whole point of the navigation filter is to keep a tractable belief and update it
optimally as data arrives. Probability is how you write "I'm 87% sure I'm here, ±3 m."

### 3.1 Random variables, distributions, and why Gaussian wins

A random variable has a distribution — a function saying how likely each value is. The
two you must own:

- **Gaussian (Normal)** `N(μ, σ²)`: the bell curve. Fully described by mean and variance.
  In `n` dimensions: `N(μ, Σ)` with a mean *vector* and a covariance *matrix*.
- **Uniform / categorical** for discrete choices (e.g., which data-association hypothesis
  in track fusion).

Why the Gaussian dominates estimation:

1. **Central Limit Theorem.** Sum many small independent errors → the total is
   approximately Gaussian. Sensor noise is a sum of many small effects, so Gaussian is a
   *physically justified* default, not just a convenient one.
2. **Closed under linear maps and conditioning.** A linear function of a Gaussian is
   Gaussian. The conditional of a joint Gaussian is Gaussian. This is *the* reason the
   Kalman filter exists: if the belief starts Gaussian and the models are linear, it
   *stays* Gaussian forever, so you only ever propagate `(μ, Σ)` — two cheap objects —
   instead of a full distribution.
3. **Maximum entropy.** Among all distributions with a given mean and variance, the
   Gaussian assumes the least — it is the most honest default.

### 3.2 Mean, variance, covariance — read the matrix

For a state vector, the covariance `Σ` (your `P`) encodes:

```
        ┌                          ┐
        │ var(x)  cov(x,y) cov(x,z)│   diagonal = how uncertain each axis is
   Σ =  │ cov(y,x) var(y)  cov(y,z)│   off-diagonal = how errors *correlate*
        │ cov(z,x) cov(z,y) var(z) │
        └                          ┘
```

The off-diagonals are where the magic lives. When GPS corrects your *position*, a
nonzero position–velocity covariance lets the filter also correct your *velocity* — a
sensor you never directly read. Correlation is how a Kalman filter updates states it
cannot measure. That is the entire trick behind estimating accelerometer bias from
position fixes.

### 3.3 Bayes' rule — the engine under every filter

Bayes' rule is the *only* correct way to combine a prior belief with new evidence:

```
   posterior  ∝  likelihood × prior

   p(state | measurement)  ∝  p(measurement | state) · p(state)
        │                           │                      │
   what you believe          how well this state      what you
   after the sensor          explains the reading      believed before
```

Read it as a sentence: *your updated belief is your prior belief, re-weighted by how well
each possible state predicts the data you just saw.* Every recursive estimator — Kalman,
EKF, particle filter, your track-fusion associator — is Bayes' rule applied over and over,
with different assumptions about the distributions.

**Where this shows up in your stack.** In `perception/` track fusion, when a new detection
arrives you compute, for each existing track, `p(detection | track)` (the likelihood, a
Gaussian on the predicted measurement) and weight it by the track's prior confidence. The
hash-chained [`policy/decisions.py`](../autonomy/28-gnc.md) log then records *which* hypothesis
won and why — a Bayesian decision made auditable.

### 3.4 Gaussian math you'll actually use

Two operations dominate:

**(a) Multiplying two Gaussians** (fusing two independent estimates of the same quantity).
The product of `N(μ₁, σ₁²)` and `N(μ₂, σ₂²)` is Gaussian with

```
   1/σ² = 1/σ₁² + 1/σ₂²          (precisions add)
   μ    = σ² (μ₁/σ₁² + μ₂/σ₂²)   (precision-weighted mean)
```

This *is* sensor fusion in one line: trust each source in proportion to its precision
(inverse variance). The Kalman gain is the matrix version of that weight.

**(b) The Mahalanobis distance** — "how many sigmas away is this?" in a correlated space:

```
   d² = (z − ẑ)ᵀ S⁻¹ (z − ẑ)
```

where `z − ẑ` is the **innovation** (measurement minus prediction) and `S` its covariance.
You use this every cycle:

- **Gating in track fusion:** reject a detection as not belonging to a track if `d²`
  exceeds a chi-square threshold. This is your defense against ghost associations.
- **EKF health monitoring:** a stream of large `d²` (high "normalized innovation squared")
  means the filter and reality have diverged — a trigger to fall back to a safer mode,
  which your [constitution gate](#8-the-map-which-math-runs-which-module) can enforce.

### 3.5 Maximum Likelihood Estimation (MLE) — and its tie to least squares

MLE asks: *which parameters make the observed data most probable?* Maximize the
likelihood, or equivalently minimize the negative log-likelihood. The punchline that ties
this whole module together:

> **Under Gaussian noise, MLE *is* least squares.** Minimizing `Σ (zᵢ − model(x))² / σᵢ²`
> is exactly maximizing a Gaussian likelihood. So every least-squares fit in §2.5 and §5
> is secretly a maximum-likelihood estimate. Calibration, VO, SLAM — all MLE with a
> Gaussian-noise assumption.

That single equivalence is why an estimation engineer can move fluidly between "I'm fitting
a curve," "I'm doing maximum likelihood," and "I'm running a Kalman update." They are the
same idea wearing different hats.

### 3.6 Why all of this underlies the EKF

Stack the pieces and the Extended Kalman Filter falls out:

```
   1. Belief is Gaussian            → carry only (x̂, P)           [§3.1]
   2. Predict: push belief through  → x̂⁻ = f(x̂),  P⁻ = F P Fᵀ + Q [§4 Jacobian F]
      the (nonlinear) dynamics,
      linearized by a Jacobian
   3. Innovation: y = z − h(x̂⁻),    → how surprised are we?         [§3.4]
      S = H P⁻ Hᵀ + R
   4. Kalman gain K = P⁻ Hᵀ S⁻¹     → precision-weighted trust      [§3.4 product]
   5. Update: x̂ = x̂⁻ + K y,         → Bayes' posterior, Gaussian    [§3.3]
      P = (I − K H) P⁻
```

Every line traces to something above: the Gaussian assumption (3.1), Bayes' rule (3.3),
Gaussian fusion (3.4), and — for the nonlinear `f`, `h` — the **Jacobian** from calculus,
which is the next section. The EKF is not a magic box; it is this module assembled. See it
fully fleshed out in [28-autonomy-gnc.md](../autonomy/28-gnc.md).

---

## 4. Calculus & Numerical Methods — the language of change

Your dynamics are nonlinear and continuous; your computer is discrete and linear-friendly.
Calculus is how you bridge them: differentiate to linearize, integrate to predict, and
watch the numerics so the bridge doesn't collapse.

### 4.1 Derivatives and gradients — the direction of steepest change

For a scalar function of many variables `f(x)`, the **gradient** `∇f` is the vector of
partial derivatives — it points uphill, toward fastest increase. Two uses:

- **Optimization** (§5): walk *downhill* (negative gradient) to minimize a cost.
- **Sensitivity:** `∇f` tells you which input the output is most sensitive to — the same
  idea as the error-budget sensitivities in
  [01_first_principles_systems_engineering.md](01-first_principles_systems_engineering.md).

### 4.2 The Jacobian — the matrix that linearizes everything

When the function is *vector-valued* (`f: ℝⁿ → ℝᵐ`), the matrix of all partial derivatives
is the **Jacobian** `J`, with `J[i,j] = ∂fᵢ/∂xⱼ`. It is the best linear approximation of a
nonlinear map near a point:

```
   f(x + δ) ≈ f(x) + J δ          (first-order Taylor, vector form)
```

This single approximation is the entire reason the **Extended** Kalman Filter can handle
nonlinear motion and sensors: it replaces the true nonlinear `f` and `h` with their
Jacobians `F` and `H` at the current estimate, then runs the *linear* Kalman equations.

**Where this shows up in your stack.** Your motion model (integrate IMU, rotate body
accelerations into NED, add gravity) is nonlinear because of the rotation. The EKF
linearizes it by computing `F = ∂f/∂x` every step. A wrong sign or a missed term in that
Jacobian is the most common silent EKF bug — the filter runs, looks plausible, and is
subtly biased. Deriving and unit-testing `F` and `H` is a rite of passage; do it by hand
once before you ever trust an autodiff version.

### 4.3 Taylor expansion — the universal "zoom in"

`f(x+δ) = f(x) + f'(x)δ + ½f''(x)δ² + …`. Truncating after the linear term is *the* move
behind linearization (EKF), Newton's method (keep the quadratic term, §5.3), and most
numerical integrators. When you hear "to first order," someone dropped everything past the
`J δ` term. Knowing what you dropped tells you when the approximation breaks — e.g., the
EKF degrades exactly when the nonlinearity is strong enough that the `½f''δ²` term you
ignored is no longer small (fast rotations, aggressive maneuvers). That is *why* an
Unscented or particle filter sometimes beats an EKF.

### 4.4 Numerical integration — predicting forward in time

The motion model is a differential equation `ẋ = f(x, u)`. To predict the next state you
integrate it over a timestep `dt`. Three methods, increasing cost/accuracy:

| Method | Update | Error per step | Use when |
|---|---|---|---|
| Euler | `x ← x + dt·f(x)` | `O(dt²)` | cheap, fast loops, small `dt` |
| RK2 (midpoint) | evaluate `f` at the midpoint | `O(dt³)` | better accuracy, modest cost |
| RK4 | 4 weighted slope evals | `O(dt⁵)` | high-fidelity sim, offline |

> **Where this shows up.** The EKF prediction step integrates IMU data — usually plain
> Euler or a simple trapezoid, because it runs at hundreds of Hz where `dt` is tiny and
> speed matters. Your **SITL simulator** ([22-autonomy-px4-sitl.md](../autonomy/22-px4-sitl.md))
> integrates the full rigid-body dynamics with RK4, because there accuracy matters more than
> speed. Same math, different accuracy/cost tradeoff — a textbook systems-engineering call.

### 4.5 Numerical stability — when the math is right but the floats betray you

Three failure modes you will personally meet:

1. **Catastrophic cancellation.** Subtracting two nearly-equal large numbers destroys
   precision. This is *why* the naive covariance update `P = (I − KH)P` can go non-SPD and
   the Joseph form (§2.7) exists.
2. **Ill-conditioning.** A matrix with a huge condition number turns tiny input errors into
   huge output errors. Watch the SVD's `σ_max/σ_min` (§2.6) on every calibration solve.
3. **Stiff dynamics / step-size.** Too large a `dt` makes an integrator blow up even though
   the analytic system is stable. Halve `dt` and re-run; if the answer changes a lot, you
   were unstable.

A senior keeps a mental smoke alarm for these. "It works in double precision in sim but
diverges on the embedded float32 on the Pi" is almost always one of the three above.

---

## 5. Optimization — the language of "best fit"

Estimation, calibration, VO, SLAM, trajectory planning, and machine learning are all the
same verb: **find the parameters that minimize a cost.** Optimization is how you make a
model agree with reality.

### 5.1 Convexity — the property that tells you if life is easy

A function is **convex** if a line between any two points on its graph lies above the graph
— intuitively, a single bowl with one bottom. The payoff:

> **Convex ⇒ any local minimum is the global minimum, and gradient descent is guaranteed
> to find it.** Non-convex ⇒ you can get trapped in a local minimum, and the answer you get
> depends on where you started.

This single distinction governs your engineering strategy:

- **Least-squares with a linear model is convex** (a paraboloid) → solve it directly,
  trust the answer. (Magnetometer calibration, linear fits.)
- **VO / SLAM / bundle adjustment is non-convex** (rotations make it so) → you need a good
  *initial guess* and an iterative solver, and you must guard against bad local minima.
  This is why VO front-ends spend so much effort on initialization.

### 5.2 Gradient descent — the most general hammer

Walk downhill: `x ← x − α ∇f(x)`, with step size (learning rate) `α`. Simple, scales to
millions of parameters, used to train every neural net in your
[perception stack](../autonomy/20-ml-ai.md) (the IMX500 model was trained by a fancy variant —
Adam — of exactly this). Weaknesses: slow near flat valleys, sensitive to `α`, no use of
curvature. For *small* problems with structure, you can do far better:

### 5.3 Gauss–Newton and Levenberg–Marquardt — the estimation workhorses

For **nonlinear least squares** — minimize `Σ ‖rᵢ(x)‖²` where each residual `rᵢ` is
"measurement minus model" — you exploit the special structure instead of using blind
gradient descent.

**Gauss–Newton.** Linearize each residual with its Jacobian `J`, then solve a *linear*
least-squares step:

```
   (JᵀJ) δ = −Jᵀ r        (the normal equations again — §2.5)
   x ← x + δ               (take the step, re-linearize, repeat)
```

`JᵀJ` approximates the curvature (Hessian) cheaply. It converges fast near the solution but
can overshoot or diverge far from it.

**Levenberg–Marquardt (LM).** The robust, production version. Add a damping term `λ`:

```
   (JᵀJ + λ diag(JᵀJ)) δ = −Jᵀ r
```

- Large `λ` → behaves like cautious gradient descent (safe when far from the answer).
- Small `λ` → behaves like fast Gauss–Newton (when close).
- The algorithm adapts `λ` automatically: shrink it when a step helps, grow it when a step
  hurts. This adaptivity is why LM is the default in essentially every calibration and SLAM
  toolbox (Ceres, g2o, GTSAM).

**Where this shows up in your stack.** Two flagship uses:

1. **Camera–IMU calibration** for the VO pipeline — LM fits the extrinsic transform and
   time offset that make the two sensors agree.
2. **VO / pose-graph back-end** — once the front-end proposes relative poses between
   keyframes, the back-end runs LM (over an SE(3) manifold, §7) to find the trajectory that
   best satisfies *all* the constraints at once. The "loop closure snaps the map straight"
   moment is one LM solve.

### 5.4 Least squares for calibration & SLAM — the full picture

Tie §2.5, §3.5, and §5.3 together:

```
   PHYSICAL PROBLEM            MATH FORM                       SOLVER
   ────────────────           ──────────                      ──────
   mag/accel calibration  →   linear least squares      →    direct (QR/SVD)   [convex]
   camera–IMU extrinsics  →   nonlinear least squares   →    Levenberg–Marquardt
   visual odometry        →   nonlinear LS on SE(3)     →    Gauss–Newton/LM   [non-convex]
   full SLAM / pose graph →   sparse nonlinear LS       →    LM + sparse Cholesky
```

Every row is "minimize squared measurement error," i.e., maximum likelihood under Gaussian
noise (§3.5). The difference is only the model's nonlinearity and the problem's size — which
dictates the solver. Once you see that, calibration and SLAM stop being separate topics.

---

## 6. Rigid-Body Math — frames, Euler angles, quaternions

This is the section that, gotten wrong, *crashes the drone*. A rigid body has a position
and an orientation; representing orientation correctly — and tracking which frame every
vector lives in — is where most real autonomy bugs hide.

### 6.1 Coordinate frames — name them or die

You will juggle at least these, constantly:

| Frame | Definition | Used by |
|---|---|---|
| **Body (FRD)** | Forward-Right-Down, fixed to the airframe | IMU, control allocation, your tilt-rotor geometry |
| **NED** | North-East-Down, local tangent plane | PX4 navigation, the EKF state |
| **ENU** | East-North-Up | ROS, many sim tools — *opposite Z from NED!* |
| **ECEF** | Earth-Centered Earth-Fixed (rotates with Earth) | GNSS receivers report here |
| **Geodetic** | lat / lon / alt on the WGS84 ellipsoid | what humans and the map use |

> **The single most expensive bug class in this whole module:** mixing NED and ENU. Their
> Z axes point opposite ways, so a sign error in altitude or yaw silently inverts a control
> response. When your sim (often ENU/ROS) and your flight stack (NED/PX4) disagree, *suspect
> the frame first.* Your VO pipeline lives at exactly this seam — camera frame → body →
> NED — so put a frame label on every vector variable name (`v_ned`, `acc_body`) and never
> let an unlabeled vector cross a module boundary.

The transform chain you care about for the GPS-denied pipeline:

```
   geodetic (lat/lon/alt)  ⇄  ECEF  ⇄  NED (local origin)  ⇄  body (FRD)  ⇄  camera
        WGS84 ellipsoid       big XYZ    nav frame            IMU/control    VO/IMX500
```

Map-matching in your nav pipeline ultimately answers "where am I in geodetic coords?" by
chaining transforms back up this ladder from a camera observation.

### 6.2 Rotation matrices — the safe, redundant representation

A rotation is a 3×3 orthonormal matrix `R` with `det R = +1` (the group SO(3), §7).
`v_ned = R_ned_body · v_body` rotates a body vector into NED. Properties to internalize:

- **Compose by multiplying:** `R_a_c = R_a_b · R_b_c`. Read the subscripts like cancelling
  units — `b` meets `b`, leaving `a_c`. This bookkeeping trick prevents half your frame
  bugs.
- **Invert by transposing:** `R_body_ned = R_ned_bodyᵀ`. Free and exact.
- **Cost:** 9 numbers for 3 degrees of freedom — redundant, and drifts off the manifold
  under integration (fix with the SVD trick, §2.6).

### 6.3 Euler angles — intuitive, and a trap

Roll-pitch-yaw (φ, θ, ψ) are how humans think and how you'll talk to operators. But they
have a fatal flaw for computation:

> **Gimbal lock.** At pitch = ±90°, two of the three axes align and you lose a degree of
> freedom — the representation becomes singular and yaw/roll become ambiguous. For a VTOL
> that can pitch hard during transition, this is not hypothetical.

Euler angles are also non-unique and don't compose by simple multiplication. **Use them for
display and human interface; never as your internal attitude state.** That is precisely why
the EKF stores a quaternion internally and only converts to roll/pitch/yaw for the telemetry
you show the operator.

### 6.4 Quaternions — the representation flight code actually uses

A unit quaternion `q = [w, x, y, z]` with `‖q‖ = 1` represents a rotation with **4 numbers,
no singularities, and cheap composition.** This is what PX4's EKF2, ArduPilot, and your own
nav state carry.

| Property | Quaternion | Euler | Rotation matrix |
|---|---|---|---|
| Numbers / DOF | 4 / 3 | 3 / 3 | 9 / 3 |
| Singularities | **none** | gimbal lock | none |
| Compose | `q₁ ⊗ q₂` (cheap) | hard | `R₁R₂` (9 mults each) |
| Interpolate | **SLERP** (smooth) | ugly | awkward |
| Human-readable | no | **yes** | no |

Operations you'll use:

- **Compose rotations:** quaternion multiply `q₁ ⊗ q₂` (note: non-commutative — order is
  the rotation order).
- **Rotate a vector:** `v' = q ⊗ [0, v] ⊗ q⁻¹` (or, faster, the equivalent direct formula).
- **Invert:** conjugate `q⁻¹ = [w, −x, −y, −z]` (for a unit quaternion).
- **Renormalize every few steps:** `q ← q/‖q‖` — the quaternion analog of the SVD
  re-orthonormalization, because numerical integration nudges `‖q‖` off 1.

> **Where this shows up.** Your nav filter integrates gyro rates into the attitude
> quaternion every cycle. The "error-state" formulation (Sola's paper, below) keeps the
> *big* quaternion outside the filter and lets the EKF estimate only a small 3-vector
> rotation *error*, which it folds back in — sidestepping the "4 numbers, 3 DOF" mismatch
> that would otherwise make `P` singular. That trick is the bridge to the final section.

### 6.5 The quaternion / Euler / matrix cheat sheet

```
   q (filter state)  ──to matrix──►  R (rotate vectors between frames)
        │   ▲                              │
   to Euler│   │from Euler                 │ SVD project if drifted (§2.6)
        ▼   │                              ▼
   φθψ (operator display)            R re-orthonormalized
```

Internal state: quaternion. Vector rotation: matrix. Human I/O: Euler. Keep those three
roles straight and most attitude bugs evaporate.

---

## 7. Lie Groups SO(3)/SE(3) — pose on a manifold

Here is the deepest idea in this module, and the one that separates a state-estimation
engineer from someone who merely *uses* a Kalman library. Rotations and poses do **not**
live in a flat vector space. You cannot just add two rotations or compute their average by
averaging the numbers. They live on a curved surface — a *manifold* — and you need the math
of **Lie groups** to do calculus on them correctly.

### 7.1 The problem: you can't subtract two orientations

Try the naive thing: estimate an attitude error as `q_measured − q_estimate`. The result is
not a valid quaternion (its norm isn't 1). Average two rotation matrices element-wise and
you get a matrix that isn't a rotation. The "+" and "−" the Kalman filter relies on simply
**don't exist** for orientation. So either you give up on the EKF for attitude, or you find
the right notion of "+" and "−" on the manifold. Lie theory provides exactly that.

### 7.2 The vocabulary, in plain terms

- **SO(3):** the group of all valid 3D rotations (the rotation matrices / unit quaternions).
  A smooth curved 3-dimensional surface living inside 9-dimensional matrix space.
- **SE(3):** the group of all valid *poses* — rotation **and** translation together (6 DOF).
  This is what a VO/SLAM system actually estimates: where the camera *is and points*.
- **The tangent space (Lie algebra, so(3)/se(3)):** at any point on the manifold, the local
  *flat* space of small motions. For SO(3) this is just 3-vectors (a rotation axis × angle —
  an angular velocity). **This is flat, so the Kalman filter's linear algebra works here.**
- **exp and log maps:** the elevator between the two worlds.
  - `exp`: take a small flat 3-vector (axis-angle) → the actual rotation it produces (curved).
  - `log`: take a rotation (curved) → the equivalent small 3-vector (flat).

```
   MANIFOLD (curved)                       TANGENT SPACE (flat ℝ³ / ℝ⁶)
   SO(3): rotations                        so(3): axis-angle vectors
   SE(3): poses                            se(3): twist vectors
        │                                        ▲
        │   log  (manifold → flat)               │
        └────────────────────────────────────────┤
        ▲                                         │
        │   exp  (flat → manifold)                │
        └─────────────────────────────────────────┘
```

### 7.3 The ⊞ and ⊟ operators — "+ and − that respect the curve"

Lie theory gives you **boxplus** (`⊞`) and **boxminus** (`⊟`), the manifold-correct versions
of `+` and `−`:

```
   X ⊞ δ  =  X · exp(δ)        "apply a small flat correction δ to pose X"
   Y ⊟ X  =  log(X⁻¹ · Y)      "the small flat vector that takes X to Y"   (the error!)
```

Now the EKF works again. You keep the *nominal* pose `X` on the manifold (a clean
quaternion/matrix), and let the filter estimate a small **error vector δ in the flat tangent
space** — where addition, covariance, and Jacobians all behave. After each update you fold δ
back onto the manifold with `⊞`. This is the **error-state Kalman filter (ESKF)**, and it is
how every serious VIO/SLAM system (VINS-Mono, PX4's EKF2 attitude, ORB-SLAM's back-end) does
attitude and pose. The covariance `P` is now a clean 3×3 (SO(3)) or 6×6 (SE(3)) over the
*error*, never singular, always meaningful.

### 7.4 Why this is the keystone of your GPS-denied stack

Your visual-odometry pipeline estimates a *trajectory of SE(3) poses* and refines them by
nonlinear least squares (§5.3). Every piece of this module converges here:

```
   VO / pose-graph optimization on SE(3)
   ─────────────────────────────────────
   • State        : a chain of SE(3) poses                         [§7  Lie groups]
   • Residuals    : "predicted relative pose vs observed"  via ⊟   [§7.3 boxminus]
   • Jacobians    : ∂residual/∂δ in the tangent space             [§4.2 + §7.2]
   • Solver       : Gauss–Newton / Levenberg–Marquardt            [§5.3]
   • Noise model  : Gaussian on the tangent space → MLE = LS       [§3.5]
   • Numerics     : keep poses on-manifold (exp/log, renormalize)  [§2.6/§2.7]
```

When loop closure "snaps" your map straight, what physically happened is: an LM solver took
a Gauss–Newton step, computed in the flat tangent space via `⊟`, on a graph of SE(3) poses,
under a Gaussian (MLE) noise model — then mapped the correction back onto the manifold with
`⊞`. That one sentence is this entire module, and it is the literal core of your GPS-denied
navigation. Read Sola's *micro Lie theory* until `⊞`/`⊟` feel as natural as `+`/`−`; after
that, advanced state estimation is just bookkeeping.

---

## 8. The map: which math runs which module

Pin this table to the wall. It is the "return address" for every abstraction above.

| Stack module (your repo) | Math doing the work | Section |
|---|---|---|
| EKF predict (IMU integration) | numerical integration, Jacobian `F`, frames | §4.2, §4.4, §6 |
| EKF update (GPS/baro/VO) | Bayes' rule, Gaussian fusion, Kalman gain, SPD care | §3.3–3.4, §2.7 |
| Attitude state | quaternions, error-state / SO(3) | §6.4, §7.3 |
| Visual odometry front-end | SVD (8-point), least squares | §2.6, §2.5 |
| VO / pose-graph back-end | nonlinear LS on SE(3), Gauss–Newton/LM | §5.3, §7.4 |
| Map-matching / geodetic fix | frame transforms (camera→body→NED→ECEF→geodetic) | §6.1 |
| Track fusion (`perception/`) | covariance, Mahalanobis gating, Bayes association | §3.2, §3.4 |
| Sensor calibration (mag/IMU/cam) | least squares, LM, SVD conditioning | §2.5, §5.3 |
| Control loops | eigenvalues/stability, linearization | §2.3, §4.2 |
| IMX500 perception model | gradient descent (training), linear algebra (inference) | §5.2, §2 |
| Constitution gate / decision log | probability thresholds, chi-square gating → auditable decisions | §3.4 |

> **Senior tell.** When a teammate says "the filter is drifting," you don't reach for a
> tuning knob. You walk this table: *Is it a frame bug (§6)? A bad Jacobian (§4.2)? A
> non-SPD covariance (§2.7)? An unobservable state (§2.3)? A non-convex VO solve stuck in a
> local minimum (§5.1)?* Naming the broken link is the skill. The math above is what lets
> you name it.

---

## 9. Practice this week

Do these in your own stack, not in a textbook. Each maps to a section.

1. **Linear algebra (§2).** Open your covariance `P` mid-flight from a log. Compute its
   eigenvalues. Plot the 1-σ position ellipse. Now corrupt `P` to be non-SPD and watch the
   update explode — then fix it with the Joseph form. You will never forget §2.7 again.
2. **Probability (§3).** Implement Gaussian product fusion (§3.4a) for two range estimates.
   Confirm the fused variance is smaller than either input. That's the Kalman gain in 1D.
3. **Calculus (§4).** Derive the EKF motion Jacobian `F` by hand for a simplified
   position-velocity-attitude state. Unit-test it against a finite-difference numerical
   Jacobian. The day those match, you trust your filter.
4. **Optimization (§5).** Fit your magnetometer calibration ellipsoid as a linear least
   squares. Then deliberately use a bad initial guess on a nonlinear version and watch LM
   recover where Gauss–Newton diverges.
5. **Rigid-body (§6).** Take one telemetry packet and transform a velocity from body → NED →
   ENU by hand, then with your code. Find the sign that flips between NED and ENU. Label
   every variable with its frame.
6. **Lie groups (§7).** Implement `exp`/`log` for SO(3) and verify `R ⊞ (R₂ ⊟ R) == R₂`.
   When that identity holds, you understand the error-state filter.

When all six feel routine, re-read [28-autonomy-gnc.md](../autonomy/28-gnc.md) — the EKF and
VO derivations there will read like commentary on math you now own, which is exactly the
point.

---

## Sources & Citations

**Linear algebra**
- Strang, G. — *Introduction to Linear Algebra*, Wellesley-Cambridge (the canonical intuition-first text). Lectures free on MIT OCW: https://ocw.mit.edu/courses/18-06-linear-algebra-spring-2010/
- Strang, G. — *Linear Algebra and Learning from Data*, Wellesley-Cambridge (SVD, least squares, the modern view).
- Golub & Van Loan — *Matrix Computations*, Johns Hopkins (the numerical-linear-algebra reference for conditioning, QR, SVD).

**Probability & statistics**
- Wasserman, L. — *All of Statistics: A Concise Course in Statistical Inference*, Springer (fast, rigorous, exactly the working subset).
- Bishop, C. — *Pattern Recognition and Machine Learning*, Springer (Gaussians, Bayes, MLE done carefully).
- Thrun, Burgard & Fox — *Probabilistic Robotics*, MIT Press (Bayes filters, EKF, the robotics framing of everything in §3).

**Calculus, numerical methods & optimization**
- Boyd, S. & Vandenberghe, L. — *Convex Optimization*, Cambridge (free: https://web.stanford.edu/~boyd/cvxbook/). Read §1–§9 for convexity, gradient/Newton methods.
- Nocedal & Wright — *Numerical Optimization*, Springer (Gauss–Newton, Levenberg–Marquardt, line search).
- Trefethen & Bau — *Numerical Linear Algebra*, SIAM (stability, conditioning, the honest numerics).

**Rigid-body & Lie theory**
- Sola, J. — *Quaternion kinematics for the error-state Kalman filter* (arXiv:1711.02508) — the practical bridge from quaternions to the ESKF.
- Sola, Deray & Atchuthan — *A micro Lie theory for state estimation in robotics* (arXiv:1812.01537) — the clearest on-ramp to SO(3)/SE(3), ⊞/⊟.
- Barfoot, T. — *State Estimation for Robotics*, Cambridge (the full treatment of estimation on matrix Lie groups).
- Diebel, J. — *Representing Attitude: Euler Angles, Unit Quaternions, and Rotation Vectors* (the conversion reference).

**Official docs / source**
- PX4 EKF2 (ECL) state estimation & frame conventions: https://docs.px4.io
- Eigen (the C++ linear-algebra library behind most flight code): https://eigen.tuxfamily.org
- Ceres Solver (nonlinear least squares / LM, the calibration & SLAM back-end): http://ceres-solver.org
- GTSAM (factor-graph SLAM on Lie groups): https://gtsam.org

---

*End of Module 03. Inline references to `navigation/`, `perception/`, the EKF, the VO
pipeline, the constitution gate, and the decision log point at the author's own
`pixhawk/drone/` project and are kept as code references. Re-derive the EKF assembly in
§3.6 and the SE(3) optimization in §7.4 until they feel inevitable; after that, the rest of
autonomy math is just careful bookkeeping.*
