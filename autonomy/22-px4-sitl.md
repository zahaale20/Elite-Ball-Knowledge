# PX4 SITL for the VTOL drone

> SITL (Software-In-The-Loop) is the cheapest place you will ever fly. This file
> exists so you can run the *exact same autopilot firmware* the Pixhawk runs,
> against a simulated airframe, and break things for free. If you understand how
> SITL actually works — the lockstep clock, the simulator/MAVLink bridge, uORB,
> parameters — you stop treating it as a black box and start using it as a
> debugging instrument. Read this alongside the roadmap
> ([21-autonomy-vtol-roadmap.md](21-vtol-roadmap.md)), the onboard
> service ([23-autonomy-onboard-system.md](23-onboard-system.md)), and
> the test scaffold ([24-autonomy-test-scaffold.md](24-test-scaffold.md)),
> which uses SITL as its integration target.

Stage 1 deliverable: run the same autopilot firmware the Pixhawk will run, but
as a process on your **dev laptop**, flying a simulated **Tiltrotor VTOL** in
Gazebo Garden -- so mission scripts and the ground-station UI can be developed
end-to-end without risking the airframe.

The target VTOL pack is a **3-motor tilt-tricopter** (2 front tilt
motors + 1 rear stationary lift motor + V-tail), which is non-standard for
PX4's stock VTOL airframes (those assume 4 motors). For Stage 1 we use PX4's
stock `gz_tiltrotor` model as the closest stand-in -- it exercises the
transition state machine, mission upload, and the GCS end-to-end. An
airframe-accurate Gazebo SDF + airframe params land in Stage 2 / Stage 4 (see
[21-autonomy-vtol-roadmap.md](21-vtol-roadmap.md)).

> **Why not on the Pi?** PX4 only ships a no-physics shim (`none_iris`) for a
> single quadcopter. A VTOL needs real physics (Gazebo Garden), which is too
> heavy for a Pi 5. The Pi is the **hardware** target, not the SITL target.

## Supported hosts

| Host          | Status      | Notes                                                                    |
| ------------- | ----------- | ------------------------------------------------------------------------ |
| Linux (x86_64)| Primary     | PX4's reference SITL environment.                                        |
| macOS (arm64) | Supported   | Gazebo Garden via Homebrew works; expect occasional GUI quirks.          |
| Pi 5 (arm64)  | **Not for VTOL** | Use `none_iris` as a quad smoke test only; VTOL sim won't run here. |

## One-time install (macOS, Apple Silicon)

```bash
# Toolchain + PX4 deps
brew install cmake ninja gcc python git ccache xz
brew install --cask gz-garden          # Gazebo Garden

cd ~
git clone https://github.com/PX4/PX4-Autopilot.git --recursive
cd PX4-Autopilot
bash ./Tools/setup/macos.sh

# First build is slow (~20 min on M-series, much slower on a Pi). The
# Tiltrotor airframe is the closest stock PX4 match to the tilt-
# tricopter geometry until the Stage 2 custom SDF lands.
make px4_sitl gz_tiltrotor
```

## One-time install (Linux)

```bash
cd ~
git clone https://github.com/PX4/PX4-Autopilot.git --recursive
cd PX4-Autopilot
bash ./Tools/setup/ubuntu.sh
make px4_sitl gz_tiltrotor
```

## Ports that PX4 SITL opens

| Port (UDP) | Audience                                                              |
| ---------- | --------------------------------------------------------------------- |
| 14540      | Offboard / MAVSDK / DroneKit / pymavlink scripts (our onboard service)|
| 14550      | Ground stations (QGC, MAVProxy)                                       |

## How SITL works internally

SITL is not "PX4 pretending to fly." It is the **real PX4 flight stack** — the
same EKF2 estimator, the same commander state machine, the same control
allocation — compiled for your laptop instead of the FMU, with the sensor and
actuator drivers replaced by a bridge to a physics simulator.

