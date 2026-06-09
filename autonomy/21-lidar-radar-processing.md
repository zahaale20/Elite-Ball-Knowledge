# LiDAR & Radar Processing — Point Clouds, Doppler & All-Weather Sensing

> **Why this exists.** Cameras give rich semantics but no native metric depth and fail in darkness, glare, and weather. LiDAR and radar are the *active* ranging sensors that close that gap: LiDAR emits laser pulses and times their return to build dense, centimeter-accurate 3D geometry; radar emits RF and exploits the Doppler shift to measure *velocity directly* through rain, fog, dust, and darkness. Every serious ground vehicle, many drones, and all weather-critical platforms carry at least one. But their data is alien to image-trained intuition — an unordered cloud of millions of 3D points with no grid, no color, and brutal sparsity at range, or a radar tensor smeared by clutter and multipath. Learning to register, segment, and fuse this data is what separates a robot that works only on sunny test days from one that works at 3 a.m. in a downpour.
>
> **What mastering it makes you.** The engineer who can fuse a laser, a radar, and a camera into one coherent, all-weather model of the world — and who knows which sensor to trust when they disagree.

Point-cloud and radar processing feed the fusion stack of [13-autonomy-sensor-fusion.md](13-sensor-fusion.md), the SLAM/mapping of [12-autonomy-slam-and-mapping.md](12-slam-and-mapping.md), and the state estimation of [14-autonomy-state-estimation-advanced.md](14-state-estimation-advanced.md). It complements the camera geometry of [20-autonomy-computer-vision.md](20-computer-vision.md) and the perception pipelines of [11-autonomy-perception-deep.md](11-perception-deep.md). The deep models for point clouds extend [01-autonomy-ml-ai.md](01-ml-ai.md); the signal-processing math draws on [03-foundations-mathematics.md](../foundations/03-mathematics.md); and the all-weather robustness it provides is essential to the planning of [10-autonomy-planning-decision.md](10-planning-decision.md). Radar's anti-jam relevance ties to [07-autonomy-gnss-jamming-spoofing.md](07-gnss-jamming-spoofing.md).

---

## 1. How the Sensors Work

**LiDAR (Light Detection and Ranging).** Emit a short laser pulse, measure time-of-flight $t$ to the return; range is $r = ct/2$. A spinning or solid-state scanner sweeps the beam across azimuth and elevation, producing a **point cloud**: a set of $(x, y, z, \text{intensity})$ measurements, often with a per-point timestamp and ring index.

Two ranging principles:
- **Pulsed time-of-flight** (Velodyne, Ouster, Hesai): direct timing, long range, robust.
- **AMCW / FMCW LiDAR:** frequency-modulated continuous wave measures range *and* radial velocity per point via the beat frequency — Doppler LiDAR (Aeva, Aurora) brings radar-like velocity to laser resolution.

**Radar (Radio Detection and Ranging).** Emit RF, typically **FMCW** at 77 GHz for automotive. The transmitted chirp's frequency ramps linearly; the echo mixes with the transmitted signal to produce a beat frequency proportional to range, and the phase change across chirps gives Doppler velocity. A 2D FFT (range-FFT then Doppler-FFT) over the received samples yields a **range-Doppler map**; antenna arrays add angle via a third FFT (range-Doppler-angle).

| Property | LiDAR | Radar | Camera |
|---|---|---|---|
| Native depth | Excellent (cm) | Good (range) | None (inferred) |
| Native velocity | Only FMCW | **Yes (Doppler)** | None |
| Angular resolution | High | Low–moderate | Very high |
| Weather (rain/fog/dust) | Degrades | **Robust** | Poor |
| Darkness | Works | Works | Fails |
| Semantics | Geometry only | Poor | Rich |
| Cost / SWaP | High | Low | Very low |

The lesson is written into that table: **no single sensor wins — fusion is mandatory.**

---

## 2. The Point Cloud — A Hard Data Structure

A point cloud $\mathcal{P} = \{\mathbf{p}_i \in \mathbb{R}^3\}_{i=1}^N$ is **unordered, irregular, and sparse**. Unlike an image, there's no grid, no fixed neighbor relationship, and density falls off with range ($\propto 1/r^2$). This breaks convolution and forces specialized data structures and algorithms.

