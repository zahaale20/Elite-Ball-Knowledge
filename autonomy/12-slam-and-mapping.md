# SLAM & Mapping — Building a Map While Finding Yourself

> **Why this exists.** A robot dropped into an unknown environment faces a
> chicken-and-egg problem: to know where it is, it needs a map; to build a map,
> it needs to know where it is. Simultaneous Localization and Mapping (SLAM) is
> the act of solving both at once from the same noisy measurements. It is the
> capability that lets a drone navigate a GPS-denied warehouse, a Mars rover
> traverse unmapped terrain, and a quadruped close a loop around a building and
> realize it has returned to its start. Without SLAM, "autonomy" in unknown
> environments is impossible — you are reduced to dead reckoning that drifts
> without bound.
>
> **What mastering it makes you.** The engineer who understands *why* the map
> "snaps" into place at a loop closure, who can read a covariance ellipse and say
> "that's the drift accumulating along the unobservable direction," and who can
> choose between a filter and a smoother for a given compute and latency budget.

SLAM consumes the detections and features produced in
[11-autonomy-perception-deep.md](11-perception-deep.md), is built on the
estimation theory of [09-autonomy-gnc.md](09-gnc.md), and reaches its
modern form through the factor-graph machinery developed fully in
[14-autonomy-state-estimation-advanced.md](14-state-estimation-advanced.md).
It fuses the multi-modal inputs covered in
[13-autonomy-sensor-fusion.md](13-sensor-fusion.md). The nonlinear
least-squares it rests on requires the calculus and linear algebra of
[03-foundations-mathematics.md](../foundations/03-mathematics.md), and you validate
it in simulation per [06-foundations-simulation-test-verification.md](../foundations/06-simulation-test-verification.md).

---

## Table of Contents

