# Thermodynamics & Fluid Mechanics — Energy, Flow & Why Engines Work

> **Why this exists.** Autonomy runs on energy and moves through fluid. A drone's endurance is a thermodynamic budget; its lift, drag, and propeller efficiency are fluid-mechanical; its electronics throttle when they cannot reject heat. Every propulsion choice — battery, turbine, fuel cell — is bounded by the second law, and every aerodynamic surface lives or dies by the boundary layer. If you cannot reason about energy conversion and flow, you cannot size a power system, predict range, or understand why a stalled wing stops lifting. Thermo and fluids are where abstract autonomy meets the hard limits of physics.

> **What mastering it makes you.** The engineer who can estimate a vehicle's endurance from first principles, explain why a turbojet has a Carnot ceiling, predict where a boundary layer separates, and reason about shock waves on a transonic propeller tip. You become the person who sizes the powertrain and the airframe *together*, because you understand they are one coupled energy-and-flow problem.

This module supplies the energy and flow physics behind the vehicles modeled in [08-foundations-physics-for-engineers.md](08-physics-for-engineers.md) and controlled in [07-foundations-control-advanced.md](07-control-advanced.md). Endurance and propulsion tradeoffs feed mission planning in [10-autonomy-planning-decision.md](../autonomy/10-planning-decision.md) and the systems budgets of [01_first_principles_systems_engineering.md](../foundations/01-first_principles_systems_engineering.md). The calculus and differential-equation tools come from [03-foundations-mathematics.md](../foundations/03-mathematics.md); the field analogies (flux, divergence) recur in [10-foundations-electromagnetics.md](10-electromagnetics.md).

---

## 1. The four laws — what energy can and cannot do

Thermodynamics is the accounting and the censorship of energy.

- **Zeroth law:** thermal equilibrium is transitive — temperature is well-defined.
- **First law (conservation):** $dU = \delta Q - \delta W$. Internal energy changes by heat added minus work done. There is no free energy.
- **Second law (direction):** entropy of an isolated system never decreases, $dS \ge \delta Q / T$. This forbids perpetual motion of the second kind and sets the *efficiency ceiling* of every engine.
- **Third law:** entropy $\to$ constant as $T \to 0$; absolute zero is unreachable.

The first law tells you energy is conserved; the **second law tells you it degrades**. Both bills must be paid.

### 1.1 Entropy and irreversibility

For a reversible process $dS = \delta Q_{\text{rev}}/T$. Real processes generate entropy: friction, mixing, finite-temperature heat transfer. Every irreversibility is lost work — directly, lost endurance. This is why a 90%-efficient motor still matters: the missing 10% becomes heat you must reject (Section 6).

---

## 2. The Carnot limit — the ceiling no engine beats

Consider any engine operating between a hot reservoir $T_H$ and cold reservoir $T_C$. The second law forces

$$
\boxed{\;\eta = \frac{W}{Q_H} \le \eta_{\text{Carnot}} = 1 - \frac{T_C}{T_H}.\;}
$$

### 2.1 Derivation sketch

A Carnot cycle is two isotherms and two adiabats. On the isotherms, $Q_H = T_H \Delta S$ and $Q_C = T_C \Delta S$ with equal $\Delta S$ (the adiabats are isentropic). Net work $W = Q_H - Q_C$, so

$$
\eta = 1 - \frac{Q_C}{Q_H} = 1 - \frac{T_C}{T_H}.
$$

No engine, however clever, exceeds this — because doing so would let you build a perpetual-motion machine violating the second law. A gas turbine with $T_H \approx 1500\,$K and $T_C \approx 300\,$K is capped at $\eta \le 0.80$; real turbines reach ~40% because of irreversibilities. The lesson for autonomy: **raising turbine inlet temperature** (materials problem) is the only way to fundamentally raise propulsion efficiency.

---

## 3. Engine cycles — turning the laws into thrust

| Cycle | Process | Application | Ideal efficiency |
|---|---|---|---|
| Carnot | 2 isotherm + 2 adiabat | theoretical bound | $1 - T_C/T_H$ |
| Otto | const-volume heat add | piston/gasoline | $1 - r^{1-\gamma}$ |
| Diesel | const-pressure heat add | compression-ignition | (cutoff-dependent) |
| Brayton | const-pressure | **gas turbine / jet** | $1 - (p_1/p_2)^{(\gamma-1)/\gamma}$ |
| Rankine | phase change | steam, ORC waste-heat | — |

### 3.1 The Brayton cycle (jet propulsion)