**Spatial indexing** is the prerequisite for everything:
- **k-d tree** — recursive axis-aligned splits; $O(\log N)$ nearest-neighbor queries. The default (Open3D, PCL).
- **Octree** — hierarchical voxel subdivision; great for occupancy and multi-resolution.
- **Voxel grid hashing** — map continuous points to integer voxel keys; the basis of voxel downsampling and modern sparse-conv networks.

**Preprocessing pipeline:**
```
Raw cloud (≈1–2M pts/frame)
   │ voxel downsample (e.g., 5 cm leaf)      → fixed density, ~10× fewer points
   │ statistical outlier removal              → drop points far from local mean
   │ ground-plane segmentation (RANSAC plane) → split ground vs obstacles
   │ normal estimation (PCA on local k-NN)    → per-point surface orientation
   ▼
Clean, structured cloud → registration / segmentation
```

**Normal estimation** fits a plane to each point's neighborhood via PCA: the smallest eigenvector of the local covariance $C = \frac{1}{k}\sum (\mathbf{p}_j - \bar{\mathbf{p}})(\mathbf{p}_j - \bar{\mathbf{p}})^\top$ is the surface normal. Normals power point-to-plane ICP and feature description.

---

## 3. Registration — Aligning Clouds with ICP

The central geometric operation is **registration**: find the rigid transform $(R, \mathbf{t})$ that aligns a source cloud to a target. This is how consecutive LiDAR scans become odometry and how a new scan localizes against a map.

**Iterative Closest Point (ICP)** alternates two steps to convergence:

1. **Correspondence:** for each source point, find the nearest target point (k-d tree).
2. **Solve:** find $(R,\mathbf{t})$ minimizing the alignment error, then transform and repeat.

**Point-to-point ICP** minimizes
$$E(R,\mathbf{t}) = \sum_{i} \big\| R\mathbf{p}_i + \mathbf{t} - \mathbf{q}_{c(i)} \big\|^2$$
solved in closed form per iteration via the SVD of the cross-covariance $H = \sum (\mathbf{p}_i - \bar{\mathbf{p}})(\mathbf{q}_i - \bar{\mathbf{q}})^\top = U\Sigma V^\top$, giving $R = VU^\top$ (with a sign fix for reflections) and $\mathbf{t} = \bar{\mathbf{q}} - R\bar{\mathbf{p}}$.

**Point-to-plane ICP** uses target normals $\mathbf{n}_i$ and converges far faster on structured scenes:
$$E = \sum_i \big( (R\mathbf{p}_i + \mathbf{t} - \mathbf{q}_i) \cdot \mathbf{n}_i \big)^2$$

```
  ITERATION k:                        ITERATION k+1:
   source ○ ○ ○                         source  ○○○
          ╲ ╲ ╲  nearest-pt links        (moved closer)
   target ● ● ●                         target ●●●
   → solve R,t → apply → repeat until ΔE below tol or max iters
```

ICP's weaknesses are its teaching points: it finds only a *local* minimum, so it needs a good initial guess (from IMU/wheel odometry); it's fragile to outliers (use robust kernels, trimmed ICP) and to non-overlapping regions. Global registration (**FPFH features + RANSAC**, or **Fast Global Registration**, or learned **DCP/DGR**) provides the coarse alignment ICP then refines. **NDT (Normal Distributions Transform)** is the common alternative — it models the target as a grid of Gaussians and optimizes the source points' likelihood, more robust to initialization.

---

## 4. Deep Learning on Point Clouds

Standard CNNs assume a grid; point clouds have none. Three families solved this:

- **Point-based (PointNet / PointNet++):** apply a shared MLP to each point independently, then aggregate with a *symmetric* function (max-pool) to achieve permutation invariance:
$$f(\{\mathbf{p}_i\}) = \gamma\!\left( \max_{i} \; h(\mathbf{p}_i) \right)$$
The max-pool is the key insight — it makes the network's output independent of point ordering. PointNet++ adds hierarchical local grouping to capture fine structure.

- **Voxel / sparse-conv (VoxelNet, SECOND, MinkowskiNet):** voxelize, then run 3D convolution *only on occupied voxels* (sparse convolution) to avoid wasting compute on empty space. Efficient and accurate for detection.

