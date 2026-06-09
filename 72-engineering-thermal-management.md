# Thermal Management — Keeping Electronics and Engines Alive

> **Why this exists.** Every watt of energy a system fails to convert into useful work becomes heat, and heat is the silent killer of electronics and engines alike. A flight computer that throttles or resets when its processor crosses 100°C, a motor drive whose MOSFETs cook off because the heatsink was undersized, a battery that thermal-runs away into fire, a satellite that freezes on its dark side and bakes on its sunlit one — all are thermal failures. Thermal management is the discipline of moving heat from where it's generated to where it can be rejected, fast enough and reliably enough that nothing exceeds its limits. The engineer who masters it keeps the rest of the system alive: every electrical, propulsion, and structural design eventually hands its waste heat to thermal, and a system that ignores thermal until the end discovers it has built something that overheats in the first hot day of testing.

> **What mastering it makes you.** The person who sizes the heatsink, picks the thermal interface, designs the airflow, and predicts junction temperatures before the board is built — the engineer who ensures the impressive electronics and propulsion actually run continuously instead of for ninety seconds before throttling.

Thermal management is applied heat transfer — the partial differential equations of [03-foundations-mathematics.md](03-foundations-mathematics.md) (the heat equation) made into hardware. It is where the losses computed in [68-engineering-power-electronics.md](68-engineering-power-electronics.md) and the combustion heat of [69-engineering-propulsion-and-electric-propulsion.md](69-engineering-propulsion-and-electric-propulsion.md) must go, and it sets the limits on the firmware processors of [65-engineering-embedded-firmware.md](65-engineering-embedded-firmware.md) and FPGAs of [66-engineering-fpga-and-hardware-accel.md](66-engineering-fpga-and-hardware-accel.md). The structures that conduct and radiate heat are those of [71-engineering-structures-and-materials.md](71-engineering-structures-and-materials.md), and thermal margins are a safety case in the sense of [09-foundations-safety-assurance.md](09-foundations-safety-assurance.md). The whole subject is a first-principles energy-balance problem ([01_first_principles_systems_engineering.md](01_first_principles_systems_engineering.md)): heat in must equal heat out, or temperature rises until something fails.

---

## 1. The three modes of heat transfer

Heat moves by exactly three mechanisms, and every thermal design is a combination of them. Know all three cold.

**Conduction** — heat diffusing through a solid (or stationary fluid) down a temperature gradient. Governed by Fourier's law:

$$ q = -k A \frac{dT}{dx} \qquad\Rightarrow\qquad Q = \frac{kA}{L}\,\Delta T = \frac{\Delta T}{R_{\text{cond}}}, \quad R_{\text{cond}} = \frac{L}{kA} $$

where $k$ is thermal conductivity (W/m·K), $A$ the cross-section, $L$ the path length. This is the path from a chip's junction through its package to a heatsink.

**Convection** — heat carried away by a moving fluid (air, liquid). Governed by Newton's law of cooling:

$$ Q = h A \,(T_s - T_\infty) = \frac{\Delta T}{R_{\text{conv}}}, \quad R_{\text{conv}} = \frac{1}{hA} $$

where $h$ is the convection coefficient (W/m²·K), which depends enormously on whether the flow is natural (buoyancy, $h \sim 5$–25) or forced (fan/pump, $h \sim 25$–250 for air, thousands for liquid). Convection is usually the bottleneck and the biggest lever.

**Radiation** — heat emitted as electromagnetic waves, needing no medium. Governed by the Stefan-Boltzmann law:

$$ Q = \varepsilon \sigma A \,(T_s^4 - T_{\text{surr}}^4) $$

where $\varepsilon$ is emissivity (0–1), $\sigma = 5.67\times10^{-8}$ W/m²·K⁴. The fourth-power dependence makes radiation negligible at low temperatures but dominant at high ones — and it is the *only* mode available in the vacuum of space, making it the central concern for spacecraft thermal design.

