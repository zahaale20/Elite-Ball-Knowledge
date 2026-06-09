# Technical Interview Preparation

> The interview loop is a separate skill from engineering. You can build a real
> production system and still bomb a LeetCode-hard graph problem under a 40-minute
> clock — because the loop tests *interview performance*, not *engineering
> ability*. This file is the training plan that closes that gap for software and
> engineering roles across the industry. A real, substantial project you built and
> can speak to deeply is your unfair advantage — almost no candidate can narrate a
> system they truly own end to end. Here you learn to *perform* the technical bar
> and *weaponize* that project as evidence.

Pair this with [03-career-software-engineering.md](03-software-engineering.md)
(what to learn) and [09-career-resume-portfolio.md](09-resume-portfolio.md)
(how to get the interview in the first place).

---

## 0. Know the Battlefield (Different Companies, Different Bars)

The single biggest prep mistake is preparing for the wrong loop. The interview
bar varies by company *type*, not just by company — mirroring the split in
[03-career-software-engineering.md](03-software-engineering.md) §0:

| | **Big Tech / FAANG-style** | **Startups / scale-ups** | **Large traditional enterprises** |
|---|---|---|---|
| Coding bar | **LeetCode medium–hard**, real algorithmic depth | Medium, but pragmatic; ship-fast bias | Moderate; sometimes language/framework trivia |
| Systems design | **Heavy** — distributed systems at scale | Moderate–heavy; pragmatic architecture | Lighter; more architecture/process focus |
| Take-home | Rare (mostly live coding) | **Common** — a real mini-project | Rare |
| Behavioral | Structured, leveling-focused, "bar raiser" | Ownership, scrappiness, "what did *you* build" | Teamwork, process discipline, stakeholder mgmt |
| What's weighted | Breadth + depth + level calibration | Impact + speed + product sense | Domain experience + reliability + process |

**Strategy:** for **big tech**, your prep is **80% DS&A + systems design** done to
a high, well-calibrated bar. For **startups/scale-ups**, keep coding at a solid
medium and lean into a clean take-home plus ownership stories. For **large
enterprises**, shift weight toward **domain experience, behavioral, and process**
and keep coding at a solid-medium level. (Some roles add gating screens — e.g.,
clearance or citizenship in regulated industries; treat those as a logistics check
in §10, not the center of your prep.)

> A substantial project you built helps in *all three* contexts, in different ways:
> at big tech it's proof you can reason about real systems; at a startup it's proof
> you ship; at an enterprise it's proof you understand production constraints.

---

## 1. The Full Loop (What Actually Happens)

A typical software-engineering loop:

1. **Recruiter screen (20–30 min)** — interest, basics, logistics, and any role
   gating (location, work authorization, and in regulated industries sometimes
   clearance/citizenship). *Not* technical, but it gates everything. (See §10 for
   the screening answers; if a role needs clearance, see the optional aside in
   [07-career-security-clearance.md](07-security-clearance.md).)
2. **Technical phone screen (45–60 min)** — 1–2 coding problems (medium), shared
   editor (CoderPad/HackerRank). Sometimes light system-design questions.
3. **Take-home or pair-programming (optional, 2–6 hrs)** — a real mini-project
   (e.g., a small service, a parser, a CLI, a data pipeline). Common at
   startups/scale-ups.
4. **Onsite / virtual onsite (4–6 rounds, full day)**:
   - **2× coding** (medium–hard DS&A)
   - **1× systems design** (distributed-systems design)
   - **1× project / domain deep-dive** (a system you built — *this is where a deep
     project wins*)
   - **1× behavioral / "bar raiser"** (ownership, conflict, judgment)
5. **Debrief & decision** — interviewers write structured feedback; a committee or
   hiring manager decides. Then offer → negotiation
   ([06-career-negotiation-compensation.md](06-negotiation-compensation.md)).

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

