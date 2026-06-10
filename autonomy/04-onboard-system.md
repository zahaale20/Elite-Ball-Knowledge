# Drone side — Pixhawk 6C + Raspberry Pi

> **Why this project exists:** My primary motivation is to land a job at a
> leading defense-autonomy company (such as
> Shield AI, Skydio, or Auterion). This repo is a deliberate portfolio of the
> exact skills those teams hire for: PX4/Pixhawk autopilots, MAVLink/MAVSDK,
> onboard edge autonomy, real-time telemetry, and computer-vision targeting on
> embedded hardware. Every design decision here is made to demonstrate
> production-minded defense-autonomy engineering.

Everything in this directory runs **on the drone** (the Raspberry Pi attached
to the Pixhawk autopilot). The Pi is the **edge processing** node: it intakes
sensors, runs onboard logic (mission management, telemetry shaping, future
computer-vision / autonomy), and exposes a pure JSON / WebSocket / MJPEG API.

There are two operator surfaces:
- Network UI via the onboard API (ground-station style client over HTTP/WS).
- Local HDMI tactical HUD via `tools/hdmi_inference_display.py`.

The HDMI HUD is local-only (physically attached display). It does not replace
or change the onboard API contract.

Hardware: Holybro/Auterion **PX4 FMU v6C.x** (USB ID `3185:0038`)
Host: Raspberry Pi, Debian 13 (trixie), arm64
Device node: `/dev/ttyACM0`
Stable symlink: `/dev/serial/by-id/usb-Auterion_PX4_FMU_v6C.x_0-if00`

## Layout

| Path                    | Purpose                                                       |
| ----------------------- | ------------------------------------------------------------- |
| `scripts/`              | Standalone telemetry scripts (`heartbeat.py`, `mavsdk_telemetry.py`) |
| `missions/`             | MAVSDK mission scripts and example waypoint files             |
| `onboard/`              | FastAPI onboard service (telemetry WS, REST commands, MJPEG)  |
| `systemd/`              | User-level systemd unit and env-file template                 |
| `tools/hdmi_inference_display.py` | Local HDMI viewer: IMX500 detections + HUD + minimap + DVR |
| `tools/sim_up.sh`       | tmux orchestrator for PX4 SITL + onboard service              |
| `test/`                 | Unit / integration / exploratory test scaffold                |
| `sitl.md`               | PX4 SITL bring-up notes (now [03-autonomy-px4-sitl.md](03-px4-sitl.md)) |
| `ROADMAP.md`            | Program source of truth (now [02-autonomy-vtol-roadmap.md](02-vtol-roadmap.md)) |

## What is installed

| Tool                       | Where                                                      | Use                           |
| -------------------------- | ---------------------------------------------------------- | ----------------------------- |
| `mavproxy.py`              | pipx venv `~/.local/share/pipx/venvs/mavproxy`             | Terminal GCS, map, console    |
| `pymavlink`, `mavsdk`, `pyserial`, `dronekit` | venv `~/pixhawk/.venv`                  | Python scripting              |
| `python3-wxgtk4.0` (apt)   | system, symlinked into the mavproxy venv                   | MAVProxy `module load map`    |

QGroundControl is **not installed** — no official ARM64 AppImage. Use a
laptop for the GUI, or build from source.

## Quick start

```bash
# Terminal GCS
mavproxy.py --master=/dev/serial/by-id/usb-Auterion_PX4_FMU_v6C.x_0-if00 --baudrate=115200

# Inside MAVProxy: load helpers
module load console
module load map        # graphical map (needs X / desktop session)
status                 # vehicle info
param show SYS_AUTOSTART

# Python scripting
source ~/pixhawk/.venv/bin/activate
python drone/scripts/heartbeat.py
python drone/scripts/mavsdk_telemetry.py
```

## Onboard services (current)

`drone-onboard.service` runs the FastAPI backend.

`drone-display.service` runs the local HDMI display manager. Behavior:
- HDMI connected: turns display power on and starts fullscreen viewer.
- HDMI disconnected: turns display power off and idles.

Typical install/update commands:

```bash
mkdir -p ~/.config/systemd/user
cp ~/pixhawk/drone/systemd/drone-onboard.service ~/.config/systemd/user/
cp ~/pixhawk/drone/systemd/drone-display.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now drone-onboard drone-display
```

Useful logs:

