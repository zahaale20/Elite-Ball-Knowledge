# Raspberry Pi — From SoC to Fielded Edge Computer, in Depth

> **Why this exists.** The Raspberry Pi is the most consequential piece of hardware in modern hobbyist-to-professional engineering: a $35–$80 board that boots Linux, exposes a 40-pin header of raw silicon, and ends up flying on drones, sitting inside industrial cabinets, and running edge-AI inference in fielded products at volume. Most engineers treat it as a magic black box that "runs Python," and that ignorance costs them when the SD card corrupts in the field, when a brownout reboots the board mid-flight, or when their "real-time" control loop jitters by 40 ms because Linux scheduled a journald flush. To reach elite level in autonomy and defense, you must understand the Pi the way you understand a microcontroller: the Broadcom SoC, the boot chain, the electrical limits of every pin, and exactly where Linux betrays you. This module turns the Pi from a toy into an instrument you can be trusted to put on a vehicle.
>
> **What mastering it makes you.** The engineer who can take a Compute Module, a schematic, and a power budget, and ship a rugged, SSD-booting, thermally-honest edge computer that survives the field — and who knows precisely when the Pi is the right tool and when it is malpractice.

This module sits between the bare-metal world of [65-engineering-embedded-firmware.md](65-engineering-embedded-firmware.md) and the model-deployment discipline of [64-autonomy-edge-inference-deployment.md](64-autonomy-edge-inference-deployment.md): the Pi is the most common host on which edge inference actually runs. The real-time C++ craft of [04-foundations-modern-cpp-realtime.md](04-foundations-modern-cpp-realtime.md) and the scheduling realities of [82-software-real-time-operating-systems.md](82-software-real-time-operating-systems.md) explain why a stock Pi cannot guarantee deadlines, and the GPU/parallel material of [81-software-gpu-and-parallel-computing.md](81-software-gpu-and-parallel-computing.md) explains its VideoCore and accelerator story. The power-and-thermal honesty demanded by [68-engineering-power-electronics.md](68-engineering-power-electronics.md) and the board-bring-up discipline of [78-engineering-pcb-and-electronics-design.md](78-engineering-pcb-and-electronics-design.md) are what keep it alive in a vehicle, and the whole exercise is an application of [01_first_principles_systems_engineering.md](01_first_principles_systems_engineering.md). For the deeper "why hardware bounds everything" argument, read its companion [110-hardware-foundations-no-software-without-hardware.md](110-hardware-foundations-no-software-without-hardware.md).

---

## 1. The Broadcom SoC — What You Are Actually Running On

A Raspberry Pi is not "a computer with a Broadcom chip." It is a **Broadcom SoC with a little DRAM and connectors bolted around it.** The SoC *is* the computer. Understanding its internal blocks is the difference between using the Pi and reasoning about it.

| Model | SoC | CPU | GPU | Process | Max DRAM |
|---|---|---|---|---|---|
| Pi 3B+ | BCM2837B0 | 4× Cortex-A53 @1.4 GHz (ARMv8, 64-bit) | VideoCore IV | 40 nm | 1 GB |
| Pi 4B | BCM2711 | 4× Cortex-A72 @1.5–1.8 GHz | VideoCore VI | 28 nm | 1/2/4/8 GB |
| Pi 5 | BCM2712 | 4× Cortex-A76 @2.4 GHz | VideoCore VII | 16 nm | 4/8/16 GB |

A few facts that matter more than the marketing numbers:

- **The CPU is a real ARM application core**, not a microcontroller core. The A76 in the Pi 5 is out-of-order, superscalar, with L1/L2 caches and a shared L2/L3 — it speculates, reorders, and has unpredictable per-instruction timing. That is *why* it is fast and *why* it is non-deterministic (see [110-hardware-foundations-no-software-without-hardware.md](110-hardware-foundations-no-software-without-hardware.md) on the datapath).
- **The "GPU" is the VideoCore**, and historically it was the *real* boss of the board. On Pi 1–4, the VideoCore is the **first processor to run at power-on** — the ARM cores are held in reset until the GPU's firmware brings them up. The VideoCore handles video decode (H.264/HEVC), the camera ISP, and the early boot. On Pi 5, this changed (see §2).
- **The Pi 5 added the RP1 I/O controller** — a separate Broadcom chip (designed in-house) that handles USB, Ethernet, GPIO, and the camera/display interfaces over a PCIe link to the SoC. This is a major architectural shift: I/O is no longer a bolt-on of the SoC but a dedicated southbridge.