- **Range-image / BEV projection:** project the cloud to a 2D range image (native to spinning LiDAR) or a **bird's-eye-view** grid, then use ordinary 2D CNNs. BEV is the dominant paradigm for autonomous-driving detection (**PointPillars**, **CenterPoint**) because it's fast and fuses naturally with maps.

**Tasks:** 3D object detection (oriented bounding boxes + class), semantic segmentation (per-point label), panoptic segmentation, and scene flow (per-point motion). Metrics: 3D IoU and mAP. PointPillars and CenterPoint are the production workhorses on embedded GPUs (chapter 64).

---

## 5. Radar Signal Processing — CFAR & Doppler

Radar's power is velocity and weather penetration; its curse is clutter and low angular resolution. The classic detection problem: in a noisy range-Doppler map, decide which cells are real targets.

**CFAR (Constant False Alarm Rate)** sets an adaptive threshold from the local noise estimate around each cell-under-test, holding the false-alarm probability fixed regardless of background level:
$$T = \alpha \cdot \hat{P}_{noise}, \qquad \alpha = N\!\left( P_{fa}^{-1/N} - 1 \right) \ \text{(CA-CFAR scaling)}$$
where $\hat{P}_{noise}$ averages training cells (with guard cells excluded around the test cell) and $N$ is the number of training cells. **CA-CFAR** (cell-averaging) is the baseline; **OS-CFAR** (ordered-statistics) handles multiple close targets and clutter edges better.

```
   Range-Doppler cells (1D slice):
   [train train | guard | CUT | guard | train train]
        └──── estimate noise ────┘ exclude ─┘
   Detect if  CUT  >  α · (mean of training cells)
```

**Doppler** gives radial velocity directly from the phase progression across chirps:
$$v_r = \frac{\lambda \, f_d}{2}, \qquad f_d = \frac{2 v_r}{\lambda}$$
A single FMCW radar frame thus yields, per detection, range + radial velocity + (coarse) angle — an *instantaneous velocity measurement* no LiDAR or camera provides without differencing frames. This is gold for tracking moving objects and for ego-motion estimation (radar odometry). The cost is angular blur, multipath ghosts, and micro-Doppler clutter — which is why radar detections are *sparse and noisy*, processed as a point cloud of "detections" rather than dense geometry. Modern **4D imaging radar** (range-Doppler-azimuth-elevation) narrows the resolution gap and is increasingly fed to the same deep detectors as LiDAR.

---

## 6. Fusion — Combining Laser, Radar & Camera

The sensors are complementary in *exactly* the dimensions where each is weak, so fusion is the whole game. Three architectural levels:

| Level | What's combined | Pro | Con |
|---|---|---|---|
| **Early (raw/point)** | Paint camera color onto LiDAR points; concat radar to BEV | Maximal information | Tight calibration/sync needed |
| **Mid (feature)** | Fuse learned feature maps in BEV (e.g., BEVFusion) | Best accuracy today | Heavy compute |
| **Late (object)** | Each sensor detects/tracks; fuse object lists (Kalman/JPDA) | Modular, robust to one sensor failing | Loses low-level cues |

The enabling prerequisites are **extrinsic calibration** (the rigid transform between each sensor frame — get this wrong and fused points smear) and **temporal synchronization** (hardware-triggered or timestamp-interpolated; a moving object at 20 m/s moves 0.2 m in 10 ms of sync error). Fusion then rides the estimators of [13-autonomy-sensor-fusion.md](13-sensor-fusion.md): a Kalman/IMM tracker that updates object state from whichever sensor reports, weighting each by its measurement covariance.

```
   LiDAR ─┐ (precise geometry)
   Camera ─┼─► extrinsic-calibrated, time-synced
   Radar ─┘ (velocity, all-weather)
            │
        ┌───┴──────────────────────┐
        │ BEV feature fusion (mid)  │  or object-level (late)
        └───┬──────────────────────┘
            ▼
   Tracked objects {pose, velocity, class, covariance} → planning
```

**Disagreement handling** is the mark of a mature system: when the camera sees nothing but radar reports a 30-m/s closing target in fog, the architecture must *trust the weather-robust sensor* and brake. Encoding these trust priorities — per-sensor validity gating tied to environmental conditions — is real engineering, not a hyperparameter.

