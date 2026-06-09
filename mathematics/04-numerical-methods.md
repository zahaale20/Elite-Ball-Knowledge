# Numerical Methods — Computing Answers That Don't Blow Up

> **Why this exists.** The math in the rest of this band is exact; the computer that runs
> it is not. Every real number gets squeezed into 64 bits, every integral becomes a sum,
> every derivative becomes a difference, and every "solve" becomes an iteration that might
> converge, stall, or diverge. Numerical methods is the discipline of getting *trustworthy*
> answers out of *finite, imperfect* arithmetic — and of knowing when an answer is garbage
> dressed as precision. Your EKF integrates dynamics with a Runge-Kutta step; your
> optimizer takes finite-difference gradients; your filter inverts a covariance that might
> be ill-conditioned. If you do not understand floating point, stability, and conditioning,
> you will eventually ship a system that works in the demo and silently NaNs over the
> ocean.
>
> **What mastering it makes you.** The engineer who reads a sudden `inf`, a drifting
> integrator, or a diverging Newton iteration and diagnoses it as *catastrophic
> cancellation*, *step-size instability*, or *bad conditioning* — and fixes the algorithm
> rather than sprinkling clamps and hoping.

This module is where the clean mathematics of the other foundations meets silicon. The
solvers it stabilizes power [01-foundations-optimization.md](01-optimization.md);
the factorizations it implements come from
[03-foundations-linear-algebra-applied.md](03-linear-algebra-applied.md); the
sampling it makes reliable serves
[02-foundations-probability-and-stochastic.md](02-probability-and-stochastic.md).
Its ODE integrators run the dynamics in
[06-autonomy-control-theory.md](../autonomy/06-control-theory.md) and the prediction step in
[09-autonomy-gnc.md](../autonomy/09-gnc.md); it underpins the training loops of
[01-autonomy-ml-ai.md](../autonomy/01-ml-ai.md) and extends
[03-foundations-mathematics.md](../foundations/03-mathematics.md).

---

## Table of Contents

