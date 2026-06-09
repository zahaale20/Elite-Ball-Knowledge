# Applied Linear Algebra — The Language of State and Transformation

> **Why this exists.** State is a vector. Sensors are matrices. Motion is a linear map.
> Almost every quantity your autonomy stack tracks — position, velocity, attitude,
> feature locations, network activations — lives in a vector space, and almost every
> operation on it is a matrix acting on that vector. Linear algebra is not a subject you
> pass and forget; it is the *notation in which estimation, control, and learning are
> written*. When the EKF inverts an innovation covariance, when visual odometry recovers
> camera motion from an essential matrix, when PCA compresses a sensor stream, when a
> least-squares calibration fits a model — those are all decompositions of matrices,
> done well or done badly.
>
> **What mastering it makes you.** The engineer who reads a matrix and sees *geometry* —
> rotation, projection, scaling, rank-deficiency — and who therefore knows before running
> anything whether a solve is well-posed, why a covariance went singular, and which
> decomposition makes the numerics behave.

This is the structural backbone beneath the rest of the foundations. The optimization that
uses these solves is in [01-foundations-optimization.md](01-optimization.md); the
covariance algebra that depends on it is in
[02-foundations-probability-and-stochastic.md](02-probability-and-stochastic.md);
the finite-precision care that keeps factorizations stable is in
[04-foundations-numerical-methods.md](04-numerical-methods.md). It is the working
language of [09-autonomy-gnc.md](../autonomy/09-gnc.md) and
[06-autonomy-control-theory.md](../autonomy/06-control-theory.md), reappears as weight matrices
in [01-autonomy-ml-ai.md](../autonomy/01-ml-ai.md), and extends the general math of
[03-foundations-mathematics.md](../foundations/03-mathematics.md).

---

## Table of Contents

