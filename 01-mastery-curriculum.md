# The Mastery Curriculum — Everything the Top People at Elite Defense-Tech Companies Know

> **How this library was made — read this first.** This repository is a compilation of
> real questions people have asked me, answered with the help of **AI tools** and
> **AI tools**. It is **AI-assisted synthesis that I curate and review** — not
> original primary research, and not a substitute for authoritative sources. Treat every
> guide as a strong, structured *starting point*: learn the shape of a topic here, then
> verify anything load-bearing against primary sources before you rely on it, cite it, or
> build on it. Holding that line is the whole point — it keeps all of us honest.

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
| 03 | [Guidance, Navigation & Control (GNC)](autonomy/09-gnc.md) | Make a vehicle know where it is and go where it's told | ✅ written |
| 04 | [Autonomy: Planning & Decision-Making](autonomy/10-planning-decision.md) | Turn "state of the world" into correct action | ✅ written |
| 05 | [Distributed Systems, Comms & Mesh](foundations/05-distributed_systems_comms_mesh.md) | Make many vehicles + operators act as one system (the "Lattice" problem) | ✅ written |
| 06 | [Simulation, Test & Verification](foundations/06-simulation-test-verification.md) | *Prove* a system works before it flies — the real moat | ✅ written |
| 07 | [Defense Domain & Acquisition](foundations/07-defense-acquisition.md) | Speak the customer's language: missions, the kill chain, how DoD buys | ✅ written |
| 08 | [Company Strategy & The Moat](foundations/08-company-strategy-moat.md) | See *why* these companies win and where you create value | ✅ written |
| M | [Mathematics for Autonomy](foundations/03-mathematics.md) | The linear algebra, probability, calculus & Lie theory under every layer | ✅ written |
| S | [Safety Engineering & Assurance](foundations/09-safety-assurance.md) | Argue and prove "this is safe to fly" | ✅ written |

### Already-written companions (read alongside)
- **ML / AI for autonomy** → [01-autonomy-ml-ai.md](autonomy/01-ml-ai.md)
  is the deep perception + learning module. Module 04 here links into it rather
  than repeating it.
- **GNC & estimation** → [09-autonomy-gnc.md](autonomy/09-gnc.md) (the written
  Module 03). **Planning & decision-making** →
  [10-autonomy-planning-decision.md](autonomy/10-planning-decision.md) (Module 04).
- **Control theory** → [06-autonomy-control-theory.md](autonomy/06-control-theory.md).
- **Career execution** → [02-career-defense-aerospace-playbook.md](career/02-defense-aerospace-playbook.md)
  and the other `career-*` guides cover resume
  ([09](career/09-resume-portfolio.md)), interview
  ([08](career/08-interview-prep.md)), clearance
  ([07](career/07-security-clearance.md)), negotiation
  ([06](career/06-negotiation-compensation.md)), and growth
  ([10](career/10-leadership-growth.md)). Modules 07–08 give you the *substance*
  those guides help you present.

---

## The full repository map (all 100+ guides)

