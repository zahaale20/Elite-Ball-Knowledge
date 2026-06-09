# Power Electronics — Converters, Motor Drives & Power Delivery

> **Why this exists.** Every drone, satellite, ground robot, and electric aircraft runs on a battery or bus at one voltage and needs a dozen others: 3.3 V for the MCU, 5 V for sensors, 12 V for a gimbal, hundreds of volts and tens of amps to spin a propulsion motor. Power electronics is the discipline of converting electrical energy from one form to another *efficiently* — because every watt you waste becomes heat you must remove and range you lose. A motor drive that's 95% efficient instead of 85% can be the difference between a 30-minute flight and a 25-minute one, or between a power stage that runs cool and one that melts. The engineer who masters switching converters and motor drives controls the single subsystem that turns stored energy into useful work.

> **What mastering it makes you.** The person who designs the power stage that doesn't catch fire, the motor drive that delivers full torque silently and efficiently, and the power architecture that survives a battery sag during a hard maneuver — competence that sits at the literal center of every electromechanical system.

Power electronics is where the firmware of [65-engineering-embedded-firmware.md](65-embedded-firmware.md) (the MCU/FPGA generating the gate signals), the thermal physics of [72-engineering-thermal-management.md](72-thermal-management.md) (where the losses go), and the propulsion of [69-engineering-propulsion-and-electric-propulsion.md](69-propulsion-and-electric-propulsion.md) (what the motor drives) all meet. The control loops that regulate a converter and run field-oriented control come straight from [25-autonomy-control-theory.md](../autonomy/25-control-theory.md), and the energy and efficiency arguments are pure [01_first_principles_systems_engineering.md](../foundations/01-first_principles_systems_engineering.md). The math of switching waveforms and averaging is the calculus and Laplace-domain analysis of [03-foundations-mathematics.md](../foundations/03-mathematics.md).

---

## 1. The core idea: switch, don't burn

There are two ways to convert 12 V to 5 V. A **linear regulator** drops the extra 7 V across a transistor — burning $7\text{ V} \times I$ as heat. At 1 A that's 7 W wasted to deliver 5 W: 42% efficient. A **switching converter** instead chops the input with a transistor switching on and off thousands of times per second and uses an inductor and capacitor to average the result — wasting almost nothing because an ideal switch dissipates zero power (it's either fully on, no voltage across it, or fully off, no current through it).

$$ P_{\text{linear}} = (V_{\text{in}} - V_{\text{out}})\cdot I_{\text{out}} \quad\text{vs.}\quad \eta_{\text{switching}} > 90\% $$

This is the founding insight: **modulate, then filter.** A switch generates a square wave whose *average* is the output you want; the LC filter removes the switching ripple and leaves the DC. Everything else is detail.

| | Linear | Switching |
|---|---|---|
| Efficiency | (Vout/Vin), poor for big drops | 85–98% |
| Heat | High | Low |
| Noise | Very clean | Switching ripple/EMI |
| Cost/size | Small, cheap | Inductor/cap, more complex |
| Use | Low-noise analog, small drops | Everything power-hungry |

---

## 2. The buck converter — stepping voltage down

The buck (step-down) converter is the workhorse. A high-side switch connects the input to an inductor for a fraction $D$ (the duty cycle) of each switching period; a diode or synchronous switch carries the inductor current the rest of the time. The inductor smooths current; the output capacitor smooths voltage.

```
Vin ──[ SW ]──┬──[ L ]──┬──► Vout
              │         │
            [diode]   [Cout]   Load
              │         │
             GND ──────┴──── GND
```

In steady state, the inductor's volt-seconds must balance over a cycle (it can't accumulate flux forever), which gives the governing relation:

$$ V_{\text{out}} = D \cdot V_{\text{in}}, \qquad D = \frac{t_{\text{on}}}{T_{\text{sw}}} \in [0,1] $$

So a 50% duty cycle halves the voltage. The inductor ripple current and output voltage ripple are the design knobs:

$$ \Delta I_L = \frac{(V_{\text{in}} - V_{\text{out}})\,D}{L\,f_{\text{sw}}}, \qquad \Delta V_{\text{out}} = \frac{\Delta I_L}{8\,C\,f_{\text{sw}}} $$

Higher switching frequency $f_{\text{sw}}$ shrinks the inductor and capacitor (smaller, lighter — critical for flight) but increases switching losses. This frequency-vs-loss tradeoff is the central tension of converter design, and it's why GaN/SiC devices (which switch faster with less loss) are revolutionizing aerospace power.