```
   ┌──────────────── your laptop ────────────────────────────────┐
   │                                                              │
   │  ┌───────────────┐   sensor msgs (sim → PX4)  ┌───────────┐  │
   │  │  Gazebo Garden │ ─────────────────────────► │  PX4 SITL │  │
   │  │  (gz_tiltrotor │   actuator msgs (PX4 → sim)│  (px4 bin)│  │
   │  │   physics)     │ ◄───────────────────────── │  EKF2 +   │  │
   │  └───────────────┘                             │ commander │  │
   │        ▲  lockstep clock barrier               │ + mixer   │  │
   │        └────────────────────────────────────── └─────┬─────┘  │
   │                                          MAVLink UDP │        │
   └──────────────────────────────────────────────┬──────┼────────┘
                                                   │      │
                          MAVSDK / pymavlink :14540 │      │ :14550 QGC / MAVProxy
                          (onboard service)         ▼      ▼
```

### Lockstep — the SITL clock

By default PX4 SITL runs in **lockstep**: the simulator and the flight stack
advance in tightly coupled steps. PX4 will not run faster than the simulator can
deliver sensor data, and the simulator waits for PX4's actuator outputs before
stepping physics. The consequences you must internalize:

- **Determinism.** Two runs with the same inputs produce (nearly) the same flight
  — that is what makes SITL a usable test target. Your integration tests in
  [24-autonomy-test-scaffold.md](24-test-scaffold.md) depend on this.
- **A stalled simulator stalls PX4.** If Gazebo hangs (common on macOS under GPU
  pressure), PX4's clock freezes too. The vehicle does not "fly away" — the whole
  system pauses. This is a feature, but it can look like a hang.
- **Wall-clock ≠ sim-clock.** A heavily loaded laptop runs SITL slower than
  real time. Never put real-time `sleep()` assertions in tests; key off vehicle
  state and telemetry instead.
- **Disabling lockstep** (non-lockstep mode) lets PX4 run free-running for HITL
  or performance work, at the cost of determinism. Stay in lockstep for Stage 1.

### The simulator / MAVLink bridge

Two distinct channels carry traffic, and conflating them is a classic source of
confusion:

| Channel | Endpoints | Carries |
| ------- | --------- | ------- |
| **Sim bridge** | Gazebo ↔ PX4 (internal) | simulated IMU/GPS/baro/airspeed *in*, motor/servo commands *out* |
| **MAVLink (UDP)** | PX4 ↔ your scripts/GCS | heartbeats, telemetry, commands, mission upload |

Your onboard service and tests only ever touch the **MAVLink** side (`:14540`).
They never see the sim bridge. That is exactly why the same `vtol_demo.py`
script works against SITL and against the real Pixhawk — only the connection URL
changes; the MAVLink contract is identical.

### uORB and parameters (the two things to know)

- **uORB** is PX4's internal publish/subscribe message bus. Estimator output,
  setpoints, actuator commands — every module talks over uORB topics. You
  rarely touch it directly, but when you do (`listener <topic>` in the px4
  shell, e.g. `listener vehicle_status`), it is the ground truth for what the
  flight stack believes. MAVLink is a *projection* of selected uORB topics out
  over the link.
- **Parameters** are PX4's persistent config (`SYS_AUTOSTART`, `VT_F_TRANS_DUR`,
  transition airspeeds, allocation/mixer settings). In SITL they live in the
  build; on hardware they live in FMU flash. The Stage 4 goal of a single
  `tiltrotor.params` file is precisely so the *same* parameter set loads into
  both — keeping SITL representative. Inspect with `param show <name>`, set with
  `param set <name> <value>` in the px4 shell.

## Fly the Stage 1 VTOL demo mission

In one terminal, start the simulator:

```bash
cd ~/PX4-Autopilot && make px4_sitl gz_tiltrotor
```

