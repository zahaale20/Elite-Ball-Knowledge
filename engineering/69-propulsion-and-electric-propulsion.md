# Propulsion — From Rocket Thermodynamics to Electric Motors & Props

> **Why this exists.** Propulsion is the answer to the most basic question any flying or space-bound system asks: how do I produce force against nothing, or against air, to go where I want? A rocket throws mass out the back at enormous velocity to reach orbit; a turbojet swallows air, burns fuel, and accelerates the flow; an electric drone spins a propeller to push air down and itself up. These look unrelated but obey one law — Newton's third — and a small set of thermodynamic and aerodynamic equations that decide whether a vehicle can lift off, how far it can go, and how long it can stay up. The engineer who understands propulsion holds the lever that sets range, endurance, payload, and the entire feasibility of a mission.

> **What mastering it makes you.** The person who can size a propulsion system from first principles — pick the motor, prop, and battery for a 45-minute VTOL mission, or run the rocket equation to know whether a stage reaches orbit — and explain exactly why the numbers are what they are.

Propulsion is applied thermodynamics, fluid mechanics, and energy accounting — the math of [03-foundations-mathematics.md](../foundations/03-mathematics.md) made physical. The electric side is driven by the converters and motor control of [68-engineering-power-electronics.md](68-power-electronics.md); the aerodynamics of props and intakes connect to [70-engineering-aerodynamics-and-flight-mechanics.md](70-aerodynamics-and-flight-mechanics.md); the heat it generates is the domain of [72-engineering-thermal-management.md](72-thermal-management.md); and the structures that contain combustion and transmit thrust are [71-engineering-structures-and-materials.md](71-structures-and-materials.md). The whole subsystem is a systems-engineering balance of energy, mass, and efficiency in the spirit of [01_first_principles_systems_engineering.md](../foundations/01-first_principles_systems_engineering.md).

---

## 1. The one law: conservation of momentum

All propulsion is reaction. You produce thrust by accelerating mass in the opposite direction. The thrust of any propulsive device:

$$ F = \dot{m}\,\Delta V = \dot{m}\,(V_e - V_0) + (p_e - p_0)A_e $$

where $\dot{m}$ is mass flow rate, $V_e$ exhaust velocity, $V_0$ vehicle (or intake) velocity, and the second term is the pressure thrust at the nozzle exit. This single equation underlies rockets, jets, and propellers — they differ only in *what* mass they accelerate and *how much* they accelerate it.

The strategic split is right here:

- **Rockets** carry their own propellant and throw it out very fast ($V_e \sim$ thousands of m/s) — works in vacuum, but mass-hungry.
- **Air-breathers** (jets, props) grab atmospheric mass for free and accelerate it modestly — vastly more efficient, but useless above the atmosphere.

This is the deepest tradeoff in flight: a little mass thrown fast vs. a lot of mass thrown slow.

---

## 2. The rocket equation — the tyranny of the exponential

For a rocket, integrating the thrust law over a burn (no external forces) gives Tsiolkovsky's rocket equation — the most important equation in spaceflight:

$$ \Delta V = V_e \ln\!\left(\frac{m_0}{m_f}\right) = I_{sp}\, g_0 \ln\!\left(\frac{m_0}{m_f}\right) $$

$\Delta V$ is the velocity change the vehicle can achieve, $m_0/m_f$ is the wet-to-dry mass ratio, and $I_{sp}$ (specific impulse) is the exhaust velocity expressed in seconds. The logarithm is the tyranny: to double $\Delta V$ you must *square* the mass ratio. Reaching low Earth orbit needs ~9.4 km/s of $\Delta V$, which forces mass ratios around 20:1 — the reason rockets are almost entirely propellant.

**Specific impulse** is the efficiency figure of merit — thrust per unit propellant weight flow:

$$ I_{sp} = \frac{F}{\dot{m}\,g_0} = \frac{V_e}{g_0} $$

| Propulsion | Typical $I_{sp}$ (s) | Exhaust velocity |
|---|---|---|
| Solid rocket | 250 | ~2.5 km/s |
| Kerolox (RP-1/LOX) | 300–340 | ~3.3 km/s |
| Hydrolox (LH2/LOX) | 450 | ~4.4 km/s |
| Ion / Hall thruster | 1500–4000 | 15–40 km/s |
| Turbojet (effective) | 3000–6000 | (air-breathing) |