```
        Raspberry Pi 5 — block view
   ┌──────────────────────────────────────┐
   │ BCM2712 SoC                          │
   │  4× Cortex-A76 ── shared L2 ── LPDDR4X│──► RAM (4–16 GB)
   │  VideoCore VII (3D + video + ISP)    │
   │  PCIe Gen2/3 root ──┐                │
   └─────────────────────┼────────────────┘
                         │ PCIe x4 (internal) + x1 (external connector)
              ┌──────────┴───────────┐
              │ RP1 I/O controller   │
              │  USB3 ×2, USB2 ×2    │──► USB
              │  GbE MAC             │──► Ethernet
              │  GPIO, I2C, SPI, PWM │──► 40-pin header
              │  2× MIPI (CSI/DSI)   │──► cameras/displays
              └──────────────────────┘
```

The lesson: **the Pi 5 is closer to a real SBC architecture (CPU + southbridge + PCIe) than its predecessors.** That is why it can drive NVMe SSDs and PCIe AI accelerators that the Pi 4 could only fake over USB.

---

## 2. The Boot Process — Five Stages Before Your Code

If you cannot draw the Pi boot chain, you cannot debug a board that won't come up. It is fundamentally different from x86 (no BIOS/UEFI) and from a microcontroller (no jump-to-reset-vector).

**Pi 1–4 boot order:**

