# Structures & Materials — Strength, Stiffness, Fatigue & Composites

> **Why this exists.** Every airframe, motor mount, landing leg, pressure vessel, and circuit-board bracket must carry loads without breaking, without flexing too much, and without cracking after thousands of cycles — while weighing as little as physically possible. In aerospace and robotics, structure is the silent constraint behind every other subsystem: a wing that flutters, a bracket that fatigues, or a composite layup that delaminates ends a mission as surely as a dead battery. The engineer who understands stress, stiffness, fatigue, and materials can size a part to survive its loads with a known margin, shave grams without inviting failure, and explain exactly why a structure will or won't hold. This is the discipline that decides whether a vehicle is robust, light, and trustworthy — or a liability waiting for the wrong load case.

> **What mastering it makes you.** The person who sizes the load-bearing parts with real margins, chooses metal vs. composite for the right reasons, predicts fatigue life instead of discovering it in the field, and turns a heavy over-built prototype into a light, certifiable flight article.

Structures is applied mechanics and calculus — the differential equations and linear algebra of [03-foundations-mathematics.md](../foundations/03-mathematics.md) governing how forces distribute through solids. It is the deep specialty within the broader mechanical engineering of [04-career-mechanical-engineering.md](../career/04-mechanical-engineering.md). The loads it carries come from the aerodynamics of [06-engineering-aerodynamics-and-flight-mechanics.md](06-aerodynamics-and-flight-mechanics.md) and the thrust of [05-engineering-propulsion-and-electric-propulsion.md](05-propulsion-and-electric-propulsion.md); the heat that weakens and expands it is the domain of [08-engineering-thermal-management.md](08-thermal-management.md); and the safety margins and failure analysis are the assurance discipline of [09-foundations-safety-assurance.md](../foundations/09-safety-assurance.md). The whole subject is a relentless first-principles optimization of strength and stiffness against mass, in the tradition of [01_first_principles_systems_engineering.md](../foundations/01-first_principles_systems_engineering.md).

---

## 1. Stress and strain — the fundamental quantities

When a force acts on a material, the internal force per unit area is **stress**; the resulting fractional deformation is **strain**. These are the two quantities everything else builds on:

$$ \sigma = \frac{F}{A} \quad [\text{Pa}], \qquad \varepsilon = \frac{\Delta L}{L} \quad [\text{dimensionless}] $$

For most engineering materials in their normal operating range, stress and strain are linearly proportional — **Hooke's law** — with the constant of proportionality being the **Young's modulus** $E$ (a measure of stiffness):

$$ \sigma = E\,\varepsilon $$

Stiffness ($E$) and strength (the stress at which it yields or breaks) are *different* properties, and confusing them is a classic error. Steel and aluminum have very different strengths but a structure made of either deflects according to its $E$. A material can be stiff but brittle (ceramic), or compliant but tough (rubber). The stress-strain curve tells the whole story:

```
 σ │        ___ ultimate strength (UTS)
   │      /    \___ fracture
   │    / ← yield point (σ_y)
   │   /
   │  / slope = E (elastic, reversible)
   │ /
   └────────────────► ε
     elastic | plastic (permanent)
```

Below yield, deformation is elastic and reversible. Past yield, it's plastic and permanent. The area under the curve is **toughness** (energy absorbed before fracture) — why a tough material survives an impact a strong-but-brittle one shatters under.

---

## 2. Three dimensions and Poisson's ratio

Real parts are three-dimensional, and stress is a tensor — nine components (six independent) describing normal and shear stresses on each face of a material element:

$$ \boldsymbol{\sigma} = \begin{bmatrix} \sigma_{xx} & \tau_{xy} & \tau_{xz} \\ \tau_{xy} & \sigma_{yy} & \tau_{yz} \\ \tau_{xz} & \tau_{yz} & \sigma_{zz} \end{bmatrix} $$

Stretching a bar in one direction makes it contract in the others, quantified by **Poisson's ratio** $\nu$ (~0.3 for metals):

$$ \varepsilon_{\text{lateral}} = -\nu\,\varepsilon_{\text{axial}} $$

The shear modulus relates to $E$ and $\nu$: $G = E/[2(1+\nu)]$. To predict yielding under combined (multiaxial) stress, you reduce the tensor to a single equivalent stress — the **von Mises stress** — and compare it to the yield strength:

$$ \sigma_{vM} = \sqrt{\tfrac{1}{2}\!\left[(\sigma_1-\sigma_2)^2 + (\sigma_2-\sigma_3)^2 + (\sigma_3-\sigma_1)^2\right]} \;<\; \sigma_y $$

This single scalar is what FEA reports and what you check against allowables — it captures how a part under complex loading yields when the distortion energy reaches a critical value.