---

## 3. The boost converter — stepping voltage up

The boost (step-up) converter does the opposite: it stores energy in the inductor while the switch is on (input shorted through L to ground), then releases it in series with the input when the switch opens, pumping the output above the input.

$$ V_{\text{out}} = \frac{V_{\text{in}}}{1 - D} $$

As $D \to 1$, output theoretically goes to infinity (in practice limited by losses). Boost converters drive LED strings, charge high-voltage buses, and appear in maximum-power-point trackers for solar. The **buck-boost** and **SEPIC** topologies handle cases where the input can be above *or* below the output (a battery that sags from 4.2 V to 3.0 V while the load needs 3.3 V).

| Topology | Relation | Use |
|---|---|---|
| Buck | $V_o = D V_i$ | Step down (rails) |
| Boost | $V_o = V_i/(1-D)$ | Step up (HV bus) |
| Buck-Boost | $V_o = -V_i D/(1-D)$ | Either direction |
| Flyback | isolated, ratio set by turns + D | Isolated supplies |
| Full-bridge | isolated, high power | Big DC-DC, chargers |

---

## 4. The real losses — where efficiency goes to die

Ideal switches are lossless; real ones aren't. Four loss mechanisms dominate, and managing them *is* power-stage design:

**Conduction loss** — the switch has on-resistance $R_{DS(on)}$, so it burns $I^2 R$ while conducting:

$$ P_{\text{cond}} = I_{\text{rms}}^2 \, R_{DS(on)} \cdot D $$

**Switching loss** — during the finite transition between on and off, voltage and current overlap, dissipating energy each switching event:

$$ P_{\text{sw}} = \tfrac{1}{2}\, V_{\text{in}}\, I_{\text{load}}\, (t_{\text{rise}} + t_{\text{fall}})\, f_{\text{sw}} $$

This scales with frequency — the reason you can't push $f_{\text{sw}}$ arbitrarily high. It's also why **soft-switching** (resonant topologies that switch at zero voltage or current) matters for high-frequency, high-efficiency designs.

**Gate drive loss** — charging the MOSFET's gate capacitance every cycle: $P_{\text{gate}} = Q_g V_{\text{gs}} f_{\text{sw}}$.

**Magnetic & capacitor losses** — core hysteresis/eddy losses and ESR in the output cap.

Total efficiency:

$$ \eta = \frac{P_{\text{out}}}{P_{\text{out}} + P_{\text{cond}} + P_{\text{sw}} + P_{\text{gate}} + P_{\text{mag}}} $$

Every one of these losses becomes heat that [72-engineering-thermal-management.md](72-thermal-management.md) must remove. A 1 kW motor drive at 95% efficiency dumps 50 W into a heatsink — manageable. At 85%, it's 150 W — a thermal crisis. Efficiency is not a luxury; it's a thermal and range constraint.

---

## 5. Gate drive — the unglamorous detail that blows things up

A power MOSFET or IGBT is voltage-controlled, but its gate is a capacitor that must be charged and discharged *fast* (amps of peak current for nanoseconds) to switch cleanly. A weak gate drive leaves the device in its lossy linear region too long, overheating it. A **gate driver** IC provides this current punch and the level-shifting to drive a high-side switch whose source floats at the input voltage.

Critical gate-drive concerns:

- **Dead time.** In a half-bridge, both switches must never conduct simultaneously (shoot-through = a dead short across the bus = instant destruction). The driver inserts dead time, but too much dead time distorts the output.
- **Bootstrap / isolated supply** for the high-side gate (its reference floats).
- **Miller plateau & dv/dt immunity** — fast switching can falsely turn on the opposite device through parasitic coupling.
- **Gate resistor** trades switching speed against ringing and EMI.

```
        Vbus
         │
       [Q_high] ◄── high-side driver (bootstrapped)
         │
         ├──── phase node ──► to motor/inductor
         │
       [Q_low]  ◄── low-side driver
         │
        GND      dead time between them = survival
```

This is where firmware ([65-engineering-embedded-firmware.md](65-embedded-firmware.md)) meets power: the MCU's timer peripheral generates complementary PWM *with hardware dead-time insertion* precisely so shoot-through is impossible even if software glitches.

---

## 6. BLDC/PMSM motors — how electric propulsion actually moves

The brushless DC (BLDC) and permanent-magnet synchronous motor (PMSM) are the muscles of modern robotics and electric flight. A rotor of permanent magnets spins inside a stator of three-phase windings. There are no brushes; instead, electronics (the ESC, electronic speed controller) energize the windings in sequence to keep pulling the rotor around.