Compress ($1\to2$), burn at constant pressure ($2\to3$), expand through turbine and nozzle ($3\to4$). Ideal thermal efficiency depends only on the **pressure ratio** $r_p = p_2/p_1$:

$$
\eta_{\text{Brayton}} = 1 - r_p^{-(\gamma-1)/\gamma},
$$

with $\gamma = c_p/c_v \approx 1.4$ for air. Higher pressure ratio → higher efficiency, which is why modern engines stack many compressor stages. This is the thermodynamic heart of every turbine-powered UAV.

---

## 4. Fluid statics and the governing equations

A fluid is a continuum described by velocity field $\mathbf u(\mathbf x, t)$, pressure $p$, density $\rho$. Two conservation laws govern it.

### 4.1 Continuity (mass conservation)

$$
\frac{\partial \rho}{\partial t} + \nabla\cdot(\rho \mathbf u) = 0.
$$

For incompressible flow ($\rho$ const) this collapses to the elegant $\nabla\cdot\mathbf u = 0$ — velocity is divergence-free, a constraint analogous to the magnetic field's $\nabla\cdot\mathbf B = 0$ in [10-foundations-electromagnetics.md](10-electromagnetics.md).

### 4.2 Navier–Stokes (momentum conservation)

$$
\boxed{\;\rho\left( \frac{\partial \mathbf u}{\partial t} + (\mathbf u\cdot\nabla)\mathbf u \right) = -\nabla p + \mu \nabla^2 \mathbf u + \mathbf f.\;}
$$

Left side: inertia (with the nonlinear convective term $(\mathbf u\cdot\nabla)\mathbf u$ that makes turbulence hard and the Clay Millennium Prize open). Right side: pressure gradient, viscous diffusion, body forces. Almost all of aerodynamics is this equation under different simplifications.

---

## 5. Bernoulli, lift, and the Reynolds number

### 5.1 Bernoulli's equation

For steady, inviscid, incompressible flow along a streamline, integrating Euler's equation gives

$$
p + \tfrac12 \rho u^2 + \rho g h = \text{const}.
$$

