# Landing a Job at Boeing, SpaceX, or a Leading Defense-Tech Company (2026 Edition)

A field guide for aerospace BS/MS graduates. This is opinionated, dense, and built
to be acted on. Read it once end-to-end, then come back and use the checklists.

---

## 0. The 60-Second Summary

- **Boeing** = large, process-driven, defense + commercial aviation. Values rigor,
  systems engineering, certification knowledge, security clearances, and stability.
- **SpaceX** = fast, vertically integrated, hardware-rich, brutal pace. Values raw
  ability, hands-on building, first-principles thinking, and ownership.
- **Leading defense-tech companies** = defense-tech startup energy at scale, software-defined hardware,
  autonomy/AI. Values builders who ship, software fluency, and mission alignment.

What they all reward in 2026: **you have actually built and flown/tested real
hardware or software, you understand systems end-to-end, and you can prove it.**

The single biggest differentiator between candidates is not GPA. It is
**demonstrated building** — projects, internships, research, competition teams,
and a portfolio that shows you ship.

---

## 1. Core Engineering Fundamentals (Non-Negotiable)

These are the things an interviewer assumes you know cold. If you are rusty,
this is your study list.

### 1.1 Aerodynamics & Fluid Mechanics
- Conservation laws: mass, momentum, energy (integral and differential forms).
- Bernoulli, compressible flow, isentropic relations, normal/oblique shocks.
- Mach number regimes: subsonic, transonic, supersonic, hypersonic.
- Airfoil theory, lift/drag, boundary layers, separation, stall.
- Reynolds and Mach scaling; when each dominates.
- Computational Fluid Dynamics (CFD) literacy: what RANS vs LES vs DNS mean,
  mesh quality, y+ , turbulence models (k-ε, k-ω SST). You don't need to be a
  CFD PhD, but you must speak the language.

### 1.2 Propulsion
- **Air-breathing:** Brayton cycle, turbojet/turbofan/turboprop, bypass ratio,
  thrust specific fuel consumption (TSFC), compressor/turbine stages.
- **Rocket:** Tsiolkovsky rocket equation ($\Delta v = I_{sp}\, g_0 \ln(m_0/m_f)$),
  specific impulse, thrust = $\dot{m} v_e + (p_e - p_a)A_e$, nozzle expansion,
  combustion, staging, throttling.
- Engine cycles for rockets: gas-generator, staged combustion (full-flow like
  SpaceX Raptor), electric/pressure-fed, expander. Know the tradeoffs.
- Cooling: regenerative, film, ablative.

