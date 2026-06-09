# Systems Engineering & MBSE — Requirements, Architecture & V-Model at Scale

> **Why this exists.** A drone is a few thousand parts; a missile system is tens of
> thousands; an aircraft program is millions, built by hundreds of teams over years. No
> individual holds it all in their head. Systems engineering is the discipline that keeps
> a large technical effort coherent: it captures what the system must do (requirements),
> decides how the pieces fit (architecture), defines the seams between them (interfaces),
> and proves the result satisfies the need (verification & validation). Done well it
> prevents the integration disasters where every subsystem "works" but the system fails.
> Done badly — or skipped — it is why programs run years late and billions over.
>
> **What mastering it makes you.** The engineer who can write a requirement that is
> verifiable rather than aspirational; who can draw the system boundary and the interfaces
> across it; who runs a trade study with weighted criteria instead of opinion; and who
> uses a model (SysML/MBSE) as the single source of truth instead of a graveyard of
> stale documents.

Systems engineering is the organizing layer above every other discipline: it integrates
the actuators of [73-engineering-mechatronics-and-actuation.md](73-mechatronics-and-actuation.md),
the sensors of [74-engineering-sensors-and-instrumentation.md](74-sensors-and-instrumentation.md),
the boards of [78-engineering-pcb-and-electronics-design.md](78-pcb-and-electronics-design.md),
and the power of [79-engineering-batteries-and-energy-storage.md](79-batteries-and-energy-storage.md)
into one system. It is the natural home of the first-principles decomposition of
[01_first_principles_systems_engineering.md](../foundations/01-first_principles_systems_engineering.md),
the verification rigor of [06-foundations-simulation-test-verification.md](../foundations/06-simulation-test-verification.md),
the safety assurance of [09-foundations-safety-assurance.md](../foundations/09-safety-assurance.md),
and the reliability budgets of [77-engineering-reliability-and-failure-analysis.md](77-reliability-and-failure-analysis.md).
Manufacturing readiness ([75-engineering-manufacturing-and-dfm.md](75-manufacturing-and-dfm.md))
is a systems milestone, and the acquisition framing comes from
[07-foundations-defense-acquisition.md](../foundations/07-defense-acquisition.md).

---

## Table of Contents