The torque comes from the interaction of stator current and rotor flux:

$$ \tau = \frac{3}{2}\, p\, \lambda_m\, i_q $$

where $p$ is pole pairs, $\lambda_m$ the magnet flux linkage, and $i_q$ the torque-producing (quadrature) current. The back-EMF the spinning rotor generates opposes the supply and sets the speed limit:

$$ V_{\text{bemf}} = K_e \,\omega, \qquad \tau = K_t \, I $$

with the motor constant linking them. Crucially $K_t$ (N·m/A) and $K_e$ (V·s/rad) are numerically equal in SI — a consequence of energy conservation. Hobby motors are rated in **Kv** (RPM per volt), the inverse of $K_e$.

---

## 7. Field-Oriented Control — the algorithm that makes it smooth

Simple six-step commutation (energize one pair of phases at a time) is crude and torque-rippley. **Field-Oriented Control (FOC)** is the technique that makes electric motors silent, efficient, and precisely controllable — the reason a modern drone or robot arm moves so cleanly.

The insight: a three-phase AC motor is hard to control in its native rotating frame, so transform the stator currents into a frame that rotates *with the rotor*, where they become two DC quantities:

- $i_d$ (direct axis) — aligned with the magnets; produces no torque (set to 0 for max efficiency).
- $i_q$ (quadrature axis) — perpendicular; produces all the torque.

The transforms:

$$ \text{Clarke: } \begin{bmatrix} i_\alpha \\ i_\beta \end{bmatrix} = \frac{2}{3}\begin{bmatrix} 1 & -\frac{1}{2} & -\frac{1}{2} \\ 0 & \frac{\sqrt3}{2} & -\frac{\sqrt3}{2} \end{bmatrix}\begin{bmatrix} i_a \\ i_b \\ i_c \end{bmatrix} $$

$$ \text{Park: } \begin{bmatrix} i_d \\ i_q \end{bmatrix} = \begin{bmatrix} \cos\theta & \sin\theta \\ -\sin\theta & \cos\theta \end{bmatrix}\begin{bmatrix} i_\alpha \\ i_\beta \end{bmatrix} $$

Now you control $i_d$ and $i_q$ with simple PI loops ([25-autonomy-control-theory.md](../autonomy/25-control-theory.md)), transform back, and feed **space-vector PWM** to the gate drivers. The whole loop runs at 10–40 kHz on the MCU/FPGA.

```
ia,ib,ic ─► Clarke ─► Park ─► [PI on id,iq] ─► inv Park ─► SVPWM ─► gates ─► motor
   ▲                  ▲                                                       │
   │              rotor angle θ ◄───── encoder / sensorless estimator ◄───────┘
   └──────────────── current sense (shunt/Hall) ─────────────────────────────┘
```

**Sensorless FOC** estimates rotor angle from back-EMF or a flux observer, eliminating the encoder — standard in drone ESCs. This algorithm, running thousands of times per second, is what converts a battery and three wires into precise, efficient thrust.

---

## 8. Power architecture — the system view

A real vehicle has a power *tree*, not a single converter. The battery feeds a high-voltage bus; converters branch off to each subsystem at its required voltage, each isolated and protected.

```
Battery (e.g. 6S, ~22V) ─┬─► ESC ×4 ──► propulsion motors (full bus)
                         ├─► Buck 12V ──► gimbal, payload
                         ├─► Buck 5V  ──► companion computer, sensors
                         └─► Buck 3.3V ─► flight controller MCU
```

Design concerns at the architecture level:

