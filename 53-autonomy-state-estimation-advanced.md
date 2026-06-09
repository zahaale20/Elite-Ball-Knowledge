# Advanced State Estimation — Factor Graphs, Smoothing & Robust Estimation

> **Why this exists.** The Kalman filter answers "where am I *now*?" by throwing
> away the past. But the optimal estimate of any pose uses *all* measurements,
> including future ones — a filter is strictly worse than a smoother. Modern
> robotics reframes estimation as **inference on a factor graph**: a sparse
> probabilistic model whose maximum-a-posteriori solution is a nonlinear
> least-squares problem solved by the same machinery as SLAM and bundle
> adjustment. Mastering this reframing unifies SLAM, sensor fusion, calibration,
> and tracking under one mathematical roof — and unlocks incremental smoothers
> (iSAM2) that deliver smoothing accuracy at filtering speed.
>
> **What mastering it makes you.** The engineer who reaches for a factor graph
> instead of bolting another state onto an already-fragile EKF, who knows when
> marginalization is safe and when it destroys sparsity, and who can make an
> estimator survive 30% outliers with the right robust kernel.

This module is the mathematical capstone of the estimation thread: it generalizes
the filters of [28-autonomy-gnc.md](28-autonomy-gnc.md), the graph back-end of
[51-autonomy-slam-and-mapping.md](51-autonomy-slam-and-mapping.md), and the
fusion of [52-autonomy-sensor-fusion.md](52-autonomy-sensor-fusion.md) into a
single MAP-inference framework. The optimization rests on the calculus and linear
algebra of [03-foundations-mathematics.md](03-foundations-mathematics.md), and its
robustness claims must be validated per
[06-foundations-simulation-test-verification.md](06-foundations-simulation-test-verification.md).
The decision layer that consumes its estimates lives in
[29-autonomy-planning-decision.md](29-autonomy-planning-decision.md).

---

## Table of Contents

