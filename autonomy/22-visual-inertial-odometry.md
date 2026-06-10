# Visual-Inertial Odometry — Tightly-Coupled Camera + IMU Estimation

> **Why this exists.** A camera sees rich structure but is blind to scale, drifts under fast motion, and goes dark in low light or blur. An IMU measures acceleration and angular rate at hundreds of hertz, is immune to lighting, and resolves fast motion — but integrates its own noise into unbounded drift within seconds. Each sensor's weakness is the other's strength, and fusing them *tightly* yields metric, low-drift, high-rate pose estimation from hardware that weighs grams and costs dollars. This is the estimation engine inside every modern drone, AR headset, and increasingly every robot that can't rely on GPS. Visual-Inertial Odometry (VIO) is where probabilistic estimation, multi-view geometry, and real-time optimization fuse into one of the most elegant and demanding pieces of software in all of robotics.
>
> **What mastering it makes you.** The engineer who can deliver centimeter-accurate, 200 Hz pose on a GPS-denied platform with a $10 camera and a $3 IMU — and who understands every term in the cost function well enough to debug it when it diverges over a featureless wall.

VIO is the synthesis of camera geometry from [20-autonomy-computer-vision.md](20-computer-vision.md) and the estimation theory of [14-autonomy-state-estimation-advanced.md](14-state-estimation-advanced.md) and [13-autonomy-sensor-fusion.md](13-sensor-fusion.md). It is the front-end of the SLAM systems in [12-autonomy-slam-and-mapping.md](12-slam-and-mapping.md), provides the navigation state for the GNC of [09-autonomy-gnc.md](09-gnc.md), and is the GPS-denied fallback that makes the resilience of [07-autonomy-gnss-jamming-spoofing.md](07-gnss-jamming-spoofing.md) real. The optimization math is nonlinear least squares from [03-foundations-mathematics.md](../foundations/03-mathematics.md); deployment onboard draws on [25-autonomy-edge-inference-deployment.md](25-edge-inference-deployment.md) and the PX4/SITL toolchain of [03-autonomy-px4-sitl.md](03-px4-sitl.md).

---

## 1. The State We Estimate

VIO estimates the **navigation state** of the body over time. At time $k$ the state is

$$\mathbf{x}_k = \big[\; \mathbf{p}_k \in \mathbb{R}^3,\;\; \mathbf{v}_k \in \mathbb{R}^3,\;\; \mathbf{q}_k \in SO(3),\;\; \mathbf{b}_a,\;\; \mathbf{b}_g \;\big]$$

position, velocity, orientation (a unit quaternion / rotation on the manifold $SO(3)$), plus the slowly-drifting **accelerometer bias** $\mathbf{b}_a$ and **gyroscope bias** $\mathbf{b}_g$. Estimating the biases is non-negotiable — an unmodeled gyro bias of $0.5°/s$ corrupts orientation, which corrupts the gravity-compensated acceleration, which corrupts position quadratically.

Orientation lives on a manifold, not a vector space, so updates use the Lie-algebra / error-state formulation: a small rotation perturbation $\delta\boldsymbol{\theta}$ maps to the manifold via the exponential map $\mathbf{q} \leftarrow \mathbf{q} \otimes \exp(\tfrac12 \delta\boldsymbol{\theta})$. Getting this manifold algebra right is half of VIO correctness.

---

## 2. The IMU Model

An IMU reports specific force $\tilde{\mathbf{a}}$ and angular rate $\tilde{\boldsymbol{\omega}}$, each corrupted by bias and white noise:

$$\tilde{\mathbf{a}} = \mathbf{a} + \mathbf{b}_a + \mathbf{n}_a, \qquad \tilde{\boldsymbol{\omega}} = \boldsymbol{\omega} + \mathbf{b}_g + \mathbf{n}_g$$

with biases themselves random walks $\dot{\mathbf{b}} = \mathbf{n}_{bw}$. Continuous-time kinematics (in world frame, $R$ from body to world, $\mathbf{g}$ gravity):

$$\dot{\mathbf{p}} = \mathbf{v}, \qquad \dot{\mathbf{v}} = R(\tilde{\mathbf{a}} - \mathbf{b}_a - \mathbf{n}_a) + \mathbf{g}, \qquad \dot{R} = R\,[\tilde{\boldsymbol{\omega}} - \mathbf{b}_g - \mathbf{n}_g]_\times$$

Naively integrating these between camera frames is correct but *re-integration is expensive* — every time the optimizer changes the bias estimate, you'd re-integrate hundreds of IMU samples. **Preintegration** (Sec. 4) is the trick that makes this tractable.

