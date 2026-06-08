# Drone side — Pixhawk 6C + Raspberry Pi

> **Why this project exists:** My primary motivation is to land a job at a
> defense-autonomy company like **Anduril** (or a similar place such as
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
| `sitl.md`               | PX4 SITL bring-up notes (now [22-autonomy-px4-sitl.md](22-autonomy-px4-sitl.md)) |
| `ROADMAP.md`            | Program source of truth (now [21-autonomy-vtol-roadmap.md](21-autonomy-vtol-roadmap.md)) |

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