1. [Floating point — the ground you stand on](#1-floating-point--the-ground-you-stand-on)
2. [Conditioning vs. stability](#2-conditioning-vs-stability)
3. [Solving linear systems numerically](#3-solving-linear-systems-numerically)
4. [Root finding and Newton's method](#4-root-finding-and-newtons-method)
5. [Numerical differentiation and integration](#5-numerical-differentiation-and-integration)
6. [Integrating ODEs: Euler to Runge-Kutta](#6-integrating-odes-euler-to-runge-kutta)
7. [Stability of integrators — stiffness and step size](#7-stability-of-integrators--stiffness-and-step-size)
8. [Where numerics decide success in the stack](#8-where-numerics-decide-success-in-the-stack)
9. [Sources & further study](#sources--further-study)

---

## 1. Floating point — the ground you stand on

A 64-bit IEEE-754 double stores a number as $\pm\, m \times 2^{e}$ with a 52-bit mantissa,
giving about **15-16 significant decimal digits**. The spacing between representable numbers
near 1 is the **machine epsilon**:

$$
\varepsilon_{\text{mach}} = 2^{-52} \approx 2.22\times 10^{-16}.
$$

Every operation rounds, so the model is: $\operatorname{fl}(a \circ b) = (a\circ b)(1+\delta)$
with $|\delta|\le\varepsilon_{\text{mach}}$. Three consequences bite repeatedly:

- **Floats are not associative.** $(a+b)+c \neq a+(b+c)$ in general; summation order matters.
- **Catastrophic cancellation.** Subtracting two nearly-equal numbers annihilates significant
  digits. Computing variance as $\mathbb{E}[X^2]-\mathbb{E}[X]^2$ can return *negative*
  numbers; the two-pass or Welford formula avoids it.
- **No exact equality.** Never test `x == y` on floats; test `abs(x-y) < tol`.

The classic trap: the quadratic formula $x = \frac{-b\pm\sqrt{b^2-4ac}}{2a}$ loses precision
when $b^2\gg 4ac$ because one root subtracts near-equal quantities. The fix is to compute the
well-conditioned root first and get the other from $x_1 x_2 = c/a$.

```python
import numpy as np

def stable_quadratic(a, b, c):
    """Solve a x^2 + b x + c = 0 without catastrophic cancellation.

    We compute the root whose formula adds same-sign quantities, then
    recover the second root from the product relation x1*x2 = c/a, which
    sidesteps subtracting two nearly equal numbers.
    """
    disc = np.sqrt(b * b - 4 * a * c)
    q = -0.5 * (b + np.sign(b) * disc)      # avoids cancellation
    return q / a, c / q
```

---

## 2. Conditioning vs. stability

These two are constantly confused and must be kept separate.

- **Conditioning** is a property of the *problem*: how much the true answer changes when the
  input is perturbed. A problem with condition number $\kappa$ amplifies relative input error
  by up to $\kappa$ — *no algorithm can do better*. Inverting a near-singular matrix is
  ill-conditioned no matter how cleverly you code it.
- **Stability** is a property of the *algorithm*: whether it introduces error beyond what the
  conditioning forces. A **backward-stable** algorithm returns the exact answer to a slightly
  perturbed problem.

The governing inequality:

$$
\text{forward error} \;\lesssim\; \text{condition number} \times \text{backward error}.
$$

A good algorithm keeps backward error near $\varepsilon_{\text{mach}}$; if the answer is
still bad, the *problem* was ill-conditioned and you must reformulate or regularize. This is
why the linear-algebra module insists on QR over normal equations: same problem, but normal
equations square $\kappa$, turning a tolerable conditioning into an intolerable one.

---

## 3. Solving linear systems numerically

To solve $A\mathbf{x}=\mathbf{b}$, **never compute $A^{-1}$**. Inversion is more expensive,
less accurate, and throws away structure. Instead **factor and back-substitute**:

- **LU with partial pivoting** for general $A$: $PA=LU$, then solve two triangular systems.
  Pivoting (swapping rows to put the largest element on the diagonal) is what keeps Gaussian
  elimination stable; without it, a tiny pivot divides everything and amplifies error.
- **Cholesky** ($A=LL^\top$) for SPD matrices — twice as fast, inherently stable, and its
  failure flags loss of positive-definiteness.
- **QR** for least squares, preserving conditioning.

The cost of a dense solve is $O(n^3)$, but most real systems (factor graphs, finite-element
meshes, sparse Jacobians) are **sparse**, and exploiting that sparsity drops cost by orders of
magnitude — the difference between a SLAM backend that runs at frame rate and one that does
not. **Iterative solvers** (conjugate gradient for SPD systems) shine when $A$ is huge and
sparse and you only need a matrix-vector product, converging in far fewer than $n$ steps when
the spectrum is favorable (and faster still with a preconditioner).

---

## 4. Root finding and Newton's method

Many problems reduce to "find $x$ with $f(x)=0$" — equilibria, implicit constraints,
maximum-likelihood stationarity. **Bisection** is bulletproof but slow: bracket a sign change
and halve the interval, gaining one bit per step (linear convergence). **Newton's method**
uses the derivative for speed:

$$
x_{k+1} = x_k - \frac{f(x_k)}{f'(x_k)}.
$$

Near a simple root it converges **quadratically** — error squares each step,
$|e_{k+1}|\approx C|e_k|^2$ — so digits double. The price is fragility: it needs a good start,
a nonzero derivative, and can diverge or cycle otherwise. The robust practice is a **hybrid**
(e.g. Brent's method): Newton when it behaves, bisection as a safety net. The vector
generalization $\mathbf{x}_{k+1}=\mathbf{x}_k - J^{-1}\mathbf{f}(\mathbf{x}_k)$ (solve the
Jacobian system, do not invert) is the same Newton step that powers the optimizers in
[01-foundations-optimization.md](01-optimization.md).

```python
import numpy as np

def newton(f, df, x0, tol=1e-12, maxit=50):
    """Find a root of f via Newton's method with a simple safeguard.

    Newton converges quadratically near a simple root but can diverge from
    a poor start, so we cap iterations and stop on a small step. Production
    code would fall back to bisection when a step misbehaves.
    """
    x = x0
    for _ in range(maxit):
        fx = f(x)
        step = fx / df(x)
        x -= step
        if abs(step) < tol:
            break
    return x
```

---

## 5. Numerical differentiation and integration

**Differentiation by finite differences** trades truncation error against rounding error. The
**central difference**

$$
f'(x) \approx \frac{f(x+h) - f(x-h)}{2h} + O(h^2)
$$

is second-order accurate. But there is a sweet spot: too-large $h$ leaves truncation error,
too-small $h$ drowns the difference in floating-point cancellation. The optimal step for a
central difference scales like $h^* \sim \varepsilon_{\text{mach}}^{1/3}$. When you need exact
derivatives cheaply, **automatic differentiation** (the engine of every deep-learning
framework) computes them to machine precision with no step-size tuning — see
[01-autonomy-ml-ai.md](../autonomy/01-ml-ai.md). The **complex-step trick**,
$f'(x)\approx \operatorname{Im}[f(x+ih)]/h$, dodges cancellation entirely and is accurate to
machine epsilon.

**Integration (quadrature)** approximates $\int_a^b f\,dx$ by weighted samples. The
**trapezoidal rule** is $O(h^2)$; **Simpson's rule**, fitting parabolas, is $O(h^4)$;
**Gaussian quadrature** chooses both nodes and weights to integrate polynomials of degree
$2n-1$ exactly with $n$ points — remarkable efficiency for smooth integrands. In high
dimensions all of these die to the curse of dimensionality and you switch to **Monte Carlo**,
whose $1/\sqrt{N}$ error is dimension-independent (§7 of
[02-foundations-probability-and-stochastic.md](02-probability-and-stochastic.md)).

| Method | Order | Best for |
|---|---|---|
| Trapezoid | $O(h^2)$ | quick, low accuracy |
| Simpson | $O(h^4)$ | smooth 1-D integrands |
| Gauss quadrature | spectral | very smooth functions |
| Monte Carlo | $O(N^{-1/2})$ | high dimension |

---

## 6. Integrating ODEs: Euler to Runge-Kutta

Your vehicle dynamics are an ODE $\dot{\mathbf{x}} = f(\mathbf{x}, u, t)$, and you must march
the state forward in discrete steps. **Forward (explicit) Euler** is the simplest:

$$
\mathbf{x}_{n+1} = \mathbf{x}_n + h\, f(\mathbf{x}_n, t_n),
$$

but it is only **first-order** ($O(h)$ local error per step) and its stability is poor — it
needs tiny steps to avoid blowing up. The workhorse is **fourth-order Runge-Kutta (RK4)**,
which samples the slope four times per step and blends them:

$$
\begin{aligned}
k_1 &= f(\mathbf{x}_n, t_n) \\
k_2 &= f(\mathbf{x}_n + \tfrac{h}{2}k_1,\ t_n+\tfrac{h}{2}) \\
k_3 &= f(\mathbf{x}_n + \tfrac{h}{2}k_2,\ t_n+\tfrac{h}{2}) \\
k_4 &= f(\mathbf{x}_n + h\,k_3,\ t_n+h) \\
\mathbf{x}_{n+1} &= \mathbf{x}_n + \tfrac{h}{6}\,(k_1 + 2k_2 + 2k_3 + k_4).
\end{aligned}
$$

RK4 is **fourth-order** ($O(h^4)$ local error) — for the same accuracy it takes vastly larger
steps than Euler, more than paying back the four evaluations. **Adaptive** schemes (RK45,
Dormand-Prince) run two orders simultaneously, estimate the local error from their difference,
and shrink or grow $h$ to hold error under a tolerance — the integrators inside every serious
simulator and SITL stack.

```python
import numpy as np

def rk4_step(f, x, t, h):
    """Advance an ODE x' = f(x, t) by one RK4 step of size h.

    RK4 samples the slope four times across the interval and forms a
    weighted average, achieving fourth-order accuracy. For smooth dynamics
    it is dramatically more accurate per step than forward Euler.
    """
    k1 = f(x, t)
    k2 = f(x + 0.5 * h * k1, t + 0.5 * h)
    k3 = f(x + 0.5 * h * k2, t + 0.5 * h)
    k4 = f(x + h * k3, t + h)
    return x + (h / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
```

---

## 7. Stability of integrators — stiffness and step size

Accuracy is not enough; an integrator must also be **stable** — its errors must not grow
without bound. Test on the linear model $\dot x = \lambda x$ with solution $x=e^{\lambda t}$.
Forward Euler gives $x_{n+1}=(1+h\lambda)x_n$, which stays bounded only when

$$
|1 + h\lambda| \le 1.
$$

For a real negative $\lambda$ (a decaying mode) this forces $h \le 2/|\lambda|$ — a hard
**step-size limit**. A system with both fast and slow modes is **stiff**: the fast mode you
do not even care about dictates a punishingly small step for explicit methods. The cure is an
**implicit** method like backward Euler, $x_{n+1}=x_n + h\lambda x_{n+1}$, whose amplification
factor $1/(1-h\lambda)$ is bounded for *any* $h>0$ when $\lambda<0$ (**A-stability**) — you
pay a solve per step but escape the step-size tyranny. Recognizing stiffness (fast electrical
or actuator dynamics coupled to slow rigid-body motion) and choosing an implicit or adaptive
solver is exactly the judgment that keeps a simulator both fast and correct. The continuous
stability theory behind $\lambda$ lives in
[06-autonomy-control-theory.md](../autonomy/06-control-theory.md).

---

## 8. Where numerics decide success in the stack

| Stack component | Numerical concern |
|---|---|
| Dynamics propagation / SITL | ODE integrator order & stability (§6, §7) |
| EKF covariance inverse | conditioning, Cholesky stability (§2, §3) |
| Finite-difference Jacobians | step-size / cancellation tradeoff (§5) |
| Optimizer Newton steps | factor-don't-invert, root finding (§3, §4) |
| Variance / statistics online | catastrophic cancellation (§1) |
| Large sparse SLAM solve | sparse direct vs. iterative solvers (§3) |
| Sensor integration over time | accumulation order, drift (§1) |

The throughline: the mathematics promises an answer, but only careful arithmetic *delivers*
one. The competent engineer treats $\varepsilon_{\text{mach}}$, conditioning, and stability as
real forces — like mass and drag — that shape what computation can actually achieve, and
designs algorithms that respect them instead of being ambushed by them at 2 a.m. over a test
range.

---

## Sources & further study

- **Trefethen & Bau, *Numerical Linear Algebra*** — conditioning, stability, backward error,
  factorizations; the clearest modern treatment.
- **Heath, *Scientific Computing: An Introductory Survey*** — broad, practical tour of floating
  point, root finding, quadrature, and ODEs.
- **Press et al., *Numerical Recipes*** — battle-tested algorithms with candid discussion of
  pitfalls (read the prose, port the ideas).
- **Hairer, Nørsett & Wanner, *Solving Ordinary Differential Equations I & II*** — the
  definitive reference on Runge-Kutta methods and stiffness.
- **Goldberg, *"What Every Computer Scientist Should Know About Floating-Point Arithmetic"*** —
  the essay every engineer should read once.
- **Golub & Van Loan, *Matrix Computations*** — costs and stability of every linear solve.

> Framing note: precision is a story the computer tells, and numerical methods is learning to
> audit it. The frightening failures are not the ones that crash loudly but the ones that
> return a confident, wrong number — a covariance that drifted negative, an integrator that
> aliased a fast mode, a gradient lost to cancellation. The engineer who internalizes floating
> point, conditioning, and stability is the one whose systems degrade *gracefully and visibly*
> rather than failing silently when it matters most.