In a second terminal, run the VTOL mission. It hovers, transitions to
forward flight, flies a 4-waypoint loop, transitions back to multicopter mode,
and lands.

```bash
source ~/pixhawk/.venv/bin/activate
python drone/missions/vtol_demo.py --conn udp://:14540
```

Optionally, watch it with MAVProxy in a third terminal:

```bash
mavproxy.py --master=udp:127.0.0.1:14550 --console
```

Or, recommended, point the ground-station UI at the SITL backend (see
`../ground-station/README.md`).

## Moving the same script to real hardware

```bash
python drone/missions/vtol_demo.py \
    --conn serial:///dev/serial/by-id/usb-Auterion_PX4_FMU_v6C.x_0-if00:115200
```

**Bench test with all propellers OFF first.** Every mission script's preflight
gate refuses to arm without GPS lock + home position + healthy calibrations, so
indoors it will time out — that is the safety feature working.

## Sensor & environment simulation

A common misconception is that SITL feeds PX4 "perfect" data. It does not — and
that is the point. Gazebo models sensor imperfections so the EKF2 estimator has
something realistic to converge on.

| Simulated sensor | What Gazebo models | Why it matters |
| ---------------- | ------------------ | -------------- |
| IMU (accel/gyro) | noise, bias | EKF2 must filter it; a perfect IMU would hide tuning bugs |
| GPS | fix delay, noise, dropout (configurable) | lets you test "won't arm without lock" and GPS-loss behavior |
| Barometer | noise, drift | altitude estimation realism |
| Magnetometer | noise, interference | heading estimate convergence |
| Airspeed | modeled from sim airflow | **critical** for VTOL transition gating |

You can perturb the environment to test robustness:

- **Wind.** Gazebo can apply steady and gusting wind. A back-transition that
  works in calm air may stall in a headwind — test the transition envelope
  ([21-autonomy-vtol-roadmap.md](21-vtol-roadmap.md)) under wind before
  trusting it.
- **GPS dropout.** Inducing GPS loss in SITL is the cheapest way to exercise the
  GPS-denied path and the policy gate's GPS check
  ([23-autonomy-onboard-system.md](23-onboard-system.md)) before
  hardware.
- **Sensor failure injection.** Killing a sensor stream tests whether the
  estimator degrades gracefully or the commander triggers the right failsafe.

These perturbations are exactly the **fault injection** cases the integration
tests in [24-autonomy-test-scaffold.md](24-test-scaffold.md) automate.

## Running headless and faster

| Goal | How | Notes |
| ---- | --- | ----- |
| No Gazebo GUI (CI) | `HEADLESS=1 make px4_sitl gz_tiltrotor` | the integration suite runs this way |
| Faster-than-real-time | lockstep allows a sim speed factor where the host keeps up | useful for long missions; mind determinism |
| Scripted bring-up | `tools/sim_up.sh` (tmux: SITL + onboard + UI) | the Stage 1 one-command path |
| Clean restart | kill the `make`/`gz` processes, relaunch | a stuck lockstep usually needs a full restart |

Headless mode is non-negotiable for CI: a GUI sim can't run on a GitHub Actions
runner, and the integration layer must run unattended.

## px4 shell cheat sheet

The terminal running `make px4_sitl` is a live PX4 console. The commands you'll
reach for most:

| Command | Tells you |
| ------- | --------- |
| `commander status` | armed/disarmed and the reason it won't arm |
| `commander arm` / `commander disarm` | force arming state (SITL only) |
| `listener vehicle_status` | flight mode, arming, failsafe flags (uORB ground truth) |
| `listener vehicle_local_position` | EKF position/velocity estimate |
| `listener vtol_vehicle_status` | the VTOL sub-state through a transition |
| `listener airspeed` | airspeed feeding the transition gate |
| `param show VT_*` | every VTOL/transition parameter |
| `param set <name> <val>` | change a parameter live |
| `ekf2 status` | estimator health and innovations |

