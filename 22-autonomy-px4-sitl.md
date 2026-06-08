# PX4 SITL for the VTOL drone

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
[21-autonomy-vtol-roadmap.md](21-autonomy-vtol-roadmap.md)).

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

---

## Sources & Citations

- PX4 SITL & simulation docs: https://docs.px4.io/main/en/simulation/
- PX4 Gazebo (gz) simulation & `gz_tiltrotor`: https://docs.px4.io/main/en/sim_gazebo_gz/
- Gazebo (Garden) docs: https://gazebosim.org/docs
- PX4 VTOL configuration & tiltrotor: https://docs.px4.io/main/en/config_vtol/
- MAVSDK-Python (offboard/missions): https://mavsdk.mavlink.io
- PX4 toolchain setup (macOS/Ubuntu scripts): https://docs.px4.io/main/en/dev_setup/
- MAVProxy: https://ardupilot.org/mavproxy/

*SITL ports, model names, and setup scripts track PX4 `main`; verify against the current PX4 docs for your checked-out version.*