| Mode | Equation | Needs | Dominant when |
|---|---|---|---|
| Conduction | $Q = kA\Delta T/L$ | Solid path | Inside packages, heatsink base |
| Convection | $Q = hA\Delta T$ | Moving fluid | Heatsink-to-air, liquid loops |
| Radiation | $Q = \varepsilon\sigma A\,\Delta T^4$ | Line of sight | Hot surfaces, vacuum/space |

---

## 2. Thermal resistance — the circuit analogy

The most powerful tool in thermal engineering is treating heat flow like an electrical circuit: temperature difference is voltage, heat flow is current, and **thermal resistance** $R_\theta$ (°C/W) is resistance. Resistances in a series path add, exactly like resistors:

$$ \Delta T = Q \cdot R_{\theta,\text{total}}, \qquad R_{\theta,\text{total}} = R_{jc} + R_{cs} + R_{sa} $$

For a power transistor cooling to air through a heatsink, the chain is junction → case → sink → ambient:

```
  T_junction ──[R_jc]──[R_cs]──[R_sa]── T_ambient
   (the chip)   pkg    TIM    heatsink
                          
  T_j = T_ambient + Q·(R_jc + R_cs + R_sa)
```

This single equation is how you answer the question that drives every electronics thermal design: **given my power dissipation, will the junction stay below its rated maximum (often 125–150°C)?** Rearranged, it tells you the maximum allowable heatsink resistance:

$$ R_{sa,\max} = \frac{T_{j,\max} - T_{\text{ambient}}}{Q} - R_{jc} - R_{cs} $$

If a 50 W power stage at 50°C ambient needs $T_j < 125°C$, with $R_{jc}=0.5$ and $R_{cs}=0.2$: $R_{sa} < (125-50)/50 - 0.7 = 0.8$ °C/W — a concrete heatsink spec you can shop for. This is the bread-and-butter calculation of the whole field.

---

## 3. The heat equation — transient behavior

Steady-state resistance tells you the final temperature; the **heat equation** tells you how temperature evolves in time and space — essential for transient loads (a motor that runs hard for 30 seconds, a processor with bursty workloads):

$$ \frac{\partial T}{\partial t} = \alpha \nabla^2 T + \frac{\dot{q}}{\rho c_p}, \qquad \alpha = \frac{k}{\rho c_p} $$

where $\alpha$ is thermal diffusivity (how fast temperature changes propagate) and $\dot q$ is volumetric heat generation. The lumped-capacitance simplification (valid when the object is nearly isothermal) gives an intuitive first-order response:

$$ Q = m c_p \frac{dT}{dt} + \frac{T - T_\infty}{R_\theta} \;\Rightarrow\; \tau = R_\theta C_\theta = R_\theta\, m c_p $$

