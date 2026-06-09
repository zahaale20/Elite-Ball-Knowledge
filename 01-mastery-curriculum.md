# The Mastery Curriculum — Everything the Top People at Elite Defense-Tech Companies Know

> **Why this exists.** The people who run autonomy, GNC, and product at the leading
> defense-technology companies, and the elite groups inside the primes
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
| 01 | [First Principles & Systems Engineering](foundations/01-first_principles_systems_engineering.md) | Decompose any system, reason about tradeoffs like a chief engineer | ✅ written |
| 02 | [Modern C++ & Real-Time Embedded](foundations/04-modern-cpp-realtime.md) | Write/read the flight-software language these companies live in | ✅ written |
| 03 | [Guidance, Navigation & Control (GNC)](autonomy/28-gnc.md) | Make a vehicle know where it is and go where it's told | ✅ written |
| 04 | [Autonomy: Planning & Decision-Making](autonomy/29-planning-decision.md) | Turn "state of the world" into correct action | ✅ written |
| 05 | [Distributed Systems, Comms & Mesh](foundations/05-distributed_systems_comms_mesh.md) | Make many vehicles + operators act as one system (the "Lattice" problem) | ✅ written |
| 06 | [Simulation, Test & Verification](foundations/06-simulation-test-verification.md) | *Prove* a system works before it flies — the real moat | ✅ written |
| 07 | [Defense Domain & Acquisition](foundations/07-defense-acquisition.md) | Speak the customer's language: missions, the kill chain, how DoD buys | ✅ written |
| 08 | [Company Strategy & The Moat](foundations/08-company-strategy-moat.md) | See *why* these companies win and where you create value | ✅ written |
| M | [Mathematics for Autonomy](foundations/03-mathematics.md) | The linear algebra, probability, calculus & Lie theory under every layer | ✅ written |
| S | [Safety Engineering & Assurance](foundations/09-safety-assurance.md) | Argue and prove "this is safe to fly" | ✅ written |

### Already-written companions (read alongside)
- **ML / AI for autonomy** → [20-autonomy-ml-ai.md](autonomy/20-ml-ai.md)
  is the deep perception + learning module. Module 04 here links into it rather
  than repeating it.
- **GNC & estimation** → [28-autonomy-gnc.md](autonomy/28-gnc.md) (the written
  Module 03). **Planning & decision-making** →
  [29-autonomy-planning-decision.md](autonomy/29-planning-decision.md) (Module 04).
- **Control theory** → [25-autonomy-control-theory.md](autonomy/25-control-theory.md).
- **Career execution** → [11-career-defense-aerospace-playbook.md](career/11-defense-aerospace-playbook.md)
  and the other `career-*` guides cover resume
  ([18](career/18-resume-portfolio.md)), interview
  ([17](career/17-interview-prep.md)), clearance
  ([16](career/16-security-clearance.md)), negotiation
  ([15](career/15-negotiation-compensation.md)), and growth
  ([19](career/19-leadership-growth.md)). Modules 07–08 give you the *substance*
  those guides help you present.

---

## The full repository map (all 100+ guides)

The guides are numbered in bands: **01–09 foundations**, **10–19 career**,
**20–29 autonomy**, **30 tooling**, **31–36 information environment**,
**37–49 companies & beating the giants**, **50–64 deep autonomy & robotics**,
**65–79 engineering across domains**, **80–94 software, compute & infrastructure**,
and **95–106 math, science & cross-cutting foundations**, and
**107–114 hardware, AI compute, power & the human layer**, and
**115–124 career mastery & the meta-skills that move careers**. The first row table below
lists the original `01–36` spine; the expansion bands `37–124` are detailed in the
sections that follow it.

