# The Mastery Curriculum — Everything the Top People at Anduril-Class Companies Know

> **Why this exists.** The people who run autonomy, GNC, and product at companies
> like Anduril, Shield AI, Skydio, Palantir, and the elite groups inside the primes
> (Skunk Works, Phantom Works) are not smarter than you. They have **access** —
> to mentors, to programs, to a body of knowledge that is usually transmitted
> verbally inside the building and never written down for outsiders. This
> curriculum writes it down. It is the thing you said wasn't fair that you didn't
> have. Now you have it. Work through it and you will be **caught up** — and
> because you also *build* (this repo is a real autonomy stack), you will be ahead
> of most people who only have the theory.

This is not a reading list of links. It is a **self-contained, first-principles,
extreme-depth course** that teaches the *why* under every layer, anchored to the
real autonomy system in this repository (`drone/`). Every abstract idea is tied to
a file you can open, run, and modify.

---

## How to read this

There are three honest truths about how mastery actually works, and this
curriculum is built around them:

1. **Depth compounds; breadth impresses.** You need a few areas where you are
   genuinely deep (for you: autonomy + perception + the onboard stack you've
   built) and a working literacy everywhere else so you can integrate. Each module
   is written deep, but you do **not** need to master all of them before you are
   competitive — see the *learning paths* below.
2. **You learn the math by needing it.** Every equation here appears at the moment
   a real problem forces it, not as decoration. If a derivation doesn't yet make
   sense, build the thing it controls and come back.
3. **The moat is integration, not any single trick.** Top engineers are valued
   because they can reason across the whole loop —
   `sense → perceive → estimate → decide → act → assure → log` — and across the
   whole *organization* — physics, software, program, customer, mission. The last
   two modules (domain + strategy) are what separate a strong engineer from
   someone who gets put in charge.

---

## The modules

Every module below is now **written**. The `#` column is the conceptual module
number from the curriculum; the link points to the file that teaches it.

| # | Module | What it makes you | Status |
|---|---|---|---|
| 00 | **This index** | A map of the whole field | this file |
| 01 | [First Principles & Systems Engineering](01_first_principles_systems_engineering.md) | Decompose any system, reason about tradeoffs like a chief engineer | ✅ written |
| 02 | [Modern C++ & Real-Time Embedded](04-foundations-modern-cpp-realtime.md) | Write/read the flight-software language these companies live in | ✅ written |
| 03 | [Guidance, Navigation & Control (GNC)](28-autonomy-gnc.md) | Make a vehicle know where it is and go where it's told | ✅ written |
| 04 | [Autonomy: Planning & Decision-Making](29-autonomy-planning-decision.md) | Turn "state of the world" into correct action | ✅ written |
| 05 | [Distributed Systems, Comms & Mesh](05_distributed_systems_comms_mesh.md) | Make many vehicles + operators act as one system (the "Lattice" problem) | ✅ written |
| 06 | [Simulation, Test & Verification](06-foundations-simulation-test-verification.md) | *Prove* a system works before it flies — the real moat | ✅ written |
| 07 | [Defense Domain & Acquisition](07-foundations-defense-acquisition.md) | Speak the customer's language: missions, the kill chain, how DoD buys | ✅ written |
| 08 | [Company Strategy & The Moat](08-foundations-company-strategy-moat.md) | See *why* these companies win and where you create value | ✅ written |
| M | [Mathematics for Autonomy](03-foundations-mathematics.md) | The linear algebra, probability, calculus & Lie theory under every layer | ✅ written |
| S | [Safety Engineering & Assurance](09-foundations-safety-assurance.md) | Argue and prove "this is safe to fly" | ✅ written |

### Already-written companions (read alongside)
- **ML / AI for autonomy** → [20-autonomy-ml-ai.md](20-autonomy-ml-ai.md)
  is the deep perception + learning module. Module 04 here links into it rather
  than repeating it.
- **GNC & estimation** → [28-autonomy-gnc.md](28-autonomy-gnc.md) (the written
  Module 03). **Planning & decision-making** →
  [29-autonomy-planning-decision.md](29-autonomy-planning-decision.md) (Module 04).
