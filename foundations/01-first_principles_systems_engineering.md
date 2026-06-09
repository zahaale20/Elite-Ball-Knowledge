# Module 01 — First Principles & Systems Engineering

> **Where this sits.** This is the foundation module of the MASTERY track. Everything
> else — [Guidance, Navigation & Control](../autonomy/09-gnc.md),
> [Autonomy Planning & Decision-Making](../autonomy/10-planning-decision.md) — is a
> *specialization* of the way of thinking taught here. Read this first, then return to it
> whenever a downstream module feels like a pile of disconnected facts. The job of a
> systems engineer is to keep the whole picture in their head while everyone else holds a
> piece.
>
> **What "senior" actually means.** A senior engineer at a leading defense-technology company, Shield AI, Skydio, or
> the Skunk Works is not someone who memorized more equations. They are someone who can
> (a) reason from physics when the handbook runs out, (b) decompose a vague mission into
> verifiable requirements, (c) reason about an entire system's failure modes before
> building it, and (d) *tell the story* of that system convincingly to a room of skeptics.
> This module teaches all four.

**Companion code.** Throughout, we anchor abstract ideas to the real autonomy stack in
this repository — the VTOL drone running PX4 on a Raspberry Pi companion computer. Key
modules referenced: `policy/constitution.py` (the command gate), `policy/decisions.py`
(the tamper-evident hash-chain log), `policy/intent.py` (the LLM safety gate),
`onboard/geofence.py`, and the `navigation/` filters. See also the sibling docs
[README](../README.md), [Mastery Curriculum](../01-mastery-curriculum.md), [Ten-Year Plan](02-ten-year-mastery-plan.md),
and [ML/AI for autonomy](../autonomy/01-ml-ai.md).

---

## Table of Contents