---

## 3. Beam bending — the most useful structural model

Most structural members — spars, booms, brackets, landing legs — act as beams in bending. The **Euler-Bernoulli beam equation** governs how a beam deflects under load, and the bending-stress formula tells you the stress at any point:

$$ \sigma = \frac{M\,y}{I}, \qquad \frac{1}{R} = \frac{M}{EI}, \qquad EI\frac{d^4w}{dx^4} = q(x) $$

where $M$ is bending moment, $y$ the distance from the neutral axis, $I$ the **second moment of area** (the geometric stiffness of the cross-section), $R$ the radius of curvature, $w$ the deflection, and $q$ the distributed load. Two profound consequences:

- **Stress is highest at the outer fibers** (max $y$) and zero at the neutral axis — which is *why* I-beams and hollow tubes are efficient: they put material where stress is high and remove it from the useless center.
- **Bending stiffness scales with $I$**, and for a solid section $I \propto (\text{depth})^3$ — so depth is hugely powerful. Doubling a beam's height makes it ~8× stiffer in bending.

$$ I_{\text{rectangle}} = \frac{bh^3}{12}, \qquad I_{\text{circle}} = \frac{\pi d^4}{64}, \qquad I_{\text{tube}} = \frac{\pi(d_o^4 - d_i^4)}{64} $$

The hollow tube's near-equal $I$ at a fraction of the mass is the single most important lightweighting insight in structures — it's why drone arms, bike frames, and aircraft spars are tubes.

---

## 4. Buckling — when slender things collapse without yielding

A long, slender column under compression can fail suddenly by **buckling** — bending sideways — at a load far below its yield strength. This is a stability failure, not a strength failure, and it's catastrophic because it's sudden. The **Euler buckling load**:

$$ P_{cr} = \frac{\pi^2 E I}{(K L)^2} $$

where $L$ is length and $K$ the end-condition factor (1 for pinned ends, 0.5 for fixed). The lesson: buckling depends on stiffness ($EI$) and length, *not* material strength — a stronger alloy doesn't help a buckling-limited strut; only more $I$ or less length does. Thin-walled structures (aircraft skins, tubes) can also buckle locally (crippling, wrinkling) before global buckling, which is why aerospace structures use stiffeners, stringers, and sandwich panels. Buckling is the quiet killer of lightweight design — push lightweighting too far and a part that's strong enough still folds.

---

## 5. Torsion, shear, and combined loading

Beyond bending, members carry **torsion** (twisting) and **shear**. For a circular shaft in torsion:

$$ \tau = \frac{T\,r}{J}, \qquad \theta = \frac{T L}{G J} $$

where $T$ is torque, $J$ the polar moment of area, $G$ the shear modulus, and $\theta$ the twist angle. Closed thin-walled tubes are far better in torsion than open sections (a slit tube is dramatically weaker in twist — the reason structural tubes are closed). Real parts rarely see pure loading; they carry combined axial, bending, shear, and torsion simultaneously, and you superpose the stresses (within the elastic range) and reduce to von Mises to check against yield. Stress **concentrations** at holes, fillets, and notches multiply local stress by a factor $K_t$ (often 2–3×) — which is why sharp internal corners are designed out and holes are placed and sized carefully.

$$ \sigma_{\max} = K_t\,\sigma_{\text{nominal}} $$

---

## 6. Factor of safety — designing for the unknown

You never design a part to fail exactly at its expected load. The **factor of safety** (FoS) is the ratio of a material's capability to the applied stress, absorbing uncertainty in loads, material properties, manufacturing, and analysis:

$$ \text{FoS} = \frac{\sigma_{\text{allowable}}}{\sigma_{\text{applied}}} $$

In aerospace, the convention is precise and conservative:

- **Limit load** — the maximum expected in service.
- **Ultimate load** = limit × **1.5** (the standard aircraft factor) — the structure must not fail at ultimate.
- **Yield** — must not permanently deform at limit load.

| Application | Typical FoS |
|---|---|
| Aircraft structure (ultimate) | 1.5 |
| Spacecraft (varies, tested) | 1.25–2.0 |
| Pressure vessels | 2.5–4 |
| Lifting/human-rated ground | 4–8 |
| Unknown materials/loads | higher |

A low FoS means a light, efficient, but unforgiving structure (aerospace earns this through rigorous analysis and test); a high FoS means heavy but tolerant. Choosing FoS is a risk decision tied directly to the assurance arguments of [09-foundations-safety-assurance.md](../foundations/09-safety-assurance.md) — the margin *is* the safety case for the structure.

---

## 7. Fatigue — failure by repetition