- **Control theory** → [25-autonomy-control-theory.md](25-autonomy-control-theory.md).
- **Career execution** → [11-career-defense-aerospace-playbook.md](11-career-defense-aerospace-playbook.md)
  and the other `career-*` guides cover resume
  ([18](18-career-resume-portfolio.md)), interview
  ([17](17-career-interview-prep.md)), clearance
  ([16](16-career-security-clearance.md)), negotiation
  ([15](15-career-negotiation-compensation.md)), and growth
  ([19](19-career-leadership-growth.md)). Modules 07–08 give you the *substance*
  those guides help you present.

---

## The full repository map (all 30 guides)

The guides are numbered in bands: **01–09 foundations**, **10–19 career**,
**20–29 autonomy**, **30 tooling**.

| # | File | Band |
|---|---|---|
| 01 | [01-mastery-curriculum.md](01-mastery-curriculum.md) · [01_first_principles_systems_engineering.md](01_first_principles_systems_engineering.md) | Foundations |
| 02 | [02-ten-year-mastery-plan.md](02-ten-year-mastery-plan.md) | Foundations |
| 03 | [03-foundations-mathematics.md](03-foundations-mathematics.md) | Foundations |
| 04 | [04-foundations-modern-cpp-realtime.md](04-foundations-modern-cpp-realtime.md) | Foundations |
| 05 | [05_distributed_systems_comms_mesh.md](05_distributed_systems_comms_mesh.md) | Foundations |
| 06 | [06-foundations-simulation-test-verification.md](06-foundations-simulation-test-verification.md) | Foundations |
| 07 | [07-foundations-defense-acquisition.md](07-foundations-defense-acquisition.md) | Foundations |
| 08 | [08-foundations-company-strategy-moat.md](08-foundations-company-strategy-moat.md) | Foundations |
| 09 | [09-foundations-safety-assurance.md](09-foundations-safety-assurance.md) | Foundations |
| 10 | [10-career-aerospace-engineering.md](10-career-aerospace-engineering.md) | Career |
| 11 | [11-career-defense-aerospace-playbook.md](11-career-defense-aerospace-playbook.md) | Career |
| 12 | [12-career-software-engineering.md](12-career-software-engineering.md) | Career |
| 13 | [13-career-mechanical-engineering.md](13-career-mechanical-engineering.md) | Career |
| 14 | [14-career-dod-politics.md](14-career-dod-politics.md) | Career |
| 15 | [15-career-negotiation-compensation.md](15-career-negotiation-compensation.md) | Career |
| 16 | [16-career-security-clearance.md](16-career-security-clearance.md) | Career |
| 17 | [17-career-interview-prep.md](17-career-interview-prep.md) | Career |
| 18 | [18-career-resume-portfolio.md](18-career-resume-portfolio.md) | Career |
| 19 | [19-career-leadership-growth.md](19-career-leadership-growth.md) | Career |
| 20 | [20-autonomy-ml-ai.md](20-autonomy-ml-ai.md) | Autonomy |
| 21 | [21-autonomy-vtol-roadmap.md](21-autonomy-vtol-roadmap.md) | Autonomy |
| 22 | [22-autonomy-px4-sitl.md](22-autonomy-px4-sitl.md) | Autonomy |
| 23 | [23-autonomy-onboard-system.md](23-autonomy-onboard-system.md) | Autonomy |
| 24 | [24-autonomy-test-scaffold.md](24-autonomy-test-scaffold.md) | Autonomy |
| 25 | [25-autonomy-control-theory.md](25-autonomy-control-theory.md) | Autonomy |
| 26 | [26-autonomy-gnss-jamming-spoofing.md](26-autonomy-gnss-jamming-spoofing.md) | Autonomy |
| 27 | [27-autonomy-counter-uas-ew.md](27-autonomy-counter-uas-ew.md) | Autonomy |
| 28 | [28-autonomy-gnc.md](28-autonomy-gnc.md) | Autonomy |
| 29 | [29-autonomy-planning-decision.md](29-autonomy-planning-decision.md) | Autonomy |
| 30 | [30-ai-power-prompts.md](30-ai-power-prompts.md) | Tooling |