The guides are organized **by folder**, and **each folder is numbered
independently from `01`**. The folders are: **foundations** (`01–21`),
**career** (`01–20`), **autonomy** (`01–29`), **tooling** (`01`),
**information-environment** (`01–06`), **companies** (`01–20`),
**engineering** (`01–16`), **software** (`01–15`), **mathematics** (`01–12`),
**compute-and-hardware** (`01–04`), **mindset-and-society** (`01–17`),
**general** (`01–14`), **space** (`01`), and **products** (`01`). The first table
below lists the original foundations/career/autonomy/tooling/information-environment
spine; the remaining folders — including the **Extended Foundations** (`foundations/10–21`),
**Space**, and **Products** sections — are detailed in the sections that follow it. A
separate **machine learning/** folder holds standalone course materials and is
documented at the end of the repository map, not as part of the curriculum spine.

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
| 01 | [01-career-aerospace-engineering.md](career/01-aerospace-engineering.md) | Career |
| 02 | [02-career-defense-aerospace-playbook.md](career/02-defense-aerospace-playbook.md) | Career |
| 03 | [03-career-software-engineering.md](career/03-software-engineering.md) | Career |
| 04 | [04-career-mechanical-engineering.md](career/04-mechanical-engineering.md) | Career |
| 05 | [05-career-dod-politics.md](career/05-dod-politics.md) | Career |
| 06 | [06-career-negotiation-compensation.md](career/06-negotiation-compensation.md) | Career |
| 07 | [07-career-security-clearance.md](career/07-security-clearance.md) | Career |
| 08 | [08-career-interview-prep.md](career/08-interview-prep.md) | Career |
| 09 | [09-career-resume-portfolio.md](career/09-resume-portfolio.md) | Career |
| 10 | [10-career-leadership-growth.md](career/10-leadership-growth.md) | Career |
| 01 | [01-autonomy-ml-ai.md](autonomy/01-ml-ai.md) | Autonomy |
| 02 | [02-autonomy-vtol-roadmap.md](autonomy/02-vtol-roadmap.md) | Autonomy |
| 03 | [03-autonomy-px4-sitl.md](autonomy/03-px4-sitl.md) | Autonomy |
| 04 | [04-autonomy-onboard-system.md](autonomy/04-onboard-system.md) | Autonomy |
| 05 | [05-autonomy-test-scaffold.md](autonomy/05-test-scaffold.md) | Autonomy |
| 06 | [06-autonomy-control-theory.md](autonomy/06-control-theory.md) | Autonomy |
| 07 | [07-autonomy-gnss-jamming-spoofing.md](autonomy/07-gnss-jamming-spoofing.md) | Autonomy |
| 08 | [08-autonomy-counter-uas-ew.md](autonomy/08-counter-uas-ew.md) | Autonomy |
| 09 | [09-autonomy-gnc.md](autonomy/09-gnc.md) | Autonomy |
| 10 | [10-autonomy-planning-decision.md](autonomy/10-planning-decision.md) | Autonomy |
| 01 | [01-ai-power-prompts.md](tooling/01-ai-power-prompts.md) | Tooling |
| 01 | [01-information-environment-systems.md](information-environment/01-information-environment-systems.md) | Info Environment |
| 02 | [02-social-media-platform-mechanics.md](information-environment/02-social-media-platform-mechanics.md) | Info Environment |
| 03 | [03-cognitive-bias-attention-and-narratives.md](information-environment/03-cognitive-bias-attention-and-narratives.md) | Info Environment |
| 04 | [04-information-operations-history-defense.md](information-environment/04-information-operations-history-defense.md) | Info Environment |
| 05 | [05-osint-verification-and-sensemaking.md](information-environment/05-osint-verification-and-sensemaking.md) | Info Environment |
| 06 | [06-trust-safety-opsec-and-digital-resilience.md](information-environment/06-trust-safety-opsec-and-digital-resilience.md) | Info Environment |

### Information Environment & Influence Systems (`information-environment/01–06`)

A professional, **defense-oriented** band on how the modern information environment
actually works — platforms, audiences, cognition, influence operations, open-source
verification, and operational security. It exists because modern defense and autonomy
problems are not only hardware and software problems; they are sensing, networking,
decision, **trust, and information** problems. Everything here is framed for
**understanding, analysis, and defense — never manipulation.**

| # | Module | What it makes you |
|---|---|---|
| 01 | [Information Environment Systems](information-environment/01-information-environment-systems.md) | Understand how platforms, audiences, and incentives shape modern perception and conflict |
| 02 | [Social Media Platform Mechanics](information-environment/02-social-media-platform-mechanics.md) | Explain how feeds, recommendations, and engagement markets actually work (incl. how a company like Meta thinks) |
| 03 | [Cognition, Attention & Narratives](information-environment/03-cognitive-bias-attention-and-narratives.md) | Reason about human belief formation, bias, and analytic failure modes — and communicate clearly under uncertainty |
| 04 | [Information Operations: History & Defense](information-environment/04-information-operations-history-defense.md) | Recognize influence patterns and build resilience and detection (not conduct them) |
| 05 | [OSINT, Verification & Sensemaking](information-environment/05-osint-verification-and-sensemaking.md) | Turn noisy public information into disciplined, calibrated judgment — lawfully and ethically |
| 06 | [Trust, Safety, OPSEC & Digital Resilience](information-environment/06-trust-safety-opsec-and-digital-resilience.md) | Protect people, teams, and operations in contested information spaces |

These connect back to [05_distributed_systems_comms_mesh.md](foundations/05-distributed_systems_comms_mesh.md)
(message propagation), [07-foundations-defense-acquisition.md](foundations/07-defense-acquisition.md)
(mission/stakeholder context), [10-autonomy-planning-decision.md](autonomy/10-planning-decision.md)
(decision-making under uncertainty), and
[07-career-security-clearance.md](career/07-security-clearance.md) (security baseline).

---

## The Deep Expansion bands

The foundations/career/autonomy/tooling/information-environment folders give you the
spine. The expansion folders below give you
**elite, first-principles depth across every domain an autonomy/defense engineer
touches** — plus the strategic literacy to out-compete the giants. Each module is a
self-contained, extreme-depth course in the same house style.

### Companies & Beating the Giants (`companies/01–20`)

What the biggest companies actually do that makes them win — and the specific,
transferable skills an ordinary person or small team needs to beat them. This is the
strategic companion to [08-foundations-company-strategy-moat.md](foundations/08-company-strategy-moat.md).

| # | Module | What it makes you |
|---|---|---|
| 01 | [How the Giants Win](companies/01-how-the-giants-win.md) | See the recurring winning patterns across SpaceX, Palantir, Apple, Amazon, Nvidia, Tesla, Google |
| 02 | [SpaceX — Rapid Iteration](companies/02-spacex-rapid-iteration.md) | Operate a fly-test-break-fix, design-to-cost flywheel |
| 03 | [Productized Defense](companies/03-productized-defense.md) | Understand counter-positioning and software-defined hardware |
| 04 | [Palantir — Forward-Deployed](companies/04-palantir-forward-deployed.md) | Own the data ontology and deploy into hard accounts |
| 05 | [Tesla — Vertical Integration & Data](companies/05-tesla-vertical-integration-data.md) | Build a fleet data flywheel and manufacturing moat |
| 06 | [Nvidia — Platform & Ecosystem](companies/06-nvidia-platform-ecosystem.md) | Build ecosystem lock-in and ride compute waves |
| 07 | [Apple — Integration & Taste](companies/07-apple-integration-taste.md) | Integrate end-to-end and say no with taste |
| 08 | [Amazon — Mechanisms & Customer Obsession](companies/08-amazon-mechanisms-customer-obsession.md) | Install working-backwards and narrative operating mechanisms |
| 09 | [Google — Scale & Infrastructure](companies/09-google-scale-infra.md) | Get leverage from infrastructure and 10x thinking |
| 10 | [Skunk Works — Small Elite Teams](companies/10-skunkworks-rapid-prototyping.md) | Run tiny, empowered, prototype-first teams |
| 11 | [The Asymmetric Playbook](companies/11-startup-asymmetric-playbook.md) | Beat incumbents with speed, focus, and counter-positioning |
| 12 | [Operating Mechanisms & Culture](companies/12-operating-mechanisms-and-culture.md) | Build the invisible machinery that compounds |
| 13 | [The Skills to Beat Them](companies/13-skills-to-beat-them.md) | A personal operating system of the transferable skills |

#### Companies extension (`companies/14–20`): the highest-impact companies the band was missing

These seven modules close the biggest gaps in the original band — the incumbents
it never dissected (the primes), the platform/AI giants reshaping every market, the
supply chain everything depends on, the live defense-tech cohort you'll actually
join, and the culture system underneath it all. They continue the band's house style
and cross-link back into it.

| # | Module | What it makes you |
|---|---|---|
| 14 | [The Defense Primes — How Incumbents Win](companies/14-defense-primes-how-incumbents-win.md) | Read Lockheed/Northrop/RTX/GD/Boeing as a system of real moats — the counterweight to the new defense-tech entrants |
| 15 | [Microsoft — Reinvention & Platform](companies/15-microsoft-reinvention-platform.md) | Escape your own moat; wield distribution, partnership, and culture-as-strategy |
| 16 | [Frontier AI Labs — OpenAI/Anthropic/DeepMind](companies/16-frontier-ai-labs.md) | Reason about scaling laws, compute moats, and research-to-product |
| 17 | [Meta — Open Source as Strategy](companies/17-meta-open-source-as-strategy.md) | Commoditize your complement; decide open vs. closed rigorously |
| 18 | [Semiconductor Titans — TSMC & ASML](companies/18-semiconductor-titans-tsmc-asml.md) | See the physical substrate of all compute and its geopolitics |
| 19 | [The New Defense-Tech Cohort](companies/19-new-defense-tech-cohort.md) | Map the live wave (Shield AI, Skydio, Saronic, Applied Intuition…) you'll join or fight |
| 20 | [Netflix — Talent Density & Culture](companies/20-netflix-talent-density-culture.md) | Build a high-density, high-candor, context-led team that beats institutions |

### Deep Autonomy & Robotics (`autonomy/11–29`)

The full autonomy stack at research depth — perception, SLAM, estimation, planning,
learning, swarms, and deployment. Extends [01-autonomy-ml-ai.md](autonomy/01-ml-ai.md),
[09-autonomy-gnc.md](autonomy/09-gnc.md), and [10-autonomy-planning-decision.md](autonomy/10-planning-decision.md).

| # | Module |  | # | Module |
|---|---|---|---|---|
| 11 | [Perception Deep Dive](autonomy/11-perception-deep.md) | | 19 | [Multi-Agent & Swarm](autonomy/19-multi-agent-swarm.md) |
| 12 | [SLAM & Mapping](autonomy/12-slam-and-mapping.md) | | 20 | [Computer Vision](autonomy/20-computer-vision.md) |
| 13 | [Sensor Fusion](autonomy/13-sensor-fusion.md) | | 21 | [LiDAR & Radar](autonomy/21-lidar-radar-processing.md) |
| 14 | [Advanced State Estimation](autonomy/14-state-estimation-advanced.md) | | 22 | [Visual-Inertial Odometry](autonomy/22-visual-inertial-odometry.md) |
| 15 | [Motion Planning](autonomy/15-motion-planning.md) | | 23 | [Sim-to-Real](autonomy/23-sim-to-real.md) |
| 16 | [Trajectory Optimization](autonomy/16-trajectory-optimization.md) | | 24 | [Foundation Models for Robotics](autonomy/24-foundation-models-robotics.md) |
| 17 | [Reinforcement Learning](autonomy/17-reinforcement-learning.md) | | 25 | [Edge Inference & Deployment](autonomy/25-edge-inference-deployment.md) |
| 18 | [Imitation Learning](autonomy/18-imitation-and-learning-from-demo.md) | | | |

#### Autonomy extension (`autonomy/26–29`): the domain verticals the band was missing

These four modules take the core stack into the specific operational domains an
autonomy/defense engineer is most likely to be pulled into — the undersea world
where GPS dies and sound rules, the terminal guidance of guided munitions, the
speed-of-light fight of directed energy and the spectrum, and the human operator
who is always part of the loop. They continue the band's house style and cross-link
back into it. Everything is framed for **understanding and defense**, not for
building weapons.

| # | Module | What it makes you |
|---|---|---|
| 26 | [Maritime & Undersea Autonomy](autonomy/26-maritime-and-undersea-autonomy.md) | Design autonomy where sound replaces light — navigating GPS-denied underwater through currents, sonar, and traffic law |
| 27 | [Missiles, Guided Munitions & Hypersonics](autonomy/27-missiles-guided-munitions-hypersonics.md) | Reason about guidance laws and seeker physics at the kill chain's terminal link — to understand, not build |
| 28 | [Directed Energy & Electronic Warfare](autonomy/28-directed-energy-and-electronic-warfare.md) | Reason about systems that survive contested spectrum — lasers, microwaves, and the detect–deny–deceive–destroy fight |
| 29 | [Human-Autonomy Teaming & Human Factors](autonomy/29-human-autonomy-teaming.md) | Design the whole human-plus-machine system — calibrating trust, workload, and autonomy levels to ship deployable autonomy |

### Engineering Across Domains (`engineering/01–16`)

The hardware and physical-engineering breadth that makes you fluent across the whole
vehicle — firmware, FPGAs, RF, power, propulsion, aero, structures, thermal,
mechatronics, sensors, manufacturing, systems engineering, reliability, PCB,
batteries, and quantum technologies.

| # | Module |  | # | Module |
|---|---|---|---|---|
| 01 | [Embedded Firmware](engineering/01-embedded-firmware.md) | | 09 | [Mechatronics & Actuation](engineering/09-mechatronics-and-actuation.md) |
| 02 | [FPGAs & HW Acceleration](engineering/02-fpga-and-hardware-accel.md) | | 10 | [Sensors & Instrumentation](engineering/10-sensors-and-instrumentation.md) |
| 03 | [RF & Comms Systems](engineering/03-rf-and-comms-systems.md) | | 11 | [Manufacturing & DFM](engineering/11-manufacturing-and-dfm.md) |
| 04 | [Power Electronics](engineering/04-power-electronics.md) | | 12 | [Systems Engineering & MBSE](engineering/12-systems-engineering-mbse.md) |
| 05 | [Propulsion](engineering/05-propulsion-and-electric-propulsion.md) | | 13 | [Reliability & Failure Analysis](engineering/13-reliability-and-failure-analysis.md) |
| 06 | [Aerodynamics & Flight Mechanics](engineering/06-aerodynamics-and-flight-mechanics.md) | | 14 | [PCB & Electronics Design](engineering/14-pcb-and-electronics-design.md) |
| 07 | [Structures & Materials](engineering/07-structures-and-materials.md) | | 15 | [Batteries & Energy Storage](engineering/15-batteries-and-energy-storage.md) |
| 08 | [Thermal Management](engineering/08-thermal-management.md) | | 16 | [Quantum Technologies](engineering/16-quantum-technologies.md) |

### Software, Compute & Infrastructure (`software/01–15`)

The production-software depth behind any fielded autonomy system — distributed
systems, GPUs, RTOS, networking, data, MLOps, security, crypto, observability,
cloud, Rust, compilers, performance, system design, and testing.

| # | Module |  | # | Module |
|---|---|---|---|---|
| 01 | [Distributed Systems Deep](software/01-distributed-systems-deep.md) | | 09 | [Observability & SRE](software/09-observability-and-sre.md) |
| 02 | [GPU & Parallel Computing](software/02-gpu-and-parallel-computing.md) | | 10 | [Cloud & Kubernetes](software/10-cloud-and-kubernetes.md) |
| 03 | [Real-Time Operating Systems](software/03-real-time-operating-systems.md) | | 11 | [Systems Programming in Rust](software/11-systems-programming-rust.md) |
| 04 | [Networking & Protocols](software/04-networking-and-protocols.md) | | 12 | [Compilers & Languages](software/12-compilers-and-languages.md) |
| 05 | [Databases & Data Engineering](software/05-databases-and-data-engineering.md) | | 13 | [Performance Engineering](software/13-performance-engineering.md) |
| 06 | [MLOps & ML Infrastructure](software/06-mlops-and-ml-infrastructure.md) | | 14 | [API & System Design](software/14-api-and-system-design.md) |
| 07 | [Cybersecurity Engineering](software/07-cybersecurity-engineering.md) | | 15 | [Testing & Verification Deep](software/15-testing-and-verification-deep.md) |
| 08 | [Applied Cryptography](software/08-cryptography-applied.md) | | | |

### Math, Science & Cross-cutting Foundations (`mathematics/01–12`)

The mathematics and physics under every layer above — optimization, probability,
linear algebra, numerical methods, signal processing, information theory, advanced
control, mechanics, thermo/fluids, electromagnetics, decision/game theory, and
algorithms. Deepens [03-foundations-mathematics.md](foundations/03-mathematics.md).

| # | Module |  | # | Module |
|---|---|---|---|---|
| 01 | [Optimization](mathematics/01-optimization.md) | | 07 | [Advanced Control](mathematics/07-control-advanced.md) |
| 02 | [Probability & Stochastic](mathematics/02-probability-and-stochastic.md) | | 08 | [Physics for Engineers](mathematics/08-physics-for-engineers.md) |
| 03 | [Applied Linear Algebra](mathematics/03-linear-algebra-applied.md) | | 09 | [Thermodynamics & Fluids](mathematics/09-thermodynamics-and-fluids.md) |
| 04 | [Numerical Methods](mathematics/04-numerical-methods.md) | | 10 | [Electromagnetics](mathematics/10-electromagnetics.md) |
| 05 | [Signal Processing](mathematics/05-signal-processing.md) | | 11 | [Decision & Game Theory](mathematics/11-decision-and-game-theory.md) |
| 06 | [Information Theory](mathematics/06-information-theory.md) | | 12 | [Algorithms & Complexity](mathematics/12-complexity-and-algorithms.md) |

### Hardware, AI Compute, Power & the Human Layer (`compute-and-hardware/01–04` + `mindset-and-society/01–04`)

A mixed applied band: the silicon-and-power reality under all software, how AI data
centers and distributed-compute startups actually work (and fail), and the human
dimension — manipulation defense, organizational politics, company design, the life
lessons that compound, and the inner operating system beneath them all: emotional
self-governance, how societies rise and fall, status and tribe, relationships, the
psychology of money, resilience, power, and meaning. Connects the engineering folder
(`engineering/01–16`), the companies folder (`companies/01–20`), and the
information-environment folder (`information-environment/01–06`).

| # | Module | What it makes you |
|---|---|---|
| 01 | [Raspberry Pi Deep Dive](compute-and-hardware/01-raspberry-pi-deep-dive.md) | Understand a real edge computer from SoC to fielded product |
| 02 | [Building AI Data Centers](compute-and-hardware/02-building-ai-data-centers.md) | Reason about power, cooling, networking, and the speed-to-power gap |
| 03 | [Distributed Data Centers & Startup Ideas](compute-and-hardware/03-distributed-data-centers-and-startup-ideas.md) | Critique the SPAN XFRA model and find better AI-compute bets |
| 04 | [Hardware Foundations](compute-and-hardware/04-foundations-no-software-without-hardware.md) | See why there is no software without hardware |
| 01 | [Psychological Manipulation Defense](mindset-and-society/01-psychological-manipulation-defense.md) | Recognize and defend against manipulation (never wield it) |
| 02 | [Big Tech Politics](mindset-and-society/02-politics-navigation.md) | Navigate organizational power with integrity and effectiveness |
| 03 | [Big Tech Flaws & the Optimal Company](mindset-and-society/03-flaws-and-the-optimal-company.md) | Diagnose structural flaws and design a better company |
| 04 | [Life Lessons People Ignore](mindset-and-society/04-life-lessons-people-ignore.md) | Internalize the compounding truths most people never live |

### Career Mastery — The Meta-Skills That Move Careers (`career/11–20`)

The original career band (`career/01–10`) covers the domains and the job-hunt mechanics
(resume, interview, clearance, negotiation). This band covers the **highest-leverage
career skills nobody writes down** — the relationship capital, communication,
reputation, money, execution, entrepreneurship, adaptability, sustainability, and
ethics that actually decide how far an engineer goes. It is the personal-operating-system
companion to the [companies band](companies/01-how-the-giants-win.md) and
[10-career-leadership-growth.md](career/10-leadership-growth.md).

| # | Module | What it makes you |
|---|---|---|
| 11 | [Networking, Mentors & Sponsors](career/11-networking-mentors-sponsors.md) | Build the relationship capital that gets you chosen, not just considered |
| 12 | [Technical Communication](career/12-technical-communication.md) | Make people understand, trust, and act on your work — the mid-career multiplier |
| 13 | [Personal Brand & Public Presence](career/13-personal-brand-public-presence.md) | Manufacture luck with a public body of work that draws opportunity inbound |
| 14 | [Job Search & Career Capital](career/14-job-search-career-capital.md) | Run your career as a portfolio of compounding capital, not a series of panics |
| 15 | [Financial Literacy & Wealth](career/15-financial-literacy-wealth.md) | Turn a high income into real wealth, freedom, and equity you don't fumble |
| 16 | [Productivity & Deep Work](career/16-productivity-deep-work.md) | Convert capability into shipped output sustainably, as an engineered system |
| 17 | [Engineer to Founder](career/17-engineer-to-founder.md) | Cross from building someone's product to building your own — with managed risk |
| 18 | [Career Pivots & the AI Era](career/18-career-pivots-ai-era.md) | Reinvent faster than the field changes; use AI as leverage, not threat |
| 19 | [Health, Energy & Career Longevity](career/19-health-energy-career-longevity.md) | Stay excellent for decades; treat burnout as a system failure to prevent |
| 20 | [Ethics, Export Control & Responsibility](career/20-ethics-export-control.md) | Stay far from the one mistake no technical brilliance can recover from (ITAR/EAR, classification, safety) |

These connect back to the job-hunt mechanics in `career/06–10`, the strategy in the
[companies band](companies/01-how-the-giants-win.md), the clearance baseline in
[07-career-security-clearance.md](career/07-security-clearance.md), and the
information-environment folder (`information-environment/01–06`).

---

### Band: General Knowledge (`general/`)

A broad, accessible band for the questions almost everyone is curious about —
money, the internet, AI, health, learning, and how the world around you works.
These are written for a general reader (lighter on jargon) while staying
first-principles and honest. They live in the `general/` folder and, like every
folder, are numbered independently from `01`.

| # | Module |  | # | Module |
|---|---|---|---|---|
| 01 | [How Money & Inflation Work](general/01-how-money-and-inflation-work.md) | | 08 | [Health Foundations](general/08-health-foundations-sleep-food-movement.md) |
| 02 | [Personal Finance & Investing](general/02-personal-finance-and-investing.md) | | 09 | [The Electric Grid & Energy](general/09-how-the-electric-grid-and-energy-work.md) |
| 03 | [How the Internet Works](general/03-how-the-internet-works.md) | | 10 | [Negotiation & Everyday Persuasion](general/10-negotiation-and-everyday-persuasion.md) |
| 04 | [How AI & LLMs Actually Work](general/04-how-ai-and-llms-actually-work.md) | | 11 | [Productivity, Focus & Time](general/11-productivity-focus-and-time-management.md) |
| 05 | [The Science of Learning](general/05-the-science-of-learning.md) | | 12 | [Statistics for Everyday Decisions](general/12-statistics-for-everyday-decisions.md) |
| 06 | [Critical Thinking & Fallacies](general/06-critical-thinking-and-logical-fallacies.md) | | 13 | [How GPS Finds You](general/13-how-gps-and-your-phone-find-you.md) |
| 07 | [How the Economy Works](general/07-how-the-economy-works.md) | | 14 | [Understanding Taxes](general/14-understanding-taxes.md) |

---

### The Human Operating System — Inner Mastery (`mindset-and-society/05–17`)

The technical bands above make you a world-class *engineer*. This band makes you a
world-class *operator of yourself* — the internal stack that sits **underneath**
every other module and decides whether all that knowledge ever becomes action. It
extends the human-layer modules (`mindset-and-society/01–04`) with the inner operating system:
emotional self-governance, resilience, the habit engine that converts knowing into
doing, the judgment that makes every decision better, the trained attention that
gates focus and learning, the creativity that produces asymmetric bets, and the
knowledge system that keeps it all compounding. It then widens out to the social
and existential layers: how societies rise and decay, the status and tribal games
that drive human behavior, the relationships and social capital that most reliably
predict a good life, the psychology of money, the honest mechanics of power, and the
search for meaning that keeps all of it from hollowing you out. These are the
highest-leverage subjects in the entire curriculum precisely because they
**multiply the value of everything else**.

| # | Module | What it makes you |
|---|---|---|
| 05 | [Stoicism & Emotional Self-Governance](mindset-and-society/05-stoicism-emotional-self-governance.md) | Govern your own mind under pressure — the inner OS beneath all the rest |
| 06 | [How Societies Rise, Decay & Renew](mindset-and-society/06-societies-rise-decay-renewal.md) | Read the long arc of institutions, trust, and civilizational health |
| 07 | [Status, Tribe & Social Dynamics](mindset-and-society/07-status-tribe-social-dynamics.md) | See the status and belonging games driving human behavior — and not be ruled by them |
| 08 | [Relationships & Social Capital](mindset-and-society/08-relationships-and-social-capital.md) | Build the relationships that most reliably predict a good life |
| 09 | [The Psychology of Money & Wealth](mindset-and-society/09-money-psychology-and-wealth.md) | Master the behavior, not just the math, of money — and define "enough" |
| 10 | [Resilience, Failure & Antifragility](mindset-and-society/10-resilience-failure-antifragility.md) | Recover from, and grow through, hard things; design a life that gains from stress |
| 11 | [Habits, Behavior Change & Self-Discipline](mindset-and-society/11-habits-behavior-change-and-discipline.md) | The engine that converts knowing into doing — the highest-impact module in the band |
| 12 | [Rationality, Mental Models & Judgment](mindset-and-society/12-rationality-mental-models-and-judgment.md) | Think well when it counts; raise the quality of every decision you make |
| 13 | [Meditation, Mindfulness & Flow](mindset-and-society/13-meditation-mindfulness-and-flow.md) | Train attention — the master resource under focus, learning, and regulation |
| 14 | [Creativity & Idea Generation](mindset-and-society/14-creativity-and-idea-generation.md) | Manufacture the non-obvious, asymmetric bet on demand |
| 15 | [Knowledge Management & the Second Brain](mindset-and-society/15-knowledge-management-and-second-brain.md) | Capture, connect, and retrieve everything you learn so it compounds *(stub)* |
| 16 | [Power — The Honest Manual](mindset-and-society/16-power-the-honest-manual.md) | Understand power clearly so you can wield it ethically and resist its abuse |
| 17 | [Meaning, Purpose & Avoiding Nihilism](mindset-and-society/17-meaning-purpose-avoiding-nihilism.md) | Build a durable "why" — the capstone that keeps everything else from going hollow |

These connect to the science of learning ([foundations/10](foundations/10-learning-how-to-learn.md)),
deep work ([career/16](career/16-productivity-deep-work.md)), the health substrate
([general/08](general/08-health-foundations-sleep-food-movement.md)), the formal
decision math ([mathematics/11](mathematics/11-decision-and-game-theory.md)), and
the cognition module in the information-environment band
([03](information-environment/03-cognitive-bias-attention-and-narratives.md)).

---

### Extended Foundations — Cross-Cutting Literacy (`foundations/10–21`)

The spine table above lists the original foundations spine (`01–09`). These twelve
modules extend the foundations folder into the **cross-cutting literacy** that makes
every technical module land: how to learn, write, reason about data, money, decisions,
ethics, negotiation, health, systems, history, and law. They are the bridge between
the technical bands and the human-operating-system band, and several are referenced
from the learning paths and the Human OS band above.

| # | Module | What it makes you |
|---|---|---|
| 10 | [Learning How to Learn](foundations/10-learning-how-to-learn.md) | Reach working competence in any hard field in weeks, through deliberate practice |
| 11 | [Writing & Technical Communication](foundations/11-writing-and-technical-communication.md) | Make complex ideas legible so your docs get approved and your reasoning earns authority |
| 12 | [Applied Statistics & Causal Inference](foundations/12-applied-statistics-and-causal-inference.md) | Extract valid causal conclusions from messy real data and tell signal from noise |
| 13 | [Economics & Markets](foundations/13-economics-and-markets.md) | See the incentives behind any behavior and build things that actually win markets |
| 14 | [Personal Finance & the Math of Wealth](foundations/14-personal-finance-and-the-math-of-wealth.md) | Master compounding and optionality to buy back your freedom and take asymmetric bets |
| 15 | [Decision-Making & Rationality](foundations/15-decision-making-and-rationality.md) | Reason in probabilities, defeat your biases, and be trusted with high-stakes ambiguous calls |
| 16 | [Ethics of Force & Engineering Responsibility](foundations/16-ethics-of-force-and-engineering-responsibility.md) | Reason rigorously about lethal-capability work and keep capability tethered to conscience and law |
| 17 | [Negotiation & Persuasion](foundations/17-negotiation-and-persuasion.md) | Win resources, compensation, and buy-in without burning relationships or your integrity |
| 18 | [Health, Energy & Human Performance](foundations/18-health-energy-and-human-performance.md) | Sustain hard cognitive work at a high level for years without burning out |
| 19 | [Systems Thinking & Complexity](foundations/19-systems-thinking-and-complexity.md) | Diagnose the structure driving a misbehaving system and find its high-leverage intervention points |
| 20 | [History of Technology & War](foundations/20-history-of-technology-and-war.md) | Place any technology or strategic situation in its historical pattern and anticipate what's coming |
| 21 | [Law, Contracts & IP for Builders](foundations/21-law-contracts-and-ip-for-builders.md) | Read contracts, protect your inventions, and know exactly when you need a lawyer |

### Specialist Domains — Space & Products (`space/01`, `products/01`)

Two single-module folders that round out the breadth of the curriculum: one takes the
autonomy stack into orbit, the other treats your own tooling as a force multiplier.

| Folder | Module | What it makes you |
|---|---|---|
| `space/01` | [Space Systems & Astronautics](space/01-space-systems-and-astronautics.md) | Reason from vis-viva to real missions — sizing orbits, constellations, link and power budgets for contested space |
| `products/01` | [Twenty Underrated, High-Impact Products](products/01-twenty-underrated-high-impact-products.md) | Treat tooling as a force multiplier — smell 10× tools early and delete recurring friction permanently |

### Separate Collection — Machine Learning Course Materials (`machine learning/`)

The `machine learning/` folder is **not part of the mastery curriculum** above; it is a
self-contained collection of university machine-learning course materials (CPSC 5310)
kept in this repository for convenience. It includes weekly lecture decks (statistics,
regression, classification, SVMs, ensembles, clustering, PCA, neural networks,
attention/transformers, and GenAI systems), hands-on notebooks (CNN, RNN, Transformer,
and RAG "course assistant"), and two review documents:
[STUDY_GUIDE.md](machine%20learning/STUDY_GUIDE.md) and
[FINAL_PRACTICE_EXAM.md](machine%20learning/FINAL_PRACTICE_EXAM.md). It complements the
first-principles ML coverage in [autonomy/01](autonomy/01-ml-ai.md) and
[general/04](general/04-how-ai-and-llms-actually-work.md) but is maintained separately.

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
`information-environment/01 → 02 → 03 → 04 → 05 → 06`
Rationale: understand the information environment as a system, then platform
mechanics, then the cognition they act on, then influence operations and their
defense, then lawful OSINT verification, and finally OPSEC and resilience. This is
the defense-oriented, *understanding-and-defense* path — pair it with `foundations/07` (mission
context) and `career/07` (security baseline). It makes you fluent in the sensing, trust, and
information dimensions of modern defense problems, not just the hardware/software ones.

### Path F — "I want elite autonomy depth" (research-grade stack)
`autonomy/11 → 12 → 13 → 14 → 15 → 16 → 17 → 20 → 22 → 23 → 25`
Rationale: build perception, then the estimation/SLAM spine, then planning and
learning, then the vision/VIO/deployment skills that put it on real hardware. Pair
with the math folder (`mathematics/01–06`) exactly when an equation stops making sense.

### Path G — "I want full-stack hardware fluency"
`engineering/01 → 10 → 09 → 04 → 14 → 07 → 08 → 06 → 05 → 12 → 13`
Rationale: firmware and sensors first, then actuation and power, then board/structure/
thermal/aero, then propulsion, finishing with systems engineering and reliability —
the order in which a real vehicle is actually built and certified.

### Path H — "I want to beat the giants"
`companies/01 → 11 → 13 → 12`, plus the company deep-dives (`companies/02–10`) for the ones you compete
with. Pair with [08-foundations-company-strategy-moat.md](foundations/08-company-strategy-moat.md)
and [02-ten-year-mastery-plan.md](foundations/02-ten-year-mastery-plan.md). This is the strategy
path: see the patterns, learn the asymmetric playbook, then install the skills and
mechanisms in whatever you build.

### Path I — "I want production-software depth"
`software/01 → 04 → 03 → 02 → 13 → 11 → 09 → 10 → 07 → 15`
Rationale: distributed systems and networking first, then real-time and GPU compute,
then performance and Rust, then operations, security, and disciplined testing.

### Path J — "I want to compound my career, not just survive it"
`career/14 → 12 → 11 → 13 → 16 → 15 → 19`, plus `career/20` early and always.
Rationale: first see your career as compounding capital, then build the
communication and relationship capital that move it, then the public presence that
makes opportunity inbound, then the execution and money systems that turn it into
freedom — all riding on the health that sustains a multi-decade career, and fenced by
the ethics/export-control discipline that protects all of it. Add `career/17` if founding
is on the table and `career/18` to stay relevant as the field shifts. Pair with the
job-hunt mechanics in `career/06–10` and the strategy in the companies folder (`companies/01–13`).

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
- [01-autonomy-ml-ai.md](autonomy/01-ml-ai.md) — perception & learning.
- [09-autonomy-gnc.md](autonomy/09-gnc.md) — guidance, navigation & control.
- [10-autonomy-planning-decision.md](autonomy/10-planning-decision.md) — planning & decision-making.
- [06-autonomy-control-theory.md](autonomy/06-control-theory.md) — control deep dive.

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
