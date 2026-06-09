# FPGAs & Hardware Acceleration — When Software Isn't Fast Enough

> **Why this exists.** There is a hard ceiling to what a sequential processor can do. When a radar must correlate returns at gigasamples per second, when a sensor fusion pipeline must process 4K imagery at the camera's native frame rate with bounded, sub-microsecond latency, or when an electronic-warfare receiver must detect and classify a pulse in nanoseconds, a CPU running an instruction at a time simply cannot keep up. FPGAs let you build the exact digital circuit your problem needs — thousands of operations literally happening in parallel each clock — and ASICs cast that circuit in permanent silicon. The engineer who knows when and how to move computation into hardware unlocks performance regimes that software engineers cannot reach.

> **What mastering it makes you.** The rare person who can read a signal-processing requirement, decide whether it belongs on a CPU, GPU, FPGA, or ASIC, and then actually close timing on the FPGA — a skill that gates entire defense and aerospace programs.

FPGA work sits where the determinism obsession of [04-foundations-modern-cpp-realtime.md](../foundations/04-modern-cpp-realtime.md) becomes physical: there is no operating system, no jitter, just clocks and logic. It extends the firmware world of [01-engineering-embedded-firmware.md](01-embedded-firmware.md) into true parallelism, and the DSP and linear algebra it implements come straight from [03-foundations-mathematics.md](../foundations/03-mathematics.md). The systems-engineering tradeoff framing of [01_first_principles_systems_engineering.md](../foundations/01-first_principles_systems_engineering.md) governs the central question — *should this be in hardware at all?* — and the assurance arguments of [09-foundations-safety-assurance.md](../foundations/09-safety-assurance.md) (specifically DO-254 for airborne hardware) decide whether your design can fly. It pairs with [03-engineering-rf-and-comms-systems.md](03-rf-and-comms-systems.md) (SDR back-ends are FPGAs) and [04-engineering-power-electronics.md](04-power-electronics.md) (FPGA-timed motor control).

---

## 1. What an FPGA actually is

A Field-Programmable Gate Array is a sea of configurable logic that you wire up after manufacturing. It is not a processor running your program — it *becomes* the circuit you describe. The fundamental fabric:

- **LUTs (Look-Up Tables):** tiny memories (typically 6-input) that implement any Boolean function of their inputs. This is the universal logic primitive.
- **Flip-flops (registers):** store one bit, clocked. LUT + FF together form a "logic cell" or "slice."
- **DSP slices:** hardened multiply-accumulate units (e.g., Xilinx DSP48: a 27×18 multiplier + accumulator). The currency of signal processing.
- **Block RAM (BRAM):** on-chip dual-port memory, kilobits each, hundreds to thousands of blocks.
- **Routing fabric:** the configurable interconnect — and the thing that usually limits your clock speed.
- **I/O blocks, clock managers (MMCM/PLL), transceivers (multi-Gbps SerDes).**

```
   ┌─────┬─────┬─────┬─────┐
   │ CLB │ CLB │ BRAM│ CLB │   CLB = LUTs + FFs
   ├─────┼─────┼─────┼─────┤
   │ CLB │ DSP │ CLB │ DSP │   DSP = hardened MAC
   ├─────┼─────┼─────┼─────┤   routing = sea of wires
   │ CLB │ CLB │ CLB │ CLB │          between them
   └─────┴─────┴─────┴─────┘
```

A modern AMD/Xilinx UltraScale+ device has hundreds of thousands of LUTs, thousands of DSP slices, tens of megabits of BRAM, and serial transceivers running at 28+ Gbps. You "program" it by loading a **bitstream** that configures every LUT's truth table and every routing switch.

---

## 2. HDL — describing hardware, not writing software

You design FPGAs in a **Hardware Description Language** (Verilog/SystemVerilog or VHDL). The mental shift that trips up every software engineer: **HDL describes structure that exists simultaneously, not steps that execute in sequence.** Two `always` blocks are two physical circuits running at once, every clock, forever.

```verilog
// A registered adder: this is a physical adder + register.
module accumulator #(parameter W = 16) (
    input  wire            clk,
    input  wire            rst_n,
    input  wire            valid,
    input  wire [W-1:0]    din,
    output reg  [W+3:0]    sum     // extra bits to prevent overflow
);
    always @(posedge clk) begin
        if (!rst_n)      sum <= '0;
        else if (valid)  sum <= sum + din;
    end
endmodule
```

Key distinctions you must internalize:

