# Module 06 — Simulation, Test & Verification

> **Why this file exists.** Anyone can make a drone fly *once*, in good weather, with a
> charged battery and a clear sky. The thing that separates a hobbyist from an engineer at
> Anduril, Shield AI, or Skydio is the ability to **prove a system works before it flies** —
> and to prove it keeps working after every change. That proof is not a feeling. It is a
> stack of simulations, tests, and verification arguments that each name a specific failure
> mode and demonstrate the system survives it. This is the module the demo videos never
> show, and it is *the real moat*. A flashy autonomy capability that nobody can verify is a
> liability; a boring capability with an airtight verification story is a product.
>
> **What mastering it makes you.** The engineer the team trusts to say "yes, this is safe to
> fly" — and to be *right*. You will be able to take a vague requirement, decompose it into
> testable claims, build the simulation and test infrastructure that exercises those claims,
> and wire it into CI so that the proof is *continuous*, not a one-time heroic effort. That
> skill is rarer and more valuable than writing the autonomy code in the first place.

**Companion code.** This module is anchored to the real test infrastructure in this
repository's `drone/` autonomy stack: the `drone/test/` scaffold (see
[24-autonomy-test-scaffold.md](24-autonomy-test-scaffold.md)), the PX4 SITL flow (see
[22-autonomy-px4-sitl.md](22-autonomy-px4-sitl.md)), the FastAPI onboard service
(`onboard/server.py`), the constitution-gated command policy (`policy/constitution.py`),
the hash-chained decision log (`policy/decisions.py`), the navigation filters, and the
`.ulog` flight logs PX4 writes. Every abstract idea below ties to something you can open,
run, and break on purpose.

---

## Table of Contents

