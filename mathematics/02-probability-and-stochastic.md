# Probability & Stochastic Processes — Reasoning Under Uncertainty

> **Why this exists.** Your autonomy stack never sees the world; it sees *noisy
> measurements of the world* and must act anyway. A GPS fix is a true position plus a
> blob of error. A camera detection is a guess with a confidence. An IMU integrates
> drift. Probability is the calculus that lets a machine hold many hypotheses at once,
> weight them by evidence, and update rationally as data arrives. Bayes' rule is the
> beating heart of every filter you will build; expectation and variance are how you
> reason about cost and risk; Markov chains and Gaussian processes are how you model
> systems that evolve through time and space.
>
> **What mastering it makes you.** The engineer who treats uncertainty as a
> first-class quantity to be propagated and reduced — not a nuisance to be ignored —
> and who can therefore explain *why* the filter is overconfident, *how much* a new
> sensor actually helps, and *when* a "99% sure" detection should still be doubted.

This module is the probabilistic spine of the curriculum. The optimization that turns a
likelihood into an estimate is in [01-foundations-optimization.md](01-optimization.md);
the linear algebra of covariance lives in
[03-foundations-linear-algebra-applied.md](03-linear-algebra-applied.md);
the Monte-Carlo numerics are sharpened in
[04-foundations-numerical-methods.md](04-numerical-methods.md). Downstream it
is the language of the estimators in [09-autonomy-gnc.md](../autonomy/09-gnc.md), the learning
in [01-autonomy-ml-ai.md](../autonomy/01-ml-ai.md), the decision-making in
[10-autonomy-planning-decision.md](../autonomy/10-planning-decision.md), and it sits beside the
general math foundation in [03-foundations-mathematics.md](../foundations/03-mathematics.md).
Information-theoretic measures that build on it appear in
[06-foundations-information-theory.md](06-information-theory.md).

---

## Table of Contents