Ion engines have huge $I_{sp}$ but tiny thrust — they sip propellant for years to build $\Delta V$ slowly, perfect for deep space, useless for liftoff. The $I_{sp}$-vs-thrust tradeoff is the propulsion engineer's central choice.

---

## 3. Rocket thermodynamics — turning heat into velocity

A chemical rocket is a controlled, continuous explosion: combust propellant in a chamber at high pressure and temperature, then expand the gas through a converging-diverging (de Laval) nozzle that converts thermal energy into directed kinetic energy. The exhaust velocity from isentropic expansion:

$$ V_e = \sqrt{\frac{2\gamma}{\gamma-1}\,\frac{R T_c}{M}\left[1 - \left(\frac{p_e}{p_c}\right)^{\frac{\gamma-1}{\gamma}}\right]} $$

Read the levers directly from the equation: high chamber temperature $T_c$, low exhaust molar mass $M$ (why hydrogen wins — light molecules go fast), and a large pressure ratio $p_c/p_e$ (why high chamber pressure and good expansion matter). This is why hydrolox has the best $I_{sp}$: combustion products are light water molecules.

```
   propellant   ┌─── combustion ───┐   expansion
   injectors ──►│  high p, high T  │──► throat ──► diverging ──► fast exhaust
                └──────────────────┘   (M=1)       (M>1, supersonic)
```

The nozzle is a thermodynamic machine: subsonic flow accelerates in the converging section, chokes to Mach 1 at the throat, and goes supersonic in the diverging section. The expansion ratio $A_e/A_t$ is tuned to the ambient pressure — a sea-level nozzle and a vacuum nozzle have very different bells, and a nozzle expanded wrong (over/under-expanded) loses thrust and can flow-separate.

---

## 4. Air-breathing engines — free oxidizer, huge efficiency

Within the atmosphere, carrying your own oxidizer is wasteful — the air is full of it. Air-breathing engines (turbojet, turbofan, turboprop, ramjet) ingest air, add energy, and exhaust it faster. The Brayton cycle governs the turbomachinery:

```
intake ─► compressor ─► combustor ─► turbine ─► nozzle
         (raise p)      (add heat)   (extract   (accelerate
                                      work)      flow)
```

Thermal efficiency rises with pressure ratio:

$$ \eta_{th} = 1 - \frac{1}{r_p^{\,(\gamma-1)/\gamma}}, \qquad r_p = \frac{p_2}{p_1} $$

The propulsive efficiency — how well the engine converts that energy into useful thrust rather than wasted exhaust kinetic energy — favors moving *more* air *slower*:

$$ \eta_p = \frac{2V_0}{V_0 + V_e} $$

This single equation explains the entire evolution from turbojet → high-bypass turbofan: a big fan moving a huge mass of air at modest velocity is far more efficient than a small jet at high velocity. It's also why **propellers** — the extreme case of moving enormous air mass slowly — are the most efficient of all at low speed.

---

## 5. Propellers — the drone and small-aircraft workhorse

A propeller is a rotating wing that produces thrust by pushing air backward. Two complementary models:

**Momentum (actuator disk) theory** treats the prop as a disk that accelerates a stream tube. The ideal (Froude) efficiency:

$$ \eta_{\text{ideal}} = \frac{2}{1 + \sqrt{1 + \frac{T}{\frac{1}{2}\rho A V_0^2}}} $$

This reveals the static-thrust truth: to hover (large $T$, $V_0 \to 0$), efficiency is governed by **disk loading** $T/A$. Low disk loading (big slow props) is efficient; high disk loading (small fast props, ducted fans) is compact but power-hungry. A helicopter's huge rotor and a quadcopter's relatively large props both exploit this.

**Blade element theory** integrates lift and drag along the radius, accounting for the twist that keeps each section at a good angle of attack despite the radially increasing speed. The dimensionless coefficients used to size everything:

$$ T = C_T\,\rho\,n^2 D^4, \qquad P = C_P\,\rho\,n^3 D^5, \qquad \eta = \frac{T V_0}{P} = \frac{C_T}{C_P}J $$

where $n$ is rotations/sec, $D$ diameter, and $J = V_0/(nD)$ the advance ratio. These power-law scalings ($D^4$ thrust, $D^5$ power) are why prop and motor sizing is so sensitive to diameter — a small change in $D$ swings the numbers hard.

---

## 6. Electric propulsion for aircraft — the system sizing

