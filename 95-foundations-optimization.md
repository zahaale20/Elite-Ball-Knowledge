# Optimization — The Engine Under Estimation, Control & Learning

> **Why this exists.** Almost every interesting thing your autonomy stack does is
> secretly an optimization problem wearing a disguise. The EKF update is a weighted
> least-squares solve. Visual odometry is Gauss-Newton on a reprojection cost.
> Model-predictive control is a quadratic program solved every 20 ms. Training a
> network is stochastic gradient descent on an empirical risk. Trajectory planning
> is a constrained nonlinear program. If you can see the common skeleton —
> *objective, constraints, optimality conditions, an algorithm that descends* — you
> stop memorizing a dozen unrelated recipes and start recognizing one machine with
> many faceplates.
>
> **What mastering it makes you.** The engineer who, shown a diverging solver or a
> controller that chatters, asks the right diagnostic questions: *Is the problem
> convex? Is the Hessian conditioned? Are the constraints active? Is the step size
> killing me?* — and fixes the cause instead of tuning blindly.

Optimization is the connective tissue of this whole curriculum. The probability that
feeds it lives in [96-foundations-probability-and-stochastic.md](96-foundations-probability-and-stochastic.md);
the matrix factorizations that solve its linear algebra core live in
[97-foundations-linear-algebra-applied.md](97-foundations-linear-algebra-applied.md);
the numerical care that keeps it from exploding lives in
[98-foundations-numerical-methods.md](98-foundations-numerical-methods.md). Downstream
it powers the estimators and controllers of [28-autonomy-gnc.md](28-autonomy-gnc.md)
and [25-autonomy-control-theory.md](25-autonomy-control-theory.md), the learning of
[20-autonomy-ml-ai.md](20-autonomy-ml-ai.md), and the planners of
[29-autonomy-planning-decision.md](29-autonomy-planning-decision.md). It also rests on
the general math foundation in [03-foundations-mathematics.md](03-foundations-mathematics.md).

---

## Table of Contents

