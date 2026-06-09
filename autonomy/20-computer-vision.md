# Computer Vision for Robotics — Geometry, Features & Deep Perception

> **Why this exists.** A robot that cannot see is a robot that cannot act in unstructured environments. Cameras are the highest-information, lowest-cost, lowest-weight sensor on any autonomous platform — a $5 image sensor delivers millions of measurements per frame — but those measurements arrive as a flat array of brightness values with no inherent notion of distance, object, or motion. Computer vision is the discipline of inverting the imaging process: recovering 3D geometry, identity, and dynamics from 2D projections. For robotics it splits into two lineages that must be married — the *geometric* tradition (calibrated cameras, epipolar constraints, structure from motion) that gives metric, verifiable estimates, and the *learned* tradition (CNNs, transformers) that gives semantic understanding no hand-written feature could. Master both or you will either have geometry with no meaning or meaning with no metric.
>
> **What mastering it makes you.** The engineer who can take a raw camera stream and produce a calibrated, semantically-labeled, metrically-scaled model of the world the robot can plan against — and who knows exactly when the deep network is hallucinating.

Vision is the front-end for nearly everything downstream: it feeds the VIO of [22-autonomy-visual-inertial-odometry.md](22-visual-inertial-odometry.md), the SLAM of [12-autonomy-slam-and-mapping.md](12-slam-and-mapping.md), the fusion of [13-autonomy-sensor-fusion.md](13-sensor-fusion.md), and the perception pipelines of [11-autonomy-perception-deep.md](11-perception-deep.md). Its deep-learning half is an application of [01-autonomy-ml-ai.md](01-ml-ai.md); its geometric half is projective linear algebra from [03-foundations-mathematics.md](../foundations/03-mathematics.md); and its outputs drive the planning of [10-autonomy-planning-decision.md](10-planning-decision.md). Edge deployment of the networks is covered in [25-autonomy-edge-inference-deployment.md](25-edge-inference-deployment.md).

---

## 1. The Imaging Model — How 3D Becomes 2D

Everything starts with the **pinhole camera**. A 3D point $\mathbf{X} = (X, Y, Z)^\top$ in the camera frame projects to image coordinates $(u, v)$ by perspective division and the intrinsic matrix $K$:

$$
\begin{bmatrix} u \\ v \\ 1 \end{bmatrix} \sim K \begin{bmatrix} X \\ Y \\ Z \end{bmatrix}, \qquad
K = \begin{bmatrix} f_x & s & c_x \\ 0 & f_y & c_y \\ 0 & 0 & 1 \end{bmatrix}
$$

with focal lengths $f_x, f_y$ (pixels), principal point $(c_x, c_y)$, and skew $s \approx 0$. The full projection from world coordinates includes extrinsics — rotation $R$ and translation $\mathbf{t}$:

$$\mathbf{x} \sim K\,[\,R \mid \mathbf{t}\,]\,\mathbf{X}_{world}, \qquad P = K[R\mid\mathbf{t}]\ \text{(the }3\times4\text{ camera matrix)}$$

Real lenses violate the pinhole model. **Distortion** is modeled with radial ($k_1,k_2,k_3$) and tangential ($p_1,p_2$) terms:
$$x_d = x(1 + k_1 r^2 + k_2 r^4 + k_3 r^6) + 2p_1 xy + p_2(r^2 + 2x^2), \quad r^2 = x^2 + y^2$$