- **Sequencing.** Some rails must come up before others (the MCU's core before its I/O) or chips latch up. Power-management ICs handle this.
- **Sag and inrush.** A hard throttle pulls huge current; bus voltage sags, browning out logic if the architecture isn't decoupled. Bulk capacitance and separate logic rails prevent this.
- **Protection.** Over-current, over-voltage, reverse-polarity, and fusing. A shorted ESC must not take down the flight controller.
- **Battery management (BMS).** Lithium cells need per-cell balancing, over-discharge protection, and accurate state-of-charge estimation — a flight that runs a cell below ~3.0 V damages it permanently.

The energy budget ties to range: usable energy $E = V \cdot Q$ (Wh), and flight time is energy divided by total power draw — dominated by propulsion. A 5% efficiency gain in the motor drive directly extends endurance, which is why power electronics is a top-tier lever in [69-engineering-propulsion-and-electric-propulsion.md](69-propulsion-and-electric-propulsion.md).

---

## 9. Magnetics — the components nobody respects enough

The inductor and transformer are where energy is stored and converted, and they're the hardest parts to get right. Core selection (ferrite for high frequency, powdered iron for high current), saturation (above a flux limit the inductor stops being an inductor and current spikes destructively), and winding losses (skin and proximity effect at high frequency) all matter.

$$ V_L = L\frac{di}{dt}, \qquad E = \tfrac{1}{2}L I^2, \qquad B = \frac{N I}{\ell}\mu \;<\; B_{\text{sat}} $$

Saturation is a hard cliff: design with margin, because a saturated inductor in a converter is a near-short. Transformer design adds turns ratios (for isolation and voltage scaling) and leakage inductance (which causes voltage spikes the snubber must absorb).

---

## 10. EMI — the noise you create and must contain

Fast switching (high $dv/dt$ and $di/dt$) radiates and conducts electromagnetic interference that can corrupt sensors, jam your own radio ([67-engineering-rf-and-comms-systems.md](67-rf-and-comms-systems.md)), or fail certification. Mitigation is layout and filtering:

- **Tight switching loops** — minimize the loop area carrying high $di/dt$ to reduce radiated EMI (this is the #1 PCB-layout rule for power stages).
- **Input/output filtering** — common-mode chokes and X/Y capacitors.
- **Snubbers** — RC or RCD networks that damp ringing on the switch node.
- **Spread-spectrum clocking** — dither $f_{\text{sw}}$ to smear emissions across frequencies.
- **Shielding and grounding** discipline.

A power stage that works on the bench but kills GPS lock in flight is an EMI failure, and it's a common, painful one.

---

## 11. Wide-bandgap semiconductors — the current revolution

Silicon MOSFETs are being displaced by **GaN** (gallium nitride) and **SiC** (silicon carbide) devices in high-performance power electronics. They switch faster, with lower losses, and tolerate higher voltages and temperatures.

| | Silicon | GaN | SiC |
|---|---|---|---|
| Switching speed | Baseline | Very fast | Fast |
| On-resistance | Baseline | Low | Low (high V) |
| Max temp | ~150°C | ~150°C | ~200°C+ |
| Voltage range | All | ≤ ~650 V | ≥ 650 V, kV-class |
| Sweet spot | General | Compact, high-freq | High-voltage, hot |

For aerospace, the payoff is **power density**: a GaN-based DC-DC can be a fraction the size and weight of its silicon equivalent at the same power. Weight is everything in flight, so wide-bandgap is rapidly becoming standard in electric propulsion inverters and onboard converters.

---

## 12. Tooling and ecosystem

| Need | Tools |
|---|---|
| Circuit simulation | LTspice, PLECS, SIMetrix, QSPICE |
| Converter design | TI WEBENCH, vendor design tools |
| Motor control dev | STM32 MotorControl SDK, ODrive, VESC, SimpleFOC |
| PCB layout | KiCad, Altium (power-aware layout) |
| Magnetics | core vendor tools (Ferroxcube, Würth) |
| Measurement | scope + current probe, power analyzer, thermal camera |
| Control | MATLAB/Simulink, embedded C on STM32/TI C2000 |

The open-source **VESC** and **ODrive** projects are superb learning platforms — real FOC motor drives whose firmware and hardware you can study end to end.

---

## Sources & further study

- Robert Erickson & Dragan Maksimović, *Fundamentals of Power Electronics* — the definitive graduate text.
- Ned Mohan, Undeland & Robbins, *Power Electronics: Converters, Applications, and Design* — broad and practical.
- Marian Kazimierczuk, *Pulse-Width Modulated DC-DC Power Converters* — rigorous converter analysis.
- Bimal Bose, *Modern Power Electronics and AC Drives* — motor drives and FOC.
- Austin Hughes, *Electric Motors and Drives* — superb intuition before the math.
- Horowitz & Hill, *The Art of Electronics* (3rd ed.) — the analog and gate-drive reality.
- Sanjaya Maniktala, *Switching Power Supplies A–Z* — practical, debugging-oriented.
- Texas Instruments and Infineon application notes — the real-world design guides practitioners actually use.

> Framing note: Power electronics is the discipline of moving energy without wasting it, and it punishes carelessness immediately — a wrong gate-drive detail, a saturated inductor, or a sloppy switching loop turns into smoke, not a warning message. Master it and you control the conversion at the heart of every electromechanical system: the place where stored energy becomes thrust, motion, and capability.
