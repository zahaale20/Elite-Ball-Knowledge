# Batteries & Energy Storage — Chemistry, BMS & Pack Design

> **Why this exists.** Energy storage is the binding constraint on almost every untethered
> system: a drone's endurance, a robot's range, a missile's burn time, a satellite's eclipse
> survival. The battery is simultaneously the heaviest single subsystem, the most dangerous
> (thermal runaway is a fire that makes its own oxygen), and the one whose physics is least
> forgiving of wishful thinking. You cannot software your way out of a Joule shortfall. The
> engineer who understands cell chemistry, pack design, the battery management system, and the
> thermal/safety envelope is the one who sets — and meets — the endurance number that defines
> the whole vehicle.
>
> **What mastering it makes you.** The engineer who sizes a pack from the mission energy and
> power profile rather than guesswork; who reads a discharge curve and knows the usable
> capacity at the real C-rate and temperature; who designs a BMS that balances, protects, and
> estimates state-of-charge honestly; and who treats thermal runaway as a containment problem,
> not a probability to ignore.

Energy storage powers the actuators of [09-engineering-mechatronics-and-actuation.md](09-mechatronics-and-actuation.md)
(its bus-voltage sag limits motor performance), the boards of
[14-engineering-pcb-and-electronics-design.md](14-pcb-and-electronics-design.md)
(the PDN starts at the cell), and the sensors of
[10-engineering-sensors-and-instrumentation.md](10-sensors-and-instrumentation.md).
It is the endurance driver in the VTOL roadmap of [02-autonomy-vtol-roadmap.md](../autonomy/02-vtol-roadmap.md)
and a first-principles energy-budget problem per
[01_first_principles_systems_engineering.md](../foundations/01-first_principles_systems_engineering.md).
Pack manufacturing follows [11-engineering-manufacturing-and-dfm.md](11-manufacturing-and-dfm.md),
cell aging and safety are reliability problems per
[13-engineering-reliability-and-failure-analysis.md](13-reliability-and-failure-analysis.md),
the thermal-runaway hazard is a core case for [09-foundations-safety-assurance.md](../foundations/09-safety-assurance.md),
and the pack is a subsystem with hard interfaces in
[12-engineering-systems-engineering-mbse.md](12-systems-engineering-mbse.md).

---

## Table of Contents