The most insidious structural failure is **fatigue**: a part loaded well below its yield strength can crack and fail after enough load cycles. Vibration, gust cycles, takeoff/landing, and thermal cycling all accumulate damage. Fatigue caused the Comet airliner crashes and countless rotorcraft failures — it is the dominant failure mode for anything that flies repeatedly.

The relationship between stress amplitude and cycles to failure is the **S-N (Wöhler) curve**:

```
 σ_a │\
     │ \___
     │     \___
     │         \____  steel: fatigue limit (flat)
     │              \________________
     │  aluminum: keeps dropping (no limit)
     └──────────────────────────────► log N (cycles)
        10³    10⁵    10⁷    10⁹
```

A critical materials fact: **steel has an endurance limit** — below a certain stress amplitude it lasts effectively forever — while **aluminum does not**, so aluminum structures are inherently life-limited and must be retired or inspected on a schedule. Variable-amplitude loading accumulates damage by **Miner's rule**:

$$ \sum_i \frac{n_i}{N_i} \ge 1 \;\Rightarrow\; \text{failure}, \qquad \text{where } n_i = \text{cycles applied}, \; N_i = \text{cycles to fail at that level} $$

**Damage-tolerant design** assumes cracks exist and uses fracture mechanics — the stress intensity factor $K = \beta\sigma\sqrt{\pi a}$ and the Paris law for crack growth $da/dN = C(\Delta K)^m$ — to ensure a crack grows slowly enough to be caught at inspection before reaching critical size $K_{IC}$. This inspect-and-tolerate philosophy underlies modern aircraft certification.

---

## 8. The material palette — choosing the right stuff

Material selection is the lever that most directly trades strength, stiffness, weight, cost, temperature capability, and manufacturability. The figures of merit that matter for flight are **specific strength** ($\sigma_y/\rho$) and **specific stiffness** ($E/\rho$) — strength and stiffness per unit weight:

| Material | $E$ (GPa) | $\sigma_y$ (MPa) | $\rho$ (g/cm³) | Notes |
|---|---|---|---|---|
| Aluminum 6061-T6 | 69 | 276 | 2.70 | Cheap, workable, life-limited |
| Aluminum 7075-T6 | 72 | 503 | 2.81 | High-strength aero alloy |
| Titanium Ti-6Al-4V | 114 | 880 | 4.43 | Strong, hot, corrosion-proof, costly |
| Steel 4340 | 205 | 1000+ | 7.85 | Strong, stiff, heavy, endurance limit |
| CFRP (carbon/epoxy) | 70–200 | 600–2000 | 1.6 | Best specific properties, anisotropic |
| Magnesium | 45 | 150 | 1.74 | Lightest metal, flammable |

The **Ashby chart** (plotting $E$ vs $\rho$, $\sigma$ vs $\rho$ on log axes) is the master tool: it shows at a glance which material maximizes the right figure of merit for a given load case (e.g., $E^{1/2}/\rho$ for a light stiff panel, $E^{1/3}/\rho$ for a light stiff beam). Material choice is never about "the strongest" — it's about the best ratio for the specific failure mode and constraint.

---

## 9. Composites — anisotropy as a design freedom

Carbon-fiber-reinforced polymer (CFRP) dominates modern aerospace because its specific strength and stiffness beat all metals. But composites are **anisotropic** — strong along the fibers, weak across them — which is both their power and their peril. You don't just pick a material; you *design the material* by choosing fiber orientations in each ply of a laminate.

```
Layup [0/45/-45/90]s :
   0°  ──────────  carries primary axial load
  45°  ╱╱╱╱╱╱╱╱╱╱  carries shear
 -45°  ╲╲╲╲╲╲╲╲╲╲  carries shear (balanced)
  90°  ||||||||||  carries transverse load
```

Classical lamination theory predicts the stiffness matrix (the ABD matrix) of a layup from its plies, letting you tailor stiffness directionally — a freedom metals don't offer. The failure modes are different and trickier:

- **Delamination** — plies separating, often from impact or out-of-plane load (composites are weak through-thickness).
- **Matrix cracking, fiber breakage, buckling** of the fibers in compression (composites are weaker in compression than tension).
- **Barely-visible impact damage (BVID)** — a tool drop can cause internal delamination invisible from the surface, a major certification concern.

Composites also don't yield — they fail suddenly and brittlely, so the damage-tolerance and inspection philosophy is even more critical. Manufacturing (autoclave cure, fiber volume fraction, void content) directly determines strength, making process control part of structural integrity.

---

## 10. Finite Element Analysis — computing what hand calcs can't

