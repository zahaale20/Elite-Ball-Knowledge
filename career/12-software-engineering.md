# Software Engineering for Defense & Aerospace: A Job-Readiness Guide (Boeing / Anduril)

A practical roadmap of the software knowledge, tools, and habits that get you hired and keep you effective at companies like **Boeing**, **Anduril**, **Lockheed Martin**, **Northrop Grumman**, **SpaceX**, **Skydio**, and **Shield AI**.

> You're already working with PX4/Pixhawk — that's directly relevant. This guide connects that experience to what these employers actually screen for.

---

## 0. The Two Cultures (Read This First)

The defense/aerospace software world splits into two very different cultures. Know which roles you're targeting.

| | **"Old-space / Primes"** (Boeing, Lockheed, Northrop, Raytheon) | **"New defense-tech"** (Anduril, SpaceX, Skydio, Shield AI) |
|---|---|---|
| Process | Heavy, certified, document-driven (DO-178C, AS9100) | Fast, iterative, startup-paced but still rigorous |
| Languages | C, C++, Ada, MATLAB/Simulink, some Java | C++, Rust, Python, Go, TypeScript |
| Hiring bar | Domain knowledge + clearance + process discipline | Strong CS fundamentals + systems/embedded + ship fast |
| Interview style | Behavioral + domain + moderate coding | Hard data-structures/algorithms + systems design + take-home |
| What impresses | Safety certification experience, real flight software | Shipped autonomy/robotics, performance optimization, ownership |

**Bottom line:** Anduril/SpaceX interview much more like elite tech companies (LeetCode-hard + systems design). Boeing/Lockheed weigh domain experience, process maturity, and clearance more heavily.

---

## 1. Security Clearance (The Gatekeeper)

This is often more decisive than your coding skill for defense roles.

- **U.S. citizenship is almost always required.** Most roles need it; clearances *always* do.
- **Clearance levels:** Public Trust → Secret → Top Secret → TS/SCI (with polygraph for some).
- You usually **can't get a clearance yourself** — a sponsoring employer initiates it. So "clearable" (clean background, citizen) is the realistic entry state.
- **What helps clearability:** clean criminal/financial history, limited foreign contacts, no drug issues, honesty on the SF-86 form.
- **Anduril** sponsors clearances heavily; **Boeing** too. Having even a Secret clearance already makes you dramatically more hireable.

> Action: If you're a U.S. citizen with a clean record, you are "clearable." Say so on your resume. If not a citizen, target the (fewer) commercial/ITAR-exempt roles.

---

## 2. Core CS Fundamentals (Non-Negotiable)

These get tested in interviews regardless of company.

### Data Structures & Algorithms
- Arrays, strings, hash maps, linked lists, stacks, queues
- Trees (BST, heaps, tries), graphs (BFS/DFS, Dijkstra, A*)
- Sorting, binary search, two-pointers, sliding window
- Dynamic programming, recursion, backtracking
- **Big-O analysis** — time and space, for everything

> Practice: **LeetCode** (target 150–250 problems, focus on Blind 75 / NeetCode 150). Anduril and SpaceX ask genuinely hard problems. A* and graph search are *especially* relevant for autonomy/path-planning roles.

### Operating Systems & Concurrency
- Processes vs threads, scheduling, context switches
- Mutexes, semaphores, condition variables, deadlock, race conditions
- Memory: stack vs heap, virtual memory, paging, cache behavior
- Real-time scheduling (RTOS concepts — directly relevant to flight software)

### Computer Architecture
- How CPUs work, pipelines, caches, memory hierarchy
- Endianness, alignment, word sizes (matters for embedded + protocols)
- Fixed-point vs floating-point math

### Networking
- TCP vs UDP (UDP dominates real-time telemetry — e.g., MAVLink over UDP)
- IP, sockets, ports, latency vs throughput
- Serialization formats: Protocol Buffers, FlatBuffers, MAVLink, JSON

---