### 1.3 Structures & Materials
- Statics, stress/strain, Mohr's circle, failure criteria (von Mises, Tresca).
- Beam bending, torsion, buckling (Euler), thin-walled pressure vessels.
- Fatigue (S-N curves, Miner's rule), fracture mechanics, damage tolerance —
  **huge** at Boeing for airframe certification.
- Composites: laminate theory basics, layup, anisotropy, why aerospace loves
  carbon fiber, and the failure modes (delamination).
- Finite Element Analysis (FEA) literacy: element types, mesh convergence,
  boundary conditions, interpreting stress concentrations.

### 1.4 Dynamics, Controls & GNC
- Rigid body dynamics, 6-DOF equations of motion, reference frames, quaternions
  vs Euler angles (and gimbal lock).
- Classical control: transfer functions, Laplace, root locus, Bode, gain/phase
  margin, PID tuning.
- Modern control: state-space, controllability/observability, LQR, pole placement.
- Estimation: Kalman filter (and EKF/UKF), sensor fusion (IMU + GPS).
- **Guidance, Navigation & Control (GNC)** is one of the hottest skill areas at
  all three, especially SpaceX (landing) and leading defense-tech companies (autonomy).

### 1.5 Orbital Mechanics (Space track)
- Two-body problem, Kepler's laws, orbital elements.
- Hohmann transfers, bi-elliptic, plane changes, $\Delta v$ budgeting.
- Lambert's problem, patched conics, gravity assists (conceptually).
- Reference frames (ECI, ECEF), ground tracks, station-keeping, deorbit.
- Tools: GMAT, STK (AGI/Ansys), or Poliastro/Astropy in Python.

### 1.6 Thermodynamics & Heat Transfer
- Cycles, entropy, conduction/convection/radiation.
- Thermal management of spacecraft and electronics; reentry heating.

### 1.7 Systems Engineering
- Requirements flow-down, V-model, verification & validation (V&V), trade studies,
  margins, interface control documents (ICDs), failure modes (FMEA), reliability.
- This is the connective tissue. Boeing especially lives and breathes it.

---

## 2. The 2026 Skill Stack (What's Actually Changed)

The classic curriculum is necessary but no longer sufficient. In 2026 the bar
moved toward software, autonomy, and digital engineering.

### 2.1 Programming — You Must Code
- **Python**: the universal glue. NumPy, SciPy, Matplotlib, Pandas, control,
  simulation, data analysis. Non-negotiable.
- **C/C++**: embedded, flight software, performance-critical systems. SpaceX and
  defense-tech flight/avionics roles expect real C++ (modern C++17/20). Memory model,
  RAII, real-time constraints.
- **MATLAB/Simulink**: still dominant for GNC and controls modeling, especially
  Boeing and legacy defense. Know it.
- **Rust**: rising in defense-tech (leading defense-autonomy companies use it). A plus, not yet required.
- **Julia**: niche but appears in scientific computing.

### 2.2 Autonomy, AI & ML
- This is the defining shift. Leading defense-tech companies are fundamentally autonomy companies;
  SpaceX uses ML for vision/landing/manufacturing; Boeing invests in autonomous
  systems and AI-assisted design.
- Learn: linear algebra for ML, basic neural nets, computer vision (object
  detection, SLAM), sensor fusion, path planning (A*, RRT, MPC), reinforcement
  learning at a conceptual level.
- Frameworks: PyTorch, ONNX, OpenCV, ROS 2.
- You don't need to be an ML researcher, but autonomy fluency is a massive edge.

### 2.3 Robotics & Embedded
- ROS 2, real-time operating systems (RTOS), microcontrollers (STM32),
  flight controllers (PX4/ArduPilot — relevant to drone/UAS work).
- Hardware-in-the-loop (HIL) and software-in-the-loop (SITL) testing.
- Hands-on: solder, wire, debug with an oscilloscope/logic analyzer, read a
  datasheet, bring up a board. This impresses SpaceX and defense-tech companies enormously.

### 2.4 Digital Engineering & Tools
- **CAD**: SolidWorks, CATIA (Boeing), NX, Fusion 360, Onshape.
- **Model-Based Systems Engineering (MBSE)**: SysML, Cameo. Boeing and large
  primes increasingly require it.
- **Simulation**: Ansys, Abaqus, Nastran, Star-CCM+, COMSOL.
- **Version control**: Git is mandatory. Know branching, PRs, code review.
- **Linux**: be comfortable on the command line.

### 2.5 Data & Test
- Test data acquisition (DAQ), LabVIEW, signal processing, statistics.
- Telemetry analysis, anomaly detection, the discipline of test-driven iteration
  (SpaceX's "test, fly, fail, fix, repeat" culture).

---

## 3. Company-by-Company Deep Dive

### 3.1 Boeing

**Culture & what they want**
- Large, structured, process- and safety-driven. Commercial aviation
  (737/777/787), defense (fighters, tankers, satellites via subsidiaries),
  and space (Starliner, SLS work).
- Values: certification knowledge (FAA Part 25, DO-178C for software, DO-254 for
  hardware), systems engineering rigor, documentation discipline, reliability.
- Stability and benefits over startup intensity. Good for those who want
  deep specialization and structured growth.

**What to emphasize**
- Systems engineering, V&V, requirements, configuration management.
- Airworthiness, certification, safety analysis (FMEA, fault trees).
- Strong fundamentals and attention to detail.

**Clearance**: many roles (defense/space) need a U.S. **security clearance**.
You generally must be a U.S. person. Even commercial roles can require ITAR
compliance. This is a gating factor — see Section 6.

**Watch the context**: Boeing has been under intense quality/safety scrutiny.
Showing genuine commitment to engineering rigor and safety culture resonates.

### 3.2 SpaceX

**Culture & what they want**
- Extreme pace, vertical integration (they build almost everything in-house),
  long hours, high ownership, low bureaucracy. "Move fast, test hardware."
- Values raw engineering talent, first-principles reasoning, hands-on building,
  and people who take responsibility end-to-end.
- Hardware-rich: Falcon 9, Starship, Dragon, Raptor engines, Starlink.

**What to emphasize**
- Things you have physically built and tested. Rocketry teams, Formula SAE,
  combustion projects, custom electronics, anything where you made hardware work.
- First-principles problem solving. They love "I calculated it from scratch."
- Willingness to grind. Be honest with yourself about the lifestyle.

**Interview reality**
- Technical and deep. Expect fundamentals derived live, not memorized.
- Common areas: thermodynamics, fluids, structures, controls, plus a coding
  screen for software-adjacent roles.
- They ask about your projects in extreme detail — know YOUR work cold.

**Clearance**: generally requires U.S. person status (ITAR), though not always a
formal clearance.

### 3.3 Leading Defense-Tech Companies

**Culture & what they want**
- Defense-tech "startup at scale." Mission-driven (Western defense), software-first,
  build autonomous systems: an integrated autonomy/C2 platform (AI command software),
  attritable drones, underwater vehicles, counter-UAS, and interceptors.
- Values builders who ship fast, strong software engineers, autonomy/AI/ML talent,
  and people aligned with the mission (this matters to them — they screen for it).
- Less aerospace-traditional, more Silicon-Valley-meets-defense.

**What to emphasize**
- Software fluency (C++, Python, Rust), autonomy, computer vision, sensor fusion,
  embedded systems, real-time control.
- Full-stack hardware/software integration. Shipping working systems.
- Comfort with ambiguity and rapid iteration.

**Interview reality**
- Strong software/coding component even for many "hardware" roles.
- Systems thinking across hardware + software + autonomy.

**Clearance & mission fit**: U.S. person status typically required; clearances
common. They explicitly care that you want to work in defense — have a real,
honest answer for "why defense?"

---

## 4. Projects & Experience That Actually Land Offers

Ranked roughly by impact. Stack several of these.

1. **Internships at aerospace/defense/hardware companies.** The single strongest
   signal. Apply early and broadly; return offers are common.
2. **Hands-on engineering teams**: collegiate rocketry (especially anything that
   flew to high altitude or competed at Spaceport America Cup / FAR), CubeSat
   programs, Design/Build/Fly (DBF), Formula SAE, combustion/liquid engine teams,
   autonomous drone/robotics teams.
3. **Built hardware you can demo**: a flight controller, a small turbine, a
   pressure-fed engine test, a tracked telemetry system, a working UAV.
4. **Research** (especially MS): GNC, propulsion, autonomy, structures. Publications
   help for R&D roles.
5. **Software/autonomy projects**: a SLAM implementation, a Kalman-filter sensor
   fusion demo, a reinforcement-learning landing sim, a CV object detector running
   on a Jetson. Put them on GitHub.
6. **Simulations from scratch**: a 6-DOF rocket sim, an orbit propagator, a
   trajectory optimizer. Shows you understand the physics AND can code it.

**The portfolio rule**: if it isn't documented (GitHub, a writeup, a video, photos),
it's much weaker in an interview. Build a simple portfolio. Show, don't tell.

---

## 5. The Math & Physics You Can't Fake

Interviewers probe these because they reveal depth.

- **Linear algebra**: eigenvalues, matrix decomposition, rotations, least squares.
  Underpins controls, ML, and estimation.
- **Differential equations**: ODEs, PDEs, stability, numerical integration
  (RK4 — know how to write it).
- **Probability & statistics**: distributions, Bayes, error propagation,
  hypothesis testing, Monte Carlo. Critical for test, reliability, and ML.
- **Numerical methods**: integration, root finding, optimization, conditioning.
- **Vector calculus**: gradients, divergence, curl (fields, fluids, EM).

If you can derive the rocket equation, set up a free-body diagram under load,
linearize a system about an operating point, and write an RK4 integrator — you're
in good shape.

---

## 6. The Gatekeepers: Citizenship, Clearance & ITAR

This trips up many candidates, so be clear-eyed.

- Most U.S. aerospace/defense roles require **U.S. person** status (citizen or
  permanent resident) because of **ITAR/EAR** export-control law.
- Defense and space roles often require a **security clearance** (Secret / Top
  Secret). You can't get one yourself; an employer sponsors it. A clean
  background, financial responsibility, and limited foreign contacts help.
- If you are an international student: focus on companies/roles that don't require
  ITAR restriction (some commercial, research, or non-U.S. divisions), pursue
  green-card paths, and lean into research where visa sponsorship is more common.
- Be honest about your status early — it determines which doors are open.

---

## 7. Resume, Application & Interview Playbook

### 7.1 Resume
- One page (early career). Lead with projects and impact, quantify everything
  ("reduced mass 18%", "achieved apogee of 9,200 ft", "cut sim runtime 40%").
- Tailor keywords to the job posting (ATS systems are real).
- List concrete tools/skills you can actually defend in an interview.
- Put a GitHub/portfolio link at the top.

### 7.2 Applying
- Apply **early** (fall for next summer; many close by winter).
- Referrals dramatically improve your odds — network with alumni, recruiters at
  career fairs, and engineers on LinkedIn (be specific and respectful).
- Don't only apply to the big three. Build experience at suppliers, startups
  (Stoke, Relativity, Hermeus, Ursa Major, Vast, etc.), and primes (Lockheed,
  Northrop, RTX, Blue Origin). Each makes you a stronger candidate for the next.

### 7.3 Interviews
- **Know your own projects cold.** Every number, every decision, every failure.
- Expect to derive fundamentals live. Practice on a whiteboard, out loud.
- For software-adjacent roles, do **coding practice** (LeetCode easy/medium,
  plus embedded/C++ specifics). SpaceX and defense-tech companies screen for it.
- Behavioral: ownership, dealing with failure, teamwork under pressure. Use
  STAR (Situation, Task, Action, Result).
- Have sharp answers for: "Why this company?" and (for defense-tech/defense) "Why
  defense?" Generic answers sink candidates.
- Ask good questions. Show genuine curiosity about their hardware/mission.

---

## 8. A Concrete 6–12 Month Plan

If you're starting from "solid student, not job-ready," do this:

1. **Months 1–2**: Pick a track (GNC/autonomy, propulsion, structures, avionics).
   Refresh fundamentals in Sections 1 & 5. Get fluent in Python + Git.
2. **Months 2–4**: Build one real project end-to-end (e.g., a 6-DOF sim with a
   controller, or a sensor-fusion demo on real hardware). Document it on GitHub.
3. **Months 3–6**: Join/contribute to a hands-on team or open-source project
   (PX4/ArduPilot, a CubeSat, a rocketry team). Get hardware under your nails.
4. **Months 4–8**: Learn one "2026 edge" skill deeply — autonomy/ML, or modern
   C++ embedded, or MBSE. Ship something with it.
5. **Months 5–9**: Polish resume + portfolio. Start applying early, get referrals,
   do mock interviews, grind coding + fundamentals.
6. **Ongoing**: Track applications, follow up, iterate on rejections. Persistence
   is part of the skill.

---

## 9. Curated Learning Resources

**Books**
- *Fundamentals of Aerodynamics* — Anderson
- *Mechanics and Thermodynamics of Propulsion* — Hill & Peterson
- *Rocket Propulsion Elements* — Sutton
- *Orbital Mechanics for Engineering Students* — Curtis
- *Feedback Systems* — Åström & Murray (free PDF)
- *Probabilistic Robotics* — Thrun (for autonomy/estimation)
- *Aircraft Structures for Engineering Students* — Megson

**Courses / Online**
- MIT OCW: Unified Engineering, 16.07 Dynamics, 6.832 Underactuated Robotics
- Brian Douglas / "Control Systems Lectures" (YouTube) for controls intuition
- Russ Tedrake's Underactuated Robotics (autonomy/control)
- Fast.ai or Andrew Ng for ML foundations
- ArduPilot/PX4 dev docs for real flight-software exposure

**Practice**
- LeetCode (coding), Project Euler (numerical), Kaggle (data/ML)
- Build, don't just watch.

---

## 10. Mindset: What Separates Hired from Rejected

- **Builders beat memorizers.** Demonstrated, documented building is the moat.
- **Depth on your own work** matters more than breadth you can't defend.
- **First principles**: be the person who derives, not just recalls.
- **Ownership**: speak in terms of what *you* did and decided.
- **Honesty about failure**: every great project has failures; own and explain them.
- **Mission/fit**: especially at SpaceX (intensity) and defense-tech companies (defense) — they
  screen hard for genuine alignment. Be real about what you want.

The job market is competitive, but the formula is unglamorous and reliable:
master the fundamentals, build real things, prove it, and apply relentlessly.

---

*Notes: Specific certification standards, clearance requirements, and tool stacks
evolve. Always confirm current requirements on each company's careers page and in
the specific job listing before applying.*

---

## 11. Deeper Dive: The 2026 Hiring Market & Emerging Tracks

### 11.1 What changed in the last 24 months
- **Reusable launch went mainstream.** SpaceX Starship iteration normalized
  "fly, fail, fix" at scale; competitors (Blue Origin New Glenn, Rocket Lab
  Neutron, Stoke, Relativity) hire for rapid-iteration hardware engineers, not
  just analysts.
- **Defense-tech funding surged.** Shield AI, Saronic, and a wave of
  Series-B+ startups expanded autonomy/embedded headcount. The bar shifted
  toward shipping software-defined hardware.
- **Autonomy + AI is now a first-class aerospace discipline,** not an add-on.
  GNC, perception, and edge ML roles multiplied.
- **Drone/UAS and counter-UAS** demand spiked post-2022 (lessons from Ukraine):
  cheap attritable systems, electronic warfare resilience, and swarming.

### 11.2 Emerging role families worth targeting
| Track | What you do | Who hires |
|---|---|---|
| **GNC / autonomy** | Estimation, control, planning for vehicles | SpaceX, Shield AI, Skydio |
| **Flight software / avionics** | Real-time C++/Rust on the vehicle | All three + primes |
| **Propulsion test** | Build, instrument, fire, analyze engines | SpaceX, Ursa Major, Stoke |
| **Manufacturing / production eng** | Scale hardware from 1 to 1000s | SpaceX, defense-tech startups, Boeing |
| **Systems / integration & test** | Prove the whole system works | Everyone; great entry point |
| **Digital engineering / MBSE** | Model-based systems engineering | Boeing, primes |

### 11.3 The compensation & lifestyle reality (be honest with yourself)
- **SpaceX:** strong equity-light cash + RSUs, intense hours (50–60+/wk common),
  high burnout but unmatched hardware velocity and resume value.
- **Defense-tech startups:** competitive cash + meaningful equity,
  startup intensity, mission-driven culture.
- **Boeing/primes:** stable comp, better work-life balance, pension/benefits,
  slower pace, deep specialization. Clearance adds a durable salary premium.
- A **TS/SCI clearance** can add a 10–20% lifetime earnings premium and makes
  you far harder to replace.

### 11.4 The fastest credibility builders (ranked)
1. A **flown** hardware result (even a small UAV or high-power rocket) with data.
2. An **internship** at any hardware/defense company (return-offer pipeline).
3. A **from-scratch simulation** (6-DOF sim, orbit propagator, EKF) on GitHub.
4. An **open-source contribution** to PX4/ArduPilot/Astropy/poliastro.
5. A **competition team** result (Spaceport America Cup, DBF, Formula SAE).

---

## Sources & Citations

**Foundational texts**
- Anderson, J.D. — *Fundamentals of Aerodynamics*, McGraw-Hill.
- Sutton, G.P. & Biblarz, O. — *Rocket Propulsion Elements*, Wiley.
- Hill, P. & Peterson, C. — *Mechanics and Thermodynamics of Propulsion*, Pearson.
- Curtis, H. — *Orbital Mechanics for Engineering Students*, Elsevier.
- Åström, K.J. & Murray, R.M. — *Feedback Systems* (free): https://fbswiki.org
- Thrun, Burgard, Fox — *Probabilistic Robotics*, MIT Press.
- Megson, T.H.G. — *Aircraft Structures for Engineering Students*, Elsevier.

**Courses & official docs**
- MIT OpenCourseWare (Unified Engineering, 16.07 Dynamics): https://ocw.mit.edu
- Russ Tedrake, *Underactuated Robotics* (MIT 6.832): https://underactuated.mit.edu
- PX4 Autopilot developer docs: https://docs.px4.io
- ArduPilot developer docs: https://ardupilot.org
- NASA Technical Reports Server (NTRS): https://ntrs.nasa.gov

**Export control & hiring context**
- U.S. Dept. of State, Directorate of Defense Trade Controls (ITAR): https://www.pmddtc.state.gov
- U.S. Bureau of Industry and Security (EAR): https://www.bis.doc.gov
- Company careers pages (authoritative for current requirements): SpaceX, Boeing, and leading defense-tech companies.

*Compiled from the author's domain knowledge and the publicly available sources above. Standards (DO-178C, FAA Part 25), clearance rules, and tool stacks change — verify against primary sources before relying on them.*

---

## ⚡ The Insider Layer — What the Field Knows but Rarely Writes Down

The brochures sell you a meritocracy of GPA and coursework. The actual hiring
machine sorts on dimensions the career office never mentions. Here is the part
engineers learn three years in.

### The funnel filters in an order nobody tells you
A defense aerospace requisition is screened roughly in this sequence: **U.S.-person
status (ITAR) → clearance/clearability → ATS keyword match → human skim**. The
engineering doesn't get evaluated until the last step. This is why a non-citizen's
brilliant résumé silently evaporates on the classified side, and why a mediocre
candidate with an active clearance gets a callback the same afternoon. The single
highest-leverage line on a defense résumé is not a project — it's *"U.S. Citizen,
active Secret"*. An active clearance is worth roughly a full seniority level in
practice, because it removes 6–18 months of carrying cost the employer would
otherwise eat before you can bill to the contract.

### Internships are the front door; the new-grad req is the back alley
The dominant path into Boeing, SpaceX, and the primes is **intern-to-full-time
conversion**, not the public job board. Conversion offers face a far smaller,
friendlier funnel; the open new-grad req is a meat grinder where qualified
candidates routinely see single-digit response rates. New-grad and college reqs
also open in *bursts* tied to the fiscal-year budget and to program wins — apply
the day a posting goes live, because recruiters work the top of the stack and ATS
timestamps are real. A referral that lands you on a hiring manager's desk bypasses
the entire keyword gauntlet.

### SpaceX interviews like an oral qualifying exam, not a coding shop
The folklore is true: expect first-principles vivas — *derive the rocket equation,
size this pressure vessel, walk me through a Brayton cycle on the whiteboard, what
have you physically built and broken.* They are probing whether you *understand*
versus *memorized*, and they reward people who've gotten their hands dirty on real
hardware. The unwritten trade: you exchange a few years of 50–60-hour weeks and
high churn for a launchpad-grade brand on your résumé. Go in clear-eyed about the
price, not just the prestige.

### At primes, the "charge number" governs your week and your job security
You don't really work for Boeing or Lockheed — you work for a **contract charge
number**. When your program's funding runs thin you get "benched," reassigned, or
laid off, almost independently of your performance reviews. Layoffs track
**program wins and losses on recompetes**, not individual output. The practical
move: read *Defense News* and *Breaking Defense* like a ticker for your own
employer, and learn enough budget literacy (RDT&E vs. procurement "color of
money") to know whether your seat sits on stable, multi-year money or on a
fragile line that Congress can zero in a markup.

### Prime compensation is paid in stability, not cash or equity
Comp is banded to a job code; equity is essentially nonexistent and base growth is
slow. The *real* compensation is the benefit stack — strong retirement, 9/80
schedules (every other Friday off), tuition reimbursement, and, crucially, the
**clearance and certification experience you accumulate and carry elsewhere**. The
common wealth-building play is: get cleared and trained at a prime, then jump to a
defense-tech startup or contractor body-shop for a 20–40% raise the prime's bands
could never authorize. There's no real "up or out" — you can plateau comfortably
for a decade, and the genuine risk is skill atrophy on a single program rather
than being managed out.

### ITAR controls what you're even allowed to read
Export control isn't an HR formality — it physically gates rooms, wikis, and
repositories. As a non-U.S.-person you can be barred from the technical data
altogether, and even green-card holders hit walls at SAP and full clearance tiers.
This is the mechanical reason "U.S. Person" appears on nearly every defense req,
and why naturalization timing is a legitimate, deliberate career lever rather than
a paperwork afterthought.

### The résumé is read by a machine, then by a human in eight seconds
Mirror the posting's exact nouns — *"composite layup," "GD&T," "DO-178C,"
"thermal," "6-DOF"* — because the ATS does literal string matching and the human
skims only the top third. Quantify or it didn't happen: "reduced mass 22%,
validated within 8% of FEA" survives a skim where "worked on structures" dies.
The people who get hired aren't the ones who know the most aerodynamics; they're
the ones who made their evidence *legible to a stranger in a hurry*.
