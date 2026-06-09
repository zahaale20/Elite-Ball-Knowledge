# Manufacturing & Design for Manufacturability — From Prototype to Production

> **Why this exists.** A design that exists only as a CAD model or a single hand-built
> prototype is not a product. The chasm between "it works on my bench" and "we ship
> 10,000 units that all work" is crossed by manufacturing knowledge: which process makes
> the part, what tolerances it can hold, what it costs at volume, and how to design the
> part so it can be made repeatably and assembled without skilled labor. In aerospace and
> defense, manufacturability also determines lead time, supply-chain resilience, and
> whether you can surge production when it matters. An engineer who ignores DFM designs
> parts that are beautiful, unmanufacturable, and late.
>
> **What mastering it makes you.** The engineer who picks the process before drawing the
> part; who specifies GD&T that controls function without gold-plating tolerances; who
> designs for assembly so a part can only go in one way; and who reads a quote and knows
> which feature is driving the cost.

Manufacturing turns the mechanical design of [13-career-mechanical-engineering.md](../career/13-mechanical-engineering.md)
into hardware and is constrained by the first-principles cost/physics reasoning of
[01_first_principles_systems_engineering.md](../foundations/01-first_principles_systems_engineering.md).
It is coupled to the actuator housings of [73-engineering-mechatronics-and-actuation.md](73-mechatronics-and-actuation.md),
the boards of [78-engineering-pcb-and-electronics-design.md](78-pcb-and-electronics-design.md),
and the packs of [79-engineering-batteries-and-energy-storage.md](79-batteries-and-energy-storage.md).
Manufacturing variation feeds the reliability statistics of
[77-engineering-reliability-and-failure-analysis.md](77-reliability-and-failure-analysis.md);
production readiness is a milestone in the systems lifecycle of
[76-engineering-systems-engineering-mbse.md](76-systems-engineering-mbse.md);
sensors that verify parts come from [74-engineering-sensors-and-instrumentation.md](74-sensors-and-instrumentation.md).
First-article inspection is a verification activity per
[06-foundations-simulation-test-verification.md](../foundations/06-simulation-test-verification.md).

---

## Table of Contents