- **`<=` (non-blocking)** in clocked blocks models registers updating together on the edge. **`=` (blocking)** models combinational logic. Mixing them wrong creates simulation/synthesis mismatches — bugs that pass in simulation and fail in silicon.
- **Combinational logic** (LUTs) computes continuously; **sequential logic** (FFs) samples on a clock edge.
- Everything is **fixed width**. There is no `int`; there is `[15:0]`. Overflow is your responsibility.

---

## 3. The clock is everything: timing closure

An FPGA design runs at a target clock frequency. Between any two registers sits combinational logic with a finite propagation delay. For the design to work, every signal must arrive at the next register *before* its clock edge. This is the **setup constraint**, and satisfying it everywhere is **timing closure** — the central discipline of FPGA design.

$$ T_{\text{clk}} \;\ge\; t_{\text{clk-q}} + t_{\text{logic}} + t_{\text{routing}} + t_{\text{setup}} - t_{\text{skew}} $$

If the longest combinational path (the **critical path**) exceeds your clock period, the tools report **negative slack** and the design fails. Your options:

1. **Pipeline.** Insert registers to break a long path into shorter stages. This increases latency (more clocks) but raises throughput (higher clock) — usually the right trade.
2. **Parallelize.** Use more hardware to do more per clock.
3. **Reduce logic depth.** Restructure the math (e.g., tree adders instead of chains).

$$ \text{slack} = T_{\text{required}} - T_{\text{arrival}}, \qquad \text{slack} \ge 0 \text{ required} $$

The other timing hazard is the **hold constraint** (a signal must *not* arrive too soon), usually fixed automatically but deadly across clock domains.

---

## 4. Pipelining — the core throughput technique

Pipelining is to FPGAs what it is to a CPU: overlap work in stages so a new result emerges every clock even though each result takes several clocks end to end. Consider a 4-stage multiply-accumulate filter tap:

```
din ─►[reg]─►[× coef]─►[reg]─►[+ acc]─►[reg]─► out
      stage1   stage2    stage3  stage4
```

Latency = 4 clocks. **Throughput = 1 result/clock.** At 300 MHz that's 300 million taps/second per lane — and you instantiate hundreds of lanes in parallel. This is the structural source of the FPGA's advantage: a CPU does one MAC per core per cycle; an FPGA does thousands.