```bash
journalctl --user -u drone-onboard -f
journalctl --user -u drone-display -f
```

## HDMI viewer modes and controls

Primary mode (`DRONE_CAM=picam`) uses Raspberry Pi AI Camera + IMX500 model
metadata for on-device detections, then overlays the tactical HUD.

Fallback mode (non-picam camera, for example `/dev/video0`) uses OpenCV MOG2
motion detection and renders the same HUD shell.

Keyboard controls in the fullscreen viewer:
- `q` or `Esc`: exit viewer loop.
- `n`: toggle night vision.
- `m`: cycle minimap view (radar, map, heading_up, perspective, off).
- `[`/`]` (or `-`/`=`): decrease/increase minimap range.

Mouse controls:
- Click NV pill to toggle night vision.
- Click minimap header to cycle view.
- Click minimap body to cycle range.

Important knobs (env in `~/.config/drone-onboard.env`):
- Display: `DRONE_DISPLAY_ENABLE`, `DRONE_DISPLAY_POLL_SEC`,
  `DRONE_DISPLAY_NAME`, `DRONE_DISPLAY_WIDTH`, `DRONE_DISPLAY_HEIGHT`.
- Camera: `DRONE_CAM`, `DRONE_CAM_WIDTH`, `DRONE_CAM_HEIGHT`,
  `DRONE_CAM_AE_MODE`, `DRONE_CAM_EV`, `DRONE_CAM_NV_EV`.
- Inference/tracking: `DRONE_IMX500_MODEL`, `DRONE_INFER_CONF`,
  `DRONE_INFER_IOU`, `DRONE_INFER_MAX_DET`, `DRONE_INFER_CLASSES`,
  `DRONE_TRACK_*`, `DRONE_TRACK_CMC`.
- HUD/minimap: `DRONE_HUD_MAP_VIEW`, `DRONE_HUD_MAP_RANGE_M`,
  `DRONE_MAP_PROVIDER`, `DRONE_DEM_PROVIDER`, `DRONE_BUILDINGS`.
- Video clips: `DRONE_DVR`, `DRONE_DVR_DIR`, `DRONE_DVR_*`.

## Notes / gotchas hit during setup

- `setuptools >= 81` removed `pkg_resources`, which MAVProxy still imports.
  We pinned `setuptools<81` in the MAVProxy pipx venv.
- `wxPython` has no ARM64 wheel on PyPI. We installed `python3-wxgtk4.0`
  from apt and symlinked `/usr/lib/python3/dist-packages/wx*` into the
  MAVProxy venv so the `map` module works.
- `~/.local/bin` was appended to `PATH` in `~/.bashrc`.
- ModemManager is not installed — good, it would steal `/dev/ttyACM0`.
- User `azaharia` is already in the `dialout` group.

## Network forwarding (so a laptop GCS can connect over Wi-Fi)

```bash
mavproxy.py --master=/dev/ttyACM0 --baudrate=115200 \
            --out=udp:<laptop-ip>:14550
```
On the laptop, open QGroundControl → it auto-listens on UDP 14550.

## Onboard architecture: the autonomy loop

Everything the Pi does fits one loop. Naming the stages keeps responsibilities
clean and gives every module exactly one job:

```
  sense → perceive → estimate → decide → act → assure
    │         │          │         │       │       │
  sensors   CV/IMX500   nav/EKF   policy  MAVLink  log
   (in)     detections  + fusion  + gates  out     + telemetry
                          │         ▲
                          └─ world memory / track fusion feeds decide
```

| Stage | Responsibility | Key inputs | Key outputs |
| ----- | -------------- | ---------- | ----------- |
| **sense** | pull raw data off hardware | Pixhawk MAVLink, IMX500 camera, future lidar/IMU | raw frames, raw telemetry |
| **perceive** | turn pixels into objects | camera frames, IMX500 on-sensor inference | detections (class, bbox, conf) |
| **estimate** | turn objects + motion into world state | detections, MAVLink pose, GPS-denied nav | fused tracks, vehicle state, world memory |
| **decide** | choose the next command | world state, mission, constitution | a *candidate* command |
| **act** | execute, if allowed | candidate command + policy verdict | MAVLink command to PX4 |
| **assure** | prove what happened | every command + state transition | hash-chained decision log, shaped telemetry |

The two stages people skip are the ones that matter most for a defense-grade
system: **decide** is gated by an explicit policy (not buried in `if` statements
scattered through handlers), and **assure** makes every decision auditable after
the fact. Those are the two sections below.

