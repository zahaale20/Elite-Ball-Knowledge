# Ten-Year Mastery Plan — From This Drone to Operating at an Elite Level at Anduril

**Author's situation (June 2026):** You have built a working onboard autonomy
stack (FastAPI service, MAVSDK/pymavlink, IMX500 on-device inference, GPS-denied
nav pipeline, track fusion, world memory, constitution-gated command policy,
tamper-evident decision log) and assembled a physical VTOL tilt-tricopter around
a Pixhawk 6C + Raspberry Pi 5. You move fast with AI assistance.

**The gap this plan closes:** Moving fast with AI gets you a *working* system.
Operating at an elite level at a company like Anduril requires you to *own the
fundamentals* — to know why every layer works, to debug it at 3am when the AI
is wrong, to design systems that are safe, real-time, testable, and that scale
from one vehicle to a coordinated fleet. This plan makes you the engineer who
can do that.

> **How to read this document.** Each year has: (1) **Mission** — the one-line
> objective; (2) **Why it matters at Anduril** — the connection to elite defense
> autonomy work; (3) **Topics to learn** — broken into fundamentals, depth, and
> frontier; (4) **Concrete actions on THIS project**; (5) **Milestones /
> exit criteria**; (6) **Proof of mastery** — what you must be able to do
> unaided. Do not advance a year until the exit criteria are genuinely met.

---

## North Star

> **Become an autonomy systems engineer who can design, build, harden, and
> field a safety-critical, perception-driven, GPS-denied-capable, multi-vehicle
> autonomous system — and explain and defend every layer of it.**

Anduril's product surface (Lattice, autonomous air/ground/maritime vehicles,
sensor fusion, counter-UAS, edge AI) maps almost one-to-one onto the
capabilities you are already prototyping. This plan turns prototypes into
mastery.

The non-negotiable through-lines for all ten years:

- **Fundamentals over frameworks.** You must understand the math and the
  systems, not just the API calls.
- **Safety and determinism are features.** In defense autonomy, "it usually
  works" is a failure. Everything is gated, logged, testable, and recoverable.
- **Write it in C++ eventually.** Python is your prototyping language. The
  real-time, flight-critical, and embedded layers of elite autonomy are C++
  (and increasingly Rust). You will become fluent.
- **Measure everything.** Logs, metrics, replay, and post-mission analysis are
  how serious autonomy teams learn. Build that muscle from year one.

---

## Skills Map (the full territory)

```
                         ELITE AUTONOMY ENGINEER
                                   |
   ┌───────────────┬───────────────┼───────────────┬───────────────┐
   |               |               |               |               |
 MATH &         CONTROLS &      PERCEPTION &     SYSTEMS &       AUTONOMY &
 ESTIMATION     FLIGHT          COMPUTER         SOFTWARE        FLEET / C2
   |            DYNAMICS         VISION / AI      ENGINEERING        |
   |               |               |               |               |
 - Linear alg   - Rigid-body    - Camera model  - C++/Rust       - Planning
 - Probability    dynamics      - Multi-view    - Real-time OS   - Multi-agent
 - Calculus/    - PID/LQR/MPC     geometry      - Concurrency    - Task alloc
   optimization - State machines- Deep learning - Networking     - Behavior trees
 - Kalman/EKF/  - Control       - Detection/    - Distributed    - Human-machine
   particle       allocation      tracking        systems          teaming
   filters      - Aerodynamics  - Sensor fusion - Security       - Mission C2
 - SLAM math    - VTOL          - Edge          - CI/CD          - Sim & test
 - Lie groups     transition      inference     - Observability  - Safety case
```

Every year drives one or two columns deeper while keeping the others alive.

---

# YEAR 1 (2026–2027) — Make the Aircraft Trustworthy + Rebuild Your Fundamentals

### Mission
Turn your assembled airframe into a machine that flies *predictably and safely*,
and rebuild the mathematical and systems fundamentals underneath everything you
have been generating with AI.

### Why it matters at Anduril
Elite autonomy engineers are trusted because their systems don't surprise
anyone. The path there starts with disciplined hardware bring-up, sensor
calibration, failsafe design, and the math literacy to reason about every
estimate and command. You cannot fake this layer.

### Topics to learn

