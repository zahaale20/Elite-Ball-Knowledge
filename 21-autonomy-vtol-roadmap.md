# Autonomous VTOL Program Roadmap

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

*This roadmap documents the author's own VTOL program; stage definitions are the author's. Hardware/firmware specifics track the vendor docs above.*