1. [The canonical form](#1-the-canonical-form)
2. [Convexity — the property that buys global guarantees](#2-convexity--the-property-that-buys-global-guarantees)
3. [Unconstrained descent: gradient, Newton, quasi-Newton](#3-unconstrained-descent-gradient-newton-quasi-newton)
4. [Least squares — the workhorse](#4-least-squares--the-workhorse)
5. [Constrained optimization: Lagrangian, KKT, duality](#5-constrained-optimization-lagrangian-kkt-duality)
6. [QP and NLP — the shapes your stack actually solves](#6-qp-and-nlp--the-shapes-your-stack-actually-solves)
7. [Stochastic gradient descent — optimization at scale](#7-stochastic-gradient-descent--optimization-at-scale)
8. [Where each method runs in the stack](#8-where-each-method-runs-in-the-stack)
9. [Sources & further study](#sources--further-study)

---

## 1. The canonical form

Every optimization problem can be written

$$
\min_{x \in \mathbb{R}^n} \; f(x) \quad \text{subject to} \quad
g_i(x) \le 0,\; i=1,\dots,m, \qquad h_j(x) = 0,\; j=1,\dots,p.
$$

Here $x$ is the **decision variable** (a state estimate, a control sequence, a weight
vector), $f$ is the **objective** (cost, negative log-likelihood, reprojection error),
the $g_i$ are **inequality constraints** (actuator limits, obstacle clearance), and the
$h_j$ are **equality constraints** (dynamics, calibration identities). The feasible set
is $\mathcal{F} = \{x : g_i(x)\le 0,\ h_j(x)=0\}$. A point $x^\star$ is **globally
optimal** if $f(x^\star)\le f(x)$ for all $x\in\mathcal{F}$, and **locally optimal** if
that holds only in some neighborhood.

The entire game is: *how much structure does the problem have, and how much does that
structure buy me?* Convexity buys global optimality. Smoothness buys fast local
convergence. Sparsity buys speed. Recognizing which you have is the first move.

---

## 2. Convexity — the property that buys global guarantees

A set $C$ is **convex** if the line segment between any two of its points stays inside:

$$
x, y \in C,\; \theta \in [0,1] \implies \theta x + (1-\theta) y \in C.
$$

A function $f$ is **convex** if its domain is convex and

$$
f\big(\theta x + (1-\theta) y\big) \le \theta f(x) + (1-\theta) f(y).
$$

Geometrically, the chord never dips below the graph. For twice-differentiable $f$, this
is equivalent to the **Hessian being positive semidefinite everywhere**:

$$
\nabla^2 f(x) \succeq 0 \quad \forall x.
$$

**Why we care so much.** For a convex problem, *any local minimum is a global minimum*,
and the first-order condition $\nabla f(x^\star)=0$ (suitably generalized for
constraints) is sufficient, not just necessary. There is no fear of getting trapped in a
bad valley. Least squares, linear programs, quadratic programs with PSD cost, and convex
relaxations all live here — which is exactly why estimation and control lean on them.

**Worked check.** Is $f(x) = \tfrac12 x^\top Q x + b^\top x$ convex? Its Hessian is
$\nabla^2 f = Q$. So $f$ is convex iff $Q \succeq 0$, and strictly convex (unique
minimizer) iff $Q \succ 0$. Setting $\nabla f = Qx + b = 0$ gives $x^\star = -Q^{-1}b$ —
the closed form behind every quadratic cost you will ever minimize.

```python
import numpy as np

def is_convex_quadratic(Q, tol=1e-9):
    """Return True if the quadratic 0.5 x'Qx + b'x is convex.

    A quadratic is convex exactly when its Hessian Q is positive
    semidefinite, i.e. every eigenvalue is non-negative.
    """
    w = np.linalg.eigvalsh(0.5 * (Q + Q.T))  # symmetrize first
    return np.all(w >= -tol)
```

---

## 3. Unconstrained descent: gradient, Newton, quasi-Newton

For smooth unconstrained $f$, the **first-order necessary condition** for a local
minimum is $\nabla f(x^\star) = 0$, and the **second-order sufficient condition** adds
$\nabla^2 f(x^\star) \succ 0$. Iterative methods chase that stationary point.

### Gradient descent

Move opposite the gradient:

$$
x_{k+1} = x_k - \alpha_k \nabla f(x_k).
$$

The step $\alpha_k$ matters enormously. Convergence rate is governed by the **condition
number** $\kappa = \lambda_{\max}/\lambda_{\min}$ of the Hessian. For a strongly convex
quadratic, gradient descent converges linearly with rate

$$
\frac{\kappa - 1}{\kappa + 1},
$$

so an ill-conditioned problem ($\kappa \gg 1$) crawls along a narrow valley, zig-zagging.
This single fact explains why preconditioning, feature scaling, and Newton steps exist.

### Newton's method

Use curvature. Take the second-order Taylor model

$$
f(x_k + p) \approx f(x_k) + \nabla f(x_k)^\top p + \tfrac12 p^\top \nabla^2 f(x_k)\, p,
$$

minimize over $p$ by setting its gradient to zero, and get the **Newton step**

$$
p_k = -\big[\nabla^2 f(x_k)\big]^{-1} \nabla f(x_k), \qquad x_{k+1} = x_k + p_k.
$$

Near the solution Newton converges **quadratically** — the number of correct digits
roughly doubles each iteration. The price is forming and inverting the Hessian, $O(n^3)$,
and the requirement that $\nabla^2 f \succ 0$ (else the step may go uphill).

### Quasi-Newton (BFGS) and Gauss-Newton

When the true Hessian is too expensive, build an approximation $B_k \approx \nabla^2 f$
from gradient differences (BFGS), getting superlinear convergence at $O(n^2)$ cost. When
$f$ is a sum of squares, $f(x) = \tfrac12\|r(x)\|^2$, the **Gauss-Newton** approximation
drops the second-derivative term:

$$
\nabla^2 f \approx J^\top J, \qquad J = \frac{\partial r}{\partial x},
$$

giving the step $(J^\top J)\,p = -J^\top r$. This is the engine inside bundle
adjustment, visual odometry, and EKF-style nonlinear least squares. **Levenberg-Marquardt**
adds a damping term, solving $(J^\top J + \mu I)\,p = -J^\top r$, which interpolates
between Gauss-Newton ($\mu \to 0$) and gradient descent ($\mu \to \infty$) for robustness.

| Method | Step cost | Convergence | Needs |
|---|---|---|---|
| Gradient descent | $O(n)$ | linear (rate $\propto \kappa$) | $\nabla f$ |
| Newton | $O(n^3)$ | quadratic | $\nabla f, \nabla^2 f \succ 0$ |
| BFGS | $O(n^2)$ | superlinear | $\nabla f$ |
| Gauss-Newton / LM | $O(n^3)$ but sparse | ~quadratic near small residual | Jacobian $J$ |

---

## 4. Least squares — the workhorse

The linear least-squares problem

$$
\min_x \; \tfrac12 \|Ax - b\|_2^2
$$

is the most-solved optimization problem on Earth. Its gradient is $A^\top(Ax-b)$, so the
optimum satisfies the **normal equations**

$$
A^\top A\, x^\star = A^\top b \quad\Longrightarrow\quad x^\star = (A^\top A)^{-1} A^\top b,
$$

assuming $A$ has full column rank. The matrix $A^+ = (A^\top A)^{-1}A^\top$ is the
**Moore-Penrose pseudoinverse**. In practice you never form $A^\top A$ (it squares the
condition number); you solve via QR or SVD — see
[97-foundations-linear-algebra-applied.md](97-foundations-linear-algebra-applied.md).

**Weighted and regularized.** If measurements have covariance $R$, minimize the
**Mahalanobis** cost $\tfrac12 (Ax-b)^\top R^{-1}(Ax-b)$, giving
$x^\star = (A^\top R^{-1}A)^{-1}A^\top R^{-1}b$ — exactly the EKF measurement update.
Adding **Tikhonov / ridge** regularization $\tfrac{\lambda}{2}\|x\|^2$ yields
$x^\star = (A^\top A + \lambda I)^{-1}A^\top b$, which stabilizes ill-posed problems and
is the deterministic twin of a Gaussian prior (a recurring theme with
[96-foundations-probability-and-stochastic.md](96-foundations-probability-and-stochastic.md)).

```python
import numpy as np

def weighted_ls(A, b, Rinv):
    """Solve a weighted least-squares problem min (Ax-b)' Rinv (Ax-b).

    We form the weighted normal equations and solve them with a stable
    solver rather than an explicit inverse. This is the same algebra the
    Kalman measurement update performs every cycle.
    """
    M = A.T @ Rinv @ A          # information matrix
    y = A.T @ Rinv @ b          # information vector
    return np.linalg.solve(M, y)
```

---

## 5. Constrained optimization: Lagrangian, KKT, duality

Constraints turn "find the bottom" into "find the bottom you are allowed to reach." The
key device is the **Lagrangian**, which folds constraints into the objective with
multipliers:

$$
\mathcal{L}(x, \lambda, \nu) = f(x) + \sum_{i} \lambda_i g_i(x) + \sum_j \nu_j h_j(x),
\qquad \lambda_i \ge 0.
$$

A multiplier is the *shadow price* of its constraint — how much the optimal cost would
change if you loosened it by a unit. At an optimum, the **Karush-Kuhn-Tucker (KKT)
conditions** must hold:

$$
\begin{aligned}
&\nabla_x \mathcal{L} = \nabla f + \textstyle\sum_i \lambda_i \nabla g_i + \sum_j \nu_j \nabla h_j = 0 &&\text{(stationarity)}\\
&g_i(x) \le 0,\quad h_j(x) = 0 &&\text{(primal feasibility)}\\
&\lambda_i \ge 0 &&\text{(dual feasibility)}\\
&\lambda_i\, g_i(x) = 0 &&\text{(complementary slackness)}
\end{aligned}
$$

The last line is the deep one: **complementary slackness** says each inequality is either
*active* ($g_i = 0$, multiplier can be positive) or *inactive* ($g_i < 0$, so
$\lambda_i = 0$). For convex problems the KKT conditions are both necessary and
sufficient — solving them *is* solving the problem.

**Duality.** The **dual function** $q(\lambda,\nu) = \min_x \mathcal{L}(x,\lambda,\nu)$
is always concave and lower-bounds the optimal value (**weak duality**:
$q(\lambda,\nu) \le f(x^\star)$). For convex problems satisfying Slater's condition the
bound is tight (**strong duality**), and the **duality gap** is zero. Duality is not
academic: it gives you a *certificate of optimality* (stop when the gap is small) and
often a cheaper problem to solve.

**Worked example — equality-constrained quadratic.** Minimize
$\tfrac12 x^\top Q x$ subject to $Ax = b$ with $Q \succ 0$. Stationarity gives
$Qx + A^\top \nu = 0$, i.e. $x = -Q^{-1}A^\top\nu$. Substituting into $Ax = b$:

$$
-AQ^{-1}A^\top \nu = b \;\Rightarrow\; \nu = -(AQ^{-1}A^\top)^{-1} b,
\qquad x^\star = Q^{-1}A^\top (AQ^{-1}A^\top)^{-1} b.
$$

This **KKT system** — solving the block matrix
$\begin{bmatrix} Q & A^\top \\ A & 0 \end{bmatrix}\begin{bmatrix}x\\\nu\end{bmatrix}=\begin{bmatrix}0\\b\end{bmatrix}$ —
is the literal core of equality-constrained MPC and trajectory optimization.

---

## 6. QP and NLP — the shapes your stack actually solves

### Quadratic programs (QP)

$$
\min_x \; \tfrac12 x^\top Q x + c^\top x \quad \text{s.t.}\quad Gx \le h,\; Ax = b,
\qquad Q \succeq 0.
$$

When $Q \succeq 0$ the QP is convex and solvable to global optimality in milliseconds by
**active-set** or **interior-point** methods. This is the form of **model-predictive
control**: stack the dynamics as equality constraints, actuator and state limits as
inequalities, and a tracking cost as $Q, c$. It is also the form of an SVM, of contact
dynamics, and of the control-allocation problem that maps desired wrench to motor
commands on your VTOL — see [25-autonomy-control-theory.md](25-autonomy-control-theory.md).

### Nonlinear programs (NLP)

When $f$ or the constraints are nonlinear (rigid-body dynamics, obstacle fields), you get
a general NLP. Solvers like **SQP** (sequential quadratic programming) repeatedly
linearize into a QP and step; **interior-point** methods (IPOPT) push a barrier term
$-\mu \sum_i \log(-g_i(x))$ that fades as $\mu \to 0$, keeping iterates strictly feasible.
Trajectory optimization in [29-autonomy-planning-decision.md](29-autonomy-planning-decision.md)
lives here.

| Problem class | Convex? | Typical solver | Where it shows up |
|---|---|---|---|
| LP | yes | simplex / interior-point | resource allocation, $\ell_1$ |
| QP ($Q\succeq0$) | yes | active-set / interior-point | MPC, SVM, control allocation |
| Least squares | yes | QR / SVD / normal eqns | EKF, regression, calibration |
| SOCP / SDP | yes | interior-point | robust control, relaxations |
| General NLP | no | SQP / IPOPT | trajectory opt, bundle adjustment |

---

## 7. Stochastic gradient descent — optimization at scale

Machine learning minimizes an **empirical risk** that is a sum over data:

$$
f(x) = \frac{1}{N} \sum_{i=1}^N \ell_i(x).
$$

Computing $\nabla f$ means touching all $N$ examples — wasteful when $N$ is millions.
**Stochastic gradient descent (SGD)** estimates the gradient from a random minibatch
$\mathcal{B}$:

$$
x_{k+1} = x_k - \alpha_k\, \hat g_k, \qquad
\hat g_k = \frac{1}{|\mathcal{B}|}\sum_{i\in\mathcal{B}} \nabla \ell_i(x_k).
$$

The estimate is **unbiased**, $\mathbb{E}[\hat g_k] = \nabla f(x_k)$, but noisy. That
noise is a feature: it helps escape saddle points and shallow minima. The classic
**Robbins-Monro** condition for convergence balances persistence and decay:

$$
\sum_k \alpha_k = \infty, \qquad \sum_k \alpha_k^2 < \infty.
$$

Modern variants add **momentum** (an exponentially-averaged velocity that smooths the
path) and **per-coordinate adaptive rates** (Adam: divide by a running estimate of each
coordinate's gradient magnitude, effectively a cheap diagonal preconditioner that fights
the conditioning problem from §3). The full ML treatment is in
[20-autonomy-ml-ai.md](20-autonomy-ml-ai.md).

```python
import numpy as np

def sgd_step(x, grad_fn, batch, lr, velocity, momentum=0.9):
    """One SGD-with-momentum update.

    Momentum maintains a velocity that is an exponential average of past
    gradients; this damps oscillation in ill-conditioned directions and
    accelerates progress along consistent ones.
    """
    g = grad_fn(x, batch)                 # noisy minibatch gradient
    velocity = momentum * velocity - lr * g
    return x + velocity, velocity
```

---

## 8. Where each method runs in the stack

| Stack component | Optimization underneath |
|---|---|
| EKF / UKF measurement update | weighted least squares (§4) |
| Visual odometry, bundle adjustment | Gauss-Newton / Levenberg-Marquardt (§3) |
| Model-predictive control | convex QP every cycle (§6) |
| Control allocation (wrench → motors) | constrained QP (§5, §6) |
| Trajectory / motion planning | NLP via SQP / interior-point (§6) |
| Network training | SGD on empirical risk (§7) |
| Calibration (camera, IMU) | nonlinear least squares (§3, §4) |
| Sensor fusion smoothing | sparse least squares on a factor graph (§4) |

The lesson: there are not twelve algorithms to learn, there is **one objective-plus-method
pattern** instantiated twelve ways. Master the pattern — objective, optimality conditions,
descent, exploit structure — and every box in `sense → estimate → decide → act` becomes
legible.

---

## Sources & further study

- **Boyd & Vandenberghe, *Convex Optimization*** — the canonical text; convex sets,
  duality, KKT, interior-point. Freely available and worth reading cover to cover.
- **Nocedal & Wright, *Numerical Optimization*** — the practitioner's bible for
  unconstrained, Newton/quasi-Newton, SQP, interior-point methods.
- **Bertsekas, *Nonlinear Programming*** — rigorous treatment of Lagrangian duality and
  constrained methods.
- **Strang, *Linear Algebra and Its Applications*** — for the least-squares and normal-equation
  machinery underneath everything here.
- **Bishop, *Pattern Recognition and Machine Learning***, ch. 3-5 — least squares,
  regularization, and the optimization view of learning.
- **Goodfellow, Bengio & Courville, *Deep Learning***, ch. 8 — SGD, momentum, Adam, and
  optimization for neural networks.

> Framing note: optimization is where mathematics stops describing the world and starts
> *acting* on it. An estimator chooses the state that best explains the data; a controller
> chooses the input that best reaches the goal; a learner chooses the parameters that best
> fit experience. "Best," in each case, is a number you defined and an algorithm you trusted
> to descend. Own both — the objective you wrote and the solver you ran — and you own the
> behavior of the machine.
