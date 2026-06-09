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

## The full repository map (all 100+ guides)

The guides are numbered in bands: **01–09 foundations**, **10–19 career**,
**20–29 autonomy**, **30 tooling**, **31–36 information environment**,
**37–49 companies & beating the giants**, **50–64 deep autonomy & robotics**,
**65–79 engineering across domains**, **80–94 software, compute & infrastructure**,
and **95–106 math, science & cross-cutting foundations**, and
**107–114 hardware, AI compute, power & the human layer**. The first row table below
lists the original `01–36` spine; the expansion bands `37–106` are detailed in the
sections that follow it.

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
| 31 | [31-information-environment-systems.md](31-information-environment-systems.md) | Info Environment |
| 32 | [32-social-media-platform-mechanics.md](32-social-media-platform-mechanics.md) | Info Environment |
| 33 | [33-cognitive-bias-attention-and-narratives.md](33-cognitive-bias-attention-and-narratives.md) | Info Environment |
| 34 | [34-information-operations-history-defense.md](34-information-operations-history-defense.md) | Info Environment |
| 35 | [35-osint-verification-and-sensemaking.md](35-osint-verification-and-sensemaking.md) | Info Environment |
| 36 | [36-trust-safety-opsec-and-digital-resilience.md](36-trust-safety-opsec-and-digital-resilience.md) | Info Environment |

### Band 31–36: Information Environment & Influence Systems

A professional, **defense-oriented** band on how the modern information environment
actually works — platforms, audiences, cognition, influence operations, open-source
verification, and operational security. It exists because modern defense and autonomy
problems are not only hardware and software problems; they are sensing, networking,
decision, **trust, and information** problems. Everything here is framed for
**understanding, analysis, and defense — never manipulation.**

| # | Module | What it makes you |
|---|---|---|
| 31 | [Information Environment Systems](31-information-environment-systems.md) | Understand how platforms, audiences, and incentives shape modern perception and conflict |
| 32 | [Social Media Platform Mechanics](32-social-media-platform-mechanics.md) | Explain how feeds, recommendations, and engagement markets actually work (incl. how a company like Meta thinks) |
| 33 | [Cognition, Attention & Narratives](33-cognitive-bias-attention-and-narratives.md) | Reason about human belief formation, bias, and analytic failure modes — and communicate clearly under uncertainty |
| 34 | [Information Operations: History & Defense](34-information-operations-history-defense.md) | Recognize influence patterns and build resilience and detection (not conduct them) |
| 35 | [OSINT, Verification & Sensemaking](35-osint-verification-and-sensemaking.md) | Turn noisy public information into disciplined, calibrated judgment — lawfully and ethically |
| 36 | [Trust, Safety, OPSEC & Digital Resilience](36-trust-safety-opsec-and-digital-resilience.md) | Protect people, teams, and operations in contested information spaces |

These connect back to [05_distributed_systems_comms_mesh.md](05_distributed_systems_comms_mesh.md)
(message propagation), [07-foundations-defense-acquisition.md](07-foundations-defense-acquisition.md)
(mission/stakeholder context), [29-autonomy-planning-decision.md](29-autonomy-planning-decision.md)
(decision-making under uncertainty), and
[16-career-security-clearance.md](16-career-security-clearance.md) (security baseline).

---

## Bands 37–106: The Deep Expansion

The original `01–36` guides give you the spine. The expansion bands below give you
**elite, first-principles depth across every domain an autonomy/defense engineer
touches** — plus the strategic literacy to out-compete the giants. Each module is a
self-contained, extreme-depth course in the same house style.

### Band 37–49: Companies & Beating the Giants

What the biggest companies actually do that makes them win — and the specific,
transferable skills an ordinary person or small team needs to beat them. This is the
strategic companion to [08-foundations-company-strategy-moat.md](08-foundations-company-strategy-moat.md).