## The FastAPI onboard service

The onboard service (`drone/onboard/`) is a **pure API** — no UI assets ship
from the Pi (roadmap rule). It exposes three surfaces over one process:

| Surface | Transport | Purpose |
| ------- | --------- | ------- |
| REST commands | HTTP `POST /api/...` | discrete operator actions: arm, takeoff, transition, upload mission |
| Telemetry stream | WebSocket `/ws/telemetry` | shaped 5 Hz state frames + breadcrumb |
| Video | MJPEG `/video` | downscaled camera feed, fallback when bandwidth is tight |

```
drone/onboard/
├── server.py            # FastAPI app, routes, lifespan startup/shutdown
├── mavlink/             # MAVSDK + pymavlink connections to PX4
│   ├── link.py          #   single owner of the vehicle connection
│   └── ext_state.py     #   pymavlink side-channel for EXTENDED_SYS_STATE
├── telemetry/           # shaping: raw MAVLink firehose → 5 Hz curated frame
├── perception/          # IMX500 detections + track fusion + world memory
├── policy/              # constitution-gated command policy (the safety gate)
├── decisionlog/         # hash-chained, append-only decision log
└── camera/              # Picamera2 / OpenCV capture + MJPEG encoder
```

Design rule: **the connection to PX4 has exactly one owner** (`mavlink/link.py`).
Every other module asks it for state or hands it a command. Two modules both
holding the MAVLink link is how you get racey, duplicated commands.

### Threading / async model

The service is `asyncio`-first because most of its work is IO-bound (waiting on
MAVLink, websockets, the camera). But two things must *not* block the event
loop, so they get their own execution context:

| Work | Runs on | Why |
| ---- | ------- | --- |
| REST handlers, WS push, MAVSDK calls | the asyncio event loop | IO-bound, naturally async |
| pymavlink `EXTENDED_SYS_STATE` listener | a background task/thread | pymavlink is blocking; isolate it |
| Camera capture + MJPEG encode | a worker thread | CPU-bound, would stall the loop |
| Telemetry shaping (5 Hz tick) | an async timer task | steady cadence independent of MAVLink rate |

```
        ┌──────────── asyncio event loop ────────────┐
        │  REST routes   WS /ws/telemetry   /video    │
        │      │              ▲                ▲       │
        │   policy gate    shaped frame     mjpeg q    │
        └──────┼──────────────┼────────────────┼───────┘
               │              │                │
        ┌──────▼─────┐  ┌─────▼──────┐   ┌─────▼──────┐
        │ MAVLink link│  │ telemetry  │   │ camera     │
        │ (single)    │  │ shaper 5Hz │   │ worker thr │
        └──────▲──────┘  └─────▲──────┘   └────────────┘
               │ blocking       │ raw MAVLink
        ┌──────┴──────┐         │
        │ ext_state   │─────────┘
        │ (pymavlink) │
        └─────────────┘
```

The golden rule: **nothing blocking touches the event loop.** A blocked loop
freezes telemetry to the operator, which in flight is a safety event.

## Constitution-gated command policy

Commands do not go straight from `decide` to `act`. They pass through a single
**policy gate** that checks every command against a fixed set of rules — the
"constitution." The gate is the only path to the vehicle, so there is no way to
route a command around the safety rules.

```
 candidate command ──► [ constitution gate ] ──► allow ──► MAVLink → PX4
                              │                     │
                              └──► deny ────────────┴──► decision log (with reason)
```

| Gate check (constitution rule) | Denies when… |
| ------------------------------ | ------------ |
| **GPS / home** | no GPS lock or no home position set |
| **Geofence** | command would take the vehicle outside the fence |
| **Battery** | below the reserve needed to RTL |
| **Transition envelope** | airspeed/altitude unsafe for the requested VTOL transition |
| **Mode legality** | command illegal in the current flight mode |
| **Authority** | request lacks a valid auth token / origin |

Properties that make this *production-minded* rather than a pile of `if`s:

- **Single choke point.** Every command — operator-issued or autonomy-issued —
  goes through the same gate. New command types inherit the gate for free.
- **Default-deny.** Unknown or unevaluable conditions deny, not allow.
- **Explainable denial.** Every denial carries a machine-readable reason that
  lands in the decision log and surfaces to the operator. "It didn't arm" is
  never a mystery.