1. [Vector spaces and the four subspaces](#1-vector-spaces-and-the-four-subspaces)
2. [Matrices as transformations](#2-matrices-as-transformations)
3. [Eigenvalues — the natural axes of a map](#3-eigenvalues--the-natural-axes-of-a-map)
4. [The SVD — the master decomposition](#4-the-svd--the-master-decomposition)
5. [QR and Cholesky — the solver's toolkit](#5-qr-and-cholesky--the-solvers-toolkit)
6. [Least squares, done right](#6-least-squares-done-right)
7. [Conditioning — when a solve betrays you](#7-conditioning--when-a-solve-betrays-you)
8. [Where each decomposition runs in the stack](#8-where-each-decomposition-runs-in-the-stack)
9. [Sources & further study](#sources--further-study)

---

## 1. Vector spaces and the four subspaces

A **vector space** is a set closed under addition and scalar multiplication. The **span**
of a set of vectors is all their linear combinations; a **basis** is a minimal spanning set;
the **dimension** is its size. Vectors are **linearly independent** when none is a
combination of the others — the condition that a basis is not wasteful.

Every $m\times n$ matrix $A$ induces **four fundamental subspaces** that completely describe
what it does:

| Subspace | Definition | Lives in | Dimension |
|---|---|---|---|
| Column space $\mathcal{C}(A)$ | all $A\mathbf{x}$ | $\mathbb{R}^m$ | $r$ (rank) |
| Null space $\mathcal{N}(A)$ | all $\mathbf{x}$ with $A\mathbf{x}=0$ | $\mathbb{R}^n$ | $n-r$ |
| Row space $\mathcal{C}(A^\top)$ | all $A^\top\mathbf{y}$ | $\mathbb{R}^n$ | $r$ |
| Left null space $\mathcal{N}(A^\top)$ | all $\mathbf{y}$ with $A^\top\mathbf{y}=0$ | $\mathbb{R}^m$ | $m-r$ |

The **rank** $r$ is the number of independent directions $A$ actually uses. The
**rank-nullity theorem**, $\operatorname{rank}(A) + \dim\mathcal{N}(A) = n$, is the
conservation law: every input dimension is either stretched into the output or collapsed
into the null space. A solve $A\mathbf{x}=\mathbf{b}$ has a solution iff
$\mathbf{b}\in\mathcal{C}(A)$, and a *unique* one iff additionally $\mathcal{N}(A)=\{0\}$.
This is why a rank-deficient observation matrix makes a state **unobservable** — the missing
information lives in a null space the sensors never touch (the bridge to observability in
[09-autonomy-gnc.md](../autonomy/09-gnc.md)).

---

## 2. Matrices as transformations

Stop reading a matrix as a grid of numbers and start reading it as a *machine that moves
space*. The columns of $A$ are the images of the basis vectors: $A\mathbf{e}_j$ is column
$j$. So $A\mathbf{x}=\sum_j x_j (A\mathbf{e}_j)$ is just "rebuild the output from where the
axes went." Three transformations recur:

- **Rotation** $R$: orthogonal ($R^\top R = I$), preserves lengths and angles, $\det R = +1$.
  Attitude is a rotation $R\in SO(3)$.
- **Scaling** $\operatorname{diag}(\sigma_1,\dots,\sigma_n)$: stretches each axis.
- **Projection** $P$: idempotent ($P^2 = P$), collapses onto a subspace. The least-squares
  fit is a projection onto a column space.

The **determinant** measures the signed volume scaling: $|\det A|$ is how much $A$ inflates
volume, and $\det A = 0$ means $A$ squashes space into a lower dimension (singular,
non-invertible). The **trace** $\operatorname{tr}(A)=\sum_i A_{ii}$ equals the sum of
eigenvalues and shows up as total variance in a covariance matrix.

---

## 3. Eigenvalues — the natural axes of a map

An **eigenvector** $\mathbf{v}$ of $A$ is a direction the map only *stretches*, not rotates:

$$
A\mathbf{v} = \lambda \mathbf{v}, \qquad \mathbf{v} \neq 0,
$$

with **eigenvalue** $\lambda$ the stretch factor. Eigenvalues are roots of the
characteristic polynomial $\det(A - \lambda I) = 0$. When $A$ has a full set of independent
eigenvectors it **diagonalizes**, $A = V\Lambda V^{-1}$, which makes powers trivial:
$A^k = V\Lambda^k V^{-1}$. That is why eigenvalues govern *dynamics* — iterate
$\mathbf{x}_{t+1}=A\mathbf{x}_t$ and the behavior is dictated by whether $|\lambda_i|<1$
(decay, stable), $=1$ (marginal), or $>1$ (growth, unstable). This is the discrete-time
stability test underneath every controller in
[06-autonomy-control-theory.md](../autonomy/06-control-theory.md).

For **symmetric** matrices (covariances, Hessians, Gram matrices) the **spectral theorem**
gives the cleanest possible structure:

$$
A = Q\Lambda Q^\top, \qquad Q^\top Q = I, \quad \Lambda = \operatorname{diag}(\lambda_i),
$$

real eigenvalues, orthonormal eigenvectors. For a covariance matrix the eigenvectors are the
**principal axes** of the uncertainty ellipsoid and the eigenvalues are the variances along
them — the foundation of PCA and of every covariance ellipse you will ever plot.

```python
import numpy as np

def principal_axes(Sigma):
    """Return the principal axes and variances of a covariance matrix.

    Eigen-decomposition of a symmetric covariance yields orthonormal axes
    (the eigenvectors) and the variance along each (the eigenvalues). This
    is the geometry of an uncertainty ellipsoid and the math behind PCA.
    """
    vals, vecs = np.linalg.eigh(Sigma)      # ascending eigenvalues
    order = np.argsort(vals)[::-1]          # largest variance first
    return vecs[:, order], vals[order]
```

---

## 4. The SVD — the master decomposition

Every matrix — rectangular, rank-deficient, ugly — has a **singular value decomposition**:

$$
A = U\Sigma V^\top, \qquad U^\top U = I_m,\; V^\top V = I_n,\;
\Sigma = \operatorname{diag}(\sigma_1 \ge \sigma_2 \ge \dots \ge 0).
$$

Geometrically, *every linear map is a rotation, then an axis-aligned scaling, then another
rotation*. The **singular values** $\sigma_i$ are the stretch factors; the columns of $V$ are
the input axes that get stretched; the columns of $U$ are where they land. The number of
nonzero $\sigma_i$ is the rank. This single factorization gives you, for free:

- **Rank and null space** — count and read off the zero singular values.
- **The pseudoinverse** $A^+ = V\Sigma^+ U^\top$ (reciprocate nonzero $\sigma_i$), which
  solves least squares even when $A$ is rank-deficient.
- **The best low-rank approximation** (Eckart-Young): truncating to the top $k$ singular
  values gives the closest rank-$k$ matrix in both Frobenius and spectral norm:

$$
A_k = \sum_{i=1}^k \sigma_i u_i v_i^\top, \qquad
\|A - A_k\|_2 = \sigma_{k+1}.
$$

This is the engine of **PCA / dimensionality reduction**, of **denoising** (small singular
values are usually noise), and of recovering camera motion from the essential matrix in
visual odometry. The **condition number** falls out too: $\kappa = \sigma_{\max}/\sigma_{\min}$
(§7).

---

## 5. QR and Cholesky — the solver's toolkit

You almost never want $A^{-1}$ explicitly; you want to *solve* systems stably and cheaply via
factorization.

**QR decomposition.** $A = QR$ with $Q$ orthogonal and $R$ upper-triangular (via
Gram-Schmidt or, better, Householder reflections). Solving $A\mathbf{x}=\mathbf{b}$ becomes
$R\mathbf{x}=Q^\top\mathbf{b}$ — one cheap triangular back-substitution. QR is the
numerically sound way to do **least squares** without forming $A^\top A$ (§6), because $Q$
preserves norms and does not amplify error.

**Cholesky decomposition.** For symmetric positive-definite $A$ (covariances, Hessians,
normal-equation matrices):

$$
A = LL^\top, \qquad L \text{ lower-triangular}.
$$

It is twice as fast as LU and inherently stable for SPD matrices. Every Kalman update,
every GP regression, every Gauss-Newton normal-equation solve runs a Cholesky underneath.
A failed Cholesky is also a *diagnostic*: if it breaks, your matrix is not positive
definite, which usually means a covariance has gone numerically sick.

| Decomposition | Applies to | Cost | Primary use |
|---|---|---|---|
| LU | general square | $O(n^3)$ | general linear solve |
| QR | general | $O(mn^2)$ | least squares, stability |
| Cholesky | SPD | $\tfrac12 O(n^3)$ | covariance / normal eqns |
| Eigen | symmetric | $O(n^3)$ | PCA, stability, modes |
| SVD | any | $O(mn^2)$ | rank, pseudoinverse, low-rank |

```python
import numpy as np

def solve_spd(A, b):
    """Solve A x = b for symmetric positive-definite A via Cholesky.

    Cholesky factorizes A = L L' and solves two triangular systems. It is
    faster and more stable than a general inverse, and its failure is a
    useful signal that A is not positive definite.
    """
    L = np.linalg.cholesky(A)               # A = L L'
    y = np.linalg.solve(L, b)               # forward substitution
    return np.linalg.solve(L.T, y)          # back substitution
```

---

## 6. Least squares, done right

The overdetermined system $A\mathbf{x}\approx\mathbf{b}$ ($m>n$) almost never has an exact
solution, so we minimize the residual $\|A\mathbf{x}-\mathbf{b}\|_2^2$. The geometric picture
is decisive: the best $\mathbf{x}$ makes $A\mathbf{x}$ the **orthogonal projection** of
$\mathbf{b}$ onto the column space, so the residual is perpendicular to every column —
$A^\top(A\mathbf{x}-\mathbf{b})=0$ — giving the **normal equations**
$A^\top A\,\mathbf{x}=A^\top\mathbf{b}$.

But *do not solve them that way*. Forming $A^\top A$ **squares the condition number**
($\kappa(A^\top A)=\kappa(A)^2$), so a moderately ill-conditioned problem becomes a disaster.
Instead use **QR** ($R\mathbf{x}=Q^\top\mathbf{b}$) for full-rank problems, or the **SVD**
pseudoinverse for rank-deficient ones, where you can also truncate tiny singular values to
regularize. This distinction — same math, very different numerics — is exactly the kind of
thing that separates a calibration that converges from one that quietly returns garbage.
The optimization view of all this is in
[01-foundations-optimization.md](01-optimization.md).

---

## 7. Conditioning — when a solve betrays you

The **condition number** of a matrix quantifies how much it amplifies relative error:

$$
\kappa(A) = \frac{\sigma_{\max}}{\sigma_{\min}}.
$$

A perturbation $\delta\mathbf{b}$ in the right-hand side can blow up in the solution by up to
$\kappa(A)$:

$$
\frac{\|\delta\mathbf{x}\|}{\|\mathbf{x}\|} \le \kappa(A)\,\frac{\|\delta\mathbf{b}\|}{\|\mathbf{b}\|}.
$$

A rule of thumb: with double precision (~16 significant digits), a condition number of
$10^k$ costs you roughly $k$ digits of accuracy. At $\kappa\approx 10^{16}$ the matrix is
**numerically singular** and the solve is meaningless. This is why covariance matrices that
become nearly rank-deficient (a state pair perfectly correlated) make filters diverge, and
why **regularization** (adding $\lambda I$, raising $\sigma_{\min}$) and **good
factorizations** are not optional niceties — they are what keep the geometry honest under
finite precision. The numerical mechanics are continued in
[04-foundations-numerical-methods.md](04-numerical-methods.md).

---

## 8. Where each decomposition runs in the stack

| Stack component | Linear algebra underneath |
|---|---|
| EKF covariance update | Cholesky + matrix products (§5) |
| Visual odometry (essential matrix) | SVD (§4) |
| PCA / sensor compression | eigen / SVD (§3, §4) |
| Least-squares calibration | QR / SVD (§5, §6) |
| Controller stability analysis | eigenvalues of system matrix (§3) |
| Observability check | rank of observability matrix (§1) |
| GP regression | Cholesky of kernel matrix (§5) |
| Neural network layers | matrix-vector products (§2) |

The recurring discipline: see the matrix as a *transformation*, choose the *decomposition*
that exposes the structure you need, and respect the *conditioning* that finite precision
imposes. Do those three things and the linear core of the whole autonomy stack stops being a
black box and becomes geometry you can reason about.

---

## Sources & further study

- **Strang, *Linear Algebra and Its Applications*** (and *Introduction to Linear Algebra*) —
  the four subspaces, geometry-first intuition, the best on-ramp there is.
- **Trefethen & Bau, *Numerical Linear Algebra*** — SVD, QR, conditioning, stability with
  rigor and unusual clarity; the bridge to the numerics module.
- **Golub & Van Loan, *Matrix Computations*** — the encyclopedic reference for every
  factorization and its cost.
- **Boyd & Vandenberghe, *Introduction to Applied Linear Algebra*** — applied, vectors-and-
  matrices view tied to least squares and data; free online.
- **Horn & Johnson, *Matrix Analysis*** — the rigorous theory of eigenvalues, norms, and
  positive-definiteness when you need proofs.

> Framing note: linear algebra is the alphabet of engineering — and like an alphabet, fluency
> is invisible until it is missing. The engineer who *sees* a rotation in an orthogonal matrix,
> a collapse in a zero singular value, a stability margin in an eigenvalue, never has to
> "figure out the math" mid-debug; the geometry is already in their hands. Learn to read
> matrices as motion, and most of estimation, control, and learning stops being a wall of
> symbols and becomes a few shapes you already know.