Hand calculations (beam, column, torsion formulas) cover simple geometries and are essential for sanity and sizing. Real parts with complex geometry and loading need **Finite Element Analysis (FEA)**: discretize the part into thousands of small elements, assemble the global stiffness matrix, and solve for displacements under applied loads and constraints:

$$ [K]\{u\} = \{F\} \;\Rightarrow\; \{u\} = [K]^{-1}\{F\} \;\Rightarrow\; \text{recover } \sigma, \varepsilon $$

FEA is powerful and dangerous in equal measure — it always produces colorful stress plots, but **garbage in, garbage out.** The discipline:

- **Validate against hand calcs** — if FEA disagrees with a beam formula on a simple case, the model is wrong, not the formula.
- **Check mesh convergence** — refine until results stop changing; stress singularities at sharp corners never converge (a modeling artifact, not real).
- **Get boundary conditions right** — over-constraining or wrong loads invalidate everything; this is the #1 source of FEA error.
- **Know the analysis type** — linear static, modal (natural frequencies, for flutter/vibration), buckling, nonlinear, fatigue — each answers a different question.

Modal analysis deserves emphasis: a structure has natural frequencies, and if an excitation (rotor RPM, engine vibration, aero flutter) matches one, **resonance** amplifies deflection catastrophically. You design natural frequencies away from operating excitations — a structural requirement driven by propulsion and aero.

---

## 11. Lightweighting and design for manufacturing

The aerospace mandate is always: lighter, for the same strength and stiffness. Every gram of structure is a gram not spent on payload, fuel, or battery. The techniques:

- **Topology optimization** — let an algorithm remove material from low-stress regions, producing organic, bone-like shapes (now buildable with additive manufacturing).
- **Sandwich structures** — thin stiff skins on a light core (honeycomb, foam) maximize bending stiffness per weight (the $I \propto h^3$ trick taken to the limit).
- **Hollow and thin-walled sections** — put material at the periphery where stress lives.
- **Integrated parts** — combine many fasteners and brackets into one molded or printed piece, removing joints (joints are where weight and failures concentrate).
- **Material substitution** — metal to composite where the load case allows.

But lightweighting fights manufacturability, cost, inspectability, and damage tolerance. The thinnest possible wall buckles; the most optimized topology may be uninspectable or uncertifiable. Structural design is the negotiation between these — exactly the multi-constraint balancing of [01_first_principles_systems_engineering.md](../foundations/01-first_principles_systems_engineering.md), and the place where a good structures engineer earns their keep by knowing which constraint actually binds.

---

## 12. Tooling and ecosystem

| Need | Tools |
|---|---|
| FEA | ANSYS Mechanical, Abaqus, Nastran, CalculiX (open), COMSOL |
| CAD + simulation | SolidWorks Simulation, Fusion 360, CATIA, Creo |
| Composites | ANSYS ACP, ESAComp, HyperSizer |
| Topology optimization | nTopology, Altair OptiStruct, Fusion generative |
| Material selection | Granta/Ansys (Ashby charts), MMPDS data |
| Hand calc / validation | MATLAB, Python, Roark's formulas, spreadsheets |
| Test | strain gauges, load frames, fatigue rigs, DIC |

The non-negotiable workflow: hand-calc to size and sanity-check, FEA to refine complex geometry, and **physical test to validate** — because no analysis is trusted in flight hardware until a real part is loaded to failure and the numbers match.

---

## Sources & further study

- Richard Budynas & Keith Nisbett, *Shigley's Mechanical Engineering Design* — the standard reference for stress, fatigue, and FoS.
- James Gere & Barry Goodno, *Mechanics of Materials* — the foundational stress/strain/beam text.
- Michael Ashby, *Materials Selection in Mechanical Design* — the Ashby-chart methodology, essential for lightweighting.
- T.H.G. Megson, *Aircraft Structures for Engineering Students* — aerospace-specific structures and thin-walled analysis.
- Robert Jones, *Mechanics of Composite Materials* — the composites and lamination-theory standard.
- Norman Dowling, *Mechanical Behavior of Materials* — fatigue and fracture mechanics in depth.
- Warren Young & Richard Budynas, *Roark's Formulas for Stress and Strain* — the hand-calc bible.
- Bruhn, *Analysis and Design of Flight Vehicle Structures* — the classic aerospace structures reference.

> Framing note: Structures is the discipline of carrying load with the least material the physics allows, and it is unforgiving because failures are physical, sudden, and sometimes invisible until they're catastrophic. Master stress, buckling, fatigue, and materials, and you can size any load-bearing part with a margin you can defend, shave weight without inviting collapse, and tell — from a sketch and a load case — whether a structure will hold for one flight or ten thousand. That judgment is what makes a vehicle both light and trustworthy.