| # | File | Band |
|---|---|---|
| 01 | [01-mastery-curriculum.md](01-mastery-curriculum.md) · [01_first_principles_systems_engineering.md](foundations/01-first_principles_systems_engineering.md) | Foundations |
| 02 | [02-ten-year-mastery-plan.md](foundations/02-ten-year-mastery-plan.md) | Foundations |
| 03 | [03-foundations-mathematics.md](foundations/03-mathematics.md) | Foundations |
| 04 | [04-foundations-modern-cpp-realtime.md](foundations/04-modern-cpp-realtime.md) | Foundations |
| 05 | [05_distributed_systems_comms_mesh.md](foundations/05-distributed_systems_comms_mesh.md) | Foundations |
| 06 | [06-foundations-simulation-test-verification.md](foundations/06-simulation-test-verification.md) | Foundations |
| 07 | [07-foundations-defense-acquisition.md](foundations/07-defense-acquisition.md) | Foundations |
| 08 | [08-foundations-company-strategy-moat.md](foundations/08-company-strategy-moat.md) | Foundations |
| 09 | [09-foundations-safety-assurance.md](foundations/09-safety-assurance.md) | Foundations |
| 10 | [10-career-aerospace-engineering.md](career/10-aerospace-engineering.md) | Career |
| 11 | [11-career-defense-aerospace-playbook.md](career/11-defense-aerospace-playbook.md) | Career |
| 12 | [12-career-software-engineering.md](career/12-software-engineering.md) | Career |
| 13 | [13-career-mechanical-engineering.md](career/13-mechanical-engineering.md) | Career |
| 14 | [14-career-dod-politics.md](career/14-dod-politics.md) | Career |
| 15 | [15-career-negotiation-compensation.md](career/15-negotiation-compensation.md) | Career |
| 16 | [16-career-security-clearance.md](career/16-security-clearance.md) | Career |
| 17 | [17-career-interview-prep.md](career/17-interview-prep.md) | Career |
| 18 | [18-career-resume-portfolio.md](career/18-resume-portfolio.md) | Career |
| 19 | [19-career-leadership-growth.md](career/19-leadership-growth.md) | Career |
| 20 | [20-autonomy-ml-ai.md](autonomy/20-ml-ai.md) | Autonomy |
| 21 | [21-autonomy-vtol-roadmap.md](autonomy/21-vtol-roadmap.md) | Autonomy |
| 22 | [22-autonomy-px4-sitl.md](autonomy/22-px4-sitl.md) | Autonomy |
| 23 | [23-autonomy-onboard-system.md](autonomy/23-onboard-system.md) | Autonomy |
| 24 | [24-autonomy-test-scaffold.md](autonomy/24-test-scaffold.md) | Autonomy |
| 25 | [25-autonomy-control-theory.md](autonomy/25-control-theory.md) | Autonomy |
| 26 | [26-autonomy-gnss-jamming-spoofing.md](autonomy/26-gnss-jamming-spoofing.md) | Autonomy |
| 27 | [27-autonomy-counter-uas-ew.md](autonomy/27-counter-uas-ew.md) | Autonomy |
| 28 | [28-autonomy-gnc.md](autonomy/28-gnc.md) | Autonomy |
| 29 | [29-autonomy-planning-decision.md](autonomy/29-planning-decision.md) | Autonomy |
| 30 | [30-ai-power-prompts.md](tooling/30-ai-power-prompts.md) | Tooling |
| 31 | [31-information-environment-systems.md](information-environment/31-information-environment-systems.md) | Info Environment |
| 32 | [32-social-media-platform-mechanics.md](information-environment/32-social-media-platform-mechanics.md) | Info Environment |
| 33 | [33-cognitive-bias-attention-and-narratives.md](information-environment/33-cognitive-bias-attention-and-narratives.md) | Info Environment |
| 34 | [34-information-operations-history-defense.md](information-environment/34-information-operations-history-defense.md) | Info Environment |
| 35 | [35-osint-verification-and-sensemaking.md](information-environment/35-osint-verification-and-sensemaking.md) | Info Environment |
| 36 | [36-trust-safety-opsec-and-digital-resilience.md](information-environment/36-trust-safety-opsec-and-digital-resilience.md) | Info Environment |