| # | Module | What it makes you |
|---|---|---|
| 37 | [How the Giants Win](37-companies-how-the-giants-win.md) | See the recurring winning patterns across SpaceX, Anduril, Palantir, Apple, Amazon, Nvidia, Tesla, Google |
| 38 | [SpaceX — Rapid Iteration](38-companies-spacex-rapid-iteration.md) | Operate a fly-test-break-fix, design-to-cost flywheel |
| 39 | [Anduril — Productized Defense](39-companies-anduril-productized-defense.md) | Understand counter-positioning and software-defined hardware |
| 40 | [Palantir — Forward-Deployed](40-companies-palantir-forward-deployed.md) | Own the data ontology and deploy into hard accounts |
| 41 | [Tesla — Vertical Integration & Data](41-companies-tesla-vertical-integration-data.md) | Build a fleet data flywheel and manufacturing moat |
| 42 | [Nvidia — Platform & Ecosystem](42-companies-nvidia-platform-ecosystem.md) | Build ecosystem lock-in and ride compute waves |
| 43 | [Apple — Integration & Taste](43-companies-apple-integration-taste.md) | Integrate end-to-end and say no with taste |
| 44 | [Amazon — Mechanisms & Customer Obsession](44-companies-amazon-mechanisms-customer-obsession.md) | Install working-backwards and narrative operating mechanisms |
| 45 | [Google — Scale & Infrastructure](45-companies-google-scale-infra.md) | Get leverage from infrastructure and 10x thinking |
| 46 | [Skunk Works — Small Elite Teams](46-companies-skunkworks-rapid-prototyping.md) | Run tiny, empowered, prototype-first teams |
| 47 | [The Asymmetric Playbook](47-companies-startup-asymmetric-playbook.md) | Beat incumbents with speed, focus, and counter-positioning |
| 48 | [Operating Mechanisms & Culture](48-companies-operating-mechanisms-and-culture.md) | Build the invisible machinery that compounds |
| 49 | [The Skills to Beat Them](49-companies-skills-to-beat-them.md) | A personal operating system of the transferable skills |

### Band 50–64: Deep Autonomy & Robotics

The full autonomy stack at research depth — perception, SLAM, estimation, planning,
learning, swarms, and deployment. Extends [20-autonomy-ml-ai.md](20-autonomy-ml-ai.md),
[28-autonomy-gnc.md](28-autonomy-gnc.md), and [29-autonomy-planning-decision.md](29-autonomy-planning-decision.md).

| # | Module |  | # | Module |
|---|---|---|---|---|
| 50 | [Perception Deep Dive](50-autonomy-perception-deep.md) | | 58 | [Multi-Agent & Swarm](58-autonomy-multi-agent-swarm.md) |
| 51 | [SLAM & Mapping](51-autonomy-slam-and-mapping.md) | | 59 | [Computer Vision](59-autonomy-computer-vision.md) |
| 52 | [Sensor Fusion](52-autonomy-sensor-fusion.md) | | 60 | [LiDAR & Radar](60-autonomy-lidar-radar-processing.md) |
| 53 | [Advanced State Estimation](53-autonomy-state-estimation-advanced.md) | | 61 | [Visual-Inertial Odometry](61-autonomy-visual-inertial-odometry.md) |
| 54 | [Motion Planning](54-autonomy-motion-planning.md) | | 62 | [Sim-to-Real](62-autonomy-sim-to-real.md) |
| 55 | [Trajectory Optimization](55-autonomy-trajectory-optimization.md) | | 63 | [Foundation Models for Robotics](63-autonomy-foundation-models-robotics.md) |
| 56 | [Reinforcement Learning](56-autonomy-reinforcement-learning.md) | | 64 | [Edge Inference & Deployment](64-autonomy-edge-inference-deployment.md) |
| 57 | [Imitation Learning](57-autonomy-imitation-and-learning-from-demo.md) | | | |

### Band 65–79: Engineering Across Domains

The hardware and physical-engineering breadth that makes you fluent across the whole
vehicle — firmware, FPGAs, RF, power, propulsion, aero, structures, thermal,
mechatronics, sensors, manufacturing, systems engineering, reliability, PCB, and
batteries.

