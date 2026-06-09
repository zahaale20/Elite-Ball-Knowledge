# PCB & Electronics Design — Schematic to Signal-Integrity

> **Why this exists.** Every modern system — flight controller, radio, sensor head, motor
> driver, battery management board — is a printed circuit board at its heart. The gap
> between a circuit that works on a breadboard and one that works at 100 MHz on a vibrating,
> hot, electrically noisy vehicle is bridged by PCB design: how you draw the schematic, lay
> out the copper, route the power and ground, and respect signal integrity and EMI. A board
> that "works on the bench" but radiates, couples noise into the IMU, or browns out the MCU
> under motor load is a board designed without these principles. Hardware that flies must be
> designed for the physics, not just the logic.
>
> **What mastering it makes you.** The engineer who reads a schematic and sees the current
> loops; who places the decoupling capacitor where it matters; who knows why a ground plane
> is non-negotiable and why a high-speed trace needs controlled impedance; and who designs a
> board that passes EMC the first time instead of chasing emissions in a chamber for weeks.

PCB design realizes the electrical interfaces defined in the ICDs of
[12-engineering-systems-engineering-mbse.md](12-systems-engineering-mbse.md)
and carries the signal conditioning of
[10-engineering-sensors-and-instrumentation.md](10-sensors-and-instrumentation.md)
and the motor drivers of [09-engineering-mechatronics-and-actuation.md](09-mechatronics-and-actuation.md).
It is constrained by the power budget of [15-engineering-batteries-and-energy-storage.md](15-batteries-and-energy-storage.md),
the manufacturability rules of [11-engineering-manufacturing-and-dfm.md](11-manufacturing-and-dfm.md)
(applied to boards), and the derating/thermal limits of
[13-engineering-reliability-and-failure-analysis.md](13-reliability-and-failure-analysis.md).
The first-principles habit of reasoning from Maxwell rather than rules-of-thumb is
[01_first_principles_systems_engineering.md](../foundations/01-first_principles_systems_engineering.md),
and every board is validated through the test regime of
[06-foundations-simulation-test-verification.md](../foundations/06-simulation-test-verification.md).

---

## Table of Contents