### Band 31–36: Information Environment & Influence Systems

A professional, **defense-oriented** band on how the modern information environment
actually works — platforms, audiences, cognition, influence operations, open-source
verification, and operational security. It exists because modern defense and autonomy
problems are not only hardware and software problems; they are sensing, networking,
decision, **trust, and information** problems. Everything here is framed for
**understanding, analysis, and defense — never manipulation.**

| # | Module | What it makes you |
|---|---|---|
| 31 | [Information Environment Systems](information-environment/31-information-environment-systems.md) | Understand how platforms, audiences, and incentives shape modern perception and conflict |
| 32 | [Social Media Platform Mechanics](information-environment/32-social-media-platform-mechanics.md) | Explain how feeds, recommendations, and engagement markets actually work (incl. how a company like Meta thinks) |
| 33 | [Cognition, Attention & Narratives](information-environment/33-cognitive-bias-attention-and-narratives.md) | Reason about human belief formation, bias, and analytic failure modes — and communicate clearly under uncertainty |
| 34 | [Information Operations: History & Defense](information-environment/34-information-operations-history-defense.md) | Recognize influence patterns and build resilience and detection (not conduct them) |
| 35 | [OSINT, Verification & Sensemaking](information-environment/35-osint-verification-and-sensemaking.md) | Turn noisy public information into disciplined, calibrated judgment — lawfully and ethically |
| 36 | [Trust, Safety, OPSEC & Digital Resilience](information-environment/36-trust-safety-opsec-and-digital-resilience.md) | Protect people, teams, and operations in contested information spaces |

These connect back to [05_distributed_systems_comms_mesh.md](foundations/05-distributed_systems_comms_mesh.md)
(message propagation), [07-foundations-defense-acquisition.md](foundations/07-defense-acquisition.md)
(mission/stakeholder context), [29-autonomy-planning-decision.md](autonomy/29-planning-decision.md)
(decision-making under uncertainty), and
[16-career-security-clearance.md](career/16-security-clearance.md) (security baseline).

---

## Bands 37–124: The Deep Expansion

The original `01–36` guides give you the spine. The expansion bands below give you
**elite, first-principles depth across every domain an autonomy/defense engineer
touches** — plus the strategic literacy to out-compete the giants. Each module is a
self-contained, extreme-depth course in the same house style.

### Band 37–49: Companies & Beating the Giants

What the biggest companies actually do that makes them win — and the specific,
transferable skills an ordinary person or small team needs to beat them. This is the
strategic companion to [08-foundations-company-strategy-moat.md](foundations/08-company-strategy-moat.md).

| # | Module | What it makes you |
|---|---|---|
| 37 | [How the Giants Win](companies/37-how-the-giants-win.md) | See the recurring winning patterns across SpaceX, Palantir, Apple, Amazon, Nvidia, Tesla, Google |
| 38 | [SpaceX — Rapid Iteration](companies/38-spacex-rapid-iteration.md) | Operate a fly-test-break-fix, design-to-cost flywheel |
| 39 | [Productized Defense](companies/39-productized-defense.md) | Understand counter-positioning and software-defined hardware |
| 40 | [Palantir — Forward-Deployed](companies/40-palantir-forward-deployed.md) | Own the data ontology and deploy into hard accounts |
| 41 | [Tesla — Vertical Integration & Data](companies/41-tesla-vertical-integration-data.md) | Build a fleet data flywheel and manufacturing moat |
| 42 | [Nvidia — Platform & Ecosystem](companies/42-nvidia-platform-ecosystem.md) | Build ecosystem lock-in and ride compute waves |
| 43 | [Apple — Integration & Taste](companies/43-apple-integration-taste.md) | Integrate end-to-end and say no with taste |
| 44 | [Amazon — Mechanisms & Customer Obsession](companies/44-amazon-mechanisms-customer-obsession.md) | Install working-backwards and narrative operating mechanisms |
| 45 | [Google — Scale & Infrastructure](companies/45-google-scale-infra.md) | Get leverage from infrastructure and 10x thinking |
| 46 | [Skunk Works — Small Elite Teams](companies/46-skunkworks-rapid-prototyping.md) | Run tiny, empowered, prototype-first teams |
| 47 | [The Asymmetric Playbook](companies/47-startup-asymmetric-playbook.md) | Beat incumbents with speed, focus, and counter-positioning |
| 48 | [Operating Mechanisms & Culture](companies/48-operating-mechanisms-and-culture.md) | Build the invisible machinery that compounds |
| 49 | [The Skills to Beat Them](companies/49-skills-to-beat-them.md) | A personal operating system of the transferable skills |