| # | Module |  | # | Module |
|---|---|---|---|---|
| 65 | [Embedded Firmware](65-engineering-embedded-firmware.md) | | 73 | [Mechatronics & Actuation](73-engineering-mechatronics-and-actuation.md) |
| 66 | [FPGAs & HW Acceleration](66-engineering-fpga-and-hardware-accel.md) | | 74 | [Sensors & Instrumentation](74-engineering-sensors-and-instrumentation.md) |
| 67 | [RF & Comms Systems](67-engineering-rf-and-comms-systems.md) | | 75 | [Manufacturing & DFM](75-engineering-manufacturing-and-dfm.md) |
| 68 | [Power Electronics](68-engineering-power-electronics.md) | | 76 | [Systems Engineering & MBSE](76-engineering-systems-engineering-mbse.md) |
| 69 | [Propulsion](69-engineering-propulsion-and-electric-propulsion.md) | | 77 | [Reliability & Failure Analysis](77-engineering-reliability-and-failure-analysis.md) |
| 70 | [Aerodynamics & Flight Mechanics](70-engineering-aerodynamics-and-flight-mechanics.md) | | 78 | [PCB & Electronics Design](78-engineering-pcb-and-electronics-design.md) |
| 71 | [Structures & Materials](71-engineering-structures-and-materials.md) | | 79 | [Batteries & Energy Storage](79-engineering-batteries-and-energy-storage.md) |
| 72 | [Thermal Management](72-engineering-thermal-management.md) | | | |

### Band 80–94: Software, Compute & Infrastructure

The production-software depth behind any fielded autonomy system — distributed
systems, GPUs, RTOS, networking, data, MLOps, security, crypto, observability,
cloud, Rust, compilers, performance, system design, and testing.

| # | Module |  | # | Module |
|---|---|---|---|---|
| 80 | [Distributed Systems Deep](80-software-distributed-systems-deep.md) | | 88 | [Observability & SRE](88-software-observability-and-sre.md) |
| 81 | [GPU & Parallel Computing](81-software-gpu-and-parallel-computing.md) | | 89 | [Cloud & Kubernetes](89-software-cloud-and-kubernetes.md) |
| 82 | [Real-Time Operating Systems](82-software-real-time-operating-systems.md) | | 90 | [Systems Programming in Rust](90-software-systems-programming-rust.md) |
| 83 | [Networking & Protocols](83-software-networking-and-protocols.md) | | 91 | [Compilers & Languages](91-software-compilers-and-languages.md) |
| 84 | [Databases & Data Engineering](84-software-databases-and-data-engineering.md) | | 92 | [Performance Engineering](92-software-performance-engineering.md) |
| 85 | [MLOps & ML Infrastructure](85-software-mlops-and-ml-infrastructure.md) | | 93 | [API & System Design](93-software-api-and-system-design.md) |
| 86 | [Cybersecurity Engineering](86-software-cybersecurity-engineering.md) | | 94 | [Testing & Verification Deep](94-software-testing-and-verification-deep.md) |
| 87 | [Applied Cryptography](87-software-cryptography-applied.md) | | | |

### Band 95–106: Math, Science & Cross-cutting Foundations

The mathematics and physics under every layer above — optimization, probability,
linear algebra, numerical methods, signal processing, information theory, advanced
control, mechanics, thermo/fluids, electromagnetics, decision/game theory, and
algorithms. Deepens [03-foundations-mathematics.md](03-foundations-mathematics.md).

| # | Module |  | # | Module |
|---|---|---|---|---|
| 95 | [Optimization](95-foundations-optimization.md) | | 101 | [Advanced Control](101-foundations-control-advanced.md) |
| 96 | [Probability & Stochastic](96-foundations-probability-and-stochastic.md) | | 102 | [Physics for Engineers](102-foundations-physics-for-engineers.md) |
| 97 | [Applied Linear Algebra](97-foundations-linear-algebra-applied.md) | | 103 | [Thermodynamics & Fluids](103-foundations-thermodynamics-and-fluids.md) |
| 98 | [Numerical Methods](98-foundations-numerical-methods.md) | | 104 | [Electromagnetics](104-foundations-electromagnetics.md) |
| 99 | [Signal Processing](99-foundations-signal-processing.md) | | 105 | [Decision & Game Theory](105-foundations-decision-and-game-theory.md) |
| 100 | [Information Theory](100-foundations-information-theory.md) | | 106 | [Algorithms & Complexity](106-foundations-complexity-and-algorithms.md) |