**Fundamentals (do not skip — these underlie all ten years):**
- **Linear algebra**: vectors, matrices, eigenvalues, rotations, change of
  basis, least squares. (Strang, *Introduction to Linear Algebra*; 3Blue1Brown
  *Essence of Linear Algebra*.)
- **Probability & statistics**: distributions, Bayes' rule, covariance,
  Gaussian math, maximum likelihood. (Wasserman, *All of Statistics*.)
- **Calculus & numerical methods**: gradients, Jacobians, Taylor expansion,
  numerical integration, stability. (Boyd & Vandenberghe, *Convex Optimization*
  ch. 1–3 for intuition.)
- **Rigid-body kinematics**: coordinate frames (body/NED/ENU/ECEF), Euler
  angles, quaternions, rotation matrices, frame transforms. This is the
  language of *everything* in flight.

**Depth (flight systems):**
- **PX4 internals**: SYS_AUTOSTART, the control allocator, mixers, EKF2,
  failsafe state machine, parameter system, uORB messaging, MAVLink streams.
- **VTOL specifics**: tiltrotor control allocation, transition airspeed
  thresholds, hover vs cruise mixing, the `MAV_VTOL_STATE` machine.
- **Power & propulsion**: LiPo chemistry, C-rating, ESC timing, motor KV,
  prop pitch, thrust/weight, current draw, thermal limits.
- **Sensor calibration**: accel/gyro/mag calibration, vibration isolation,
  compass interference, GPS fix quality, barometer drift.
- **MAVLink / MAVSDK / pymavlink**: message families, rates, the difference
  between offboard control, mission protocol, and parameter protocol.

**Frontier (start observing, not mastering):**
- Read PX4's EKF2 documentation end-to-end. You will *implement* an EKF in
  Year 5; this year you only need to read state estimation as a consumer.

### Concrete actions on THIS project
- Lock the hardware **BOM** (Stage 3 in `ROADMAP.md`): 3× motors, 3× ESCs,
  tilt servos, V-tail servos, verify Pixhawk 6C PWM/UART channel budget.
- Finalize `drone/airframes/tiltrotor.params` (Stage 4): output mapping, tilt
  allocator, V-tail mixer, transition thresholds. Load to SITL first.
- Complete the **bench bring-up protocol** (Stage 5): motors-off arm test,
  control-surface direction test, ESC calibration, all sensor cals, RC
  failsafe, telemetry link check. Script and document each step.
- Write a **preflight checklist** and a **go/no-go gate** as a runnable script.
- Make **SITL regression mandatory** before any flight: `tools/sim_up.sh` must
  pass a scripted hover→transition→waypoints→land before you touch the real
  aircraft.
- Start a **flight log discipline**: every sortie produces a `.ulog`, and you
  review it with PlotJuggler / Flight Review afterward.

### Milestones / exit criteria
- [ ] First successful manual hover, recovered cleanly.
- [ ] First autonomous takeoff → hover → land → RTL with zero unexplained
      behavior.
- [ ] Every sensor calibrated; failsafes (RC loss, low battery, geofence)
      tested in SITL and on the bench.
- [ ] You can derive a body→NED rotation by hand and explain a quaternion.

### Proof of mastery
You can take a raw `.ulog`, identify a vibration or tuning problem from the
plots, and explain the fix — without AI.

---

# YEAR 2 (2027–2028) — Make Flight Operations Boring + Control Theory

### Mission
Achieve *repeatable, predictable* flight across the full VTOL envelope, and
learn the control theory that governs it.

### Why it matters at Anduril
Autonomous vehicles must behave identically across thousands of sorties.
Control theory is the literacy that lets you tune, diagnose, and trust a vehicle
— and later design controllers for novel airframes and payloads.

### Topics to learn

**Fundamentals:**
- **Classical control**: feedback, poles/zeros, stability margins, Bode plots,
  PID tuning theory (not just trial and error). (Åström & Murray, *Feedback
  Systems* — free online.)
- **State-space control**: state vectors, controllability, observability, LQR.
- **Discrete-time systems**: sampling, aliasing, control loop rates, latency.

**Depth:**
- **PX4 tuning**: rate controllers, attitude controllers, position controllers,
  the multicopter and fixed-wing tuning guides, VTOL transition tuning.
- **Aerodynamics basics**: lift, drag, stall, angle of attack, wing loading,
  why transition is the dangerous regime.