#### Band 37–49 extension: the highest-impact companies the band was missing

These seven modules close the biggest gaps in the original band — the incumbents
it never dissected (the primes), the platform/AI giants reshaping every market, the
supply chain everything depends on, the live defense-tech cohort you'll actually
join, and the culture system underneath it all. They continue the band's house style
and cross-link back into it. (Numbered 116–122 only because the 37–49 slots were full.)

| # | Module | What it makes you |
|---|---|---|
| 116 | [The Defense Primes — How Incumbents Win](companies/116-defense-primes-how-incumbents-win.md) | Read Lockheed/Northrop/RTX/GD/Boeing as a system of real moats — the counterweight to the new defense-tech entrants |
| 117 | [Microsoft — Reinvention & Platform](companies/117-microsoft-reinvention-platform.md) | Escape your own moat; wield distribution, partnership, and culture-as-strategy |
| 118 | [Frontier AI Labs — OpenAI/Anthropic/DeepMind](companies/118-frontier-ai-labs.md) | Reason about scaling laws, compute moats, and research-to-product |
| 119 | [Meta — Open Source as Strategy](companies/119-meta-open-source-as-strategy.md) | Commoditize your complement; decide open vs. closed rigorously |
| 120 | [Semiconductor Titans — TSMC & ASML](companies/120-semiconductor-titans-tsmc-asml.md) | See the physical substrate of all compute and its geopolitics |
| 121 | [The New Defense-Tech Cohort](companies/121-new-defense-tech-cohort.md) | Map the live wave (Shield AI, Skydio, Saronic, Applied Intuition…) you'll join or fight |
| 122 | [Netflix — Talent Density & Culture](companies/122-netflix-talent-density-culture.md) | Build a high-density, high-candor, context-led team that beats institutions |

### Band 50–64: Deep Autonomy & Robotics

The full autonomy stack at research depth — perception, SLAM, estimation, planning,
learning, swarms, and deployment. Extends [20-autonomy-ml-ai.md](autonomy/20-ml-ai.md),
[28-autonomy-gnc.md](autonomy/28-gnc.md), and [29-autonomy-planning-decision.md](autonomy/29-planning-decision.md).

| # | Module |  | # | Module |
|---|---|---|---|---|
| 50 | [Perception Deep Dive](autonomy/50-perception-deep.md) | | 58 | [Multi-Agent & Swarm](autonomy/58-multi-agent-swarm.md) |
| 51 | [SLAM & Mapping](autonomy/51-slam-and-mapping.md) | | 59 | [Computer Vision](autonomy/59-computer-vision.md) |
| 52 | [Sensor Fusion](autonomy/52-sensor-fusion.md) | | 60 | [LiDAR & Radar](autonomy/60-lidar-radar-processing.md) |
| 53 | [Advanced State Estimation](autonomy/53-state-estimation-advanced.md) | | 61 | [Visual-Inertial Odometry](autonomy/61-visual-inertial-odometry.md) |
| 54 | [Motion Planning](autonomy/54-motion-planning.md) | | 62 | [Sim-to-Real](autonomy/62-sim-to-real.md) |
| 55 | [Trajectory Optimization](autonomy/55-trajectory-optimization.md) | | 63 | [Foundation Models for Robotics](autonomy/63-foundation-models-robotics.md) |
| 56 | [Reinforcement Learning](autonomy/56-reinforcement-learning.md) | | 64 | [Edge Inference & Deployment](autonomy/64-edge-inference-deployment.md) |
| 57 | [Imitation Learning](autonomy/57-imitation-and-learning-from-demo.md) | | | |

