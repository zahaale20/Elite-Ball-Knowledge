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

| # | Module | What it makes you | Status |
|---|---|---|---|
| 00 | **This index** | A map of the whole field | this file |
| 01 | First Principles & Systems Engineering | Decompose any system, reason about tradeoffs like a chief engineer | *planned* |
| 02 | Modern C++ & Real-Time Embedded | Write/read the flight-software language these companies live in | *planned* |
| 03 | [Guidance, Navigation & Control (GNC)](28-autonomy-gnc.md) | Make a vehicle know where it is and go where it's told | ✅ written |
| 04 | [Autonomy: Planning & Decision-Making](29-autonomy-planning-decision.md) | Turn "state of the world" into correct action | ✅ written |
| 05 | Distributed Systems, Comms & Mesh | Make many vehicles + operators act as one system (the "Lattice" problem) | *planned* |
| 06 | Simulation, Test & Verification | *Prove* a system works before it flies — the real moat | partial: see [24-autonomy-test-scaffold.md](24-autonomy-test-scaffold.md), [22-autonomy-px4-sitl.md](22-autonomy-px4-sitl.md) |
| 07 | Defense Domain & Acquisition | Speak the customer's language: missions, the kill chain, how DoD buys | see [14-career-dod-politics.md](14-career-dod-politics.md) |
| 08 | Company Strategy & The Moat | See *why* these companies win and where you create value | see [02-ten-year-mastery-plan.md](02-ten-year-mastery-plan.md) |

### Already-written companions (read alongside)
- **ML / AI for autonomy** → [20-autonomy-ml-ai.md](20-autonomy-ml-ai.md)
  is the deep perception + learning module. Module 04 here links into it rather
  than repeating it.
- **GNC & estimation** → [28-autonomy-gnc.md](28-autonomy-gnc.md) (the written
  Module 03). **Planning & decision-making** →
  [29-autonomy-planning-decision.md](29-autonomy-planning-decision.md) (Module 04).
- **Control theory** → [25-autonomy-control-theory.md](25-autonomy-control-theory.md).
- **Career execution** → [11-career-defense-aerospace-playbook.md](11-career-defense-aerospace-playbook.md)
  and the other `career-*` guides cover resume, interview, clearance, and the
  human game. Modules 07–08 give you the *substance* those guides help you present.

---

## Learning paths (don't try to boil the ocean)

Pick the path that matches your next 6–12 months. Each is ordered.

### Path A — "I want to be an autonomy / robotics software engineer" (your default)
`01 → 03 → 04 → ML_AI_AUTONOMY_GUIDE → 06 → 02 → 05`
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