### Band 107–114: Hardware, AI Compute, Power & the Human Layer

A mixed applied band: the silicon-and-power reality under all software, how AI data
centers and distributed-compute startups actually work (and fail), and the human
dimension — manipulation defense, organizational politics, company design, and the
life lessons that compound. Connects the hardware bands (65–79), the company bands
(37–49), and the information-environment band (31–36).

| # | Module | What it makes you |
|---|---|---|
| 107 | [Raspberry Pi Deep Dive](107-hardware-raspberry-pi-deep-dive.md) | Understand a real edge computer from SoC to fielded product |
| 108 | [Building AI Data Centers](108-compute-building-ai-data-centers.md) | Reason about power, cooling, networking, and the speed-to-power gap |
| 109 | [Distributed Data Centers & Startup Ideas](109-compute-distributed-data-centers-and-startup-ideas.md) | Critique the SPAN XFRA model and find better AI-compute bets |
| 110 | [Hardware Foundations](110-hardware-foundations-no-software-without-hardware.md) | See why there is no software without hardware |
| 111 | [Psychological Manipulation Defense](111-influence-psychological-manipulation-defense.md) | Recognize and defend against manipulation (never wield it) |
| 112 | [Big Tech Politics](112-bigtech-politics-navigation.md) | Navigate organizational power with integrity and effectiveness |
| 113 | [Big Tech Flaws & the Optimal Company](113-bigtech-flaws-and-the-optimal-company.md) | Diagnose structural flaws and design a better company |
| 114 | [Life Lessons People Ignore](114-life-lessons-people-ignore.md) | Internalize the compounding truths most people never live |

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

### Path E — "I want information-environment & contested-domain literacy"
`31 → 32 → 33 → 34 → 35 → 36`
Rationale: understand the information environment as a system, then platform
mechanics, then the cognition they act on, then influence operations and their
defense, then lawful OSINT verification, and finally OPSEC and resilience. This is
the defense-oriented, *understanding-and-defense* path — pair it with `07` (mission
context) and `16` (security baseline). It makes you fluent in the sensing, trust, and
information dimensions of modern defense problems, not just the hardware/software ones.

### Path F — "I want elite autonomy depth" (research-grade stack)
`50 → 51 → 52 → 53 → 54 → 55 → 56 → 59 → 61 → 62 → 64`
Rationale: build perception, then the estimation/SLAM spine, then planning and
learning, then the vision/VIO/deployment skills that put it on real hardware. Pair
with the math band (`95–100`) exactly when an equation stops making sense.

### Path G — "I want full-stack hardware fluency"
`65 → 74 → 73 → 68 → 78 → 71 → 72 → 70 → 69 → 76 → 77`
Rationale: firmware and sensors first, then actuation and power, then board/structure/
thermal/aero, then propulsion, finishing with systems engineering and reliability —
the order in which a real vehicle is actually built and certified.

### Path H — "I want to beat the giants"
`37 → 47 → 49 → 48`, plus the company deep-dives (`38–46`) for the ones you compete
with. Pair with [08-foundations-company-strategy-moat.md](08-foundations-company-strategy-moat.md)
and [02-ten-year-mastery-plan.md](02-ten-year-mastery-plan.md). This is the strategy
path: see the patterns, learn the asymmetric playbook, then install the skills and
mechanisms in whatever you build.

### Path I — "I want production-software depth"
`80 → 83 → 82 → 81 → 92 → 90 → 88 → 89 → 86 → 94`
Rationale: distributed systems and networking first, then real-time and GPU compute,
then performance and Rust, then operations, security, and disciplined testing.

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
