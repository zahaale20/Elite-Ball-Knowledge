# Embedded Firmware — Bare Metal, RTOS & Driving Real Hardware

> **Why this exists.** Every autonomous vehicle, missile seeker, flight controller, and smart munition is ultimately a microcontroller toggling pins at precise instants in time. The gap between an elegant control law on a whiteboard and a drone that holds altitude in gusty wind is firmware: the code that reads a gyro over SPI within 50 microseconds of a data-ready interrupt, runs the estimator, and writes a PWM duty cycle to an ESC before the next loop tick. If you cannot reason about interrupt latency, DMA bus contention, and where your variables live in physical memory, your "real-time" system is a hopeful guess. This module makes you the engineer who can be trusted with the inner loop that keeps hardware from killing itself.

> **What mastering it makes you.** The person who can bring up a new board from a blank STM32 and a schematic, debug a bus that locks up once an hour, and guarantee a control loop closes deterministically — the rarest and most defensible skill in any robotics or defense hardware team.

Embedded firmware is where the abstractions of [01_first_principles_systems_engineering.md](01_first_principles_systems_engineering.md) meet copper and silicon. The C++ discipline of [04-foundations-modern-cpp-realtime.md](04-foundations-modern-cpp-realtime.md) governs how you write deterministic, allocation-free code here; the safety arguments of [09-foundations-safety-assurance.md](09-foundations-safety-assurance.md) are what force you to prove your watchdog actually resets a hung MCU. The mechanical realities of [13-career-mechanical-engineering.md](13-career-mechanical-engineering.md) explain why your IMU mounting matters, and the linear-algebra and numerical-stability material in [03-foundations-mathematics.md](03-foundations-mathematics.md) is what your fixed-point filters depend on. This module is the foundation of the "Engineering Across Domains" band; it pairs tightly with [66-engineering-fpga-and-hardware-accel.md](66-engineering-fpga-and-hardware-accel.md) (when firmware isn't fast enough), [68-engineering-power-electronics.md](68-engineering-power-electronics.md) (what your gate-drive firmware commands), and [72-engineering-thermal-management.md](72-engineering-thermal-management.md) (why your MCU throttles).

---

## 1. The microcontroller as a physical machine

A microcontroller unit (MCU) is not a tiny PC. It is a CPU core, a fixed map of memory and peripherals, and a clock tree, all on one die. Take the STM32F405 (ARM Cortex-M4F, the workhorse of the open-source flight controller world): a 168 MHz core with a single-precision FPU, 192 KB SRAM, 1 MB flash, and dozens of memory-mapped peripherals.

The defining idea is the **memory map**. Everything — RAM, flash, GPIO registers, timers, the DMA controller — lives at a fixed physical address. Writing firmware is writing specific values to specific addresses at specific times.

```
0x0000_0000  Aliased boot region (flash, SRAM, or bootloader)
0x0800_0000  Flash (code + const data)
0x1000_0000  CCM RAM (core-coupled, 64 KB, no DMA access!)
0x2000_0000  SRAM (192 KB, DMA-accessible)
0x4000_0000  Peripherals (GPIO, TIM, SPI, I2C, UART, ...)
0xE000_0000  Cortex-M private bus (NVIC, SysTick, SCB)
```

That CCM RAM footnote is the kind of detail that separates working firmware from a three-day debugging session: the DMA engine physically cannot reach core-coupled memory. Put a DMA buffer there and the transfer silently fails.

A register access in C is just a volatile pointer dereference:

```c
#define GPIOA_BASE   0x40020000UL
#define GPIO_ODR     0x14
#define GPIOA_ODR    (*(volatile uint32_t *)(GPIOA_BASE + GPIO_ODR))

GPIOA_ODR |=  (1u << 5);   // set PA5 high
GPIOA_ODR &= ~(1u << 5);   // set PA5 low
```

`volatile` is mandatory: it tells the compiler the value can change outside the program's control (hardware) and must not be optimized into a cached register. Forgetting `volatile` on a status-register poll is a classic infinite-loop bug.

---

## 2. The clock tree — nothing happens without it

Every peripheral is clocked, and most are gated off at reset to save power. Before you can use SPI1, you must enable its clock in the RCC (Reset and Clock Control) block. The single most common "my peripheral is dead" bug is a forgotten clock-enable.

The clock tree on an STM32 typically multiplies a crystal up through a PLL:

$$ f_{\text{core}} = f_{\text{HSE}} \cdot \frac{N}{M \cdot P} $$

With an 8 MHz external crystal (HSE), $M=8, N=336, P=2$ gives $f_{\text{core}} = 8 \cdot \frac{336}{16} = 168\text{ MHz}$. The peripheral buses (APB1, APB2) are then divided down from this. Get the divider wrong and your UART baud rate is off by 2× and nothing communicates.

```
HSE 8MHz ──► /M ──► ×N ──► PLL ──► /P ──► SYSCLK 168MHz
                                    │
                                    ├─► AHB  /1  ─► 168MHz (core, DMA, SRAM)
                                    ├─► APB1 /4  ─►  42MHz (TIM2-7, I2C, USART2-3)
                                    └─► APB2 /2  ─►  84MHz (TIM1/8, SPI1, USART1)
```

A subtle trap: timer clocks are *doubled* when their APB prescaler is not 1. A TIM2 on a /4 APB1 actually clocks at 84 MHz, not 42. This single rule has corrupted countless PWM frequencies.

---

## 3. Interrupts — responding to the physical world

The CPU executes your main loop, but the world doesn't wait. An interrupt is a hardware signal that forces the CPU to drop what it's doing, save context, jump to an Interrupt Service Routine (ISR), and resume afterward. This is how a gyro's data-ready line, a UART byte arrival, or a timer overflow gets serviced in microseconds.

The Cortex-M's **NVIC** (Nested Vectored Interrupt Controller) manages priorities and nesting. Key concepts:

| Concept | Meaning | Why it matters |
|---|---|---|
| Vector table | Array of ISR addresses at flash start | Wrong entry → HardFault |
| Priority | Lower number = higher priority | Sets preemption order |
| Preemption | High-priority ISR interrupts low one | Needed for tight control loops |
| Latency | Cycles from event to ISR first instruction | ~12 cycles on Cortex-M4 |
| Tail-chaining | Back-to-back ISRs skip stack restore | Reduces overhead |

**Interrupt latency** is the deterministic budget you must respect. On a 168 MHz M4, 12 cycles of entry latency is ~71 ns. But if you've disabled interrupts in a long critical section, or a lower-priority ISR is masking, your *effective* latency balloons. This is why you measure **worst-case** latency, not typical.

The cardinal rules of ISR design:

1. **Keep ISRs short.** Set a flag, read one register, hand off to the main loop. Never `printf` or `malloc` in an ISR.
2. **Share data with `volatile` and atomics.** A variable written in an ISR and read in main must be `volatile`; multi-byte updates need critical sections or atomic types.
3. **Beware priority inversion.** A low-priority task holding a resource a high-priority task needs is a real-time killer; see [09-foundations-safety-assurance.md](09-foundations-safety-assurance.md).

```c
volatile uint32_t g_imu_ready = 0;

void EXTI4_IRQHandler(void) {   // gyro DRDY pin
    EXTI->PR = (1u << 4);       // clear pending (write-1-to-clear)
    g_imu_ready = 1;            // hand off; do real work in main loop
}
```

---

## 4. DMA — moving data without the CPU

Direct Memory Access (DMA) is a separate engine that shuttles data between peripherals and memory while the CPU does other work. For a flight controller reading six 16-bit IMU registers at 8 kHz over SPI, doing each byte in an ISR would saturate the core. DMA does it transparently and interrupts you only when the whole block is done.

```
        ┌───────┐  request   ┌─────────┐
SPI1 ───┤ RXNE  ├───────────►│   DMA   │
 RX     └───────┘            │ Stream  │──► SRAM buffer[6]
                             └────┬────┘
                                  │ Transfer Complete IRQ
                                  ▼
                            main loop processes
```

The hidden cost is **bus contention**: DMA and the CPU share the AHB bus matrix. A DMA storm can stall the core, adding jitter to your control loop. This is where the bus matrix's multiple master ports matter — an STM32F4 lets DMA hit SRAM while the core runs from flash with zero contention, but core+DMA both hitting SRAM serializes. Floor-planning your buffers across SRAM banks is a real optimization.

**Double-buffering** (ping-pong) lets you process buffer A while DMA fills buffer B, guaranteeing you never read a half-written block — a tearing bug that produces garbage sensor frames.

---

## 5. Peripheral buses — talking to chips

Your MCU is surrounded by sensors and actuators connected over standard buses. Know all four cold.

### 5.1 UART — asynchronous serial

No shared clock; both ends agree on a baud rate. Frame: start bit, 8 data bits, optional parity, stop bit. Baud error must stay under ~2% or framing fails. Used for GPS (NMEA), telemetry radios (MAVLink), and debug consoles.

$$ \text{Baud error} = \frac{f_{\text{actual}} - f_{\text{desired}}}{f_{\text{desired}}} $$

### 5.2 SPI — fast synchronous, full-duplex

Master drives clock (SCK) and chip-select (CS); data flows both ways on MOSI/MISO every clock edge. Tens of MHz. The IMU's bus of choice because it's fast and simple. Four "modes" set by clock polarity (CPOL) and phase (CPHA) — mismatch them and you read shifted garbage.

```
CS   ‾‾\_______________________/‾‾
SCK  ____|‾|_|‾|_|‾|_|‾|_|‾|_|‾|____
MOSI ----<D7><D6><D5><D4><D3><D2>--
```

### 5.3 I2C — two wires, many devices

SDA + SCL, open-drain with pull-ups, 100 kHz/400 kHz/1 MHz. Each device has a 7-bit address. Great for low-rate sensors (barometer, magnetometer) because it's just two pins for a whole bus. Its weakness: a glitched device can hold SDA low and **lock the entire bus**. Robust firmware includes a bus-recovery routine that clocks SCL nine times to free a stuck slave.

### 5.4 CAN — the robust vehicle bus

Differential pair, dominant/recessive bits, built-in arbitration and error handling. The backbone of automotive and increasingly of drones (DroneCAN/UAVCAN). Messages are prioritized by ID; lower ID wins arbitration non-destructively. CAN's error-confinement (active → passive → bus-off) is genuine fault-tolerance engineering you should study.

| Bus | Wires | Speed | Topology | Typical use |
|---|---|---|---|---|
| UART | 2 (TX/RX) | ≤ a few Mbaud | point-to-point | GPS, telemetry |
| SPI | 4+ | tens of MHz | star (per-CS) | IMU, flash, displays |
| I2C | 2 | ≤ 1 MHz | multi-drop | baro, mag, EEPROM |
| CAN | 2 (diff) | ≤ 1 Mbit (8M FD) | bus | actuators, ESCs |

---

## 6. Timers, PWM, and capturing time

Timers are the most versatile peripheral. A counter increments at a clocked rate and triggers events on match/overflow. Three core uses:

**PWM generation** — drive ESCs, servos, LEDs. Set the auto-reload (ARR) for period and capture-compare (CCR) for duty:

$$ f_{\text{PWM}} = \frac{f_{\text{TIM}}}{(\text{PSC}+1)(\text{ARR}+1)}, \qquad D = \frac{\text{CCR}}{\text{ARR}+1} $$

For a 400 Hz ESC update from an 84 MHz timer: pick PSC and ARR so the product is 210,000. A common choice gives 1 µs resolution, mapping the 1000–2000 µs servo pulse cleanly.

**Input capture** — timestamp an edge. Measure an RC receiver's pulse width or a tachometer's period with sub-microsecond precision.

**Encoder mode** — decode quadrature signals from a motor encoder in hardware, counting position with zero CPU load.

---

## 7. Bootloaders and firmware update

Fielded hardware must update without a JTAG probe. A **bootloader** is a small program that runs first, decides whether to accept new firmware (over UART, CAN, USB, or radio), writes it to flash, validates it, and jumps to the application.

```
flash layout:
0x0800_0000 ┌──────────────┐
            │  Bootloader  │  immutable, validates app
0x0800_8000 ├──────────────┤
            │ App metadata │  CRC, version, valid flag
0x0800_C000 ├──────────────┤
            │ Application  │  the real firmware
            └──────────────┘
```

Critical design points: a **CRC or signature check** before jumping (don't run corrupt firmware), an **A/B partition** scheme so a failed update rolls back, and a **jump sequence** that deinitializes peripherals and relocates the vector table (`SCB->VTOR`). For defense systems, the bootloader is also a security boundary — secure boot verifies a cryptographic signature, tying into the assurance chain in [09-foundations-safety-assurance.md](09-foundations-safety-assurance.md).

---

## 8. Real-time: bare metal vs RTOS

Two architectures dominate.

**Super-loop (bare metal):** `while(1)` runs tasks in sequence, paced by a timer tick. Simple, fully deterministic, and what most flight controllers (Betaflight, early PX4) used. The risk: one slow task delays everything. You manage timing by hand.

```c
while (1) {
    if (g_tick_1khz) { g_tick_1khz = 0;
        read_imu();          // 8 kHz via DMA, latched here
        run_estimator();     // EKF, see module 53
        run_controller();    // PID/LQR, see module 25
        write_motors();      // PWM/DShot
    }
    handle_telemetry();      // background, low priority
}
```

**RTOS (FreeRTOS, Zephyr, ChibiOS):** a scheduler runs prioritized tasks, preempting on demand. You get clean separation (a comms task, a control task, a logging task) and primitives (mutexes, queues, semaphores). The cost is complexity and the need to reason about priority inversion and stack sizing per task.

The decisive concept for both is the **real-time guarantee**. A hard-real-time loop must close within its deadline *every* cycle, not on average. You prove this by bounding worst-case execution time (WCET) and worst-case interrupt latency. Tools: cycle counters (`DWT->CYCCNT`), a scope on a GPIO toggled at loop start/end (the cheapest, most honest timing tool ever), and static analysis. This is the same WCET discipline demanded in [04-foundations-modern-cpp-realtime.md](04-foundations-modern-cpp-realtime.md).

| | Super-loop | RTOS |
|---|---|---|
| Determinism | Highest (you control everything) | High (with care) |
| Complexity | Low | Medium-high |
| Multi-rate tasks | Manual | Native |
| Memory overhead | Tiny | Per-task stacks + kernel |
| Best for | Tight inner loops | Mixed-criticality systems |

---

## 9. Memory: stack, heap, and why you avoid `malloc`

SRAM is split into the stack (grows down, holds locals and call frames) and the heap (dynamic allocation). In hard-real-time and safety-critical firmware, **dynamic allocation is banned or heavily restricted** (MISRA C, DO-178C). Reasons: `malloc` has non-deterministic timing, fragments memory over time, and can fail unpredictably mid-flight.

Instead: static allocation, fixed pools, and stack discipline. A **stack overflow** — the stack growing into your variables — is a silent, catastrophic corruption. Defenses: a stack-painting check (fill stack with a pattern, watch the high-water mark), the Cortex-M's MPU to fault on overflow, and generous static sizing.

The MPU (Memory Protection Unit) is underused gold: mark flash read-only, stack no-execute, and a guard region as no-access, and a wild pointer faults immediately instead of corrupting state. For DAL-A avionics this is effectively mandatory.

---

## 10. Debugging real hardware

You will spend more time debugging than writing. Build the muscle.

- **GPIO + oscilloscope/logic analyzer.** Toggle a pin, watch timing. Irreplaceable for catching jitter and bus glitches a debugger hides (halting the core changes the timing).
- **SWD/JTAG with GDB + OpenOCD.** Breakpoints, watchpoints, register inspection. A watchpoint on a corrupted variable finds the rogue writer fast.
- **Fault handlers.** A HardFault means something went wrong; a good handler dumps the stacked PC, LR, and fault status registers (CFSR, HFSR, BFAR) so you can decode the faulting instruction.
- **SEGGER RTT / semihosting** for low-overhead logging without a UART.
- **Power analysis.** Current spikes reveal a peripheral misbehaving; brownouts reset the MCU mysteriously.

```c
void HardFault_Handler(void) {
    __asm volatile (
        "tst lr, #4        \n"  // which stack pointer?
        "ite eq            \n"
        "mrseq r0, msp     \n"
        "mrsne r0, psp     \n"
        "b hardfault_report\n"  // r0 = stacked frame
    );
}
```

---

## 11. A concrete bring-up: blank board to flying loop

The arc of bringing up a custom flight controller, in order — each step gates the next:

1. **Power & clock.** Confirm 3.3 V rails, get the PLL locked, blink an LED at a *measured* 1 Hz. If the LED rate is wrong, your clock tree config is wrong.
2. **Debug access.** SWD working, can halt/flash. Without this, you're blind.
3. **Serial console.** UART printf at the right baud — your eyes into the system.
4. **One sensor.** Read the IMU "WHO_AM_I" register over SPI. A correct ID byte proves bus mode, wiring, and clock are all right.
5. **DMA + interrupts.** Move IMU sampling to DMA at rate, validate no dropped frames.
6. **Actuators.** Generate PWM/DShot, confirm on a scope, spin a motor *with props off*.
7. **Close the loop.** Estimator + controller at fixed rate, validate timing with a GPIO toggle on a scope.
8. **Failsafes.** Watchdog, brownout, RC-loss behavior — the things that keep it from becoming a lawn dart.

Every step produces evidence. "It probably works" is how hardware gets destroyed.

---

## 12. Tooling and ecosystem

| Need | Tools |
|---|---|
| Compiler | arm-none-eabi-gcc, LLVM, IAR, Keil |
| Flash/debug | OpenOCD, pyOCD, J-Link, ST-Link |
| RTOS | FreeRTOS, Zephyr, ChibiOS, ThreadX |
| HAL/config | STM32CubeMX, libopencm3 (lean), bare CMSIS |
| Analysis | logic analyzer (Saleae), scope, DWT cycle counter |
| Build | CMake, Make, PlatformIO |
| Standards | MISRA C, CERT C, DO-178C, AUTOSAR |

Prefer understanding registers (CMSIS, libopencm3) over leaning entirely on vendor HALs — the HAL hides exactly the timing details you must control. Use the HAL to bring up fast, then drop to registers in the hot path.

---

## Sources & further study

- Joseph Yiu, *The Definitive Guide to ARM Cortex-M3 and Cortex-M4 Processors* — the canonical core reference.
- ST Microelectronics, *RM0090 Reference Manual* (STM32F4) — read the actual register descriptions; this is the real textbook.
- Elecia White, *Making Embedded Systems* — pragmatic architecture and design.
- Jack Ganssle, *The Art of Designing Embedded Systems* and his essays on debouncing, watchdogs, and stacks.
- Richard Barry, *Mastering the FreeRTOS Real Time Kernel* (free PDF).
- Horowitz & Hill, *The Art of Electronics* (3rd ed.) — for the analog reality your pins connect to.
- Phillip Koopman, *Better Embedded System Software* — reliability and safety-minded firmware.
- MISRA C:2012 guidelines — the rule set for safety-critical C.

> Framing note: Firmware is the layer where physics stops being a model and becomes a deadline. The engineer who internalizes that every line of code costs cycles, every bus has worst-case latency, and every variable has a physical address is the one whose systems fly when the demo matters. Master this, and you become the person the hardware team cannot ship without.
