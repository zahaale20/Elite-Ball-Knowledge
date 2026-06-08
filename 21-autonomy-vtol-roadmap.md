# Autonomous VTOL Program Roadmap

> This file is the program's backbone. It exists so that every other guide in
> the autonomy band — SITL ([22-autonomy-px4-sitl.md](22-autonomy-px4-sitl.md)),
> the onboard system ([23-autonomy-onboard-system.md](23-autonomy-onboard-system.md)),
> the test scaffold ([24-autonomy-test-scaffold.md](24-autonomy-test-scaffold.md)),
> control theory ([25-autonomy-control-theory.md](25-autonomy-control-theory.md)),
> and GNC ([28-autonomy-gnc.md](28-autonomy-gnc.md)) — hangs off a single,
> staged plan with hard exit criteria. Reading it should make you able to answer
> three questions for any piece of work: *which stage am I in, what proves the
> stage is done, and what kills the program if I get it wrong?* A roadmap that
> can't answer those is a wish list. This one is gated. See
> [02-ten-year-mastery-plan.md](02-ten-year-mastery-plan.md) for how this program
> slots into the longer arc.

This document is the single source of truth for the program that builds, flies,
and operates a 3D-printed fixed-wing UAV in its **VTOL
tilt-tricopter** configuration, controlled by a Holybro/Auterion **Pixhawk 6C**
with a **Raspberry Pi 5** companion computer.

It spans two repositories that are intentionally separate:

| Repo                              | Role                                                              |
| --------------------------------- | ----------------------------------------------------------------- |
| `zahaale20/drone` (this repo)     | **Onboard edge node.** Intakes sensors, runs mission/autonomy/CV, exposes a JSON+WS+MJPEG API. No UI. |
| `zahaale20/ground-station`        | **Operator console.** React + Vite app that renders telemetry, video, and commands. No processing. |

## Architecture: edge processing, thin link, display-only GCS

```
   [ Pixhawk 6C ]──serial──┐
   [ Camera (USB) ]────────┤
   [ Future: lidar/IMU/CV ]┤        Pi 5  (this repo)
                           ▼   ┌────────────────────────────┐                      ┌──────────────────────┐
                               │  intake  →  process  →     │ JSON / WS / MJPEG    │  ground-station UI   │
                               │  - mission mgmt            │ ────────────────────►│  - map / video       │
                               │  - telemetry shaping       │                      │  - controls          │
                               │  - autonomy (Stage 6+)     │ ◄────────────────────│  - mission editor    │
                               │  - CV / payload (Stage 8)  │  high-level commands │                      │
                               └────────────────────────────┘                      └──────────────────────┘
```

Design rules this enforces:

- **All sensor I/O and decision-making lives on the Pi.** The GCS never talks
  to the Pixhawk or the camera directly.
- **Only curated state crosses the radio link.** Telemetry is shaped on the Pi
  (5 Hz aggregated frame, 200-point breadcrumb, downscaled MJPEG) instead of
  forwarding the raw MAVLink + camera firehose. Survives spotty bandwidth.
- **Commands are high-level only.** "Arm", "Takeoff", "→ FW", "Upload mission",
  not per-axis joystick. The Pi is authoritative for safety gates (geofence,
  battery, transition airspeed) — Stage 7.
- **No UI assets ship from the Pi.** The onboard service is a pure API. The
  GCS is built and served from the operator's laptop / a separate web host.
- **GCS is replaceable.** Anything that speaks the JSON+WS contract (mobile
  app, CLI, another GCS) can connect. The contract is the product.

## Vehicle of record

- **Airframe:** A 3D-printed fixed-wing UAV with a VTOL conversion pack.
  **Tilt-tricopter** layout: two
  front motors on tilt mechanisms (vertical for hover, horizontal for cruise)
  + one rear stationary lift motor (idle in forward flight). Wingspan 1340 mm,
  length 990 mm, AUW **2000-3000 g**, cruise 60-70 km/h. Material LW-PLA +
  PETG.