When a mission misbehaves, start here before you touch the Python — the console
usually tells you in one line what the script can only infer.

## SITL vs HITL — and why this program uses both

| Aspect | SITL (Software-In-The-Loop) | HITL (Hardware-In-The-Loop) |
| ------ | --------------------------- | --------------------------- |
| Where PX4 runs | as a process on your laptop | on the **real Pixhawk 6C** |
| Where physics runs | Gazebo on the laptop | Gazebo on the laptop, FMU reads sim sensors |
| What it proves | flight logic, missions, GCS, allocation | the *actual firmware build + params* on the *actual FMU* |
| Cost of failure | zero | zero (no props), but exercises real timing/IO |
| Determinism | high (lockstep) | lower (real hardware timing) |
| Role in roadmap | Stage 1 development loop | Stage 6 "log replay before each new config" gate |

The program's discipline is: **iterate in SITL, then HITL-replay before any
powered config reaches the airframe** (the SITL→hardware gates in
[21-autonomy-vtol-roadmap.md](21-vtol-roadmap.md)). SITL catches logic
bugs; HITL catches "works on my laptop, not on the FMU" bugs — param mismatches,
timing, IO. Neither replaces a careful bench bring-up.

## Debugging SITL

When SITL misbehaves, debug it like the real flight stack it is — not like a toy.

- **Drop into the px4 shell.** The terminal running `make px4_sitl` *is* the
  PX4 console. Useful commands:
  - `commander status` — arming state and why it won't arm.
  - `listener vehicle_status` / `listener vehicle_local_position` — ground-truth
    estimator and mode state straight off uORB.
  - `param show VT_*` — every VTOL/transition parameter.
  - `ekf2 status` — estimator health; a transition that won't complete is often
    an estimator or airspeed issue, not a mixer issue.
- **Watch the MAVLink side separately** with MAVProxy on `:14550` so you can see
  what the *operator* sees versus what the flight stack believes.
- **Read the logs.** SITL writes ULog files just like hardware. Open them in PX4
  Flight Review or PlotJuggler and inspect actuator outputs, airspeed, and
  `vtol_vehicle_status` through the transition. Most "mystery" transition
  failures are obvious in the log.
- **Reproduce deterministically.** Because lockstep is deterministic, a failing
  mission usually re-fails identically — capture the exact mission file and
  params so a test in [24-autonomy-test-scaffold.md](24-test-scaffold.md)
  can pin it.

## Tiltrotor model limitations & the planned custom SDF

The stock `gz_tiltrotor` is a **4-motor tilt quadplane**. Your airframe is a
**3-motor tilt-tricopter + V-tail**. The gaps you must keep in mind:

| Property | Stock `gz_tiltrotor` | Your airframe |
| -------- | -------------------- | ------------- |
| Lift/cruise motors | 4 (all tilt) | 3 (2 tilt + 1 fixed rear) |
| Tail | conventional | V-tail (ruddervators) |
| Yaw in hover | 4-motor differential | rear-motor torque + differential front tilt |
| Mass / inertia | generic | measured from the printed airframe |
| Mixer / allocation | stock | custom (Stage 4) |

What this means in practice:

- **Do not tune gains against the stock model.** Anything tuned here is throwaway
  once the Stage 2 custom SDF and Stage 4 params land. Use the stock model only
  to exercise *logic*: the transition state machine, mission upload, GCS wiring,
  telemetry shape.
- **The custom SDF** (`drone/sim/models/vtol/`, Stage 2) encodes the real
  geometry, mass, inertia tensor, wing area, V-tail throws, motor KV (1300), and
  7" prop pitch. Only after it exists does SITL behavior start to *predict*
  hardware behavior.
- **Yaw behavior is the biggest stand-in error.** The stock model's 4-motor yaw
  has nothing to do with your rear-motor + differential-tilt yaw, so any
  hover-yaw observation in stock SITL is meaningless for your airframe.