A modern electric drone propulsion chain is: **battery → ESC → BLDC motor → propeller → air.** Each stage has an efficiency, and the product sets endurance. From [68-engineering-power-electronics.md](68-power-electronics.md) you have the motor torque/speed relations; here you close the loop to mission performance.

Hover power for a multirotor follows directly from momentum theory:

$$ P_{\text{hover}} = \frac{T^{3/2}}{\sqrt{2\rho A}} \cdot \frac{1}{\eta_{\text{prop}}\,\eta_{\text{motor}}\,\eta_{\text{esc}}} $$

The $T^{3/2}$ scaling is brutal: a vehicle that weighs 50% more needs ~84% more hover power. And $A$ (total disk area) helps as a square root, so bigger props are the most direct endurance lever. Endurance is then:

$$ t_{\text{hover}} = \frac{E_{\text{battery}}\cdot \text{DoD}}{P_{\text{hover}}} = \frac{V\,Q\,\text{DoD}}{P_{\text{hover}}} $$

with battery energy $E = V\cdot Q$ (Wh) and depth-of-discharge limited to ~80% to protect the cells. The figure of merit is **specific energy** (Wh/kg): lithium-ion ~250, lithium-polymer similar, which caps electric endurance and is why hydrogen and hybrid systems are explored for long missions.

**Worked sizing intuition.** A 2 kg quad with 10-inch props (A ≈ 0.2 m², ρ = 1.2): ideal hover power ≈ $(19.6)^{1.5}/\sqrt{2\cdot1.2\cdot0.2}$ ≈ 126 W ideal, ~250 W real after efficiencies. A 4S 5000 mAh pack (74 Wh, 80% usable) gives ~14 minutes — and you can now see exactly which lever (lighter airframe, bigger props, denser battery) buys more time.

---

## 7. VTOL and hybrid propulsion — the transition problem

Vertical-takeoff-and-landing vehicles must hover *and* cruise efficiently — two regimes with opposite propulsion needs (high disk loading for compactness vs. low for efficiency). This is the central propulsion challenge of [21-autonomy-vtol-roadmap.md](../autonomy/21-vtol-roadmap.md). Architectures:

| Architecture | Hover | Cruise | Tradeoff |
|---|---|---|---|
| Multirotor | Rotors | Rotors (tilt body) | Simple, poor cruise efficiency |
| Tiltrotor | Rotors up | Rotors forward | Efficient, complex mechanism |
| Tiltwing | Wing+rotors up | Wing-borne | Efficient, heavy actuation |
| Lift+cruise | Vertical rotors | Separate pusher + wing | Robust, dead weight in cruise |
| Tailsitter | Whole vehicle pitches | Wing-borne | No tilt mechanism, hard control |