Faster flow ⇒ lower pressure. This is the *first-order* explanation of lift: a wing accelerates flow over its upper surface, dropping pressure, producing a net upward force. (The rigorous account adds circulation and the Kutta condition: $L' = \rho U \Gamma$.)

### 5.2 The Reynolds number — the master parameter

Nondimensionalize Navier–Stokes and a single group governs the flow:

$$
Re = \frac{\rho U L}{\mu} = \frac{\text{inertial forces}}{\text{viscous forces}}.
$$

- $Re \ll 1$: creeping, viscous-dominated (microdrones, insects).
- $Re \sim 10^3$–$10^5$: transitional, laminar–turbulent boundary layers (small UAVs).
- $Re > 10^6$: fully turbulent, inertia-dominated (aircraft).

A small drone and a jet are *different physics regimes* because they sit at different $Re$ — a scaling insight from [08-foundations-physics-for-engineers.md](08-physics-for-engineers.md).

---

## 6. Boundary layers, drag, and stall

Viscosity is negligible everywhere *except* a thin **boundary layer** near surfaces, where velocity rises from zero (no-slip) to freestream. The boundary layer carries the drag and decides whether the wing stalls.

### 6.1 The two drags

Total drag splits into:

$$
D = \underbrace{\tfrac12 \rho U^2 S\, C_{D,0}}_{\text{parasitic (skin friction + form)}} + \underbrace{\frac{L^2}{\tfrac12 \rho U^2 \pi e\, b^2}}_{\text{induced (lift-dependent)}}.
$$

Parasitic drag rises with speed; induced drag falls with speed. Their sum has a minimum — the speed of **maximum endurance/range**. This single curve sets a UAV's loiter time.

### 6.2 Separation and stall

When the boundary layer meets an **adverse pressure gradient** (pressure rising in flow direction, as on the rear of an airfoil at high angle of attack), it loses momentum, reverses, and *separates*. Lift collapses and drag spikes — **stall**. Predicting separation is the core of airfoil design and the reason flight controllers limit angle of attack. The control consequence: near stall the plant becomes violently nonlinear, breaking the linearizations of [07-foundations-control-advanced.md](07-control-advanced.md).

### 6.3 Endurance estimate — worked example

For an electric multirotor, hover power is set by momentum theory:

$$
P = \frac{(mg)^{3/2}}{\sqrt{2\rho A}},
$$

with $A$ the total rotor disk area. Endurance $t = \eta E_{\text{batt}} / P$. Doubling disk area cuts power by $\sqrt2$ — why large, slow rotors are efficient. This is the first-principles range budget feeding mission planning.

```python
import numpy as np

def hover_endurance(m, A_disk, E_batt_Wh, eta=0.7, rho=1.225, g=9.81):
    """Estimate multirotor hover endurance from momentum theory."""
    P_ideal = (m * g) ** 1.5 / np.sqrt(2 * rho * A_disk)   # watts
    P_real = P_ideal / eta
    return (E_batt_Wh * 3600) / P_real / 60                # minutes

print(f"{hover_endurance(2.0, 0.20, 100):.1f} min")        # ~ endurance
```

---

## 7. Compressible flow and shock waves

When flow speed approaches the speed of sound $a = \sqrt{\gamma R T}$, density changes matter. The **Mach number** $M = U/a$ governs the regime.

| Regime | Mach | Phenomenon |
|---|---|---|
| Subsonic | $M < 0.8$ | incompressible-like |
| Transonic | $0.8$–$1.2$ | local shocks, drag rise |
| Supersonic | $1.2$–$5$ | oblique/normal shocks |
| Hypersonic | $> 5$ | chemistry, heating |

Across a **normal shock**, flow goes supersonic→subsonic discontinuously, with entropy jump (irreversibility) and total-pressure loss. The Prandtl–Glauert singularity and **wave drag** explain the transonic "sound barrier": drag coefficient spikes near $M=1$. Propeller and rotor *tips* can go transonic well before the vehicle does — capping tip speed and thus thrust. The isentropic and Rankine–Hugoniot relations quantify this:

$$
\frac{T_0}{T} = 1 + \frac{\gamma-1}{2}M^2,
$$

the stagnation-to-static temperature ratio that also predicts aerodynamic heating — the design driver for high-speed vehicles.

---

## 8. Heat transfer — the constraint that throttles everything

Three modes move heat:

- **Conduction:** $q = -k\nabla T$ (Fourier's law) — through solids, heat sinks.
- **Convection:** $q = h(T_s - T_\infty)$ (Newton's cooling) — to moving fluid.
- **Radiation:** $q = \varepsilon\sigma(T_s^4 - T_\infty^4)$ (Stefan–Boltzmann) — dominant at high $T$ and in vacuum.

For autonomy, thermal management is often the *real* limit: a flight computer or motor controller that cannot reject its $I^2R$ losses will throttle or fail. The vehicle's power budget (Section 6) and its thermal-rejection capacity are two sides of the same energy ledger — the kind of coupled constraint [01_first_principles_systems_engineering.md](../foundations/01-first_principles_systems_engineering.md) insists you track jointly.

---

## 9. The unified energy-and-flow budget

| Domain | Limiting physics | Autonomy consequence |
|---|---|---|
| Propulsion | Carnot / Brayton ceiling | max efficiency, thrust |
| Aerodynamics | drag polar, stall | range, endurance, agility |
| Compressibility | wave drag, tip Mach | speed/altitude envelope |
| Thermal | conduction/convection limits | compute & motor derating |
| Battery | energy density (Wh/kg) | flight time |

Every one of these is an *exponential* or *power-law* constraint, not a linear one — which is why naive scaling fails and first-principles physics is non-negotiable. Sizing an autonomous vehicle is solving all five budgets simultaneously.

---

## Sources & further study

- Çengel & Boles, *Thermodynamics: An Engineering Approach* — the standard, cycle-by-cycle.
- Fermi, *Thermodynamics* — short, rigorous, beautiful on entropy and the second law.
- Anderson, *Fundamentals of Aerodynamics* — the definitive aero text, subsonic to hypersonic.
- White, *Fluid Mechanics* — Navier–Stokes, boundary layers, pipe and external flow.
- Kundu, Cohen & Dowling, *Fluid Mechanics* — graduate-level continuum rigor.
- Incropera & DeWitt, *Fundamentals of Heat and Mass Transfer* — conduction/convection/radiation.
- Hill & Peterson, *Mechanics and Thermodynamics of Propulsion* — ties cycles to thrust.

> Framing note: Thermodynamics tells you the ceiling, fluid mechanics tells you the cost of moving, and heat transfer tells you what you can actually run before it melts. Autonomy engineers who treat the powertrain, the airframe, and the cooling as one coupled energy-and-flow problem build vehicles that fly longer and survive harder. Those who treat them separately discover the second law the expensive way — in flight test.