### Band 65–79: Engineering Across Domains

The hardware and physical-engineering breadth that makes you fluent across the whole
vehicle — firmware, FPGAs, RF, power, propulsion, aero, structures, thermal,
mechatronics, sensors, manufacturing, systems engineering, reliability, PCB, and
batteries.

| # | Module |  | # | Module |
|---|---|---|---|---|
| 65 | [Embedded Firmware](engineering/65-embedded-firmware.md) | | 73 | [Mechatronics & Actuation](engineering/73-mechatronics-and-actuation.md) |
| 66 | [FPGAs & HW Acceleration](engineering/66-fpga-and-hardware-accel.md) | | 74 | [Sensors & Instrumentation](engineering/74-sensors-and-instrumentation.md) |
| 67 | [RF & Comms Systems](engineering/67-rf-and-comms-systems.md) | | 75 | [Manufacturing & DFM](engineering/75-manufacturing-and-dfm.md) |
| 68 | [Power Electronics](engineering/68-power-electronics.md) | | 76 | [Systems Engineering & MBSE](engineering/76-systems-engineering-mbse.md) |
| 69 | [Propulsion](engineering/69-propulsion-and-electric-propulsion.md) | | 77 | [Reliability & Failure Analysis](engineering/77-reliability-and-failure-analysis.md) |
| 70 | [Aerodynamics & Flight Mechanics](engineering/70-aerodynamics-and-flight-mechanics.md) | | 78 | [PCB & Electronics Design](engineering/78-pcb-and-electronics-design.md) |
| 71 | [Structures & Materials](engineering/71-structures-and-materials.md) | | 79 | [Batteries & Energy Storage](engineering/79-batteries-and-energy-storage.md) |
| 72 | [Thermal Management](engineering/72-thermal-management.md) | | | |

### Band 80–94: Software, Compute & Infrastructure

The production-software depth behind any fielded autonomy system — distributed
systems, GPUs, RTOS, networking, data, MLOps, security, crypto, observability,
cloud, Rust, compilers, performance, system design, and testing.

| # | Module |  | # | Module |
|---|---|---|---|---|
| 80 | [Distributed Systems Deep](software/80-distributed-systems-deep.md) | | 88 | [Observability & SRE](software/88-observability-and-sre.md) |
| 81 | [GPU & Parallel Computing](software/81-gpu-and-parallel-computing.md) | | 89 | [Cloud & Kubernetes](software/89-cloud-and-kubernetes.md) |
| 82 | [Real-Time Operating Systems](software/82-real-time-operating-systems.md) | | 90 | [Systems Programming in Rust](software/90-systems-programming-rust.md) |
| 83 | [Networking & Protocols](software/83-networking-and-protocols.md) | | 91 | [Compilers & Languages](software/91-compilers-and-languages.md) |
| 84 | [Databases & Data Engineering](software/84-databases-and-data-engineering.md) | | 92 | [Performance Engineering](software/92-performance-engineering.md) |
| 85 | [MLOps & ML Infrastructure](software/85-mlops-and-ml-infrastructure.md) | | 93 | [API & System Design](software/93-api-and-system-design.md) |
| 86 | [Cybersecurity Engineering](software/86-cybersecurity-engineering.md) | | 94 | [Testing & Verification Deep](software/94-testing-and-verification-deep.md) |
| 87 | [Applied Cryptography](software/87-cryptography-applied.md) | | | |

