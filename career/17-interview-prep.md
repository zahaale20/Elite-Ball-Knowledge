# Technical Interview Preparation

> The interview loop is a separate skill from engineering. You can build a real
> PX4/Pixhawk VTOL autonomy stack and still bomb a LeetCode-hard graph problem
> under a 40-minute clock — because the loop tests *interview performance*, not
> *engineering ability*. This file is the training plan that closes that gap for
> autonomy/robotics/defense-tech roles (Anduril, SpaceX, Skydio, Shield AI,
> Boeing, Lockheed, Northrop). Your `pixhawk/drone/` project is your unfair
> advantage — almost no candidate has a real flight-software story. Here you learn
> to *perform* the technical bar and *weaponize* that project as evidence.

Pair this with [12-career-software-engineering.md](12-software-engineering.md)
(what to learn) and [18-career-resume-portfolio.md](18-resume-portfolio.md)
(how to get the interview in the first place).

---

## 0. Know the Battlefield (Two Cultures, Two Loops)

The single biggest prep mistake is preparing for the wrong loop. Defense
engineering splits in two — same split as
[12-career-software-engineering.md](12-software-engineering.md) §0:

| | **New defense-tech** (Anduril, SpaceX, Skydio, Shield AI) | **Primes** (Boeing, Lockheed, Northrop, RTX) |
|---|---|---|
| Coding bar | **LeetCode medium–hard**, real algorithmic depth | Moderate coding; sometimes language trivia |
| Systems design | **Heavy** — distributed, real-time, robotics systems | Lighter; more architecture/process focus |
| Embedded/C++ | Deep C++/Rust, real-time, performance | Domain + safety process (DO-178C, MISRA) |
| Take-home | Common; a real mini-project | Rare |
| Behavioral | Ownership, ship-fast, "what did *you* build" | Teamwork, process discipline, safety culture |
| Clearance weight | Valued, but bar is technical first | Clearance + domain weigh heavily |

**Strategy:** if you're targeting Anduril/SpaceX, your prep is **80% looks-like-a-
top-tech-company** (DS&A + systems design) **plus** robotics/embedded depth. If
you're targeting primes, shift weight toward **domain + behavioral + safety
process** and keep coding at a solid-medium level.

> Your drone stack helps in *both*, but in different ways: at new-defense it's
> proof you ship hard systems; at primes it's proof you understand flight software
> and real-time constraints.

---

## 1. The Full Loop (What Actually Happens)

A typical autonomy/robotics loop:

1. **Recruiter screen (20–30 min)** — interest, basics, clearance/citizenship,
   logistics. *Not* technical, but it gates everything. (See §10 for the
   clearance answer; details in [16-career-security-clearance.md](16-security-clearance.md).)
2. **Technical phone screen (45–60 min)** — 1–2 coding problems (medium), shared
   editor (CoderPad/HackerRank). Sometimes light system/robotics questions.
3. **Take-home or pair-programming (optional, 2–6 hrs)** — a real mini-project
   (e.g., a path planner, a sensor-fusion node, a small service). Common at
   Anduril/Skydio.
4. **Onsite / virtual onsite (4–6 rounds, full day)**:
   - **2× coding** (medium–hard DS&A)
   - **1× systems design** (distributed and/or robotics-system design)
   - **1× domain deep-dive** (embedded/real-time, controls/estimation, or your
     project — *this is where the drone stack wins*)
   - **1× behavioral / "bar raiser"** (ownership, conflict, judgment)
5. **Debrief & decision** — interviewers write structured feedback; a committee or
   hiring manager decides. Then offer → negotiation
   ([15-career-negotiation-compensation.md](15-negotiation-compensation.md)).

> Each round has a *rubric*. Your job is to produce the **signals** the rubric
> rewards: correct, communicated, tested, and owned.

---

## 2. Data Structures & Algorithms (The Coding Rounds)

This is the round most engineers underperform on relative to their real ability.
Treat it as a sport with drills.

### 2.1 The canonical curriculum
- **Blind 75 / NeetCode 150** — the highest-ROI problem sets. Do Blind 75 *first*
  for breadth, then NeetCode 150 for pattern depth.