1. [First-Principles Reasoning](#1-first-principles-reasoning)
2. [Systems-Engineering Discipline](#2-systems-engineering-discipline)
3. [Requirements & MBSE](#3-requirements--mbse)
4. [Tradespace & Decision Analysis](#4-tradespace--decision-analysis)
5. [Reliability & Safety Engineering](#5-reliability--safety-engineering)
6. [Margins & Error Budgets](#6-margins--error-budgets)
7. [The Systems Narrative](#7-the-systems-narrative)
8. [How Elite Engineers Operate](#8-how-elite-engineers-operate)
9. [Practice This Week](#9-practice-this-week)

---

## 1. First-Principles Reasoning

### 1.1 What "first principles" actually means

The phrase is overused. Operationally it means: **strip an argument down to the smallest
set of facts you are willing to defend, then rebuild upward using only logic and
physics.** You are forbidden from saying "because that's how it's usually done." Every
inference must trace back to a conservation law, a definition, a measured constant, or a
clearly stated assumption.

A first-principles thinker has a habit loop:

```
   ┌──────────────────────────────────────────────────────────────┐
   │  CLAIM / DESIGN CHOICE                                        │
   │      │                                                        │
   │      ▼                                                        │
   │  "What must be true for this to work?"  ── decompose ──┐     │
   │      │                                                  │     │
   │      ▼                                                  ▼     │
   │  Physical constraints      Definitions/identities   Assumptions
   │  (energy, momentum,        (power = force·velocity,  (must be
   │   thermo, EM, geometry)     SNR, etc.)                stated!)  │
   │      │                                                  │     │
   │      └──────────────── rebuild ──────────────────────┘       │
   │                          │                                   │
   │                          ▼                                   │
   │            Quantified answer + sensitivity                   │
   └──────────────────────────────────────────────────────────────┘
```

The discipline that separates an engineer from a hobbyist is the last box:
**a number with a stated uncertainty and a sensitivity**, not a vibe.

### 1.2 The four conservation anchors

Almost every aerospace estimate reduces to one of these. Memorize them as your "axioms":

| Anchor | Statement | Where it bites in a VTOL |
|---|---|---|
| Energy | $E$ stored is finite; power is $P=\dfrac{dE}{dt}$ | Battery Wh sets endurance |
| Momentum | Thrust comes from accelerating mass: $T=\dot m\,\Delta v$ | Rotor disk physics, hover power |
| Mass | Every gram costs lift/energy forever | SWaP budget, payload fraction |
| Information | A channel carries finite bits: Shannon $C=B\log_2(1+\mathrm{SNR})$ | Comms link budget, sensor bandwidth |

If you can map a problem to one of these, you can almost always produce a defensible
estimate in five minutes on a whiteboard.

### 1.3 Fermi estimation as a professional skill

Fermi estimation = getting within a factor of ~3 with zero references. It is how you sniff
out a bad spec *before* spending three weeks building to it. The method:

1. Decompose the unknown into a product/quotient of quantities you can bound.
2. Estimate each factor to the nearest power of ten (or half-power).
3. Multiply. Track units religiously — units are a free correctness check.
4. State the dominant uncertainty: "this is dominated by the hover-power assumption."

> **Senior tell.** Juniors reach for a datasheet. Seniors produce a number first, *then*
> check the datasheet, because the number tells them whether the datasheet is lying.

### 1.4 Worked example A — Hover power and endurance

**Question.** Our VTOL drone has all-up mass $m = 2.5\ \text{kg}$, four rotors of radius
$r = 0.13\ \text{m}$, flying near sea level ($\rho = 1.225\ \text{kg/m}^3$). It carries a
$4\text{S}$, $5000\ \text{mAh}$ LiPo. Roughly how long can it hover?

**Step 1 — Ideal (momentum-theory) hover power.** A rotor hovering must accelerate air
downward fast enough that the reaction equals weight. Momentum theory gives the *induced*
power for total thrust $T=mg$ across total disk area $A=N\pi r^2$:

$$
P_{\text{ideal}} = \frac{T^{3/2}}{\sqrt{2\rho A}}
$$

Numbers: $T = 2.5 \times 9.81 = 24.5\ \text{N}$. Disk area
$A = 4 \times \pi \times 0.13^2 = 0.212\ \text{m}^2$. Then

$$
P_{\text{ideal}} = \frac{24.5^{1.5}}{\sqrt{2 \times 1.225 \times 0.212}}
 = \frac{121.3}{\sqrt{0.520}} = \frac{121.3}{0.721} \approx 168\ \text{W}.
$$

**Step 2 — Real power via figure of merit.** Real rotors are ~60–70 % efficient at hover
(figure of merit $\mathrm{FM}\approx0.65$), and motors+ESCs add ~15 % loss
($\eta_{\text{drive}}\approx0.85$):

$$
P_{\text{elec}} = \frac{P_{\text{ideal}}}{\mathrm{FM}\,\eta_{\text{drive}}}
 = \frac{168}{0.65 \times 0.85} \approx 304\ \text{W}.
$$

**Step 3 — Energy available.** A $4\text{S}$ LiPo is nominally $14.8\ \text{V}$. Usable
capacity is *not* the full $5\ \text{Ah}$ — you reserve ~20 % to protect the cells:

$$
E = 14.8\ \text{V} \times 5\ \text{Ah} \times 0.80 = 59.2\ \text{Wh}.
$$

**Step 4 — Endurance.**

$$
t_{\text{hover}} = \frac{E}{P_{\text{elec}}}
 = \frac{59.2\ \text{Wh}}{304\ \text{W}} = 0.195\ \text{h} \approx \boxed{11.7\ \text{min}}.
$$

**Sanity check + sensitivity.** ~12 min hover for a 2.5 kg quad on a 5 Ah 4S pack is
exactly the right order of magnitude (real-world ~10–14 min). Note the dominant lever:
$P \propto T^{3/2} \propto m^{3/2}$. **Adding 0.5 kg of payload (20 % mass) costs ~30 %
endurance**, *and* the heavier pack needed to recover it adds more mass — the spiral that
makes aircraft design hard. This single relationship is why "just add a bigger battery"
usually doesn't work; see §4.4 (SWaP).

### 1.5 Worked example B — Forward-flight is cheaper (and why fixed-wing wins range)

Hover is the worst-case power state because the rotor must generate *all* lift by pushing
air down. In efficient forward flight a VTOL's wing carries the lift, and aerodynamic
power scales roughly with the classic lift/drag relation:

$$
P_{\text{cruise}} \approx \frac{W \, V}{(L/D)\,\eta_{\text{prop}}}.
$$

For $W=24.5\ \text{N}$, cruise $V=15\ \text{m/s}$, a modest $L/D=8$, and
$\eta_{\text{prop}}=0.7$:

$$
P_{\text{cruise}} = \frac{24.5 \times 15}{8 \times 0.7} \approx 66\ \text{W}.
$$

That's ~4.6× less than hover. Same battery now gives
$t = 59.2/66 = 0.90\ \text{h} \approx 54\ \text{min}$, and range
$R = V\,t = 15 \times 3230\ \text{s} \approx 48\ \text{km}$. **This factor-of-five gap is
the entire reason VTOL+fixed-wing hybrids exist:** vertical takeoff where you need it,
wing-borne cruise where range matters. Every architecture argument in the program traces
to this number.

### 1.6 Worked example C — Communications link budget

**Question.** Will a $0.1\ \text{W}$ (20 dBm) $2.4\ \text{GHz}$ telemetry link close at
$10\ \text{km}$ line-of-sight?

Link budgets are pure bookkeeping in decibels — everything adds:

$$
P_{\text{rx}} = P_{\text{tx}} + G_{\text{tx}} + G_{\text{rx}} - L_{\text{path}} - L_{\text{misc}}.
$$

Free-space path loss:

$$
L_{\text{path}} = 20\log_{10}(d) + 20\log_{10}(f) + 92.45 \ \ [\text{dB, } d\text{ in km}, f\text{ in GHz}].
$$

$$
L_{\text{path}} = 20\log_{10}(10) + 20\log_{10}(2.4) + 92.45 = 20 + 7.6 + 92.45 = 120.1\ \text{dB}.
$$

Budget (dBi antennas, 3 dB misc/polarization loss):

| Term | Value |
|---|---|
| $P_{\text{tx}}$ | $+20$ dBm |
| $G_{\text{tx}}$ | $+2$ dBi |
| $G_{\text{rx}}$ | $+5$ dBi |
| $L_{\text{path}}$ | $-120.1$ dB |
| $L_{\text{misc}}$ | $-3$ dB |
| **$P_{\text{rx}}$** | **$-96.1$ dBm** |

A typical $2.4\ \text{GHz}$ receiver sensitivity for a low-rate link is about
$-100\ \text{dBm}$. **Link margin $= -96.1 - (-100) = +3.9\ \text{dB}$ — it closes, but
barely.** A senior immediately notes: 3.9 dB is *not enough* (you want ≥10 dB for rain,
multipath, antenna nulls during banking turns). The honest conclusion is "marginal — needs
a higher-gain ground antenna or lower data rate," not "yes it works." That nuance is the
difference between a demo and a fielded system.

### 1.7 The first-principles checklist

- [ ] Did I write down my assumptions *as numbers*?
- [ ] Do the units cancel to the answer's units?
- [ ] Is the answer within a plausible order of magnitude vs. reality?
- [ ] Which single assumption dominates the uncertainty?
- [ ] What happens to the answer if that assumption is 2× off?

---

## 2. Systems-Engineering Discipline

First principles tell you *what is physically possible*. Systems engineering (SE) is the
discipline that turns "possible" into "a thing that demonstrably works, on schedule, that
won't kill anyone." It is the connective tissue between disciplines.

### 2.1 The central problem SE solves

A drone is not a pile of parts; it is an *emergent behavior*. The autopilot, the battery,
the comms link, the safety policy, and the operator together produce behavior no single
component exhibits. SE exists because **emergent failures live in the interfaces, not the
boxes.** Most program disasters are integration disasters.

### 2.2 Requirements: the `shall` statement

The atom of SE is the requirement. The canonical form is a **`shall` statement**:

> **R-ALT-010.** The system **shall** prevent commanded altitude from exceeding
> `max_alt_m` defined in the constitution, under all flight modes.

Rules for a good `shall`:

| Property | Bad | Good |
|---|---|---|
| Verifiable | "shall be safe" | "shall reject takeoff if battery < 30 %" |
| Singular | "shall do A and B" | split into two requirements |
| Unambiguous | "shall respond quickly" | "shall respond within 100 ms" |
| Necessary | gold-plating | traces to a real need |
| Implementation-free | "shall use a Kalman filter" | "shall estimate position to ≤2 m CEP" |

The last row matters: a requirement says **what**, not **how**. "Estimate position to ≤2 m"
is a requirement; "use a Kalman filter" is a design decision that should be free to change.

### 2.3 Requirement taxonomy: where requirements come from

```
   STAKEHOLDER NEED ("watch a 1 km² area for 8 hours")
        │  (analysis)
        ▼
   SYSTEM REQUIREMENT  ── "shall provide ≥8 h on-station coverage of 1 km²"
        │  (decomposition: one system req → many lower reqs)
        ├──────────────► DERIVED requirement
        │                 (emerges from a design choice you made —
        │                  e.g. "shall recharge in <20 min" appears only
        │                  *because* you chose battery swap over fuel)
        │
        └──────────────► ALLOCATED requirement
                          (the parent req apportioned to a subsystem —
                           "propulsion shall provide ≥48 min endurance")
```

- **Derived** requirements are *born from design decisions*. They didn't exist in the
  customer's head; your architecture created them. Tracking them is how you avoid
  "where did this constraint come from?" three months later.
- **Allocated** requirements are a parent requirement *divided up* among subsystems. The
  sum of the children must satisfy the parent — this is the basis of **budgets** (§6).

### 2.4 The V-model

The V-model is the spine of disciplined development. The left arm decomposes; the right arm
integrates and verifies; horizontal arrows link each design level to the test that proves
it.

```
  DEFINITION (decompose)                         VERIFICATION (integrate)
                                                                   
  Concept of Operations ◄───── validation ─────► Operational use / acceptance
        │                                                  ▲
        ▼                                                  │
  System Requirements ◄──────── system test ──────► System verification
        │                                                  ▲
        ▼                                                  │
  Subsystem / Architecture ◄─── integration test ─► Subsystem integration
        │                                                  ▲
        ▼                                                  │
  Component Design ◄─────────── unit test ────────► Component test
        │                                                  ▲
        └────────────────► IMPLEMENTATION ─────────────────┘
                         (code, fab, wiring)
```

The horizontal arrows are the point: **every requirement on the left must have a matching
test on the right.** A requirement with no test is a wish; a test with no requirement is
gold-plating.

### 2.5 Verification vs. Validation (the most-confused pair in SE)

| | Verification | Validation |
|---|---|---|
| Question | "Did we build the **thing right**?" | "Did we build the **right thing**?" |
| Against | the requirements/spec | the actual mission need |
| Example | "geofence rejects waypoints outside polygon" (matches R-GEO-020) | "operator can actually keep the drone over the target area for 8 h" |
| Failure mode | bug | wrong product |

You can pass every verification test and still fail validation — you built a flawless drone
that solves the wrong problem. Seniors obsess over validation early (ConOps, prototypes,
operator-in-the-loop) precisely because it's the expensive mistake.

### 2.6 Interfaces and the ICD

The **Interface Control Document (ICD)** defines exactly how two subsystems talk: message
formats, units, rates, electrical pinouts, timing, coordinate frames, who owns what.

> **Coordinate frames are the #1 silent killer.** Is "down" positive (NED) or negative
> (ENU)? Is the IMU mounted rotated 90°? A frame mismatch crashes aircraft. An ICD that
> pins the frame convention prevents the single most common integration failure in
> robotics. See [GNC §frames](../autonomy/09-gnc.md).

In this repo, the constitution + the onboard service boundary *is* an ICD: every
`/api/cmd/*` call has a defined contract (name, params, units in metres / 0–100 %), and
`constitution.py` is the gatekeeper that enforces it. Documenting that boundary explicitly
is what turns "some Python" into "a system with an interface."

---

## 3. Requirements & MBSE

### 3.1 Writing requirements that survive contact

The EARS pattern (Easy Approach to Requirements Syntax) keeps `shall` statements clean by
fixing the sentence skeleton:

| EARS type | Template |
|---|---|
| Ubiquitous | "The system **shall** \<response\>." |
| Event-driven | "**When** \<trigger\>, the system **shall** \<response\>." |
| State-driven | "**While** \<state\>, the system **shall** \<response\>." |
| Unwanted | "**If** \<condition\>, **then** the system **shall** \<response\>." |
| Optional | "**Where** \<feature\>, the system **shall** \<response\>." |

Applied to the real gate in `policy/constitution.py`:

> **R-BAT-030 (unwanted behavior).** *If* battery SoC is below `min_battery_pct_takeoff`,
> *then* the system *shall* reject any `takeoff` command and log a denial.

That requirement is *directly testable* against the pure function `evaluate_command`,
which is why the module was written as a pure function with no I/O — see §5.6.

### 3.2 Requirement "smells" (review heuristics)

When reviewing a spec, hunt for these:

| Smell | Why it's dangerous | Fix |
|---|---|---|
| "etc.", "and/or", "as appropriate" | unverifiable, infinite scope | enumerate explicitly |
| "fast", "robust", "user-friendly" | no acceptance criterion | attach a number |
| "shall be designed to" | describes effort, not behavior | state the behavior |
| compound `shall` (A and B and C) | partial pass is ambiguous | split |
| solution masquerading as need ("shall use ROS") | over-constrains design | restate as capability |
| passive voice with no actor | nobody owns it | name the responsible element |

### 3.3 MBSE and SysML — conceptually

**Model-Based Systems Engineering (MBSE)** replaces a stack of Word documents with a
single connected *model*. Instead of prose that drifts out of sync, you have one
authoritative model from which requirements, diagrams, and analyses are *views*. SysML
(the modeling language) gives you a handful of diagram types; you need the concepts, not
the tool:

| SysML diagram | Answers the question |
|---|---|
| Requirement diagram | What must be true, and how reqs trace to each other |
| Block Definition Diagram (BDD) | What are the parts (the **physical** architecture)? |
| Internal Block Diagram (IBD) | How are the parts connected (ports, flows)? |
| Activity / Sequence | What is the behavior / message ordering? |
| State Machine | What modes exist and what triggers transitions? |
| Parametric diagram | What equations bind the parameters (the math model)? |

You don't need a SysML tool to think in MBSE. The mindset is: **keep one source of truth
and derive everything else from it.** That is *exactly* the design rule already written
into `constitution.py`: "One source of truth — the constitution is the only place limits
live. Code reads it; it does not hardcode duplicates." That comment is MBSE philosophy
applied to autonomy.

### 3.4 Functional vs. physical architecture

These are two different decompositions of the same system, and confusing them is a classic
junior error.

```
  FUNCTIONAL architecture                 PHYSICAL architecture
  (what the system DOES)                  (what the system IS)
  ───────────────────────                 ──────────────────────
   • Sense environment                     • Pixhawk autopilot
   • Estimate state                        • Raspberry Pi companion
   • Plan mission                          • GPS / IMU / camera
   • Decide & gate command   ── maps to ─► • policy/ package
   • Actuate                               • ESCs + motors + servos
   • Assure / log                          • decisions.py log file
```

A function may span several physical parts; a physical part may host several functions.
The **allocation matrix** (which physical element performs which function) is one of the
most valuable artifacts a systems engineer produces — it's where "who's responsible for
this" lives.

### 3.5 The N² diagram (interface mapping)

An **N²** diagram is an N×N grid of subsystems on the diagonal; off-diagonal cells hold the
data flowing *from* the row *to* the column. It makes hidden coupling visible.

```
            │  GPS/IMU  │   Nav    │  Policy  │ Autopilot │   Log
   ─────────┼───────────┼──────────┼──────────┼───────────┼─────────
    GPS/IMU │    ███     │ raw meas │    --    │     --    │   --
   ─────────┼───────────┼──────────┼──────────┼───────────┼─────────
      Nav   │    --      │   ███     │  state   │  est pos  │   --
   ─────────┼───────────┼──────────┼──────────┼───────────┼─────────
    Policy  │    --      │   --      │   ███     │ allow/deny│ decision
   ─────────┼───────────┼──────────┼──────────┼───────────┼─────────
  Autopilot │   cmds     │   --      │ telemetry │    ███     │   --
   ─────────┼───────────┼──────────┼──────────┼───────────┼─────────
      Log   │    --      │   --      │    --     │     --     │  ███
```

Reading it: Policy receives `state` from Nav and `telemetry` from the autopilot, emits
`allow/deny` to the autopilot and a `decision` record to the Log. Every non-empty
off-diagonal cell is an interface that needs an ICD (§2.6). Empty cells you *expected* to
be full reveal a missing connection; full cells you *didn't* expect reveal sneak coupling.

---

## 4. Tradespace & Decision Analysis

### 4.1 There is no "best design," only best *for a weighting*

Every real design is a compromise among competing goods (range vs. payload vs. cost vs.
endurance). The set of all candidate designs is the **tradespace**. The senior's job is to
*explore* it rationally rather than fall in love with the first concept.

### 4.2 Objective / utility functions

To compare apples and oranges you map each design to a scalar **utility** $U$. A common
weighted-sum form:

$$
U(\mathbf{x}) = \sum_{i} w_i \, u_i\big(a_i(\mathbf{x})\big), \qquad \sum_i w_i = 1,
$$

where $a_i$ is an attribute (endurance, payload, cost), $u_i(\cdot)$ is a normalizing
"value curve" mapping that attribute to $[0,1]$, and $w_i$ is its weight. The discipline
here is **making the weights explicit and arguing about them in the open**, instead of
letting them hide inside someone's intuition.

> **Caution.** Weighted sums can hide unacceptable designs (a great score on range can mask
> a zero on safety). Always pair utility with **constraints/thresholds** ("safety is a gate,
> not a weighted term") — exactly how the constitution treats safety: not a soft preference
> but a hard fail-closed gate.

### 4.3 Pareto fronts

A design is **Pareto-optimal** if you cannot improve one objective without worsening
another. The frontier of such designs is the **Pareto front** — the only designs worth
discussing; everything "inside" the front is strictly dominated and should be discarded.

```
  endurance
    ▲
    │   x   x                  ● = Pareto-optimal (the front)
    │  x  ●                    x = dominated (throw away)
    │   x    ●
    │     x     ●
    │   x    x     ●
    │  x   x   x      ● ●
    └───────────────────────────► payload
```

The picture forces an honest conversation: "We can have more payload *or* more endurance;
here is the exchange rate. Which does the mission actually need?" Choosing a point on the
front is a *values* decision (the customer's), informed by an *engineering* analysis
(yours). Keeping those two roles distinct is a senior skill.

### 4.4 SWaP — Size, Weight, and Power

**SWaP** (often SWaP-C with Cost) is the master tradeoff of every embedded/aerospace system.
On an aircraft it is brutal because of the compounding loop from §1.4:

```
   more capability  ─►  more mass  ─►  more power to hover/cruise (P ∝ m^1.5)
        ▲                                          │
        │                                          ▼
        └──────────  bigger battery  ◄──  shorter endurance
                     (= more mass again)
```

This **mass spiral** is why "add a better sensor" is never free. A 200 g better camera
might cost 8 % endurance directly, force a bigger pack (another 150 g), and push you off
the Pareto front entirely. SWaP discipline means every gram is on a budget (§6) and every
new feature must "pay rent" in capability.

### 4.5 Sensitivity analysis

A point estimate is fragile; a **sensitivity** tells you which inputs actually matter.
Compute how the output $y$ moves with each input $x_i$, ideally in dimensionless
(elasticity) form:

$$
S_i = \frac{\partial y / y}{\partial x_i / x_i} = \frac{x_i}{y}\,\frac{\partial y}{\partial x_i}.
$$

From §1.4, endurance $t \propto m^{-1.5}$, so $S_{\text{mass}} = -1.5$: a 1 % mass increase
costs 1.5 % endurance. Knowing $|S_{\text{mass}}| > |S_{\text{voltage}}|$ tells you where to
spend engineering effort. **A senior reports answers as "$X$, most sensitive to $Y$," never
as a bare number.**

### 4.6 Margins and reserves

A **margin** is deliberate slack between your *predicted* performance and the *required*
performance, sized to cover what you don't know yet:

$$
\text{Margin} = \frac{\text{capability} - \text{requirement}}{\text{requirement}}\times 100\%.
$$

Reserves shrink as a program matures and uncertainty burns down (e.g., 30 % mass margin at
concept → 5 % at critical design review). Spending your entire margin early is how programs
die. **Reserves are not waste; they are the price of not knowing the future.**

---

## 5. Reliability & Safety Engineering

This is the section that distinguishes defense-grade autonomy from a hackathon demo. A demo
asks "does it work?" A fielded system asks "**how does it fail, how often, and what happens
when it does?**"

### 5.1 The vocabulary

| Term | Meaning |
|---|---|
| Fault | a defect (a bug, a cracked solder joint) |
| Error | a wrong internal state caused by a fault |
| Failure | externally visible deviation from required behavior |
| Hazard | a system state that *can* lead to harm given a worst-case environment |
| Mishap / accident | the actual loss event |
| Reliability $R(t)$ | probability of no failure through time $t$ |
| MTBF | mean time between failures $= 1/\lambda$ for constant rate $\lambda$ |

Note the chain: **fault → error → failure → (with environment) hazard → mishap.** Safety
engineering tries to break this chain at every link.

### 5.2 FMEA / FMECA — bottom-up

**Failure Modes and Effects Analysis** walks every component, asks "how can this fail?",
and traces the effect upward. **FMECA** adds *Criticality*. The standard scoring is the
**Risk Priority Number**:

$$
\text{RPN} = S \times O \times D
$$

(Severity × Occurrence × Detection, each 1–10; higher = worse). You rank by RPN and attack
the top of the list.

| Item | Failure mode | Effect | S | O | D | RPN | Mitigation |
|---|---|---|---|---|---|---|---|
| GPS | loses 3D fix | bad position estimate | 8 | 4 | 3 | 96 | nav filter holds on IMU; constitution requires `require_gps_fix_3d` to arm |
| Battery | sag under load | brownout, loss of control | 9 | 3 | 4 | 108 | SoC gates in constitution; reserve in budget |
| Comms | link drop | no operator control | 7 | 5 | 2 | 70 | autonomous geofence + RTL behavior |
| Operator | bad waypoint | flyaway | 9 | 4 | 2 | 72 | geofence.py rejects out-of-polygon waypoints |

The right column is the payoff: **each high-RPN row maps to a concrete mitigation that
already exists in this repo's `policy/` and `onboard/` code.** That mapping *is* your safety
argument made tangible.

### 5.3 Fault Tree Analysis — top-down

FTA starts at the undesired *top event* ("uncommanded flight outside geofence") and works
*downward* through Boolean gates to root causes. AND-gates need all inputs (good — implies
redundancy); OR-gates need any input (bad — single points of failure).

```
                ┌─────────────────────────────────────┐
                │ TOP EVENT: flight outside geofence   │
                └───────────────────┬─────────────────┘
                                    │  OR
              ┌─────────────────────┼─────────────────────┐
              ▼                     ▼                     ▼
     ┌────────────────┐   ┌──────────────────┐  ┌──────────────────┐
     │ bad position    │   │ geofence check    │  │ command bypasses │
     │ estimate        │   │ disabled/empty    │  │ policy gate      │
     └───────┬────────┘   └──────────────────┘  └──────────────────┘
             │ AND  (needs BOTH to be undetected)
        ┌────┴─────┐
        ▼          ▼
   GPS fault   nav filter
              fails to flag
```

The AND-gate under "bad position estimate" is *designed in*: it takes both a GPS fault
**and** a silent nav filter to produce the hazard, because the filter is built to flag
divergence. Redundancy turns OR-gates into AND-gates — that is the whole game of reliability
design.

### 5.4 Redundancy and graceful degradation

| Pattern | Idea | Drone example |
|---|---|---|
| Hot redundancy | spare runs in parallel, instant failover | dual IMUs in the autopilot |
| Cold redundancy | spare powered up on demand | backup comms radio |
| Analytic redundancy | infer a lost signal from others | nav filter coasts on IMU when GPS drops |
| Graceful degradation | shed capability, keep flying safely | GPS lost → hold → RTL → land, never just "off" |

**Graceful degradation is the senior's signature.** A novice system has two states: working
and crashed. A mature system has a *staircase* of safe fallbacks. The constitution's
fail-closed posture is exactly this: an unparseable constitution stops the service rather
than flying with "no constraints" — it degrades to **safe**, not to **permissive**.

### 5.5 DO-178C and Design Assurance Levels (overview)

DO-178C is the airborne-software assurance standard. You don't need to memorize it, but you
must know the shape: assurance rigor scales with **how bad the worst-case failure is.**

| DAL | Failure condition | Rough meaning | Rigor |
|---|---|---|---|
| A | Catastrophic | hull loss / fatalities | exhaustive (incl. MC/DC coverage) |
| B | Hazardous | severe injury | very high |
| C | Major | significant but survivable | high |
| D | Minor | nuisance | moderate |
| E | No safety effect | — | minimal |

The key principle is **assurance proportional to consequence.** You spend DAL-A effort on
the flight-control loop and DAL-E effort on the LED that says "recording." Misallocating
rigor — gold-plating the unimportant, under-testing the lethal — is a classic program
failure. (Defense autonomy adds its own layers, e.g. UL 4600-style safety cases and the
DoD's policy on autonomy in weapon systems, but the proportionality principle is universal.)

### 5.6 The safety case — and this repo as a real one

A **safety case** is a structured, *evidenced* argument that a system is acceptably safe for
a defined use in a defined environment. The standard form is a claim-argument-evidence
(GSN-style) tree:

```
   CLAIM: "The VTOL drone will not act outside its authorized envelope."
     │
     ├─ ARGUMENT: every command is gated before reaching the autopilot
     │     └─ EVIDENCE: constitution.py evaluate_command() is pure, fail-closed,
     │                   and unit-tested against historical telemetry
     │
     ├─ ARGUMENT: spatial limits are enforced independently of the operator
     │     └─ EVIDENCE: onboard/geofence.py rejects out-of-polygon waypoints
     │
     ├─ ARGUMENT: AI-generated intents cannot bypass the gate
     │     └─ EVIDENCE: policy/intent.py routes LLM output through the same
     │                   constitutional check (the LLM proposes; policy disposes)
     │
     └─ ARGUMENT: the decision history is auditable and tamper-evident
           └─ EVIDENCE: decisions.py SHA-256 hash-chain; verify_chain() proves
                        no record was edited, reordered, or deleted
```

This is not a toy. The repo implements three of the four pillars of a credible autonomy
safety case:

1. **A declarative, version-controlled authority** (`constitution.yaml` + `constitution.py`)
   — *what is allowed* lives in one auditable place, and the service **refuses to start
   without it** (fail-closed).
2. **An independent enforcement point** — every `/api/cmd/*` call is checked *before*
   forwarding to the autopilot, with `geofence.py` enforcing spatial limits and
   `intent.py` ensuring even LLM-proposed actions pass the same gate.
3. **A tamper-evident audit trail** (`decisions.py`) — each decision is one JSON line
   carrying a SHA-256 hash over its own content **plus the previous record's hash**, a
   hash chain. Editing any past record breaks every subsequent hash, so `verify_chain()`
   can *prove* the flight's decision history is intact — a black box for BVLOS and
   regulatory review.

When an interviewer asks "how do you make autonomy *trustworthy*?", this is your answer:
**a fail-closed declarative authority, an independent enforcement gate that even the AI must
pass through, and a cryptographically tamper-evident log.** That sentence is worth more than
any framework name-drop.

### 5.7 STPA — Systems-Theoretic Process Analysis

FMEA/FTA assume failures come from *broken components*. STPA assumes that in software-rich
autonomy, accidents often arise from **unsafe interactions between perfectly-functioning
components** — bad control actions, wrong timing, missing feedback. It models the system as
a **control loop** and asks where control can go wrong.

STPA's four guideword categories for an Unsafe Control Action (UCA):

1. A control action **required for safety is not provided** (geofence check skipped).
2. An **unsafe control action is provided** (takeoff approved at low battery).
3. A safe action is provided **too early/late or out of order** (RTL triggered after the
   fence is already breached).
4. A continuous action is **stopped too soon / applied too long** (motor cut at altitude).

```
   ┌────────────┐   control action    ┌────────────┐
   │ Controller │ ──────────────────► │  Actuator/ │
   │ (policy/   │                      │  Autopilot │
   │  autopilot)│ ◄────────────────── │            │
   └────────────┘     feedback         └────────────┘
        ▲   STPA asks: can the control action be unsafe?
        │   can feedback be missing/stale/wrong, so the
        │   controller's model of the world diverges from reality?
```

The deepest STPA insight: **most autonomy accidents are a mismatch between the controller's
*model of the world* and the *actual world*** (stale telemetry, a frame error, a missed
mode transition). This is why `constitution.py` is written as a *pure function of a
telemetry snapshot*: it forces the world-model to be an explicit, inspectable, replayable
input — you can re-run a past decision against the exact telemetry it saw and check it. That
design choice is STPA-aware engineering.

---

## 6. Margins & Error Budgets

### 6.1 "Where does the error come from?"

The single most useful habit in engineering is refusing to accept an error figure as a
monolith. **Every error is a sum of contributors, and your job is to enumerate and bound
each one.** An error budget is the allocated-requirement idea (§2.3) applied to *uncertainty*
instead of mass.

### 6.2 Combining error sources

For **independent random** contributors, errors add in quadrature (root-sum-square), because
variances add:

$$
\sigma_{\text{total}} = \sqrt{\sum_i \sigma_i^2}.
$$

For **correlated or worst-case bias** terms, they add linearly:

$$
e_{\text{total}} = \sum_i |e_i|.
$$

Knowing which regime you're in matters enormously: RSS of ten equal 1 m errors is 3.2 m;
linear sum is 10 m. **Assuming independence when errors are correlated is how you under-
predict failure** — a recurring root cause in real incidents.

### 6.3 A worked position error budget (forward-link to GNC)

Suppose R-NAV-010 requires horizontal position to ≤2.0 m (1σ). Allocate it:

| Contributor | 1σ | Type | Notes |
|---|---|---|---|
| GPS receiver noise | 1.2 m | random | RSS |
| IMU drift over update interval | 0.8 m | random | RSS |
| Map-matching residual | 0.6 m | random | RSS |
| Time-sync / latency bias | 0.5 m | bias | linear |
| Frame/lever-arm calibration | 0.4 m | bias | linear |

$$
\sigma_{\text{random}} = \sqrt{1.2^2 + 0.8^2 + 0.6^2} = \sqrt{2.44} = 1.56\ \text{m},
\quad e_{\text{bias}} = 0.5 + 0.4 = 0.9\ \text{m}.
$$

A defensible total combines them: $1.56 + 0.9 = 2.46\ \text{m}$ worst-case, or
$\sqrt{1.56^2+0.9^2}=1.80\ \text{m}$ if you can argue the biases are also independent.
**Either way the budget tells you exactly where to spend effort**: GPS noise dominates the
random pool, so a better antenna or RTK buys more than tightening map-matching. This is the
machinery the navigation filters in `navigation/` exist to manage; the full treatment —
where each $\sigma$ comes from and how the Kalman filter fuses them — is in
[GNC §error budgets](../autonomy/09-gnc.md). **Carry this discipline forward:
never quote an accuracy without being able to itemize its budget.**

### 6.4 Timing and control budgets

Errors aren't only spatial. The same discipline applies to a **latency budget** (sensor
sample → estimate → decision → actuation must fit inside the control loop period) and a
**stability margin** budget (gain/phase margins). If the policy gate in §5 adds 20 ms, that
20 ms is a line item in the loop's latency budget and must be reserved like any other
resource. A senior tracks *time* as rigorously as *mass*.

---

## 7. The Systems Narrative

You can master every section above and still fail the interview or the design review if you
cannot **tell the story.** The systems narrative is the skill of walking someone through an
end-to-end system as a coherent loop — sense → estimate → decide → act → assure — so they
trust both the system and you.

### 7.1 The canonical loop

Every autonomous system, from a Roomba to a Skydio, is the same loop. Memorize it; hang
every detail off it.

```
   ┌─────────┐   ┌──────────┐   ┌─────────┐   ┌────────┐   ┌─────────┐
   │  SENSE  │──►│ ESTIMATE │──►│ DECIDE  │──►│  ACT   │──►│ ASSURE  │
   │ sensors │   │  filter  │   │ policy/ │   │ motors │   │  log /  │
   │         │   │  (world  │   │ planner │   │ servos │   │  verify │
   │         │   │  model)  │   │         │   │        │   │         │
   └─────────┘   └──────────┘   └─────────┘   └────────┘   └────┬────┘
        ▲                                                        │
        └──────────────── feedback (the world changes) ─────────┘
```

The narrative power move: **for each box, name the failure mode and the mitigation.** That
shows you think in systems, not features.

### 7.2 A concrete worked narrative (this repo)

Here is exactly how to narrate the loop using this codebase. Practice saying it out loud
until it's fluent.

> **"Let me walk you through one command, end to end.**
>
> **Sense.** The Pixhawk streams telemetry — GPS fix and satellite count, battery
> state-of-charge, attitude, position — up to the Raspberry Pi companion. *Failure mode:*
> GPS can drop or sag; so the very first gate is that the system won't even **arm** unless
> `require_gps_fix_3d` and `min_gps_sats` are satisfied.
>
> **Estimate.** The `navigation/` filters fuse GPS, IMU, and visual odometry into a single
> position estimate with a known error budget — about 1.8 m, dominated by GPS noise. *Failure
> mode:* if GPS drops, the filter coasts on the IMU rather than jumping, degrading
> gracefully instead of lying.
>
> **Decide.** Now the interesting part. Say an operator — or even an onboard **LLM** —
> proposes 'fly to this waypoint and climb to 150 m.' That intent doesn't go straight to the
> motors. It hits `policy/intent.py`, which routes it through the *same* constitutional gate
> as a human command: the LLM proposes, but policy disposes. `constitution.py`'s
> `evaluate_command` — a **pure function** of the telemetry snapshot — checks it against a
> declarative, version-controlled `constitution.yaml`: is 150 m under `max_alt_m`? Is the
> battery above `min_battery_pct_takeoff`? And `onboard/geofence.py` checks the waypoint is
> inside the authorized polygon. *Failure mode:* a bad or malicious command — caught here,
> before it ever reaches the autopilot. The whole thing is **fail-closed**: if the
> constitution is missing or unparseable, the service refuses to start. Safe, not permissive.
>
> **Act.** Only an *allowed* command is forwarded to the autopilot, which closes the inner
> control loops and drives the ESCs and servos.
>
> **Assure.** Every decision — allowed *or* denied — is written as one JSON line by
> `decisions.py`, each record carrying a SHA-256 hash over its content **plus the previous
> record's hash.** It's a hash chain: edit, reorder, or delete any past record and every
> later hash breaks, so `verify_chain()` can *prove* the flight's history is intact. After
> any incident I can `grep` the log on any machine and answer 'why did the drone do X?'
> without re-reading code — a tamper-evident black box.
>
> **So the design philosophy is one sentence:** *a fail-closed declarative authority, an
> independent enforcement gate that even the AI must pass through, and a cryptographically
> tamper-evident audit trail.* That's how you make autonomy you can actually trust BVLOS."*

### 7.3 Why this narrative works in a design review

| What you demonstrated | What the reviewer concludes |
|---|---|
| Named each loop stage | You think in systems, not scripts |
| Gave each stage a failure mode + mitigation | You're a safety thinker |
| Distinguished "LLM proposes, policy disposes" | You understand AI assurance |
| Pure-function gate replayable on telemetry | You understand testability/STPA |
| Hash chain for audit | You understand accountability/forensics |
| One-sentence philosophy at the end | You can lead, not just code |

The structure — *loop, then failure/mitigation per stage, then a one-sentence thesis* — is
reusable for **any** system you ever build. Steal it.

---

## 8. How Elite Engineers Operate

Technical depth gets you in the room; these behaviors decide whether you become the person
the room defers to.

### 8.1 Ownership

A senior takes a problem to *done*, across boundaries, without being told. "Not my
subsystem" is not in their vocabulary when the system is failing. Ownership means you track
the loose end through someone else's code, file the issue, propose the fix, and verify it
landed. The org learns it can hand you ambiguity and get back resolution.

### 8.2 Writing: design docs and RFCs

Elite engineers **write before they build.** A design doc / RFC forces the thinking that
catches the expensive mistakes while they're still cheap (a paragraph, not a fab run). A
strong design doc has a predictable skeleton:

```
  1. Context & problem      — what, why now, who's affected
  2. Goals / Non-goals      — explicitly bound the scope
  3. Requirements           — the shall-statements (§2)
  4. Proposed design        — architecture, interfaces, diagrams
  5. Alternatives considered — and WHY rejected (this is the gold)
  6. Risks & mitigations     — FMEA-lite, what could go wrong
  7. Test/verification plan  — how we'll know it works (§2.4)
  8. Rollout & open questions
```

Section 5 ("Alternatives considered") is what separates a senior doc from a junior one: it
proves you explored the tradespace (§4) instead of building the first idea. **Writing is
thinking made reviewable.**

### 8.3 Red-team your own design

Before anyone else attacks your design, attack it harder yourself. Ask: *"If this fails in
the field at 2 a.m., what's the most likely cause?"* Then go fix that cause *now*. The
constitution's fail-closed posture, the geofence, and the hash chain all exist because
someone red-teamed the autonomy stack and asked "what if the command is wrong? what if the
operator is wrong? what if the *log* is tampered with?" Red-teaming is FMEA (§5.2) applied to
your own ego.

### 8.4 Strong opinions, weakly held

Have a clear, defensible position (so the team can move) — but update *instantly* when
evidence contradicts it (so you don't drive off a cliff). The failure modes on both ends:

- **Strong opinions, strongly held** → you ignore data, the team builds the wrong thing.
- **Weak opinions, weakly held** → you provide no leadership, decisions thrash.

The art is holding a firm hypothesis *and* genuinely wanting it disproven. "Here's what I
believe and exactly what evidence would change my mind" is the most senior sentence in
engineering.

### 8.5 Running a design review

A good review is not a presentation; it's a **structured adversarial collaboration.** As the
author: send the doc 24 h ahead, state the *decision you need*, timebox, capture every
objection as an action item with an owner, and separate "blocking" concerns from "nice-to-
have." As a reviewer: attack the *design*, never the person; ask "what would have to be true
for this to fail?"; and offer a path, not just a veto.

### 8.6 Build-Measure-Learn in a hardware-software org

Software can iterate hourly; hardware iterates in weeks and costs real money and risk. Elite
hardware-software orgs reconcile this by **moving as much learning as possible to the cheap,
fast layer:**

```
   FAST / CHEAP  ──────────────────────────────────►  SLOW / EXPENSIVE
   unit tests → SITL sim → HITL bench → tethered → flight test → fielded
   (seconds)    (minutes)   (hours)     (a day)    (a week)     (a program)

   PRINCIPLE: never learn at flight-test what you could have
              learned in SITL. Push every question left.
```

This is why `constitution.py`'s `evaluate_command` is a **pure function with no I/O and no
clock**: you can replay it against thousands of historical telemetry snapshots in CI in
seconds, catching policy bugs on the cheap-left side of the curve rather than discovering
them with a real airframe over a real target. The architecture *is* the build-measure-learn
strategy encoded in code. That is what elite engineering looks like: the right values baked
into the structure, so doing the safe thing is also the easy thing.

### 8.7 The senior mindset, condensed

| Junior instinct | Senior instinct |
|---|---|
| "Does it work?" | "How does it fail, and how often?" |
| Builds the first idea | Explores the tradespace, documents alternatives |
| Quotes a number | Quotes a number + its sensitivity + its budget |
| Optimizes their component | Optimizes the system, including the interfaces |
| Defends their design | Tries to break their own design first |
| Writes code | Writes the doc, *then* the code, *then* the test |
| "Not my subsystem" | "I'll own it to done" |

---

## 9. Practice This Week

A checklist to convert reading into capability. Do these against *this* repo where possible —
applied practice beats passive reading every time.

- [ ] **Fermi day.** Without datasheets, estimate this drone's (a) hover endurance, (b)
      cruise range, and (c) a 5 km link margin. Then check against §1.4–1.6 and explain any
      factor-of-2 gaps.
- [ ] **Write five `shall` statements** for the policy gate (alt, battery-arm, battery-
      takeoff, geofence, GPS-fix) using the EARS templates (§3.1). Mark each as derived or
      allocated.
- [ ] **Smell-test a spec.** Take the README/ROADMAP, find three requirement smells (§3.2),
      and rewrite them verifiably.
- [ ] **Build an N² diagram** of the real subsystems in `drone/` (`navigation/`, `policy/`,
      `onboard/`, autopilot, log) and circle every interface that lacks a written ICD.
- [ ] **Run a 5-row FMECA** on the airframe; map each high-RPN row to an existing mitigation
      in `policy/` or `onboard/` (§5.2). Where there's no mitigation, that's a backlog item.
- [ ] **Draw the safety-case tree** (§5.6) for one claim and point to the file that is the
      evidence. Confirm `verify_chain()` actually detects a tampered record (try editing a
      line of the decision log and re-verifying).
- [ ] **Write one position error budget** (§6.3) and identify the dominant term, then
      cross-check against [GNC](../autonomy/09-gnc.md).
- [ ] **Record the systems narrative** (§7.2) out loud in under 3 minutes, failure-mode per
      stage included. Re-record until it's fluent — this is your interview answer.
- [ ] **Write a one-page design doc** (§8.2 skeleton) for one improvement to the stack,
      including an "Alternatives considered" section, and red-team it (§8.3) before reading
      it twice.

---

### Cross-links

- Next, apply estimation and error budgets to real flight: [GNC — Guidance, Navigation &
  Control](../autonomy/09-gnc.md).
- Then study how the "decide" box plans and chooses: [Autonomy — Planning & Decision-
  Making](../autonomy/10-planning-decision.md).
- Repo context: [README](../README.md) · [Mastery Curriculum](../01-mastery-curriculum.md) ·
  [Ten-Year Plan](02-ten-year-mastery-plan.md) · [ML/AI for autonomy](../autonomy/01-ml-ai.md).

> **One thing to remember from Module 01:** *Reason from physics, decompose into verifiable
> requirements, budget every resource and every error, assume it will fail and design the
> staircase down, and be able to tell the whole story in one breath.* That is what the
> senior people carry — not more facts, but that discipline.