1. [Probability as a measure of belief](#1-probability-as-a-measure-of-belief)
2. [Random variables, expectation, variance](#2-random-variables-expectation-variance)
3. [Bayes' rule — the update engine](#3-bayes-rule--the-update-engine)
4. [The Gaussian and why it is everywhere](#4-the-gaussian-and-why-it-is-everywhere)
5. [Markov chains — memoryless evolution](#5-markov-chains--memoryless-evolution)
6. [Gaussian processes — distributions over functions](#6-gaussian-processes--distributions-over-functions)
7. [Monte Carlo — when you cannot integrate](#7-monte-carlo--when-you-cannot-integrate)
8. [Where uncertainty flows in the stack](#8-where-uncertainty-flows-in-the-stack)
9. [Sources & further study](#sources--further-study)

---

## 1. Probability as a measure of belief

Formally a probability space is $(\Omega, \mathcal{F}, P)$: a sample space $\Omega$ of
outcomes, a $\sigma$-algebra $\mathcal{F}$ of events, and a measure $P$ obeying the
**Kolmogorov axioms** — $P(A)\ge 0$, $P(\Omega)=1$, and countable additivity for disjoint
events. For engineering, the useful reading is **Bayesian**: $P(A)$ is a *degree of
belief* that you update with evidence. Both views obey the same algebra; the Bayesian
reading is what makes filters make sense.

Two facts do most of the work. **Conditional probability**:

$$
P(A \mid B) = \frac{P(A \cap B)}{P(B)}, \qquad P(B) > 0.
$$

And the **law of total probability** over a partition $\{B_i\}$:

$$
P(A) = \sum_i P(A \mid B_i)\, P(B_i).
$$

Events $A,B$ are **independent** when $P(A\cap B)=P(A)P(B)$, equivalently
$P(A\mid B)=P(A)$ — knowing $B$ tells you nothing about $A$. Independence is the
assumption that makes joint distributions tractable; *conditional* independence (the
heart of Markov models) is the weaker, more realistic cousin.

---

## 2. Random variables, expectation, variance

A **random variable** $X$ maps outcomes to numbers. Its distribution is described by a
**pdf** $p(x)$ (continuous) or **pmf** (discrete). The **expectation** is the
probability-weighted average:

$$
\mathbb{E}[X] = \int x\, p(x)\, dx, \qquad
\mathbb{E}[g(X)] = \int g(x)\, p(x)\, dx.
$$

Expectation is **linear**: $\mathbb{E}[aX + bY] = a\mathbb{E}[X] + b\mathbb{E}[Y]$ —
*always*, even when $X,Y$ are dependent. **Variance** measures spread:

$$
\operatorname{Var}(X) = \mathbb{E}\big[(X - \mathbb{E}[X])^2\big] = \mathbb{E}[X^2] - \mathbb{E}[X]^2.
$$

For a random *vector* $\mathbf{x}$, the analog is the **covariance matrix**

$$
\Sigma = \mathbb{E}\big[(\mathbf{x}-\mu)(\mathbf{x}-\mu)^\top\big],
$$

a symmetric PSD matrix whose diagonal holds per-component variances and whose off-diagonal
holds correlations. Under a linear map $\mathbf{y}=A\mathbf{x}+b$:

$$
\mu_y = A\mu_x + b, \qquad \Sigma_y = A\,\Sigma_x A^\top.
$$

That last identity — **covariance propagation through a linear transform** — is the
single most-used equation in estimation. The EKF's predict step is exactly this with $A$
the dynamics Jacobian.

```python
import numpy as np

def propagate_covariance(A, Sigma, Q):
    """Propagate a Gaussian covariance through y = A x + noise.

    The transformed covariance is A Sigma A' plus the additive process
    noise Q. This is the EKF prediction of uncertainty in one line.
    """
    return A @ Sigma @ A.T + Q
```

---

## 3. Bayes' rule — the update engine

Rearranging conditional probability in two directions and equating gives **Bayes' rule**:

$$
\underbrace{p(x \mid z)}_{\text{posterior}}
= \frac{\overbrace{p(z \mid x)}^{\text{likelihood}}\;\overbrace{p(x)}^{\text{prior}}}
       {\underbrace{p(z)}_{\text{evidence}}},
\qquad p(z) = \int p(z\mid x)\,p(x)\,dx.
$$

Read it as a verb: *the posterior belief about state $x$ after seeing measurement $z$ is
the prior belief reweighted by how well each $x$ predicts $z$.* The evidence $p(z)$ is
just a normalizer ensuring the posterior integrates to one; in many algorithms you can
ignore it and work up to proportionality, $p(x\mid z) \propto p(z\mid x)\,p(x)$.

**Recursive Bayes** is the loop your filter runs forever:

$$
p(x_t \mid z_{1:t}) \propto p(z_t \mid x_t)\underbrace{\int p(x_t\mid x_{t-1})\,p(x_{t-1}\mid z_{1:t-1})\,dx_{t-1}}_{\text{prediction}}.
$$

Predict with the motion model, correct with the measurement, repeat. The Kalman filter is
this recursion when everything is linear-Gaussian; the particle filter is this recursion
approximated with samples (§7).

**Worked example — sensor fusion of two Gaussians.** Two independent measurements of a
scalar, $z_1\sim\mathcal{N}(x,\sigma_1^2)$ and $z_2\sim\mathcal{N}(x,\sigma_2^2)$, with a
flat prior, produce a posterior mean that is the **inverse-variance-weighted average**:

$$
\hat x = \frac{z_1/\sigma_1^2 + z_2/\sigma_2^2}{1/\sigma_1^2 + 1/\sigma_2^2},
\qquad \frac{1}{\sigma^2} = \frac{1}{\sigma_1^2} + \frac{1}{\sigma_2^2}.
$$

Precisions ($1/\sigma^2$) **add**. The fused estimate is always at least as confident as
either input — quantitatively *why* more sensors help.

---

## 4. The Gaussian and why it is everywhere

The multivariate Gaussian (normal) density is

$$
\mathcal{N}(\mathbf{x};\mu,\Sigma) = \frac{1}{(2\pi)^{n/2}|\Sigma|^{1/2}}
\exp\!\left(-\tfrac12 (\mathbf{x}-\mu)^\top \Sigma^{-1} (\mathbf{x}-\mu)\right).
$$

It dominates engineering for three reasons. **(1) The Central Limit Theorem:** sums of many
independent small effects converge to a Gaussian regardless of their individual
distributions — and sensor noise is usually such a sum. **(2) Closure:** Gaussians are
closed under linear maps, marginalization, and conditioning, so a linear-Gaussian system
*stays* Gaussian forever, summarized entirely by $(\mu,\Sigma)$. **(3) Maximum entropy:**
among all distributions with a given mean and covariance, the Gaussian assumes the least
(it is the maximum-entropy choice — see
[06-foundations-information-theory.md](06-information-theory.md)).

The exponent $(\mathbf{x}-\mu)^\top\Sigma^{-1}(\mathbf{x}-\mu)$ is the squared
**Mahalanobis distance** — error measured in units of standard deviation, accounting for
correlation. Maximizing a Gaussian likelihood is therefore *exactly* weighted least squares
(§4 of [01-foundations-optimization.md](01-optimization.md)); the probabilistic
and optimization views are two faces of one coin.

**Gaussian conditioning (the Kalman gain in disguise).** Partition a joint Gaussian over
$(\mathbf{x},\mathbf{z})$. The conditional $p(\mathbf{x}\mid\mathbf{z})$ is again Gaussian:

$$
\mu_{x|z} = \mu_x + \Sigma_{xz}\Sigma_{zz}^{-1}(\mathbf{z}-\mu_z), \qquad
\Sigma_{x|z} = \Sigma_{xx} - \Sigma_{xz}\Sigma_{zz}^{-1}\Sigma_{zx}.
$$

The term $K = \Sigma_{xz}\Sigma_{zz}^{-1}$ is the **Kalman gain**: how strongly to trust
the new measurement. Conditioning *always shrinks* covariance — observing data never makes
you less certain.

---

## 5. Markov chains — memoryless evolution

A stochastic process $\{X_t\}$ is **Markov** if the future depends on the past only through
the present:

$$
P(X_{t+1} \mid X_t, X_{t-1}, \dots, X_0) = P(X_{t+1}\mid X_t).
$$

For a finite state space this is captured by a **transition matrix** $T$ with
$T_{ij}=P(X_{t+1}=j\mid X_t=i)$, each row summing to one. A distribution $\pi$ (a row
vector) evolves by $\pi_{t+1} = \pi_t T$. A **stationary distribution** satisfies

$$
\pi = \pi T,
$$

i.e. $\pi$ is the left eigenvector of $T$ with eigenvalue 1. For an irreducible aperiodic
chain this distribution is unique and the chain converges to it from any start — the
foundation of MCMC sampling (§7) and of PageRank.

Markov chains underlie **Hidden Markov Models** (hidden state, noisy observations — the
discrete cousin of the Kalman filter) and **Markov Decision Processes** (states, actions,
rewards — the foundation of reinforcement learning and planning in
[10-autonomy-planning-decision.md](../autonomy/10-planning-decision.md)).

```python
import numpy as np

def stationary_distribution(T, tol=1e-12):
    """Find the stationary distribution pi satisfying pi = pi T.

    We take the left eigenvector of T whose eigenvalue is 1 and normalize
    it to a probability vector. For an ergodic chain this is the unique
    long-run fraction of time spent in each state.
    """
    w, V = np.linalg.eig(T.T)               # left eigenvectors of T
    idx = np.argmin(np.abs(w - 1.0))        # eigenvalue closest to 1
    pi = np.real(V[:, idx])
    return pi / pi.sum()
```

---

## 6. Gaussian processes — distributions over functions

Sometimes you want a probability distribution not over a vector but over an entire
*function* — a terrain height field, a signal-strength map, a smooth control input. A
**Gaussian process (GP)** does exactly that: any finite set of function values is jointly
Gaussian. It is specified by a mean function $m(x)$ and a **covariance (kernel)** function
$k(x,x')$ encoding how correlated nearby points are:

$$
f \sim \mathcal{GP}(m, k), \qquad k(x,x') = \sigma_f^2 \exp\!\left(-\frac{\|x-x'\|^2}{2\ell^2}\right)
$$

(the ubiquitous squared-exponential kernel, with length scale $\ell$). Given noisy
observations $\mathbf{y}$ at inputs $X$, the predictive distribution at a new point $x_*$ is
Gaussian with

$$
\bar f_* = k_*^\top (K + \sigma_n^2 I)^{-1}\mathbf{y}, \qquad
\operatorname{Var}(f_*) = k(x_*,x_*) - k_*^\top (K+\sigma_n^2 I)^{-1} k_*,
$$

where $K_{ij}=k(x_i,x_j)$ and $k_* = [k(x_*,x_i)]$. GPs give **calibrated uncertainty** —
the variance grows far from data — which is why they shine in Bayesian optimization, terrain
modeling, and sample-efficient learning. The cost is the $O(N^3)$ matrix inversion, solved
with the Cholesky factorization from
[03-foundations-linear-algebra-applied.md](03-linear-algebra-applied.md).

---

## 7. Monte Carlo — when you cannot integrate

Most expectations of interest have no closed form. **Monte Carlo** estimates them by
sampling: to approximate $\mathbb{E}[g(X)] = \int g(x)p(x)dx$, draw $x_i \sim p$ and average,

$$
\hat\mu_N = \frac{1}{N}\sum_{i=1}^N g(x_i).
$$

By the law of large numbers $\hat\mu_N \to \mathbb{E}[g(X)]$, and the **standard error
shrinks like $1/\sqrt{N}$** — *independent of dimension*, the property that makes Monte
Carlo beat grid quadrature in high dimensions. The catch: $1/\sqrt{N}$ is slow, so cutting
error by 10× costs 100× the samples.

**Importance sampling** reweights samples from an easier proposal $q$:
$\mathbb{E}_p[g] = \mathbb{E}_q[g(x)\,p(x)/q(x)]$. **Markov-chain Monte Carlo (MCMC)** builds
a Markov chain (§5) whose stationary distribution is the target $p$, letting you sample
distributions you cannot even normalize. And the **particle filter** is sequential
importance sampling applied to recursive Bayes (§3): represent the posterior by weighted
particles, propagate through the motion model, reweight by the likelihood, resample. It is
the go-to estimator when the Gaussian assumption breaks — nonlinear dynamics, multimodal
beliefs, GPS-denied localization with a map.

```python
import numpy as np

def monte_carlo_expectation(g, sampler, N):
    """Estimate E[g(X)] by averaging g over N samples of X.

    The estimate is unbiased and its standard error scales as 1/sqrt(N),
    which is why Monte Carlo remains practical even in high dimensions
    where deterministic quadrature becomes hopeless.
    """
    xs = sampler(N)
    vals = np.array([g(x) for x in xs])
    return vals.mean(), vals.std(ddof=1) / np.sqrt(N)   # estimate, std error
```

---

## 8. Where uncertainty flows in the stack

| Stack component | Probabilistic object |
|---|---|
| EKF / UKF | recursive Bayes on a Gaussian (§3, §4) |
| Particle filter (GPS-denied) | sequential Monte Carlo (§7) |
| Track fusion | covariance propagation + Gaussian conditioning (§2, §4) |
| Detection confidence | likelihood / posterior probability (§3) |
| HMM behavior models | Markov chains (§5) |
| Reinforcement learning | Markov Decision Process (§5) |
| Bayesian optimization, mapping | Gaussian processes (§6) |
| Risk-aware planning | expectation and variance of cost (§2) |

The throughline: a competent autonomy engineer never reports a number without its
**uncertainty**, never updates a belief without **Bayes**, and never trusts a point
estimate where the *distribution* tells a richer story. Probability is the discipline that
keeps a confident machine honest.

---

## Sources & further study

- **Bishop, *Pattern Recognition and Machine Learning*** — the best single bridge from
  probability to estimation and learning; Gaussians, Bayes, GPs, sampling all in one voice.
- **Thrun, Burgard & Fox, *Probabilistic Robotics*** — recursive Bayes, Kalman and particle
  filters, written for exactly the autonomy stack this curriculum builds.
- **Rasmussen & Williams, *Gaussian Processes for Machine Learning*** — the definitive GP
  text, freely available online.
- **Ross, *Introduction to Probability Models*** — clean, applied treatment of Markov chains
  and stochastic processes.
- **Cover & Thomas, *Elements of Information Theory*** — the entropy view of why the Gaussian
  is special and how uncertainty is measured.
- **MacKay, *Information Theory, Inference, and Learning Algorithms*** — Bayesian inference
  and Monte Carlo with unusual clarity; free online.

> Framing note: certainty is a luxury the real world rarely grants, and pretending otherwise
> is how systems fail quietly. Probability is the engineering of *humility made
> computable* — a machine that knows what it does not know can ask for more data, hedge its
> commitments, and refuse to act when the evidence is thin. That is not weakness. That is the
> difference between a system you can trust over a runway and a demo that worked once.