---

## 7. Testing All-Weather Perception

> Per the house testing discipline, weather sensors exist precisely for the conditions hardest to test — so testing here is risk prevention against the rare, dangerous case.

| Level | Target | Method |
|---|---|---|
| **Unit** | ICP solve, CFAR threshold, voxel hashing, normal estimation | Synthetic clouds/signals with ground truth |
| **Geometric** | Registration accuracy & convergence basin | Known-transform pairs; sweep init error |
| **Detection** | CFAR $P_d$/$P_{fa}$; 3D mAP | Labeled range-Doppler & point-cloud sets |
| **Robustness** | Rain/fog/dust/snow degradation behavior | Adverse-weather datasets, simulated dropout/attenuation |
| **Fusion** | Correct sensor weighting under disagreement | Inject single-sensor failures; assert safe fallback |
| **Calibration** | Extrinsic/temporal error sensitivity | Perturb calibration; measure smear; sync-jitter sweeps |
| **Exploratory** | Ghost targets, multipath, retroreflectors | Adversarial scene mining |

**Boundary cases to force:** ICP from a bad initial guess (does it diverge gracefully or lock to a wrong minimum?), two targets in one CFAR window (resolution), heavy rain attenuating LiDAR returns, a radar retroreflector ghost, total camera blindness with radar still tracking, and a desync between sensors during fast motion. The acceptance criterion: the fused output *degrades predictably and stays safe* as each sensor is impaired — never a confident wrong answer.

```python
def test_fusion_trusts_radar_in_fog():
    # Risk: camera/LiDAR blindness in fog while a vehicle closes fast.
    scene = SimScene(weather="dense_fog", target_closing_mps=30)
    cam = camera_detector(scene)      # expected: near-empty in fog
    radar = radar_pipeline(scene)     # expected: valid Doppler return
    fused = fuse([cam, radar, lidar_attenuated(scene)])
    # Acceptance: the closing target survives fusion and triggers braking.
    assert fused.has_object(closing_velocity_gt=25)
    assert fused.recommended_action == "brake"
```

---

## 8. The Practical Stack

- **PCL (Point Cloud Library)** — classical filtering, ICP, segmentation, features (FPFH). C++ workhorse.
- **Open3D** — modern Python/C++ for registration, voxelization, visualization, and learning bridges.
- **ROS 2 `sensor_msgs/PointCloud2`, `radar_msgs`** — transport and integration.
- **OpenPCDet / MMDetection3D** — PointPillars, CenterPoint, SECOND, BEVFusion implementations.
- **MinkowskiEngine / spconv** — sparse 3D convolution.
- **Drivers/sensors:** Velodyne, Ouster, Hesai, Livox (LiDAR); Continental, Texas Instruments mmWave, Arbe (radar).
- **TensorRT** — deploying the 3D detectors onboard (chapter 64).

---

## Sources & further study

- **Rusu & Cousins (2011), "3D is here: Point Cloud Library (PCL)."** Plus Rusu's thesis on FPFH and semantic 3D perception.
- **Besl & McKay (1992), "A Method for Registration of 3-D Shapes" (ICP);** Chen & Medioni (point-to-plane); **Biber & Straßer (2003), "NDT."**
- **Qi et al. (2017), "PointNet" and "PointNet++."** **Lang et al. (2019), "PointPillars."** **Yin et al. (2021), "CenterPoint."** **Liu et al. (2022), "BEVFusion."**
- **Richards — *Fundamentals of Radar Signal Processing*.** The standard text: matched filtering, CFAR, Doppler.
- **Skolnik — *Introduction to Radar Systems*.** Classic reference.
- **Zhou & Tuzel (2018), "VoxelNet."** **Choy et al. (2019), "4D Spatio-Temporal ConvNets" (Minkowski).**
- **nuScenes, KITTI, Waymo Open, and adverse-weather datasets (CADC, RADIATE)** for benchmarking fusion.

> Framing note: LiDAR draws the world's geometry with a laser pencil; radar feels its motion through the storm. Cameras understand meaning but go blind when it matters most. The engineer who masters this band stops thinking of "the perception sensor" and starts thinking in *complementary failure modes* — architecting a system that always has at least one sensor it can trust, and that knows, at every instant, which one that is.