- **Pure and testable.** The gate is a pure function of (command, world state) →
  verdict, so it is unit-tested exhaustively at the boundaries (see
  [05-autonomy-test-scaffold.md](05-test-scaffold.md)).

This is the software half of the SITL→hardware gates in
[02-autonomy-vtol-roadmap.md](02-vtol-roadmap.md): the preflight gate
that "refuses to arm without GPS lock + home + healthy calibrations" *is* this
policy in action.

## The hash-chained decision log

`assure` writes an append-only, tamper-evident record of every decision. Each
entry hashes its own content plus the previous entry's hash, so the log forms a
chain: altering or deleting any past entry breaks every hash after it.

```
 entry[n].hash = H( entry[n].payload || entry[n-1].hash )

 ┌─────────┐    ┌─────────┐    ┌─────────┐
 │ entry 0 │◄───│ entry 1 │◄───│ entry 2 │◄── …   (each links the previous hash)
 └─────────┘    └─────────┘    └─────────┘
```

| Field (per entry) | Why it's there |
| ----------------- | -------------- |
| timestamp (monotonic + wall) | order events even when wall-clock jumps |
| command + parameters | what was requested |
| policy verdict + reason | why it was allowed or denied |
| relevant world state snapshot | what the vehicle believed at decision time |
| `prev_hash` / `hash` | tamper-evidence |

Why a defense-autonomy reviewer cares:

- **Auditability.** After an incident you can replay exactly what the system
  decided and *why*, not just what it did.
- **Tamper-evidence.** You can prove the log wasn't edited after the fact.
- **Debuggability.** A denied command's reason is right next to the world state
  that caused it.

This pairs with HITL log replay (Stage 6): the ULog says what the *vehicle* did;
the decision log says what the *autonomy* intended.

## Telemetry shaping

