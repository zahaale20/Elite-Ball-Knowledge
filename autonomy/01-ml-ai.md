# Machine Learning & AI for Autonomous Flight — a deep, practical course

**Audience:** you, the owner of this repo — building a 3D-printed tilt-tricopter
VTOL on a Pixhawk 6C + Raspberry Pi 5, with an IMX500 AI camera, that must
eventually **operate on its own**.

**Goal of this document:** teach you *everything* in the ML/AI stack that turns
a remote-controlled airframe into an autonomous one — what each layer is, the
math that makes it work, why it's built the way it is, and exactly where it
already lives (or should live) in *this* codebase. Nothing here is generic
filler; every concept is anchored to a file in `drone/`.

> Mental model for the whole document: **autonomy is a control loop.**
> `sense → perceive → estimate state → decide → act → log`, run at some rate,
> forever. ML lives mostly in **perceive** and parts of **decide**. Classical
> estimation and control own the rest. Knowing which problems are *not* ML
> problems is half of being good at this.

---

## Table of contents

1. [The autonomy stack as layers](#1-the-autonomy-stack-as-layers)
2. [Math you actually need (and what you can skip)](#2-math-you-actually-need)
3. [Perception I — object detection on the IMX500](#3-perception-i--object-detection-on-the-imx500)
4. [Perception II — tracking & data association](#4-perception-ii--tracking--data-association)
5. [State estimation — the EKF and sensor fusion](#5-state-estimation--the-ekf-and-sensor-fusion)
6. [GPS-denied navigation — visual odometry & map-matching](#6-gps-denied-navigation--visual-odometry--map-matching)
7. [World model — memory, contacts, geospatial reasoning](#7-world-model--memory-contacts-geospatial-reasoning)
8. [Decision-making — from rules to policies to learning](#8-decision-making--from-rules-to-policies-to-learning)
9. [Learning control — RL, imitation, sim-to-real](#9-learning-control--rl-imitation-sim-to-real)
10. [The data flywheel — datasets, labeling, retraining](#10-the-data-flywheel)
11. [Model lifecycle on the edge — quantization, deployment, monitoring](#11-model-lifecycle-on-the-edge)
12. [Safety, assurance & the policy layer](#12-safety-assurance--the-policy-layer)
13. [A concrete capability ladder for *this* drone](#13-a-concrete-capability-ladder-for-this-drone)
14. [Glossary](#14-glossary)

---

## 1. The autonomy stack as layers

Think in layers. Each has a **rate**, an **input**, an **output**, and a
**failure mode**. Autonomy is reliable only when every layer degrades
gracefully into the one below it.

```
 Layer            Rate     ML?     This repo
 ───────────────  ───────  ──────  ─────────────────────────────────────────
 Mission / intent ~0.1 Hz  some    policy/intent.py, onboard/mission_director.py
 Decision/policy  1–10 Hz  some    policy/decisions.py, policy/constitution.py
 World model      1–10 Hz  no      onboard/world_memory.py, onboard/contacts.py
 Perception       5–30 Hz  YES     onboard/inference.py, onboard/track_engine.py
 State estimate   50–250Hz mostly  navigation/nav_state.py (filter)
                                    navigation/visual_odometry.py, map_match.py
 Flight control   250–1kHz no       PX4 firmware (on the Pixhawk, not the Pi)
 Actuators        1 kHz    no       ESCs / servos
```

Two rules fall out of this table and drive every design decision in the repo:

1. **The fast inner loops are not ML and must never block on ML.** Attitude and
   rate control run at 1 kHz inside PX4. If your Pi's neural net stalls, the
   aircraft must keep flying straight and level. That's why the Pi is a
   *companion*, advisory by default, and PX4 is authoritative for stabilization.
2. **ML outputs are measurements, not commands.** A detection or a VO velocity
   is fed into an *estimator* with an uncertainty, never wired straight to a
   control surface. This is exactly what `navigation/manager.py` enforces: the
   server hands VO/map-match results in as measurements; the filter decides how
   much to trust them.

If you internalize only one thing: **autonomy = estimation + decision under
uncertainty, with ML as one (fallible) sensor among many.**

---

## 2. Math you actually need

You do not need a PhD. You need fluency in a small set of tools. Here's the
honest list, in priority order, with *why each one shows up in this drone.*

### 2.1 Linear algebra (non-negotiable)
- **Vectors, matrices, matrix multiply.** State `x`, covariance `P`, Jacobians
  `F/H`. Everything in `nav_state.py` is matrix arithmetic.
- **Frames & rotations.** Body frame, NED (North-East-Down), camera frame,
  world/geodetic. A rotation matrix or quaternion converts between them. VO
  produces *body-frame* velocity; the filter needs it in *NED*. Get a frame
  wrong and your drone flies confidently in the wrong direction.
- **Eigenvalues / positive-definiteness.** A covariance matrix must stay
  symmetric positive-definite. When an EKF "blows up," it's usually `P` losing
  that property.

### 2.2 Probability & statistics (the heart of it)
- **Gaussian distributions.** Mean + covariance. The EKF *is* the assumption
  that everything is Gaussian. The `GPS_FIX_SIGMA_M = 2.5` constant in
  `manager.py` is literally "the 1-sigma of this measurement."
- **Bayes' rule.** `posterior ∝ likelihood × prior`. Sensor fusion is Bayes
  applied repeatedly: prior = prediction, likelihood = new measurement.
- **Covariance as trust.** Big sigma = "barely trust this." The whole
  VTOL-phase-dependent aiding in `manager.py` (CRUISE inflates VO sigma ×4) is
  trust-tuning by changing covariances.

### 2.3 Calculus & optimization
- **Gradients / Jacobians.** The "Extended" in EKF means linearizing a
  nonlinear model with a Jacobian. Training any neural net is gradient descent.
- **Least squares.** Map-matching, calibration, bundle adjustment — all
  minimize squared error. Know the normal equations `(AᵀA)x = Aᵀb`.

### 2.4 Geometry
- **Pinhole camera model.** `meters_per_pixel` in `visual_odometry.py` is this:
  pixels → metric ground motion via focal length, altitude, depression angle.
- **Geodesy.** lat/lon ↔ local meters (ENU/NED). Haversine for distance.
  `world_memory.py` and `map_match.py` live here.

### 2.5 What you can defer
- Measure theory, functional analysis, most of "deep learning theory." Useful
  for research; not on the critical path to a flying drone. Learn them when a
  concrete problem demands them, not before.

> **Study tactic:** every time you touch a constant in this repo (a sigma, a
> threshold, a gain), ask "what equation makes this the right number?" That
> reverse-engineering teaches more than any textbook chapter.

---

## 3. Perception I — object detection on the IMX500

This is the part most people mean when they say "AI on a drone." It's also the
most *deceptively* simple, because the hard parts are tracking, geolocation, and
trust — not drawing a box.

### 3.1 What the IMX500 actually is
The Sony **IMX500** is a camera sensor with a small neural-network accelerator
*on the same die*. The model runs **on the sensor**, and the Pi receives
**detections as metadata**, not raw frames it has to run a net over. This is the
single most important hardware fact for your power and latency budget:

- **Pro:** inference is ~free for the Pi CPU; the net runs at sensor frame rate;
  no NPU/GPU needed on the Pi 5.
- **Con:** you're constrained to models the IMX500 toolchain can compile, and to
  modest input resolutions. The default is **SSD MobileNetV2 FPNLite** trained
  on **COCO** (the 80-class list is hard-coded in `inference.py:COCO_LABELS`).

### 3.2 How a single-shot detector works (conceptually)
SSD = **Single Shot Detector**. One forward pass produces, for a grid of
"anchor" boxes tiled over the image at several scales:
1. **Class scores** — softmax over the 80 COCO classes + background.
2. **Box offsets** — how to nudge each anchor to fit the object.

Then two post-processing steps you must understand because you tune them:
- **Confidence threshold** (`DRONE_INFER_CONF`): drop boxes below a score. Too
  low = hallucinations; too high = misses. Drones favor *higher* thresholds
  because a false "person" can trigger the wrong autonomous behavior.
- **Non-Maximum Suppression / IoU** (`DRONE_INFER_IOU`): collapse overlapping
  boxes of the same class into one. **IoU** (Intersection-over-Union) measures
  box overlap; NMS keeps the highest-scoring box and removes others above the
  IoU threshold.

`MobileNetV2` is the **backbone** (feature extractor) — built from
*depthwise-separable convolutions*, which factor a normal convolution into a
cheap per-channel filter + a 1×1 mix. That factorization is *why* it fits on a
sensor. `FPNLite` is a **Feature Pyramid Network**: it fuses features across
scales so small objects (a person seen from 80 m AGL) and large ones are both
detectable.

### 3.3 What this means for your detection quality
The default model was trained on ground-level photos (COCO). Your drone looks
**down from altitude**. This **domain gap** is the #1 reason stock detection
underperforms aerially:
- Objects are tiny, top-down, low-texture.
- COCO has almost no nadir imagery.
- Classes you care about (a *specific* vehicle, a person in a field) are rare
  or absent.

Three escalating fixes, cheapest first:
1. **Tune thresholds + class allow-list** (`DRONE_INFER_CLASSES`). Already
   supported in `inference.py`. Restrict to `person, car, truck, boat` etc. to
   kill irrelevant COCO noise. *Zero training cost.*
2. **Fine-tune the existing model** on aerial data (see §10). You re-use the
   COCO-trained backbone and retrain the head on your own labeled frames. This
   is the highest ROI per hour you'll spend on ML.
3. **Train/compile a custom detector** for the IMX500 toolchain when you need
   classes COCO doesn't have. Highest cost, do it last.

### 3.4 Evaluating a detector honestly
Never trust "it looks good on the HUD." Use numbers:
- **Precision** = of the boxes I drew, what fraction were real? (Low precision =
  false alarms.)
- **Recall** = of the real objects, what fraction did I find? (Low recall =
  misses.)
- **mAP@0.5** (mean Average Precision at IoU 0.5) — the standard single-number
  detector score. Compute it on a held-out *aerial* set, not COCO.
- **Per-altitude / per-lighting breakdown.** A drone's failure modes are
  altitude- and sun-angle-dependent. Average mAP hides that. Your night-vision
  toggle exists for exactly this reason.

> **Where it lives:** `onboard/inference.py` (parse + normalize + allow-list +
> snapshot), `onboard/detection_log.py` (persist detections),
> `tools/hdmi_inference_display.py` (the local overlay). Read these three
> together — they're a complete edge-perception pipeline.

---

## 4. Perception II — tracking & data association

A detector gives you boxes *this frame*. Autonomy needs **persistent objects
over time**: "that's the *same* truck I saw 3 seconds ago, now moving east at
8 m/s." That's **multi-object tracking (MOT)**, and it's where `track_engine.py`
and `contacts.py` come in.

### 4.1 The two sub-problems
1. **Motion prediction** — where will an existing track be next frame? Usually a
   small **Kalman filter** per track with a constant-velocity model. (Yes,
   Kalman again — it's everywhere. Learn it once, §5.)
2. **Data association** — match this frame's detections to existing tracks.
   - **IoU/distance gating:** only consider matches whose boxes are close.
   - **Assignment:** solve the optimal one-to-one matching (the **Hungarian
     algorithm** minimizes total matching cost). Your env knobs `DRONE_TRACK_*`
     parametrize this.
   - **Appearance (optional):** an embedding vector per detection so you can
     re-identify an object after occlusion (this is "DeepSORT"-style tracking;
     `DRONE_TRACK_CMC` hints at camera-motion compensation, important on a
     moving drone where the *whole scene* slides between frames).

### 4.2 Why camera-motion compensation matters here specifically
On a tripod, a stationary car has zero pixel motion. On your drone, the car's
box moves every frame because *the camera* moved. Naive trackers interpret that
as the object accelerating. **CMC** estimates the global background motion
(often from the same optical flow VO uses) and subtracts it, so tracks reflect
*real-world* motion. This is a direct synergy with §6 — the same flow field
feeds both navigation and tracking.

### 4.3 Track lifecycle (the state machine you must get right)
```
 tentative ──(confirmed over N frames)──► active ──(missed M frames)──► lost ──► deleted
```
Tuning N and M trades **false tracks** (too eager to confirm) against **dropped
tracks** (too eager to delete). For a drone, a flickering false track on a
"person" is dangerous if downstream autonomy reacts to it — so confirm
conservatively. This is policy-relevant, not just an ML detail.

### 4.4 From pixels to the world — geolocation
A track in pixels is useless to a mission planner. You need its **ground
position (lat/lon)**. With the drone's pose (from the estimator), the camera
intrinsics/extrinsics, and a ground-height assumption (flat-earth or a DEM),
you **ray-cast** the pixel through the camera onto the ground. This is the same
pinhole geometry as VO, run in reverse.
- `onboard/geotag.py` — stamps detections/imagery with geolocation.
- `onboard/contacts.py` — promotes geolocated tracks into persistent
  **contacts** (real-world entities with a position, class, confidence, history).
- `onboard/world_memory.py` — the spatial store those contacts live in.

> **The conceptual ladder:** `detection (pixels, 1 frame)` → `track (pixels,
> over time)` → `contact (world coords, persistent)` → `world model entity
> (reasoned about by the mission layer)`. Each step adds persistence and
> meaning. ML does the first step; classical geometry + bookkeeping does the
> rest. Knowing where ML *stops* is the senior-engineer insight.

---

## 5. State estimation — the EKF and sensor fusion

If you learn one thing deeply, make it this. **Everything** autonomous depends
on knowing *where you are and how you're moving* with a calibrated sense of
*how sure you are.* That's state estimation, and the workhorse is the
**Kalman filter** (and its nonlinear cousin, the **EKF**).

### 5.1 The Kalman filter in one screen
State `x` (e.g. position + velocity) with covariance `P` (uncertainty). Two
steps, repeated forever:

**Predict** (use a motion model `F`, add process noise `Q`):
$$ \hat{x}_k = F\,x_{k-1}, \qquad P_k = F\,P_{k-1}\,F^\top + Q $$

**Update** (fold in a measurement `z` with model `H` and noise `R`):
$$ K = P_k H^\top (H P_k H^\top + R)^{-1} $$
$$ x_k = \hat{x}_k + K\,(z - H\hat{x}_k), \qquad P_k = (I - K H)\,P_k $$

Read it in English:
- **Predict** = "based on physics, here's where I think I am, and I'm a bit less
  sure now" (`P` grows).
- **Kalman gain `K`** = "how much do I trust this new measurement vs. my
  prediction?" — computed *automatically* from the relative covariances. Small
  `R` (precise sensor) → big `K` → snap to the measurement. Big `R` → ignore it.
- **Update** = "blend prediction and measurement, and I'm more sure now"
  (`P` shrinks).

**The "Extended" part:** when the motion or measurement model is nonlinear
(geodesy, camera projection), you linearize it each step via a Jacobian. That's
the only difference. PX4's internal estimator (**EKF2**) does this at high rate
for attitude/position; your `navigation/nav_state.py` does a focused version for
the GPS-denied position problem.

### 5.2 Why fuse at all? Because no single sensor is enough
| Sensor      | Good at                    | Bad at                          |
| ----------- | -------------------------- | ------------------------------- |
| IMU (gyro/accel) | fast, high-rate motion | drifts; integrates error fast   |
| GPS         | absolute position          | slow, jammable, denied indoors  |
| Barometer   | altitude trend             | absolute offset, weather drift  |
| Magnetometer| heading                    | metal/motor interference        |
| Camera (VO) | local velocity, cheap      | scale/altitude dependent, blurs |
| Map-match   | absolute, GPS-free fix     | needs texture + a reference map |

Fusion = let each sensor cover the others' weaknesses, weighted by trust (`R`).
The IMU carries you between slow absolute fixes; GPS or map-match bounds the
IMU's drift. This is the entire game.

### 5.3 The crucial honesty: covariance is a promise
An estimator that reports a tight covariance but is actually wrong is **worse
than no estimator** — downstream code *trusts* that number. Two failure modes:
- **Overconfident** (`R`/`Q` too small): filter ignores reality, diverges.
- **Underconfident** (too big): filter is sluggish, noisy, never commits.

Tuning `Q` and `R` is the real job. Your repo exposes them as env knobs
(`DRONE_NAV_GPS_SIGMA_M`, `DRONE_VO_VEL_SIGMA`, the CRUISE multipliers) so you
tune on *logged flight data* without code changes — exactly right.

### 5.4 The phase-dependent trust trick (study `manager.py`)
A tiltrotor is three different aircraft: a multicopter in HOVER, an airplane in
CRUISE, and chaos in TRANSITION. VO assumes a slow, near-nadir, textured-ground
view — true in HOVER, false in CRUISE (motion blur, high AGL), worst in
TRANSITION (violent attitude change). So `manager.py` **changes which sensors it
trusts based on the live `MAV_VTOL_STATE`**:
- HOVER → trust VO at face value.
- CRUISE → inflate VO covariance ×4 (or drop it), lean on map-match + air-data
  dead-reckoning.
- TRANSITION → drop VO, coast on last good velocity.

This is sensor fusion *with situational awareness of the platform.* It's a
beautiful, slightly advanced idea and it's already in your code — read it until
it's obvious.

---

## 6. GPS-denied navigation — visual odometry & map-matching

The single most valuable autonomy capability for a defense-relevant drone:
**fly without GPS.** GPS is jammed and spoofed routinely. Your stack already has
the two halves.

### 6.1 Visual odometry (the *relative* half) — `visual_odometry.py`
**Idea:** between two frames, the ground appears to shift. If you know your
altitude (so each pixel = a known number of ground-meters) and your frame
interval, the *median motion of tracked features* gives a **body-frame
velocity**. Integrated by the filter, that holds position locally — the same
job a PX4FLOW optical-flow sensor does, but in software on the camera you
already carry.

The pipeline (all classical CV, no neural net needed):
1. **Detect features** (corners — Shi-Tomasi / `goodFeaturesToTrack`).
2. **Track them** to the next frame (**Lucas-Kanade** optical flow).
3. **Reject outliers** (RANSAC / median; moving cars must not bias the
   *ego*-motion estimate).
4. **Scale to metric** via `meters_per_pixel(altitude, FOV, depression)` — the
   pinhole geometry. The `MIN_DEPRESSION_DEG = 15` guard refuses to emit a
   velocity when the camera looks too near the horizon and the scale explodes.
5. **Emit velocity + a covariance** that grows when few features survive or the
   geometry is poor. *Always emit uncertainty, never a bare number.*

**Why classical, not learned?** Lucas-Kanade is deterministic, cheap, certifiable
and debuggable. Learned VO (deep flow nets) can be more robust to blur/low
texture but costs compute and trust you don't need yet. Correct engineering
call: classical first, learned only if it earns its place.

### 6.2 Map-matching (the *absolute* half) — `map_match.py`
VO drifts — every odometry method does, because you're integrating noisy
velocity (errors accumulate). You need **absolute fixes** to bound the drift.
Map-matching answers "where am I on a known map?" by matching the live
downward camera to **georeferenced reference imagery / a terrain DEM**:
- Correlate the current frame (or its features) against a reference tile.
- The best-aligned tile location is an **absolute lat/lon fix** — fed into the
  filter as a measurement (a `MapFix` with a covariance), bounding VO drift.
- Conceptually it's **visual terrain-relative navigation (TRN)**, the technique
  cruise missiles and Mars landers use.

### 6.3 How the two combine (this is the architecture)
```
 IMU (high rate) ─► predict ─┐
 VO velocity (HOVER)  ───────┤
 air-data DR (CRUISE) ───────┤──► EKF (nav_state.py) ──► position + covariance
 map-match abs fix ──────────┤
 GPS (when healthy/allowed) ─┘
```
- **VO** keeps you smooth and local (relative).
- **Map-match** keeps you honest and global (absolute, drift-bounded).
- **The filter** blends them by trust.
- **`set_gps_denied()`** is the honest flight-test toggle: cut GPS and prove the
  vision-only stack holds position *before* you ever need it for real.

> This is genuinely the crown jewel of your autonomy stack. If you can
> demonstrate a clean GPS-denied hover-and-return on logged data, you have
> something most hobby programs never reach and that defense programs care about.

---

## 7. World model — memory, contacts, geospatial reasoning

Perception is per-instant. Autonomy needs **persistent spatial memory**: a model
of *what is where in the world*, updated over time, reasoned about by the mission
layer. This is mostly **not ML** — it's data structures, geometry, and
probabilistic bookkeeping — but it's where perception becomes *useful*.

### 7.1 Contacts — `onboard/contacts.py`
A **contact** is a real-world entity: class, geolocation, confidence, first/last
seen, track history. Built by promoting geolocated tracks (§4.4). The key
operations:
- **Fuse** new detections into existing contacts (is this the same truck?
  spatial + class + temporal gating — same association math as tracking, now in
  world coordinates).
- **Decay** confidence over time (a contact unseen for minutes is stale).
- **Deconflict** duplicates from multiple viewpoints/passes.

### 7.2 World memory — `onboard/world_memory.py`
The spatial store. Think "a queryable map of contacts and observations":
- Spatial indexing so "what's within 200 m of this waypoint?" is fast.
- Persistence across the flight (and ideally across flights — a prior map).
- Feeds the search planner, the follow behavior, and the mission director.

### 7.3 Search & coverage — `onboard/search_planner.py`
"Find X in this area" is a **coverage planning** problem, not an ML one:
- Decompose the search area, plan a lawnmower/boustrophedon or spiral path that
  guarantees sensor coverage given the camera footprint.
- Optionally **information-driven** search: go where the probability of finding
  the target is highest (a Bayesian occupancy/probability grid — this is where a
  little probabilistic ML *does* help).

### 7.4 Follow & swarm — `onboard/follow.py`, `onboard/swarm.py`
- **Follow**: keep a contact in frame / maintain a standoff. A control problem
  (a PID or pursuit law on the contact's geolocation), informed by perception.
- **Swarm**: coordinate multiple aircraft (deconflict airspace, partition
  search). Mostly distributed-systems and consensus, with optional learned
  coordination far down the road.

> **The senior insight again:** by line count, most "autonomy" is geometry,
> bookkeeping, and state machines — not neural nets. ML is a powerful *sensor*
> feeding a mostly-classical decision system. Build the classical scaffolding
> well and ML slots in cleanly; skip it and no model will save you.

---

## 8. Decision-making — from rules to policies to learning

"Operate on its own" ultimately means **the drone chooses actions**. There's a
spectrum from hand-written rules to learned policies. You should climb it slowly
and deliberately, because **every rung trades transparency for capability**, and
in a flying, possibly-armed system, transparency is safety.

### 8.1 The spectrum
```
 Rules / FSM ──► Behavior trees ──► Planning (search/optim) ──► Learned policy (RL/IL)
 transparent                                                     capable
 certifiable                                                     opaque
```

### 8.2 Where you are now — rules + a constitution
- `onboard/mission_director.py` — the **finite state machine / behavior tree**
  that sequences mission phases (takeoff → transition → waypoints → search →
  RTL). This is the right default: explicit, testable, debuggable.
- `policy/intent.py` — captures *what the operator wants* (the goal), separate
  from *how* it's achieved. Clean separation of intent vs. execution.
- `policy/constitution.yaml` + `constitution.py` — **hard constraints the
  autonomy may never violate** (geofence, altitude caps, no-fly, battery
  reserves). This is your **safety envelope as code**. Crucially it sits *above*
  any learned component: a policy can *propose*, the constitution *disposes*.
- `policy/decisions.py` — the **tamper-evident decision log** (hash-chained, see
  the file's docstring). Every allow/deny is recorded with provenance so you can
  answer "why did it do that?" after the fact. **This is what makes autonomy
  auditable** — non-negotiable for BVLOS/defense.

### 8.3 Climbing toward planning
Before any learning, the next rung is **classical planning**:
- **Path planning** — A*/Dijkstra/RRT on a cost map (avoid terrain, no-fly,
  threat zones). Deterministic, explainable, certifiable.
- **Decision under uncertainty** — **POMDP**-style reasoning when you must act
  with incomplete knowledge (search, pursuit). Often approximated with simple
  heuristics + the probability grid from §7.3.

### 8.4 When (and whether) to use learned decision-making
Learned policies (RL/IL, §9) shine for **continuous control in hard-to-model
dynamics** — e.g. aggressive maneuvers, wind rejection, perch-and-land. They are
*bad* fits for **discrete safety-critical mission logic**, where a rule you can
read and test beats a black box. Recommended posture for this program:
- **Learn the lowest, fastest, most-physical layers** (control, agility) *in
  sim, under the constitution.*
- **Keep the high-level mission logic explicit** (FSM + planner) where humans and
  auditors can read it.
- **Never let a learned component issue an action the constitution hasn't
  cleared.** The constitution is the seatbelt; learning is the engine.

---

## 9. Learning control — RL, imitation, sim-to-real

This is the deep-ML frontier of autonomy. You likely won't need it to reach a
useful autonomous mission, but you asked for *everything*, and understanding it
tells you what's possible and what's hype.

### 9.1 Reinforcement learning (RL) in one paragraph
An **agent** in a **state** takes an **action**, gets a **reward**, lands in a
new state; it learns a **policy** (state → action) that maximizes long-term
reward. Formalized as a **Markov Decision Process** (states, actions,
transitions, reward, discount γ). For drones, RL has produced superhuman
**acrobatic** and **racing** control (e.g. Swift, champion-level FPV racing) by
training in simulation and transferring to hardware.

Key algorithm families:
- **Policy gradient / PPO** — the workhorse for continuous control; stable,
  widely used for locomotion and flight.
- **Actor-critic (SAC, TD3)** — sample-efficient continuous control.
- **Model-based RL** — learn the dynamics, plan through them; data-efficient,
  more complex.

### 9.2 Imitation learning (often the smarter first step)
Instead of rewards, learn from **demonstrations**: record an expert (you, flying
manually, or a classical controller) and train a net to copy the mapping
(observation → action). **Behavioral cloning** is the simplest; **DAgger**
fixes its biggest flaw (the net visits states the expert never demonstrated, so
you iteratively add corrections). For your program, imitation of your *own
classical controllers* is a safe way to distill them into faster/cheaper nets.

### 9.3 Sim-to-real — the wall everyone hits
A policy trained in simulation fails on hardware because **sim ≠ reality** (the
*reality gap*): unmodeled aerodynamics, motor lag, sensor noise, latency.
Bridging it:
- **Domain randomization** — randomize masses, winds, delays, sensor noise in
  sim so the policy learns a *robust* behavior that includes reality as one
  sample.
- **System identification** — measure your *actual* motor/airframe params and
  match the sim to them (this is literally your Stage 2 custom SDF + Stage 4
  airframe params — **good system ID is the foundation of any future learned
  control**).
- **HITL / log replay** — validate on recorded real data before flying.

### 9.4 The honest recommendation for *this* drone
1. Nail classical control + estimation + the SITL → real pipeline first
   (Stages 1–6). This *is* the sim-to-real infrastructure RL would need anyway.
2. If you pursue learning, start with **imitation in sim** for a *narrow* skill
   (e.g. a smooth, wind-robust transition), under the constitution, validated in
   HITL.
3. Treat full RL flight control as a research arc, not a milestone. The payoff
   is agility you may never need; the risk is opacity you can't afford. Know it
   exists; deploy it only when a concrete capability demands it.

---

## 10. The data flywheel

Models are only as good as their data, and a drone is a **data-generation
machine**. Building the loop that turns flights into better models is the
highest-leverage ML *engineering* you can do — more than any architecture choice.

```
 fly ─► log frames + detections + telemetry ─► curate/label ─► train/fine-tune
   ▲                                                                   │
   └──────────────── deploy improved model to the edge ◄──────────────┘
```

### 10.1 Logging (you already have the hooks)
- `onboard/detection_log.py` — detections over time.
- `drone/logs/` + PX4 `.ulog` — telemetry & flight state.
- **Synchronize** them by timestamp so every frame has the drone's pose. *A
  frame without a pose is nearly worthless for aerial training.* This pairing is
  what makes your data uniquely valuable.

### 10.2 Curate before you label
Don't label everything — label what's *informative*:
- **Hard / uncertain cases** (detections near the confidence threshold) teach
  the most. (This is **active learning**: prioritize the examples the model is
  least sure about.)
- **Failure cases** (false alarms, misses you noticed) — the decision log and
  DVR clips let you find these.
- Balance altitudes, lighting (your NV mode!), backgrounds.

### 10.3 Labeling
- Tools: CVAT, Label Studio, Roboflow. For boxes you need class + tight
  rectangle; for tracking, consistent IDs across frames.
- **Auto-label then correct:** run the current model, fix its mistakes. Far
  faster than from scratch, and it focuses human effort exactly on the model's
  weaknesses.

### 10.4 Train / fine-tune
- **Transfer learning**: start from the COCO-pretrained backbone, retrain the
  head on your aerial data. Orders of magnitude less data than from scratch.
- **Augmentation**: rotation, scale, brightness, blur, cutout — synthesize the
  variety you can't fly. Especially valuable to simulate altitude/lighting you
  under-sampled.
- **Validate on a held-out *aerial* set** (§3.4), never on COCO, never on your
  training frames.

### 10.5 Close the loop
Re-deploy (§11), measure the new model against the old on the same held-out set,
keep it only if it's *actually* better. This discipline — versioned data,
versioned models, measured deltas — is what separates an ML *engineer* from
someone who runs `train.py` and hopes.

---

## 11. Model lifecycle on the edge

Training is on a laptop/cloud GPU. Running is on a sensor with a tiny compute
and power budget. Bridging that is **edge ML engineering**, and it's where many
hobby projects quietly fail.

### 11.1 Quantization (the central edge technique)
Neural nets train in 32-bit floats but the IMX500 runs **8-bit integers**.
**Quantization** maps floats → int8, cutting size/compute ~4× and enabling the
on-sensor accelerator. Two flavors:
- **Post-training quantization (PTQ)** — quantize a trained model using a small
  *calibration* set to pick the float→int scales. Fast; usually a small accuracy
  hit. Start here.
- **Quantization-aware training (QAT)** — simulate int8 during training so the
  model adapts. More work, recovers most of the lost accuracy. Use if PTQ drops
  too much.

For the IMX500 specifically, you compile through **Sony's IMX500 converter /
Model Compression Toolkit** to produce the on-sensor `.rpk`. The compiler's
**operator support is the real constraint** — design/choose architectures the
toolchain accepts (that's why SSD-MobileNet is the default; it's known-good).

### 11.2 Latency, rate, and the control-loop budget
Every layer has a deadline. If perception runs at 10 Hz but tracking assumes
30 Hz, your motion models are wrong. Measure **end-to-end latency** (photon →
detection → decision), not just model inference. A late detection is a *wrong*
detection because the world moved. This is why fast loops never wait on ML (§1).

### 11.3 Deployment & versioning
- **Version models like code** — a model is an artifact with a hash, a training
  dataset version, and measured metrics. `DRONE_IMX500_MODEL` selects it; treat
  that as a pinned dependency, not a loose file.
- **Shadow / canary**: run a new model alongside the old, logging both, before
  trusting it to drive behavior. The decision log makes this auditable.

### 11.4 Monitoring & drift
A model that was great in summer degrades in snow. **Distribution shift** is
real and silent. Monitor:
- Detection-rate and confidence distributions over time (sudden changes = drift
  or a sensor problem).
- **Out-of-distribution** inputs — if the camera sees something unlike training
  data, *lower autonomy's trust*, don't barrel ahead. An honest "I don't know"
  routed to the policy layer is a feature, not a bug.

---

## 12. Safety, assurance & the policy layer

For a drone that acts on its own — and especially anything defense-adjacent —
**this section outranks all the ML above it.** A clever model that can't be
trusted or audited is a liability, not a capability. Your repo already takes
this seriously; here's the framework around it.

### 12.1 Defense in depth — layers that each fail safe
1. **PX4 firmware failsafes** (lowest, most trusted): RC loss, battery, geofence
   breach → RTL/land. Independent of the Pi. If the Pi (and all your ML) dies,
   the aircraft still recovers.
2. **The constitution** (`policy/constitution.*`) — hard limits autonomy can't
   cross, checked *before* any command reaches the autopilot.
3. **`nav_failsafe.py` / `geofence.py`** — onboard enforcement of position and
   boundary safety.
4. **The decision log** (`policy/decisions.py`) — tamper-evident audit so every
   autonomous choice is explainable and reviewable after the fact.

> The pattern: **propose-then-check.** Any layer (including a future learned
> one) may *propose* an action; an independent, simple, trusted layer *checks*
> it against hard constraints. The proposer can be complex and opaque; the
> checker must be simple and certifiable.

### 12.2 Why ML makes assurance *harder* (and how to cope)
- **Non-determinism / opacity** — you can't read a net's "reasoning." Cope by
  bounding its *authority* (advisory, under the constitution) and *logging* its
  outputs.
- **Brittleness / adversarial inputs** — small perturbations fool detectors.
  Cope with OOD detection (§11.4), conservative thresholds, and never letting a
  single detection trigger an irreversible action.
- **Specification gaming** (RL) — a policy maximizes the literal reward, not your
  intent. Cope by keeping learned components *narrow*, *sandboxed*, and *under
  the constitution.*

### 12.3 The human's role
Autonomy is a spectrum, not a switch. Design explicit **autonomy levels** and
**human-on-the-loop** handoffs: the drone proposes, a human can veto, and as
trust is *earned on logged evidence*, you widen autonomy deliberately. "Operate
on its own" should be the *end* of a measured progression, never the default.

### 12.4 Ethics & legality (not optional)
For anything defense-relevant: **meaningful human control** over the use of
force is the line. Engineering autonomy responsibly means building the
*ability to constrain it* (the constitution, the log, the human handoff) with at
least as much rigor as the capability itself. This is not a footnote; it is the
profession.

---

## 13. A concrete capability ladder for *this* drone

Map ML/AI work onto your existing Stage gates ([02-autonomy-vtol-roadmap.md](02-vtol-roadmap.md)). Each rung is
*demonstrable* and builds on the last. Don't skip; each is the test infra for
the next.

| Rung | Capability | What you build | Repo anchor | ML depth |
| ---- | ---------- | -------------- | ----------- | -------- |
| 0 | **Reliable detection HUD** | Tune conf/IoU/class allow-list; honest aerial mAP eval | `inference.py`, `tools/hdmi_inference_display.py` | tuning only |
| 1 | **Persistent tracking** | Confirm/delete tuning, CMC, stable IDs | `track_engine.py` | classical KF + association |
| 2 | **Geolocated contacts** | Ray-cast pixels→lat/lon, fuse into contacts | `geotag.py`, `contacts.py`, `world_memory.py` | geometry, light prob. |
| 3 | **GPS-denied hold** | VO + map-match + filter; `set_gps_denied()` on logged data | `navigation/*` | estimation (the big one) |
| 4 | **Autonomous search** | Coverage planner + probability grid over the world model | `search_planner.py` | planning + Bayes grid |
| 5 | **Autonomous follow** | Standoff control on a contact, under constitution | `follow.py`, `policy/*` | control + perception |
| 6 | **Data flywheel** | Logging → curate → fine-tune → redeploy, measured deltas | `detection_log.py`, `logs/` | the real ML engineering |
| 7 | **Custom aerial model** | Fine-tuned/compiled IMX500 detector for your classes | IMX500 toolchain | training + quantization |
| 8 | **(Research) learned control** | Imitation-in-sim of a narrow skill, HITL-validated | sim + `policy/*` | RL/IL, sim-to-real |

**Suggested order of effort:** 0 → 1 → 2 → **3** → 6 → 4 → 5 → 7 → (8 maybe
never). Rung 3 (GPS-denied) is the highest-value, most-differentiating
capability and it's the one your codebase is already architected around. Rung 6
(the flywheel) is what compounds — it makes every other rung better over time.

---

## 14. Glossary

- **AGL** — Above Ground Level (altitude over terrain, not sea level).
- **Anchor box** — a prior box shape a detector refines into a prediction.
- **Backbone** — the feature-extracting body of a net (e.g. MobileNetV2).
- **BVLOS** — Beyond Visual Line Of Sight operation.
- **CMC** — Camera Motion Compensation (subtract ego-motion from tracks).
- **Covariance (`P`,`Q`,`R`)** — uncertainty; the language of trust in fusion.
- **DEM** — Digital Elevation Model (terrain height map).
- **Domain gap / distribution shift** — train data ≠ deployment data.
- **EKF** — Extended Kalman Filter (Kalman for nonlinear models).
- **FPN** — Feature Pyramid Network (multi-scale features for small + big objects).
- **Hungarian algorithm** — optimal one-to-one assignment (detections↔tracks).
- **IoU** — Intersection over Union (box overlap metric; drives NMS).
- **Imitation learning (BC/DAgger)** — learn a policy from demonstrations.
- **Jacobian** — matrix of partial derivatives; linearizes a nonlinear model.
- **Kalman gain (`K`)** — auto-computed trust between prediction & measurement.
- **mAP** — mean Average Precision (the standard detector score).
- **MDP / POMDP** — (Partially Observable) Markov Decision Process; RL/planning math.
- **MOT** — Multi-Object Tracking.
- **NED / ENU** — local Cartesian frames (North-East-Down / East-North-Up).
- **NMS** — Non-Maximum Suppression (collapse duplicate boxes).
- **NPU** — Neural Processing Unit (here, on the IMX500 die).
- **OOD** — Out Of Distribution (input unlike training data).
- **PPO / SAC / TD3** — continuous-control RL algorithms.
- **PTQ / QAT** — Post-Training / Quantization-Aware (int8) Training.
- **Precision / Recall** — false-alarm vs. miss trade-off.
- **Quantization** — float32 → int8 for edge inference.
- **RANSAC** — robust model fit that rejects outliers (used in VO).
- **RL** — Reinforcement Learning.
- **Sim-to-real / reality gap** — why sim-trained policies fail on hardware.
- **SSD** — Single Shot Detector (one-pass detection; your default model).
- **State estimation** — recover pose/velocity + uncertainty from sensors.
- **TRN** — Terrain-Relative Navigation (absolute fix from matching terrain/imagery).
- **VO** — Visual Odometry (velocity/position from image motion).
- **ULog** — PX4's binary flight log format.

---

### How to use this document

Read §1, §2, and §5 until they're reflexes — they're the spine. Then pick your
current rung from §13 and read the matching deep section. Every time you change a
constant in the code, find the equation behind it here. The fastest way to learn
this material is to **make a number in this repo correct on purpose.**

*Built against the actual state of `drone/` as of June 2026: PX4 6C + Pi 5,
IMX500/SSD-MobileNet perception, `navigation/` GPS-denied stack, `onboard/`
tracking + world model, `policy/` constitution + decision log.*

---

## Sources & Citations

> Companion docs in this folder: GNC/estimation → [09-autonomy-gnc.md](09-gnc.md);
> planning/decision → [10-autonomy-planning-decision.md](10-planning-decision.md);
> control → [06-autonomy-control-theory.md](06-control-theory.md);
> capability ladder maps onto [02-autonomy-vtol-roadmap.md](02-vtol-roadmap.md).

**Perception & detection**
- Liu et al. — *SSD: Single Shot MultiBox Detector* (arXiv:1512.02325).
- Sandler et al. — *MobileNetV2* (arXiv:1801.04381); Lin et al. — *Feature Pyramid Networks* (arXiv:1612.03144).
- Lin et al. — *Microsoft COCO* (arXiv:1405.0312).
- Redmon et al. — *YOLO* family (arXiv:1506.02640 and successors).

**Tracking**
- Bewley et al. — *SORT* (arXiv:1602.00763); Wojke et al. — *DeepSORT* (arXiv:1703.07402).
- Zhang et al. — *ByteTrack* (arXiv:2110.06864); Aharon et al. — *BoT-SORT* (arXiv:2206.14651).

**Estimation, VO & navigation**
- Thrun, Burgard & Fox — *Probabilistic Robotics*, MIT Press.
- Lucas & Kanade (1981) optical flow; Shi & Tomasi — *Good Features to Track* (CVPR 1994).
- Qin et al. — *VINS-Mono* (arXiv:1708.03852); Mur-Artal et al. — *ORB-SLAM*.

**Learning control & edge ML**
- Sutton & Barto — *Reinforcement Learning* (free): http://incompleteideas.net/book/the-book.html
- Schulman et al. — *PPO* (arXiv:1707.06347); Haarnoja et al. — *SAC* (arXiv:1801.01290).
- Kaufmann et al. — *Champion-level drone racing with deep RL (Swift)*, Nature 2023.
- Tobin et al. — *Domain Randomization* (arXiv:1703.06907).
- Sony IMX500 / Model Compression Toolkit: https://developer.sony.com/imx500/  ·  https://github.com/sony/model_optimization

**Official docs**
- PyTorch: https://pytorch.org  ·  OpenCV: https://opencv.org  ·  ONNX: https://onnx.ai
- PX4 EKF2 / vision fusion: https://docs.px4.io  ·  Ultralytics YOLO: https://docs.ultralytics.com

*Repo references (`onboard/`, `navigation/`, `policy/`) point to the author's `pixhawk/drone/` codebase.*