### Band 95–106: Math, Science & Cross-cutting Foundations

The mathematics and physics under every layer above — optimization, probability,
linear algebra, numerical methods, signal processing, information theory, advanced
control, mechanics, thermo/fluids, electromagnetics, decision/game theory, and
algorithms. Deepens [03-foundations-mathematics.md](foundations/03-mathematics.md).

| # | Module |  | # | Module |
|---|---|---|---|---|
| 95 | [Optimization](mathematics/95-optimization.md) | | 101 | [Advanced Control](mathematics/101-control-advanced.md) |
| 96 | [Probability & Stochastic](mathematics/96-probability-and-stochastic.md) | | 102 | [Physics for Engineers](mathematics/102-physics-for-engineers.md) |
| 97 | [Applied Linear Algebra](mathematics/97-linear-algebra-applied.md) | | 103 | [Thermodynamics & Fluids](mathematics/103-thermodynamics-and-fluids.md) |
| 98 | [Numerical Methods](mathematics/98-numerical-methods.md) | | 104 | [Electromagnetics](mathematics/104-electromagnetics.md) |
| 99 | [Signal Processing](mathematics/99-signal-processing.md) | | 105 | [Decision & Game Theory](mathematics/105-decision-and-game-theory.md) |
| 100 | [Information Theory](mathematics/100-information-theory.md) | | 106 | [Algorithms & Complexity](mathematics/106-complexity-and-algorithms.md) |

### Band 107–114: Hardware, AI Compute, Power & the Human Layer

A mixed applied band: the silicon-and-power reality under all software, how AI data
centers and distributed-compute startups actually work (and fail), and the human
dimension — manipulation defense, organizational politics, company design, the life
lessons that compound, and the inner operating system beneath them all: emotional
self-governance, how societies rise and fall, status and tribe, relationships, the
psychology of money, resilience, power, and meaning. Connects the hardware bands
(65–79), the company bands (37–49), and the information-environment band (31–36).

| # | Module | What it makes you |
|---|---|---|
| 107 | [Raspberry Pi Deep Dive](compute-and-hardware/107-raspberry-pi-deep-dive.md) | Understand a real edge computer from SoC to fielded product |
| 108 | [Building AI Data Centers](compute-and-hardware/108-building-ai-data-centers.md) | Reason about power, cooling, networking, and the speed-to-power gap |
| 109 | [Distributed Data Centers & Startup Ideas](compute-and-hardware/109-distributed-data-centers-and-startup-ideas.md) | Critique the SPAN XFRA model and find better AI-compute bets |
| 110 | [Hardware Foundations](compute-and-hardware/110-foundations-no-software-without-hardware.md) | See why there is no software without hardware |
| 111 | [Psychological Manipulation Defense](mindset-and-society/111-psychological-manipulation-defense.md) | Recognize and defend against manipulation (never wield it) |
| 112 | [Big Tech Politics](mindset-and-society/112-politics-navigation.md) | Navigate organizational power with integrity and effectiveness |
| 113 | [Big Tech Flaws & the Optimal Company](mindset-and-society/113-flaws-and-the-optimal-company.md) | Diagnose structural flaws and design a better company |
| 114 | [Life Lessons People Ignore](mindset-and-society/114-life-lessons-people-ignore.md) | Internalize the compounding truths most people never live |

### Band 115–124: Career Mastery — The Meta-Skills That Move Careers

The original career band (`10–19`) covers the domains and the job-hunt mechanics
(resume, interview, clearance, negotiation). This band covers the **highest-leverage
career skills nobody writes down** — the relationship capital, communication,
reputation, money, execution, entrepreneurship, adaptability, sustainability, and
ethics that actually decide how far an engineer goes. It is the personal-operating-system
companion to the [companies band](companies/37-how-the-giants-win.md) and
[19-career-leadership-growth.md](career/19-leadership-growth.md).