The raw MAVLink + camera firehose must not cross the radio link. The shaper
collapses it to something a spotty link survives (roadmap: "only curated state
crosses the link").

| Raw | Shaped |
| --- | ------ |
| MAVLink at 50-100+ Hz, dozens of message types | one aggregated state frame at **5 Hz** |
| full position history | **200-point** breadcrumb trail |
| full-res camera | **downscaled MJPEG**, drop-frame under pressure |

The 5 Hz frame is a single, versioned dataclass serialized to JSON — which is
why telemetry serialization is a first-class unit test target. If the frame
schema changes, the GCS contract changes, so it is tested at the boundary.

## Deployment on the Pi

The service runs as user-level systemd units (full commands and logs above):

| Unit | Role |
| ---- | ---- |
| `drone-onboard.service` | the FastAPI service (telemetry, commands, MJPEG) |
| `drone-display.service` | local HDMI HUD; powers display on/off with HDMI presence |

Deployment realities that bit during bring-up (see the gotchas section):

- **`/dev/ttyACM0` ownership.** ModemManager would steal the port — it is not
  installed; the user is in `dialout`. The stable
  `/dev/serial/by-id/...` symlink is used everywhere so a re-enumeration doesn't
  break the link.
- **User services, not system.** `systemctl --user` keeps the stack in the
  operator's session and avoids root for application logic.
- **Env-driven config.** Every knob (camera, inference, HUD, DVR) is an env var
  in `~/.config/drone-onboard.env`, so the same image behaves differently per
  airframe without code changes.
- **No SITL on the Pi.** The Pi talks to the *real* Pixhawk only; SITL lives on
  the laptop ([03-autonomy-px4-sitl.md](03-px4-sitl.md)).

## How the modules wire together (end to end)

```
 IMX500 cam ─► perception ─► tracks/world ─┐
 Pixhawk ───► mavlink/link ─► estimate ────┤
                                           ▼
                                    decide (mission + autonomy)
                                           │ candidate command
                                           ▼
                                    policy gate (constitution)
                                       │allow        │deny+reason
                                       ▼             ▼
                                 mavlink/link    decision log ◄── every verdict
                                       │             ▲
                                       ▼             │
                                    PX4 / vehicle    │
                                       │ raw telemetry
                                       ▼             │
                                 telemetry shaper ───┘
                                       │ 5 Hz frame
                                       ▼
                              /ws/telemetry  +  /video (MJPEG)  ──► GCS
```

Read this diagram as the answer to "where does my change go?" A new sensor adds
to **sense/perceive**; a new safety rule adds to the **policy gate**; a new
operator action adds a REST route plus a gate check plus a decision-log entry —
never a route that talks to the vehicle directly.

---

## Sources & Citations

> Note: paths like `tools/`, `onboard/`, `systemd/` refer to the author's
> `pixhawk/drone/` repository this README originally documented.

- PX4 Autopilot docs (companion computers, MAVLink): https://docs.px4.io
- MAVSDK (Python): https://mavsdk.mavlink.io  ·  pymavlink / MAVProxy: https://github.com/ArduPilot/pymavlink, https://ardupilot.org/mavproxy/
- MAVLink protocol: https://mavlink.io
- Raspberry Pi AI Camera / Sony IMX500 + Picamera2: https://www.raspberrypi.com/documentation/accessories/ai-camera.html
- systemd user services: https://www.freedesktop.org/software/systemd/man/
- FastAPI: https://fastapi.tiangolo.com  ·  OpenCV: https://opencv.org
- QGroundControl: https://docs.qgroundcontrol.com
- Python `asyncio` (event loop, threads, executors): https://docs.python.org/3/library/asyncio.html
- Hash chaining / tamper-evident logs: Haber & Stornetta, *How to Time-Stamp a Digital Document* (J. Cryptology, 1991); Merkle, *A Digital Signature Based on a Conventional Encryption Function*.
- Companion guides: roadmap [02-autonomy-vtol-roadmap.md](02-vtol-roadmap.md), SITL [03-autonomy-px4-sitl.md](03-px4-sitl.md), tests [05-autonomy-test-scaffold.md](05-test-scaffold.md), GNC [09-autonomy-gnc.md](09-gnc.md), assurance [09-foundations-safety-assurance.md](../foundations/09-safety-assurance.md).

---

## ⚡ The Insider Layer — What the Field Knows but Rarely Writes Down

### The serial link is your weakest hardware

USB-serial to the Pixhawk (`/dev/ttyACM0`) is the flakiest part of the whole stack. It enumerates differently across boots (which is exactly why the `by-id` symlink exists — use it, always, never hard-code `ttyACM0`), it resets under EMI from the ESCs, and a brown-out re-enumerates it mid-flight. Production practice: reconnect logic with backoff, and active detection of the *silent half-dead link* — port open, file handle valid, but no heartbeats arriving. A link that's "connected" but mute is worse than one that's cleanly down.

### The Pi throttles, and throttling looks like a software bug

A Pi 5 under CV load with poor airflow hits 80–85 °C and throttles; your "FPS dropped and offboard timed out" is thermal, not code. `vcgencmd get_throttled` is the truth oracle — check it before you debug anything else. A heatsink and airflow are flight-safety items, not niceties. Undervoltage from a sagging 5 V rail produces *identical* symptoms, so power the Pi from a real BEC, never from the Pixhawk's servo rail.

### Linux is not real-time, and pretending otherwise bites

The Pi runs Debian, not an RTOS. Any loop near a hard deadline has no scheduling guarantee — a log flush, an `apt` cron job, or the GIL can stall you for tens of milliseconds. Keep anything with a real deadline (offboard streaming) on its own thread or process, raise its priority where it matters, and *design for jitter* instead of wishing it away. The flight controller owns the 1 kHz control loop precisely because the companion structurally cannot.

### One link, many consumers — arbitrate it

MAVSDK, a logger, and QGC all wanting the same serial port is a classic, maddening contention bug. Run a multiplexer (mavlink-router or a MAVSDK server) so the link has exactly one owner and everything else subscribes downstream. Two processes opening the same tty don't fail loudly — they silently corrupt each other's MAVLink parsing, and you'll chase phantom packet errors for a day.

### systemd is your flight-readiness contract

A user-level systemd unit with `Restart=on-failure`, an ordered dependency chain, and a watchdog turns "I forgot to start the service" into a non-event. The watchdog is the real point: a *hung* Python process that still holds the serial port is far worse than a crashed one that restarts cleanly. Encode liveness, not just existence.

### Tamper-evident logs aren't paranoia

Hash-chained logs (the Haber–Stornetta and Merkle lineage this file already cites) matter the instant a flight goes wrong and someone asks "what did it decide, and when?" An append-only, hash-linked decision log is the difference between a defensible incident review and a shrug. At defense-autonomy companies this is table stakes — the ability to *prove* the sequence of decisions, untampered, is part of the product, not an afterthought.