1. [Why verification is the moat](#1-why-verification-is-the-moat)
2. [The vocabulary: V&V, the V-model, and what "done" means](#2-the-vocabulary-vv-the-v-model-and-what-done-means)
3. [The test pyramid for an autonomy stack](#3-the-test-pyramid-for-an-autonomy-stack)
4. [Simulation fidelity: SIL, SITL, HITL, and the reality gap](#4-simulation-fidelity-sil-sitl-hitl-and-the-reality-gap)
5. [PX4 SITL and Gazebo in practice](#5-px4-sitl-and-gazebo-in-practice)
6. [Deterministic replay from `.ulog`](#6-deterministic-replay-from-ulog)
7. [Property-based testing with Hypothesis](#7-property-based-testing-with-hypothesis)
8. [Fault injection: testing the unhappy path](#8-fault-injection-testing-the-unhappy-path)
9. [Estimator verification: NEES & NIS consistency](#9-estimator-verification-nees--nis-consistency)
10. [CI for autonomy & regression gates](#10-ci-for-autonomy--regression-gates)
11. [Coverage vs risk: where to spend your tests](#11-coverage-vs-risk-where-to-spend-your-tests)
12. [Writing a test that names its failure mode](#12-writing-a-test-that-names-its-failure-mode)
13. [Capability ladder & practice this week](#13-capability-ladder--practice-this-week)
14. [Sources & Citations](#sources--citations)

---

## 1. Why verification is the moat

Start with the economics, because they explain everything that follows.

A defense autonomy product is sold on **trust**, not features. The customer — a program
office, a unit, a pilot who will be standing under the thing when it transitions — does not
buy "the drone can do X." They buy "the drone does X reliably, and here is the evidence."
The evidence *is* the product. Two companies can ship the same capability; the one that can
hand a safety officer a verification dossier wins the program, and the one that can't is a
science fair project.

This inverts the hobbyist instinct. As a hobbyist you optimize for **time-to-first-flight**.
As an engineer you optimize for **time-to-trustworthy** — and trustworthy is a function of
how cheaply you can re-prove the system after every change. The teams that move fastest in
defense autonomy are not the ones that skip testing; they are the ones whose testing is so
automated that they can change anything and know within minutes whether they broke it.

```
   Hobbyist loop                         Engineer loop
   ─────────────                         ─────────────
   idea → code → fly → "it worked!"      idea → testable claim → test (red)
        ↑___________|                          → code → test (green) → SITL
        (no memory of what                     → fault-inject → CI gate
         used to work)                         → fly → log → replay → CI gate
                                               (every past guarantee is re-checked
                                                automatically, forever)
```

The right mental model: **a test suite is institutional memory for correctness.** Every
test is a sentence that says "we once decided this must be true, and here is the machine
that re-checks it for us so we never have to remember." A team without that memory
re-discovers the same bugs every few weeks; a team with it accrues guarantees.

> **Senior tell.** Juniors ask "does it work?" Seniors ask "what would have to be true for
> me to *believe* it works, and which of those things do I currently have evidence for?"
> The gap between those two questions is this entire module.

### 1.1 The three things verification buys you

1. **Confidence to change.** A good suite means refactoring the navigation filter or the
   command gate is a normal Tuesday, not a gamble. Velocity comes from safety nets.
2. **A truthful map of risk.** When something *isn't* tested, you know it, and you can
   decide consciously whether that's acceptable for this flight. Untested ≠ broken, but
   untested = unknown, and unknown is the thing that kills airframes and people.
3. **A sellable assurance story.** This connects directly to safety cases
   ([09-foundations-safety-assurance.md](09-foundations-safety-assurance.md)) and to why
   the company wins ([08-foundations-company-strategy-moat.md](08-foundations-company-strategy-moat.md)).
   The same tests that protect you internally become evidence externally.

---

## 2. The vocabulary: V&V, the V-model, and what "done" means

Precision in language prevents whole categories of error. Three terms get conflated; keep
them distinct.

| Term | Question it answers | Example in this stack |
|---|---|---|
| **Verification** | "Did we build the thing right?" (matches spec) | The transition timeout clamp triggers at exactly 8 s as specified |
| **Validation** | "Did we build the right thing?" (matches need) | The 8 s timeout is actually the right value for *this* airframe's transition |
| **Test** | A single repeatable experiment producing pass/fail | `test_transition_timeout_aborts()` |

Verification is *internal* — you check the artifact against its requirement. Validation is
*external* — you check the requirement against reality and the mission. You can verify a
wrong system perfectly (it does exactly what the wrong spec said). Both matter. Most
software testing energy goes to verification; the validation gap is where systems
engineering ([01_first_principles_systems_engineering.md](01_first_principles_systems_engineering.md))
earns its keep.

### 2.1 The V-model — requirements decompose, tests recompose

The V-model is the cleanest picture of how verification *should* be planned. The left arm
decomposes the system into ever-smaller pieces; the right arm reassembles it, and **each
level on the right verifies the corresponding level on the left.**

```
  Mission need ───────────────────────────────► Acceptance test / flight demo
     │   (ConOps: "find and track a moving       (operator flies the real mission,
     │    ground contact in GPS-denied area")     it works end-to-end)
     ▼                                                        ▲
  System requirements ──────────────────────► System integration test
     │   ("hold track for 30 s through a          (full onboard service ↔ SITL,
     │    20 s GPS dropout")                        all subsystems wired together)
     ▼                                                        ▲
  Subsystem design ─────────────────────────► Subsystem / integration test
     │   (track fusion module, nav filter,        (fusion ↔ filter ↔ world memory,
     │    world memory)                             real interfaces, fake hardware)
     ▼                                                        ▲
  Unit design ──────────────────────────────► Unit test
         (gating function, waypoint validator,    (pure-logic pytest, no hardware)
          NIS computation)
```

The discipline this enforces: **before you write a requirement, you write down how you will
verify it.** A requirement you cannot test is not a requirement — it is a wish. "The system
shall be robust to GPS loss" is a wish. "The system shall maintain position estimate with
≤ 5 m drift for ≥ 20 s after total GPS loss, verified in SITL with the GPS module disabled"
is a requirement, because the verification method is baked in.

### 2.2 Definition of done for a capability

A capability in this stack is "done" only when **all** of these exist:

- [ ] Unit tests for the pure logic (validators, math, gating decisions).
- [ ] Integration tests through SITL for the wiring.
- [ ] At least one fault-injection test for the dominant failure mode.
- [ ] A deterministic replay test if it consumes flight data.
- [ ] A line in the decision log (`policy/decisions.py`) so the behavior is observable in flight.
- [ ] An exploratory charter run by a human, with notes.
- [ ] It is in CI and the gate is green.

Notice "it flew once" is not on the list. Flight is *evidence*, not *proof*. One flight is
a single sample from a distribution you don't understand yet.

---

## 3. The test pyramid for an autonomy stack

The test pyramid is the single most important structural idea in testing. It says: **have
many fast, cheap, narrow tests at the bottom; fewer slow, expensive, broad tests at the
top.** Inverting it — relying mostly on end-to-end flights — is the classic failure: slow
feedback, flaky results, and no idea *which* component broke when the whole mission fails.

This repository's `drone/test/` directory implements exactly this pyramid (see
[24-autonomy-test-scaffold.md](24-autonomy-test-scaffold.md)):

```
                         ▲  slower, broader, fewer, more "real"
            ┌───────────────────────────┐
            │      exploratory/         │   human charters: "GPS loss mid-mission,"
            │   (operator charters)     │   "transition brownout" — finds the unknown
            ├───────────────────────────┤
            │      acceptance/          │   operator-POV end-to-end: the mission as the
            │  (mission-level, SITL)    │   ground station sees it; ABORT-free vtol_demo
            ├───────────────────────────┤
            │     integration/          │   onboard service ↔ PX4 SITL ↔ MAVSDK;
            │   (wiring, needs SITL)    │   /api/state connected=true; interfaces real
            ├───────────────────────────┤
            │         unit/             │   pure logic, venv only: auth, waypoint
            │   (pytest, no hardware)   │   validation, mission math, JPEG framing,
            └───────────────────────────┘   telemetry shaping, gating decisions
                         ▼  faster, narrower, many, fully deterministic
```

### 3.1 The four layers, by what they prove and what they cost

| Layer | Proves | Needs | Speed | Determinism | Where it lives |
|---|---|---|---|---|---|
| **Unit** | Logic is correct in isolation | venv only | ms | Total | `drone/test/unit/` |
| **Integration** | Components are wired correctly | PX4 SITL | seconds | High | `drone/test/integration/` |
| **Acceptance** | The mission works for the operator | SITL + UI | minutes | Medium | `drone/test/acceptance/` |
| **Exploratory** | The unknown-unknowns | A human, the system | hours | None (by design) | `drone/test/exploratory/` |

The trap everyone falls into: writing too many *integration* tests because they "feel more
real." They are slower, flakier (anything touching a network or a simulator can hang), and
when they fail they tell you *that* something broke, not *what*. A unit test failure points
at one function. Push logic down the pyramid until only genuinely-cross-component behavior
needs the higher layers.

### 3.2 Why exploratory testing is non-negotiable for autonomy

Scripted tests can only check the failure modes you already imagined. Autonomy fails in
ways nobody scripted — the emergent interaction of a GPS dropout *during* a VTOL transition
*while* the link is degraded. **Exploratory testing** is structured human improvisation: an
operator takes a *charter* ("spend 60 minutes trying to make the drone lose track during a
transition") and pokes the system creatively, taking notes. It is how you discover the
test you should have written. Every good exploratory finding becomes a new scripted test at
the appropriate pyramid layer — that's the ratchet: humans find the novel failure once, the
machine guards it forever.

> **Anchor.** The author's `drone/test/exploratory/` holds free-form charters exactly like
> "GPS loss mid-mission" and "transition brownout." These are not afterthoughts; they are
> the intake funnel for the rest of the pyramid.

---

## 4. Simulation fidelity: SIL, SITL, HITL, and the reality gap

Simulation exists so you can test the dangerous and the rare cheaply and repeatedly. The
key question for any simulation is always: **what is it faithful to, and what is it lying
about?** A simulation is a model, and all models are wrong; the discipline is knowing the
specific ways yours is wrong so you don't trust it past its limits.

### 4.1 The fidelity ladder

```
  Fidelity  ┌──────────────────────────────────────────────────────────┐  Cost / realism
    low      │ Model-in-the-loop (MIL): test the algorithm as math      │     low
     │       │   e.g. run the EKF on synthetic IMU data in a notebook   │      │
     │       ├──────────────────────────────────────────────────────────┤      │
     │       │ Software-in-the-loop (SIL/SITL): real FLIGHT CODE runs    │      │
     │       │   as a process; physics simulated (PX4 + Gazebo)         │      │
     │       ├──────────────────────────────────────────────────────────┤      │
     │       │ Hardware-in-the-loop (HITL): real AUTOPILOT BOARD runs    │      │
     │       │   firmware; sim feeds it sensor data over the wire       │      │
     │       ├──────────────────────────────────────────────────────────┤      │
     ▼       │ Iron bird / bench: real actuators, real wiring, no flight │     high
    high     │ Captive carry / tethered: real airframe, constrained      │      │
             │ Flight test: the real thing, in the real world            │      ▼
             └──────────────────────────────────────────────────────────┘
```

Each rung trades cost and risk for realism. The skill is **using the lowest rung that can
falsify the claim you care about.** Testing your task-allocation logic? That's pure math —
MIL/unit, no simulator needed. Testing whether the onboard service correctly commands a
transition? That needs the real flight stack — SITL. Testing whether the Pi 5 can keep up
with the control loop under thermal load? That needs hardware — HITL or bench.

### 4.2 SIL / SITL — your daily driver

**Software-in-the-loop** runs the *actual flight software* (PX4 firmware compiled for the
host, plus your onboard service) as ordinary processes, with a physics engine standing in
for the airframe and the world. This is the workhorse because:

- It exercises the **real code paths** — the same MAVLink messages, the same state machine,
  the same transition logic that runs on the Pixhawk.
- It is **cheap and repeatable** — no battery, no props, no risk, no weather.
- It runs in **CI** — every commit can fly the mission.

What SITL lies about: timing jitter, real sensor noise spectra, EMI, vibration, thermal
behavior, prop wash, and the thousand analog realities of an actual airframe. So SITL
proves *logic and wiring*, never *flight-worthiness*. A green SITL run is a necessary
condition for flight, never a sufficient one.

### 4.3 HITL — closing the timing gap

**Hardware-in-the-loop** flashes real firmware onto the real Pixhawk 6C and feeds it
simulated sensor data while reading its real actuator outputs. This catches what SITL
can't: does the *actual board*, with its *actual clock and scheduler*, meet timing under
load? HITL is more expensive to set up and slower, so you use it for a smaller set of
claims — specifically anything where the *hardware's* real-time behavior is the thing under
test. For this stack, HITL is the bridge between "passes SITL on my laptop" and "won't
brown out the flight controller during a transition on the real Pi+Pixhawk pair."

### 4.4 The reality gap (sim-to-real) — name it explicitly

The **reality gap** is the difference between simulation and the world. It is where
autonomy that "worked in sim" dies on the range. You manage it by:

1. **Knowing which claims cross the gap.** Logic and protocol claims (does the gate fire?)
   barely cross it. Perception and dynamics claims (does the IMX500 detector hold a track
   in real glare? does the controller stay stable with real prop flex?) cross it hard.
2. **Domain randomization** for anything learned. If a model trained only on clean sim
   imagery, it will fail on the real sensor. Randomize lighting, noise, blur, and texture
   in sim so the model learns the *invariant*, not the sim's quirks. (See the perception
   work in [20-autonomy-ml-ai.md](20-autonomy-ml-ai.md).)
3. **Anchoring sim to logs.** Replay real `.ulog` data through the algorithms (Section 6)
   so at least some of your "simulation" is literally recorded reality.

> **The honest sentence to keep on a sticky note:** *Simulation lets me fail a thousand
> times for free, but it cannot tell me the one way the real world will surprise me. It
> shrinks the unknown; it does not eliminate it.*

---

## 5. PX4 SITL and Gazebo in practice

This section grounds the abstractions in the exact flow this repo uses (full detail in
[22-autonomy-px4-sitl.md](22-autonomy-px4-sitl.md)).

### 5.1 The loop

```
   ┌────────────────┐     MAVLink UDP :14540      ┌──────────────────────┐
   │  PX4 SITL      │◄───────────────────────────►│ onboard/server.py    │
   │  (real firmware│                              │ (FastAPI + MAVSDK)   │
   │   as a process)│     MAVLink UDP :14550       │  your autonomy code  │
   │       ▲        │◄──────────────┐              └──────────────────────┘
   │       │        │               │                        ▲
   │   physics      │               ▼                        │ WebSocket /telemetry
   │   ┌─────────┐  │      ┌──────────────────┐               ▼
   │   │ Gazebo  │  │      │ GCS (QGroundCtl) │      ┌──────────────────────┐
   │   │ Garden  │  │      └──────────────────┘      │ ground-station UI    │
   │   │tiltrotor│  │                                │ (operator's view)    │
   │   └─────────┘  │                                └──────────────────────┘
   └────────────────┘
```

The same firmware that will run on the Pixhawk runs here as a process. Gazebo Garden
provides VTOL physics. Port `14540` carries offboard/onboard control (your service); `14550`
feeds the GCS. The acceptance criterion for Stage 1 is precise and testable: the onboard
service reaches SITL, `/api/state` reports `connected=true`, and the `vtol_demo` mission
completes without an `ABORT`.

### 5.2 Why the VTOL is the hard case

The airframe is a **3-motor tilt-tricopter** (two front tilt motors + one rear lift motor +
V-tail) — not a stock PX4 VTOL geometry (those assume four motors). For Stage 1 the repo
uses PX4's stock `gz_tiltrotor` as the closest stand-in because the goal at that stage is to
exercise the **transition state machine, mission upload, and GCS path end-to-end**, not to
model the exact airframe. This is a textbook fidelity decision: pick the lowest-fidelity
model that still exercises the claim under test (the transition logic), and defer the
airframe-accurate SDF + params to a later stage when the claim becomes "does *this* airframe
transition correctly."

### 5.3 What to test at each SITL stage

| Stage | Claim under test | Test |
|---|---|---|
| Connectivity | Service ↔ SITL link works | `/api/state` → `connected=true` |
| Mission | Upload + execute completes | `vtol_demo` ends without `ABORT` |
| Transition | MC→FW and FW→MC transitions complete | assert mode + airspeed envelope |
| Failsafe | Link loss triggers correct action | inject loss, assert RTL/loiter |
| GPS-denied | Estimate survives dropout | disable GPS, assert drift bound |

---

## 6. Deterministic replay from `.ulog`

PX4 writes a binary **`.ulog`** flight log containing every subscribed message — IMU, GPS,
estimator state, setpoints, commands — timestamped. This is gold for verification, because
it lets you do something flight test alone can't: **replay reality through your code,
deterministically, as many times as you want.**

### 6.1 The principle: separate the world from the algorithm

The core trick is architectural. If your navigation filter or track-fusion module is
written as a **pure function of its inputs** — "given this sequence of measurements, produce
this sequence of estimates" — then you can feed it a recorded `.ulog` and get *bit-identical*
output every time. No simulator, no hardware, no randomness. A bug that only appeared on
flight 47 becomes a regression test you run in 40 ms.

```
   ┌─────────────┐    parsed messages      ┌──────────────────┐    estimates
   │ flight.ulog │ ──────────────────────► │ nav filter /     │ ───────────────►  assert
   │ (recorded   │   (IMU, GPS, baro,      │ track fusion     │   (compare to     against
   │   reality)  │    timestamps)          │ (pure function)  │    golden output)  golden
   └─────────────┘                         └──────────────────┘
```

### 6.2 Why determinism is the whole game

A test you can't reproduce is not a test — it's a rumor. Sources of non-determinism that
will ruin you and how to kill them:

- **Wall-clock time** → inject a clock; never call `time.now()` inside testable logic. Drive
  time from the log's timestamps.
- **Threading / async races** → make the core estimator single-threaded and synchronous;
  push concurrency to the edges (the FastAPI layer), not the math.
- **Floating-point order** → pin it. Same input order → same output. Avoid set/dict
  iteration order leaking into numeric results.
- **Random seeds** → seed everything; log the seed.

> **Anchor.** When the author's nav pipeline drops a track or the filter diverges in a real
> flight, the fix workflow is: pull the `.ulog`, find the moment, build a replay test that
> reproduces the divergence, fix the code until the replay is clean, and *keep the test
> forever*. That is the difference between "I think I fixed it" and "I proved I fixed it and
> it can't silently come back."

### 6.3 Golden-file testing and its trap

Replay tests often compare output to a stored "golden" file. The trap: when you change the
filter intentionally, the golden file must change too, and a sloppy team just regenerates
it blindly — which silently accepts regressions. The discipline: when a golden file changes,
a **human reviews the diff** and confirms the new behavior is *intended and better*. Golden
files are only as good as the review of their updates.

---

## 7. Property-based testing with Hypothesis

Example-based tests check specific inputs you thought of. **Property-based tests** check a
*property* that must hold for *all* inputs in a range, and the framework (Hypothesis, in
Python) generates hundreds of inputs trying to break it — including the nasty edge cases you
would never have typed by hand (empty lists, NaNs, the exact integer boundary, zero-length
missions).

### 7.1 From examples to properties

```python
# Example-based: checks the cases you imagined.
def test_clamp_examples():
    assert clamp_altitude(150) == 120     # over max
    assert clamp_altitude(-5)  == 0       # under min
    assert clamp_altitude(50)  == 50      # passthrough

# Property-based: checks an invariant for EVERYTHING in range.
from hypothesis import given, strategies as st

@given(st.floats(allow_nan=False, allow_infinity=False))
def test_clamp_output_is_always_in_bounds(alt):
    """The clamp's whole job: output is ALWAYS within [MIN_ALT, MAX_ALT].
    Defends against: any input — finite, negative, huge — escaping the geofence
    altitude envelope. Hypothesis will hunt for the value that breaks this."""
    out = clamp_altitude(alt)
    assert MIN_ALT <= out <= MAX_ALT
```

The property test is strictly stronger: it asserts the *contract* of the function, not three
points on it. When it fails, Hypothesis **shrinks** the failing input to the minimal example
(e.g., it won't report `1.7976e308`; it reports the smallest value that still breaks it),
which usually points straight at the bug.

### 7.2 Properties worth asserting in this stack

| Module | Property |
|---|---|
| Waypoint validator | Any accepted mission is inside the geofence and within count/spacing limits |
| Altitude/airspeed clamp | Output always within the envelope, for all finite inputs |
| Track fusion | Number of fused tracks ≤ number of input contacts; no track has NaN state |
| Constitution gate | A denied command never produces an executed action (round-trip invariant) |
| Decision log | The hash chain always verifies after any sequence of appends (Section 10.3) |
| Telemetry shaping | Serialized telemetry always round-trips back to equal values |

### 7.3 Metamorphic properties — when there's no oracle

Sometimes you can't state the *right* answer (what *exactly* should the EKF output be?), but
you can state a relationship that must hold. **Metamorphic testing**: if you rotate the whole
input frame by 90°, the estimated trajectory should rotate by 90° too. If you scale all
distances by 2, the fused-track geometry should scale by 2. These relational properties
catch deep bugs without ever needing the ground-truth answer — invaluable for perception and
estimation where the "correct" output is itself unknown.

---

## 8. Fault injection: testing the unhappy path

Most code is written for the happy path and dies on the unhappy one. **Fault injection** is
the deliberate practice of breaking inputs, links, and subsystems *on purpose* to verify the
system degrades the way you designed it to — not the way the laws of probability eventually
discover for you, in flight, over a populated area.

This is the highest-leverage testing you can do for autonomy, because in the field the
faults are not hypothetical. GPS *will* drop in an urban canyon or under jamming (see
[27-autonomy-counter-uas-ew.md](27-autonomy-counter-uas-ew.md)). The link *will* die. The
transition *will* sometimes brown out. The only question is whether your system has rehearsed
its response.

### 8.1 The fault catalog for this airframe

| Fault | How to inject (SITL) | Required behavior | Test asserts |
|---|---|---|---|
| **GPS loss** | Disable GPS module / corrupt fix | Switch to dead-reckon / vision nav, bound drift, warn operator | Estimate drift ≤ bound for ≥ N s; mode flag set; decision logged |
| **Link loss** | Drop `14550` (GCS) traffic | Enter failsafe (RTL/loiter per policy), keep flying the gate locally | Failsafe entered within timeout; no command from dead link executed |
| **Transition brownout** | Throttle/voltage sag during MC↔FW | Abort transition safely, return to stable mode | Transition aborts; airframe in known-stable mode; ABORT logged |
| **Sensor spike / NaN** | Inject NaN / out-of-range IMU | Reject sample, don't poison the filter | Filter state stays finite; bad sample rejected, not fused |
| **Command flood** | Spam offboard setpoints | Rate-limit; gate still enforces envelope | No envelope violation; gate denials logged |
| **Clock jump** | Skew timestamps | Detect, don't integrate garbage | No NaN; estimator flags time anomaly |

### 8.2 The structure of a good fault-injection test

```python
def test_gps_loss_midmission_bounds_drift_and_warns():
    """FAILURE MODE DEFENDED: total GPS loss mid-mission must NOT silently
    corrupt the position estimate. The drone must fall back to dead reckoning,
    keep drift within the spec bound for the dropout window, raise the operator
    warning, and write a decision-log entry. Inspired by the exploratory charter
    'GPS loss mid-mission'."""
    sim = start_sitl_with_mission("vtol_demo")
    sim.fly_until(phase="cruise")

    sim.inject_fault(GPS_TOTAL_LOSS)          # the unhappy path, on purpose
    drift = sim.measure_drift(window_s=20)

    assert drift.max <= GPS_DENIED_DRIFT_BOUND_M     # estimate stays usable
    assert sim.operator_warnings.contains("GPS_DEGRADED")
    assert decision_log.last().event == "NAV_FALLBACK_DEAD_RECKON"
    assert decision_log.verify_chain()               # log integrity intact
```

Notice the docstring **names the failure mode first**. That is the rule (Section 12). Notice
also that the test ties three subsystems together — nav fallback, operator warning, decision
log — because the *required behavior* is a system-level contract, not a single function's.

### 8.3 Chaos for robotics

The cloud world calls deliberate production fault-injection **chaos engineering** (kill a
server at random, see if the system survives). The robotics analog: in a SITL soak test,
randomly inject faults from the catalog and assert the system never enters an unsafe state.
This finds the *combinations* — GPS loss *and* link loss *during* a transition — that no
single scripted test covers. The acceptance criterion isn't "it completes the mission"; it's
"it never violates a safety invariant, no matter what we throw at it."

---

## 9. Estimator verification: NEES & NIS consistency

Estimators (the EKF/UKF in your nav stack) are special: their output isn't just a number,
it's a number *plus a claimed uncertainty* (the covariance). A filter can be confidently
wrong — reporting a tight covariance while being far off — and that is the most dangerous
failure of all, because everything downstream *trusts* the covariance. Verifying an
estimator means verifying that its claimed uncertainty matches its actual error. Two
statistical tests do this.

### 9.1 NEES — Normalized Estimation Error Squared (needs ground truth)

In SITL you *have* ground truth (the simulator knows the true state). NEES measures whether
the estimation error is consistent with the reported covariance:

$$
\epsilon_k = (\mathbf{x}_k - \hat{\mathbf{x}}_k)^\top \mathbf{P}_k^{-1} (\mathbf{x}_k - \hat{\mathbf{x}}_k)
$$

If the filter is consistent, $\epsilon_k$ follows a chi-squared distribution with $n$ degrees
of freedom (n = state dimension), so its average over many runs should sit near $n$. The
interpretation is a tuning diagnosis:

- **Average NEES ≈ n** → consistent. The filter knows how unsure it is. 
- **Average NEES ≫ n** → *overconfident*. Covariance too small; the filter believes itself
  more than it should. Dangerous: downstream code under-hedges.
- **Average NEES ≪ n** → *underconfident / conservative*. Covariance too large; the filter
  is sluggish and throws away good information.

### 9.2 NIS — Normalized Innovation Squared (no ground truth needed)

In real flight you *don't* have ground truth, but you have the **innovation** — the
difference between the measurement and what the filter predicted — and its covariance $S_k$:

$$
\nu_k = \tilde{\mathbf{y}}_k^\top \mathbf{S}_k^{-1} \tilde{\mathbf{y}}_k
$$

NIS also follows chi-squared (df = measurement dimension). This is the **only** consistency
check you can run on real `.ulog` data, which makes it the bridge between SITL verification
and flight verification: tune with NEES in sim where you have truth, then **monitor NIS in
flight** to confirm the filter stays consistent against the real sensor noise the sim
couldn't reproduce. A NIS that suddenly spikes in flight is an early warning that the filter
is diverging — a run-time health signal, not just a test.

### 9.3 As a regression gate

Both metrics become CI gates: run the filter over a battery of SITL scenarios and the golden
`.ulog` replays, compute average NEES/NIS, and **fail the build if they leave their
chi-squared confidence bounds.** This catches the silent killer — a "small" change to the
process-noise tuning that makes the filter overconfident — before it ever flies. (Estimator
theory lives in [28-autonomy-gnc.md](28-autonomy-gnc.md); here we only verify it.)

---

## 10. CI for autonomy & regression gates

Continuous Integration is what turns a pile of tests into *continuous proof*. Every push
runs the suite automatically; a red build blocks the merge. The whole point: **no change
reaches the airframe without re-proving every guarantee you've accumulated.**

### 10.1 The pipeline, staged by cost

You stage CI by the pyramid so feedback is fast where it can be and thorough where it must
be:

```
  push / PR
    │
    ▼
  ┌──────────────┐  fail fast: seconds
  │ lint + types │  ruff / mypy — catch the typos and type errors first
  └──────┬───────┘
         ▼
  ┌──────────────┐  unit tests: tens of seconds
  │ unit/        │  pure logic, no hardware, runs on any laptop
  └──────┬───────┘
         ▼
  ┌──────────────┐  property + replay: a minute
  │ hypothesis + │  golden .ulog regression, NEES/NIS gates
  │ ulog replay  │
  └──────┬───────┘
         ▼
  ┌──────────────┐  integration: minutes, needs SITL in the runner
  │ PX4 SITL     │  vtol_demo completes, /api/state connected, failsafe checks
  └──────┬───────┘
         ▼
  ┌──────────────┐  nightly / pre-release only: slow soak + fault-injection chaos
  │ soak + chaos │  hours; not on every PR
  └──────────────┘
```

The cheap stages gate the expensive ones: don't burn ten minutes of SITL on a PR that fails
`mypy` in two seconds.

### 10.2 What makes autonomy CI hard (and how to handle it)

| Problem | Why it's worse for autonomy | Mitigation |
|---|---|---|
| **Flakiness** | SITL/sim involves timing, networking, async — non-determinism leaks in | Quarantine flaky tests; fix root cause (Section 6.2); never "retry until green" |
| **Slow E2E** | A full mission takes real wall-clock minutes | Push logic to unit/property layers; run E2E nightly, not per-PR |
| **Sim in CI** | Gazebo is heavy; runners may lack a GPU | Headless SITL; pin the model; cache the PX4 build |
| **Nondeterminism** | Floating point, threads, clocks | Inject clocks, single-thread the math, seed RNG, pin FP order |

> **Hard rule: never normalize a retry.** The instant the team accepts "just re-run it, it's
> flaky," CI stops being proof and becomes theater. A flaky test is a bug — in the test or in
> the code — and it must be fixed or quarantined, never silently retried into green.

### 10.3 The decision-log integrity gate — a worked example

The hash-chained decision log (`policy/decisions.py`) is tamper-evident: each entry includes
a hash of the previous entry, so any alteration breaks the chain. This is a *security and
forensics* property (it's how you prove after an incident what the autonomy actually decided
and why). It is also trivially testable, and it belongs in CI as a hard gate:

```python
@given(st.lists(decision_entries(), min_size=0, max_size=200))
def test_decision_log_chain_always_verifies(entries):
    """FAILURE MODE DEFENDED: a corrupted or reordered decision log would
    destroy the forensic/airworthiness audit trail and let a tampered command
    history pass as genuine. The hash chain MUST verify after ANY sequence of
    appends, and MUST fail if any entry is mutated."""
    log = DecisionLog()
    for e in entries:
        log.append(e)
    assert log.verify_chain()                  # honest history verifies

    if entries:                                # tampering is always detected
        log.tamper_with_random_entry()
        assert not log.verify_chain()
```

This single property — verify after any append sequence, fail under any tamper — is exactly
the kind of high-value invariant that justifies property-based testing: it covers an infinite
input space with one statement, and it directly underwrites the assurance argument in
[09-foundations-safety-assurance.md](09-foundations-safety-assurance.md) and the moat in
[08-foundations-company-strategy-moat.md](08-foundations-company-strategy-moat.md).

---

## 11. Coverage vs risk: where to spend your tests

Code coverage (the % of lines a test suite executes) is a **seductive and dangerous**
metric. 100% coverage means every line ran during testing; it does **not** mean every line
is *correct*, that the right *assertions* were made, or that the dangerous *combinations*
were exercised. You can hit 100% coverage with tests that assert nothing.

### 11.1 Coverage is a floor, not a goal

Use coverage to find the **untested** code (a line that never runs in any test is a blind
spot you should know about), not to declare victory. The right question is never "what's our
coverage?" It is "**what's the worst thing that can happen, and is it tested?**" Those two
questions point at completely different code. The worst-case code in this stack — the command
gate, the geofence, the failsafe, the transition abort — must be tested to *exhaustion*; the
telemetry-formatting helper can survive on a few unit tests.

### 11.2 Risk-based prioritization

Rank what to test by **(probability of failure) × (consequence of failure)**:

```
   consequence
   (severity)
      high │  ┌──────────────┐   ┌──────────────────────────┐
           │  │ rare but     │   │ TEST TO EXHAUSTION        │
           │  │ catastrophic │   │ command gate, geofence,   │
           │  │ — still test │   │ failsafe, transition abort│
           │  └──────────────┘   └──────────────────────────┘
           │  ┌──────────────┐   ┌──────────────────────────┐
       low │  │ ignore /     │   │ test enough to not annoy  │
           │  │ accept       │   │ users (telemetry format)  │
           │  └──────────────┘   └──────────────────────────┘
           └──────────────────────────────────────────────────
                   low                      high
                          probability of failure
```

The top-left quadrant is the one juniors skip and seniors obsess over: **rare but
catastrophic.** A GPS-loss-during-transition is rare — and it can lose the airframe. Rarity is
not a reason to skip it; it's the reason it's never been debugged in the field, which is
exactly why your test has to be the thing that catches it.

### 11.3 Mutation testing — testing your tests

The deepest coverage question is "are my *assertions* any good?" **Mutation testing**
deliberately introduces bugs into your code (flips a `<` to `<=`, changes a `+` to `-`) and
checks whether your tests *catch* the mutation. If a mutant survives — your tests still pass
with the bug in place — your tests are weak there, regardless of coverage. It is expensive but
illuminating to run periodically on the safety-critical core (the gate, the validators).

---

## 12. Writing a test that names its failure mode

This is the single most important *cultural* habit in this module, and it is the explicit
philosophy of the author's `drone/test/` scaffold: **every test names the failure mode it
defends against, at the top of the file or the top of the test.**

### 12.1 Why naming the failure mode matters

A test named `test_waypoint_2()` is a liability. When it fails in CI at 2 a.m., the on-call
engineer has no idea what guarantee just broke or whether it matters. A test whose docstring
says *"defends against: a mission with a waypoint outside the geofence being accepted and
flown"* tells the reader, instantly, **what real-world bad outcome this test exists to
prevent.** The test becomes self-documenting risk management. The name is for the machine;
the failure-mode statement is for the human who has to act when it goes red.

### 12.2 The template

```python
def test_<behavior>_<condition>():
    """FAILURE MODE DEFENDED: <the specific bad thing that happens in the real
    world if this guarantee breaks — concrete, operational, scary>.

    GIVEN  <starting condition / setup>
    WHEN   <the action or injected fault>
    THEN   <the required, testable behavior>

    Source: <exploratory charter / .ulog flight N / requirement REQ-xyz>"""
    ...
```

### 12.3 Good vs bad, side by side

```python
# BAD: names a thing, defends nothing. Useless at 2 a.m.
def test_transition():
    d = Drone()
    d.transition()
    assert d.mode == "FW"

# GOOD: names the failure mode; ties to a real risk and its source.
def test_transition_aborts_on_low_airspeed_to_prevent_stall_drop():
    """FAILURE MODE DEFENDED: commanding MC->FW transition below the minimum
    transition airspeed would let the wing fail to generate lift, dropping the
    airframe out of the sky. The transition MUST abort and return to a stable
    multicopter mode rather than complete into a stall.

    GIVEN  airframe in multicopter mode, airspeed below V_transition_min
    WHEN   a transition to fixed-wing is commanded
    THEN   the transition aborts, mode returns to MC, and an ABORT is logged.

    Source: exploratory charter 'transition brownout'; PX4 transition spec."""
    sim = start_sitl(airspeed=V_TRANSITION_MIN - 2.0)
    result = sim.command_transition(to="FW")
    assert result == "ABORT"
    assert sim.mode == "MC"
    assert decision_log.last().event == "TRANSITION_ABORT_LOW_AIRSPEED"
```

The good test is longer, and that length is the point: it encodes *why it exists*, *what it
proves*, and *where the knowledge came from*. Six months later, nobody deletes it by
accident, because its docstring tells them an airframe will fall out of the sky if they do.

### 12.4 The cultural ratchet

Tie it all together into one loop that makes the whole system monotonically safer over time:

```
  exploratory charter finds a novel failure
        │
        ▼
  reproduce it deterministically (.ulog replay or SITL fault inject)
        │
        ▼
  write a test that NAMES that failure mode  ── pushed to the lowest pyramid layer that catches it
        │
        ▼
  fix the code until green
        │
        ▼
  the test enters CI and guards that failure mode FOREVER
        │
        └──────────► every future change is now re-checked against it
```

Each turn of this loop converts a one-time human discovery into a permanent machine
guarantee. Do it a few hundred times and you have something no demo video can fake: a system
whose every known failure mode has a named, automated defender. **That is the moat.**

---

## 13. Capability ladder & practice this week

### 13.1 The ladder — from "it flew" to "I can prove it"

| Rung | You can… |
|---|---|
| 0 | Fly the mission once in SITL and watch it work |
| 1 | Write unit tests for the pure logic; they run in CI |
| 2 | Write an integration test through SITL that asserts a real mission contract |
| 3 | Replay a real `.ulog` deterministically and regression-gate the nav filter |
| 4 | Write property-based tests for the validators, gate, and decision log |
| 5 | Inject the full fault catalog and assert correct degradation for each |
| 6 | Gate the estimator on NEES/NIS consistency; monitor NIS in flight |
| 7 | Run a chaos soak that combines faults and asserts safety invariants hold |
| 8 | Hand a safety officer a verification dossier and defend every claim in it |

Rungs 0–2 are table stakes. Rungs 4–6 are what make you a strong autonomy engineer. Rungs
7–8 are what make you the person who signs off the flight — and that signature is the job.

### 13.2 Practice this week

1. **Pick one safety-critical function** in the stack (start with the geofence altitude
   clamp or a waypoint validator). Write a **property-based** test that asserts its invariant
   for all finite inputs. Watch Hypothesis try to break it.
2. **Name a failure mode.** Take your weakest existing test and rewrite its docstring to name
   the specific real-world bad outcome it defends against. Notice how the test improves once
   you know *why* it exists.
3. **Inject one fault in SITL.** Disable GPS mid-mission in the `vtol_demo` run and write the
   test that asserts bounded drift + operator warning + a decision-log entry. If the system
   *doesn't* degrade correctly, you just found a bug the right way — on a laptop, not on the
   range.
4. **Replay a log.** Take one `.ulog` (real or from SITL), feed it through the nav filter as a
   pure function, store the output as a golden file, and make a regression test out of it.
5. **Stand up the gate.** Add the decision-log chain-integrity property test (Section 10.3)
   to CI as a hard gate. Now the audit trail is continuously proven.

By the end of the week you will have moved at least one capability from "it flew" to "I can
prove it, automatically, forever." Repeat until the whole stack is on the right side of that
line.

---

## Sources & Citations

**Books**
- Kaner, Bach & Pettichord — *Lessons Learned in Software Testing* (the exploratory-testing
  and risk-based-testing canon).
- Cohn — *Succeeding with Agile* (origin of the test pyramid).
- Nygard — *Release It!* (failure under load, fault injection, stability patterns).
- Bar-Shalom, Li & Kirubarajan — *Estimation with Applications to Tracking and Navigation*
  (NEES/NIS filter consistency, Chapters on performance evaluation).
- Feldt et al. / Fowler — writing on mutation testing and metamorphic testing.
- Leveson — *Engineering a Safer World* (STAMP; complements the assurance angle in Module 09).

**Papers**
- Chen, Cheung & Yiu — "Metamorphic Testing: A New Approach for Generating Next Test Cases"
  (the metamorphic-property method, Section 7.3).
- Basili & Selby — empirical comparisons of testing strategies (why layered testing wins).

**Official docs & tools**
- PX4 SITL & simulation: https://docs.px4.io/main/en/simulation/
- PX4 ULog format: https://docs.px4.io/main/en/dev_log/ulog_file_format.html
- Gazebo (Garden): https://gazebosim.org/docs
- MAVSDK: https://mavsdk.mavlink.io/  ·  MAVLink: https://mavlink.io/en/
- pytest & pytest-asyncio: https://docs.pytest.org · https://pytest-asyncio.readthedocs.io
- Hypothesis (property-based testing): https://hypothesis.readthedocs.io
- Playwright (end-to-end UI): https://playwright.dev
- Netflix Chaos Engineering / *Principles of Chaos*: https://principlesofchaos.org

**Sibling guides**
- [24-autonomy-test-scaffold.md](24-autonomy-test-scaffold.md) — the concrete `drone/test/`
  layout this module formalizes.
- [22-autonomy-px4-sitl.md](22-autonomy-px4-sitl.md) — the SITL flow used throughout Section 5.
- [09-foundations-safety-assurance.md](09-foundations-safety-assurance.md) — turns these tests
  into a safety case.
- [08-foundations-company-strategy-moat.md](08-foundations-company-strategy-moat.md) — why this
  discipline is the business moat.
- [01_first_principles_systems_engineering.md](01_first_principles_systems_engineering.md) —
  the requirements-decomposition discipline the V-model depends on.
- [27-autonomy-counter-uas-ew.md](27-autonomy-counter-uas-ew.md) — the real-world source of the
  GPS-loss/jamming faults you inject.

*Repository references (the `drone/` autonomy stack, `drone/test/` scaffold, PX4 SITL flow,
`.ulog` replay, `policy/constitution.py`, `policy/decisions.py`, and the navigation filters)
trace to the author's own project. The framing of "verification as the moat" and the
risk-based testing posture reflect the author's engineering goals and publicly available
practice from the autonomy and defense-software community.*