- **Target volume:** ~150–250 quality problems with *spaced repetition*, not 600
  problems done once and forgotten. **Re-solve** problems you missed after a week.
- **Quality > quantity:** a problem you can re-derive the optimal solution for and
  explain out loud beats ten you copied.

### 2.2 Patterns to own (in rough priority for autonomy)
| Pattern | Why it matters for autonomy | Example problems |
|---|---|---|
| **Graph BFS/DFS** | Maps, occupancy grids, connectivity | Number of Islands, Course Schedule |
| **Dijkstra / A\*** | **Path planning — your bread and butter** | Network Delay, shortest-path-on-grid |
| **Heaps / priority queues** | A* open set, top-K, scheduling | Kth Largest, Merge K Lists |
| **Two pointers / sliding window** | Stream/window processing, sensor buffers | Longest Substring, Min Window |
| **Binary search** | Tuning thresholds, search over answer | Koko Eating Bananas, rotated array |
| **Dynamic programming** | Optimal sequences, cost-to-go | Coin Change, Edit Distance |
| **Backtracking** | Constraint search, combinatorics | Subsets, N-Queens |
| **Hash maps / sets** | Dedup, memo, O(1) lookup | Two Sum, Group Anagrams |
| **Intervals** | Time windows, sensor/mission scheduling | Merge Intervals, Meeting Rooms |
| **Union-Find** | Connectivity, clustering | Number of Provinces, Redundant Connection |

### 2.3 A\* deserves its own section (autonomy edge)
You should be able to write **Dijkstra and A\*** from memory, explain the
admissibility/consistency of a heuristic, and discuss why A* with a good heuristic
expands fewer nodes. This is the rare topic where your domain and the interview
*perfectly* overlap — and a path-planning question is highly likely in an autonomy
loop.

```python
import heapq

def a_star(start, goal, neighbors, heuristic):
    """Return the lowest-cost path from start to goal.

    neighbors(n) yields (next_node, step_cost).
    heuristic(n) must be admissible (never overestimate true cost-to-goal)
    and ideally consistent (monotone) for optimal, non-re-expanding search.
    """
    # Frontier ordered by f = g + h; store (f, g, node).
    open_heap = [(heuristic(start), 0, start)]
    came_from = {}
    g_score = {start: 0}          # Best known cost from start to each node.

    while open_heap:
        f, g, node = heapq.heappop(open_heap)
        if node == goal:
            return _reconstruct(came_from, node)
        # Skip stale heap entries left behind by a better relaxation.
        if g > g_score.get(node, float("inf")):
            continue
        for nxt, step in neighbors(node):
            tentative = g + step
            if tentative < g_score.get(nxt, float("inf")):
                came_from[nxt] = node
                g_score[nxt] = tentative
                heapq.heappush(open_heap, (tentative + heuristic(nxt), tentative, nxt))
    return None                    # No path exists.

def _reconstruct(came_from, node):
    path = [node]
    while node in came_from:
        node = came_from[node]
        path.append(node)
    return path[::-1]
```

> Be ready to discuss: what happens if the heuristic overestimates (you lose
> optimality), grid vs. graph neighbors (4- vs. 8-connected, diagonal cost),
> Manhattan vs. Euclidean vs. octile heuristics, and how this connects to your
> drone's planner. That last sentence is the move — **anchor textbook A\* to your
> real stack.**

### 2.4 The communication protocol (this is graded as much as the code)
Run **every** coding problem through this loop out loud:

1. **Clarify** — restate the problem; ask about input size, ranges, duplicates,
   empties, expected complexity. (Interviewers reward this.)
2. **Examples** — work a small example by hand; define the expected output.
3. **Approach first, code second** — state a brute force, then optimize, **state
   the target complexity before coding.** Get a nod.
4. **Code cleanly** — meaningful names, small helpers, talk as you type.
5. **Test** — walk your own code on the example, then edge cases (empty, single,
   max, negative, cycles). **Find your own bugs before they do.**
6. **Analyze** — state final time/space, and mention a tradeoff or follow-up.

> Silence is the killer. A correct solution typed in silence scores worse than a
> slightly-imperfect solution narrated clearly. They are hiring a *collaborator*.

