# Perception Deep Dive — From Photons to Object Tracks

> **Why this exists.** Every autonomous decision is downstream of a number that
> a sensor produced and a perception stack interpreted. A drone does not "see" a
> car; it integrates photons on a focal plane, debayers them, runs a detector
> that emits a noisy bounding box, associates that box with a hypothesis it has
> been maintaining for 0.4 seconds, and finally hands a *track* — position,
> velocity, covariance, identity — to the planner. If any link in that chain is
> miscalibrated, mis-associated, or over-confident, the autonomy commands an
> unbounded action on a fiction. This module is the chain, derived from the
> physics up.
>
> **What mastering it makes you.** The engineer who can look at a tracker that
> "loses the target during a crossing maneuver" and know instantly whether the
> failure is in the measurement model, the gating threshold, the association
> algorithm, or the motion model — and fix the right one.

This module is the front-end that feeds the estimators of
[09-autonomy-gnc.md](09-gnc.md) and the decision layer of
[10-autonomy-planning-decision.md](10-planning-decision.md). The
learning-based detectors it relies on are developed in
[01-autonomy-ml-ai.md](01-ml-ai.md); the probability and linear algebra
it assumes live in [03-foundations-mathematics.md](../foundations/03-mathematics.md).
Its output is consumed directly by [12-autonomy-slam-and-mapping.md](12-slam-and-mapping.md)
and fused with other modalities in [13-autonomy-sensor-fusion.md](13-sensor-fusion.md).
You cannot test what you cannot model, so pair it with
[06-foundations-simulation-test-verification.md](../foundations/06-simulation-test-verification.md).

---

## Table of Contents