---

## Learning paths (don't try to boil the ocean)

Pick the path that matches your next 6–12 months. Each is ordered.

### Path A — "I want to be an autonomy / robotics software engineer" (your default)
`01 → 03 → 04 → 20 → 06 → 02 → 05`
Rationale: think in systems, master the estimation/control spine, then the
decision layer and perception, then prove it with sim/test, then go deep on C++
and the distributed problem.

### Path B — "I want GNC / state-estimation" (most mathematically prestigious)
`03 → 01 → 06 → 02`, with heavy time on the EKF and control-theory sections.

### Path C — "I want to be the person who gets put in charge"
`01 → 07 → 08 → 04`, plus enough of 02/03 to be credible with engineers.
This is the technical-leadership / product / program path.

### Path D — "I have an interview in 3 weeks"
Skim `01` and `08` for framing, drill the CS/coding parts of `02`, the EKF
intuition in `03`, and rehearse one end-to-end story from your own repo using
the **systems narrative** in `01 §7`.

---

## The single mental model to keep in your head

Everything in every module is a layer of one loop, running forever:

```
        ┌─────────────────────────── ASSURE / LOG (Module 06, policy/) ──────────────────────────┐
        │                                                                                          │
   ┌────┴─────┐   ┌───────────┐   ┌────────────┐   ┌──────────┐   ┌────────┐   ┌──────────────┐
   │  SENSE   │──▶│ PERCEIVE  │──▶│  ESTIMATE  │──▶│  DECIDE  │──▶│  ACT   │──▶│  ACTUATORS   │
   │ cameras, │   │ detect,   │   │ state: GNC │   │ planning,│   │ control│   │ motors,      │
   │ IMU, GPS │   │ track, ML │   │ EKF (03)   │   │ policy   │   │ laws   │   │ servos       │
   └──────────┘   │ (ML guide)│   └────────────┘   │ (04)     │   │ (03)   │   └──────────────┘
                  └───────────┘                     └──────────┘   └────────┘
        └──────────────── COMMS / MESH: share state & intent across vehicles (Module 05) ─────────┘
```

- **Modules 01 + 07 + 08** teach you to reason *about* this loop and the
  organization and mission that surround it.
- **Modules 02–06** teach you to *build every box* in it.
- The repo `drone/` is a working instance of this exact loop. Use it as your lab.

---

## A note on honesty and clearances

Much of this field is U.S.-export-controlled (ITAR/EAR) and clearance-gated.
Nothing in this curriculum is classified or controlled — it is the open
fundamentals, taught well. The career guides cover the clearance path. The
fastest way to "have what they have" is the combination this repo already gives
you: **real built systems + the written-down fundamentals + integrity**. Keep
building, keep this curriculum open beside the code, and close the gap.

---

## Sources & Citations

This curriculum is a synthesis; the depth lives in the written modules and the
canonical works they draw on.

**Written modules in this folder**
- [20-autonomy-ml-ai.md](20-autonomy-ml-ai.md) — perception & learning.
- [28-autonomy-gnc.md](28-autonomy-gnc.md) — guidance, navigation & control.
- [29-autonomy-planning-decision.md](29-autonomy-planning-decision.md) — planning & decision-making.
- [25-autonomy-control-theory.md](25-autonomy-control-theory.md) — control deep dive.

**Foundational works the modules build on**
- Thrun, Burgard & Fox — *Probabilistic Robotics*, MIT Press.
- Åström & Murray — *Feedback Systems* (free): https://fbswiki.org
- LaValle — *Planning Algorithms* (free): http://lavalle.pl/planning/
- Stroustrup — *A Tour of C++*; Meyers — *Effective Modern C++*.
- Kleppmann — *Designing Data-Intensive Applications*, O'Reilly.
- Beard & McLain — *Small Unmanned Aircraft: Theory and Practice*, Princeton.

**Official docs**
- PX4: https://docs.px4.io  ·  ROS 2: https://docs.ros.org  ·  MAVLink: https://mavlink.io

*Repo references point to the author's `pixhawk/drone/` project. The "caught up"
framing is the author's; the technical substance traces to the sources above.*