- **VTOL pack electronics:**
  - 3 × Emax ECOII 2807 1300KV (or T-Motor F90 1300KV)
  - 3 × BlHeli_S 45A ESC (or Lumenier 51A)
  - 7" props: two CCW + one CW (the rear motor differs in rotation for yaw
    authority during hover, classic tricopter convention)
  - 2 × Kingmax 1203MD tilt servos (or GDW DS041MG)
  - The base airframe contributes wing/V-tail servos on top of the above.
- **PX4 airframe class:** **Tiltrotor VTOL** (`MAV_TYPE = 21`). The
  3-motor tilt-tri layout is non-standard for PX4's stock 4-motor tiltrotor,
  so the stock model is a placeholder until the Stage 2 custom SDF + airframe
  params land. For SITL we use PX4's `gz_tiltrotor` as the closest stand-in
  (a 4-motor tilt quadplane) so the transition state machine and the GCS get
  exercised end-to-end.
- **Flight controller:** Pixhawk 6C (FMU v6C.x). USB ID `3185:0038`,
  stable serial path `/dev/serial/by-id/usb-Auterion_PX4_FMU_v6C.x_0-if00`.
- **Companion:** Raspberry Pi 5, Debian 13 (trixie), arm64.

## Where simulation runs — and why not on the Pi

PX4 ships a no-physics shim (`none_iris`) only for the iris quadcopter. **There
is no equivalent shim for a VTOL.** VTOL SITL therefore needs a real physics
simulator -- **Gazebo Garden** with the `gz_tiltrotor` model -- which is too
heavy to run usefully on a Pi 5.

The program splits accordingly:

| Host                  | Role                                                                                       |
| --------------------- | ------------------------------------------------------------------------------------------ |
| macOS / Linux laptop  | PX4 SITL (`gz_tiltrotor`) + onboard service pointed at it (`udpin://0.0.0.0:14540`)        |
| Raspberry Pi 5        | Onboard service talking to the real Pixhawk over `/dev/ttyACM0`. *No* SITL.                |
| Ground-station UI     | Same React app for both. Connects to whichever host you point it at via `VITE_DRONE_URL`.  |

The legacy `none_iris` Pi-side SITL target is kept as a quadcopter smoke test
only; it is not representative of VTOL behavior.

## Stage gates