### 2.5 Language for the coding round
Use the language you're **fastest and cleanest** in under pressure — usually
**Python** for raw DS&A speed, even at C++/Rust shops, *unless* the role
explicitly tests C++/embedded (then see §4). Know your chosen language's standard
library cold (`heapq`, `collections.deque`, `defaultdict`, `bisect`, sorting keys).

---

## 3. Systems Design (The Round That Separates Levels)

Systems design is where **senior** signal lives. For autonomy/defense you'll see
two flavors — **distributed-systems** design and **robotics-system** design.

### 3.1 The universal framework
1. **Requirements** — functional (what it does) + non-functional (scale, latency,
   throughput, availability, consistency). **Always ask for numbers.**
2. **Estimate** — back-of-envelope: QPS, data volume, bandwidth, storage.
3. **API / interfaces** — define the contracts first.
4. **High-level architecture** — boxes and arrows; data flow.
5. **Deep dive** — pick the hard part (the interviewer will steer) and go deep:
   data model, partitioning, caching, queues, failure modes.
6. **Bottlenecks & tradeoffs** — name them; discuss scaling, consistency,
   redundancy. **Tradeoffs are the whole point.**

### 3.2 Distributed-systems building blocks to know cold
- **CAP / PACELC**, consistency models (strong, eventual), idempotency.
- **Load balancing, caching (write-through/back), CDNs.**
- **Queues & streams** (Kafka-style), back-pressure, at-least/at-most/exactly-once.
- **Databases** — SQL vs. NoSQL, indexing, sharding, replication, leader election.
- **Serialization** — Protobuf/FlatBuffers (you already touch MAVLink), schema
  evolution.
- **Observability** — metrics, logs, tracing; SLOs.

### 3.3 Robotics / autonomy system design (your home turf)
Prepare to design things like:
- **A real-time telemetry & C2 pipeline** for a fleet of drones (uplink/downlink,
  MAVLink over UDP, lossy links, prioritization, store-and-forward).
- **An onboard autonomy architecture** — perception → state estimation → planning →
  control loop, with timing budgets and a safety/abort path. *You literally built
  a version of this.*
- **A multi-vehicle / swarm coordination** system — task allocation, deconfliction,
  comms-degraded operation.
- **A SITL/HITL test & data pipeline** — log capture, replay, regression.

For each, drive the discussion toward what makes **real-time + safety-critical +
comms-degraded** systems special:
- **Determinism & latency budgets** — control loops have hard deadlines; you can't
  GC-pause a flight controller.
- **Graceful degradation** — GPS-denied fallback, link loss → loiter/RTL, sensor
  dropout handling. (Tie to your GPS-denied nav work.)
- **Safety gating** — your **constitution-gated policy** is a *perfect* design
  story: a policy layer that vetoes unsafe commands before actuation. Bring it up.

> Move that wins the round: when asked to design an autonomy system, **narrate the
> architecture you actually built** (PX4 + Pi 5 companion, onboard FastAPI service,
> perception, GPS-denied nav, constitution gate), then generalize it. You're
> designing from memory, not improvising.

### 3.4 Worked mini-example: "Design a drone fleet telemetry service"
- **Requirements:** N=500 drones, 10 Hz telemetry each → ~5k msgs/s; lossy
  cellular/RF links; operators need <1s freshness; must survive link drops.
- **Estimate:** 5k msg/s × ~200 B ≈ 1 MB/s ingest; spikes ×3 on reconnection.
- **Architecture:** drone → MAVLink/UDP → edge gateway (per-region) → message
  broker (partition by drone-id) → stream processor (state, geofence, health) →
  time-series store + live websocket to operator UI; command path is separate,
  authenticated, idempotent, with ACK/timeout.
- **Deep dive:** back-pressure when a region floods; **prioritize** safety msgs
  (low battery, geofence breach) over routine position; **store-and-forward** on
  the drone for link loss; exactly-once-ish command semantics via dedup keys.
- **Tradeoffs:** UDP (low latency, lossy) vs. TCP (reliable, head-of-line); per-
  drone partition (ordering) vs. rebalancing cost; strong vs. eventual consistency
  for the fleet view.

---

## 4. Embedded, Real-Time & C++ Specifics