## Common failure modes

| Symptom | Likely cause | Fix |
| ------- | ------------ | --- |
| `make px4_sitl gz_tiltrotor` hangs at start | Gazebo GPU/driver stall (esp. macOS) | retry; fall back to Docker-Linux or a Linux VM (roadmap risk #1) |
| Everything "freezes" mid-flight | lockstep: simulator stalled, so PX4 clock paused | unstick/restart Gazebo; do not assume PX4 crashed |
| Script can't connect on `:14540` | wrong URL, or a GCS already holding the port | confirm `udp://:14540`; close duplicate listeners |
| Won't arm in SITL | no GPS lock / home / failed preflight | wait for EKF convergence; check `commander status` |
| Transition never completes | airspeed never reaches blend threshold | check `VT_*` params, airspeed source in the log |
| Mission runs but UI shows no VTOL sub-state | MAVSDK-Python doesn't expose `EXTENDED_SYS_STATE` | add the pymavlink side-channel (Stage 2) |
| First build extremely slow | full PX4 + Gazebo compile | expected (~20 min on M-series); subsequent builds use ccache |

## What SITL will and won't catch

SITL is a powerful filter, but knowing its blind spots keeps you honest about
which bugs still wait for the bench and first flight
([21-autonomy-vtol-roadmap.md](21-vtol-roadmap.md) SITL→hardware gates).

| SITL catches | SITL does **not** catch |
| ------------ | ----------------------- |
| Mission logic and sequencing errors | Wiring/polarity errors (reversed motor, servo, prop) |
| Transition state-machine bugs | Real tilt-servo backlash and linkage slop |
| GCS ↔ onboard wiring and telemetry shape | True airframe mass/inertia (until the custom SDF) |
| Policy-gate / preflight behavior | EMI, brown-outs, connector vibration failures |
| GPS-loss and failsafe *logic* | Real RF link dropouts and antenna placement |
| Estimator convergence in nominal cases | Sensor calibration quality on the real FMU |

The honest summary: **SITL proves your software; the bench proves your wiring;
first flight proves your airframe.** Each gate exists because the layer above it
cannot see the failure the layer below catches. Treat a green SITL run as
permission to move to the bench — never as permission to fly.

---

## Sources & Citations

- PX4 SITL & simulation docs: https://docs.px4.io/main/en/simulation/
- PX4 Gazebo (gz) simulation & `gz_tiltrotor`: https://docs.px4.io/main/en/sim_gazebo_gz/
- Gazebo (Garden) docs: https://gazebosim.org/docs
- PX4 VTOL configuration & tiltrotor: https://docs.px4.io/main/en/config_vtol/
- MAVSDK-Python (offboard/missions): https://mavsdk.mavlink.io
- PX4 toolchain setup (macOS/Ubuntu scripts): https://docs.px4.io/main/en/dev_setup/
- MAVProxy: https://ardupilot.org/mavproxy/
- PX4 uORB messaging & `listener`: https://docs.px4.io/main/en/middleware/uorb.html
- PX4 parameters reference: https://docs.px4.io/main/en/advanced_config/parameter_reference.html
- PX4 SITL lockstep & HITL: https://docs.px4.io/main/en/simulation/#sitl-simulation-environment, https://docs.px4.io/main/en/simulation/hitl.html
- ULog flight log review: https://logs.px4.io (Flight Review), https://plotjuggler.io
- Companion guides: roadmap [21-autonomy-vtol-roadmap.md](21-vtol-roadmap.md), onboard [23-autonomy-onboard-system.md](23-onboard-system.md), tests [24-autonomy-test-scaffold.md](24-test-scaffold.md), sim/test foundations [06-foundations-simulation-test-verification.md](../foundations/06-simulation-test-verification.md).

*SITL ports, model names, and setup scripts track PX4 `main`; verify against the current PX4 docs for your checked-out version.*