| Stage | Deliverable | Done-when                                                                                                                                                | Owner repo(s) |
| ----- | ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------- |
| **1** | **SITL as a Tiltrotor VTOL** | `tools/sim_up.sh` (Linux) or the same script on macOS brings up PX4 SITL with `gz_tiltrotor` (placeholder for the 3-motor tilt-tri until Stage 2), the onboard service, and the UI. The `vtol_demo.py` mission performs **hover takeoff → transition to FW → fly waypoints → transition to MC → hover land** end-to-end. UI exposes operator buttons to command transitions. | drone, ground-station |
| 2 | Airframe-specific Gazebo SDF **+ live VTOL state pill** | Custom Gazebo model with the actual 3-motor tilt-tricopter geometry (2 front tilt motors + 1 rear lift motor), mass, inertia, wing area, V-tail throws, motor KV (1300), prop pitch (7"). Checked into `drone/sim/models/vtol/`. **Plus** a pymavlink listener for `EXTENDED_SYS_STATE` so the UI can show the live `MAV_VTOL_STATE` (MC / TRANSITION_TO_FW / FW / TRANSITION_TO_MC) -- MAVSDK Python does not expose this stream, so a side-channel pymavlink connection is required. | drone, ground-station |
| 3 | Hardware BOM lock-in | Bill of materials cross-checked against the recommended VTOL-pack electronics (3× Emax ECOII 2807 1300KV motors, 3× BlHeli_S 45A ESCs, 7" props 2CCW+1CW, 2× Kingmax 1203MD tilt servos) **plus** base airframe control servos AND against Pixhawk 6C constraints (PWM/DShot channel count, UART count for GPS + ELRS + telemetry + companion link). Committed as `drone/hardware/BOM.md`. | drone |
| 4 | PX4 airframe params for the VTOL | `drone/airframes/tiltrotor.params` (motor/servo output mapping for 3-motor tilt-tri, tilt-servo control allocator, V-tail mixer, transition airspeed thresholds, tuning seeds). Loadable to **both** SITL and the real Pixhawk. | drone |
| 5 | Bench bring-up protocol | Documented + scripted: motors-off arm test, control-surface direction test, ESC calibration, mag/accel cal, RC failsafe, GCS link, telemetry radio link. | drone |
| 6 | First flight protocol | Manual hover, manual forward flight, autonomous transition, RTL — each with a go/no-go checklist and HITL log replay. | drone |
| 7 | Security & CI hardening | TLS in front of the onboard service, rotate API token via env, restrict mission upload origin, GitHub Actions on both repos (lint, type-check, unit + integration tests, dependency scan). | both |
| 8 | Mission expansion | Geofence enforcement, BVLOS-ready logging, payload integration via the airframe's modular nose. | both |

### Stage-by-stage rationale, exit criteria, and risks

The table above is the contract. This section is the *why* behind each row —
the reasoning a reviewer (or a future you) needs to decide whether a stage is
genuinely closed or just looks closed.

#### Stage 1 — SITL as a Tiltrotor VTOL

- **Rationale.** You cannot iterate on mission logic, telemetry shaping, or the
  transition state machine against real hardware — the cost of a mistake is a
  broken airframe. SITL collapses the iteration loop from hours to seconds and
  lets you exercise the *full* software stack (onboard service + GCS) before any
  motor spins. This is the single highest-leverage stage; everything downstream
  rides on having a trustworthy simulator in the loop.
- **Exit criteria (binary).** `tools/sim_up.sh` brings up PX4 SITL +
  onboard service + UI with one command; `vtol_demo.py` completes
  hover → FW → waypoints → MC → land with **zero `ABORT`**; the UI can command a
  transition and you see the vehicle obey.
- **Risks.** macOS Gazebo flakiness (mitigation: Docker-Linux fallback);
  treating the `gz_tiltrotor` stand-in as if it were the real airframe (it is
  *not* — see Stage 2). Do not tune gains against the stand-in.

#### Stage 2 — Airframe-specific SDF + live VTOL state pill

- **Rationale.** The stock `gz_tiltrotor` is a 4-motor quadplane. Your airframe
  is a 3-motor tilt-tri with a V-tail. Their mass, inertia, and control
  allocation differ enough that any tuning done against the stand-in is
  throwaway. A geometry-accurate SDF is the first time SITL behavior starts to
  predict hardware behavior. The live `MAV_VTOL_STATE` pill matters because the
  transition is the most dangerous phase of flight and the operator must *see*
  which sub-state the vehicle is in.
- **Exit criteria.** Custom model in `drone/sim/models/vtol/` with measured (not
  guessed) mass/inertia once a physical airframe exists; UI shows MC /
  TRANSITION_TO_FW / FW / TRANSITION_TO_MC sourced from a **pymavlink**
  side-channel (MAVSDK-Python does not surface `EXTENDED_SYS_STATE`).
- **Risks.** Inertia tensor guessed instead of measured; CG drift from LW-PLA
  warpage invalidating the model (re-weigh after every major print revision).

#### Stage 3 — Hardware BOM lock-in

- **Rationale.** Ordering the wrong ESC current rating, prop pitch, or servo
  torque costs weeks of shipping lead time and can damage the airframe on first
  power-up. Locking the BOM *before* Stage 4 params forces you to reconcile the
  electrical reality (channel count, current draw, UART budget) with the
  firmware mapping.
- **Exit criteria.** `drone/hardware/BOM.md` committed; every output channel
  mapped to a physical 6C pin; total continuous current within ESC/battery
  limits with margin.
- **Risks.** PWM/DShot channel shortfall (9 outputs needed — see the channel
  budget below); UART contention (GPS + ELRS + telemetry + companion link).

#### Stage 4 — PX4 airframe params for the VTOL

- **Rationale.** This is where the custom control allocator and mixer live. A
  tilt-tri is not expressible with a stock mixer; you need explicit motor/servo
  output mapping, tilt-servo allocation, and transition thresholds. The params
  file is the bridge that lets the *same* configuration load into SITL and the
  real Pixhawk, so SITL stays representative.
- **Exit criteria.** `drone/airframes/tiltrotor.params` loads cleanly into both
  SITL and hardware; control-surface and motor directions verified on the bench
  (Stage 5); transition airspeed thresholds set conservatively.
- **Risks.** Allocation sign errors (a reversed tilt servo turns a transition
  into a crash); over-aggressive transition airspeed causing a stall during
  back-transition.

#### Stages 5-8 — bring-up, first flight, hardening, expansion

- **Stage 5 (bench bring-up)** exists to catch every wiring and direction error
  *with props off*. Exit: motors-off arm test, surface-direction test, ESC cal,
  sensor cal, RC failsafe, link tests all pass and are scripted.
- **Stage 6 (first flight)** is gated by go/no-go checklists and HITL log
  replay — never fly a config you have not replayed. Exit: manual hover, manual
  FW, autonomous transition, RTL all logged and reviewed in Flight Review.
- **Stage 7 (security & CI)** treats the onboard service as an internet-facing
  product: TLS, rotating tokens, restricted mission-upload origin, GitHub
  Actions running lint + types + unit + integration on every push. See
  [09-foundations-safety-assurance.md](09-foundations-safety-assurance.md).
- **Stage 8 (mission expansion)** adds geofence enforcement, BVLOS-grade
  logging, and payload integration. Exit: geofence breach triggers the correct
  failsafe in SITL *and* on the bench.

## Tilt-tricopter control allocation

The control problem that defines this airframe is **allocation**: how the
autopilot's desired body torques and thrust get mapped onto three motors, two
tilt servos, and a V-tail — and how that mapping *changes continuously* through
the transition. This is the part that no stock PX4 airframe gives you for free.

```
              FRONT
        M1 (tilt) ── M2 (tilt)      M1,M2: front motors on tilt servos
            \         /             tilt = 90° (up)  → hover
             \       /              tilt =  0° (fwd) → cruise
              \     /
               body                 M3: rear lift motor (CW),
                |                        idles in forward flight
               M3 (fixed, lift)
              /     \
           V-tail   V-tail          ruddervators: pitch + yaw in FW
            REAR
```

| Flight phase | Lift source | Pitch | Roll | Yaw |
| ------------ | ----------- | ----- | ---- | --- |
| Hover (MC) | M1+M2+M3 thrust | front/rear thrust diff | front motor thrust diff | rear motor torque + differential tilt |
| Transition | blended (tilt sweeps) | blended | blended | blended (authority migrates) |
| Cruise (FW) | wing | V-tail (ruddervators) | ailerons | V-tail (ruddervators) |

Key allocation facts to internalize:

- **Yaw authority migrates.** In hover, yaw comes from the rear motor's reaction
  torque plus differential tilt of the two front motors (tilt them slightly
  opposite to produce a yaw moment). In cruise, yaw is aerodynamic via the
  V-tail. The dangerous window is mid-transition where *neither* source is at
  full authority — this is why transition airspeed scheduling matters.
- **The rear motor is dead weight in cruise.** It produces drag and mass it
  cannot pay back aerodynamically, so the allocator must idle it cleanly and the
  airframe design must accept the cruise-efficiency penalty.
- **Tilt servos are a control surface, not a config switch.** The allocator
  commands a continuous tilt angle, not a binary up/down. Treat tilt angle as a
  first-class actuator with its own rate limit, slew, and failure mode.
- **Sign discipline is everything.** A reversed motor rotation, prop, or tilt
  direction passes a desk review and kills the vehicle on the bench. Stage 5
  exists specifically to catch this with props off.

For the control-theory underneath (mixing matrices, pseudo-inverse allocation,
actuator saturation), see [25-autonomy-control-theory.md](25-autonomy-control-theory.md)
and the GNC integration in [28-autonomy-gnc.md](28-autonomy-gnc.md).

## Transition envelope

The transition is a scheduled maneuver, not an instant. PX4 sequences it through
`MAV_VTOL_STATE`, and your job is to keep the vehicle inside a safe envelope of
airspeed, altitude, and tilt angle the whole way.

```
 airspeed
   │                         ┌──────────── FW cruise (wing-borne)
   │                     ────┘
   │   stall margin  ┌───┘   ← back-transition must stay above stall
   │ ───────────────┤        ← forward-transition must reach blend airspeed
   │  hover (0)  ────┘
   └─────────────────────────────────────► time
        MC   │ TRANSITION_TO_FW │   FW   │ TRANSITION_TO_MC │  MC
```

| Parameter (conceptual) | Forward transition | Back transition |
| ---------------------- | ------------------ | --------------- |
| Trigger | operator/mission command in MC | command in FW |
| Tilt schedule | 90° → 0° over `VT_F_TRANS_DUR` | 0° → 90° |
| Airspeed gate | must reach blend airspeed before completing | must stay **above stall** until hover thrust supports weight |
| Failure mode | incomplete transition → wallowing, altitude loss | stall/drop if airspeed bled off too early |
| Abort path | revert to MC, re-establish hover | hold FW, climb, retry |

Hard rules:

- **Always have altitude to spend.** Both transitions can lose altitude; never
  initiate one near the ground in SITL or on hardware.
- **Back-transition is the killer.** Going FW → MC, if airspeed drops below
  stall before the lift motors take the load, the wing stops flying and the
  vehicle falls. Conservative airspeed thresholds (Stage 4) buy margin.
- **The operator must see the sub-state.** Hence the Stage 2 pymavlink
  `EXTENDED_SYS_STATE` pill — a transition stuck in `TRANSITION_TO_MC` is an
  emergency the operator needs to recognize in under a second.

## BOM & airframe considerations

The airframe is a constraint, not a detail. CG, channel count, current budget,
and print tolerances all feed back into the firmware and the flight envelope.

### Pixhawk 6C output channel budget

Nine outputs are required. Verify against the 6C MAIN/AUX PWM map *before*
ordering ESCs and wiring tilt-servo extensions.

| Output | Count | Type | Notes |
| ------ | ----- | ---- | ----- |
| Lift/cruise motors | 3 | PWM or DShot | M1, M2 (tilting) + M3 (fixed rear) |
| Tilt servos | 2 | PWM | continuous angle, needs rate limit |
| V-tail (ruddervators) | 2 | PWM | pitch + yaw in FW |
| Ailerons | 2 | PWM | inherited from base airframe |
| **Total** | **9** | | check AUX vs MAIN split on 6C |

### UART budget

The companion link, GPS, RC (ELRS), and a telemetry radio all compete for
serial ports. Map every consumer to a physical UART before Stage 3 closes —
running out of UARTs mid-build is a common, avoidable stall.

### Mass, CG, and print tolerance

- **AUW 2000-3000 g** drives motor/prop/ESC sizing and the stall airspeed that
  bounds the transition envelope.
- **LW-PLA + PETG** warps and absorbs moisture; CG can shift between prints.
  Re-weigh and re-balance after every major airframe revision and feed the new
  numbers back into the Stage 2 SDF inertia tensor.
- **Tilt mechanism slop** is a real failure source: backlash in the tilt servo
  linkage shows up as a control-allocation error mid-transition. Inspect it as
  part of Stage 5 bench bring-up.

## SITL-to-hardware gates

Nothing moves from simulation to a powered airframe without passing an explicit
gate. This is the single discipline that separates a portfolio project from a
crash compilation.

```
 SITL green ──► Bench (props OFF) ──► Tethered/manual hover ──► Autonomous
   │                │                        │                      │
   └ vtol_demo      └ Stage 5 protocol       └ Stage 6 go/no-go      └ HITL replay
     zero ABORT       all checks pass          checklist              before each new config
```

| Gate | You may proceed only when… |
| ---- | -------------------------- |
| SITL → Bench | `vtol_demo.py` completes with zero `ABORT`; params load identically into SITL and hardware |
| Bench → Hover | every Stage 5 check passes **with props off**; surface and motor directions verified |
| Hover → Autonomous | manual hover + manual FW logged and reviewed; failsafes (RC loss, geofence, low battery) tested |
| New config → Flight | the exact config has been HITL log-replayed; no untested param reaches a powered airframe |

The preflight gate in every mission script enforces the software half of this:
it refuses to arm without GPS lock, home position, and healthy calibrations. If
it times out indoors, that is the safety feature working — see
[23-autonomy-onboard-system.md](23-autonomy-onboard-system.md) for the
constitution-gated command policy that backs it.

## Test strategy (applies to every stage)

Per the project's testing philosophy, every change ships with risk-prevention
tests across the four layers below. Stage 1 establishes the scaffolding; later
stages fill it out.

| Layer | What it covers | Tooling                                                          |
| ----- | -------------- | ---------------------------------------------------------------- |
| Unit  | Pure logic: waypoint validation, mission plan construction, auth gate, telemetry dataclass serialization | `pytest` for `drone/`, `vitest` for `ground-station/`           |
| Integration | Onboard service ↔ PX4 SITL: arm/disarm, mission upload + start, VTOL transitions, /ws/telemetry frame shape, MJPEG fallback | `pytest` + a SITL fixture (`gz_tiltrotor --headless`)            |
| Acceptance | End-to-end scenario: operator logs in, uploads a 4-WP mission, watches it fly to RTL+land, sees telemetry on the map. | Playwright against UI + SITL stack                               |
| Exploratory | Charters around: brown-out during transition, GPS loss mid-mission, mission upload of malformed JSON, onboard-service auth bypass attempts | Manual session notes committed under `drone/test/exploratory/`   |

## Open risks tracked against this roadmap

1. **Gazebo Garden on macOS** is supported but rougher than on Linux. If macOS
   SITL becomes flaky, fall back to running SITL inside a Docker Linux container
   on the Mac, or on a Linux VM.
2. **The tilt-tricopter layout is non-standard for PX4.** Stock PX4
   VTOL airframes assume 4 lift motors (`Standard VTOL`) or 4 tilt motors
   (`Tiltrotor`). This airframe is 3 motors total (2 tilting + 1 fixed) with a
   V-tail. Stage 4 will require a custom control allocator and mixer; expect
   tuning iteration during Stages 5-6.
3. **Pixhawk 6C PWM channel count** must cover 3 motors + 2 tilt servos +
   V-tail (2 servos) + ailerons (2 servos, inherited from the base airframe) = 9
   outputs. Verify against the 6C's PWM AUX/MAIN map before ordering ESCs and
   wiring up tilt servo extensions.
4. **LW-PLA print warpage** can change CG. Stage 2 SDF will need updating once a
   physical airframe is weighed and balanced.

---

## Sources & Citations

- PX4 VTOL (tiltrotor) configuration & control allocation: https://docs.px4.io/main/en/config_vtol/
- PX4 airframe reference & `SYS_AUTOSTART`: https://docs.px4.io/main/en/airframes/airframe_reference.html
- PX4 simulation / `gz_tiltrotor`: https://docs.px4.io/main/en/sim_gazebo_gz/
- MAVLink `EXTENDED_SYS_STATE` / `MAV_VTOL_STATE`: https://mavlink.io/en/messages/common.html
- MAVSDK-Python: https://mavsdk.mavlink.io  ·  pymavlink: https://github.com/ArduPilot/pymavlink
- Pixhawk 6C (Holybro) hardware: https://docs.holybro.com  ·  PX4 hardware: https://docs.px4.io/main/en/flight_controller/
- Flight log review (PlotJuggler / PX4 Flight Review): https://plotjuggler.io, https://logs.px4.io
- VTOL aerodynamics & transition: Anderson, *Aircraft Performance and Design*; Beard & McLain, *Small Unmanned Aircraft: Theory and Practice* (Princeton).
- Control allocation background: see [25-autonomy-control-theory.md](25-autonomy-control-theory.md) and [28-autonomy-gnc.md](28-autonomy-gnc.md).
- Companion guides: SITL [22-autonomy-px4-sitl.md](22-autonomy-px4-sitl.md), onboard [23-autonomy-onboard-system.md](23-autonomy-onboard-system.md), tests [24-autonomy-test-scaffold.md](24-autonomy-test-scaffold.md), assurance [09-foundations-safety-assurance.md](09-foundations-safety-assurance.md).

*This roadmap documents the author's own VTOL program; stage definitions are the author's. Hardware/firmware specifics track the vendor docs above.*