**Calibration** recovers $K$ and distortion by imaging a known target (checkerboard) and solving a nonlinear least-squares (Zhang's method, implemented in OpenCV `calibrateCamera`). *Garbage calibration ⇒ garbage geometry forever downstream* — this is the single most common silent failure in robot vision.

```
   World point X
        │   project through optical center
        ▼
   ┌───────────┐
   │  image     │   (u,v) = K · [R|t] · X  (up to scale)
   │  plane     │   depth Z is LOST in a single image
   └───────────┘
        │
        ▼  recover depth only via motion / stereo / learned prior
```

---

## 2. Features — Finding What to Track

A single pixel is ambiguous; we need *distinctive, repeatable* points. A feature has two parts: a **detector** (where) and a **descriptor** (what).

- **Harris / Shi-Tomasi corners:** points where the image gradient varies in two directions, measured by the second-moment matrix $M = \sum_W \nabla I \nabla I^\top$. A corner has two large eigenvalues of $M$ (the Harris response $R = \det M - \kappa\,(\operatorname{tr} M)^2$).
- **SIFT** (Lowe): scale-invariant via difference-of-Gaussians pyramid; 128-D descriptor from gradient histograms; rotation-invariant. Gold standard for robustness, patented-then-freed, somewhat slow.
- **ORB** (Oriented FAST + rotated BRIEF): binary 256-bit descriptor, Hamming-distance matching, ~100× faster than SIFT. The workhorse of real-time SLAM (**ORB-SLAM3**).
- **Learned features:** **SuperPoint** (self-supervised detector+descriptor) matched with **SuperGlue / LightGlue** (graph-neural-network matcher) now beat hand-crafted features in hard conditions (low texture, viewpoint change) and run on GPU.

| Feature | Invariance | Descriptor | Speed | Robotics use |
|---|---|---|---|---|
| Harris/Shi-Tomasi | translation | — (track patch) | very fast | KLT optical flow, VIO front-end |
| SIFT | scale, rotation | 128-D float | slow | offline SfM, loop closure |
| ORB | rotation, some scale | 256-bit binary | fast | ORB-SLAM3, real-time |
| SuperPoint+SuperGlue | learned, robust | learned | GPU-bound | hard relocalization |

Matching descriptors gives putative correspondences; outliers are rejected with **RANSAC** fitting a geometric model (Sec. 3).

---

## 3. Multi-View Geometry — Recovering 3D from Motion

Two views of the same scene are linked by the **epipolar constraint**, the foundation of structure from motion. For corresponding *normalized* image points $\hat{\mathbf{x}}, \hat{\mathbf{x}}'$ (after applying $K^{-1}$):

$$\hat{\mathbf{x}}'^\top E\, \hat{\mathbf{x}} = 0, \qquad E = [\mathbf{t}]_\times R \quad \text{(essential matrix)}$$

In raw pixel coordinates the analog is the **fundamental matrix** $F = K'^{-\top} E K^{-1}$, satisfying $\mathbf{x}'^\top F \mathbf{x} = 0$. Geometrically, a point in one image must lie on a *line* (its epipolar line $F\mathbf{x}$) in the other — this collapses the 2D search for a match to 1D.

```
   View 1                         View 2
   ●  x  ─────────── epipolar plane ───────────  x' ●
    \         (defined by X and two centers)        /
     \                                              /
   center C1 ────────── baseline ────────── center C2
   Match for x must lie on the epipolar line l' = F·x in View 2.
```

**The SfM pipeline:**
1. Detect & match features across views.
2. Estimate $F$ (8-point algorithm) or $E$ (5-point, Nistér) inside **RANSAC** to reject mismatches.
3. Decompose $E = U \Sigma V^\top$ into the four possible $(R, \mathbf{t})$ solutions; pick the one with points in front of both cameras (cheirality).
4. **Triangulate** matched points: each correspondence gives two equations; solve the linear system (DLT) then refine.
5. **Bundle adjustment** — jointly refine all camera poses $\{R_i,\mathbf{t}_i\}$ and 3D points $\{\mathbf{X}_j\}$ by minimizing total reprojection error:

$$\min_{\{R_i,\mathbf{t}_i\},\{\mathbf{X}_j\}} \sum_{i,j} \rho\!\left( \big\| \mathbf{x}_{ij} - \pi(K_i,R_i,\mathbf{t}_i,\mathbf{X}_j) \big\|^2 \right)$$

where $\pi$ is the projection function and $\rho$ a robust (Huber) cost. This sparse nonlinear least-squares is solved with Levenberg–Marquardt and Schur complement tricks in **Ceres Solver**, **g2o**, or **GTSAM** — the same machinery powering SLAM and VIO. The scale of $\mathbf{t}$ is unobservable from a monocular camera alone, which is *exactly* why we add an IMU (chapter 61) or stereo.

**Stereo** sidesteps the scale ambiguity with a known baseline $b$: depth from disparity $d = u_L - u_R$ is

$$Z = \frac{f \cdot b}{d}$$

Disparity is estimated by matching along epipolar lines (after rectification), classically with semi-global matching (SGM), now with learned stereo networks.

---

## 4. Deep Perception I — Convolutional Networks

Geometry tells you *where*; CNNs tell you *what*. A convolutional layer slides learned kernels over the image, exploiting translation equivariance and locality — the right inductive bias for pixels. Stacked with nonlinearities and pooling, CNNs learn a hierarchy from edges → textures → parts → objects.

The convolution at layer $\ell$:
$$y_{c'}(i,j) = \sigma\!\left( b_{c'} + \sum_{c}\sum_{p,q} w_{c'c}(p,q)\, x_c(i+p, j+q) \right)$$

Architectures that matter for robotics:
- **ResNet** — residual connections $\mathbf{y} = \mathcal{F}(\mathbf{x}) + \mathbf{x}$ enable very deep, trainable backbones; still the default feature extractor.
- **U-Net / FCN** — encoder–decoder with skip connections for dense **semantic segmentation** (per-pixel class).
- **YOLO / SSD** — single-shot **object detection**: predict boxes + classes in one forward pass, real-time on edge GPUs.
- **Mask R-CNN** — instance segmentation (separate masks per object).

The losses you train against:
$$\mathcal{L}_{cls} = -\sum_c y_c \log \hat{y}_c \ \ (\text{cross-entropy}), \qquad \mathcal{L}_{box} = \text{smooth-}L_1(\hat{b}, b)$$

For detection, anchors and **non-max suppression (NMS)** clean up overlapping boxes; metrics are **IoU** and **mAP**. Robotics cares about *latency and calibration of confidence* as much as accuracy — see chapter 64.

---

## 5. Deep Perception II — Vision Transformers

Transformers replaced convolution's locality bias with global **self-attention**. An image is split into patches, linearly embedded into tokens, and processed by attention layers. The core operation, for queries $Q$, keys $K$, values $V$:

$$\text{Attention}(Q,K,V) = \operatorname{softmax}\!\left( \frac{QK^\top}{\sqrt{d_k}} \right) V$$

Every patch attends to every other patch, so a ViT models long-range context (a wheel implies a car across the image) that a CNN's small receptive field reaches only after many layers. The $\sqrt{d_k}$ scaling keeps the softmax in a stable gradient regime.

- **ViT** — pure transformer classification backbone; needs large data or distillation.
- **DETR** — object detection as *set prediction* with bipartite (Hungarian) matching; removes anchors and NMS.
- **SAM (Segment Anything)** — promptable, zero-shot segmentation foundation model; increasingly used to bootstrap robot perception labels.
- **DINOv2 / self-supervised ViTs** — features that transfer to depth, segmentation, correspondence without task labels.

The cost is quadratic in token count ($O(N^2)$ attention), which is why edge deployment (chapter 64) leans on windowed attention (Swin), token pruning, and quantization. Hybrid CNN+transformer backbones are common in practice.

---

## 6. Depth, Flow & Dense Structure

Robots act on geometry, so dense per-pixel estimates are often the goal:

- **Monocular depth** (MiDaS, Depth Anything): a network predicts relative depth from a single image using learned priors. *Scale-ambiguous* — calibrate against a metric sensor or known object before trusting absolute distances.
- **Optical flow** (RAFT): dense per-pixel motion $\mathbf{u}(x,y)$ between frames via iterative refinement on a 4D correlation volume. Drives motion segmentation and VIO front-ends.
- **Stereo depth networks** (RAFT-Stereo, PSMNet): learned disparity, metric when the baseline is known.
- **Neural fields** (NeRF, 3D Gaussian Splatting): represent a scene as a continuous function of position/direction; reconstruct photorealistic geometry from posed images. Increasingly used for robot mapping and sim asset generation (links to chapter 62 sim-to-real).

$$\text{NeRF: } (\mathbf{x}, \mathbf{d}) \to (\mathbf{c}, \sigma), \quad C(\mathbf{r}) = \int_{t_n}^{t_f} T(t)\,\sigma(t)\,\mathbf{c}(t)\,dt$$

where $T(t) = \exp(-\int_{t_n}^t \sigma\,ds)$ is accumulated transmittance — volumetric rendering by quadrature.

---

## 7. The Geometry ↔ Learning Marriage

The two lineages are complementary, and modern robot vision *fuses* them:

| Need | Geometry gives | Learning gives | Fusion |
|---|---|---|---|
| Pose / scale | Metric, verifiable, drift-bounded with loop closure | — (scale-ambiguous alone) | Learned features feed BA |
| Semantics | — | Object/class/mask | Semantic SLAM |
| Robust matching | Epipolar verification | SuperGlue correspondence | RANSAC on learned matches |
| Depth | Metric (stereo/SfM) | Dense even in low texture | Learned depth scaled by geometry |

The principle: **use learning for the ill-posed parts (semantics, single-image priors, matching in hard conditions) and geometry for the parts that must be metric and certifiable (pose, triangulation, scale).** A network's confidence is not a probability you can trust without calibration; a reprojection residual is.

```
   Image stream
       │
   ┌───┴────────────────────────────┐
   │ Learned front-end              │  SuperPoint / SuperGlue
   │ (features, matches, semantics) │
   └───┬────────────────────────────┘
       │ correspondences + labels
   ┌───┴────────────────────────────┐
   │ Geometric back-end             │  RANSAC + Bundle Adjustment
   │ (pose, structure, scale)       │  (Ceres / GTSAM)
   └───┬────────────────────────────┘
       │ metric, semantic 3D model → planning
```

---

## 8. Testing Vision Systems

> Per house testing discipline, vision must be validated as risk prevention, not just accuracy chasing — a 99%-mAP detector that fails silently at dusk can crash the vehicle.

| Level | Target | Method |
|---|---|---|
| **Unit** | Calibration math, projection $\pi$, triangulation, NMS | Synthetic points with known ground truth |
| **Geometric** | Reprojection error bounded; epipolar residuals small | Inject known-pose pairs, assert residuals |
| **Model** | Detection/segmentation accuracy *and calibration* | Held-out set, mAP/IoU, reliability diagrams |
| **Robustness** | Lighting, motion blur, rain, glare, sensor noise | Domain-shift suites, adversarial corruptions |
| **Integration** | Vision → SLAM/planning closed loop | Sim (Isaac/CARLA) + recorded rosbags |
| **Exploratory** | Out-of-distribution failure discovery | Edge-case mining, failure-case clustering |

**Boundary cases to force:** textureless walls (feature starvation), repetitive patterns (aliased matches), reflective/transparent surfaces, glare and over/under-exposure, fast rotation (motion blur), and OOD objects the detector never trained on. The acceptance criterion is not "high accuracy" but "*known* behavior — detect-or-abstain — under all foreseeable inputs."

```python
def test_detector_abstains_under_blur():
    # Risk: motion blur silently degrades detections during fast maneuvers.
    img = load("frame.png")
    clear = detector(img)
    blurred = detector(motion_blur(img, kernel=21))
    # Acceptance: confidences must drop (calibrated) rather than stay falsely high.
    assert mean_confidence(blurred) < mean_confidence(clear)
    # And the system must flag low-confidence frames for the safety monitor.
    assert any(d.confidence < ABSTAIN_THRESHOLD for d in blurred)
```

---

## 9. The Practical Stack

- **OpenCV** — calibration, classical features, geometry, RANSAC. The bedrock.
- **ORB-SLAM3 / VINS-Fusion** — geometric SLAM/VIO using these primitives.
- **PyTorch + torchvision / Detectron2 / MMDetection / Ultralytics YOLO** — deep models.
- **GTSAM / Ceres / g2o** — bundle adjustment and factor-graph back-ends.
- **Open3D** — point clouds and 3D (overlaps with chapter 60).
- **TensorRT / ONNX Runtime** — deploying the networks onboard (chapter 64).
- **ROS 2 `image_pipeline`, `vision_msgs`** — integration glue.

---

## Sources & further study

- **Hartley & Zisserman — *Multiple View Geometry in Computer Vision*.** The bible of projective geometry, epipolar constraints, fundamental/essential matrices, bundle adjustment.
- **Szeliski — *Computer Vision: Algorithms and Applications* (2nd ed., free online).** Broad, modern, robotics-aware reference.
- **Forsyth & Ponce — *Computer Vision: A Modern Approach*.**
- **Lowe (2004), "Distinctive Image Features from Scale-Invariant Keypoints" (SIFT).**
- **Rublee et al. (2011), "ORB: an efficient alternative to SIFT or SURF."**
- **He et al. (2016), "Deep Residual Learning" (ResNet);** **Dosovitskiy et al. (2021), "An Image is Worth 16×16 Words" (ViT);** **Carion et al. (2020), "End-to-End Object Detection with Transformers" (DETR).**
- **Mur-Artal & Tardós — ORB-SLAM2/3 papers.** **Teed & Deng (2020), "RAFT."** **Mildenhall et al. (2020), "NeRF."**
- **Kirillov et al. (2023), "Segment Anything" (SAM).**

> Framing note: Computer vision for robotics is a humility discipline. Geometry will tell you, with provable residuals, where things are — but only if your calibration is honest. Deep networks will tell you what things are with superhuman skill — but they will also, occasionally and confidently, lie. The master engineer treats the camera as a precision instrument *and* the network as a fallible expert, and architects the system so that geometry can catch the network's hallucinations before they reach the actuators.