1. **On-SoC ROM bootloader** (mask ROM, unchangeable) runs on the **VideoCore GPU**, not the ARM. It looks for the next stage.
2. **`bootcode.bin`** (on Pi 4, this moved into the SoC's EEPROM) — second-stage GPU bootloader; initializes DRAM, reads the boot config.
3. **`start.elf`** — the GPU firmware proper. Parses `config.txt`, splits RAM between GPU and CPU, loads the device tree and kernel.
4. **Device Tree (`*.dtb` + overlays)** — a binary description of the hardware (which I2C buses exist, what's on the SPI pins, which camera). The kernel reads this instead of probing.
5. **`kernel.img` / `kernel8.img`** — the Linux kernel finally runs on the ARM cores. `init` / `systemd` takes over.

**Pi 5 changed this:** the second-stage bootloader now lives in **SPI EEPROM** and the boot is more conventional. The Pi 5 supports a proper boot-order config (NVMe → USB → SD) stored in EEPROM, editable with `rpi-eeprom-config`.

Two files own the board's personality:

```ini
# /boot/firmware/config.txt — firmware-level hardware config
arm_boost=1                # let A76 hit max clock
dtparam=i2c_arm=on         # enable the I2C-1 bus on pins 3/5
dtparam=spi=on             # enable SPI0 on pins 19/21/23
dtoverlay=disable-bt       # free up the good UART (PL011) from Bluetooth
enable_uart=1              # console UART on pins 8/10
dtoverlay=pcie-32bit-dma   # Pi 5 NVMe quirk for some drives
```

The **device tree** is the concept most engineers miss. The kernel does not auto-discover your I2C sensor. You declare the bus in the device tree (via an overlay), and the driver binds to it. A missing or wrong overlay is the #1 reason "my sensor doesn't show up" — the hardware is fine; the kernel was never told it exists. This is the Linux analog of the clock-enable bug in [65-engineering-embedded-firmware.md](65-engineering-embedded-firmware.md).

---

## 3. GPIO and the 40-Pin Header — Real Silicon, Real Limits

The 40-pin header is the Pi's reason to exist for engineers. But every pin is a **3.3 V CMOS** pin wired *directly to the SoC* (or the RP1 on Pi 5) with **no protection diodes rated for abuse and no 5 V tolerance.**

```
   3V3  (1) (2)  5V
  GPIO2 (3) (4)  5V        GPIO2/3 = I2C1 (SDA/SCL)
  GPIO3 (5) (6)  GND
  GPIO4 (7) (8)  GPIO14    GPIO14/15 = UART (TXD/RXD)
   GND  (9)(10)  GPIO15
 GPIO17(11)(12)  GPIO18    GPIO18 = PWM0 / PCM_CLK (I2S)
 GPIO27(13)(14)  GND
 GPIO22(15)(16)  GPIO23
   3V3 (17)(18)  GPIO24
 GPIO10(19)(20)  GND       GPIO10/9/11 = SPI0 (MOSI/MISO/SCLK)
  GPIO9(21)(22)  GPIO25
 GPIO11(23)(24)  GPIO8     GPIO8/7 = SPI0 CE0/CE1
   GND (25)(26)  GPIO7
   ... (27–40: ID EEPROM, more GPIO, PWM1, I2S) ...
```

Hard electrical truths every engineer must internalize:

- **Logic is 3.3 V. Pins are NOT 5 V tolerant.** Drive a 5 V signal into a GPIO and you can kill the SoC. Use a level shifter (e.g., TXB0108, or a simple MOSFET shifter for I2C).
- **Per-pin current is ~16 mA max, ~50 mA total across all GPIO** (and the drive strength is configurable in the pad control, default 8 mA). A GPIO cannot drive a motor, a relay coil, or even a bright LED string directly. Use a transistor/driver.
- **The 5 V pins are unfused pass-through from the input supply.** They can source amps — and they can backfeed the board if you power through them.
- **There is no ADC.** Unlike an Arduino/STM32, the Pi has **zero analog inputs.** You add an external ADC (MCP3008 over SPI, ADS1115 over I2C) for any analog sensor.

| Interface | Pins (BCM) | Typical use | Notes |
|---|---|---|---|
| I2C-1 | GPIO2/3 | sensors, IMUs, ADCs, displays | needs 1.8–4.7 kΩ pull-ups (on-board on header) |
| SPI0 | GPIO7–11 | high-rate sensors, displays, ADCs | 2 chip-selects; up to tens of MHz |
| UART (PL011) | GPIO14/15 | GPS, telemetry, console | the *good* UART; free it from BT |
| PWM | GPIO12/13/18/19 | servos, fans, dimming | only 2 hardware PWM channels |
| I2S/PCM | GPIO18/19/20/21 | audio DACs/ADCs, MEMS mics | |
| CSI / DSI | MIPI connectors | camera / display | not on the 40-pin; ribbon |
| PCIe | Pi 5 only | NVMe SSD, Hailo/Coral via HAT | x1 external, Gen2 default, Gen3 hackable |

---

## 4. Pi vs Microcontroller — Linux Is a Feature and a Curse

The single most important conceptual divide: **a Pi runs a preemptive multitasking OS; a microcontroller runs your code and nothing else.**

| Property | Raspberry Pi (Linux) | MCU (STM32, bare metal/RTOS) |
|---|---|---|
| Determinism | **No** — scheduler, IRQs, page faults | **Yes** — you own every cycle |
| Boot time | 10–30 s | microseconds–milliseconds |
| Interrupt latency | tens of µs to *ms* (kernel) | < 1 µs (NVIC) |
| GPIO toggle rate | ~MHz, jittery (userspace) | tens of MHz, exact |
| Memory protection | MMU, virtual memory | usually none (flat physical) |
| Power | 2–12 W | µW–mW |
| Cold-start safety | filesystem can corrupt | runs from flash, robust |
| Best at | networking, vision, ML, files | hard real-time control, low power |

The correct architecture for a serious vehicle is **both**: a microcontroller (e.g., a Pixhawk/STM32 flight controller from [65-engineering-embedded-firmware.md](65-engineering-embedded-firmware.md)) closes the hard real-time inner loop at 1 kHz with guaranteed timing, and the Pi sits beside it as the **mission computer** doing vision, planning, and ML — talking to the MCU over UART/SPI. The Pi *never* directly stabilizes the airframe. This "companion computer" split is the industry-standard pattern (e.g., PX4 + a Pi/Jetson over MAVLink).

---

## 5. Real-Time on Linux — How People Make the Pi Behave

Stock Raspberry Pi OS is a **throughput-optimized, fair-scheduling** desktop kernel. Its worst-case latency under load can be tens of milliseconds. For soft-real-time work you fight back:

1. **`PREEMPT_RT` kernel.** The real-time patch set makes nearly all kernel code preemptible, converts most spinlocks to sleeping locks, and turns IRQ handlers into kernel threads you can prioritize. It cuts worst-case latency from ~10 ms to ~100 µs on a Pi 4. You build it or use an RT image.
2. **CPU isolation.** Boot with `isolcpus=3 nohz_full=3 rcu_nocbs=3` to remove core 3 from the scheduler's general pool, then pin your control thread to it with `taskset`/`pthread_setaffinity_np`. That core now runs essentially one thing.
3. **`SCHED_FIFO` priority.** Run the loop with `chrt -f 80` (real-time scheduling class) so the fair scheduler can't preempt it for a `apt` job.
4. **Lock memory.** `mlockall(MCL_CURRENT|MCL_FUTURE)` to prevent page faults; preallocate everything — no `malloc` in the loop (the [04-foundations-modern-cpp-realtime.md](04-foundations-modern-cpp-realtime.md) discipline).
5. **Kill the jitter sources.** Disable swap, throttle/disable journald flushes, turn off Wi-Fi power save, fix the CPU governor to `performance` (no DVFS clock changes mid-loop).

```bash
# Pin and prioritize a control process on an isolated core
sudo chrt -f 80 taskset -c 3 ./flight_companion
# Confirm the governor isn't changing clocks under you
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
```

The honest framing (from [82-software-real-time-operating-systems.md](82-software-real-time-operating-systems.md)): even with all of this, a Pi gives you **soft** real-time — good enough for a 200 Hz vision-aided loop, *not* good enough to be the sole stabilizer of an inherently unstable airframe. Know the difference or someone gets hurt.

---

## 6. Power and Thermal Reality

The Pi's datasheet power number is a polite fiction; the field number is set by your workload.

| Model | Idle | CPU-loaded | + accelerator/USB | Recommended PSU |
|---|---|---|---|---|
| Pi 4B | ~2.7 W | ~6.4 W | ~8–10 W | 5 V / 3 A (15 W) |
| Pi 5 | ~3 W | ~9 W | ~12–25 W | 5 V / 5 A (27 W, USB-PD) |

Key realities:

- **The Pi 5 demands 5 V at 5 A over USB-C PD.** With a non-PD supply it throttles peripherals (limits USB/PCIe current). Budget the *real* 27 W.
- **Throttling is silent.** The BCM2711/2712 throttles at **80–85 °C**. Under sustained AI load with no heatsink, a Pi 5 hits this in seconds and quietly halves your throughput — your "slow model" is actually a cooling failure. Always run with a heatsink + fan (the Active Cooler) or a metal case. Watch it: `vcgencmd measure_temp` and check `vcgencmd get_throttled` (`throttled=0x0` is what you want; bit flags reveal under-voltage and throttle events).
- **Power is roughly $P \approx C V^2 f$** for the digital core (see [110-hardware-foundations-no-software-without-hardware.md](110-hardware-foundations-no-software-without-hardware.md)). The DVFS governor scales $f$ (and effectively $V$); pinning to `performance` trades watts for determinism.
- **Inrush and brownout kill fielded Pis.** At boot the board pulls a current spike; a marginal regulator sags below the **4.63 V under-voltage threshold**, and you get the lightning-bolt warning, SD corruption, or a reboot. On a vehicle, the Pi shares a bus with motors whose transients dwarf it — you **must** give the Pi its own well-decoupled buck regulator, not a tap off the motor rail. This is straight out of [68-engineering-power-electronics.md](68-engineering-power-electronics.md).

---

## 7. Storage — Why You Stop Booting From SD

The microSD card is the Pi's original sin. It is the single most common field failure.

- **Flash wear:** consumer microSD has limited program/erase cycles and weak wear-leveling. A logging workload that writes constantly will wear out a cheap card in weeks. Power-loss during a write corrupts the FAT/ext4 structures — and the Pi pulls power ungracefully all the time.
- **The fix:** boot from **USB SSD** (Pi 4) or **NVMe SSD over PCIe** (Pi 5, via an M.2 HAT), or use the **Compute Module's onboard eMMC** for embedded products. eMMC has managed wear-leveling and is soldered — no card to vibrate loose on a drone.
- **Mitigations if you must use SD:** mount root read-only with an overlay filesystem (`overlayroot`), move logs to `tmpfs`/RAM, use industrial/pSLC cards, and design clean power-down. Treat the SD as firmware, not as a database.

| Medium | Endurance | Power-loss safety | Use case |
|---|---|---|---|
| Consumer microSD | low | poor | prototyping only |
| Industrial SD (pSLC) | medium | better | constrained fielding |
| USB SSD | high | good | Pi 4 products |
| NVMe (PCIe) | high | good | Pi 5 high-throughput |
| eMMC (CM4/CM5) | high, managed | good | embedded products |

---

## 8. Compute Module — Designing a Real Product

When you ship a *product* (not a prototype), you do not solder a consumer Pi into a chassis. You design around the **Compute Module (CM4 / CM5)**: the same SoC + RAM (+ optional eMMC + optional wireless) on a **SO-DIMM-style or high-density connector**, with *all* the I/O brought out to two 100-pin connectors for **you** to route on your own carrier board.

Why the CM is the right answer for embedded:

- **You design the carrier** — exactly the connectors, power, and protection your product needs, no HDMI/USB you'll never use.
- **Onboard eMMC** removes the SD card failure mode entirely.
- **Industrial temperature** variants and long-term availability (Raspberry Pi commits to multi-year supply) make it designable-in.
- **PCIe is exposed** on the CM4/CM5 — connect an NVMe SSD or a Hailo-8 AI accelerator directly.

```
   Designing a CM5-based edge computer — checklist
   ┌─────────────────────────────────────────────────────────┐
   │ 1. Power: dedicated 5 V buck (≥5 A), wide-input front    │
   │    end (e.g. 9–36 V vehicle → 5 V), TVS + reverse-       │
   │    polarity protection, big bulk + local decoupling.     │
   │ 2. Sequencing/brownout: supervisor IC holds reset until  │
   │    rails are valid; watchdog + clean shutdown on power-  │
   │    fail (supercap gives ~2 s to flush + halt).           │
   │ 3. Storage: CM with eMMC, OR route PCIe to an M.2 NVMe.  │
   │ 4. I/O: level-shift every external 3.3 V line that       │
   │    leaves the board; ESD-protect connectors.             │
   │ 5. Thermal: SoC heat path to chassis (thermal pad to an  │
   │    aluminum lid); size for sustained, not peak.          │
   │ 6. Comms to MCU: isolated/decoupled UART or SPI to the   │
   │    flight controller; never share the motor rail.        │
   │ 7. Boot: program eMMC via the CM's USB device mode       │
   │    (rpiboot) on the line; lock the boot order in EEPROM. │
   └─────────────────────────────────────────────────────────┘
```

This is the bridge from "hobbyist who flashes an SD" to "engineer who ships a fielded box," and it draws directly on the PCB and power discipline of [78-engineering-pcb-and-electronics-design.md](78-engineering-pcb-and-electronics-design.md) and [68-engineering-power-electronics.md](68-engineering-power-electronics.md).

---

## 9. The Pi as an Edge-AI and Robotics Computer

The modern reason the Pi matters in autonomy: it is a cheap, Linux-native host for cameras and AI accelerators — but **the CPU/GPU alone are poor at neural inference.** The VideoCore is a graphics/video engine, not a tensor engine; a Pi 5 CPU runs a small YOLO at single-digit FPS. The answer is an **accelerator**:

| Accelerator | Interface | Throughput | Notes |
|---|---|---|---|
| Hailo-8 / 8L | PCIe (Pi 5 AI HAT/Kit) | up to ~26 / 13 TOPS | best Pi 5 inference path |
| Google Coral Edge TPU | USB / M.2 | ~4 TOPS (INT8) | TFLite-only, INT8-only |
| Pi 5 CPU (A76 ×4) | — | ~a few hundred GOPS | fallback / preprocessing |

Pair this with the **CSI camera** (MIPI ribbon → on-SoC ISP for debayering and tuning) and you have the canonical edge-vision stack: camera → ISP → INT8 model on Hailo → detections → planner on the CPU → commands to the MCU. The model side — quantization to INT8, meeting the latency/power budget — is exactly the discipline of [64-autonomy-edge-inference-deployment.md](64-autonomy-edge-inference-deployment.md). The Pi's job is to be the honest, well-cooled, well-powered *host* that lets that model hit its deadline frame after frame.

The verdict for a drone or rover: **Pi 5 + Hailo + CSI camera + an isolated MCU for control** is a legitimate, low-cost fielded autonomy brain — *if and only if* you respect §5 (real-time limits), §6 (power/thermal), and §7 (storage). Ignore those and it is a science fair project that dies on the first cold morning.

---

## Sources & further study

- *BCM2711 / BCM2712 ARM Peripherals* datasheets — Raspberry Pi Ltd (the authoritative register-level reference).
- *Raspberry Pi Compute Module 4 / 5 Datasheet* and *CM4 IO Board* design files — the canonical carrier-board reference design.
- *Raspberry Pi Hardware Documentation* (raspberrypi.com/documentation) — boot, `config.txt`, device tree overlays, `rpi-eeprom-config`.
- ARM *Cortex-A76 Technical Reference Manual* and *ARMv8-A Architecture Reference Manual* — what the CPU actually does.
- *Linux Foundation PREEMPT_RT* documentation and `cyclictest` (rt-tests) — measuring and reducing real-time latency.
- Hailo-8 and Google Coral Edge TPU datasheets and developer guides — accelerator integration.
- Brendan Gregg, *Systems Performance* — Linux scheduling, latency, and observability that apply directly to taming the Pi.
- *Making Embedded Systems*, Elecia White — the companion-computer / MCU split mindset.

> Framing note: The Raspberry Pi rewards engineers who refuse to treat it as magic. Underneath the friendly Python is a Broadcom application processor running a fair-scheduling OS off a wear-prone flash card, powered by a marginal supply, throttling silently when it gets warm. Master those four truths — the SoC, the scheduler, the storage, and the power/thermal envelope — and the Pi becomes a serious instrument. Ignore them and it becomes the thing that fails in the field at the worst possible moment.