If the role is flight software / firmware / autonomy runtime (very common at
Anduril/Skydio/Shield AI and all primes), expect a dedicated round. This is
**your moat** — most web-trained candidates can't do it.

### 4.1 C++ topics they probe
- **RAII & ownership** — `unique_ptr`/`shared_ptr`, rule of 0/3/5, move semantics,
  why you avoid raw `new`/`delete`.
- **The memory model** — stack vs. heap, alignment, `const`/`constexpr`, references
  vs. pointers, dangling, lifetime.
- **Real-time discipline** — **no dynamic allocation in hot paths**, no unbounded
  locks, avoiding priority inversion, deterministic worst-case execution time.
- **Undefined behavior** — common UB traps and why they matter in safety code.
- **Concurrency** — `std::atomic`, memory ordering (relaxed/acquire/release),
  lock-free ring buffers, condition variables, false sharing.
- **Templates/STL** — enough to be fluent; not metaprogramming gymnastics.

### 4.2 Embedded/RTOS topics
- **Interrupts, DMA, timers, watchdogs**; ISR constraints (no blocking, minimal
  work).
- **Buses:** I2C/SPI/UART/CAN(DroneCAN), and avionics buses **ARINC 429 /
  MIL-STD-1553** (name-drop for primes).
- **RTOS scheduling** — preemptive priority scheduling, **rate-monotonic**,
  priority inheritance; **NuttX** (PX4 runs on it — you know this!), FreeRTOS,
  VxWorks/QNX (avionics).
- **Fixed vs. floating point**, endianness, bit manipulation, register-level I/O.
- **Sensor fusion** — IMU/GPS/baro/mag; the bridge to §5.

### 4.3 Classic embedded interview questions (be ready)
- "Implement a **lock-free single-producer/single-consumer ring buffer**."
- "Set/clear/toggle a specific **bit** in a register" (`reg |= (1u << n)` etc.).
- "What's `volatile` for, and what does it *not* guarantee?" (visibility, not
  atomicity).
- "Why avoid `malloc` in a control loop?" (nondeterministic latency,
  fragmentation).
- "Debounce a button / handle an ISR safely."
- "Detect endianness; convert network↔host order."

> Anchor every answer to your stack: "On the Pixhawk side I'm working against
> NuttX with hard-real-time constraints; on the Pi 5 companion I run the FastAPI
> service where soft-real-time and Python are fine — and I keep the hard-real-time
> work off the companion deliberately." That sentence demonstrates *judgment*, not
> just knowledge.

---

## 5. Robotics, Controls & Estimation Round

For autonomy roles specifically, expect math-y robotics questions. Depth scales
with seniority and whether the role is GNC/controls vs. software.

### 5.1 Controls
- **PID** — what each term does, tuning intuition, integral windup, derivative
  noise, why you filter D. (You tune this on the drone — speak from experience.)
- **State-space** — `x' = Ax + Bu`, controllability/observability at a concept
  level; LQR as "optimal full-state feedback."
- **Stability** — poles, gain/phase margin, Nyquist intuition.
- **Discretization** — control loops run at fixed rate; sampling, aliasing, the
  effect of loop rate on stability.
Cross-link: [25-autonomy-control-theory.md](../autonomy/25-control-theory.md) and
[28-autonomy-gnc.md](../autonomy/28-gnc.md).

### 5.2 Estimation / sensor fusion
- **Kalman filter** — predict/update, what the covariance means, why you fuse
  IMU + GPS, EKF for nonlinear (attitude/position). Be able to *sketch* the
  predict/update equations and explain process vs. measurement noise.
- **GPS-denied navigation** — dead reckoning drift, visual/inertial odometry,
  why integration of IMU drifts, loop closure. (Your **GPS-denied nav** work is a
  direct talking point — and a differentiator most candidates lack. See
  [26-autonomy-gnss-jamming-spoofing.md](../autonomy/26-gnss-jamming-spoofing.md).)
- **Frames & transforms** — body vs. world frame, rotation matrices, quaternions
  (and why quaternions over Euler — gimbal lock), homogeneous transforms.

### 5.3 Planning
- **Search:** Dijkstra/A\* (§2.3), D*/D*-Lite for replanning, RRT/RRT* for
  continuous spaces, potential fields.