---

## 3. Tightly vs. Loosely Coupled

This is the defining architectural choice in VIO.

| | Loosely coupled | Tightly coupled |
|---|---|---|
| What's fused | Independent VO pose + IMU pose | Raw features + raw IMU in one estimator |
| Information | Lossy (VO collapses features to a pose first) | Full (every feature constrains the state) |
| Robustness | Worse — VO failure poisons the filter | Better — IMU bridges feature dropout |
| Complexity | Lower | Higher |
| Scale observability | Often poor | Recovered from IMU+vision jointly |

```
  LOOSELY COUPLED                 TIGHTLY COUPLED
  ┌──────┐  pose   ┌─────┐        ┌──────────────────────────┐
  │  VO  │────────►│fuse │        │ joint estimator:          │
  └──────┘         │ KF  │        │  reprojection residuals   │
  ┌──────┐  pose   │     │        │  + IMU preintegration     │
  │ IMU  │────────►│     │        │  + bias random walk       │
  └──────┘         └─────┘        │  over a sliding window    │
   (information lost at arrows)    └──────────────────────────┘
```

Modern high-performance systems (**VINS-Mono/Fusion**, **OKVIS**, **ORB-SLAM3**'s VI mode, **OpenVINS**) are all tightly coupled, because throwing away the per-feature information before fusion measurably hurts accuracy and robustness. Loosely coupled is reserved for quick integrations or when the VO black box can't be opened.

---

## 4. IMU Preintegration — The Key Idea

Forster et al.'s **on-manifold preintegration** (2015) is the breakthrough that made tightly-coupled optimization real-time. The insight: summarize all IMU measurements between two keyframes $i$ and $j$ into *relative* motion increments $\Delta \mathbf{R}_{ij}, \Delta \mathbf{v}_{ij}, \Delta \mathbf{p}_{ij}$ that are expressed in the body frame at $i$ and are therefore **independent of the absolute state** at $i$:

$$
\Delta R_{ij} = \prod_{k=i}^{j-1} \exp\big((\tilde{\boldsymbol{\omega}}_k - \mathbf{b}_g)\Delta t\big), \quad
\Delta \mathbf{v}_{ij} = \sum \Delta R_{ik}(\tilde{\mathbf{a}}_k - \mathbf{b}_a)\Delta t, \quad
\Delta \mathbf{p}_{ij} = \sum \big[\Delta\mathbf{v}\,\Delta t + \tfrac12 \Delta R_{ik}(\tilde{\mathbf{a}}_k-\mathbf{b}_a)\Delta t^2\big]
$$

Because the preintegrated terms don't depend on the global pose, they need re-integration only when the *bias* changes — and even then a first-order Jacobian correction $\Delta R_{ij}(\mathbf{b}_g) \approx \Delta\bar R_{ij}\exp(J^R_{b_g}\,\delta\mathbf{b}_g)$ avoids full recomputation. The preintegration also propagates a covariance, giving the **information weight** of the IMU factor. This single idea is what lets a sliding-window optimizer touch hundreds of IMU samples without choking.

The resulting **IMU factor** penalizes the mismatch between the predicted and estimated relative motion:
$$\mathbf{r}_{IMU} = \big[\; \log(\Delta R_{ij}^\top R_i^\top R_j),\;\; R_i^\top(\mathbf{v}_j - \mathbf{v}_i - \mathbf{g}\Delta t) - \Delta\mathbf{v}_{ij},\;\; \dots,\;\; \mathbf{b}_j - \mathbf{b}_i \;\big]$$

---

## 5. The Optimization — Sliding-Window Bundle Adjustment

VIO is a **factor graph**: states are nodes; IMU preintegration factors connect consecutive states; visual reprojection factors connect states to observed landmarks. We find the maximum-a-posteriori estimate by minimizing the sum of squared, information-weighted residuals:

$$
\min_{\mathcal{X}} \; \underbrace{\sum_{(i,j)} \| \mathbf{r}_{IMU}(i,j) \|^2_{\Sigma_{IMU}}}_{\text{inertial}} \;+\; \underbrace{\sum_{(i,l)} \rho\!\Big( \| \mathbf{r}_{repr}(i,l) \|^2_{\Sigma_{C}} \Big)}_{\text{visual}} \;+\; \underbrace{\| \mathbf{r}_{prior} \|^2}_{\text{marginalization}}
$$

The **visual reprojection residual** for landmark $l$ seen in frame $i$ is the familiar
$$\mathbf{r}_{repr} = \mathbf{z}_{il} - \pi\big(K,\, R_i^\top(\mathbf{X}_l - \mathbf{p}_i)\big)$$
with $\pi$ the camera projection and $\rho$ a robust Huber kernel to tame mismatched features. The norms $\|\cdot\|_\Sigma$ are Mahalanobis — each factor is weighted by its inverse covariance, so the IMU and camera contribute in proportion to their confidence. This is solved by **Gauss-Newton / Levenberg-Marquardt** (Ceres, GTSAM, g2o), exploiting the sparse block structure with the Schur complement to eliminate landmarks efficiently.

```
   FACTOR GRAPH (sliding window of 4 keyframes)

   [x_i]──IMU──[x_{i+1}]──IMU──[x_{i+2}]──IMU──[x_{i+3}]
     │  ╲          │  ╲           │  ╱           │
   repr  repr    repr  repr     repr           repr
     │     ╲       │     ╲        │   ╱          │
   (L1)    (L2)  (L3)   (L4)    (L5)          (L6)   ← landmarks
     └─ prior (from marginalizing older states) ─┘
```

To stay real-time, the window is bounded: old keyframes and landmarks are **marginalized** out via the Schur complement, leaving a dense **prior factor** that preserves their information without keeping their variables. Marginalization order and consistency (FEJ — First-Estimate Jacobians) are subtle; done wrong they inject spurious information and cause the estimator to become overconfident and inconsistent.

**Filter alternative — MSCKF.** The Multi-State Constraint Kalman Filter (Mourikis & Roumeliotis 2007, the basis of **OpenVINS** and Apple/Google AR) keeps a sliding window of *poses* in an EKF and applies a clever null-space projection so landmarks never enter the state vector. It's lighter than full optimization, trading a little accuracy for lower, more predictable compute — often the right call on constrained hardware (chapter 64).

| Approach | Examples | Pro | Con |
|---|---|---|---|
| Sliding-window optimization | VINS-Mono, OKVIS, ORB-SLAM3-VI | Most accurate, relinearizes | Heavier, latency varies |
| Filter (MSCKF) | OpenVINS, MSCKF | Light, constant-time, deterministic | Single linearization, less accurate |

---

## 6. Initialization — The Hard Cold Start

VIO's dirtiest secret is that *starting* it is harder than running it. From a standstill the system must bootstrap: monocular scale, gravity direction, initial velocity, and gyro/accel biases are all unknown and partially unobservable until the platform *moves with sufficient excitation*.

The standard recipe (VINS-Mono style):
1. Run pure monocular SfM over the first few frames to get up-to-scale structure and relative poses.
2. **Visual-inertial alignment:** solve a linear system relating the scale-free vision and the metric IMU preintegration to recover the metric **scale** $s$, **gravity vector** $\mathbf{g}$, per-frame **velocities**, and **gyro bias**.
3. Refine $\mathbf{g}$ on its $\|\mathbf{g}\|=9.81$ manifold; switch to full tightly-coupled optimization.

**Observability** is the deep concept here: metric scale is observable only under *non-constant acceleration* (you must actually accelerate, not just translate at constant velocity), and the global yaw and absolute position are unobservable (VIO is odometry, not global localization). Constant-velocity or pure-rotation startup gives a degenerate, unobservable problem — the estimator will produce a confident, wrong scale. Knowing which states are observable under which motions is what lets you design a startup wiggle that excites them.

---

## 7. Failure Modes & Robustification

Real VIO lives or dies on handling degeneracy:

- **Feature starvation** (textureless wall, white-out): vision goes silent; IMU dead-reckons and drifts — bridge briefly, flag uncertainty growth, recover on feature return.
- **Aggressive motion / blur:** rolling-shutter distortion and blur poison features; model the rolling shutter, lean harder on IMU.
- **Dynamic objects:** moving people/cars violate the static-world assumption; reject with RANSAC, robust kernels, or semantic masking (chapter 59).
- **IMU saturation / clipping:** high-g maneuvers exceed sensor range; detect and down-weight.
- **Time offset / extrinsic error:** camera–IMU temporal misalignment and extrinsic calibration error are leading accuracy killers — modern systems estimate the time offset $t_d$ and extrinsics *online* as part of the state.

The covariance is your honesty signal: a well-tuned VIO *reports growing uncertainty* during degeneracy rather than silently drifting with false confidence. Downstream planners must consume that covariance, not just the mean pose.

---

## 8. Testing VIO

> Per the house testing discipline, VIO testing is risk prevention against the silent, confident drift that crashes a GPS-denied drone — boundary motions and degeneracies are the entire point.

| Level | Target | Method |
|---|---|---|
| **Unit** | Preintegration math, manifold ops, Jacobians | Synthetic IMU with analytic ground truth; finite-difference Jacobian checks |
| **Estimator** | Consistency (NEES), covariance honesty | Monte-Carlo with known truth; chi-square consistency tests |
| **Initialization** | Scale/gravity/bias recovery under excitation | Replay startup sequences with/without excitation |
| **Trajectory** | ATE / RPE drift on benchmarks | EuRoC, TUM-VI, replay; compare to ground truth |
| **Degeneracy** | Behavior under feature loss, pure rotation, constant velocity | Inject blackout/rotation; assert uncertainty grows, no false confidence |
| **Calibration** | Sensitivity to extrinsic/time-offset error | Perturb $t_d$, extrinsics; measure drift |
| **Exploratory** | Find divergence triggers | Aggressive-motion fuzzing, adversarial scenes |

**Boundary cases to force:** stationary start (unobservable scale — does it wait for excitation or invent a scale?), pure rotation (no translation parallax), constant-velocity cruise (scale drifts), total visual blackout for $N$ seconds, and a sudden IMU bias jump. The acceptance criterion is **consistency**: NEES within the chi-square bound and the reported covariance bracketing the true error — accuracy is secondary to not lying.

```python
def test_uncertainty_grows_during_blackout():
    # Risk: a featureless tunnel silently drifts while VIO claims high confidence.
    vio = VIOEstimator(config="euroc")
    vio.replay(frames=normal_sequence(2.0))      # warm up with good features
    cov_before = vio.position_covariance_trace()
    vio.replay(frames=black_frames(seconds=3.0)) # camera blackout, IMU only
    cov_after = vio.position_covariance_trace()
    # Acceptance: covariance must inflate, honestly reflecting dead-reckoning.
    assert cov_after > 5.0 * cov_before
    # And recovery must reconverge once features return.
    vio.replay(frames=normal_sequence(2.0))
    assert vio.position_covariance_trace() < 2.0 * cov_before
```

---

## 9. The Practical Stack

- **VINS-Mono / VINS-Fusion** (HKUST) — the canonical open tightly-coupled optimization VIO; mono, stereo, GPS-fusable.
- **OpenVINS** (UD) — clean MSCKF filter implementation, excellent for learning and embedded use.
- **OKVIS / OKVIS2** — keyframe-based VI optimization.
- **ORB-SLAM3** — VI mode with loop closure and multi-map; full SLAM, not just odometry.
- **GTSAM (with iSAM2) / Ceres / g2o** — the optimization back-ends; GTSAM's `ImuFactor`/`CombinedImuFactor` implement Forster preintegration.
- **Kalibr** — camera–IMU extrinsic and time-offset calibration (a prerequisite, not optional).
- **EuRoC MAV, TUM-VI, KITTI** — benchmark datasets with ground truth.
- Deploys onboard via the techniques of [25-autonomy-edge-inference-deployment.md](25-edge-inference-deployment.md), feeding pose to PX4/ROS 2.

---

## Sources & further study

- **Forster, Carlone, Dellaert & Scaramuzza (2017), "On-Manifold Preintegration for Real-Time Visual–Inertial Odometry,"** *IEEE T-RO*. The preintegration paper — read it line by line.
- **Mourikis & Roumeliotis (2007), "A Multi-State Constraint Kalman Filter for Vision-Aided Inertial Navigation" (MSCKF).**
- **Qin, Li & Shen (2018), "VINS-Mono: A Robust and Versatile Monocular Visual-Inertial State Estimator,"** *IEEE T-RO*.
- **Leutenegger et al. (2015), "Keyframe-based visual–inertial odometry using nonlinear optimization" (OKVIS).**
- **Geneva et al. (2020), "OpenVINS: A Research Platform for Visual-Inertial Estimation,"** ICRA.
- **Campos et al. (2021), "ORB-SLAM3,"** *IEEE T-RO*.
- **Sola (2017), "Quaternion kinematics for the error-state Kalman filter"** — the manifold/error-state reference.
- **Barfoot — *State Estimation for Robotics*.** The rigorous textbook for the underlying math.
- **Scaramuzza & Fraundorfer, "Visual Odometry" tutorial (IEEE RAM, 2011/2012).**

> Framing note: VIO is the discipline where two humble, flawed sensors become greater than their sum through the patient algebra of manifolds, preintegration, and weighted least squares. Its hardest lesson is observability: the estimator can only know what the *motion* reveals to it. A master of VIO doesn't just tune covariances — they design the platform's motion to excite the states they need, and they trust the reported uncertainty as much as the estimate itself, because in GPS-denied flight, a confident wrong answer is the one that kills.

---

## ⚡ The Insider Layer — What the Field Knows but Rarely Writes Down

The published VIO systems converge beautifully in the paper's figures. Getting your own to converge on your own hardware is a different sport, and almost all of the difficulty is concentrated in three places the papers gloss over: initialization, time sync, and convention discipline.

### Initialization is where VIO actually dies

Monocular VIO has to bootstrap metric scale, gravity direction, initial velocity, and biases from nothing but early motion — and that recovery is **only possible if the motion excites it.** Start the vehicle static, or lift off in pure hover, and scale is mathematically unobservable; the estimator will report a confident answer that is silently wrong by a constant factor. The unwritten rule among drone teams is to *induce* excitation at startup — a deliberate wiggle, a translating takeoff, anything with acceleration in more than one axis — because constant-velocity flight and steady hover are the enemy of observability. Pure rotation with no translation gives you zero parallax and therefore zero depth. If your VIO "drifts after takeoff," the bug is usually not the back-end; it's that you never excited scale and the front-end has been guessing since frame one.

### Time offset and rolling shutter are silent accuracy assassins

The camera and IMU clocks are never truly aligned, and an unmodeled temporal offset $t_d$ of even a few milliseconds smears every reprojection residual — the single most common cause of "it works at slow speed and falls apart when I fly fast." Good systems (VINS-Mono) estimate $t_d$ online; if yours doesn't, you must calibrate it and hold it. **Rolling shutter is poison**: each image row is exposed at a different instant, so a fast yaw shears the image, and unless you model the line delay (or, far better, buy a global-shutter sensor) your features are geometrically inconsistent. Spend the extra dollars on global shutter; it is the cheapest accuracy you will ever buy.

### The noise parameters you set are not the datasheet numbers

Engineers copy the IMU's Allan-variance noise densities straight from the datasheet and wonder why the filter is overconfident. In practice the continuous-time noise you feed the estimator is often **5–10× the datasheet value**, because those covariances must also absorb everything you *didn't* model — scale-factor error, axis misalignment, g-sensitivity, vibration, unmodeled latency. The covariances are tuning knobs that represent "my ignorance," not just thermal noise. Do a real Allan-variance characterization of *your* unit to get the right order of magnitude, then inflate to cover the unmodeled residual.

### Observability, FEJ, and the consistency trap

VIO has exactly four unobservable degrees of freedom — global position (3) and yaw (1) — while roll and pitch are pinned by gravity. The subtle killer is that a naive sliding-window estimator can **gain spurious information about the unobservable yaw** because Jacobians get evaluated at inconsistent linearization points across the window, making the filter overconfident and inconsistent (its reported covariance shrinks below the true error). The fix the field actually uses is **First-Estimates Jacobians (FEJ)** or observability-constrained updates — evaluate the Jacobians for a given state at a single fixed estimate. If you don't know why your filter "looks great until it suddenly diverges," inconsistency from this mechanism is the prime suspect. Run NEES/NIS consistency checks on a dataset with ground truth before you trust a single covariance.

### Convention wars cost more time than algorithms

The deepest VIO bugs are not in the math — they are sign and frame-convention mismatches. Body-to-world vs. world-to-body rotations, **JPL vs. Hamilton quaternion conventions** (which differ in the sign of the imaginary part and the order of multiplication), active vs. passive rotations, gravity as $+9.81$ or $-9.81$ — mix any two and you get an estimator that *almost* works, drifting in a way that looks like a tuning problem but never tunes out. Pick one convention, write it at the top of every file, and audit every library you import against it (OpenVINS is JPL; many others are Hamilton).

### Front-end pragmatics and honest benchmarking

Most production VIO tracks features with cheap KLT optical flow, not descriptors — and it loses everything on textureless white walls, HDR scenes, and motion blur, so a feature health monitor that triggers IMU-only dead-reckoning is mandatory. Remember the categories: **VIO drifts unboundedly** (good systems hold ~0.1–1% of distance traveled); only adding loop closure makes it **VI-SLAM**. When you read results on EuRoC or TUM-VI, assume reported numbers are best-of-N runs on tuned parameters; evaluate your own with `evo` (APE/RPE) on *your* trajectories, because a system that wins on a handheld dataset can still fail on your aggressive quad.