1. [The perception pipeline as a chain of estimators](#1-the-perception-pipeline-as-a-chain-of-estimators)
2. [Sensor models — cameras, LiDAR, radar](#2-sensor-models--cameras-lidar-radar)
3. [Detection — turning pixels into measurements](#3-detection--turning-pixels-into-measurements)
4. [Single-target tracking — the recursive Bayes filter](#4-single-target-tracking--the-recursive-bayes-filter)
5. [Data association — the hard problem](#5-data-association--the-hard-problem)
6. [Multi-object tracking — JPDA, MHT, and modern alternatives](#6-multi-object-tracking--jpda-mht-and-modern-alternatives)
7. [Uncertainty, calibration, and failure modes](#7-uncertainty-calibration-and-failure-modes)
8. [Practice this week](#8-practice-this-week)
9. [Sources & further study](#9-sources--further-study)
10. [The Insider Layer — what the field knows but rarely writes down](#-the-insider-layer--what-the-field-knows-but-rarely-writes-down)

---

## 1. The perception pipeline as a chain of estimators

The cardinal mistake of newcomers is to treat perception as a single neural
network. It is a *pipeline*, and every stage is an estimator with its own error
model. Errors compound multiplicatively, not additively — a 95%-accurate
detector feeding a 95%-accurate associator into a 95%-reliable motion model
yields a track that is correct $0.95^3 \approx 86\%$ of the time.

```
photons → optics → focal plane → ISP/debayer → detector → measurement zₖ
                                                              │
                          ┌───────────────────────────────────┘
                          ▼
   track set {x̂ᵢ, Pᵢ} ◄── update ◄── association ◄── gating
                          │
                          └──► predict (motion model) ──► next frame
```

The contract between stages is a **measurement with a covariance**, never a point.
A detector that emits a bounding box without an uncertainty is lying by omission,
and every downstream filter will trust it absolutely.

---

## 2. Sensor models — cameras, LiDAR, radar

### 2.1 The pinhole camera and its calibration

A 3D point $\mathbf{X} = [X, Y, Z]^\top$ in the camera frame projects to pixel
$\mathbf{u} = [u, v]^\top$ via the intrinsic matrix $K$:

$$
\lambda \begin{bmatrix} u \\ v \\ 1 \end{bmatrix}
= K \begin{bmatrix} X \\ Y \\ Z \end{bmatrix},
\qquad
K = \begin{bmatrix} f_x & s & c_x \\ 0 & f_y & c_y \\ 0 & 0 & 1 \end{bmatrix}.
$$

Real lenses violate the pinhole model. Brown–Conrady radial-tangential distortion
warps the normalized coordinates $(x, y) = (X/Z, Y/Z)$ before applying $K$:

$$
\begin{aligned}
x_d &= x(1 + k_1 r^2 + k_2 r^4 + k_3 r^6) + 2p_1 x y + p_2(r^2 + 2x^2), \\
y_d &= y(1 + k_1 r^2 + k_2 r^4 + k_3 r^6) + p_1(r^2 + 2y^2) + 2p_2 x y,
\end{aligned}
\qquad r^2 = x^2 + y^2.
$$

You recover $K, k_i, p_i$ by minimizing reprojection error over a checkerboard
(Zhang's method, implemented in OpenCV `calibrateCamera`). The residual you
minimize is the same one bundle adjustment uses (see
[12-autonomy-slam-and-mapping.md](12-slam-and-mapping.md) §6):

$$
\min_{K, \mathbf{d}, \{R_j, t_j\}} \sum_j \sum_i
\big\| \mathbf{u}_{ij} - \pi(K, \mathbf{d}, R_j, t_j, \mathbf{X}_i) \big\|^2 .
$$

### 2.2 LiDAR — time-of-flight geometry and noise

A spinning or solid-state LiDAR returns range $r$, azimuth $\theta$, elevation
$\phi$. The Cartesian point is

$$
\mathbf{p} = \begin{bmatrix} r\cos\phi\cos\theta \\ r\cos\phi\sin\theta \\ r\sin\phi \end{bmatrix}.
$$

Range noise is roughly constant in $r$ (a few cm) but the *Cartesian* covariance
is anisotropic and grows with range because angular error $\sigma_\theta$ maps to
a lateral error $r\,\sigma_\theta$. Linearizing,

$$
\Sigma_{\mathbf p} = J \,\mathrm{diag}(\sigma_r^2, \sigma_\theta^2, \sigma_\phi^2)\, J^\top,
\qquad J = \frac{\partial \mathbf{p}}{\partial(r,\theta,\phi)}.
$$

This is why LiDAR point clouds are "smeary" far away — and why naïvely fitting
planes to distant returns produces biased normals.

### 2.3 Radar — the only sensor that measures velocity directly

Radar returns range, azimuth, and **range-rate** $\dot r$ via the Doppler shift
$f_d = 2 v_r / \lambda$. Range-rate is a measurement of the *radial* velocity
component only:

$$
\dot r = \frac{(\mathbf{v}_\text{target} - \mathbf{v}_\text{ego}) \cdot (\mathbf{p}_\text{target} - \mathbf{p}_\text{ego})}{\|\mathbf{p}_\text{target} - \mathbf{p}_\text{ego}\|}.
$$

Doppler is the reason automotive radar can disambiguate a moving pedestrian from
clutter in a single frame. Fuse it and your velocity converges an order of
magnitude faster (see [13-autonomy-sensor-fusion.md](13-sensor-fusion.md)).

| Sensor | Direct measurands | Strengths | Weaknesses |
|---|---|---|---|
| Camera | bearing (2 angles), appearance | cheap, dense, semantic | no range, light-dependent |
| LiDAR | range + 2 angles | accurate 3D geometry | no semantics, weather, cost |
| Radar | range + bearing + range-rate | velocity, all-weather | low angular resolution |

---

## 3. Detection — turning pixels into measurements

A modern detector (YOLO, DETR, CenterPoint for LiDAR) emits, per object, a
location, a class distribution, and a confidence. The output of a *raw* detector
is a dense set of overlapping candidates; **non-maximum suppression (NMS)**
collapses them:

```python
def nms(boxes, scores, iou_thresh=0.5):
    order = scores.argsort()[::-1]          # highest score first
    keep = []
    while order.size > 0:
        i = order[0]; keep.append(i)
        ious = iou(boxes[i], boxes[order[1:]])
        order = order[1:][ious < iou_thresh]  # drop overlapping boxes
    return keep
```

The detection score is **not** a calibrated probability — a softmax output of
0.9 does not mean the object is present 90% of the time. We return to calibration
in §7. For tracking, convert each surviving detection into a measurement
$\mathbf{z}_k$ with a measurement covariance $R_k$ derived from box geometry
(small boxes → high positional variance) and detector confidence.

The detection-to-measurement contract:

$$
\mathbf{z}_k = h(\mathbf{x}) + \mathbf{v}_k, \qquad \mathbf{v}_k \sim \mathcal{N}(0, R_k),
$$

where $h(\cdot)$ is the projection of the object's true state into measurement
space (pixel center, or 3D centroid for LiDAR).

---

## 4. Single-target tracking — the recursive Bayes filter

Tracking *is* recursive Bayesian estimation. The posterior over the target state
$\mathbf{x}_k$ given all measurements $\mathbf{z}_{1:k}$ factors recursively:

$$
p(\mathbf{x}_k \mid \mathbf{z}_{1:k}) \propto
\underbrace{p(\mathbf{z}_k \mid \mathbf{x}_k)}_{\text{measurement}}
\int \underbrace{p(\mathbf{x}_k \mid \mathbf{x}_{k-1})}_{\text{motion}}
\, p(\mathbf{x}_{k-1} \mid \mathbf{z}_{1:k-1}) \, d\mathbf{x}_{k-1}.
$$

For linear-Gaussian models this is the **Kalman filter**. With state
$\mathbf{x}_k$, transition $F$, process noise $Q$, measurement matrix $H$:

**Predict**
$$
\hat{\mathbf{x}}_{k|k-1} = F\hat{\mathbf{x}}_{k-1}, \qquad
P_{k|k-1} = F P_{k-1} F^\top + Q.
$$

**Update** (with innovation $\mathbf{y}_k$ and innovation covariance $S_k$)
$$
\mathbf{y}_k = \mathbf{z}_k - H\hat{\mathbf{x}}_{k|k-1}, \qquad
S_k = H P_{k|k-1} H^\top + R_k,
$$
$$
K_k = P_{k|k-1} H^\top S_k^{-1}, \qquad
\hat{\mathbf{x}}_k = \hat{\mathbf{x}}_{k|k-1} + K_k \mathbf{y}_k, \qquad
P_k = (I - K_k H) P_{k|k-1}.
$$

The **innovation covariance $S_k$ is the single most important object in
tracking** — it defines the gate (§5) and the association cost. For maneuvering
targets, a constant-velocity model under-predicts $Q$; use the **Interacting
Multiple Model (IMM)** filter, which runs a bank of filters (CV, CA, coordinated
turn) and mixes them by a Markov transition matrix:

$$
\mu_k^{(j)} \propto \Lambda_k^{(j)} \sum_i \pi_{ij}\, \mu_{k-1}^{(i)},
$$

where $\Lambda_k^{(j)}$ is the model-$j$ likelihood and $\pi_{ij}$ the model-switch
probability. IMM is what makes air-defense trackers hold a target through a hard
break turn.

---

## 5. Data association — the hard problem

With one target and one measurement, tracking is the Kalman filter. With $M$
measurements and $N$ tracks in clutter, the question *which measurement belongs
to which track?* is combinatorial and is where real trackers live or die.

### 5.1 Gating

First prune: a measurement $\mathbf{z}$ is a plausible candidate for track $i$
only if its **squared Mahalanobis distance** falls inside a gate:

$$
d^2_{ij} = \mathbf{y}_{ij}^\top S_i^{-1} \mathbf{y}_{ij} \le \gamma,
\qquad \mathbf{y}_{ij} = \mathbf{z}_j - H\hat{\mathbf{x}}_i.
$$

Since $d^2 \sim \chi^2_{n_z}$ under the correct-association hypothesis, choose
$\gamma$ from the chi-square inverse CDF (e.g., $\gamma = 9.21$ for a 2D
measurement at 99%). Too tight and you drop real returns during maneuvers; too
loose and clutter floods the association.

### 5.2 Global nearest neighbor (GNN)

The simplest principled associator builds a cost matrix $C_{ij} = d^2_{ij}$ (plus
a gate-violation penalty) and solves the **assignment problem** — minimize total
cost over a permutation — with the **Hungarian algorithm** in $O(n^3)$:

$$
\min_{A} \sum_{i,j} C_{ij} A_{ij}
\quad\text{s.t.}\quad \sum_j A_{ij} \le 1,\ \sum_i A_{ij} \le 1,\ A_{ij}\in\{0,1\}.
$$

GNN commits to one hard assignment per frame. It is fast and fails catastrophically
when two targets cross: at the crossing point both measurements gate to both
tracks and a single bad commit swaps the identities permanently.

---

## 6. Multi-object tracking — JPDA, MHT, and modern alternatives

### 6.1 Joint Probabilistic Data Association (JPDA)

Instead of committing, JPDA computes the *marginal probability* $\beta_{ij}$ that
measurement $j$ originated from track $i$, summed over all feasible joint
association events $\theta$:

$$
\beta_{ij} = \sum_{\theta : j \to i} P(\theta \mid Z_k),
\qquad
P(\theta \mid Z_k) \propto \prod_{(i,j)\in\theta} \mathcal{N}(\mathbf{y}_{ij}; 0, S_i)\, P_D^{\,|\theta|}(1-P_D)^{\cdots}.
$$

Each track is then updated with a **probabilistically weighted innovation**:

$$
\hat{\mathbf{x}}_i = \hat{\mathbf{x}}_{i|k-1} + K_i \sum_j \beta_{ij}\,\mathbf{y}_{ij}.
$$

JPDA never makes a hard commit, so it survives crossings — at the cost of
"smearing" the estimate when targets are genuinely ambiguous. It also assumes a
*known, fixed* number of targets.

### 6.2 Multiple Hypothesis Tracking (MHT)

MHT is the "defer the decision" philosophy taken to its limit. It maintains a
*tree of association hypotheses* across multiple frames and prunes later, when
ambiguity resolves:

```
frame k     k+1        k+2
  T1 ──┬── (z1→T1) ──┬── (z3→T1)   hyp A  score 0.7
       │             └── (z4→T1)   hyp B  score 0.2
       └── (z2→T1) ───── (z3→T1)   hyp C  score 0.1   ← pruned
```

Hypothesis scores accumulate log-likelihoods; an N-scan pruning window and a
k-best assignment solver (Murty's algorithm) keep the tree bounded. MHT is the
gold standard for sparse, high-value targets (air defense, space-object tracking)
but is expensive and tuning-heavy.

### 6.3 Random Finite Sets and the PHD filter

The modern measure-theoretic framing treats the *set* of targets as a single
random object. The **Probability Hypothesis Density (PHD)** filter propagates the
first moment (intensity) $v(\mathbf{x})$ of the target RFS, eliding explicit data
association entirely. The integral of $v$ over a region is the expected number of
targets there. The Gaussian-mixture PHD (GM-PHD) is tractable and handles
birth/death of targets natively — a real advantage over JPDA's fixed count.

### 6.4 Tracking-by-detection in the deep era

SORT and DeepSORT keep the JPDA/GNN skeleton but swap hand-tuned costs for a
Kalman motion gate **plus an appearance-embedding distance**:

$$
C_{ij} = \lambda\, d^2_{\text{motion}}(i,j) + (1-\lambda)\,\big(1 - \cos(\mathbf{e}_i, \mathbf{e}_j)\big),
$$

where $\mathbf{e}$ are learned re-identification features. Appearance is what
lets DeepSORT re-acquire a target after a long occlusion that motion alone could
never bridge.

---

## 7. Uncertainty, calibration, and failure modes

### 7.1 Detector confidence is not probability

A detector trained with cross-entropy is typically **over-confident**. Measure it
with the **Expected Calibration Error**:

$$
\text{ECE} = \sum_{b=1}^{B} \frac{|B_b|}{N}\,\big|\,\text{acc}(B_b) - \text{conf}(B_b)\,\big|,
$$

binning predictions by confidence and comparing average confidence to empirical
accuracy. Temperature scaling — dividing logits by a learned scalar $T$ before
softmax — is the cheapest fix and usually halves ECE. Feed *calibrated*
confidences into the measurement covariance $R_k$, never raw softmax outputs.

### 7.2 The consistency check that catches everything

A correctly tuned tracker has white, unit-magnitude normalized innovations. The
**Normalized Innovation Squared (NIS)** must follow its chi-square distribution:

$$
\text{NIS}_k = \mathbf{y}_k^\top S_k^{-1} \mathbf{y}_k \sim \chi^2_{n_z}.
$$

Average it over a window: if the running NIS sits above the upper $\chi^2$ bound,
your filter is *over-confident* ($Q$ or $R$ too small) and will reject good
measurements; below the lower bound, it is *under-confident* and sluggish. NIS is
the single diagnostic every estimation engineer runs first.

### 7.3 Failure-mode catalogue

| Symptom | Likely cause | Fix |
|---|---|---|
| Identity swap on crossing | hard GNN commit | move to JPDA/MHT or add appearance |
| Track loss during maneuver | $Q$ too small / CV model | IMM, inflate process noise |
| Phantom tracks in clutter | gate too loose, low $P_D$ model | tighten gate, model clutter density |
| Lag behind fast target | latency not modeled | timestamp + predict to measurement time (§[13](13-sensor-fusion.md)) |
| Over-confident covariance | uncalibrated detector | temperature scaling, NIS tuning |

---

## 8. Practice this week

1. Calibrate a webcam with OpenCV `calibrateCamera`; plot the reprojection-error
   histogram and confirm it is zero-mean.
2. Implement a 2D constant-velocity Kalman tracker; feed it synthetic detections
   with clutter and log NIS. Tune $Q$ until NIS sits inside the 95% band.
3. Add Hungarian-algorithm GNN association for two crossing targets and *watch*
   the identity swap. Then add an appearance feature and confirm it disappears.
4. Build a GM-PHD filter on a 4-target scenario with birth/death and compare its
   cardinality estimate to ground truth.

---

## 9. Sources & further study

- **Bar-Shalom, Willett & Tian — *Tracking and Data Fusion*** (and the classic
  Bar-Shalom & Fortmann *Tracking and Data Association*). The canonical reference
  for JPDA, MHT, gating, and IMM.
- **Thrun, Burgard & Fox — *Probabilistic Robotics*.** Recursive Bayes filtering,
  Kalman/particle filters, measurement models.
- **Szeliski — *Computer Vision: Algorithms and Applications*.** Camera models,
  calibration, feature detection.
- **Mahler — *Statistical Multisource-Multitarget Information Fusion*.** The RFS /
  PHD-filter bible.
- **Vo & Ma — "The Gaussian Mixture Probability Hypothesis Density Filter"**
  (IEEE TSP, 2006).
- **Wojke, Bewley & Paulus — "Simple Online and Realtime Tracking with a Deep
  Association Metric" (DeepSORT)**, 2017.
- **Guo et al. — "On Calibration of Modern Neural Networks"**, ICML 2017
  (temperature scaling).

> Framing note: Perception is not "the part where AI sees things." It is a
> stack of estimators, each of which must declare its own uncertainty honestly.
> The engineers who ship reliable autonomy are the ones who treat a bounding box
> the way a surveyor treats a measurement — as a number with error bars — and
> who run NIS on everything before they trust it.

---

## ⚡ The Insider Layer — What the Field Knows but Rarely Writes Down

The published metrics are a recruiting brochure. What follows is the part that
lives in slack threads, postmortems, and the heads of people who have shipped a
perception stack and then been paged at 3 a.m. when it failed.

### mAP is a sales number; the long tail is the product

Everyone benchmarks on mean Average Precision, and mAP is almost useless for
fielded autonomy. It averages over a class distribution dominated by easy,
common objects, so a detector can post a beautiful 0.55 mAP and still miss the
one stroller, the one debris chunk, the one matte-black motorcycle at dusk that
actually kills you. The field's real currency is **failure rate on the rare
class under the rare condition** — what AV teams call the *long tail*. The dirty
secret is that perception accuracy follows a power law: getting from 90% to 99%
costs roughly what getting from 0% to 90% did, and 99% to 99.9% costs that
again. Teams that promise "we're 95% done" are usually 50% done by effort.
Nobody puts the per-condition disaggregated numbers (night + rain + occluded +
small) in a paper because they are embarrassing.

### Calibration and time sync silently eat more accuracy than the model

Newcomers tune the network. Veterans suspect the *plumbing* first. A 5 ms
timestamp error between camera and IMU at 30 m/s smears every projection by
0.15 m — larger than most detector localization error. Extrinsic drift from
thermal expansion and vibration is real: a rigidly bolted camera mount on a
combustion vehicle walks by fractions of a degree as it heats, and a 0.5°
rotation error at 50 m is a 0.44 m lateral shift. The unwritten rule: **before
you blame the detector, run the NIS/innovation whitening test (§7.2) and check
that your sensor latencies are measured, not assumed.** Most "the model is bad"
tickets are actually "the clock is wrong" or "the calibration aged out."

### Label noise sets your ceiling, and your labels are worse than you think

Human bounding-box labels disagree with each other at the few-pixel level and
disagree wildly on occluded, distant, or ambiguous objects. Inter-annotator
IoU on hard examples routinely sits below 0.7. Your model cannot be more
consistent than the labels it learned from, so a chunk of your "error" is
actually the test set being wrong. The pros spend real money on **label
audits and consensus relabeling of the hard slice**, and they treat
auto-labeling (using a large offline model to pseudo-label) as the actual lever
that moved the needle in the last few years — not architecture changes.

### NMS, confidence thresholds, and the knobs that decide everything

The single threshold that most affects a deployed system — the detection
confidence cutoff and the NMS IoU — is rarely discussed in papers because it is
"just engineering." In production it is a *policy decision*: lower the threshold
and you flood the tracker with false positives (phantom braking); raise it and
you drop real objects (the dangerous failure). The right operating point is set
per-class, per-range, and is chosen against the downstream cost of each error
type, not against F1. Soft-NMS and class-aware NMS matter far more in the wild
than the latest backbone. And feed *calibrated* confidence into $R_k$ — raw
softmax is confidence theater.

### Radar and the "sensor everyone underrates"

Marketing loves LiDAR and cameras. The people who keep cars from rear-ending
stopped vehicles in fog love **radar** — it sees velocity directly via Doppler,
punches through weather, and is cheap — but its data is sparse, multipath-ridden,
and has poor angular resolution, so it is unglamorous and underpublished. Fusing
a noisy radar Doppler track with a high-resolution but velocity-blind camera is
where a lot of real safety margin comes from, and almost nobody writes it up
because it is messy and product-specific.

### Unwritten norms of the trade

- **The detector is rarely the bottleneck; association and tracking are.** Spend
  your last week of tuning on gating, IMM, and appearance re-ID, not on swapping
  detector versions.
- **Shadow-mode before you trust.** New perception code runs in the loop
  producing logs but not commanding actuators for weeks, scored against the
  shipping stack. This catches regressions no offline metric does.
- **Disengagement and intervention logs are the real dataset.** The events where
  a human took over *are* your hard-negative mine. Companies live or die on the
  loop: deploy → collect failures → relabel → retrain.
- **"It works in the demo" is the most dangerous sentence in the building.**
  Demos are curated daylight on familiar routes; the tail is where the work is.

What textbooks omit: perception is 20% modeling and 80% data engineering,
calibration hygiene, and operating-point politics. The engineer who internalizes
that — and who reaches for the innovation-consistency test before the GPU — is
the one whose stack survives contact with the real world.