- **Trajectory generation** — feasibility, smoothness, dynamic constraints.
- Cross-link: [29-autonomy-planning-decision.md](../autonomy/29-planning-decision.md).

### 5.4 Sample questions
- "Why a quaternion instead of Euler angles for attitude?"
- "Your GPS drops out for 30 s — what does your estimator do, and how bad is the
  drift?"
- "Tune a position loop: outer position → velocity → inner attitude. Walk the
  cascade."
- "EKF vs. UKF vs. particle filter — when would you pick each?"

---

## 6. The Take-Home Project

Common at new-defense (Anduril/Skydio). It's a *gift* — unlimited thinking time,
your tools, your environment. Treat it like production work.

### 6.1 What they're grading
- **Correctness** + **clean, readable code** + **tests** + **a clear README** +
  **good judgment about scope** (you didn't over- or under-build).

### 6.2 Execution checklist
- [ ] Read the prompt twice; **list assumptions** explicitly in the README.
- [ ] Build the **simplest correct version first**, then improve.
- [ ] **Write tests** — unit + a couple of integration/edge cases. (This is a
      differentiator; many candidates skip it. Per your own standard, design tests
      across unit, integration, and exploratory levels and call out the **risks**
      each test prevents.)
- [ ] **README:** how to run, design decisions, tradeoffs, what you'd do with more
      time, known limitations.
- [ ] **Clean git history**; meaningful commit messages.
- [ ] Match their stack if specified (C++/Rust/Python/ROS 2).
- [ ] Time-box it; **note** where you stopped and why rather than silently
      cutting corners.

> Your `pixhawk/drone/` repo is essentially a perpetual take-home. The habits you
> build there (README quality, tests, constitution-gated safety) are exactly what
> wins a take-home. See [18-career-resume-portfolio.md](18-resume-portfolio.md).

---

## 7. Behavioral / STAR (Where Your Drone Stack Wins)

Behavioral rounds decide level and "would I work with this person." For
new-defense, the themes are **ownership, bias-to-action, shipping under
ambiguity**; for primes, **teamwork, process, safety**.

### 7.1 STAR structure
- **Situation** — brief context.
- **Task** — what *you* specifically owned.
- **Action** — what *you* did (use "I", not "we"; be specific and technical).
- **Result** — outcome, ideally **quantified**, plus what you learned.

### 7.2 Pre-write your stories from the real stack
Build a **brag doc** of 8–10 STAR stories. Many can come straight from the drone
project:

| Theme | Story seed from your stack |
|---|---|
| **Ownership / shipped under ambiguity** | "Built an onboard FastAPI autonomy service from scratch on the Pi 5 companion, defined the interface to PX4, got it flying in SITL then on hardware." |
| **Debugging a hard problem** | "Diagnosed a GPS-denied drift/estimator issue; isolated it with log replay against SITL; fixed and added a regression check." |
| **Safety / judgment** | "Designed a constitution-gated policy layer that vetoes unsafe commands before actuation — chose to fail safe (loiter/RTL) on policy violation." |
| **Real-time tradeoff** | "Kept hard-real-time work on the flight controller (NuttX) and soft-real-time on the companion; explained the determinism reasoning." |
| **Testing / quality** | "Built a SITL test scaffold so I could validate behavior changes without risking the airframe." |
| **Learning fast** | "Came up the PX4/MAVLink stack solo; read the source to understand the control pipeline." |
| **Conflict / feedback** | (a real interpersonal example — keep one non-drone story) |
| **Failure** | "An early flight test failed because X; here's the root cause and the process change I made." |

> The differentiator: most candidates' behavioral stories are abstract ("I
> collaborated on a feature"). Yours are **"I built a flying autonomous system and
> here's the engineering judgment I exercised."** That is *memorable* and *senior*.

### 7.3 Behavioral pitfalls
- Don't say "we" when it was you (or "I" when it was the team — be honest).
- Don't ramble — STAR keeps you tight (aim ~2 minutes/story).
- Have a **real failure** story with genuine learning. "I'm a perfectionist" is a
  non-answer.
- For primes: emphasize **safety culture and process**; for new-defense: emphasize
  **ownership and shipping**.

---

## 8. Company-Specific Calibration

| Company | What to expect | How to prep |
|---|---|---|
| **Anduril** | LeetCode medium–hard, strong systems design, Rust/C++ depth, ownership-heavy behavioral; take-homes common | Full DS&A + systems design + your robotics depth; lean hard on shipped-autonomy stories |
| **SpaceX** | Genuinely hard coding, fast pace, intense "why" probing, real-time/embedded for flight software | Hard LeetCode, embedded/C++, be ready for rapid-fire follow-ups and "first-principles" questions |
| **Skydio** | Robotics/CV-heavy, autonomy systems, take-home; practical | Estimation/perception/planning depth; clean take-home |
| **Shield AI** | Autonomy/AI for GPS-denied flight — *your exact niche* | GPS-denied nav, estimation, planning; your drone stack is on-point |
| **Boeing / Lockheed / Northrop** | Moderate coding, domain + behavioral + safety process, clearance weight | Domain depth (avionics buses, DO-178C awareness), behavioral/process, clearance line ready |

Cross-link [11-career-defense-aerospace-playbook.md](11-defense-aerospace-playbook.md)
for company-by-company context.

---

## 9. The Study Schedule

A focused **8–12 week** plan (compress/expand to taste). Assumes ~10–15 hrs/week.

### Weeks 1–2 — Foundations & baseline
- [ ] Set up CoderPad-style practice; pick your interview language.
- [ ] **Blind 75**, patterns 1–5 (arrays/strings, hashing, two-pointers, sliding
      window, binary search). ~3–4 problems/day, narrated out loud.
- [ ] One **mock** to find your weak spots.

### Weeks 3–4 — Graphs, trees, A\*
- [ ] Trees/heaps, **graph BFS/DFS**, **Dijkstra/A\*** until you can write A* cold.
- [ ] Re-solve Week 1 misses (spaced repetition).
- [ ] Start the **brag doc** (8–10 STAR stories from the drone stack, §7.2).

### Weeks 5–6 — DP, systems design intro
- [ ] DP + backtracking patterns.
- [ ] **Systems design** framework (§3) + 3 designs, including the **drone fleet
      telemetry** one (§3.4).
- [ ] 1–2 mocks (one coding, one design).

### Weeks 7–8 — Domain depth (your edge)
- [ ] **Embedded/C++** drills (§4.3) and **estimation/controls** review (§5).
- [ ] Prepare your **project deep-dive** narrative (architecture diagram of the
      drone stack you can whiteboard from memory).
- [ ] Mock the **behavioral** round.

### Weeks 9–12 — Polish & simulate
- [ ] Full **mock onsites** (coding + design + domain + behavioral) end-to-end.
- [ ] Re-solve the ~30 problems you've missed most.
- [ ] Tighten company-specific prep (§8) for your top targets.
- [ ] Lock your **clearance/citizenship** answer (§10).

> Consistency beats cramming. Daily reps with spaced repetition and **out-loud
> narration** is the whole game.

---

## 10. Screening & Logistics Answers

- **Clearance/citizenship (recruiter screen):** keep it short and honest. *"I'm a
  U.S. citizen, clearable, and happy to undergo a background investigation"* — or
  if you hold one, *"I have an active Secret/TS."* **Never** discuss classified
  details of past work. Full guidance:
  [16-career-security-clearance.md](16-security-clearance.md) §12.
- **Comp question (recruiter screen):** deflect to range/research; don't anchor low.
  See [15-career-negotiation-compensation.md](15-negotiation-compensation.md) §4.
- **"Tell me about yourself":** 60–90 seconds — who you are, the **drone stack** as
  your headline proof, what you want next. Practice it until it's automatic.
- **Logistics:** test your camera/mic/editor before virtual onsites; have water,
  a notepad, and your architecture sketch nearby (for design/project rounds).

---

## 11. Mock-Interview Discipline

You cannot self-assess interview *performance* — you need reps under observation.

- **Frequency:** ≥1 mock/week from Week 1; ramp to full mock onsites by Weeks 9–12.
- **Sources:** Pramp/interviewing.io (peer/pro mocks), a friend who interviews,
  or record yourself solving a problem and watch it back (painful, effective).
- **Grade against the rubric:** Did you clarify? Narrate? State complexity before
  coding? Test your own code? Stay collaborative when stuck?
- **The "stuck" protocol:** when blocked, **say what you're thinking**, propose a
  brute force, ask a clarifying question, or simplify the problem. Visible problem-
  solving under pressure is itself the signal — silence and freezing are the
  failure.
- **Debrief every mock:** write 3 things to fix; verify they're fixed next time.

---

## 12. The Day-Of Checklist

- [ ] Sleep > cramming the night before.
- [ ] Warm up with 1 easy problem to get the engine running.
- [ ] Re-read your **brag doc** and **"tell me about yourself."**
- [ ] Have your **drone stack architecture sketch** ready to whiteboard.
- [ ] Water, quiet room, tested A/V (virtual) or arrive early (onsite).
- [ ] For each round: **clarify → plan → narrate → test → reflect.**
- [ ] Prepare **3 questions per interviewer** (about the team, the autonomy
      problems, what success looks like — shows ownership).
- [ ] After: jot what was asked while fresh (helps future loops & negotiation).

---

## 13. How This Connects to the Rest of the Curriculum

- [12-career-software-engineering.md](12-software-engineering.md) — *what*
  to learn; this file is *how to perform it under the clock.*
- [18-career-resume-portfolio.md](18-resume-portfolio.md) — gets you the
  interview; the loop converts it to an offer.
- [16-career-security-clearance.md](16-security-clearance.md) — the gate
  that runs in parallel with the loop.
- [15-career-negotiation-compensation.md](15-negotiation-compensation.md) —
  what to do the moment you pass the loop.
- Autonomy band: [22-autonomy-px4-sitl.md](../autonomy/22-px4-sitl.md),
  [23-autonomy-onboard-system.md](../autonomy/23-onboard-system.md),
  [25-autonomy-control-theory.md](../autonomy/25-control-theory.md),
  [26-autonomy-gnss-jamming-spoofing.md](../autonomy/26-gnss-jamming-spoofing.md),
  [28-autonomy-gnc.md](../autonomy/28-gnc.md),
  [29-autonomy-planning-decision.md](../autonomy/29-planning-decision.md) — the
  technical substance behind your domain rounds.
- [04-foundations-modern-cpp-realtime.md](../foundations/04-modern-cpp-realtime.md) —
  the C++/real-time depth for §4.
- [02-ten-year-mastery-plan.md](../foundations/02-ten-year-mastery-plan.md) — slot interview prep
  as a recurring "sharpen the saw" sprint before each job search.

---

## Sources & Citations

**Practice platforms & problem sets**
- NeetCode (Blind 75 / NeetCode 150, patterns): https://neetcode.io
- LeetCode: https://leetcode.com
- interviewing.io (mock interviews, write-ups): https://interviewing.io
- Pramp (peer mocks): https://www.pramp.com

**Books**
- McDowell, G.L. — *Cracking the Coding Interview*, CareerCup.
- *System Design Interview* (Alex Xu), Vol. 1 & 2.
- Kleppmann, M. — *Designing Data-Intensive Applications*, O'Reilly.
- Meyers, S. — *Effective Modern C++*, O'Reilly.
- Thrun, Burgard, Fox — *Probabilistic Robotics*, MIT Press (estimation/planning).
- LaValle, S. — *Planning Algorithms* (free): http://lavalle.pl/planning/

**Domain & docs**
- PX4: https://docs.px4.io  ·  ROS 2: https://docs.ros.org  ·  MAVLink: https://mavlink.io
- NuttX: https://nuttx.apache.org
- A\* / search references — Red Blob Games (excellent visual intro):
  https://www.redblobgames.com/pathfinding/a-star/introduction.html

**Company engineering context**
- Anduril: https://www.anduril.com  ·  SpaceX: https://www.spacex.com/careers
- Skydio: https://www.skydio.com  ·  Shield AI: https://shield.ai

*This is personal career guidance reflecting the author's goals and publicly
available information. Interview formats, difficulty, and company processes change
frequently — confirm specifics with your recruiter and the companies' current
careers pages.*