The transition — converting from rotor-borne to wing-borne flight — is where propulsion, aerodynamics, and control are most coupled and most failure-prone. Power demand peaks during hover and transition; cruise on a wing can be an order of magnitude more efficient (a wing's lift-to-drag does the work the rotors otherwise pay for). The propulsion engineer sizes for the worst case (hover/transition) while optimizing for the common case (cruise).

---

## 8. Combustion engines and turbines for endurance

For multi-hour missions, chemical fuel's specific energy (~12,000 Wh/kg for gasoline vs ~250 for batteries — nearly 50×) is decisive. Small UAVs use two-stroke and Wankel engines; larger ones use turboprops and turbofans. Even with poor engine efficiency (~25–30%), the raw energy density wins for endurance.

**Hybrid-electric** systems combine a combustion generator (running at its efficiency sweet spot) with batteries (for peak power and quiet/redundant operation). The generator charges the pack and the electric motors drive the props — decoupling the energy source from the thrust producer, a powerful architectural move. Series, parallel, and turbo-electric topologies each trade weight, efficiency, and complexity.

$$ \text{Energy source choice} \approx \arg\max \frac{(\text{specific energy})\cdot(\text{efficiency})}{(\text{system mass penalty})} $$

---

## 9. Nozzles, intakes, and matching

Propulsion components must *match* the vehicle's flight envelope. A nozzle expanded for vacuum wastes thrust at sea level; an intake designed for subsonic chokes at supersonic. Key matching ideas:

- **Nozzle expansion ratio** tuned to ambient pressure; the ideal nozzle has exit pressure equal to ambient. Altitude-compensating nozzles (aerospike) try to be ideal everywhere.
- **Supersonic intakes** must slow incoming air to subsonic before the compressor via shock systems; the geometry that works at Mach 2 fails at Mach 0.8.
- **Prop pitch** matched to cruise speed; a fixed-pitch prop optimized for cruise has poor static thrust and vice versa. Variable-pitch props resolve this at a mechanical cost.

The unifying principle: a propulsion system is optimal only at its design point, and the engineer's job is choosing that point and managing performance away from it.

---

## 10. Thrust-to-weight and the feasibility check

Before any detailed design, two ratios tell you if a concept can fly:

$$ \frac{T}{W} > 1 \text{ (to hover/accelerate up)}, \qquad \frac{T}{W} \approx \frac{1}{(L/D)} \text{ (to cruise level)} $$

A multirotor needs $T/W \gtrsim 2$ for adequate control authority and maneuver margin. A fixed-wing in cruise needs only enough thrust to overcome drag, so $T/W$ can be small if lift-to-drag $L/D$ is high — directly linking propulsion to the aerodynamics of [70-engineering-aerodynamics-and-flight-mechanics.md](70-aerodynamics-and-flight-mechanics.md). The Breguet range equation closes the loop for cruising aircraft:

$$ R = \frac{V}{c}\,\frac{L}{D}\,\ln\!\left(\frac{W_0}{W_1}\right) \quad\text{(fuel)}, \qquad R = \frac{E}{g}\,\frac{1}{m}\,\frac{L}{D}\,\eta \quad\text{(electric, fixed mass)} $$

Range depends on propulsion efficiency, aerodynamic efficiency ($L/D$), and energy fraction — three subsystems multiplying together. No single one saves a bad design.

---

## 11. Scaling laws and the cube-square trap

Propulsion does not scale linearly. As a vehicle grows by linear factor $k$: area (lift, thrust, drag) scales as $k^2$, but mass scales as $k^3$. Larger vehicles get *heavier faster than they get more lift*, so they need disproportionately more power — the cube-square law that limits how big a flapping or rotor vehicle can be. Conversely, very small vehicles operate at low Reynolds number where props and airfoils are inefficient (sticky, viscous air), so microdrones pay an efficiency penalty.

$$ \frac{P_{\text{required}}}{m} \propto \sqrt{\frac{W/S}{\rho}} \quad\Rightarrow\quad \text{wing/disk loading drives power-to-weight} $$

This is why insects, birds, drones, and airliners occupy distinct, physics-bounded niches — and why you can't just scale a design up or down without re-running the whole propulsion analysis.

---

## 12. Tooling and ecosystem

| Need | Tools |
|---|---|
| Rocket performance | NASA CEA, RPA, OpenRocket |
| Prop/motor sizing | eCalc, MotoCalc, QPROP, XROTOR |
| Aero/CFD | XFOIL, OpenVSP, ANSYS Fluent, OpenFOAM |
| Cycle analysis | NPSS, GasTurb, pyCycle |
| System modeling | MATLAB/Simulink, Python |
| Test | thrust stand, dynamometer, flow bench |

For learning, OpenRocket (model rockets), eCalc (electric drone sizing), and QPROP/XROTOR (propeller analysis) let you turn the equations above into real designs on a laptop.

---

## Sources & further study

- Sutton & Biblarz, *Rocket Propulsion Elements* — the definitive rocket text.
- Hill & Peterson, *Mechanics and Thermodynamics of Propulsion* — air-breathing and rocket fundamentals together.
- Jack Mattingly, *Elements of Propulsion: Gas Turbines and Rockets* — thorough cycle analysis.
- Barnes McCormick, *Aerodynamics, Aeronautics, and Flight Mechanics* — propeller theory and integration.
- Wayne Johnson, *Helicopter Theory* — rotor and hover aerodynamics in depth.
- John Anderson, *Introduction to Flight* — accessible propulsion + aero overview.
- Saeed Farokhi, *Aircraft Propulsion* — modern, well-illustrated.
- Goebel, *Fundamentals of Electric Propulsion* (JPL) — ion and Hall thrusters.

> Framing note: Propulsion is where energy becomes motion, and every equation in it is really a statement about what you're allowed to do — the rocket equation says how much you can throw, the propulsive-efficiency equation says how to throw it cheaply, and the scaling laws say how big you can get before physics says no. Master propulsion and you can look at any flying or spacefaring concept and know, from a handful of numbers, whether it leaves the ground and how far it gets.