1. [The PCB stack and the design flow](#1-the-pcb-stack-and-the-design-flow)
2. [Schematic capture done right](#2-schematic-capture-done-right)
3. [Power delivery & decoupling](#3-power-delivery--decoupling)
4. [Ground planes & return current](#4-ground-planes--return-current)
5. [Signal integrity & controlled impedance](#5-signal-integrity--controlled-impedance)
6. [EMI / EMC](#6-emi--emc)
7. [Layout, thermal & DFM for boards](#7-layout-thermal--dfm-for-boards)
8. [Tools & verification](#8-tools--verification)
9. [Practice this week](#9-practice-this-week)
10. [Sources & further study](#10-sources--further-study)

---

## 1. The PCB stack and the design flow

A PCB is layers of copper separated by dielectric (FR-4, the standard glass-epoxy). The
**stack-up** — how many layers and what each does — is the first and most consequential
decision.

| Layers | Typical use | Notes |
|---|---|---|
| 2 | simple, low-speed | no continuous ground plane → noise prone |
| 4 | most products | signal / GND / PWR / signal — the workhorse |
| 6–8 | high-speed, dense | dedicated planes, controlled impedance |
| 8+ | RF, FPGA, fast memory | many planes, buried vias |

A good 4-layer stack puts **signal–ground–power–signal**, so every signal layer is adjacent
to a solid plane (essential for return current, §4). The design flow:

```
requirements → schematic → component selection → layout (placement) →
routing → power/ground planes → DRC → SI/PI check → fab files (Gerber) →
assembly drawing → fab + assembly → bring-up → EMC test
```

Each stage feeds the next; mistakes upstream (wrong stack-up, bad part choice) are expensive
to fix downstream. The board is, in MBSE terms
([12](12-systems-engineering-mbse.md)), the physical realization of a set of
electrical interfaces — design it from the ICD outward.

---

## 2. Schematic capture done right

The schematic is the *intent*; the layout is the *implementation*. A clean schematic
prevents a class of layout bugs. Principles:

- **Draw current loops, not just connections.** Every signal has a return path; show power
  and ground explicitly so the loops are visible.
- **One function per sheet/block.** Power, MCU, sensors, radio — hierarchical sheets keep it
  readable.
- **Decoupling caps next to every IC** on the schematic (and the layout, §3).
- **Net names that mean something** (`3V3_MCU`, `MOSI`, `IMU_INT`), so the netlist and DRC
  are debuggable.
- **Design-in test points** and debug headers (SWD/JTAG) — you cannot probe what you did not
  expose.
- **Pin-1 indicators, polarity, and footprints** verified against the datasheet — a wrong
  footprint kills a board spin.

The schematic drives the **netlist**, which drives layout connectivity and the **DRC**
(design rule check). Symbol/footprint libraries (KiCad's, or manufacturer-provided) must be
verified — a mismatched footprint is the most common and costly schematic-stage error,
a literal-interface failure of the kind §1 and the ICD discipline guard against.

---

## 3. Power delivery & decoupling

Digital ICs draw current in sharp transients as gates switch. The **Power Delivery Network
(PDN)** must supply that current with low impedance across frequency, or the supply rail
sags and the chip misbehaves. The transient current creates a voltage droop across any
inductance:

$$ V_\text{droop} = L\frac{di}{dt} $$

A switching edge with $di/dt$ of amps-per-nanosecond across even a few nH of trace/lead
inductance produces a damaging droop. **Decoupling capacitors** are local charge reservoirs
that supply the transient before the distant regulator can respond. The rules:

- **Place small caps (100 nF) as close as possible** to each power pin — the loop from cap
  to pin to ground must be tiny, because the *loop inductance* sets the high-frequency
  impedance, not the capacitance.
- **Use a hierarchy:** bulk (10–100 µF) at the regulator, mid (1–10 µF) per region, small
  (100 nF) per IC pin, and sometimes small high-freq (1–10 nF) for fast logic.
- **Minimize the via-to-plane path** — vias add inductance; short, fat connections matter.

A capacitor is not ideal; its impedance has a self-resonant frequency where lead inductance
takes over:
$$ f_\text{SRF} = \frac{1}{2\pi\sqrt{L_\text{ESL}\,C}} $$
Above $f_\text{SRF}$ the cap looks inductive — which is why you parallel different values to
keep low impedance across a wide band. PDN design is reliability design: a marginal rail is
an intermittent, maddening field failure ([13](13-reliability-and-failure-analysis.md)).

---

## 4. Ground planes & return current

The single most important layout fact: **current returns to its source, and at high frequency
it returns directly under the signal trace.** A signal trace over a solid ground plane has its
return current flowing in the plane immediately beneath it, minimizing the loop area — and
loop area is what radiates and picks up noise.

```
signal trace  ───────────────────  (top layer)
                |  |  |  return current follows
ground plane ───┴──┴──┴──────────  directly underneath (HF)
```

The return current's path is frequency-dependent: at DC it spreads to minimize resistance; at
high frequency it concentrates under the trace to minimize **inductance** (loop area). The
implications:

- **Never split a ground plane under a signal** — the return current is forced to detour
  around the gap, creating a huge loop that radiates and couples. The infamous "moat" rule.
- **Keep a continuous reference plane** adjacent to every signal layer.
- **Stitching vias** tie planes together and give return current a path when a signal changes
  layers — place a ground via next to every signal via on a high-speed net.
- **Star or single-point grounds** for mixed analog/digital, joining at one point, so digital
  return current does not flow through the analog ground (the grounding discipline of
  [10-engineering-sensors-and-instrumentation.md](10-sensors-and-instrumentation.md)).

Ground is not a passive "0 V everywhere" net — it is the return half of every signal loop, and
treating it as such separates working boards from radiating ones.

---

## 5. Signal integrity & controlled impedance

At low frequency a trace is a wire. When the signal's rise time becomes comparable to its
propagation delay down the trace, the trace becomes a **transmission line** and reflections,
ringing, and crosstalk appear. The rule of thumb: treat a trace as a transmission line when
its length exceeds about a sixth of the rise-time's spatial extent:

$$ \ell_\text{crit} \approx \frac{t_r \cdot v}{6} $$

where $v \approx c/\sqrt{\varepsilon_r}$ (on FR-4, $\varepsilon_r\approx4.3$, so $v\approx
15\,$cm/ns). Fast edges (USB, Ethernet, DDR, high-speed SPI) cross this threshold on
centimeter-scale traces.

A transmission line has a **characteristic impedance** $Z_0$ set by geometry. For a microstrip
(trace over a plane):
$$ Z_0 \approx \frac{87}{\sqrt{\varepsilon_r + 1.41}}\ \ln\!\left(\frac{5.98\,h}{0.8w + t}\right) $$
where $h$ is dielectric height, $w$ trace width, $t$ trace thickness. Designers target standard
impedances (50 Ω single-ended, 90/100 Ω differential for USB/Ethernet) by setting $w$ and $h$.

**Termination** matches the line to the load to kill reflections: the reflection coefficient
is
$$ \Gamma = \frac{Z_L - Z_0}{Z_L + Z_0} $$
which is zero when $Z_L = Z_0$. Series or parallel termination, length-matched differential
pairs, and reference-plane continuity are the SI toolkit. Crosstalk between adjacent traces is
controlled by spacing (the 3W rule) and by the ground plane that shrinks each trace's loop.

---

## 6. EMI / EMC

**Electromagnetic Compatibility** means the board neither emits harmful interference nor
malfunctions when others do — and certified products *must* pass EMC (FCC Part 15, CISPR/EN,
MIL-STD-461 for defense). Emissions come in two modes:

- **Differential-mode:** current loops act as small loop antennas; radiated power scales with
  loop area and the square of frequency — minimized by the ground-plane/return-path discipline
  of §4.
- **Common-mode:** unintended currents on cables and shields driven by ground bounce; often the
  dominant emitter — controlled by common-mode chokes, ferrites, and good chassis grounding.

The countermeasures, in order of effectiveness:

| Technique | Targets |
|---|---|
| Solid ground plane / small loops | radiated emissions (root cause) |
| Decoupling / clean PDN (§3) | switching noise injection |
| Slowest acceptable edge rates | high-frequency harmonics |
| Series resistors / ferrites on lines | ringing, common-mode |
| Shielding (cans, chassis) | last resort for stubborn emitters |
| Filtering at connectors | conducted emissions on cables |

MIL-STD-461 (CE/RE/CS/RS limits) is far stricter than commercial limits and is a hard gate for
defense hardware — EMC failure late in a program is schedule-killing, so design for it from the
stack-up. EMC is fundamentally the same loop-area and return-path physics as SI, viewed from the
antenna's perspective.

---

## 7. Layout, thermal & DFM for boards

Placement precedes routing and largely determines success:

- **Group by function and signal speed**; keep high-speed and sensitive analog apart.
- **Place decoupling and crystal circuits tight** to their ICs.
- **Keep the motor/power section physically separated** from the MCU and sensors (the
  magnetometer especially — §4 of [10](10-sensors-and-instrumentation.md)).
- **Orient connectors at the board edge**; respect mechanical/enclosure constraints (the
  mechanical ICD).

**Thermal:** copper is the heat spreader. Power devices need copper pour, thermal vias to inner
planes, and sometimes heatsinks. The junction temperature follows the thermal resistance chain:
$$ T_j = T_a + P\,(\theta_{jc} + \theta_{ca}) $$
Keeping $T_j$ low is direct reliability (Arrhenius, [13](13-reliability-and-failure-analysis.md)).

**DFM for boards** (the [11](11-manufacturing-and-dfm.md) mindset applied to
copper): respect the fab's minimum trace/space and drill, avoid acid traps (acute angles), give
adequate annular rings, use standard footprints with proper courtyards, add fiducials and
tooling holes for assembly, and follow IPC-2221/IPC-A-610 (acceptability) and IPC-7351 (land
patterns). A board that violates fab rules is rejected or yields poorly — a DFM cost just like
any mechanical part.

---

## 8. Tools & verification

| Tool | Role |
|---|---|
| **KiCad** | free, capable schematic + layout; the open-source standard |
| **Altium Designer** | industry workhorse; integrated, expensive |
| **Cadence Allegro / OrCAD** | high-end, complex boards |
| **ngspice / LTspice** | analog circuit simulation |
| **SI/PI simulators (HyperLynx, Ansys SIwave)** | impedance, reflections, PDN |
| **Gerber viewers** | verify fab output before sending |

Verification before fabrication is non-negotiable:
- **ERC** (electrical rule check) on the schematic — unconnected pins, conflicting drivers.
- **DRC** (design rule check) on the layout — clearance, width, via violations.
- **Netlist comparison** schematic-vs-layout — catches manual routing errors.
- **Impedance/length reports** for high-speed nets.
- **Gerber + drill review** — visually confirm the fab files match intent.

After fab comes **bring-up**: power the board through a current-limited supply, check rails in
order, then debug incrementally. This staged verification mirrors the V-model
([12](12-systems-engineering-mbse.md)) and the test discipline of
[06-foundations-simulation-test-verification.md](../foundations/06-simulation-test-verification.md):
prove each layer before building on it.

---

## 9. Practice this week

1. Design a simple 4-layer board in KiCad (MCU + IMU + regulator); set up the stack-up so every
   signal layer references a plane.
2. Place decoupling caps and compute the PDN: pick the cap hierarchy and estimate the
   self-resonant frequencies; keep loop inductance minimal.
3. Compute the controlled-impedance trace width for a 50 Ω microstrip on FR-4 with your fab's
   dielectric height; route one high-speed net with a reference plane and ground vias.
4. Run ERC + DRC, fix every violation, and review the Gerbers in a viewer before declaring the
   board "done."

---

## 10. Sources & further study

- **Horowitz & Hill — *The Art of Electronics*.** The foundational circuits reference.
- **Johnson & Graham — *High-Speed Digital Design: A Handbook of Black Magic*.** SI from first principles.
- **Ott — *Electromagnetic Compatibility Engineering*.** The EMC/grounding bible.
- **Bogatin — *Signal and Power Integrity — Simplified*.** Modern SI/PI with intuition.
- **IPC-2221 / IPC-7351 / IPC-A-610** — PCB design, land patterns, assembly acceptability.
- **MIL-STD-461** — defense EMC requirements, linking to [07-foundations-defense-acquisition.md](../foundations/07-defense-acquisition.md).
- **KiCad documentation and the Phil's Lab tutorials** — practical, hands-on board design.

> Framing note: A PCB is not a 2D drawing of connections — it is a 3D structure of current
> loops and transmission lines governed by Maxwell's equations. The engineers whose boards work
> the first time, pass EMC, and survive the field are the ones who design the ground return, the
> power delivery, and the signal impedance deliberately — because the copper, not the schematic,
> is where the physics lives.