1. [The process map — choosing how to make it](#1-the-process-map--choosing-how-to-make-it)
2. [Subtractive: machining](#2-subtractive-machining)
3. [Formative: injection molding & casting](#3-formative-injection-molding--casting)
4. [Additive manufacturing](#4-additive-manufacturing)
5. [Tolerances & GD&T](#5-tolerances--gdt)
6. [DFM & DFA principles](#6-dfm--dfa-principles)
7. [Cost, volume & the supply chain](#7-cost-volume--the-supply-chain)
8. [Scaling: prototype → pilot → production](#8-scaling-prototype--pilot--production)
9. [Practice this week](#9-practice-this-week)
10. [Sources & further study](#10-sources--further-study)

---

## 1. The process map — choosing how to make it

Process selection is driven by **volume, geometry, material, tolerance, and cost**.
The dominant trade is fixed (tooling) cost vs per-part cost: molding has huge tooling
cost amortized over millions; machining has near-zero tooling but high per-part cost.

| Process | Tooling cost | Per-part cost | Volume sweet spot | Tolerance |
|---|---|---|---|---|
| CNC machining | low | high | 1–10⁴ | ±0.01–0.05 mm |
| Injection molding | very high | very low | 10⁴–10⁷ | ±0.05–0.2 mm |
| Die casting | high | low | 10³–10⁶ | ±0.1 mm |
| Sheet metal | low–med | med | 10²–10⁵ | ±0.1–0.5 mm |
| 3D printing (FDM/SLA/SLS) | none | med–high | 1–10³ | ±0.1–0.3 mm |
| Metal AM (DMLS) | none | very high | 1–10² | ±0.1 mm |
| Extrusion | med | low | continuous | profile-dependent |

The crossover volume between two processes is where their **total cost** lines meet:

$$ C_\text{total}(n) = C_\text{tooling} + n\,c_\text{part} $$

Set two processes equal and solve for the break-even $n$. Below it, the low-tooling
process wins; above it, the low-per-part process wins. This single calculation governs
most "machine it or mold it" decisions — and it is pure
[01_first_principles_systems_engineering.md](../foundations/01-first_principles_systems_engineering.md)
cost reasoning.

```
cost/part
  |  machining (flat, high)
  |  ----------------------
  |          \
  |           \  molding (drops as 1/n + c)
  |            \____________________
  +-------------|----------------------> volume
            break-even
```

---

## 2. Subtractive: machining

CNC milling and turning remove material from a billet. The design rules follow from the
tool's geometry and access:

- **Internal corners cannot be sharper than the tool radius.** A pocket needs fillets ≥
  cutter radius; specify ≥ 1/3 of the pocket depth so a stiff tool reaches.
- **Deep pockets are expensive** — tool deflection forces slow, light cuts. Keep
  depth-to-width modest (≤ 3–4×).
- **Avoid features requiring tiny tools**; a 0.5 mm endmill is slow and fragile.
- **Minimize setups.** Every reorientation adds cost and stacks tolerance. Design so most
  features are reachable from few directions.
- **Threads:** prefer tapped holes to single-point threading; call out standard sizes.

Material removal rate and cutting force scale with feed and depth; surface finish improves
with smaller stepover at the cost of time. The machinist's intuition — "what tool, what
setup, what fixture?" — is what DFM for machining encodes. Tolerances tighter than
±0.01 mm demand grinding or precision processes and multiply cost; **only tighten what
function requires** (§5).

---

## 3. Formative: injection molding & casting

Injection molding forces molten thermoplastic into a steel mold; at volume it makes parts
for cents. The catch is the **mold** (tool): tens of thousands of dollars and weeks of
lead time, and it imposes strict geometry rules.

- **Uniform wall thickness.** Thick sections cool unevenly → **sink marks** and warp.
  Core out thick areas; keep walls constant (typ. 1–3 mm).
- **Draft angles.** Every face parallel to the pull direction needs ≥ 0.5–2° draft so the
  part ejects without scraping.
- **No undercuts** without side-actions/lifters (which add tool cost).
- **Ribs and gussets** for stiffness instead of thick walls; rib thickness ≤ 60% of the
  adjoining wall to avoid sink.
- **Gate, runner, ejector-pin placement** affect cosmetics and warp — design with the
  mold in mind.

Cooling time dominates cycle time and scales roughly with the square of wall thickness:
$$ t_\text{cool} \propto \frac{s^2}{\alpha} $$
where $s$ is wall thickness and $\alpha$ thermal diffusivity — another reason to keep
walls thin and uniform. **Die casting** applies the same logic to metals (aluminum, zinc,
magnesium) for structural parts. These processes are the volume backbone of consumer and
automotive hardware.

---

## 4. Additive manufacturing

3D printing builds parts layer by layer. It has revolutionized prototyping and
low-volume/complex-geometry production, but it is not free of rules.

| Process | Material | Strength | Best for |
|---|---|---|---|
| FDM | thermoplastic filament | anisotropic, weak in Z | jigs, prototypes |
| SLA/DLP | photopolymer resin | brittle, fine detail | cosmetic prototypes, molds |
| SLS | nylon powder | isotropic, durable | functional plastic parts |
| DMLS/SLM | metal powder | near-wrought | aerospace brackets, manifolds |

Key constraints: **support structures** for overhangs beyond ~45°, **anisotropy** (FDM
parts are weak between layers — orient loads in-plane), **surface roughness**, and slow
build rate. Metal AM enables **topology-optimized**, organic geometries impossible to
machine — consolidating an assembly of brackets into one printed part (a DFA win, §6) —
but demands post-processing (heat treat, HIP, machined interfaces) and qualification.
For defense, AM's value is **distributed/on-demand production** and rapid iteration,
echoing the prototyping ethos of skunkworks teams.

---

## 5. Tolerances & GD&T

A nominal dimension is meaningless without a tolerance: no part is ever exact.
**Geometric Dimensioning & Tolerancing** (ASME Y14.5) controls *function* — fit, form,
location — far better than ± box tolerances.

| Symbol | Control | Controls |
|---|---|---|
| ⏥ flatness | form | surface deviation |
| ⌭ cylindricity | form | round + straight |
| ⊥ perpendicularity | orientation | 90° to datum |
| ⌖ position | location | true position of a feature |
| ◎ concentricity | location | shared axis |
| ⌓ profile | form+location | a whole surface |

**Datums** establish the reference frame (primary, secondary, tertiary — like a 3-2-1
fixture). **Position tolerance** with **maximum material condition (MMC)** gives a *bonus
tolerance* as the feature departs from MMC — the elegant way to guarantee assembly of
mating bolt patterns.

**Tolerance stack-up** is the discipline of ensuring a chain of toleranced parts still
assembles. Worst-case stack sums the extremes:
$$ T_\text{stack} = \sum_i |T_i| $$
Statistical (RSS) stack, valid for many independent parts, uses:
$$ T_\text{RSS} = \sqrt{\sum_i T_i^2} $$
RSS yields tighter, more realistic assembly tolerances because not all parts hit their
extreme simultaneously — connecting directly to the process-capability statistics of
[77-engineering-reliability-and-failure-analysis.md](77-reliability-and-failure-analysis.md).
**Golden rule:** loosen every tolerance to the widest the function allows — tight
tolerances are where cost hides.

---

## 6. DFM & DFA principles

**Design for Manufacturability** minimizes the cost and risk of making each part;
**Design for Assembly** minimizes the cost and risk of putting them together. DFA often
dominates total cost.

DFA heuristics (Boothroyd-Dewhurst):
1. **Minimize part count** — every part is a BOM line, an inventory item, an assembly
   step, and a failure point. Combine functions; a printed/molded part can replace an
   assembly.
2. **Design for one-way assembly** — features that only fit one way (poka-yoke) prevent
   error. Asymmetric connectors, keyed slots.
3. **Eliminate fasteners** where possible — snap fits, press fits beat screws (screws are
   slow and loosen, see vibration in [77](77-reliability-and-failure-analysis.md)).
4. **Top-down assembly** — stack parts vertically so gravity helps; avoid reorienting.
5. **Provide self-alignment** — chamfers and lead-ins guide parts together.
6. **Standardize** fasteners and components — fewer part numbers, fewer tools.

The **DFA efficiency** metric quantifies it:
$$ E_\text{DFA} = \frac{N_\text{min}\times t_\text{ideal}}{t_\text{actual}} $$
where $N_\text{min}$ is the theoretical minimum part count. Driving this up is the core
of design-for-assembly reviews. DFM/DFA reviews belong in the design phase of the
V-model ([76-engineering-systems-engineering-mbse.md](76-systems-engineering-mbse.md)),
not after tooling is cut.

---

## 7. Cost, volume & the supply chain

Unit cost decomposes into material, processing, tooling (amortized), assembly, test,
yield loss, and overhead:

$$ c_\text{unit} = c_\text{mat} + c_\text{proc} + \frac{C_\text{tool}}{n}
   + c_\text{assy} + c_\text{test} + \frac{c_\text{unit}}{\text{yield}} $$

Note the yield term: a 90% yield inflates effective cost by ~11%; scrap is real money.
The **learning curve** (Wright's law) captures cost falling with cumulative volume:
$$ c(n) = c_1\,n^{\log_2(1-r)/\ ... } \;\Rightarrow\; c(2n) = (1-r)\,c(n) $$
i.e., each doubling of cumulative production cuts cost by a fixed fraction $r$
(typically 10–25%). This is why **volume is a moat** — SpaceX, Tesla, and Anduril ride
the learning curve down faster than competitors.

**Supply chain** decisions — make vs buy, single vs dual source, COTS vs custom, domestic
vs offshore — determine resilience and lead time. For defense, ITAR/EAR, DFARS, and
sourcing rules (no prohibited components) constrain the chain. **Vertical integration**
(make the critical parts yourself) trades capital for control and resilience — the
[41-companies-tesla-vertical-integration-data.md](../companies/41-tesla-vertical-integration-data.md)
strategy applied to hardware.

---

## 8. Scaling: prototype → pilot → production

Production ramps through stages, each de-risking the next:

```
EVT  →  DVT  →  PVT  →  MP
(does it   (is it      (can we    (mass
 work?)     reliable?)  build it   production)
                        at rate?)
```

- **EVT (Engineering Validation Test):** does the design function? Hand-built units,
  process not representative.
- **DVT (Design Validation Test):** does it meet *all* requirements including environment,
  reliability, regulatory? Production-intent parts, soft tooling.
- **PVT (Production Validation Test):** can the *factory* build it at rate, at yield, with
  the real line and operators?
- **MP (Mass Production):** sustained, with SPC monitoring.

Each gate has exit criteria (first-article inspection, reliability demonstration, yield
target). **Statistical Process Control** monitors the line: track a critical dimension's
mean and range on control charts; a process is "in control" when variation is only
common-cause. Process capability connects design tolerance to factory reality:

$$ C_{pk} = \min\!\left(\frac{\text{USL}-\mu}{3\sigma},\ \frac{\mu-\text{LSL}}{3\sigma}\right) $$

$C_{pk} \ge 1.33$ is the usual production target (≈ 63 ppm defects). This same statistic
feeds the reliability and yield models of
[77-engineering-reliability-and-failure-analysis.md](77-reliability-and-failure-analysis.md).

---

## 9. Practice this week

1. Take one of your machined prototype parts and redesign it for injection molding:
   uniform walls, draft, ribs, no undercuts — and compute the break-even volume vs machining.
2. Apply GD&T to a mating bolt pattern using position tolerance at MMC; compute the
   worst-case and RSS stack-up for the assembly.
3. Run a DFA analysis on a small assembly: count parts, identify which can be eliminated
   or combined, and compute $E_\text{DFA}$ before and after.
4. Build a unit-cost model across volumes 100 / 10k / 1M for two processes; plot total
   cost and find the crossover.

---

## 10. Sources & further study

- **Boothroyd, Dewhurst & Knight — *Product Design for Manufacture and Assembly*.** The DFM/DFA bible.
- **ASME Y14.5 — *Dimensioning and Tolerancing*.** The GD&T standard; learn it cold.
- **Bralla — *Design for Manufacturability Handbook*.** Process-by-process design rules.
- **Ulrich & Eppinger — *Product Design and Development*.** Process selection, cost, ramp.
- **Groover — *Fundamentals of Modern Manufacturing*.** The physics of each process.
- **Montgomery — *Introduction to Statistical Quality Control*.** SPC, $C_{pk}$, control charts.
- **MIL-STD-1916 / AS9100** for defense and aerospace quality systems, linking to [07-foundations-defense-acquisition.md](../foundations/07-defense-acquisition.md).

> Framing note: Manufacturing is design's reality check. The engineer who chooses the
> process before drawing the part, tolerances only what function needs, designs assemblies
> that go together one way, and rides the learning curve down is the one who turns a clever
> prototype into a fielded system at rate — which, in defense, is the difference between a
> demo and a deterrent.