- **Battery & energy management**: usable capacity, sag under load, range/
  endurance estimation, reserve policy.
- **RF & link budgets**: RC link (ELRS), telemetry radio, Wi-Fi range,
  antenna placement, what link loss actually looks like in logs.

**Frontier:**
- **Model Predictive Control (MPC)**: read the concept; you'll appreciate why
  advanced autonomy uses it for trajectory tracking.

### Concrete actions on THIS project
- Fly **structured sortie cards**: same maneuver, repeated, logged, compared.
- **Tune the transition** until MC→FW→MC is smooth and repeatable.
- Implement and test **safety gates**: geofence breach → RTL (already scaffolded
  in `onboard/geofence.py`), battery floor, link-loss behavior, transition
  airspeed interlock.
- Build a **post-flight analysis script**: ingest a `.ulog`, emit a one-page
  report (max tilt, vibration, current peaks, mode timeline, any failsafe).
- Formalize an **incident review**: every anomaly gets a written root cause.

### Milestones / exit criteria
- [ ] 25+ logged sorties with consistent, documented behavior.
- [ ] You can launch, transition, fly a mission, and recover on demand.
- [ ] You can hand-tune a rate loop and explain *why* each gain changed.

### Proof of mastery
Given a poorly tuned vehicle, you can diagnose it from logs and bring it to a
clean tune methodically, explaining the control-theory reasoning at each step.

---

# YEAR 3 (2028–2029) — Production-Grade Software + Learn C++

### Mission
Turn your onboard stack from "works on my Pi" into a hardened, observable,
reproducible system — and become genuinely fluent in C++ (the language of
flight-critical autonomy).

### Why it matters at Anduril
Lattice and the vehicle autonomy stacks are large, real-time, C++/Rust
codebases with rigorous engineering practices. Python prototyping gets you in
the room; systems engineering keeps you there.

### Topics to learn

**Fundamentals:**
- **C++ (modern, C++17/20)**: ownership/RAII, smart pointers, move semantics,
  templates, the STL, build systems (CMake), undefined behavior, sanitizers.
  (Stroustrup, *A Tour of C++*; then *Effective Modern C++*, Meyers.)