1. [The SLAM problem, formally](#1-the-slam-problem-formally)
2. [Front-end vs back-end architecture](#2-front-end-vs-back-end-architecture)
3. [The front-end — odometry and feature tracking](#3-the-front-end--odometry-and-feature-tracking)
4. [Pose graphs and the back-end](#4-pose-graphs-and-the-back-end)
5. [Loop closure — recognizing where you have been](#5-loop-closure--recognizing-where-you-have-been)
6. [Bundle adjustment and the full MAP](#6-bundle-adjustment-and-the-full-map)
7. [Map representations — occupancy grids, TSDFs, point clouds](#7-map-representations--occupancy-grids-tsdfs-point-clouds)
8. [Drift, observability, and consistency](#8-drift-observability-and-consistency)
9. [Practice this week](#9-practice-this-week)
10. [Sources & further study](#10-sources--further-study)
11. [The Insider Layer — what the field knows but rarely writes down](#-the-insider-layer--what-the-field-knows-but-rarely-writes-down)

---

## 1. The SLAM problem, formally

Let $\mathbf{x}_{1:T}$ be the robot's trajectory (poses), $\mathbf{m}$ the map
(landmarks or a grid), $\mathbf{u}_{1:T}$ the control/odometry inputs, and
$\mathbf{z}_{1:T}$ the observations. **Full SLAM** seeks the joint posterior over
the entire trajectory and the map:

$$
p(\mathbf{x}_{1:T}, \mathbf{m} \mid \mathbf{z}_{1:T}, \mathbf{u}_{1:T}).
$$

**Online SLAM** marginalizes out past poses and tracks only the current one:

$$
p(\mathbf{x}_t, \mathbf{m} \mid \mathbf{z}_{1:t}, \mathbf{u}_{1:t})
= \int\!\!\cdots\!\!\int p(\mathbf{x}_{1:t}, \mathbf{m} \mid \cdots)\, d\mathbf{x}_{1:t-1}.
$$

The historical split: filtering SLAM (EKF-SLAM, FastSLAM) solves online SLAM;
graph SLAM solves full SLAM as a batch optimization. The field decisively moved
to **graph SLAM** in the 2010s because sparsity makes the batch problem cheaper
than the filter's $O(N^2)$ covariance update over $N$ landmarks.

---

## 2. Front-end vs back-end architecture

Every modern SLAM system has two halves with a clean interface between them:

```
   sensors                FRONT-END                    BACK-END
 ┌─────────┐   raw    ┌──────────────────┐  constraints ┌────────────────┐
 │ cam/LiDAR├────────►│ feature extract  ├─────────────►│ factor graph   │
 │ IMU/wheel│         │ data association │   (edges)    │ optimization   │
 └─────────┘          │ short-term odom  │              │ (MAP / NLLS)   │
                      └──────────────────┘              └───────┬────────┘
                              ▲                                 │
                              │       loop-closure constraints  │
                              └─────────────────────────────────┘
                                       optimized poses → map
```

- **Front-end:** geometry and data association. Extracts features, matches them
  across frames, proposes loop closures, and emits *constraints* (relative-pose
  measurements with covariances). This is where association errors enter and
  where most SLAM failures originate.
- **Back-end:** estimation. Takes the constraint graph and finds the trajectory
  and map that best explain all constraints simultaneously. This is a nonlinear
  least-squares problem solved by GTSAM, g2o, or Ceres.

The discipline: keep all *recognition* in the front-end and all *optimization* in
the back-end. A single wrong loop closure injected into the back-end can corrupt
the entire map (§8).

---

## 3. The front-end — odometry and feature tracking

### 3.1 Visual odometry

Visual SLAM front-ends (ORB-SLAM3, SVO) track features frame-to-frame and recover
relative motion. The geometric backbone is the **epipolar constraint**: matched
normalized points $\mathbf{x}, \mathbf{x}'$ in two views satisfy

$$
\mathbf{x}'^\top E\, \mathbf{x} = 0, \qquad E = [\mathbf{t}]_\times R,
$$

where $E$ is the essential matrix encoding the relative rotation $R$ and
translation direction $\mathbf{t}$. Decompose $E$ (four-fold ambiguity, resolved
by cheirality) and triangulate to get 3D points. Robustify with **RANSAC** to
reject the inevitable mismatches.

### 3.2 LiDAR odometry — ICP and its descendants

LiDAR front-ends register consecutive scans by **Iterative Closest Point (ICP)**.
Given source points $\{\mathbf{p}_i\}$ and target $\{\mathbf{q}_i\}$, point-to-plane
ICP minimizes

$$
\min_{R, \mathbf{t}} \sum_i \Big( \big(R\mathbf{p}_i + \mathbf{t} - \mathbf{q}_i\big) \cdot \mathbf{n}_i \Big)^2,
$$

where $\mathbf{n}_i$ is the surface normal at the matched target point.
Point-to-plane converges far faster than point-to-point because it slides points
along surfaces rather than pinning them. The loop:

```python
def icp(src, tgt, T_init, iters=30):
    T = T_init
    for _ in range(iters):
        corr = nearest_neighbors(T.transform(src), tgt)   # data association
        T = solve_point_to_plane(src, tgt, corr)          # minimize residual
        if converged(T): break
    return T
```

State-of-the-art systems (**FAST-LIO2**, **LIO-SAM**, **LeGO-LOAM**) tightly fuse
LiDAR with IMU so the IMU provides the motion prior that initializes ICP and
de-skews the scan during the sweep.

---

## 4. Pose graphs and the back-end

Strip the landmarks away and you get **pose-graph SLAM**: nodes are robot poses
$\mathbf{x}_i \in SE(3)$, edges are relative-pose constraints $\mathbf{z}_{ij}$
with information matrix $\Omega_{ij}$. The MAP estimate minimizes the sum of
squared, information-weighted residuals:

$$
\mathbf{x}^* = \arg\min_{\mathbf{x}} \sum_{(i,j)\in\mathcal{E}}
\mathbf{e}_{ij}(\mathbf{x}_i, \mathbf{x}_j)^\top \,\Omega_{ij}\, \mathbf{e}_{ij}(\mathbf{x}_i, \mathbf{x}_j),
$$

$$
\mathbf{e}_{ij} = \log\!\Big( \mathbf{z}_{ij}^{-1} \, (\mathbf{x}_i^{-1}\mathbf{x}_j) \Big)^\vee \in \mathbb{R}^6,
$$

where $\log(\cdot)^\vee$ is the $SE(3)$ logarithm mapping the pose error to a
6-vector (translation + axis-angle). This is **nonlinear** because of the rotation
manifold, so we linearize and iterate with **Gauss–Newton** or
**Levenberg–Marquardt**:

$$
\big(J^\top \Omega J\big)\, \delta\mathbf{x} = -J^\top \Omega\, \mathbf{e},
\qquad \mathbf{x} \leftarrow \mathbf{x} \boxplus \delta\mathbf{x}.
$$

The key engineering fact: the **information matrix $H = J^\top \Omega J$ is sparse**
— each edge touches only two poses — so a sparse Cholesky factorization solves it
in near-linear time for typical trajectories. This sparsity is the entire reason
graph SLAM scales where EKF-SLAM does not.

---

## 5. Loop closure — recognizing where you have been

Odometry drifts; loop closure is the only thing that *removes* accumulated error
rather than merely slowing it. The front-end must recognize a previously visited
place from current sensor data.

### 5.1 Appearance-based recognition

The dominant method is **Bag of Visual Words** (DBoW2): quantize image features
into a vocabulary, represent each image as a histogram, and compare with a
TF-IDF-weighted score. A geometric verification step (RANSAC on the putative
match) rejects perceptual aliasing — two corridors that *look* identical but are
not the same place.

### 5.2 Why one bad loop closure is catastrophic

A false loop closure adds an edge insisting two distant poses are coincident. The
optimizer, trusting it, folds the map to satisfy it and **corrupts everything**.
The defense is robust back-end optimization — **switchable constraints** or
**Dynamic Covariance Scaling**, which augment each loop edge with a latent
scaling variable $s_{ij}\in[0,1]$ that the optimizer can drive toward zero to
"switch off" an inconsistent constraint:

$$
\min_{\mathbf{x}, \{s_{ij}\}} \sum_{\text{odom}} \|\mathbf{e}\|^2_\Omega
+ \sum_{\text{loop}} \Big( s_{ij}^2\,\|\mathbf{e}_{ij}\|^2_\Omega + \Phi(1 - s_{ij})^2 \Big).
$$

This is the difference between a SLAM system that survives a single recognition
error and one that explodes the first time DBoW2 is fooled.

---

## 6. Bundle adjustment and the full MAP

When the map is a set of 3D landmarks $\mathbf{l}_k$ observed by camera poses
$\mathbf{x}_i$, the gold-standard estimate is **bundle adjustment** — jointly
optimize all poses and all landmarks to minimize total reprojection error:

$$
\{\mathbf{x}^*, \mathbf{l}^*\} = \arg\min \sum_{i,k} \rho\Big( \big\| \mathbf{z}_{ik} - \pi(\mathbf{x}_i, \mathbf{l}_k) \big\|^2_{\Sigma_{ik}} \Big),
$$

where $\pi$ is the projection (§2 of [11](11-perception-deep.md)) and
$\rho$ is a robust kernel (Huber/Cauchy) that down-weights outliers. The Hessian
has a characteristic **arrowhead/block structure** (cameras × landmarks), and the
**Schur complement** exploits it: marginalize the many landmarks to solve the
small camera system first, then back-substitute. This trick — implemented in
**Ceres Solver** and **GTSAM** — is what makes BA over thousands of landmarks
real-time.

$$
\underbrace{\big( H_{cc} - H_{cl} H_{ll}^{-1} H_{lc} \big)}_{\text{reduced camera system}}\,\delta\mathbf{x}_c = -\,\big( \mathbf{g}_c - H_{cl}H_{ll}^{-1}\mathbf{g}_l \big).
$$

---

## 7. Map representations — occupancy grids, TSDFs, point clouds

The "M" in SLAM takes different forms depending on what the planner needs.

| Representation | Stores | Query | Used by |
|---|---|---|---|
| **Occupancy grid** | $p(\text{occupied})$ per cell | collision check | 2D nav, gmapping |
| **OctoMap** | hierarchical 3D occupancy | 3D collision | aerial / 3D nav |
| **TSDF** | signed distance to surface | dense reconstruction | KinectFusion, Voxblox |
| **Point cloud** | raw 3D points | registration | LiDAR SLAM |
| **Landmark map** | sparse 3D features | localization | ORB-SLAM |

The **occupancy grid** uses a log-odds update so the recursion is additive:

$$
\ell_t(c) = \ell_{t-1}(c) + \log\frac{p(z_t \mid \text{occ})}{p(z_t \mid \text{free})} - \ell_0,
\qquad p(\text{occ}) = 1 - \frac{1}{1 + e^{\ell_t}}.
$$

Log-odds is chosen precisely because Bayesian fusion of many measurements becomes
a running sum, immune to numerical underflow near $p=0$ or $p=1$.

The **TSDF** stores, per voxel, the truncated signed distance $d$ to the nearest
surface and a weight $w$; new measurements fuse by a weighted average

$$
D \leftarrow \frac{wD + w' d'}{w + w'}, \qquad W \leftarrow w + w',
$$

and the surface is the zero-crossing $D=0$, extracted by marching cubes. This is
how dense reconstruction (Voxblox, KinectFusion) builds watertight surfaces from
noisy depth.

---

## 8. Drift, observability, and consistency

### 8.1 Why SLAM drifts

Odometry errors are *correlated over time*: each pose is computed relative to the
last, so errors integrate. Translation drift grows roughly linearly with distance;
heading drift causes *position* error to grow super-linearly because a small
angular error rotates the entire subsequent trajectory.

### 8.2 Observability and gauge freedom

A SLAM problem has an unobservable **gauge**: the absolute position and yaw of the
whole map are undetermined by relative measurements alone (you can translate and
rotate the entire solution freely). The Fisher information matrix is therefore
**rank-deficient** by the gauge dimension (4 for visual-inertial: 3 position + yaw;
roll and pitch are observable via gravity). Naïve EKF-SLAM that ignores this
*injects spurious information* into unobservable directions and becomes
inconsistent — the famous EKF-SLAM over-confidence. The fix is
**observability-constrained** estimation (OC-EKF) or, better, a batch smoother that
fixes the gauge explicitly by anchoring the first pose.

### 8.3 The consistency test

Same NIS/NEES logic as [11](11-perception-deep.md): compute the
Normalized Estimation Error Squared against ground truth in simulation,

$$
\text{NEES}_t = (\mathbf{x}_t - \hat{\mathbf{x}}_t)^\top P_t^{-1} (\mathbf{x}_t - \hat{\mathbf{x}}_t) \sim \chi^2_{n},
$$

and confirm it sits inside the chi-square bounds. A SLAM system whose NEES grows
above the bound is over-confident and will reject correct loop closures.

---

## 9. Practice this week

1. Run ORB-SLAM3 on the EuRoC MAV dataset; visualize the map before and after a
   loop closure and *watch* the trajectory snap.
2. Implement 2D pose-graph optimization with g2o or GTSAM on the
   Intel/Manhattan datasets; corrupt one loop edge and observe the map fold,
   then add a switchable constraint and watch it recover.
3. Implement point-to-plane ICP and register two LiDAR scans; plot convergence of
   the residual.
4. Build an occupancy grid from a simulated 2D LiDAR with the log-odds update.

---

## 10. Sources & further study

- **Thrun, Burgard & Fox — *Probabilistic Robotics*.** EKF-SLAM, FastSLAM,
  occupancy grids, the foundational treatment.
- **Barfoot — *State Estimation for Robotics*.** $SE(3)$ optimization, Lie-group
  Jacobians, batch estimation — the modern backbone of graph SLAM.
- **Cadena et al. — "Past, Present, and Future of SLAM: Toward the Robust-Perception
  Age"** (IEEE T-RO, 2016). The definitive survey.
- **Mur-Artal & Tardós — "ORB-SLAM2/3."** The reference visual SLAM system.
- **Xu et al. — "FAST-LIO2."** State-of-the-art tightly-coupled LiDAR-inertial odometry.
- **Triggs et al. — "Bundle Adjustment — A Modern Synthesis."** The BA reference.
- **Dellaert & Kaess — *Factor Graphs for Robot Perception*.** Bridges directly to
  [14-autonomy-state-estimation-advanced.md](14-state-estimation-advanced.md).

> Framing note: SLAM is not a black box you download. It is a front-end that must
> recognize honestly and a back-end that must optimize robustly, joined by a
> contract of constraints-with-covariances. The engineers who ship it are the ones
> who treat a loop closure as a *hypothesis* to be verified, never a fact to be
> trusted — because the back-end will believe whatever the front-end tells it.

---

## ⚡ The Insider Layer — What the Field Knows but Rarely Writes Down

SLAM papers report ATE on EuRoC and KITTI and call it a day. Shipping SLAM is a
different sport. Here is what the people who run it on real robots actually
worry about.

### One bad loop closure destroys everything — and it will happen

The back-end is a credulous optimizer: it minimizes the residuals you give it,
so a single false loop closure (perceptual aliasing — two different corridors
that look identical) folds the entire map, and there is no graceful degradation,
just a catastrophic snap. This is *the* reason robust kernels and switchable
constraints exist, but the deeper insider move is **geometric verification
before you ever add the edge**: a place-recognition hit (DBoW2/NetVLAD) is only a
candidate; you confirm it with a RANSAC geometric check and a minimum inlier
count, and you still add it with a switch variable so the optimizer can disown
it. Teams that trusted appearance-only loop closure have war stories about maps
that looked perfect in the lab and ate themselves in a repetitive warehouse.

### Drift is anisotropic, and the unobservable directions are where it lives

Monocular SLAM has an unobservable scale; VINS has four unobservable directions
(global position and yaw); a pure-LiDAR system degenerates in a long featureless
tunnel. The number nobody puts on the slide: error accumulates *along the
unobservable subspace* while staying tight elsewhere, which is why your
covariance ellipse is a cigar, not a sphere. The practical consequence — known
to every veteran, rarely written — is that **straight, feature-poor corridors
and symmetric environments are where SLAM quietly dies**, and the fix is
operational (mount a wider FOV, drive a less degenerate trajectory, add a
heterogeneous sensor) far more often than algorithmic.

### The front-end is 90% of the engineering and 10% of the publications

Academic glory is in the back-end (iSAM2, GTSAM, elegant manifolds). The actual
labor — feature track lifetime management, keyframe selection heuristics, IMU
initialization that doesn't diverge, handling the first few seconds before scale
is observable, dynamic-object rejection — is unglamorous front-end plumbing that
nobody writes a clean paper about. **ORB-SLAM's real contribution was not the
optimizer; it was a thousand robustness decisions in the tracking thread.** If
you are debugging a SLAM failure, it is in the front-end with overwhelming
probability.

### Dynamic scenes break the static-world assumption papers quietly assume

Classical SLAM assumes a rigid, static world. The real world has pedestrians,
cars, and your own robot's reflection. Features on moving objects produce
beautiful, confident, wrong constraints. The fielded fix is to run a detector or
optical-flow consistency check and **mask out dynamic regions before feeding the
front-end** — a step rarely shown in the canonical pipeline diagram but present
in every system that works in a city.

### Map representation is a deployment decision, not an academic one

- **Point clouds**: great for registration, useless for planning (no free-space
  notion).
- **Occupancy grids**: planner-friendly, memory-hungry in 3D.
- **TSDFs**: beautiful surfaces, expensive, drift-sensitive.

The insider truth: you almost always carry **two maps** — a sparse,
optimization-friendly map for localization and a dense, planner-friendly map for
obstacle avoidance — and keeping them consistent after a loop closure (which
moves the trajectory the dense map was built against) is a real and rarely
discussed engineering problem.

### Numbers and norms worth memorizing

- A modern VIO/LIO drifts on the order of **0.1–1% of distance traveled** with no
  loop closures; below that, suspect you are testing on a friendly dataset.
- **Run NEES/NIS consistency checks** — an over-confident SLAM estimate rejects
  the very loop closures that would save it.
- **Benchmarks lie about generalization.** A system tuned to KITTI's forward-
  driving, daylight, low-dynamics regime tells you nothing about a handheld
  device or a drone doing aggressive yaw. Always test on motion that resembles
  *your* platform.
- **"We have SLAM" means nothing.** Ask: with loop closure or just odometry?
  Online or batch? On the target compute or a workstation? With or without GPS
  priors? The honest answers separate demos from products.

The meta-lesson the field internalizes the hard way: SLAM is not a download, it
is a contract between an honest front-end and a robust back-end, tuned to a
specific platform and environment. Treat every loop closure as a suspect, every
unobservable direction as a leak, and every benchmark number as optimistic.