| # | Module | What it makes you |
|---|---|---|
| 115 | [Networking, Mentors & Sponsors](career/115-networking-mentors-sponsors.md) | Build the relationship capital that gets you chosen, not just considered |
| 116 | [Technical Communication](career/116-technical-communication.md) | Make people understand, trust, and act on your work — the mid-career multiplier |
| 117 | [Personal Brand & Public Presence](career/117-personal-brand-public-presence.md) | Manufacture luck with a public body of work that draws opportunity inbound |
| 118 | [Job Search & Career Capital](career/118-job-search-career-capital.md) | Run your career as a portfolio of compounding capital, not a series of panics |
| 119 | [Financial Literacy & Wealth](career/119-financial-literacy-wealth.md) | Turn a high income into real wealth, freedom, and equity you don't fumble |
| 120 | [Productivity & Deep Work](career/120-productivity-deep-work.md) | Convert capability into shipped output sustainably, as an engineered system |
| 121 | [Engineer to Founder](career/121-engineer-to-founder.md) | Cross from building someone's product to building your own — with managed risk |
| 122 | [Career Pivots & the AI Era](career/122-career-pivots-ai-era.md) | Reinvent faster than the field changes; use AI as leverage, not threat |
| 123 | [Health, Energy & Career Longevity](career/123-health-energy-career-longevity.md) | Stay excellent for decades; treat burnout as a system failure to prevent |
| 124 | [Ethics, Export Control & Responsibility](career/124-ethics-export-control.md) | Stay far from the one mistake no technical brilliance can recover from (ITAR/EAR, classification, safety) |

These connect back to the job-hunt mechanics in `15–19`, the strategy in the
[companies band](companies/37-how-the-giants-win.md), the clearance baseline in
[16-career-security-clearance.md](career/16-security-clearance.md), and the
information-environment band (`31–36`).

---

### Band: General Knowledge (`general/`)

A broad, accessible band for the questions almost everyone is curious about —
money, the internet, AI, health, learning, and how the world around you works.
These are written for a general reader (lighter on jargon) while staying
first-principles and honest. They live in the `general/` folder; the numbering is
folder-scoped, so it intentionally overlaps the career band above.

| # | Module |  | # | Module |
|---|---|---|---|---|
| 115 | [How Money & Inflation Work](general/115-how-money-and-inflation-work.md) | | 122 | [Health Foundations](general/122-health-foundations-sleep-food-movement.md) |
| 116 | [Personal Finance & Investing](general/116-personal-finance-and-investing.md) | | 123 | [The Electric Grid & Energy](general/123-how-the-electric-grid-and-energy-work.md) |
| 117 | [How the Internet Works](general/117-how-the-internet-works.md) | | 124 | [Negotiation & Everyday Persuasion](general/124-negotiation-and-everyday-persuasion.md) |
| 118 | [How AI & LLMs Actually Work](general/118-how-ai-and-llms-actually-work.md) | | 125 | [Productivity, Focus & Time](general/125-productivity-focus-and-time-management.md) |
| 119 | [The Science of Learning](general/119-the-science-of-learning.md) | | 126 | [Statistics for Everyday Decisions](general/126-statistics-for-everyday-decisions.md) |
| 120 | [Critical Thinking & Fallacies](general/120-critical-thinking-and-logical-fallacies.md) | | 127 | [How GPS Finds You](general/127-how-gps-and-your-phone-find-you.md) |
| 121 | [How the Economy Works](general/121-how-the-economy-works.md) | | 128 | [Understanding Taxes](general/128-understanding-taxes.md) |

---

### Band 115–125: The Human Operating System (Inner Mastery)