## 3. Programming Languages (What to Actually Learn)

Prioritized for defense/aerospace:

### C++ — **The single most important language**
- This is the backbone of flight software, autonomy stacks, and simulators.
- Learn deeply:
  - RAII, smart pointers (`unique_ptr`, `shared_ptr`), ownership
  - Move semantics, rvalue references, perfect forwarding
  - Templates and generic programming, the STL
  - Modern C++ (C++17/20): `std::optional`, `std::variant`, `constexpr`, ranges
  - Avoiding undefined behavior; understanding the memory model
  - Real-time constraints: avoiding dynamic allocation in hot paths
- **Resources:** *Effective Modern C++* (Scott Meyers), *A Tour of C++* (Stroustrup), cppreference.com

### C — Essential for embedded / bare-metal
- Pointers, manual memory management, bit manipulation
- Memory-mapped I/O, registers, interrupts
- This is what runs on the Pixhawk/STM32 microcontrollers you're using.

### Rust — **The rising star at new defense-tech**
- Anduril uses Rust heavily. Memory safety without garbage collection.
- Ownership/borrowing, lifetimes, traits, `Result`/`Option`, async
- Increasingly used where you'd traditionally use C++ but want safety.

### Python — The glue and tooling language
- Scripting, automation, data analysis, ML, test harnesses
- Ground-station tools, log analysis (you're already doing this with PX4 logs)
- Libraries: NumPy, pandas, asyncio, pymavlink, MAVSDK

### Supporting
- **MATLAB/Simulink** — huge at Boeing/Lockheed for control-law design & model-based development
- **Ada/SPARK** — still in legacy avionics (Boeing, defense). Niche but valued.
- **Go / TypeScript** — backend services and operator UIs at Anduril (Lattice platform)

---

## 4. Embedded & Real-Time Systems (Your Edge)

This is where your PX4/Pixhawk experience is **gold**. Lean into it.

- **Microcontrollers & SoCs:** STM32 (Pixhawk uses these), ARM Cortex-M/R/A
- **RTOS:** NuttX (PX4 runs on it!), FreeRTOS, VxWorks (avionics standard), QNX
- **Bare-metal concepts:** interrupts, DMA, timers, watchdogs
- **Buses & protocols:** I2C, SPI, UART, CAN/DroneCAN, ARINC 429 & MIL-STD-1553 (avionics)
- **Sensor integration:** IMUs, GPS, barometers, magnetometers — sensor fusion
- **Determinism:** worst-case execution time, jitter, hard vs soft real-time
- **Flight stacks:** PX4, ArduPilot, ROS 2 — *you already work in this space*

> Talking point for interviews: "I built/configured a PX4-based autopilot, wrote onboard navigation/policy code, and debugged it against SITL simulation." That's a concrete, relevant story most candidates don't have.

---

## 5. Robotics & Autonomy (Anduril / Skydio / Shield AI Core)

- **ROS / ROS 2** — middleware, nodes, topics, services, DDS
- **State estimation:** Kalman filters (EKF/UKF — PX4's EKF2), sensor fusion
- **Control theory:** PID, LQR, MPC, state-space models
- **Path & motion planning:** A*, RRT/RRT*, Dijkstra, potential fields
- **SLAM:** simultaneous localization and mapping
- **Coordinate frames & transforms:** body/NED/ECEF, quaternions, rotation matrices
- **Computer vision:** OpenCV, object detection, tracking (you have an IMX500 AI camera setup!)
- **ML for perception:** PyTorch/TensorFlow, ONNX, edge inference, model deployment

> The IMX500 inference work in your `tools/hdmi_inference_display.py` is exactly the kind of edge-AI-on-robotics work these companies do.

---

## 6. Safety-Critical & Certified Software (Old-Space Essential)

If targeting Boeing/Lockheed/avionics, know these:

- **DO-178C** — the avionics software certification standard. Design Assurance Levels (DAL A–E). This is the single most important acronym in commercial/military flight software.
- **DO-254** — hardware equivalent
- **ARP4754A** — system development for aircraft
- **MISRA C/C++** — coding standards for safety-critical embedded code
- **AUTOSAR** — automotive but related discipline
- **Requirements traceability:** every line of code traces to a requirement to a test
- **Tools:** DOORS (requirements), VectorCAST/LDRA (test & coverage), static analysis (Coverity, Polyspace)
- **Processes:** AS9100, CMMI, formal V&V (verification & validation), MC/DC test coverage

> You don't need to be an expert, but *knowing this vocabulary* signals you understand why aerospace software is different from a web app.

---

## 7. Software Engineering Practices (Universal)

- **Version control:** Git deeply — branching, rebasing, bisect, code review etiquette
- **Build systems:** CMake (dominant in C++ aerospace — PX4 uses it), Make, Bazel
- **Testing:** unit (GoogleTest, pytest), integration, hardware-in-the-loop (HIL), software-in-the-loop (SITL — you use this!)
- **CI/CD:** GitHub Actions, GitLab CI, Jenkins
- **Debugging:** GDB, JTAG/SWD hardware debuggers, logic analyzers, oscilloscopes, ELF/core dumps
- **Static analysis & sanitizers:** ASan, UBSan, TSan, clang-tidy, cppcheck
- **Containers:** Docker (for build environments and tooling)
- **Linux:** command line fluency, systemd (you have `systemd/` configs), cross-compilation toolchains

---

## 8. Math & Domain Knowledge

- **Linear algebra** — vectors, matrices, transforms (essential for robotics/graphics/control)
- **Calculus & differential equations** — dynamics, control systems
- **Probability & statistics** — sensor noise, estimation, ML
- **Quaternions & rotations** — attitude representation (no gimbal lock)
- **Coordinate systems & geodesy** — WGS84, NED, ECEF, lat/long
- **Signal processing** — filtering, FFT, sampling
- **Physics:** rigid body dynamics, aerodynamics basics, orbital mechanics (for space roles)

---

## 9. System Design (Senior / New-Defense Interviews)

Anduril and SpaceX ask system design even for mid-level roles:

- Designing a real-time telemetry pipeline (drone → ground station)
- Multi-vehicle coordination / swarm architecture
- Sensor fusion pipeline architecture
- Fault tolerance, redundancy, graceful degradation, failsafes
- Latency budgets, throughput, backpressure
- Message buses (DDS, pub/sub), microservices vs monolith
- Trade-offs: edge compute vs cloud, deterministic vs best-effort

> Resource: *Designing Data-Intensive Applications* (Kleppmann) for the backend/distributed side; for robotics, study real autopilot architectures (PX4's modular uORB pub/sub design is a great case study you already have access to).

---

## 10. A Concrete Study Plan

### Phase 1 — Foundations (weeks 1–8)
- Solidify C++ (Effective Modern C++) and one of C or Rust
- LeetCode: Blind 75, focus on arrays/strings/trees/graphs
- Brush up OS concepts (threads, mutexes, memory)

### Phase 2 — Domain Depth (weeks 9–16)
- Deepen embedded/RTOS via your PX4/Pixhawk work — read the PX4 source
- Learn ROS 2 and build a small autonomy project
- Study state estimation (Kalman filter) and control (PID → LQR)
- Read about DO-178C if targeting primes

### Phase 3 — Interview Prep (weeks 17–24)
- LeetCode medium/hard, timed; 2–3 problems/day
- System design practice (telemetry, swarm, fault tolerance)
- Behavioral stories (STAR format) — emphasize ownership, debugging, shipping
- Mock interviews

### Ongoing — Build a Portfolio
- **Your PX4 drone project is your portfolio.** Document it well.
- Contribute to PX4 or ArduPilot open source (huge credibility signal)
- A clean GitHub with real embedded/autonomy work beats a generic web app

---

## 11. Standout Projects (You Already Have Material)

Things that make a defense/aerospace resume pop:
- ✅ A working autonomous drone with custom navigation code ← *you're doing this*
- ✅ Edge AI inference on a camera (IMX500) ← *you're doing this*
- ✅ SITL/HIL simulation testing ← *you have `sitl.md`*
- ✅ systemd-managed onboard services ← *you have this*
- Open-source contributions to PX4/ArduPilot
- A Kalman filter / sensor fusion implementation from scratch
- A path-planning visualizer (A*/RRT)
- A real-time telemetry dashboard

---

## 12. Resume & Application Tips

- **Lead with relevant keywords:** C++, embedded, real-time, RTOS, PX4, ROS 2, autonomy, sensor fusion
- **State citizenship/clearability** clearly (defense recruiters filter on this first)
- **Quantify:** "reduced control loop latency by X ms," "achieved Y Hz update rate"
- **Tailor:** Anduril → emphasize shipping/ownership/systems; Boeing → emphasize rigor/safety/process
- **Apply directly** on their career sites; defense recruiters use clearance/citizenship filters heavily
- **Network:** veterans, alumni, conferences (AUVSI, AIAA), and open-source maintainers

---

## 13. Quick Reference: Acronym Cheat Sheet

| Acronym | Meaning |
|---|---|
| DO-178C | Avionics software certification standard |
| DAL | Design Assurance Level (A–E) |
| MC/DC | Modified Condition/Decision Coverage (test rigor) |
| RTOS | Real-Time Operating System |
| HIL / SITL | Hardware / Software In The Loop |
| EKF/UKF | Extended/Unscented Kalman Filter |
| DDS | Data Distribution Service (ROS 2 middleware) |
| MAVLink | Drone communication protocol |
| NED / ECEF | North-East-Down / Earth-Centered-Earth-Fixed frames |
| ITAR | Int'l Traffic in Arms Regulations (export control) |
| MISRA | Safety-critical C/C++ coding standard |
| V&V | Verification & Validation |
| TS/SCI | Top Secret / Sensitive Compartmented Information |

---

## 14. Curated Resources

**Books**
- *Effective Modern C++* — Scott Meyers
- *A Tour of C++* — Bjarne Stroustrup
- *The Rust Programming Language* (free online) — Klabnik & Nichols
- *Computer Systems: A Programmer's Perspective* (CS:APP)
- *Probabilistic Robotics* — Thrun, Burgard, Fox
- *Designing Data-Intensive Applications* — Martin Kleppmann
- *Cracking the Coding Interview* — McDowell

**Online**
- NeetCode.io / LeetCode (interview prep)
- PX4 & ArduPilot developer docs (you have the PX4 source right here)
- ROS 2 documentation and tutorials
- MIT OCW: 6.832 (Underactuated Robotics), 16.06 (Control)
- cppreference.com

**Communities**
- PX4 / ArduPilot Discord & forums
- r/AerospaceEngineering, r/embedded, r/ControlTheory
- AUVSI, AIAA (professional orgs)

---

### TL;DR
1. **Master C++** (and pick up C or Rust). 
2. **Grind LeetCode** for Anduril/SpaceX-tier interviews. 
3. **Lean into embedded/real-time/autonomy** — your PX4 work is a genuine differentiator. 
4. **Know the safety-cert vocabulary** (DO-178C) for the primes. 
5. **Be clearable** (U.S. citizen, clean record) — it's the biggest gate. 
6. **Ship a real project** — you already have one; document and extend it.

Good luck. You're closer than most candidates because you're already building real flight software.

---

## 15. Deeper Dive: The Modern Defense Software Stack (New)

### 15.1 The middleware & comms layer you'll actually touch
- **DDS (Data Distribution Service)** — the real-time pub/sub backbone of ROS 2
  and many defense systems. Learn QoS policies (reliability, durability,
  deadline), discovery, and why it scales to many nodes.
- **uORB** — PX4's in-process bus (RT-safe, zero-config). Know uORB vs. DDS:
  intra-process flight-critical vs. inter-process/inter-machine.
- **MAVLink2** — message signing, extension fields, the mission/param/command
  sub-protocols. The lingua franca of small UAS.
- **Protobuf / FlatBuffers** — schema'd serialization for services and logs.

### 15.2 Build, deploy, and reproducibility
- **CMake** dominates C++ aerospace (PX4 uses it). Learn targets, toolchain
  files, and cross-compilation for ARM.
- **Bazel** appears at larger software-heavy shops (hermetic, reproducible builds).
- **Yocto / buildroot** for embedded Linux images; **conan/vcpkg** for C++ deps.
- **Containers** for build environments and ground software; know why they're
  usually *not* in the flight-critical path.

### 15.3 Safety-critical software, expanded
- **DO-178C** + supplements: DO-331 (model-based), DO-332 (object-oriented),
  DO-333 (formal methods). DAL A–E maps rigor to failure severity.
- **MISRA C/C++** and **AUTOSAR C++14** coding standards; static analyzers
  (Coverity, Polyspace, clang-tidy) enforce them.
- **Formal methods** are rising: SPARK/Ada, TLA+ for protocol design, model
  checking. Even literacy here is a differentiator.

### 15.4 The AI/ML-on-the-edge layer (the fastest-growing demand)
- Model formats & runtimes: **ONNX**, **TensorRT**, **TFLite**, vendor NPUs
  (Jetson, Hailo, Sony IMX500).
- **Quantization** (PTQ/QAT), pruning, and the latency/accuracy/power triangle.
- **MLOps for the edge**: versioned datasets+models, shadow/canary deploys,
  drift monitoring. See [20-autonomy-ml-ai.md](../autonomy/20-ml-ai.md).

### 15.5 A 90-day sprint to "interview-ready"
1. **Weeks 1–4:** C++ (Tour of C++ → Effective Modern C++); 75 LeetCode (Blind 75).
2. **Weeks 5–8:** Read PX4 source; build one ROS 2 node; implement a Kalman filter.
3. **Weeks 9–12:** System-design reps (telemetry pipeline, swarm); record a demo;
   ship one open-source PR to PX4/ArduPilot.

---

## Sources & Citations

**Books**
- Meyers, S. — *Effective Modern C++*, O'Reilly.
- Stroustrup, B. — *A Tour of C++*, Addison-Wesley.
- Klabnik & Nichols — *The Rust Programming Language* (free): https://doc.rust-lang.org/book
- Bryant & O'Hallaron — *Computer Systems: A Programmer's Perspective*.
- Kleppmann, M. — *Designing Data-Intensive Applications*, O'Reilly.
- Thrun, Burgard, Fox — *Probabilistic Robotics*, MIT Press.
- McDowell, G.L. — *Cracking the Coding Interview*.

**Official docs & standards**
- PX4: https://docs.px4.io  ·  ArduPilot: https://ardupilot.org  ·  ROS 2: https://docs.ros.org
- MAVLink: https://mavlink.io  ·  cppreference: https://cppreference.com
- DDS (OMG spec): https://www.omg.org/spec/DDS  ·  NuttX: https://nuttx.apache.org
- RTCA DO-178C (avionics software) — RTCA/EUROCAE; MISRA: https://misra.org.uk
- ONNX: https://onnx.ai  ·  NVIDIA TensorRT: https://developer.nvidia.com/tensorrt

**Practice & community**
- NeetCode: https://neetcode.io  ·  LeetCode: https://leetcode.com
- PX4 / ArduPilot forums & Discord; AUVSI, AIAA professional orgs.

*Repo references (`onboard/`, `navigation/`, `policy/`, `sitl.md` → now [22-autonomy-px4-sitl.md](../autonomy/22-px4-sitl.md)) point to the author's `pixhawk/drone/` project. Standards evolve — verify against primary sources.*