1. [What systems engineering is — and is not](#1-what-systems-engineering-is--and-is-not)
2. [Requirements — the contract with reality](#2-requirements--the-contract-with-reality)
3. [The V-model lifecycle](#3-the-v-model-lifecycle)
4. [Architecture & decomposition](#4-architecture--decomposition)
5. [Interfaces & ICDs](#5-interfaces--icds)
6. [Trade studies & decision analysis](#6-trade-studies--decision-analysis)
7. [Verification & validation matrices](#7-verification--validation-matrices)
8. [MBSE & SysML — the model as truth](#8-mbse--sysml--the-model-as-truth)
9. [Practice this week](#9-practice-this-week)
10. [Sources & further study](#10-sources--further-study)

---

## 1. What systems engineering is — and is not

Systems engineering (SE) is the management of **emergence and integration**: the system's
behavior arises from parts *and their interactions*, and SE owns the interactions. It is
not a substitute for domain depth — it relies on the mechanical, electrical, and software
specialists — it is the connective tissue that makes their work add up.

The SE value proposition is economic. Errors caught at requirements cost ~$1; the same
error caught in test costs ~$100; in the field, ~$1000+. SE front-loads thinking to keep
errors cheap.

```
cost to fix
  ^                                          *
  |                                      *
  |                              *
  |                  *
  |        *
  +--------------------------------------------> lifecycle phase
   req    design   build    test    field
```

The discipline's core activities: requirements, architecture, interfaces, integration,
verification, validation, and the *traceability* that links them. Frameworks: ISO/IEC/IEEE
15288 (lifecycle processes) and the INCOSE *Systems Engineering Handbook*. This is the same
decomposition habit taught in
[01_first_principles_systems_engineering.md](../foundations/01-first_principles_systems_engineering.md),
scaled to programs with hundreds of engineers.

---

## 2. Requirements — the contract with reality

A requirement states *what* the system must do, not *how*. Good requirements are the
foundation; bad ones poison everything downstream.

The properties of a good requirement (INCOSE):

| Property | Meaning | Bad example | Good example |
|---|---|---|---|
| Unambiguous | one interpretation | "fast response" | "respond within 100 ms" |
| Verifiable | testable | "user-friendly" | "operable with ≤ 3 button presses" |
| Complete | nothing missing | "operate in weather" | "operate in 0–95% RH, −20–50 °C" |
| Consistent | no contradictions | weight < 2 kg AND battery > 5 kg | — |
| Feasible | achievable | "infinite endurance" | "≥ 45 min hover at 25 °C" |
| Atomic | one thing | "logs and alerts and..." | split into separate reqs |
| Traceable | linked up/down | floating | derived from REQ-PARENT |

Requirements form a hierarchy: stakeholder needs → system requirements → subsystem
requirements → component requirements, each **derived** from and **traced** to its parent.
The verb matters: "shall" = binding requirement, "should" = goal, "will" = statement of
fact. Every "shall" must have a verification method (§7). A requirement with no test is a
wish; a test with no requirement is wasted effort.

---

## 3. The V-model lifecycle

The **V-model** is the canonical SE lifecycle: decomposition descends the left arm,
integration ascends the right, and each level of definition is tied to a matching level of
verification.

```
 Stakeholder ──────────────────────────────► Operational
 Needs        \                            /   Validation
               \                          /
  System Reqs ──\──────────────────────► System
                 \                      /  Verification
                  \                    /
   Subsystem ──────\────────────────► Subsystem
   Design           \                / Integration & Test
                     \              /
      Component ──────\──────────► Unit
      Design           \        /  Test
                        \      /
                         IMPLEMENT
                         (build)
```

The horizontal links are the discipline's secret: each left-side artifact defines its
own right-side test. System requirements (left) are proved by system verification
(right). Subsystem design is proved by subsystem integration test. This is why
requirements must be verifiable — the V *forces* a test for every requirement.

**Validation vs verification:** *Verification* asks "did we build the system right?" (meets
requirements). *Validation* asks "did we build the right system?" (meets the actual need).
A system can pass every verification test and still fail validation if the requirements
were wrong — which is why stakeholder involvement at the top of the V matters. The V's
rigor is the backbone of [06-foundations-simulation-test-verification.md](../foundations/06-simulation-test-verification.md)
and the assurance argument of [09-foundations-safety-assurance.md](../foundations/09-safety-assurance.md).

---

## 4. Architecture & decomposition

Architecture is the assignment of *function* to *form* and the definition of how the forms
interact. The system is decomposed along three coordinated views:

- **Functional architecture:** what the system does — a hierarchy of functions
  (e.g., "navigate," "communicate," "actuate") independent of implementation.
- **Physical architecture:** the components that perform the functions
  (the GNC computer, the IMU, the motor controller).
- **Allocation:** the mapping from functions to components (a matrix). One function may
  span several components; one component may host several functions.

Good architecture maximizes **cohesion within** a module and minimizes **coupling
between** modules — the same principle as software design, applied to whole systems. The
payoff is *modularity*: a well-bounded subsystem can be designed, tested, and replaced
independently. Anduril's productized approach and SpaceX's subsystem reuse both rest on
clean architectural boundaries.

The decomposition also defines the **work breakdown structure (WBS)** — who builds what —
and so couples technical architecture to organizational structure (Conway's Law: systems
mirror the communication structure of the org that builds them). Architecting the system
*is* architecting the team.

---

## 5. Interfaces & ICDs

If architecture defines the boxes, **interfaces** define the lines between them — and
interfaces are where integration fails. An **Interface Control Document (ICD)** is the
formal contract between two subsystems, owned jointly, frozen by agreement.

An ICD specifies, for every interface type:

| Interface | Specifies |
|---|---|
| Mechanical | bolt pattern, envelope, mass, CG, mounting loads |
| Electrical | connector pinout, voltage, current, signal levels |
| Data | protocol, message format, rate, units, byte order |
| Thermal | heat dissipation, allowable temperatures, cooling |
| RF | frequency, power, modulation, antenna |
| Logical/timing | sequencing, latency, handshakes |

The cardinal rule: **two teams must agree on the interface before either builds to it.**
The classic integration disaster — one team in metric, another in imperial (Mars Climate
Orbiter) — is an ICD failure. Interfaces should be *minimal* (fewer crossings = fewer
failure modes) and *explicit* (no assumed conventions). In MBSE, interfaces are modeled
ports and connectors (§8), so a change propagates automatically rather than rotting in a
stale document. Every electrical interface in the ICD becomes a constraint on the boards of
[78-engineering-pcb-and-electronics-design.md](78-pcb-and-electronics-design.md).

---

## 6. Trade studies & decision analysis

A **trade study** turns a design decision into a documented, repeatable analysis instead
of an argument. The method:

1. Define the decision and the alternatives (e.g., battery vs hydrogen vs hybrid power).
2. Define **evaluation criteria** (endurance, mass, cost, risk, TRL).
3. Assign **weights** $w_i$ to criteria (from stakeholder priorities, normalized $\sum w_i = 1$).
4. Score each alternative $j$ against each criterion, $s_{ij}$ (normalized).
5. Compute weighted scores and rank:

$$ S_j = \sum_i w_i\, s_{ij} $$

| Criterion | Weight | Battery | Hydrogen | Hybrid |
|---|---|---|---|---|
| Endurance | 0.35 | 0.4 | 0.9 | 0.8 |
| Mass | 0.25 | 0.8 | 0.5 | 0.6 |
| Cost | 0.20 | 0.9 | 0.3 | 0.5 |
| Maturity (TRL) | 0.20 | 0.9 | 0.4 | 0.6 |
| **Weighted total** | | **0.69** | **0.59** | **0.66** |

The discipline is in making weights and scores explicit and doing a **sensitivity
analysis**: if the ranking flips when a weight moves slightly, the decision is fragile and
needs more data. Trade studies are how SE converts engineering judgment into defensible,
auditable decisions — essential for the milestone reviews of
[07-foundations-defense-acquisition.md](../foundations/07-defense-acquisition.md).

---

## 7. Verification & validation matrices

Every requirement must be verified, by one of four methods (in increasing cost/fidelity):

| Method | Description | Example |
|---|---|---|
| **Inspection** | visual/physical examination | "the unit has two USB ports" |
| **Analysis** | calculation, modeling, simulation | structural margin by FEA |
| **Demonstration** | operate and observe (pass/fail) | "system boots in < 30 s" |
| **Test** | instrumented measurement vs criterion | "endurance ≥ 45 min, measured" |

The **Verification Cross-Reference Matrix (VCRM)** maps every requirement to its method,
its test case, and its result — the audit trail that proves nothing was forgotten:

```
REQ-ID   Requirement              Method   Test Case   Status
-------   ----------------------   ------   ---------   ------
SYS-012  endurance >= 45 min      Test     TC-031      PASS
SYS-013  MTBF >= 5000 h           Analysis AN-007      PASS
SYS-014  operate -20..50 C        Test     TC-040      OPEN
```

**Traceability** runs both ways: every requirement traces *up* to a stakeholder need and
*down* to a verification, with no orphans in either direction. A requirements-management
tool (DOORS, Jama, Polarion) maintains these links at scale. The VCRM is the connective
tissue between SE and the test program of
[06-foundations-simulation-test-verification.md](../foundations/06-simulation-test-verification.md),
and the evidence base for the safety case of
[09-foundations-safety-assurance.md](../foundations/09-safety-assurance.md).

---

## 8. MBSE & SysML — the model as truth

Document-based SE drowns in stale, inconsistent Word/Excel artifacts. **Model-Based
Systems Engineering (MBSE)** replaces them with a single, queryable **model** as the
authoritative source; documents become views generated from it.

**SysML** (the OMG modeling language, a UML profile) provides the diagram set:

| Diagram | Captures |
|---|---|
| Requirement | requirements + derive/satisfy/verify links |
| Block Definition (BDD) | system structure / hierarchy |
| Internal Block (IBD) | parts + ports + connectors (interfaces) |
| Activity | behavior / functional flow |
| State Machine | modes and transitions |
| Parametric | equations/constraints binding values |
| Sequence | interaction over time |
| Use Case | stakeholder goals |

The decisive advantage is **connected, consistent data**: a requirement links to the block
that *satisfies* it and the test case that *verifies* it; change the requirement and every
affected element is flagged. Parametric diagrams embed the engineering math (mass budgets,
power budgets, link budgets) so the model *computes* margins rather than storing stale
numbers. Tools: Cameo/MagicDraw, Capella (with the Arcadia method), SysML v2 (the emerging
text-and-graphics standard with a real API). MBSE turns SE from a documentation chore into
a living engineering model — the same shift from artifacts to executable truth that
[06-foundations-simulation-test-verification.md](../foundations/06-simulation-test-verification.md)
brings to test.

---

## 9. Practice this week

1. Take a system you know (a drone, a robot) and write 10 requirements that pass all the
   INCOSE quality checks; assign each a verification method.
2. Draw its V-model: stakeholder needs at top, decompose to subsystems, and pair each
   level with its verification activity.
3. Run a weighted trade study for one real decision (power source, compute, comms) with
   ≥ 4 criteria, weights, and a sensitivity check.
4. Build a tiny SysML model in Capella (free): one requirement diagram, one BDD, one IBD
   with ports, and trace a requirement to a block to a test.

---

## 10. Sources & further study

- **INCOSE — *Systems Engineering Handbook*.** The practitioner's reference.
- **ISO/IEC/IEEE 15288 — *Systems and software engineering — System life cycle processes*.**
- **NASA — *Systems Engineering Handbook* (SP-2016-6105).** Free, rigorous, aerospace-grounded.
- **Friedenthal, Moore & Steiner — *A Practical Guide to SysML*.** The MBSE/SysML standard text.
- **Voirin — *Model-based System and Architecture Engineering with the Arcadia Method*.** Capella in practice.
- **Buede & Miller — *The Engineering Design of Systems*.** Requirements, architecture, trade studies.
- **DAU / DoD acquisition guidance** for milestone reviews, tying to [07-foundations-defense-acquisition.md](../foundations/07-defense-acquisition.md).

> Framing note: Systems engineering is what keeps a thousand-part, hundred-engineer effort
> from collapsing under its own complexity. The engineers who ship integrated systems on
> time are the ones who write verifiable requirements, freeze clean interfaces, decide with
> trade studies, trace everything, and keep the truth in a living model rather than a pile
> of stale documents.