$$ \text{Throughput}_{\text{FPGA}} = N_{\text{parallel lanes}} \times f_{\text{clk}}, \qquad N \approx \frac{\#\text{DSP slices}}{\text{DSPs per lane}} $$

---

## 5. Fixed-point DSP — math without a floating-point unit

FPGAs *can* do floating point, but it's expensive (latency, DSP/LUT cost). High-rate signal processing uses **fixed-point** arithmetic: integers with an implied binary point. A `Q2.14` number uses 2 integer bits and 14 fractional bits in a 16-bit word, representing values in $[-2, 2)$ with resolution $2^{-14}$.

$$ x_{\text{real}} = \frac{x_{\text{int}}}{2^{f}}, \qquad \text{where } f = \text{fractional bits} $$

The engineering is in **bit-growth management**. Multiplying two Q2.14 numbers yields a Q4.28 result (widths add); accumulating $N$ of them needs $\lceil \log_2 N \rceil$ guard bits to avoid overflow. You must consciously decide where to **truncate or round** and where to **saturate** (clamp instead of wrapping — wrapping turns a max-positive into max-negative, a catastrophic glitch in a control signal).

| Operation | Input format | Output format | Hazard |
|---|---|---|---|
| Add | Qa.b + Qa.b | Q(a+1).b | overflow → saturate |
| Multiply | Qa.b × Qc.d | Q(a+c).(b+d) | width doubles |
| Accumulate ×N | Qa.b | Q(a+⌈log₂N⌉).b | guard bits |
| Truncate | Qa.b | Qa.(b−k) | rounding error / DC bias |

Quantization noise sets your effective SNR; the rule of thumb is ~6 dB per bit:

$$ \text{SNR}_{\text{dB}} \approx 6.02\,B + 1.76 $$

So a 14-bit datapath buys ~86 dB of dynamic range — enough for most radar/SDR front-ends, and a number you trade against logic cost.

---

## 6. The classic FPGA workloads

Where hardware acceleration earns its keep:

- **FIR/IIR filters & FFTs.** Streaming, deterministic, massively parallel. A pipelined FFT processes a sample every clock.
- **Matrix math / beamforming.** Phased-array radar steers beams by applying per-element phase shifts in real time — pure parallel MAC.
- **Image/video pipelines.** Debayer, undistort, stereo-match at sensor frame rate with line-buffer architectures.
- **Protocol handling & SerDes.** 10/40/100G Ethernet, JESD204 ADC links, custom low-latency links — line-rate packet parsing no CPU can match.
- **Cryptography.** AES/SHA pipelines at line rate.
- **Real-time control & EW.** Nanosecond-deterministic loops; pulse detection and DRFM (digital RF memory) in electronic warfare — see [08-autonomy-counter-uas-ew.md](../autonomy/08-counter-uas-ew.md).

---

## 7. FPGA vs GPU vs ASIC vs CPU — the decision

This is the systems decision the whole module builds toward. There is no universally best engine; there is the right engine for *this* problem's latency, throughput, power, volume, and flexibility constraints.

| Dimension | CPU | GPU | FPGA | ASIC |
|---|---|---|---|---|
| Parallelism | Few cores | Thousands of threads | Spatial, custom | Spatial, custom |
| Latency | Low, but jittery | High (batching) | **Lowest, deterministic** | Lowest |
| Throughput | Low | **Very high (batch)** | High (streaming) | Highest |
| Power efficiency | Poor | Moderate | Good | **Best** |
| Flexibility | **Total** | High (CUDA) | Reconfigurable | None (fixed) |
| NRE cost | None | None | Low-moderate | **Millions** |
| Unit cost | Low | Moderate | Moderate-high | **Low at volume** |
| Time to change | Instant | Hours | Days (resynth) | Months + respin |
| Best when | Control, branchy | Batched throughput | Low-latency streaming | High volume, fixed |

Heuristics that hold up in practice:

- **Branchy, irregular, control-heavy logic → CPU.** FPGAs hate branches.
- **Massive regular throughput, latency-tolerant, can batch → GPU.** Training, large batched inference.
- **Streaming, hard real-time, low/deterministic latency, line-rate I/O → FPGA.** Radar front-ends, SDR, sensor fusion, EW.
- **Astronomical volume with a frozen algorithm → ASIC.** A guided-munition seeker shipping by the tens of thousands; the NRE amortizes and you win on power and unit cost. Below ~$10^6$ units, an FPGA usually wins on total cost because you skip the multi-million-dollar mask set.

$$ \text{Cost}_{\text{ASIC}} = \text{NRE} + n \cdot c_{\text{die}}, \quad \text{Cost}_{\text{FPGA}} = n \cdot c_{\text{FPGA}}; \quad \text{ASIC wins when } n > \frac{\text{NRE}}{c_{\text{FPGA}} - c_{\text{die}}} $$

---

## 8. SoC FPGAs — the best of both worlds

Modern devices (Xilinx Zynq / Zynq UltraScale+, Intel Agilex/Stratix SoC) put hardened ARM Cortex-A cores (the **PS**, processing system) next to the FPGA fabric (the **PL**, programmable logic) on one die, joined by high-bandwidth AXI interconnect. The pattern is powerful: run Linux and your control/mission logic on the ARM, offload the latency-critical streaming math to the PL.

```
┌───────────────── Zynq UltraScale+ ──────────────────┐
│  PS (ARM A53 ×4, Linux)  ◄── AXI ──►  PL (fabric)   │
│  - mission logic                      - FFT/FIR     │
│  - networking                         - ADC capture │
│  - file system                        - real-time   │
└─────────────────────────────────────────────────────┘
```

This is the architecture of essentially every modern SDR (USRP, RFSoC) and most advanced sensor payloads. The RFSoC even integrates gigasample ADCs/DACs directly — the antenna nearly touches the FPGA.

---

## 9. HLS — raising the abstraction

Writing pipelined fixed-point HDL by hand is slow. **High-Level Synthesis** (Xilinx Vitis HLS, Intel HLS) compiles C/C++ with pragmas into RTL, letting you express the algorithm in software and direct the hardware structure with hints.

```cpp
void fir(const data_t x[N], const coef_t h[T], data_t &y) {
#pragma HLS PIPELINE II=1          // new input every clock
    acc_t acc = 0;
    for (int i = 0; i < T; i++) {
#pragma HLS UNROLL                 // all taps in parallel
        acc += x[i] * h[i];
    }
    y = acc >> SHIFT;              // requantize
}
```

HLS is excellent for complex datapaths and rapid exploration; the directives (`PIPELINE`, `UNROLL`, `DATAFLOW`, `ARRAY_PARTITION`) are how you control the resulting architecture. But HLS is not magic — you still must understand the hardware it generates, manage fixed-point types (`ap_fixed`), and verify timing. It lowers the barrier; it does not remove the need to think in hardware.

---

## 10. Verification — you cannot single-step silicon

There is no debugger that halts a running FPGA the way GDB halts a CPU (halting would change the very timing you care about). Verification is therefore front-loaded and rigorous:

- **Simulation (the primary tool).** A testbench drives stimulus and checks responses in a simulator (Verilator — fast, free, open; or vendor sims like Vivado/Questa). You verify functionality here, exhaustively, before touching hardware.
- **Self-checking testbenches & assertions.** SystemVerilog assertions catch protocol violations.
- **Coverage-driven & constrained-random** (UVM) for complex blocks — drive randomized legal stimulus, measure what you've exercised.
- **On-chip logic analyzers** (Xilinx ILA, Intel SignalTap) capture real signals into BRAM and stream them out for inspection — your window into live silicon.
- **Formal verification** for critical properties (e.g., a FIFO never overflows).

For airborne hardware, **DO-254** governs this process with the same rigor DO-178C applies to software — requirements traceability, verification evidence, and design assurance levels. See [09-foundations-safety-assurance.md](../foundations/09-safety-assurance.md).

---

## 11. The design flow end to end

```
Spec ─► HDL/HLS ─► Simulate ─► Synthesize ─► Place & Route ─► Timing ─► Bitstream ─► Hardware
         │            │            │              │             │           │
       (RTL)     (functional)  (LUT mapping)  (physical)   (slack≥0?)   (load to PL)
                      └─────────── iterate until correct & timing-clean ──┘
```

1. **Synthesis** maps your HDL to LUTs/FFs/DSPs.
2. **Place & route** assigns each element to a physical location and wires it — the slow, NP-hard step.
3. **Static timing analysis** checks every path against your clock constraints.
4. If timing fails: pipeline, refactor, add constraints, repeat. This loop is where the hours go.
5. **Bitstream generation** produces the configuration file you load.

Resource and timing reports are your dashboard: LUT/FF/DSP/BRAM utilization (don't exceed ~80% or routing congests), and worst negative slack (must be ≥ 0).

---

## 12. Tooling and ecosystem

| Need | Tools |
|---|---|
| Vendors | AMD/Xilinx (Vivado, Vitis), Intel/Altera (Quartus), Lattice, Microchip |
| Open-source synth | Yosys, nextpnr (Lattice iCE40/ECP5) |
| Simulation | Verilator (fast, free), Icarus, Questa, VCS |
| HLS | Vitis HLS, Intel HLS, Bambu (open) |
| Languages | SystemVerilog, VHDL, Chisel (Scala-based), SpinalHDL, Amaranth (Python) |
| Verification | cocotb (Python testbenches), UVM, SymbiYosys (formal) |
| Debug | ILA/SignalTap, Verilator traces (VCD/GTKWave) |
| Boards | Arty, Zybo, KR260, RFSoC, Alveo (datacenter) |

Start cheap: a Lattice iCE40 with the fully open Yosys/nextpnr flow teaches the entire pipeline on a laptop. Graduate to Zynq/RFSoC for real sensor work.

---

## Sources & further study

- Pong P. Chu, *FPGA Prototyping by SystemVerilog Examples* — hands-on, board-oriented.
- Clifford Cummings, "Nonblocking Assignments in Verilog Synthesis" — the paper that fixes the `<=`/`=` confusion.
- Harris & Harris, *Digital Design and Computer Architecture* — the bridge from logic to systems.
- Steve Kilts, *Advanced FPGA Design* — pipelining, timing, area/speed tradeoffs from a practitioner.
- Richard Lyons, *Understanding Digital Signal Processing* — the DSP your fabric implements.
- Uwe Meyer-Baese, *Digital Signal Processing with FPGAs* — fixed-point DSP architectures.
- AMD/Xilinx UG901 (Synthesis), UG949 (UltraFast timing closure) — the real reference manuals.
- RTCA DO-254 — design assurance for airborne electronic hardware.

> Framing note: An FPGA is the purest expression of "make the machine fit the problem." Where software bends the problem to fit a fixed processor, hardware design builds the processor the problem deserves. The engineer who can decide *whether* to do that — and then close timing when the answer is yes — operates a lever most of the industry cannot even reach.