The technical bands above make you a world-class *engineer*. This band makes you a
world-class *operator of yourself* — the internal stack that sits **underneath**
every other module and decides whether all that knowledge ever becomes action. It
extends the human-layer modules (`111–114`) with the inner operating system:
emotional self-governance, resilience, the habit engine that converts knowing into
doing, the judgment that makes every decision better, the trained attention that
gates focus and learning, the creativity that produces asymmetric bets, and the
knowledge system that keeps it all compounding. These are the highest-leverage
subjects in the entire curriculum precisely because they **multiply the value of
everything else**.

| # | Module | What it makes you |
|---|---|---|
| 115 | [Stoicism & Emotional Self-Governance](mindset-and-society/115-stoicism-emotional-self-governance.md) | Govern your own mind under pressure — the inner OS beneath all the rest |
| 120 | [Resilience, Failure & Antifragility](mindset-and-society/120-resilience-failure-antifragility.md) | Recover from, and grow through, hard things; design a life that gains from stress |
| 121 | [Habits, Behavior Change & Self-Discipline](mindset-and-society/121-habits-behavior-change-and-discipline.md) | The engine that converts knowing into doing — the highest-impact module in the band |
| 122 | [Rationality, Mental Models & Judgment](mindset-and-society/122-rationality-mental-models-and-judgment.md) | Think well when it counts; raise the quality of every decision you make |
| 123 | [Meditation, Mindfulness & Flow](mindset-and-society/123-meditation-mindfulness-and-flow.md) | Train attention — the master resource under focus, learning, and regulation |
| 124 | [Creativity & Idea Generation](mindset-and-society/124-creativity-and-idea-generation.md) | Manufacture the non-obvious, asymmetric bet on demand |
| 125 | [Knowledge Management & the Second Brain](mindset-and-society/125-knowledge-management-and-second-brain.md) | Capture, connect, and retrieve everything you learn so it compounds *(stub)* |

These connect to the science of learning ([foundations/115](foundations/115-learning-how-to-learn.md)),
deep work ([career/120](career/120-productivity-deep-work.md)), the health substrate
([general/122](general/122-health-foundations-sleep-food-movement.md)), the formal
decision math ([mathematics/105](mathematics/105-decision-and-game-theory.md)), and
the cognition module in the information-environment band
([33](information-environment/33-cognitive-bias-attention-and-narratives.md)).

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
with. Pair with [08-foundations-company-strategy-moat.md](foundations/08-company-strategy-moat.md)
and [02-ten-year-mastery-plan.md](foundations/02-ten-year-mastery-plan.md). This is the strategy
path: see the patterns, learn the asymmetric playbook, then install the skills and
mechanisms in whatever you build.

### Path I — "I want production-software depth"
`80 → 83 → 82 → 81 → 92 → 90 → 88 → 89 → 86 → 94`
Rationale: distributed systems and networking first, then real-time and GPU compute,
then performance and Rust, then operations, security, and disciplined testing.

### Path J — "I want to compound my career, not just survive it"
`118 → 116 → 115 → 117 → 120 → 119 → 123`, plus `124` early and always.
Rationale: first see your career as compounding capital, then build the
communication and relationship capital that move it, then the public presence that
makes opportunity inbound, then the execution and money systems that turn it into
freedom — all riding on the health that sustains a multi-decade career, and fenced by
the ethics/export-control discipline that protects all of it. Add `121` if founding
is on the table and `122` to stay relevant as the field shifts. Pair with the
job-hunt mechanics in `15–19` and the strategy in the company band (`37–49`).

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
- [20-autonomy-ml-ai.md](autonomy/20-ml-ai.md) — perception & learning.
- [28-autonomy-gnc.md](autonomy/28-gnc.md) — guidance, navigation & control.
- [29-autonomy-planning-decision.md](autonomy/29-planning-decision.md) — planning & decision-making.
- [25-autonomy-control-theory.md](autonomy/25-control-theory.md) — control deep dive.

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