### 2.2 Patterns to own (in rough priority)
| Pattern | Why it matters | Example problems |
|---|---|---|
| **Graph BFS/DFS** | Connectivity, traversal, dependency graphs | Number of Islands, Course Schedule |
| **Dijkstra / A\*** | Shortest paths, weighted routing | Network Delay, shortest-path-on-grid |
| **Heaps / priority queues** | Top-K, scheduling, merge | Kth Largest, Merge K Lists |
| **Two pointers / sliding window** | Stream/window processing, substring search | Longest Substring, Min Window |
| **Binary search** | Search over sorted data or answer space | Koko Eating Bananas, rotated array |
| **Dynamic programming** | Optimal sequences, cost minimization | Coin Change, Edit Distance |
| **Backtracking** | Constraint search, combinatorics | Subsets, N-Queens |
| **Hash maps / sets** | Dedup, memo, O(1) lookup | Two Sum, Group Anagrams |
| **Intervals** | Time windows, scheduling, merging | Merge Intervals, Meeting Rooms |
| **Union-Find** | Connectivity, clustering | Number of Provinces, Redundant Connection |

### 2.3 A\* deserves its own section (shortest-path depth)
You should be able to write **Dijkstra and A\*** from memory, explain the
admissibility/consistency of a heuristic, and discuss why A* with a good heuristic
expands fewer nodes. Shortest-path and weighted-graph questions show up often, and
this is a high-leverage topic to have cold.

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
> Manhattan vs. Euclidean vs. octile heuristics, and where you'd actually use this
> (routing, maps, dependency resolution). If your project touched pathfinding or
> graph search, the move is to **anchor textbook A\* to your real system.**

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

Systems design is where **senior** signal lives. Most loops focus on
**distributed-systems** design — services, data stores, queues, and the tradeoffs
that hold them together at scale.

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
- **Serialization** — JSON, Protobuf/FlatBuffers, schema evolution and
  backward/forward compatibility.
- **Observability** — metrics, logs, tracing; SLOs.

### 3.3 Common systems-design prompts to prepare
Prepare to design things like:
- **A URL shortener / pastebin** — write/read paths, key generation, caching,
  read-heavy scaling.
- **A real-time event-ingestion pipeline** — high-throughput producers, a message
  broker, stream processing, and a live dashboard.
- **A news feed / notification system** — fan-out on write vs. read, ranking,
  delivery guarantees.
- **A rate limiter / API gateway** — token bucket, distributed counters, fairness.
- **A chat or presence service** — websockets, fan-out, ordering, offline delivery.

For each, drive the discussion toward the tradeoffs that separate levels:
- **Throughput & latency budgets** — where the hot path is and how you keep it fast.
- **Graceful degradation** — what happens under partial failure, retries, timeouts,
  back-pressure, and circuit breakers.
- **Correctness under failure** — idempotency, exactly-once-ish semantics via dedup
  keys, and consistency choices.

> Move that wins the round: when asked to design a system in a space you've
> actually worked in, **narrate the architecture you really built**, then
> generalize it. Designing from memory beats improvising from scratch.

### 3.4 Worked mini-example: "Design a real-time event-ingestion service"
- **Requirements:** N=500 producers, 10 events/s each → ~5k msgs/s; lossy network
  links; consumers need <1s freshness; must survive client disconnects.
- **Estimate:** 5k msg/s × ~200 B ≈ 1 MB/s ingest; spikes ×3 on reconnection.
- **Architecture:** client → HTTP/UDP → edge gateway (per-region) → message
  broker (partition by client-id) → stream processor (validation, aggregation,
  health) → time-series store + live websocket to a dashboard; the command/control
  path is separate, authenticated, idempotent, with ACK/timeout.
- **Deep dive:** back-pressure when a region floods; **prioritize** high-value
  events over routine ones; **store-and-forward** on the client for link loss;
  exactly-once-ish semantics via dedup keys.
- **Tradeoffs:** UDP (low latency, lossy) vs. TCP (reliable, head-of-line); per-
  client partition (ordering) vs. rebalancing cost; strong vs. eventual consistency
  for the aggregate view.

---