1. [Energy, power, and the fundamental budget](#1-energy-power-and-the-fundamental-budget)
2. [Cell chemistries](#2-cell-chemistries)
3. [The cell as an electrical model](#3-the-cell-as-an-electrical-model)
4. [Pack design — series, parallel, formats](#4-pack-design--series-parallel-formats)
5. [The Battery Management System](#5-the-battery-management-system)
6. [State estimation — SoC and SoH](#6-state-estimation--soc-and-soh)
7. [Thermal runaway & safety](#7-thermal-runaway--safety)
8. [Charging & lifecycle](#8-charging--lifecycle)
9. [Practice this week](#9-practice-this-week)
10. [Sources & further study](#10-sources--further-study)

---

## 1. Energy, power, and the fundamental budget

Two quantities govern every battery decision, and conflating them is the classic beginner
error. **Energy** (Wh) is how much total work the pack can do; **power** (W) is how fast it can
deliver it.

$$ E = \int V(t)\,I(t)\,dt \approx V_\text{nom}\,Q \quad[\text{Wh}], \qquad
P = V\,I \quad[\text{W}] $$

where $Q$ is capacity in amp-hours. Endurance is energy divided by average power:
$$ t_\text{endurance} = \frac{E_\text{usable}}{P_\text{avg}} $$

The **C-rate** normalizes current to capacity: 1C discharges the pack in one hour, 2C in half
an hour. High C-rate hurts you twice — it raises internal $I^2R$ losses *and* reduces usable
capacity (the **Peukert effect**):

$$ t = \frac{Q_\text{rated}}{I^{\,k}}, \quad k > 1 $$

The two figures of merit:
- **Specific energy** (Wh/kg) — drives endurance and range. This is what limits flight time.
- **Specific power** (W/kg) — drives peak thrust/acceleration. This limits how hard you can pull.

A cell optimized for one sacrifices the other. The whole vehicle design starts here: the
mission energy and power profile, divided by cell specific energy/power, *is* the pack mass —
a pure [01_first_principles_systems_engineering.md](../foundations/01-first_principles_systems_engineering.md)
budget that no cleverness elsewhere can evade.

---

## 2. Cell chemistries

Chemistry sets the ceiling on everything else. The dominant families:

| Chemistry | Specific energy | Cycle life | Safety | Notes / use |
|---|---|---|---|---|
| LiCoO₂ (LCO) | ~150–200 Wh/kg | ~500 | poor | phones; high energy, fragile |
| NMC (LiNiMnCo) | ~150–220 Wh/kg | ~1000–2000 | moderate | EVs, drones; best all-round |
| LFP (LiFePO₄) | ~90–160 Wh/kg | ~2000–5000 | excellent | safe, long-life, lower energy |
| NCA | ~200–260 Wh/kg | ~1000 | moderate | Tesla; very high energy |
| LTO (Li titanate) | ~50–80 Wh/kg | ~10000+ | excellent | fast charge, huge life, low energy |
| Li-S (emerging) | ~400–500 Wh/kg | low (~100s) | research | endurance dream, cycle-life problem |
| Solid-state (emerging) | 300–500 Wh/kg | TBD | high (no liquid) | the next step-change |
| Li-polymer (pouch) | format, NMC inside | — | — | high power density, drones |

The chemistry trade is the master decision: **NMC/NCA** for maximum endurance (drones, EVs),
**LFP** when safety and cycle life dominate (storage, defense logistics where a fire is
unacceptable), **LTO** for extreme fast-charge/cycle-life. Lithium dominates because of the
fundamental electrochemistry: lithium's low atomic mass and high reduction potential give the
highest energy per kilogram of any practical chemistry — a physics fact, not a market accident.
Cell voltage comes from the electrode potential difference (~3.7 V nominal for Li-ion, ~3.2 V
for LFP).

---

## 3. The cell as an electrical model

For pack and BMS design, model the cell as a voltage source behind an impedance — the
**equivalent-circuit model** (ECM):

```
   +─────[ R0 ]──┬──[ R1 ]──┬── + terminal
                 |          |
  OCV(SoC)     [C1]       (more RC pairs
   (─)           |          for dynamics)
   +─────────────┴──────────┴── − terminal
```

The terminal voltage under load is the open-circuit voltage minus the IR drop and the
transient (diffusion) terms:
$$ V_\text{term} = V_\text{OCV}(\text{SoC}) - I R_0 - \sum_i V_{RC_i} $$

- $V_\text{OCV}(\text{SoC})$ is the **open-circuit voltage**, a nonlinear function of
  state-of-charge — the basis of voltage-based SoC estimation (§6). LFP's notoriously flat OCV
  curve is *why* coulomb counting is needed for LFP.
- $R_0$ is the **internal resistance** (ohmic) — it sets the instantaneous voltage sag under
  load and the $I^2R_0$ heat. It rises with age and falls with temperature.
- The **RC pairs** model the slower polarization/diffusion dynamics seen after a load step.

This model is identified from pulse-discharge tests and is the plant the BMS estimator runs on.
The voltage sag under a high-C pulse ($I R_0$) is exactly what browns out the motor bus of
[09-engineering-mechatronics-and-actuation.md](09-mechatronics-and-actuation.md)
and the board PDN of [14-engineering-pcb-and-electronics-design.md](14-pcb-and-electronics-design.md) —
pack impedance is a system-level constraint.

---

## 4. Pack design — series, parallel, formats

Cells are combined to hit the required voltage and capacity. The nomenclature is **sPm**:
$s$ cells in series, $m$ in parallel.

- **Series ($s$)** adds voltage: $V_\text{pack} = s \times V_\text{cell}$. A "6S" Li-po is
  $6 \times 3.7 = 22.2\,$V nominal ($25.2\,$V full).
- **Parallel ($m$)** adds capacity/current: $Q_\text{pack} = m \times Q_\text{cell}$.

$$ E_\text{pack} = s \cdot m \cdot V_\text{cell} \cdot Q_\text{cell} $$

| Format | Description | Pros | Cons |
|---|---|---|---|
| 18650 | cylindrical, 18×65 mm | cheap, robust, proven, easy to cool | packaging dead space |
| 21700 | cylindrical, 21×70 mm | more energy/cell, fewer welds | same |
| Pouch (Li-po) | flat, soft foil | high power density, conforms | needs compression, swells, fragile |
| Prismatic | rigid can | dense packing, large cells | heavier case |

**Pack engineering** beyond cell count:
- **Cell matching:** parallel cells share current; mismatched internal resistance causes uneven
  loading and hot spots. Series cells must be **balanced** (§5) — the weakest series cell limits
  the whole pack (the series-reliability tyranny of [13](13-reliability-and-failure-analysis.md)).
- **Interconnect:** nickel/copper busbars and spot-welds must carry the peak current without
  heating; resistance here is wasted energy and a fire risk.
- **Mechanical:** cells need compression (pouch), vibration isolation, and crash protection — a
  structural and DFM problem ([11](11-manufacturing-and-dfm.md)).
- **Thermal:** spacing and cooling paths to keep every cell in its window (§7).

---

## 5. The Battery Management System

A lithium pack without a **BMS** is a bomb on a timer. The BMS is the embedded system that
keeps every cell inside its safe operating area and makes the pack usable. Its functions:

| Function | Why |
|---|---|
| **Per-cell voltage monitoring** | over-voltage → fire; under-voltage → permanent damage |
| **Over/under-current protection** | short circuit, over-discharge |
| **Temperature monitoring** | detect runaway onset, throttle charge in cold |
| **Cell balancing** | equalize series cells so capacity isn't wasted |
| **SoC / SoH estimation** | tell the system how much is left (§6) |
| **Contactor / FET control** | disconnect on fault |
| **Communication** | report to the vehicle (CAN, the ICD of [12](12-systems-engineering-mbse.md)) |

**Cell balancing** matters because series cells drift apart in charge over cycles; the pack can
only charge until the *highest* cell hits its limit and discharge until the *lowest* hits its
floor — so imbalance strands capacity and, worse, risks over-charging one cell.
- **Passive balancing:** bleed charge from high cells through a resistor — simple, lossy, common.
- **Active balancing:** shuttle charge from high to low cells — efficient, complex, costly.

The BMS is a safety-critical embedded system: its failure modes (a stuck FET, a missed
over-voltage) are catastrophic, so it is designed with the FMEA/redundancy rigor of
[13-engineering-reliability-and-failure-analysis.md](13-reliability-and-failure-analysis.md)
and the assurance argument of [09-foundations-safety-assurance.md](../foundations/09-safety-assurance.md).

---

## 6. State estimation — SoC and SoH

**State of Charge (SoC)** is the fuel gauge — the fraction of usable capacity remaining. There
is no direct sensor for it; it must be *estimated*. Two base methods, each flawed alone:

- **Coulomb counting** integrates current: accurate short-term but drifts as the integral
  accumulates sensor bias (the same integration-of-bias problem as the IMU in
  [10-engineering-sensors-and-instrumentation.md](10-sensors-and-instrumentation.md)).
$$ \text{SoC}(t) = \text{SoC}(0) - \frac{1}{Q}\int_0^t \eta\,I(\tau)\,d\tau $$
- **Voltage-based (OCV lookup):** maps rested terminal voltage to SoC via the OCV curve —
  absolute but useless under load and ambiguous on flat curves (LFP).

The production answer **fuses both** with a model-based filter — an **Extended Kalman Filter**
on the equivalent-circuit model (§3), using coulomb counting for the fast dynamics and the OCV
relationship for the slow correction. This is *literally* the sensor-fusion architecture of
[13-autonomy-sensor-fusion.md](../autonomy/13-sensor-fusion.md) applied to a battery: a
fast-but-drifting integrator corrected by a slow-but-absolute measurement.

**State of Health (SoH)** tracks aging — capacity fade and internal-resistance rise over the
pack's life:
$$ \text{SoH} = \frac{Q_\text{current}}{Q_\text{rated}} \times 100\% $$
End-of-life is conventionally 80% SoH. SoH estimation (capacity fade tracking, impedance
spectroscopy) feeds maintenance and the wear-out reliability model of
[13-engineering-reliability-and-failure-analysis.md](13-reliability-and-failure-analysis.md).

---

## 7. Thermal runaway & safety

The defining hazard of lithium chemistry: **thermal runaway**, a self-sustaining exothermic
cascade. Above a critical temperature the cell's own reactions generate heat faster than it can
escape, and — because the cathode releases oxygen — the fire feeds itself and cannot be
smothered.

```
trigger (over-charge, short,    →  SEI breakdown (~90°C)
 crush, over-temp, internal         ↓
 defect)                         electrolyte decomposition (~120°C)
                                    ↓
                                 separator melt → internal short
                                    ↓
                                 cathode O₂ release (~150°C+)
                                    ↓
                                 RUNAWAY: venting, fire, propagation
```

The engineering response is **prevention, detection, and containment**:
- **Prevention:** BMS limits (voltage, current, temperature window), quality cells (screen
  infant mortality, [13](13-reliability-and-failure-analysis.md)), mechanical
  protection against crush/puncture.
- **Detection:** per-cell temperature and voltage, off-gas/pressure sensing for early warning.
- **Containment:** the critical insight is **propagation prevention** — one cell failing is
  survivable; the cascade to neighbors is not. Inter-cell spacing, thermal barriers
  (mica, intumescent, aerogel), directed venting, and cell fusing stop one bad cell from taking
  the pack. UL 2580 / UN 38.3 test for exactly this.

This is a textbook safety-assurance problem ([09-foundations-safety-assurance.md](../foundations/09-safety-assurance.md)):
you cannot reduce the probability of a single cell defect to zero, so the architecture must make
the *consequence* survivable — design the pack assuming a cell *will* go into runaway, and ensure
it stays contained.

---

## 8. Charging & lifecycle

Lithium cells charge by **CC-CV** (constant current, then constant voltage):

```
I, V
  | V ──────────────────────────  (CV phase: V held, I tapers)
  |        ___________/
  | I ____/           \
  |  (CC phase:        \______ taper to cutoff
  |   constant current) 
  +-------------------------------> time
```

- **CC phase:** push constant current until the cell reaches its voltage ceiling (~4.2 V
  Li-ion, 3.65 V LFP) — fast, fills most of the capacity.
- **CV phase:** hold that voltage while current tapers to a cutoff — tops off safely without
  over-voltage.

Charging rules that determine pack life:
- **Never charge below ~0 °C** — lithium plates on the anode, permanently degrading and
  dangerously shorting the cell. Cold packs must be warmed first.
- **Lower charge voltage and avoid 100%/0%** extends cycle life dramatically — staying in the
  20–80% window can multiply cycle count.
- **Heat is the enemy** — every cycle at high temperature accelerates capacity fade (Arrhenius
  again, [13](13-reliability-and-failure-analysis.md)).

**Cycle life** is the number of charge/discharge cycles before SoH hits end-of-life, and it
depends strongly on depth-of-discharge, temperature, and C-rate — the same parameters the BMS
controls. Designing the *usage envelope*, not just the pack, is how you hit a fleet's lifecycle
cost target — the vertical-integration-of-energy lesson behind Tesla's pack/charging strategy
([05-companies-tesla-vertical-integration-data.md](../companies/05-tesla-vertical-integration-data.md)).

---

## 9. Practice this week

1. Size a pack for a real mission: take an energy and power profile, pick a chemistry, and
   compute the sPm configuration, pack mass, and endurance — including Peukert and a usable-capacity
   derate.
2. Identify an equivalent-circuit model from a cell's pulse-discharge data: extract $R_0$ and one
   RC pair, and predict voltage sag at 5C.
3. Implement a simple SoC estimator that fuses coulomb counting with OCV correction (an EKF on the
   ECM); inject current-sensor bias and watch the OCV term correct the drift.
4. Design the safety architecture for a 6S pack: list BMS limits, balancing method, and three
   propagation-prevention measures, and map each to the runaway cascade it interrupts.

---

## 10. Sources & further study

- **Plett — *Battery Management Systems* (Vols. 1 & 2).** The definitive BMS and SoC/SoH estimation reference (ECM, EKF).
- **Reddy — *Linden's Handbook of Batteries*.** The encyclopedic chemistry reference.
- **Huggins — *Advanced Batteries: Materials Science Aspects*.** First-principles electrochemistry.
- **UN 38.3 / UL 2580 / IEC 62133** — transport and safety test standards for lithium packs.
- **NASA-HDBK / JSC battery safety guidelines** — aerospace pack safety and containment.
- **Battery University (batteryuniversity.com)** — accessible, accurate practical primers.
- **NTSB lithium-battery incident reports** — real thermal-runaway case studies, pairing with [09-foundations-safety-assurance.md](../foundations/09-safety-assurance.md).

> Framing note: A battery is not a tank of energy you draw down at will — it is an
> electrochemical system with a voltage that sags, a capacity that depends on rate and
> temperature, a charge state you can only estimate, and a failure mode that makes its own fire.
> The engineers who ship long-endurance, safe vehicles are the ones who size from the energy
> budget, model the cell honestly, estimate state with fusion, and design the pack assuming a
> cell *will* fail — and keep it contained when it does.