- **Computer systems**: memory hierarchy, cache behavior, processes vs threads,
  syscalls, the Linux scheduling model. (Bryant & O'Hallaron, *CS:APP*.)
- **Concurrency**: threads, locks, atomics, lock-free queues, data races, and
  why your current Python thread-locked design choices matter.

**Depth:**
- **Real-time systems**: deadlines, jitter, priority inversion, why GC and
  dynamic allocation are dangerous in flight loops.
- **API & service design**: idempotency, versioned contracts, backpressure,
  graceful degradation (you already do telemetry shaping — formalize it).
- **Observability**: structured logging, metrics, tracing, health endpoints.
- **Security**: TLS, secret management, authn/authz, MAVLink2 signing, network
  hardening (your `Security hardening` notes are the seed — complete them).
- **Reproducible deployment**: systemd, immutable images, deterministic builds,
  recovery from a fresh SD card.

**Frontier:**
- **Rust**: read an intro. Increasingly used for safety-critical autonomy.

### Concrete actions on THIS project
- **Rewrite one performance-critical module in C++** (e.g., the visual-odometry
  inner loop or the track-fusion filter) and bind it back into Python. This is
  your first real C++ artifact.
- Add **metrics + structured logs** to the onboard service; expose a health
  endpoint and a `/metrics` scrape.
- Make **deploy reproducible**: a single script that takes a blank Pi image to a
  fully running, secured onboard node.
- Complete the **security hardening**: enforce TLS, MAVLink2 signing, firewall
  the UDP ports, fail-closed secrets in production.
- Stand up **CI** (Stage 7): lint, type-check, unit + integration tests,
  dependency scan, on every push, for both repos.

### Milestones / exit criteria
- [ ] One module reimplemented in C++ with tests, matching Python behavior.
- [ ] Full system recoverable from a blank image via one documented procedure.
- [ ] CI green on both repos; no manual deploy steps remain.

### Proof of mastery
You can read a flight-critical C++ codebase, find a data race with a sanitizer,
and fix it — and you can explain why your service degrades gracefully under
link loss.

---

# YEAR 4 (2029–2030) — Perception You Can Trust + Deep Learning Foundations

### Mission
Make onboard perception (detection, tracking, classification) stable and
reliable enough to *drive mission decisions*, and learn the deep-learning and
computer-vision fundamentals underneath it.

### Why it matters at Anduril
Sensor fusion and perception are the core of modern defense autonomy. Detecting,
tracking, and classifying objects reliably — at the edge, in degraded conditions
— is the product.

### Topics to learn

**Fundamentals:**
- **Computer vision math**: camera intrinsics/extrinsics, pinhole model,
  distortion, homography, epipolar geometry, triangulation. (Szeliski,
  *Computer Vision: Algorithms and Applications* — free.)
- **Deep learning**: backprop, CNNs, training dynamics, loss functions,
  overfitting, evaluation metrics (precision/recall, mAP, IoU). (Goodfellow et
  al., *Deep Learning*; fast.ai for hands-on.)
- **Multi-object tracking math**: data association, the Hungarian algorithm,
  Kalman tracking, SORT/ByteTrack/BoT-SORT (which your tracker already mimics).

**Depth:**
- **Edge inference**: quantization, model formats, the IMX500 on-sensor NN
  pipeline, latency/throughput tradeoffs, why the sensor caps your frame rate.
- **Detection & pose models**: SSD, YOLO family, HRNet/HigherHRNet pose,
  anchor vs anchor-free, NMS.
- **Appearance / re-ID**: embeddings, feature distance, occlusion handling
  (your ghost-buffer re-ID is the seed — ground it in the theory).
- **Camera calibration in practice**: calibrate your actual IMX500 + lens.

**Frontier:**
- **Sensor fusion preview**: read about fusing EO/IR + radar tracks (you'll do
  this conceptually in Years 5–7).

### Concrete actions on THIS project
- **Calibrate your real camera** and store intrinsics; feed them into geotag /
  projection so world-positions get more accurate.
- Build an **offline replay + evaluation harness**: run recorded flights through
  detection/tracking, score against hand-labels, compare model versions.
- Improve **track identity** through occlusion and aggressive ego-motion; add
  metrics (ID switches, track fragmentation) to the harness.
- Train or fine-tune a **custom detector** for a class you care about and deploy
  it to the IMX500; measure the accuracy/latency tradeoff.
- Make perception output **drive a mission decision** (e.g., confirmed track →
  investigate), gated by the constitution policy.

### Milestones / exit criteria
- [ ] Calibrated camera; measurable improvement in geotag accuracy.
- [ ] Replay harness with quantitative tracking metrics over multiple flights.
- [ ] A custom model trained, deployed, and benchmarked on-device.

### Proof of mastery
You can take a perception failure (a dropped track, a false positive), trace it
to a root cause (calibration, association threshold, model recall), fix it, and
prove the fix with metrics.

---

# YEAR 5 (2030–2031) — GPS-Denied Navigation + State Estimation Mastery

### Mission
Make GPS-denied navigation *real and trusted*: visual odometry + map-matching +
filtering that keeps a usable pose when GPS degrades — and master the estimation
theory behind it.

### Why it matters at Anduril
Operating in contested/GPS-denied environments is a defining requirement of
defense autonomy. State estimation and sensor fusion are the deepest, most
valued skills in the field.

### Topics to learn

**Fundamentals:**
- **Estimation theory**: Kalman filter (derive it), EKF, UKF, particle filters,
  observability, consistency, NEES/NIS testing. (Thrun, Burgard, Fox,
  *Probabilistic Robotics* — the bible.)
- **SLAM & VIO**: visual-inertial odometry, factor graphs, bundle adjustment,
  loop closure, drift, scale. (Read VINS-Mono and ORB-SLAM papers.)
- **Lie groups (SO(3)/SE(3))**: the correct math for rotations and poses on
  manifolds. (Sola, *A micro Lie theory for state estimation*.)

**Depth:**
- **Terrain-relative navigation**: matching a camera frame to satellite tiles +
  DEM (you have `map_tiles.py`, `dem_tiles.py`, `map_match.py` already).
- **PX4 external vision fusion**: EKF2 `EKF2_EV_CTRL`, `VISION_POSITION_ESTIMATE`
  injection, timing/latency requirements, failure handling.
- **Uncertainty discipline**: covariance propagation, gating, when to trust a
  fix vs coast on dead reckoning.

**Frontier:**
- **Learned VIO / deep odometry**: read the literature; know the tradeoffs vs
  classical.

### Concrete actions on THIS project
- Finish and **validate the nav pipeline** (`drone/navigation/`): NavFilter,
  visual odometry, map-match, vision bridge.
- Add **consistency tests** (NEES/NIS) to prove the filter isn't overconfident.
- **Carefully** wire `VISION_POSITION_ESTIMATE` into PX4 EKF2 — SITL first,
  then tethered, then controlled outdoor tests, always with a GPS fallback.
- Build a **GPS-degradation test**: progressively starve GPS in flight and
  measure how long/accurately the vehicle holds position on vision alone.
- Wire the **nav-loss failsafe** (`onboard/nav_failsafe.py`) into the live loop.

### Milestones / exit criteria
- [ ] Filter passes consistency tests in SITL and on real logs.
- [ ] Vehicle holds a usable local pose through a controlled GPS dropout.
- [ ] Vision-to-EKF2 path validated with a safe fallback at every step.

### Proof of mastery
You can derive an EKF on a whiteboard, explain why your VIO drifts and what
bounds it, and demonstrate the aircraft navigating without GPS.

---

# YEAR 6 (2031–2032) — Mission Autonomy + Planning & Decision-Making

### Mission
Make the vehicle execute *complete missions* with minimal intervention: search,
investigate, follow, patrol — with human-in-the-loop control and clean recovery.

### Why it matters at Anduril
Autonomy is the product. The value is a system that takes a high-level intent
("search this area, report what you find") and executes it safely, with the
operator supervising rather than piloting.

### Topics to learn

**Fundamentals:**
- **Planning**: A*/D*/RRT/RRT*, cost maps, coverage planning, information-
  theoretic search. (LaValle, *Planning Algorithms* — free.)
- **Decision-making under uncertainty**: MDPs, POMDPs, utility, when to use
  learning vs explicit policy. (Sutton & Barto, *Reinforcement Learning* — for
  literacy, not necessarily deployment.)
- **Behavior architectures**: behavior trees, state machines, hierarchical
  task networks — and why these beat monolithic logic for safety.

**Depth:**
- **Mission composition**: composable mission primitives, preconditions,
  recovery transitions, operator approval gates.
- **Human-machine teaming**: supervised autonomy, override paths, intent
  expression, trust calibration, the "constitution"-gated command model you
  already have.
- **World modeling**: persistent contacts, cross-flight memory (you have
  `contacts.py`, `world_memory.py`, `search_planner.py`).

**Frontier:**
- **LLM/VLM-assisted intent** (your `policy/intent.py`): how to use models for
  high-level intent *without* letting them touch flight safety — the gating
  pattern is the moat.

### Concrete actions on THIS project
- Wire the **unwired intelligence layer** into the live loop (per your repo
  notes: `track_engine.py`, `world_memory.py`, `search_planner.py`,
  `policy/intent.py` are built+tested but not runtime-wired).
- Build a **mission template library**: inspection, area search, follow/escort,
  perimeter patrol — each composable and recoverable.
- Add **operator approval flows**: autonomy proposes, operator confirms,
  everything logged to the tamper-evident decision chain.
- Run **end-to-end autonomous missions** in SITL, then in controlled flight,
  with measured intervention counts.

### Milestones / exit criteria
- [ ] A full search→investigate→report mission runs autonomously in SITL.
- [ ] Operator can override or approve at any decision point; all logged.
- [ ] Intervention rate trends down across repeated missions.

### Proof of mastery
You can express a mission as composable, gated behaviors, prove it recovers from
injected faults (GPS loss, track loss, link loss), and explain why the
LLM/VLM layer can never bypass a safety gate.

---

# YEAR 7 (2032–2033) — From One Vehicle to a Team + Distributed Systems

### Mission
Scale from a single drone to a coordinated *team*: shared world model, task
allocation, deconfliction, fleet observability.

### Why it matters at Anduril
Multi-agent coordination (collaborative autonomy across many vehicles and
sensors) is central to the product vision. The hard problems are distributed
systems problems.

### Topics to learn

**Fundamentals:**
- **Distributed systems**: consistency models, consensus, CAP, clock sync,
  message ordering, partition tolerance. (Kleppmann, *Designing Data-Intensive
  Applications*.)
- **Multi-agent systems**: task allocation (auctions, Hungarian), distributed
  coordination, conflict resolution, emergent behavior.
- **Networking**: protocols, bandwidth budgeting, mesh networking, intermittent
  connectivity, store-and-forward.

**Depth:**
- **Shared world model**: merging contacts from multiple vehicles (you have
  `swarm.py: merge_contacts`), dedup, provenance, trust.
- **Deconfliction**: spatial/temporal separation, airspace volumes, collision
  avoidance.
- **Fleet observability**: unified telemetry, per-vehicle health, mission
  replay across the team, consistent IDs and logs.

**Frontier:**
- **Decentralized autonomy**: behavior that degrades gracefully when the network
  partitions — no single point of failure.

### Concrete actions on THIS project
- Define a **fleet protocol**: how vehicles share state, contacts, and tasks
  over a constrained link.
- Implement **multi-vehicle merge + task allocation** end-to-end (extend
  `swarm.py`) and test in SITL with 2+ simulated vehicles.
- Add **deconfliction** so two vehicles never claim the same airspace/task.
- Build **fleet observability**: one console view of N vehicles, unified replay.

### Milestones / exit criteria
- [ ] Two+ simulated vehicles execute a coordinated search with shared world
      model and no task collisions.
- [ ] System degrades gracefully when a vehicle drops off the network.
- [ ] Adding a vehicle is configuration, not redesign.

### Proof of mastery
You can reason about a partition or a stale-data bug in a multi-vehicle system,
explain the consistency tradeoffs you chose, and demonstrate graceful
degradation.

---

# YEAR 8 (2033–2034) — Productize the Platform + Systems & Release Engineering

### Mission
Turn the experimental stack into a *platform*: versioned configs, release
discipline, hardware revisions, safety cases, documentation another engineer can
build from.

### Why it matters at Anduril
Elite engineers don't just build — they ship maintainable, certifiable,
team-scalable systems. This is the difference between a clever prototype and a
fielded product.

### Topics to learn

**Fundamentals:**
- **Software engineering at scale**: modular architecture, dependency
  management, API stability, deprecation, monorepo vs polyrepo tradeoffs.
- **Release engineering**: semantic versioning, reproducible builds, staged
  rollout, rollback, hardware-in-the-loop release gates.
- **Safety engineering**: failure modes (FMEA), fault trees, safety cases,
  redundancy, the discipline behind "this is safe to fly."

**Depth:**
- **Configuration management**: versioned vehicle configs, per-airframe params,
  environment separation (dev/SITL/flight/production).
- **Documentation systems**: operator manuals, runbooks, architecture decision
  records, so knowledge isn't trapped in your head.
- **Hardware revision process**: BOM versioning, change control, regression
  flights on hardware changes.

**Frontier:**
- **Certification literacy**: airworthiness, type certification concepts, what
  it takes to field a system under regulation.

### Concrete actions on THIS project
- Split **experimental vs stable** branches/configs; tag releases.
- Define **versioned vehicle configurations** and an upgrade procedure.
- Write a **safety case** for the autonomous modes (what can fail, what catches
  it, what the operator must do).
- Author **operator + maintainer docs** complete enough that someone else can
  build, deploy, and fly from scratch.

### Milestones / exit criteria
- [ ] Tagged stable release with a documented upgrade path.
- [ ] A written safety case covering every autonomous mode.
- [ ] An outside engineer (or future-you, cold) can stand up the system from
      docs alone.

### Proof of mastery
You can present a safety case and a release plan that a serious autonomy
organization would accept, and another engineer can operate your system without
your help.

---

# YEAR 9 (2034–2035) — Operational Capability + Data & Mission Products

### Mission
Make the system produce *operational output*, not just flight: structured
mission data, reports, audit trails, searchable history, decision-quality
products.

### Why it matters at Anduril
The end value of autonomy is decision-quality information delivered to operators
and commanders. Building the data products and the trustworthy record around
them is where the system becomes genuinely useful.

### Topics to learn

**Fundamentals:**
- **Data engineering**: pipelines, schemas, storage, retention, indexing,
  provenance, reproducibility.
- **Geospatial systems**: coordinate systems, projections, mapping pipelines,
  georeferencing, mosaicking.
- **Information quality**: evidence standards, chain of custody, audit trails
  (your hash-chained decision log is exactly this instinct — generalize it).

**Depth:**
- **Mission products**: structured reports, event timelines, detected-object
  catalogs, georeferenced imagery/maps.
- **Searchable flight history**: query past missions by location, object,
  event, time (extend `world_memory.py` into a real queryable store).
- **Post-mission analysis**: automated debriefs, trend analysis across missions.

**Frontier:**
- **Multi-modal fusion products**: combining EO/IR, position, and time into a
  single coherent operational picture.

### Concrete actions on THIS project
- Build a **mission report generator**: each flight emits a structured,
  georeferenced report (what was seen, where, when, with what confidence).
- Create an **event timeline + audit trail** tied to the decision chain.
- Make flight history **queryable**: "show every confirmed contact of class X
  within Y meters of this point in the last 30 days."
- Add **mapping products**: stitch flight imagery into a georeferenced mosaic.

### Milestones / exit criteria
- [ ] Every mission auto-produces a structured, auditable report.
- [ ] Flight history is queryable by location/object/event/time.
- [ ] A georeferenced map product is generated from a real flight.

### Proof of mastery
You can hand someone a mission report and an audit trail that stands up to
scrutiny — every claim traceable to evidence and a logged decision.

---

# YEAR 10 (2035–2036) — Choose Your Scale + Systems Leadership

### Mission
Decide what this becomes — product, research platform, or fleet service — freeze
a stable architecture, isolate experiments, and build the smallest process that
sustains growth.

### Why it matters at Anduril
Operating at the highest level isn't only technical — it's judgment: knowing
what to build, what to cut, how to lead a system and (eventually) a team, and
how to align engineering with a mission.

### Topics to learn

**Fundamentals:**
- **Systems leadership**: technical direction, architecture ownership,
  mentoring, design review, making and defending hard tradeoffs.
- **Program thinking**: roadmaps, risk management, dependency planning,
  resourcing, manufacturing and field-support constraints.
- **Strategy**: regulatory landscape, procurement, the economics of defense
  technology, build-vs-buy, research-vs-product.

**Depth:**
- **Architecture stewardship**: freeze the stable core, define extension points,
  isolate the experimental branch so innovation doesn't destabilize the field
  system.
- **Field support**: deployment, maintenance, updates, incident response at
  scale.

**Frontier:**
- **Research direction**: pick the one or two hard problems (e.g., fully
  decentralized GPS-denied multi-agent autonomy) you want to push the field on.

### Concrete actions on THIS project
- Write a **platform charter**: what it is, who it's for, what it will and won't
  do.
- **Freeze the stable architecture**; move all experiments behind clear
  interfaces.
- Define a **roadmap and release cadence** for the next phase.
- If pursuing a team/company/research path: build the **minimum viable process**
  (review, CI, safety, docs) that lets others contribute without breaking it.

### Milestones / exit criteria
- [ ] A written platform charter and forward roadmap.
- [ ] Stable core frozen; experimental work isolated and non-destabilizing.
- [ ] The project is a *platform with a mission*, not "a drone."

### Proof of mastery
You can stand in front of a serious autonomy organization and present the
architecture, the safety case, the roadmap, and the engineering judgment behind
every major decision — and defend all of it.

---

## The Ten-Year Arc in One Glance

| Year | Mission | Primary skill column deepened |
| ---- | ------- | ------------------------------ |
| 1 | Trustworthy aircraft + math fundamentals | Math/Estimation, Flight |
| 2 | Boring, repeatable flight + control theory | Controls/Flight Dynamics |
| 3 | Production software + learn C++ | Systems/Software Engineering |
| 4 | Reliable perception + deep learning | Perception/CV/AI |
| 5 | GPS-denied navigation + estimation mastery | Estimation/Perception |
| 6 | Mission autonomy + planning | Autonomy/Decision-making |
| 7 | One vehicle → a team + distributed systems | Fleet/C2, Systems |
| 8 | Productize the platform + release/safety eng | Systems Engineering |
| 9 | Operational data products + data engineering | Data, Autonomy/C2 |
| 10 | Choose scale + systems leadership | Leadership across all |

> **Shortest possible summary of the order of operations:** make it fly safely →
> make it fly repeatably → make the software production-grade → make it perceive
> reliably → make it navigate without GPS → make it run missions autonomously →
> make many of them cooperate → make it a maintainable platform → make it
> produce operational intelligence → decide what it becomes.

---

## Operating Principles (apply every single year)

1. **Fundamentals before frameworks.** If you can only use the API, you don't
   own it. Learn the math and the systems.
2. **Stop letting AI hide the gaps.** Use AI to go fast, then *re-derive* the
   hard parts yourself until you could rebuild them from scratch.
3. **Safety, determinism, and recovery are features**, not afterthoughts.
   Everything is gated, logged, testable, and recoverable.
4. **Write C++ (and learn Rust).** Prototype in Python; make the flight-critical
   layers real-time and native.
5. **Measure everything.** Logs, metrics, replay, post-mission analysis. You
   learn from data, not vibes.
6. **One hard thing at a time.** Don't advance a year until the exit criteria
   are genuinely met — not "mostly."
7. **Teach what you learn.** If you can explain it to another engineer and they
   can operate your system, you've mastered it.
8. **Tie every skill to the mission.** Every topic here exists because an elite
   autonomy engineer needs it to field a system that works when it matters.

---

## Curated Core Library (the books/papers worth owning)

- **Math/estimation:** Strang *Linear Algebra*; Thrun/Burgard/Fox
  *Probabilistic Robotics*; Sola *A Micro Lie Theory for State Estimation*.
- **Controls:** Åström & Murray *Feedback Systems* (free); LaValle *Planning
  Algorithms* (free).
- **Vision/AI:** Szeliski *Computer Vision* (free); Goodfellow et al. *Deep
  Learning* (free); fast.ai course.
- **Systems/C++:** Stroustrup *A Tour of C++*; Meyers *Effective Modern C++*;
  Bryant & O'Hallaron *Computer Systems: A Programmer's Perspective*.
- **Distributed/scale:** Kleppmann *Designing Data-Intensive Applications*.
- **Key papers:** ORB-SLAM, VINS-Mono (VIO); SORT/ByteTrack/BoT-SORT
  (tracking); the PX4/EKF2 documentation (state estimation in your actual
  autopilot).

---

*This plan is intentionally demanding. Operating at an elite level at a company
like Anduril is not a framework you install — it is fundamentals you own,
systems you can defend, and judgment you earn by building, breaking, and fixing
real autonomous machines. You already have the machine. Now go own every layer
of it.*

---

## Sources & Citations

The per-year reading is embedded above; this consolidates the core library and
adds the authoritative primary sources.

**Math & estimation**
- Strang, G. — *Introduction to Linear Algebra*, Wellesley-Cambridge.
- Wasserman, L. — *All of Statistics*, Springer.
- Boyd & Vandenberghe — *Convex Optimization* (free): https://web.stanford.edu/~boyd/cvxbook/
- Thrun, Burgard & Fox — *Probabilistic Robotics*, MIT Press.
- Sola et al. — *A micro Lie theory for state estimation* (arXiv:1812.01537).

**Controls & planning**
- Åström & Murray — *Feedback Systems* (free): https://fbswiki.org
- LaValle — *Planning Algorithms* (free): http://lavalle.pl/planning/
- Sutton & Barto — *Reinforcement Learning* (free): http://incompleteideas.net/book/the-book.html

**Vision & AI**
- Szeliski — *Computer Vision: Algorithms and Applications* (free): https://szeliski.org/Book/
- Goodfellow, Bengio & Courville — *Deep Learning* (free): https://www.deeplearningbook.org
- fast.ai practical course: https://course.fast.ai

**Systems & C++**
- Stroustrup — *A Tour of C++*; Meyers — *Effective Modern C++*.
- Bryant & O'Hallaron — *Computer Systems: A Programmer's Perspective*.
- Kleppmann — *Designing Data-Intensive Applications*, O'Reilly.

**Key papers & docs**
- Mur-Artal et al. — *ORB-SLAM*; Qin et al. — *VINS-Mono* (VIO).
- Bewley et al. — *SORT*; Zhang et al. — *ByteTrack* (tracking).
- PX4 / ECL-EKF2 docs: https://docs.px4.io

*This is a personal development plan; company-specific framing reflects the
author's goals and publicly available information about the named companies.*