1. [From filtering to MAP inference](#1-from-filtering-to-map-inference)
2. [Factor graphs](#2-factor-graphs)
3. [Solving the nonlinear least-squares problem](#3-solving-the-nonlinear-least-squares-problem)
4. [On-manifold optimization](#4-on-manifold-optimization)
5. [Incremental smoothing — iSAM2 and the Bayes tree](#5-incremental-smoothing--isam2-and-the-bayes-tree)
6. [Marginalization, fixed-lag smoothing, and sparsity](#6-marginalization-fixed-lag-smoothing-and-sparsity)
7. [Robust estimation — surviving outliers](#7-robust-estimation--surviving-outliers)
8. [Practice this week](#8-practice-this-week)
9. [Sources & further study](#9-sources--further-study)

---

## 1. From filtering to MAP inference

A filter computes the *marginal* posterior of the latest state. A **smoother**
computes the *joint* posterior over the whole trajectory and is provably at least
as accurate. The maximum-a-posteriori estimate of all variables $\mathbf{X}$ given
all measurements $\mathbf{Z}$ is

$$
\mathbf{X}^* = \arg\max_{\mathbf{X}} p(\mathbf{X}\mid\mathbf{Z}) = \arg\max_{\mathbf{X}} p(\mathbf{Z}\mid\mathbf{X})\,p(\mathbf{X}).
$$

Assuming Gaussian noise, each measurement contributes a factor
$\propto \exp(-\tfrac12 \|h_i(\mathbf{X}) - \mathbf{z}_i\|^2_{\Sigma_i})$, and taking
the negative log turns the product into the familiar weighted sum of squared
residuals:

$$
\mathbf{X}^* = \arg\min_{\mathbf{X}} \sum_i \big\| h_i(\mathbf{X}) - \mathbf{z}_i \big\|^2_{\Sigma_i},
\qquad \|\mathbf{r}\|^2_\Sigma = \mathbf{r}^\top \Sigma^{-1} \mathbf{r}.
$$

This is the unifying statement of the module: **all of estimation is one nonlinear
least-squares problem.** SLAM, bundle adjustment, VIO, and calibration differ only
in which residuals appear.

---

## 2. Factor graphs

A **factor graph** is a bipartite graph that makes the structure of the above
problem explicit: circular **variable nodes** (poses, landmarks, biases,
calibration) and square **factor nodes** (measurements / priors), with an edge
when a factor depends on a variable.

```
   (x0)───[prior]
     │
   [odom]
     │
   (x1)──[obs]──(l1)
     │            │
   [odom]       [obs]
     │            │
   (x2)──[obs]──(l2)
     │
   [IMU preint]
     │
   (x3)──[GNSS]
```

Each factor $\phi_i$ encodes one term of the cost. The graph is **sparse** — a
factor touches only the few variables it measures — and this sparsity is the
entire reason the optimization is tractable. The factor-graph view is implemented
directly in **GTSAM** (Georgia Tech) and **g2o**; **Ceres Solver** expresses the
same problem as residual blocks.

The probability factorizes as

$$
p(\mathbf{X}\mid\mathbf{Z}) \propto \prod_i \phi_i(\mathbf{X}_i),
\qquad \phi_i(\mathbf{X}_i) \propto \exp\!\Big(-\tfrac12\|h_i(\mathbf{X}_i)-\mathbf{z}_i\|^2_{\Sigma_i}\Big).
$$

---

## 3. Solving the nonlinear least-squares problem

Linearize each residual about the current estimate $\mathbf{X}^{(t)}$,
$h_i(\mathbf{X}) \approx h_i(\mathbf{X}^{(t)}) + J_i\,\delta\mathbf{X}$, stack all
residuals and Jacobians (whitened by $\Sigma_i^{-1/2}$), and the problem becomes a
*linear* least squares in the increment:

$$
\delta\mathbf{X}^* = \arg\min_{\delta\mathbf{X}} \|A\,\delta\mathbf{X} - \mathbf{b}\|^2,
$$

whose normal equations are

$$
\underbrace{(A^\top A)}_{\Lambda,\ \text{information matrix}}\,\delta\mathbf{X} = A^\top \mathbf{b}.
$$

**Gauss–Newton** takes $\delta\mathbf{X} = (A^\top A)^{-1}A^\top\mathbf{b}$ and
iterates. **Levenberg–Marquardt** adds a damping term to interpolate between
Gauss–Newton and gradient descent for robustness far from the optimum:

$$
(A^\top A + \lambda\,\mathrm{diag}(A^\top A))\,\delta\mathbf{X} = A^\top\mathbf{b}.
$$

The linear solve exploits sparsity: a **sparse Cholesky** factorization
$\Lambda = R^\top R$ under a good variable ordering (COLAMD) runs in near-linear
time for the chain-and-loop structure of robotics graphs. The choice of ordering
*is* the difference between a fill-in disaster and a fast solve.

---

## 4. On-manifold optimization

Robot states live on **manifolds**, not vector spaces. A rotation is in $SO(3)$;
a pose is in $SE(3)$. You cannot add a 3-vector to a rotation matrix and stay on
the manifold. The fix: optimize in the **tangent space** and map back via the
exponential map.

Define a retraction $\boxplus: M \times \mathbb{R}^n \to M$ that perturbs a
manifold element by a tangent vector:

$$
R \boxplus \delta\boldsymbol\phi = R\,\mathrm{Exp}(\delta\boldsymbol\phi),
\qquad \mathrm{Exp}(\boldsymbol\phi) = I + \frac{\sin\theta}{\theta}[\boldsymbol\phi]_\times + \frac{1-\cos\theta}{\theta^2}[\boldsymbol\phi]_\times^2,
$$

with $\theta = \|\boldsymbol\phi\|$ (Rodrigues' formula). The optimizer computes
increments $\delta\boldsymbol\phi$ in the minimal tangent space (3 DoF for rotation,
6 for pose), and the Jacobians are taken with respect to this local parameterization.
This keeps the covariance full-rank and the increment singularity-free — the
reason every serious estimator (GTSAM, Ceres `LocalParameterization` / `Manifold`)
treats $SE(3)$ natively rather than via Euler angles or raw quaternions.

---

## 5. Incremental smoothing — iSAM2 and the Bayes tree

Batch smoothing re-solves the whole graph each step — wasteful when one new
measurement changes only a few variables. **iSAM2** (Kaess et al.) makes smoothing
*incremental*.

The key data structure is the **Bayes tree**: a directed tree obtained by
eliminating the factor graph into a chordal Bayes net and clustering into cliques.
Adding a new factor only touches the path from the affected variables to the root,
so iSAM2:
1. Identifies the **affected cliques** of the Bayes tree.
2. Re-eliminates only those (partial re-factorization).
3. Relinearizes only variables whose estimate moved beyond a threshold
   (**fluid relinearization**).

```
        ┌────────────┐
        │  root clique│
        └─────┬──────┘
        ┌─────┴──────┐
   ┌────┴───┐   ┌────┴────┐
   │ clique │   │ clique  │  ← only the affected branch is
   └────────┘   └─────────┘     re-factorized on a new factor
```

The result is smoothing-quality estimates at filtering-like cost — the algorithm
behind real-time GTSAM-based VIO and SLAM. Conceptually, iSAM2 *is* the Kalman
filter generalized: a filter is the degenerate case where you eliminate in time
order and immediately marginalize every past variable, collapsing the Bayes tree
into a single chain.

---

## 6. Marginalization, fixed-lag smoothing, and sparsity

A full smoother grows without bound. To run forever on finite compute you must
**bound the graph**, and the standard tools are marginalization and fixed-lag
smoothing.

**Marginalization** removes old variables while preserving their information by
applying the **Schur complement** to the information matrix. Partition into
variables to keep ($k$) and marginalize ($m$):

$$
\Lambda = \begin{bmatrix} \Lambda_{kk} & \Lambda_{km} \\ \Lambda_{mk} & \Lambda_{mm} \end{bmatrix}
\;\Rightarrow\;
\Lambda_{kk}^{\text{marg}} = \Lambda_{kk} - \Lambda_{km}\Lambda_{mm}^{-1}\Lambda_{mk}.
$$

The catch — and the trap every VIO engineer hits — is that marginalization creates
a dense **prior factor** connecting all variables that were linked to the
marginalized one (**fill-in**). Marginalize carelessly and you destroy the very
sparsity that makes the solve fast, and you *fix the linearization point* of the
prior (causing inconsistency unless you use First-Estimates Jacobians).

**Fixed-lag smoothing** keeps a sliding window of the last $N$ keyframes and
marginalizes everything older — the standard structure of OKVIS and VINS-Mono.
It trades a small, bounded accuracy loss for constant-time operation.

---

## 7. Robust estimation — surviving outliers

Least squares assumes Gaussian noise. One gross outlier — a false loop closure, a
mismatched feature — has *unbounded* leverage because its squared residual
dominates the cost. Robust estimation bounds that leverage.

### 7.1 M-estimators and robust kernels

Replace the quadratic cost $\rho(r)=\tfrac12 r^2$ with a function that grows
sub-quadratically for large residuals:

| Kernel | $\rho(r)$ | Behavior |
|---|---|---|
| L2 (squared) | $\tfrac12 r^2$ | no robustness |
| Huber | quadratic for $\|r\|\le\delta$, linear beyond | mild, convex |
| Cauchy | $\tfrac{c^2}{2}\log(1 + (r/c)^2)$ | strong, redescending |
| Geman–McClure | $\tfrac{r^2/2}{1 + r^2}$ | very strong, bounded |

These are implemented as **iteratively reweighted least squares (IRLS)**: each
iteration reweights the residual by $w(r) = \rho'(r)/r$, so an outlier's weight
shrinks toward zero. Ceres and GTSAM expose these as `LossFunction` /
`noiseModel::Robust`.

### 7.2 Graduated non-convexity

A redescending kernel makes the problem **non-convex** — gradient descent can get
stuck. **Graduated Non-Convexity (GNC)** (Yang, Carlone et al.) starts from a
convex surrogate and gradually anneals a control parameter $\mu$ until the cost
recovers the true robust kernel:

$$
\min_{\mathbf{X}} \sum_i \rho_\mu(r_i), \qquad \mu: \text{convex} \to \text{robust as iterations proceed}.
$$

GNC delivers near-global robustness with no initial guess and tolerates *extreme*
outlier rates (>70% in point-cloud registration). It is the modern answer to
"my optimizer keeps converging to the outlier."

### 7.3 The switchable-constraint view

As in [51-autonomy-slam-and-mapping.md](51-autonomy-slam-and-mapping.md) §5, an
alternative is to give each suspect factor a latent switch $s_{ij}\in[0,1]$ that
the optimizer can turn off, with a prior pulling it toward 1. This is robust
estimation expressed *inside* the factor graph rather than in the loss function —
equivalent in spirit, sometimes easier to tune.

---

## 8. Practice this week

1. Build a 2D pose-graph in GTSAM, solve with Gauss–Newton, then with iSAM2
   incrementally; confirm the estimates match and compare timing.
2. Implement on-manifold $SE(3)$ optimization with a $\boxplus$ retraction; verify
   the Jacobians numerically against finite differences.
3. Inject 30% outlier loop closures and watch L2 fail; add a Cauchy kernel, then
   GNC, and observe recovery.
4. Implement marginalization of an old keyframe via Schur complement and *visualize*
   the dense fill-in prior it creates.

---

## 9. Sources & further study

- **Dellaert & Kaess — *Factor Graphs for Robot Perception*** (Foundations & Trends).
  The definitive, readable treatment; pairs with the GTSAM library.
- **Kaess et al. — "iSAM2: Incremental Smoothing and Mapping Using the Bayes Tree"**
  (IJRR, 2012).
- **Barfoot — *State Estimation for Robotics*.** On-manifold least squares, $SE(3)$
  Jacobians, batch estimation — the rigorous backbone.
- **Triggs et al. — "Bundle Adjustment — A Modern Synthesis."** Schur complement,
  sparsity, robust cost.
- **Yang, Antonante, Tzoumas & Carlone — "Graduated Non-Convexity for Robust Spatial
  Perception"** (RA-L, 2020).
- **Agarwal, Mierle et al. — *Ceres Solver* documentation.** The practical NLLS
  toolkit and its loss functions.
- **Sünderhauf & Protzel — "Switchable Constraints for Robust Pose Graph SLAM"** (IROS 2012).

> Framing note: Once you see estimation as MAP inference on a sparse factor graph,
> the artificial walls between SLAM, fusion, calibration, and tracking dissolve —
> they are one optimization with different residuals. The engineers who build the
> most capable autonomy stacks are the ones who think in factors and Jacobians, who
> marginalize deliberately, and who never let a single outlier hold the whole
> estimate hostage.