## 4. Language, Concurrency & Low-Level Rounds

Some roles — backend, systems, infrastructure, embedded, or performance-sensitive
work — add a round that probes **deep language knowledge, concurrency, and memory**.
This is where specialists separate from generalists; if your target roles are in
this space, prepare it deliberately. (If they aren't, this section is optional.)

### 4.1 Memory & language fundamentals
- **Ownership & lifetimes** — how your language manages memory (GC vs. manual vs.
  ownership/borrowing); in C++/Rust: RAII, smart pointers, move semantics, rule of
  0/3/5, why you avoid raw `new`/`delete`.
- **The memory model** — stack vs. heap, alignment, `const`/`constexpr`, references
  vs. pointers, dangling references, object lifetime.
- **Undefined behavior** — common traps and why they matter in production code.
- **Templates/generics & the standard library** — enough to be fluent; not
  metaprogramming gymnastics.

### 4.2 Concurrency & performance
- **Threads & synchronization** — mutexes, condition variables, deadlock,
  starvation, priority inversion.
- **Atomics & memory ordering** — `relaxed`/`acquire`/`release`, lock-free
  structures (e.g., a single-producer/single-consumer ring buffer), false sharing.
- **Avoiding allocation in hot paths** — why unbounded allocation or locking hurts
  tail latency; pooling and pre-allocation.
- **Profiling & optimization** — measure before optimizing; cache effects, big-O
  vs. constant factors.

### 4.3 Classic low-level interview questions (be ready)
- "Implement a **lock-free single-producer/single-consumer ring buffer**."
- "Set/clear/toggle a specific **bit** in an integer" (`x |= (1u << n)` etc.).
- "What's `volatile` for in C/C++, and what does it *not* guarantee?" (visibility,
  not atomicity).
- "Why avoid allocation in a latency-critical loop?" (nondeterministic latency,
  fragmentation).
- "Explain a data race and how you'd fix it."
- "Convert between network and host byte order; detect endianness."

> Anchor every answer to real experience: "In a service I built, I kept the
> allocation off the hot path and pre-sized the buffers, because tail latency
> mattered more than peak throughput." That kind of sentence demonstrates
> *judgment*, not just knowledge.

---

## 5. The Project Deep-Dive Round

Most loops include a round where an interviewer asks you to walk through something
**you actually built** — a side project, an open-source contribution, a production
system, or a portfolio piece. This is the round where a deep project becomes your
unfair advantage: you're the world expert in the room on your own system.

### 5.1 What they're really testing
- **Depth** — can you go three "why?"s deep on any decision without hand-waving?
- **Tradeoffs** — did you choose deliberately, or cargo-cult? Can you name what you
  gave up?
- **Ownership** — did *you* build it, and do you understand the parts you didn't
  write?
- **Communication** — can you explain a complex system to someone who's never seen
  it, at the right level of abstraction?

### 5.2 Prepare a structured walkthrough
Have this ready to whiteboard from memory:
- **The one-line "what and why"** — the problem and who it's for.
- **An architecture diagram** — the major components and how data flows between
  them. Practice drawing it in under two minutes.
- **The hardest problem you solved** — the bug, the bottleneck, or the design
  decision that took real thought, and how you worked through it.
- **Key tradeoffs** — the 2–3 decisions where you chose A over B, and why.
- **What you'd do differently** — shows reflection and growth, not defensiveness.

### 5.3 Sample questions to rehearse
- "Walk me through the architecture. Where would it break first under load?"
- "Why did you choose that database / framework / language?"
- "What was the hardest bug, and how did you find the root cause?"
- "If you had two more weeks, what would you build or fix?"
- "What part are you least happy with, and why?"

> The differentiator: most candidates describe projects abstractly ("I worked on a
> feature"). You should be able to **trace a request end to end through a system you
> own**, name every tradeoff, and defend (or critique) each one. That depth reads as
> *senior*.

---

## 6. The Take-Home Project

Common at startups and scale-ups. It's a *gift* — unlimited thinking time,
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
- [ ] Match their stack if specified (the language/framework they name).
- [ ] Time-box it; **note** where you stopped and why rather than silently
      cutting corners.

> A substantial project you maintain is essentially a perpetual take-home. The
> habits you build there (README quality, tests, clean commits, deliberate scope)
> are exactly what wins a take-home. See
> [09-career-resume-portfolio.md](09-resume-portfolio.md).

---

## 7. Behavioral / STAR (Where a Deep Project Wins)

Behavioral rounds decide level and "would I work with this person." At
startups, the themes are **ownership, bias-to-action, shipping under
ambiguity**; at large enterprises, **teamwork, process, and stakeholder
management**; at big tech, structured **leadership-principle-style** probing.

### 7.1 STAR structure
- **Situation** — brief context.
- **Task** — what *you* specifically owned.
- **Action** — what *you* did (use "I", not "we"; be specific and technical).
- **Result** — outcome, ideally **quantified**, plus what you learned.

### 7.2 Pre-write your stories from a real project
Build a **brag doc** of 8–10 STAR stories. Many can come straight from a
substantial project you built:

| Theme | Story seed from a project you own |
|---|---|
| **Ownership / shipped under ambiguity** | "Built a service from scratch, defined its interfaces, and took it from prototype to running in production." |
| **Debugging a hard problem** | "Diagnosed an intermittent failure; isolated it with logging and a reproducible test; fixed it and added a regression check." |
| **Design / judgment** | "Designed a safeguard layer that rejects invalid operations before they commit — chose to fail safe on violation." |
| **Performance tradeoff** | "Kept the latency-critical work off the hot path and explained the throughput-vs-latency reasoning." |
| **Testing / quality** | "Built a test harness so I could validate behavior changes safely before shipping." |
| **Learning fast** | "Came up a new stack solo; read the source to understand how the internals actually worked." |
| **Conflict / feedback** | (a real interpersonal example — keep one collaboration story) |
| **Failure** | "An early release failed because X; here's the root cause and the process change I made." |

> The differentiator: most candidates' behavioral stories are abstract ("I
> collaborated on a feature"). Yours should be **"I built and owned a real system,
> and here's the engineering judgment I exercised."** That is *memorable* and
> *senior*.

### 7.3 Behavioral pitfalls
- Don't say "we" when it was you (or "I" when it was the team — be honest).
- Don't ramble — STAR keeps you tight (aim ~2 minutes/story).
- Have a **real failure** story with genuine learning. "I'm a perfectionist" is a
  non-answer.
- Tailor emphasis to the company type: at large enterprises emphasize **process
  and collaboration**; at startups emphasize **ownership and shipping**.

---

## 8. Company-Type Calibration

| Company type | What to expect | How to prep |
|---|---|---|
| **Big tech / FAANG-style** | LeetCode medium–hard, strong systems design, structured leveling-focused behavioral | Full DS&A + systems design to a high bar; rehearse leveling-style behavioral answers |
| **High-bar startups / scale-ups** | Genuinely hard coding, fast pace, intense "why" probing, take-homes common | Solid DS&A, a clean take-home, and ownership stories; be ready for rapid-fire follow-ups |
| **Product-/domain-focused companies** | Practical coding, design tied to their product, a take-home | Depth in their domain; a clean take-home; tie your project to their problem space |
| **Large traditional enterprises** | Moderate coding, domain + behavioral + process weight | Domain depth, behavioral/process stories, reliability mindset |
| **Regulated industries (defense, finance, health)** | As above, plus gating screens (clearance, citizenship, compliance) | Standard prep, plus have your eligibility/logistics answer ready (§10) |

Cross-link [02-career-defense-aerospace-playbook.md](02-defense-aerospace-playbook.md)
for an example of one industry's company-by-company context.

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
- [ ] Start the **brag doc** (8–10 STAR stories from a project you own, §7.2).

### Weeks 5–6 — DP, systems design intro
- [ ] DP + backtracking patterns.
- [ ] **Systems design** framework (§3) + 3 designs, including the **event-ingestion
      service** one (§3.4).
- [ ] 1–2 mocks (one coding, one design).

### Weeks 7–8 — Specialization & project depth (your edge)
- [ ] If your roles need it, **language/concurrency/low-level** drills (§4.3).
- [ ] Prepare your **project deep-dive** narrative (§5) — an architecture diagram
      of a system you built that you can whiteboard from memory.
- [ ] Mock the **behavioral** round.

### Weeks 9–12 — Polish & simulate
- [ ] Full **mock onsites** (coding + design + domain + behavioral) end-to-end.
- [ ] Re-solve the ~30 problems you've missed most.
- [ ] Tighten company-type prep (§8) for your top targets.
- [ ] Lock your **screening/logistics** answers (§10).

> Consistency beats cramming. Daily reps with spaced repetition and **out-loud
> narration** is the whole game.

---

## 10. Screening & Logistics Answers

- **Work authorization / location (recruiter screen):** answer plainly and move on.
  In regulated industries a role may also ask about clearance or citizenship — keep
  it short and honest (*"I'm a U.S. citizen and eligible for a background
  investigation"*), and **never** discuss restricted details of past work. Optional
  general guidance if a role requires it:
  [07-career-security-clearance.md](07-security-clearance.md) §12.
- **Comp question (recruiter screen):** deflect to range/research; don't anchor low.
  See [06-career-negotiation-compensation.md](06-negotiation-compensation.md) §4.
- **"Tell me about yourself":** 60–90 seconds — who you are, a **project you built**
  as your headline proof, what you want next. Practice it until it's automatic.
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
- [ ] Have your **project architecture sketch** ready to whiteboard.
- [ ] Water, quiet room, tested A/V (virtual) or arrive early (onsite).
- [ ] For each round: **clarify → plan → narrate → test → reflect.**
- [ ] Prepare **3 questions per interviewer** (about the team, the hardest
      problems they're solving, what success looks like — shows ownership).
- [ ] After: jot what was asked while fresh (helps future loops & negotiation).

---

## 13. How This Connects to the Rest of the Curriculum

- [03-career-software-engineering.md](03-software-engineering.md) — *what*
  to learn; this file is *how to perform it under the clock.*
- [09-career-resume-portfolio.md](09-resume-portfolio.md) — gets you the
  interview; the loop converts it to an offer.
- [07-career-security-clearance.md](07-security-clearance.md) — an optional
  gate that runs in parallel with the loop for regulated-industry roles.
- [06-career-negotiation-compensation.md](06-negotiation-compensation.md) —
  what to do the moment you pass the loop.
- [04-foundations-modern-cpp-realtime.md](../foundations/04-modern-cpp-realtime.md) —
  the C++/real-time depth for the optional low-level round in §4.
- If your target domain is robotics/autonomy, these provide the technical substance
  for a domain deep-dive: [03-autonomy-px4-sitl.md](../autonomy/03-px4-sitl.md),
  [04-autonomy-onboard-system.md](../autonomy/04-onboard-system.md),
  [06-autonomy-control-theory.md](../autonomy/06-control-theory.md),
  [07-autonomy-gnss-jamming-spoofing.md](../autonomy/07-gnss-jamming-spoofing.md),
  [09-autonomy-gnc.md](../autonomy/09-gnc.md),
  [10-autonomy-planning-decision.md](../autonomy/10-planning-decision.md).
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
- Meyers, S. — *Effective Modern C++*, O'Reilly (for the optional low-level round).

**References & docs**
- A\* / search references — Red Blob Games (excellent visual intro):
  https://www.redblobgames.com/pathfinding/a-star/introduction.html
- The Twelve-Factor App (service design): https://12factor.net
- High Scalability (real-world architectures): http://highscalability.com

*This is general career guidance reflecting common industry practice and publicly
available information. Interview formats, difficulty, and company processes change
frequently — confirm specifics with your recruiter and the companies' current
careers pages.*
