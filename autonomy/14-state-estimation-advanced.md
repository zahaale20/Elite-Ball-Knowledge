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
the filters of [09-autonomy-gnc.md](09-gnc.md), the graph back-end of
[12-autonomy-slam-and-mapping.md](12-slam-and-mapping.md), and the
fusion of [13-autonomy-sensor-fusion.md](13-sensor-fusion.md) into a
single MAP-inference framework. The optimization rests on the calculus and linear
algebra of [03-foundations-mathematics.md](../foundations/03-mathematics.md), and its
robustness claims must be validated per
[06-foundations-simulation-test-verification.md](../foundations/06-simulation-test-verification.md).
The decision layer that consumes its estimates lives in
[10-autonomy-planning-decision.md](10-planning-decision.md).

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
10. [The Insider Layer — what the field knows but rarely writes down](#-the-insider-layer--what-the-field-knows-but-rarely-writes-down)

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

As in [12-autonomy-slam-and-mapping.md](12-slam-and-mapping.md) §5, an
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

---

## ⚡ The Insider Layer — What the Field Knows but Rarely Writes Down

Factor graphs are taught as a beautiful unification. They are. They are also a
loaded gun, and the people who ship them know exactly where the recoil is.

### Marginalization is where sparsity goes to die

The textbook says: drop old states to bound compute, marginalize them out, done.
The thing nobody writes in bold: **marginalizing a variable fills in dense
constraints among all its neighbors.** Marginalize an old keyframe that saw
twenty landmarks and you replace a sparse set of factors with a dense
twenty-way prior. Do it carelessly across a sliding window and your once-sparse
graph becomes a dense block that destroys the very speed you marginalized to
gain. This is the central tension of fixed-lag smoothing, and the practical
answers — selective marginalization, keeping only strong constraints, or just
dropping (not marginalizing) weak ones — are folklore passed between teams more
than they are written down. MSCKF's whole design is an answer to this problem.

### Linearization point is a decision, and the wrong one makes you inconsistent

The EKF's deepest sin — re-linearizing the *same* state at different points for
different constraints — quietly injects spurious information along unobservable
directions and makes the filter over-confident. This is the **observability-
constrained EKF / FEJ (First-Estimates Jacobian)** story: you must fix the
linearization point of certain states so the estimator's observable subspace
matches reality's. It is responsible for a large fraction of "my VIO yaw is
slowly biased and over-confident" bugs, and it is barely mentioned in
introductory treatments because the math is unpleasant. Factor-graph relinearize-
everything smoothers (iSAM2) sidestep much of this, which is half the reason they
won.

### Robust kernels are a confession that your front-end lies

A Huber or Cauchy loss is sold as elegant robust statistics. In practice it is an
admission that **your data association produces outliers and you cannot trust the
front-end.** The insider knowledge is in the *details*: a robust kernel with a
badly chosen scale either does nothing (threshold too high) or rejects good data
(too low), and it has to be **annealed** — start loose, tighten as the estimate
converges — or you get stuck in a local minimum where the kernel has down-
weighted the very inliers you needed. Switchable constraints (carry a continuous
0–1 switch per loop closure and let the optimizer turn it off) are often more
robust than M-estimators for catastrophic outliers like false loop closures,
because a single false constraint can fool a Huber loss but the switch can fully
disable it.

### Non-convexity: the optimizer believes your initial guess

Bundle adjustment and pose-graph optimization are **non-convex**. Gauss-Newton
and Levenberg-Marquardt find the nearest local minimum, not the global one, so
**initialization is the whole ballgame.** A monocular system started before scale
is observable, or a pose graph initialized with bad odometry, converges
confidently to garbage. The field's hard-won practice — incremental
initialization, good front-end odometry as the seed, dog-leg trust regions,
sometimes a convex relaxation (SE-Sync) to certify global optimality — exists
because "just run the optimizer" fails silently. The optimizer never tells you it
found a local minimum; you find out when the map is folded.

### Numbers, tools, and norms

- **iSAM2 is the workhorse** because it re-solves only the part of the Bayes tree
  that changed — smoothing accuracy at near-filtering cost. Know *why* it's
  incremental, not just that it is.
- **Ceres, GTSAM, g2o** are the three you will actually use. GTSAM thinks in
  factor graphs; Ceres is a general NLLS hammer; g2o is the classic SLAM
  back-end. Picking the wrong one for the problem wastes weeks.
- **Always run NEES.** A smoother that reports a 2 cm covariance while the true
  error is 20 cm is worse than useless — it will reject the corrections that
  would save it.
- **Analytic Jacobians beat autodiff for speed but are where the bugs live.** A
  sign error in an on-manifold Jacobian produces an estimator that *almost*
  works, which is the hardest kind to debug. Validate against numerical
  differentiation before you trust hand-derived ones.
- **Sparsity structure is the performance.** The difference between a 1 Hz and a
  100 Hz back-end is almost always the variable ordering and fill-in, not the
  linear solver. COLAMD ordering is not optional.

The meta-point the literature underplays: factor-graph estimation is powerful
precisely because it externalizes every assumption as a residual — and dangerous
for the same reason, because the optimizer will faithfully satisfy a wrong
residual. The engineers who build the best stacks think in factors and Jacobians,
marginalize deliberately, guard the linearization point, and treat every outlier
as a hostage-taker to be disarmed before it touches the solution.
