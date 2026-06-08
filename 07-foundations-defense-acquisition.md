# Module 07 — Defense Domain & Acquisition

> **Why this file exists.** You can build the most elegant autonomy stack in the world and
> still build the *wrong thing*, because you don't understand the customer. The customer here
> is the U.S. defense enterprise — a strange, slow, enormous, rule-bound machine with its own
> language, its own clocks, and its own definition of "good." Engineers at Anduril, Shield AI,
> Skydio, and Palantir who get promoted are the ones who can translate between *what the
> warfighter needs* and *what the code does* — and who understand how money, requirements, and
> programs flow so they build something the system can actually buy and field. This file
> teaches you that translation layer at the *engineering* level: the kill chain, mission
> threads, how requirements are born, how DoD buys, and why the productized model exists.
>
> **What mastering it makes you.** An engineer who can sit in a room with a program manager, a
> contracting officer, and a colonel and *understand what each of them is actually optimizing
> for* — and design technical contributions that move the program forward, not just the demo.
> This is the difference between a coder and a defense-tech engineer. It is also, bluntly, what
> makes you promotable and what makes your equity worth something.

**Companion code & scope.** This module is the *substance* behind the customer; it complements,
and deliberately does **not** duplicate, the politics/hiring view in
[14-career-dod-politics.md](14-career-dod-politics.md) (which covers PPBE, JCIDS, OTAs, the
Valley of Death, COCOMs, and clearances from a *job-seeker's* angle). Read that for the human
game; read this for *how to build the right thing*. Throughout, we anchor to the author's
`drone/` autonomy stack — a GPS-denied-capable VTOL with onboard inference, track fusion, a
constitution-gated command policy, and a tamper-evident decision log — and show where each piece
maps onto a mission thread and a kill chain. See also
[11-career-defense-aerospace-playbook.md](11-career-defense-aerospace-playbook.md) for how to
present this fluency in interviews.

---

## Table of Contents

1. [The translation problem](#1-the-translation-problem)
2. [The kill chain: F2T2EA and OODA](#2-the-kill-chain-f2t2ea-and-ooda)
3. [Mission threads: how the customer actually thinks](#3-mission-threads-how-the-customer-actually-thinks)
4. [Where your drone sits in the kill chain](#4-where-your-drone-sits-in-the-kill-chain)
5. [How the DoD is organized (the buyer's anatomy)](#5-how-the-dod-is-organized-the-buyers-anatomy)
6. [The money: PPBE and the color of money](#6-the-money-ppbe-and-the-color-of-money)
7. [The requirement: JCIDS and how needs become specs](#7-the-requirement-jcids-and-how-needs-become-specs)
8. [The buy: the Adaptive Acquisition Framework](#8-the-buy-the-adaptive-acquisition-framework)
9. [The on-ramps: SBIR/STTR, OTAs, and the Valley of Death](#9-the-on-ramps-sbirsttr-otas-and-the-valley-of-death)
10. [TRLs: the maturity language](#10-trls-the-maturity-language)
11. [Cost-plus vs productized: the model that changed everything](#11-cost-plus-vs-productized-the-model-that-changed-everything)
12. [What an engineer must understand to build the right thing](#12-what-an-engineer-must-understand-to-build-the-right-thing)
13. [Practice this month](#13-practice-this-month)
14. [Sources & Citations](#sources--citations)

---

## 1. The translation problem

Every defense technical failure that *wasn't* an engineering failure was a translation
failure. The team built a thing that was technically excellent and operationally useless, or
fieldable but un-buyable, or buyable but a year too late for the threat. The defect was never
in the code; it was in the gap between the engineer's model of the problem and the customer's.

The customer speaks in **missions, threats, and effects.** The engineer speaks in **latency,
accuracy, and interfaces.** Neither is wrong; they are different layers of the same stack, and
somebody has to be bilingual. In a small defense-tech company, that somebody is often the
*engineer*, because there's no army of program managers to insulate you. The good news: the
two languages map onto each other cleanly once you learn the dictionary, and that dictionary is
this module.

```
  CUSTOMER LANGUAGE                    ENGINEER LANGUAGE
  ────────────────                     ─────────────────
  "Find the threat before it           detection range, sensor FoV, search pattern,
   finds us"                            probability of detection P_d
  "Hold custody of the target"     ⇄   track continuity, data association, world memory,
                                        time-to-reacquire after occlusion
  "Don't fratricide"                   the command gate, geofence, ROE encoding, the
                                        constitution-gated policy + decision log
  "Work when GPS is gone"              GPS-denied nav, vision/INS fusion, drift bound
  "We can't trust a black box"         explainability, the tamper-evident audit trail,
                                        run-time assurance monitors
```

Read that table in both directions until it's reflex. The left column is what gets you funded.
The right column is what gets it built. The engineer who can hold both is rare and valuable.

---

## 2. The kill chain: F2T2EA and OODA

The **kill chain** is the customer's master abstraction — the sequence of steps required to
turn "there is a threat out there" into "the threat is handled." If you learn one piece of
defense vocabulary, learn this, because *every* sensor, autonomy feature, and C2 product is
ultimately justified by which link of the kill chain it strengthens or which one it shortens.

### 2.1 F2T2EA — the canonical chain

The U.S. military's dynamic-targeting chain is **Find, Fix, Track, Target, Engage, Assess**:

```
  FIND ──► FIX ──► TRACK ──► TARGET ──► ENGAGE ──► ASSESS
   │        │        │          │          │          │
   │        │        │          │          │          └─ Did it work? (BDA) → re-enter chain
   │        │        │          │          └─ Apply the effect (kinetic or non-kinetic)
   │        │        │          └─ Decide & authorize; match effector to target (ROE, dwell)
   │        │        └─ Maintain custody over time; keep the track alive through occlusion
   │        └─ Localize precisely enough to act (coordinates, identity confirmation)
   └─ Detect that something is there at all (search, cue, tip)
```

| Link | The question | What it demands technically |
|---|---|---|
| **Find** | Is something there? | Search coverage, sensitivity, sensor cueing, P_d |
| **Fix** | Where exactly, and what is it? | Geolocation accuracy, classification/ID, sensor fusion |
| **Track** | Can I keep watching it? | Track continuity, data association, re-acquisition, world memory |
| **Target** | Should I act, and with what? | ROE, authorization, deconfliction, effector pairing |
| **Engage** | Apply the effect | Delivery accuracy, timing, the effector itself |
| **Assess** | Did it work? | Battle damage assessment, feedback to re-enter the chain |

The strategic insight defense-tech sells on: **compressing the kill chain.** The side that can
go Find→Assess faster, more reliably, and with fewer humans in the slow parts wins. Every
autonomy pitch is, at bottom, "we shorten or harden a link of this chain." Anduril's Lattice,
Shield AI's Hivemind — both are, in customer terms, *kill-chain compression engines.*

### 2.2 OODA — the cognitive version

Colonel John Boyd's **Observe, Orient, Decide, Act** loop is the kill chain's cognitive
sibling, and it's the one autonomy maps onto most directly because it describes *decision
tempo*:

```
        ┌──────────► OBSERVE ──────► ORIENT ──────► DECIDE ──────► ACT ──┐
        │            (sense)        (make sense)    (choose)       (do)   │
        └───────────────────────── feedback ───────────────────────────┘
```

Boyd's central claim: **the actor who cycles this loop faster gets inside the opponent's loop**
— acting on a fresh picture while the opponent is still orienting on a stale one — and the
opponent's world becomes incoherent. Autonomy's whole value proposition is *running OODA at
machine speed at the edge.* Your `drone/` stack is an OODA loop:

```
  OBSERVE  = IMX500 on-sensor inference + sensors
  ORIENT   = track fusion + world memory (the persistent picture)
  DECIDE   = planner + constitution-gated command policy (with the human's intent as a gate)
  ACT      = MAVSDK/PX4 commanding the airframe
  (and the decision log records every ORIENT→DECIDE step for assurance)
```

When you tell a customer "the drone closes its own OODA loop onboard, in GPS-denied, jammed
conditions, and logs every decision for audit," you have just described your repo *in their
language.* That sentence is worth more than a feature list.

---

## 3. Mission threads: how the customer actually thinks

A **mission thread** is an end-to-end operational scenario — a story of how forces accomplish a
specific task, step by step, across systems and people. It is the customer's *use case*, and it
is the unit in which they evaluate whether your thing is useful. Requirements that aren't tied
to a mission thread are orphans; the program office can't justify buying them.

### 3.1 Anatomy of a mission thread

```
  TRIGGER ──► tasks ──► systems/actors ──► info exchanges ──► decision points ──► effect
  ───────     ─────     ───────────────    ──────────────     ───────────────     ──────
  e.g.        "search   drone, GCS,        track data,        "engage / hold /    target
  "tip that   the area, operator, C2       custody handoff,   reacquire"          handled,
   a vehicle   ID the     network          warnings                                BDA fed
   is moving   contact,                                                            back
   in zone X"  hold it"
```

Notice what a mission thread surfaces that a feature list hides: the **information exchanges**
(who needs to tell whom, what, when), the **handoffs** (custody passing between platforms), and
the **decision points** (where a human or a policy gate must choose). These are exactly the
seams where systems fail and where integration value (Module 08) is created. A feature that
works in isolation but breaks a handoff is, in mission-thread terms, *worthless.*

### 3.2 Why engineers must read mission threads

When you read a mission thread, you stop optimizing the wrong thing. You discover that the
customer doesn't actually care that your detector is 2% more accurate; they care that custody
survives a 20-second occlusion behind a building, because that's the moment in *their story*
where the target gets away. The mission thread tells you which of your metrics matters and
which is vanity. **Always ask for the mission thread before you optimize.**

---

## 4. Where your drone sits in the kill chain

Make this concrete by mapping the author's actual stack onto F2T2EA. This is the exercise you
should be able to do for *any* technical contribution: "which link does this strengthen, and by
how much?"

| Kill-chain link | `drone/` module | What it contributes | The metric the customer cares about |
|---|---|---|---|
| **Find** | IMX500 on-sensor inference; search patterns | Onboard detection without phoning home | P_d, search rate, false-alarm rate |
| **Fix** | track fusion; GPS-denied nav | Geolocate the contact even without GPS | geolocation error (m), ID confidence |
| **Track** | track fusion + `world_memory` | Hold custody, re-acquire after occlusion | track continuity %, time-to-reacquire |
| **Target** | constitution-gated command policy; intent gate | Encode ROE; require human authorization; deconflict | gate correctness, false-engage rate = 0 |
| **Engage** | (out of scope for this airframe) | — | — |
| **Assess** | decision log; world memory; telemetry | Record what happened, feed it back | auditability, BDA latency |

Two of these deserve emphasis because they are where *your* stack is differentiated:

- **Track in GPS-denied** is hard and valuable. Anyone can track with GPS; holding custody when
  the adversary has jammed GPS (see [27-autonomy-counter-uas-ew.md](27-autonomy-counter-uas-ew.md))
  is a real-threat capability the customer will pay for.
- **Target with a constitution gate + tamper-evident log** is your assurance story. The single
  biggest blocker to fielding autonomy is *trust* — the customer's fear of a black box doing
  something it shouldn't. A command policy that provably enforces rules of engagement and logs
  every decision in a hash chain is the answer to "why should I trust this?" That maps straight
  to the safety case in [09-foundations-safety-assurance.md](09-foundations-safety-assurance.md)
  and the moat in [08-foundations-company-strategy-moat.md](08-foundations-company-strategy-moat.md).

> **Senior tell.** A junior demos "the drone found the truck." A senior says "this shortens the
> Find→Track links in the contested-ISR mission thread by closing the loop onboard, so it holds
> custody through GPS denial and a 20-second occlusion, and every targeting decision is gated by
> ROE and auditable." Same demo. One sentence gets funded.

---

## 5. How the DoD is organized (the buyer's anatomy)

You don't need the org chart memorized, but you need the *shape*, because it explains why the
buyer behaves the way it does. (The job-seeker's deep dive is in
[14-career-dod-politics.md](14-career-dod-politics.md); here is the engineer's minimum.)

### 5.1 Two halves that are constantly in tension

```
  ┌─────────────────────────────┐        ┌─────────────────────────────┐
  │  THE "TITLE 10" SIDE        │        │  THE "OPERATIONAL" SIDE     │
  │  (organize, train, EQUIP)   │        │  (fight)                    │
  │                             │        │                             │
  │  Military Departments:      │        │  Combatant Commands         │
  │  Army, Navy, Air Force      │        │  (COCOMs): INDOPACOM,       │
  │  + their acquisition execs  │        │  CENTCOM, etc.              │
  │                             │        │                             │
  │  They BUY and SUSTAIN.      │        │  They USE and have the      │
  │  Slow clock. Programs.      │        │  urgent NEEDS. Fast clock.  │
  └──────────────┬──────────────┘        └──────────────┬──────────────┘
                 │                                       │
                 └──────────── tension ──────────────────┘
        the warfighter needs it NOW; the acquisition system buys it in YEARS
```

The Services *equip*; the COCOMs *fight.* The COCOM has the urgent operational need ("I need
counter-UAS in the Pacific this year"); the Service runs the multi-year program that buys it.
That mismatch in clock speed is the source of half the dysfunction in defense acquisition — and
the entire business opportunity for fast-moving defense-tech. When you hear "we need to get
capability to the warfighter faster," that is the COCOM clock yelling at the Service clock.

### 5.2 The acquisition workforce you'll actually deal with

| Role | What they own | What they optimize for |
|---|---|---|
| **PM (Program Manager)** | Cost, schedule, performance of a program | Not getting yelled at; hitting milestones |
| **Contracting Officer (KO)** | The legal authority to obligate money | Compliance; a clean, protest-proof award |
| **Requirements officer** | The validated need (the document) | Traceability to a capability gap |
| **User / operator** | Actually employing the system | It works, it's simple, it doesn't get them killed |
| **T&E / safety** | Test & evaluation, airworthiness | Evidence; "prove it before it flies" |

Each optimizes for something different, and a technical proposal that ignores any of them
stalls. The PM can love your tech and the KO can still kill it because the contract vehicle is
wrong. The operator can love it and T&E can ground it for lack of a safety case. **Build for all
five.** Your test/verification discipline (Module 06) and safety case (Module 09) exist largely
to satisfy that last row.

---

## 6. The money: PPBE and the color of money

Money is the bloodstream, and it flows on a calendar that has nothing to do with your sprint.
(Politics covered in [14-career-dod-politics.md](14-career-dod-politics.md); engineering
implications here.)

### 6.1 PPBE — the two-year heartbeat

**Planning, Programming, Budgeting & Execution** is how the DoD decides what to fund. The brutal
fact for an engineer: the budget for a given fiscal year was largely decided **~two years
earlier.** If a capability isn't already in the plan, getting *new* money for it is slow — which
is exactly why fast on-ramps (SBIR, OTAs, Section 9) exist as relief valves.

### 6.2 The color of money — this one bites engineers directly

Appropriated money comes in "colors," and you legally **cannot** spend one color on another's
purpose. This shapes what you can build *when*:

| Color | Formal name | Buys | The engineer's reality |
|---|---|---|---|
| **RDT&E ("6.x")** | Research, Dev, Test & Eval | Prototypes, experiments, dev | Where new autonomy lives early; flexible-ish |
| **Procurement** | Procurement | Buying production units | Needs a mature, "done" product |
| **O&M** | Operations & Maintenance | Running/sustaining fielded gear | Sustainment, not new dev |

Why you care: a customer with only RDT&E money can fund your *prototype* but cannot *buy a
fleet*; that requires Procurement money, which requires a Program of Record (Section 8). This is
a mechanical cause of the **Valley of Death** (Section 9.3): a great prototype funded with RDT&E
that has no Procurement line to transition into simply dies, no matter how good it is. Knowing
this stops you from building a brilliant thing the customer structurally cannot buy at scale.

---

## 7. The requirement: JCIDS and how needs become specs

This is the part engineers most need and most lack: **where does a requirement come from, and
how does an operational need turn into a number in a spec you build to?**

### 7.1 The flowdown

```
  STRATEGY (NDS) ─► CAPABILITY GAP ─► VALIDATED REQUIREMENT ─► SYSTEM SPEC ─► YOUR REQS
  ──────────────    ──────────────    ────────────────────    ───────────    ─────────
  "deter in the     "we can't hold     JCIDS document         "the system     "track
   Pacific"          custody of mobile  (ICD/CDD/CPD):         shall maintain   continuity
                     targets under      a formally validated   custody of a     >= 95% through
                     GPS denial"        capability need        mobile ground    a 20 s GPS
                                                               target..."        dropout"
```

**JCIDS** (Joint Capabilities Integration and Development System) is the formal process that
*validates* a need so money can chase it. Its documents — the ICD (Initial Capabilities
Document), CDD (Capability Development Document), CPD (Capability Production Document) — are the
official statements of "we need this, validated, here are the key parameters." For an engineer,
the crucial artifacts inside them are:

- **KPPs (Key Performance Parameters):** the must-haves. Miss a KPP and the program can be
  cancelled. These are the requirements you do *not* trade away.
- **KSAs / APAs:** important but more tradeable parameters.

### 7.2 The requirement-flowdown discipline (this is just systems engineering)

The flowdown from a JCIDS KPP to *your* unit-test assertion is exactly the V-model left arm from
[06-foundations-simulation-test-verification.md](06-foundations-simulation-test-verification.md)
and the requirements discipline from
[01_first_principles_systems_engineering.md](01_first_principles_systems_engineering.md):

```
  KPP: "operate in GPS-denied environment"
     │  decompose
     ▼
  System req: "maintain position estimate with <= 5 m drift for >= 20 s after total GPS loss"
     │  decompose
     ▼
  Subsystem req: "vision/INS fusion bounds drift to <= 0.25 m/s with no GPS"
     │  decompose
     ▼
  Unit req + TEST: test_gps_loss_bounds_drift()  ← your code, your CI gate
```

The whole point: a good engineer can trace *every* line of safety-critical code up to a
validated need, and *every* validated need down to a test. That traceability is not bureaucracy
— it is how you prove, to a skeptical T&E officer, that the thing does what the warfighter
asked, no more and no less. It is also your defense when someone asks "why does the code do
*this*?": because KPP-3 says so, here's the thread.

### 7.3 The trap: requirements as ceiling vs floor

Government requirements are often written as a **floor** ("shall do at least X"), and a literal
contractor builds exactly X and stops. A *productized* company (Section 11) treats the validated
need as the floor and builds the *product* it believes the mission actually needs, then sells
that. This is a profound cultural difference and the seed of the next two sections.

---

## 8. The buy: the Adaptive Acquisition Framework

Once a need is validated and money exists, the DoD picks a **pathway** to actually acquire the
thing. The modern structure is the **Adaptive Acquisition Framework (AAF)** — a menu of pathways
tuned to different kinds of buys, replacing the old one-size-fits-all process.

### 8.1 The pathways you'll meet

| Pathway | For | Speed | Where your work fits |
|---|---|---|---|
| **Urgent Capability** | Combat-urgent needs | Months | Rapid fielding of a working capability |
| **Middle Tier (MTA)** | Rapid prototyping / rapid fielding | 2–5 yr | The sweet spot for proven-but-new tech |
| **Major Capability** | Big, complex platforms | Many years | The classic slow "program of record" |
| **Software Acquisition** | Software-centric systems | Continuous | Built for DevSecOps; the path autonomy *wants* |
| **Defense Business Systems** | IT/business systems | — | Not your world |
| **Services** | Buying services | — | Not your world |

The two that matter to defense-tech autonomy: **Middle Tier (MTA)** for rapid prototyping/fielding
of new capability, and the **Software Acquisition Pathway**, explicitly designed for continuous
delivery of software — which is the closest the DoD has come to admitting that software is never
"done" and must be iterated, the exact mindset your CI/verification stack (Module 06) embodies.

### 8.2 Program of Record (PoR) — the prize and the cage

A **Program of Record** is a formally established, budgeted, multi-year program — the thing with
a Procurement money line that can buy a fleet. Becoming part of a PoR is the prize (stable
funding, scale) and a cage (slow, requirements-locked, milestone-bound). The defense-tech
strategy (Module 08) is often to *win on speed outside* the PoR system first, prove the
capability, and then either become a PoR or render the slow PoR alternative obsolete.

---

## 9. The on-ramps: SBIR/STTR, OTAs, and the Valley of Death

Because PPBE is slow and PoRs are cages, the system grew **on-ramps** for new entrants and new
tech. Knowing these is how a small company (or a new capability inside a big one) gets its first
dollars and its first flight.

### 9.1 SBIR / STTR — the front door for small companies

The **Small Business Innovation Research** (and its university-partnered sibling **STTR**)
program is a phased funding ladder:

```
  PHASE I ──────────► PHASE II ──────────► PHASE III ─────────► (transition to a real buy)
  feasibility         prototype /          commercialization /
  (small $, months)   development          fielding (uses non-SBIR $)
                      (bigger $, ~2 yr)
```

It is the classic on-ramp: many defense-tech companies (Anduril included, early on) used SBIR
dollars to fund initial development. For an engineer, the relevant fact is that SBIR Phase I/II
work is *prototype-grade* funding — it gets you to a TRL where you can prove the capability, but
the leap to fielding (Phase III / a PoR) is the Valley of Death.

### 9.2 OTAs — the startup's favorite vehicle

**Other Transaction Authority** lets the government enter agreements *outside* the
traditional Federal Acquisition Regulation (FAR). Because OTAs sidestep much of the FAR's
overhead, they are dramatically faster and more flexible — ideal for prototyping with
non-traditional (commercial, venture-backed) companies that would otherwise be repelled by FAR
compliance cost. OTAs (often run through consortia) are how a lot of modern defense-tech actually
contracts. The engineer's takeaway: the *contract vehicle* determines your iteration speed as
much as your tech stack does.

### 9.3 The Valley of Death — the thing that kills good tech

```
   funding /
   maturity
      ▲
      │   RDT&E prototype          ████████ Program of Record (Procurement $)
      │   (SBIR/OTA, lots of       ████████ stable, scaled, fielded
      │    early money) ░░░░░░░                  ▲
      │                  ░░░░░░░░░░░░░░░░░░░░░░░░░░│
      │                         THE VALLEY        │  many great prototypes
      │                        OF DEATH ↓         │  never cross this gap
      │                  (no transition $,         │
      │                   no PoR, need gone,       │
      │                   color-of-money wall)     │
      └────────────────────────────────────────────────────────► time
```

The **Valley of Death** is the gap between a successful prototype and a funded production
program. Causes, all mechanical: the prototype money (RDT&E/SBIR) runs out; there's no
Procurement line because there's no PoR; the original urgent need cooled; or the program can't
absorb a new entrant mid-cycle. Most promising defense prototypes die here — *not* because the
tech failed, but because the *transition* failed. Understanding this is the whole reason the
productized model (Section 11) exists, and it's why "is there a path to scale-buy?" is a question
an engineer should ask *before* falling in love with a contract.

---

## 10. TRLs: the maturity language

The DoD measures how "real" a technology is on a 1–9 **Technology Readiness Level** scale. This
is a *lingua franca* — when a PM asks "what TRL are you at?" they are asking "how much risk
remains, and can I field this?" Knowing where your work sits, honestly, builds enormous
credibility.

```
  TRL 1  basic principles observed
  TRL 2  technology concept formulated
  TRL 3  proof of concept (analytic/experimental)
  TRL 4  component validated in LAB                ◄─ a notebook EKF; unit-tested logic
  TRL 5  component validated in RELEVANT environ.  ◄─ runs in PX4 SITL with realistic faults
  TRL 6  system/subsystem demo in RELEVANT environ.◄─ full stack in SITL + HITL, fault-injected
  TRL 7  system prototype demo in OPERATIONAL env. ◄─ real airframe, real range, real conditions
  TRL 8  actual system completed & qualified       ◄─ airworthiness, safety case signed
  TRL 9  actual system proven in OPERATIONS        ◄─ fielded, used in real missions
```

### 10.1 Mapping your stack to TRL — honestly

The author's `drone/` stack is, depending on the subsystem, around **TRL 4–6**: the pure logic
(validators, gate, decision log) is lab-validated (TRL 4) and unit/property-tested; the
integrated autonomy runs in PX4 SITL with fault injection (TRL 5–6); it has *not* yet been
qualified or proven operationally (TRL 7–9). Saying exactly this — "subsystem X is TRL 5, here's
the SITL evidence; getting to TRL 6 needs HITL on the Pixhawk; TRL 7 needs range time and a
safety case" — is *vastly* more credible than claiming a higher number, and it directly ties your
verification work (Module 06) and safety case (Module 09) to the maturity ladder the customer
uses.

> **Senior tell.** Juniors inflate TRL. Seniors *deflate* it and then show the evidence for the
> honest number and the concrete plan to climb the next rung. The honest, evidenced number wins
> the customer's trust faster than the inflated one ever could.

---

## 11. Cost-plus vs productized: the model that changed everything

This is the heart of why companies like Anduril exist and why an engineer's daily reality there
differs from a legacy prime. (Strategy depth is in
[08-foundations-company-strategy-moat.md](08-foundations-company-strategy-moat.md); the contrast
matters here because it shapes *what you build*.)

### 11.1 The two contracting philosophies

| | **Cost-plus (legacy prime)** | **Productized (new defense-tech)** |
|---|---|---|
| Who funds development | The government, per program | The company, with private/venture capital |
| What the gov buys | A bespoke system built to its spec | A finished product (often, a subscription) |
| Incentive | Reimbursed cost + fee → *cost is revenue* | Sell a product → *margin and reuse reward efficiency* |
| Risk holder | Government | The company |
| Iteration speed | Slow; tied to milestones/requirements | Fast; tied to product releases and CI |
| Reuse across customers | Low; everything is bespoke | High; one platform, many customers |
| Software is… | A deliverable, "done" at milestone | A living product, never done |

In **cost-plus**, the government pays the contractor's costs plus a fee, so — perversely —
*spending more can mean earning more*, and the contractor builds exactly the spec because
deviating is risk it isn't paid to take. In the **productized** model, the company spends *its
own* money to build a product, owns the IP, sells it (often as a recurring capability), and is
rewarded for efficiency and reuse — so it iterates like a software company and brings finished
capability to the customer rather than billing for the journey.

### 11.2 Why productized wins for autonomy specifically

Autonomy is *software-defined*. Its value compounds with iteration, data, and reuse — exactly
the things cost-plus structurally discourages and the productized model structurally rewards. A
company that:

- funds its own R&D (so it isn't waiting on PPBE's two-year clock),
- builds one platform reused across many customers (so each new sale is mostly margin),
- iterates the software continuously (so the capability improves every week),
- and brings a *finished, tested, assured* product to the customer,

...can move at a tempo the cost-plus world cannot match. That tempo *is* the OODA-loop argument
(Section 2.2) applied to the *business*: get inside the legacy primes' development loop and their
slow bespoke programs become obsolete before they ship.

### 11.3 What this means for you, the engineer

In a productized shop, **you own a product, not a deliverable.** That means your code lives
forever, ships continuously, and must carry its own verification and assurance (Modules 06 and
09) because there's no multi-year government test program to lean on — the company is on the hook.
It means the discipline this curriculum teaches — testable, logged, assured, reusable — isn't
optional polish; it is the literal mechanism that makes the business model work. Your
constitution-gated, hash-chain-logged, SITL-verified stack is a *miniature* of exactly the thing
that makes a productized defense company defensible.

---

## 12. What an engineer must understand to build the right thing

Pull it together into the operating checklist. Before you build a defense capability, you should
be able to answer all of these — and if you can't, you find out *before* you write the code, not
after the demo.

```
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  THE "RIGHT THING" CHECKLIST                                             │
  ├─────────────────────────────────────────────────────────────────────────┤
  │ 1. MISSION   Which mission thread does this serve? Get the thread.       │
  │ 2. KILL CHAIN Which link (F2T2EA) does it strengthen, and by how much?   │
  │ 3. NEED      Is there a VALIDATED requirement (JCIDS/KPP) behind it?      │
  │ 4. MONEY     What color of money funds it? Is there a path to scale-buy?  │
  │ 5. VEHICLE   What contract vehicle (SBIR/OTA/PoR/MTA) gets it bought?     │
  │ 6. TRL       What's the honest maturity, and what's the next rung's cost? │
  │ 7. TRUST     What's the assurance story (test + safety case + audit log)? │
  │ 8. VALLEY    Is there a transition path, or does it die after the proto?  │
  └─────────────────────────────────────────────────────────────────────────┘
```

Most engineers can answer 1, 6, and 7 (mission, maturity, assurance). The ones who get put in
charge can answer 3, 4, 5, and 8 too — because those are the questions that determine whether the
brilliant thing ever reaches a warfighter or dies in a lab as a "successful prototype." The whole
point of this module is to make those four questions as natural to you as a latency budget.

### 12.1 The one paragraph to internalize

> *The customer buys missions, not features. A mission decomposes into a kill chain; the kill
> chain decomposes into validated needs; needs flow down into specs and then into your tests.
> Money flows on a two-year clock in colors you can't mix, through contract vehicles whose speed
> matters as much as your code, and most good tech dies in the Valley of Death between prototype
> and program. The companies that win fund their own product, iterate like software, carry their
> own assurance, and bring finished capability inside the adversary's — and the bureaucracy's —
> decision loop. Your job as an engineer is to build something that is technically excellent
> AND traces to a real need AND can actually be bought AND can be trusted. Three out of four
> ships nothing.*

---

## 13. Practice this month

1. **Write the mission thread for your own drone.** One page: trigger → tasks → actors → info
   exchanges → decision points → effect, for a contested-ISR scenario. Then circle which of your
   `drone/` modules touches each step. You will find a gap; that gap is your next sprint.
2. **Map your stack to F2T2EA.** Reproduce the table in Section 4 for *your* current code. For
   each link, state the metric the customer cares about and whether you can currently measure it.
3. **Rate your TRL honestly, per subsystem,** with the evidence for each number and the concrete
   next-rung cost. Practice saying the deflated number out loud.
4. **Trace one requirement end-to-end.** Pick "operate in GPS-denied" and write the full
   flowdown from a KPP to a specific test in `drone/test/`. This is the artifact that makes a
   T&E officer trust you.
5. **Pick a contract vehicle.** For a hypothetical first dollar of funding, decide: SBIR Phase I,
   an OTA prototype, or chase a PoR? Justify it in terms of speed, money color, and the Valley of
   Death. There's no single right answer — the skill is *reasoning about it at all.*
6. **Read one real JCIDS-adjacent or DoD strategy doc.** Even a public capability statement.
   Notice how it talks about needs, not solutions, and practice translating it into the
   engineer's column of the Section 1 dictionary.

Do these and you will walk into any defense-tech room able to talk about your code in the
customer's language — which, more than any single algorithm, is what gets you hired, funded, and
promoted.

---

## Sources & Citations

**Books & foundational thinking**
- Boyd, John R. — *A Discourse on Winning and Losing* (the OODA loop; see also Coram, *Boyd: The
  Fighter Pilot Who Changed the Art of War*).
- Brose, Christian — *The Kill Chain: Defending America in the Future of High-Tech Warfare*
  (the modern argument for kill-chain compression and software-defined defense).
- Augustine, Norman — *Augustine's Laws* (the classic, wry account of defense-acquisition
  dysfunction).
- Spinney / Fitzgerald — writings on the "defense death spiral" and cost-plus incentives.

**Official frameworks & docs**
- DoD Adaptive Acquisition Framework (AAF): https://aaf.dau.edu/
- Defense Acquisition University (DAU) — pathways, PPBE, JCIDS explainers:
  https://www.dau.edu/
- JCIDS (Joint Capabilities Integration and Development System) — CJCSI 5123-series guidance.
- DoD Financial Management Regulation (the "color of money" / appropriations): DoD 7000.14-R.
- SBIR/STTR program: https://www.sbir.gov/  ·  DoD SBIR/STTR: https://www.dodsbirsttr.mil/
- Other Transaction Authority (OTA) — 10 U.S.C. §4021/§4022; DAU OTA guide.
- TRL definitions — DoD Technology Readiness Assessment Guidebook; GAO Technology Readiness
  Assessment Guide (GAO-20-48G): https://www.gao.gov/products/gao-20-48g
- U.S. National Defense Strategy (public summary) — for the strategy-to-need flowdown.

**Sibling guides (read alongside)**
- [14-career-dod-politics.md](14-career-dod-politics.md) — PPBE, JCIDS, OTAs, COCOMs, clearances
  from the *job-seeker's* angle; this module is the *engineering substance* behind it.
- [11-career-defense-aerospace-playbook.md](11-career-defense-aerospace-playbook.md) — how to
  *present* this fluency in interviews and a portfolio.
- [08-foundations-company-strategy-moat.md](08-foundations-company-strategy-moat.md) — why the
  productized model wins (Section 11 expanded).
- [09-foundations-safety-assurance.md](09-foundations-safety-assurance.md) — the assurance story
  the customer's T&E and safety officers demand.
- [06-foundations-simulation-test-verification.md](06-foundations-simulation-test-verification.md)
  — the verification evidence behind your TRL claims.
- [27-autonomy-counter-uas-ew.md](27-autonomy-counter-uas-ew.md) — the GPS-denied/EW threat that
  makes your "Track under jamming" capability valuable.

*Repository references (the `drone/` autonomy stack and its mapping onto the kill chain, mission
threads, and TRLs) trace to the author's own project. The acquisition, kill-chain, and
cost-plus-vs-productized framing reflects the author's professional goals and publicly available
information about the U.S. defense acquisition system and the modern defense-technology industry;
none of it reflects non-public program detail.*