The **thermal time constant** $\tau$ tells you whether a transient matters: a part with large thermal mass ($mc_p$) heats slowly and can absorb short bursts (a brief overload doesn't reach steady state), while a tiny die heats almost instantly. This is why a copper slug or phase-change material buffers a pulsed load — it's a thermal capacitor smoothing the temperature the way an electrical capacitor smooths voltage. The **Biot number** $Bi = hL/k$ tells you whether lumped analysis is valid ($Bi < 0.1$) or whether internal gradients matter.

---

## 4. Heat sinks — the workhorse

A heatsink spreads heat from a small source over a large surface area to give convection somewhere to work. Its performance is set by surface area, fin efficiency, and airflow:

$$ Q = \eta_{\text{fin}}\, h\, A_{\text{fin}}\,(T_{\text{base}} - T_\infty) $$

Design tensions every heatsink balances:

- **More fins = more area**, but packed too densely they choke airflow and trap a stagnant boundary layer (diminishing returns).
- **Taller fins = more area**, but fin efficiency drops as the tip gets far from the hot base (the tip runs cooler, contributing less). Fin efficiency:

$$ \eta_{\text{fin}} = \frac{\tanh(mL)}{mL}, \qquad m = \sqrt{\frac{hP}{kA_c}} $$

- **Base spreading resistance** — heat from a small chip must spread through the base before reaching the fins; a thin or low-$k$ base bottlenecks here, which is why high-power sinks use thick copper bases or vapor chambers.
- **Material** — aluminum (cheap, light, $k\approx 200$) vs. copper (heavy, $k\approx 400$, better spreading). Weight matters for flight, so aluminum dominates with copper inserts where spreading is critical.

Natural vs. forced convection is the biggest single decision: adding even a small fan can raise $h$ by 5–10×, shrinking the required heatsink dramatically — but it adds power, weight, noise, and a failure point.

---

## 5. Thermal interface materials — the hidden bottleneck

Two "flat" surfaces pressed together actually touch at only a few percent of their area; the gaps are air, a terrible conductor. The interface between a chip and its heatsink can dominate the entire thermal path if neglected. **Thermal interface materials (TIMs)** fill those gaps:

| TIM | Conductivity (W/m·K) | Notes |
|---|---|---|
| Air gap (none) | 0.025 | Catastrophic; never acceptable |
| Thermal grease/paste | 3–10 | Cheap, effective, can pump out over time |
| Thermal pads | 1–6 | Easy, fills gaps, lower performance |
| Phase-change | 3–8 | Melts to fill, stable |
| Liquid metal | 30–80 | Best, but conductive and corrosive |
| Solder/sintered | 50–80 | Permanent, highest performance |

The interface resistance:

$$ R_{\text{TIM}} = \frac{t_{\text{BLT}}}{k_{\text{TIM}} A} + R_{\text{contact}} $$

The lesson is brutal and common: a beautifully designed heatsink performs terribly if mounted with a thick, voided, or wrong TIM. Bond-line thickness, mounting pressure, and surface flatness matter as much as the material. This is where many real thermal failures hide — the analysis assumed perfect contact the assembly never delivered.

---

## 6. Electronics cooling — the system view

A real board is a network of heat sources (CPU, FPGA, power stages, regulators) sharing a thermal environment. The strategy hierarchy, from cheapest to most aggressive:

1. **Reduce the heat** — efficiency first (a 95% converter dumps a third the heat of an 85% one). The cheapest watt to cool is the one never generated, tying thermal directly to [68-engineering-power-electronics.md](68-engineering-power-electronics.md).
2. **Spread it** — copper pours, thermal vias under hot chips conducting heat to inner planes or the far side, metal-core PCBs.
3. **Natural convection + radiation** — passive heatsinks, dark/high-emissivity surfaces, chassis as a heatsink.
4. **Forced air** — fans, ducted airflow, directed at the hottest components.
5. **Liquid cooling** — cold plates, pumped loops (for very high power density: high-end FPGAs, power inverters, lasers).
6. **Phase change / heat pipes** — wick-and-vapor devices that move heat with enormous effective conductivity.

**Heat pipes and vapor chambers** deserve emphasis: a sealed wick structure where fluid evaporates at the hot end, the vapor travels to the cold end, condenses, and wicks back — moving heat with an *effective* conductivity 10–100× copper, with no moving parts. They're how laptops, GPUs, and dense avionics move heat from a hot chip to a remote heatsink.

```
  hot chip ──► [evaporator] ═══vapor═══► [condenser] ──► heatsink
                    ▲                          │
                    └──── liquid (wick) ◄───────┘
                    heat pipe: passive, near-isothermal
```

For flight, the PCB and chassis often *are* the thermal solution — there's limited airflow and weight budget, so conduction to a structural heat path and radiation from the skin do the work. This couples thermal tightly to the structures of [71-engineering-structures-and-materials.md](71-engineering-structures-and-materials.md): the airframe is a heatsink.

---

## 7. Battery thermal management — safety, not just performance

Lithium batteries are thermally fragile in a way that's a safety issue, not just a performance one. They have a narrow happy band (~15–35°C): too cold and capacity and power collapse; too hot and they degrade rapidly; past a critical temperature they enter **thermal runaway** — an exothermic chain reaction where one cell's heat triggers its neighbors, producing fire that's nearly impossible to extinguish. This is a primary safety case for any electric vehicle.

The energy released in runaway and the heat-generation rate set the design:

$$ \dot{Q}_{\text{cell}} = I^2 R_{\text{internal}} + \dot{Q}_{\text{reaction}}, \qquad T_{\text{runaway onset}} \approx 80\text{–}120°C $$

Battery thermal management spans: keeping cells in band (heating in cold, cooling under high discharge), **even temperature distribution** across the pack (hot cells age faster, creating imbalance), and **runaway containment** — physical barriers, venting paths, and cell spacing so one failed cell doesn't cascade. This is where thermal management is explicitly a safety-assurance activity ([09-foundations-safety-assurance.md](09-foundations-safety-assurance.md)) — the thermal design *is* the fire-prevention design.

---

## 8. Engine and propulsion cooling

Combustion and high-power propulsion generate heat at the upper extreme of the temperature range, where radiation dominates and materials approach their limits. Strategies:

- **Regenerative cooling** (rockets) — route the cryogenic propellant through channels in the nozzle wall before combustion, cooling the wall and preheating the fuel. The wall survives gas temperatures far above its melting point because the coolant carries heat away faster than it arrives.
- **Film/transpiration cooling** — a thin layer of cool gas blankets the hot wall.
- **Ablative cooling** — a sacrificial liner that absorbs heat by vaporizing (re-entry heat shields, solid rocket nozzles).
- **Air cooling** (piston/turbine) — fins and forced airflow; turbine blades use internal cooling passages and film cooling to run in gas hotter than their melting point.

The governing balance is always the same energy equation: heat generated must be removed before the wall temperature exceeds the material limit, with radiation's $T^4$ term doing heavy lifting at these temperatures. Thermal expansion ($\Delta L = \alpha L \Delta T$) also becomes a structural driver — hot parts grow, and mismatched expansion between materials creates thermal stress that fatigues joints, linking back to [71-engineering-structures-and-materials.md](71-engineering-structures-and-materials.md).

---

## 9. Spacecraft thermal — the radiation-only regime

In vacuum, convection vanishes; a spacecraft can only reject heat by **radiation** and only gain it by radiation (sun, Earth IR) and internal dissipation. This makes thermal design a careful energy balance with no convective safety valve:

$$ Q_{\text{absorbed}} + Q_{\text{internal}} = Q_{\text{emitted}} = \varepsilon \sigma A\, T^4 \;\Rightarrow\; T_{\text{equilibrium}} = \left(\frac{\alpha_s G_s A_{\text{sun}} + Q_{\text{int}}}{\varepsilon \sigma A}\right)^{1/4} $$

The design tools are **surface optics** ($\alpha_s$ solar absorptivity, $\varepsilon$ emissivity), chosen via coatings and multi-layer insulation (MLI blankets), plus radiators sized to dump waste heat, heaters for cold cases, and heat pipes to move heat to radiators. The brutal part is the swing between sunlit and shadowed sides — a satellite can face +120°C and −150°C simultaneously, and the structure must survive the gradient and the cycling. This is thermal engineering at its purest: a closed energy balance where every watt is accounted for and radiation is the only exit.

---

## 10. Thermal analysis and simulation

The workflow mirrors structures: hand calculations for sizing and sanity, simulation for complex geometry, test for truth.

- **Hand calc / spreadsheet** — thermal-resistance networks for the first-order answer. Always start here; if you can't estimate the junction temperature on paper, you don't understand the problem.
- **Lumped-parameter thermal models** — networks of resistances and capacitances for system-level transient behavior, fast and intuitive.
- **CFD (Computational Fluid Dynamics)** — for convection and airflow where the flow field matters (heatsink in a duct, electronics enclosure). Tools: ANSYS Icepak/Fluent, Simcenter Flotherm, OpenFOAM.
- **FEA thermal** — conduction in solids, transient temperature fields, thermal stress (often coupled to structural FEA).
- **Test** — thermocouples, IR cameras, thermal-vacuum chambers (for space). No thermal design is trusted until measured, because $h$ values, contact resistances, and real airflow are notoriously hard to predict.

The same caution as FEA applies: simulations produce confident-looking temperature maps that are only as good as the boundary conditions, material properties, and convection coefficients fed in. Correlate to test, always.

---

## 11. Designing thermal in from the start

The recurring lesson across every domain above: **thermal cannot be an afterthought.** A system designed for function first and cooled later usually can't be cooled — there's no airflow path, no room for a heatsink, no thermal mass, no radiator area. The disciplined approach treats thermal as a first-class constraint from the start:

1. **Budget the heat** — sum all dissipations (power stages, processors, motors), identify the hot spots, know the total watts to reject.
2. **Set the limits** — max junction/cell/wall temperatures and the worst-case ambient (a drone on a 45°C tarmac, a satellite in full sun).
3. **Choose the strategy** early — passive vs. active, air vs. liquid, conduction path to structure — because it shapes the whole layout.
4. **Place hot components** with cooling in mind — near airflow, near the chassis heat path, spread apart, not buried.
5. **Analyze, then test** — predict junction temperatures, then verify under worst-case load and ambient before committing.

$$ \boxed{\text{Heat in} = \text{Heat out at steady state; otherwise } T \text{ rises until something fails.}} $$

This energy balance is the whole discipline in one line, and the engineer who carries it from the first sketch builds systems that run continuously instead of impressively for ninety seconds.

---

## 12. Tooling and ecosystem

| Need | Tools |
|---|---|
| Electronics cooling CFD | ANSYS Icepak, Simcenter Flotherm, 6SigmaET |
| General CFD | ANSYS Fluent, Star-CCM+, OpenFOAM |
| Thermal FEA | ANSYS Mechanical, Abaqus, NX Thermal |
| Spacecraft thermal | Thermal Desktop, ESATAN, NX Space Systems |
| System/lumped models | MATLAB/Simulink, Python, GT-SUITE |
| Hand calc | spreadsheets, thermal-resistance networks |
| Measurement | thermocouples, IR camera (FLIR), thermal-vac chamber |

For learning, build a thermal-resistance network in a spreadsheet for a real power stage, then validate it with a $5 thermocouple and a thermal camera — the gap between your prediction and reality teaches more than any textbook.

---

## Sources & further study

- Frank Incropera & David DeWitt, *Fundamentals of Heat and Mass Transfer* — the definitive heat-transfer text.
- Yunus Çengel, *Heat and Mass Transfer: Fundamentals and Applications* — accessible, example-rich.
- Allan Kraus, Avram Bar-Cohen & others, *Thermal Analysis and Control of Electronic Equipment* — the electronics-cooling reference.
- Gilmore (ed.), *Spacecraft Thermal Control Handbook* — the standard for space thermal.
- Adrian Bejan, *Heat Transfer* and *Convection Heat Transfer* — rigorous and insight-driven.
- John Lienhard, *A Heat Transfer Textbook* (free online) — comprehensive and free.
- Horowitz & Hill, *The Art of Electronics* — the device thermal limits in context.
- Vendor application notes (Wakefield, Aavid, t-Global) — practical heatsink and TIM selection.

> Framing note: Thermal management is the discipline of obeying the first law of thermodynamics in hardware — every watt in must find a way out, or temperature climbs until something quits or burns. It is the constraint that every other subsystem eventually hands its waste heat to, and the one most often ignored until a board throttles on the bench or a battery vents in flight. Master the three modes, the resistance network, and the energy balance, and you become the engineer who makes powerful systems actually run — continuously, reliably, and within the limits physics imposes.
