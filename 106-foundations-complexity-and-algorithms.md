# Algorithms & Complexity — What Is Computable, and How Fast

> **Why this exists.** Every autonomous decision is a computation racing a deadline. A path planner that is correct but exponential is useless on a vehicle that must replan at 10 Hz; a perception pipeline that allocates badly thrashes the cache and misses frames; a SLAM back-end that uses a dense solve where a sparse one exists wastes an order of magnitude. Algorithms and complexity theory tell you what is *achievable*, what is *intractable*, and — when a problem is NP-hard — how to approximate it well enough to fly. This is the discipline of spending finite compute wisely, and of knowing the difference between "hard for me" and "hard for everyone."

> **What mastering it makes you.** The engineer who can look at a planning or perception problem and instantly recognize its complexity class, pick the data structure that turns an $O(n^2)$ loop into $O(n\log n)$, prove a greedy heuristic is within a factor of optimal, and know when to stop searching for an exact algorithm because none can exist. You become the person whose code meets the real-time deadline because you chose the right algorithm, not the fastest language.

This module provides the computational backbone for the planning algorithms of [29-autonomy-planning-decision.md](29-autonomy-planning-decision.md), the equilibrium computations of [105-foundations-decision-and-game-theory.md](105-foundations-decision-and-game-theory.md), and the optimization solvers behind [101-foundations-control-advanced.md](101-foundations-control-advanced.md) (MPC is a QP solved every timestep). The discrete-math and proof foundations come from [03-foundations-mathematics.md](03-foundations-mathematics.md); the perception consumers appear in [50-autonomy-perception-deep.md](50-autonomy-perception-deep.md) and [51-autonomy-slam-and-mapping.md](51-autonomy-slam-and-mapping.md). The engineering-tradeoff mindset is the algorithmic face of [01_first_principles_systems_engineering.md](01_first_principles_systems_engineering.md).

---

## 1. Asymptotic analysis — the language of scaling

We measure cost by how it *grows*, not by constants, because constants are dwarfed by scaling at the sizes autonomy faces.

$$
f(n) = O(g(n)) \iff \exists c, n_0 : f(n) \le c\,g(n)\ \forall n \ge n_0.
$$

Also $\Omega$ (lower bound) and $\Theta$ (tight bound). The hierarchy that decides feasibility:

| Class | Example algorithm | $n=10^6$ feel |
|---|---|---|
| $O(1)$ | hash lookup | instant |
| $O(\log n)$ | binary search | instant |
| $O(n)$ | linear scan | fast |
| $O(n\log n)$ | mergesort, FFT | the practical ceiling for large $n$ |
| $O(n^2)$ | naive pairwise | painful at $10^4$ |
| $O(2^n)$ | brute-force subset | dead past $n\approx 40$ |
| $O(n!)$ | brute-force TSP | dead past $n\approx 12$ |

The jump from polynomial to exponential is the single most important boundary in computing. A planner that is $O(2^n)$ does not "run slow" — it does not run at all beyond toy sizes.

### 1.1 Worked example — why mergesort beats bubble sort

Bubble sort does $\Theta(n^2)$ comparisons. Mergesort's recurrence is $T(n) = 2T(n/2) + \Theta(n)$. By the **Master Theorem** (with $a=2, b=2, f(n)=\Theta(n)$, so $n^{\log_b a} = n$), this is the balanced case:

$$
T(n) = \Theta(n\log n).
$$

At $n=10^6$: bubble does $\sim 10^{12}$ operations (minutes); mergesort does $\sim 2\times10^7$ (milliseconds). Same problem, five orders of magnitude — chosen by algorithm, not hardware.

---

## 2. Data structures — the right container changes the complexity class

Algorithms and data structures are inseparable; the structure determines which operations are cheap.

| Structure | Search | Insert | Use in autonomy |
|---|---|---|---|
| Array | $O(n)$ | $O(1)$ amortized | dense state, images |
| Hash table | $O(1)$ avg | $O(1)$ avg | feature matching, dedup |
| Balanced BST | $O(\log n)$ | $O(\log n)$ | ordered events |
| Binary heap | $O(1)$ peek | $O(\log n)$ | **priority queue for A\*** |
| k-d tree | $O(\log n)$ avg | — | nearest-neighbor in point clouds |
| Union-Find | $\sim O(\alpha(n))$ | — | connected components, clustering |

The **priority queue** (binary heap) is what makes Dijkstra and A\* efficient — extract-min in $O(\log n)$ instead of $O(n)$. The **k-d tree** turns nearest-neighbor queries on LiDAR point clouds from $O(n)$ to $O(\log n)$, the difference between real-time and not. Choosing the structure *is* choosing the complexity.

---

## 3. Graph algorithms — the spine of planning

Most autonomy planning reduces to graph search: nodes are configurations, edges are feasible transitions.

### 3.1 Shortest paths

**Dijkstra** finds single-source shortest paths in $O((V+E)\log V)$ with a heap, for non-negative edge weights. It greedily settles the closest unsettled node, and an exchange argument proves optimality.

**A\*** adds a **heuristic** $h(n)$ estimating cost-to-go, expanding nodes in order of $f(n) = g(n) + h(n)$. If $h$ is **admissible** (never overestimates) and **consistent** ($h(n) \le c(n,n') + h(n')$), A\* is optimal and expands no more nodes than any other optimal algorithm using the same heuristic. The proof: at the goal, $f = g$ (since $h=0$), and consistency makes $f$ non-decreasing along any path, so the first goal popped is optimal.

$$
f(n) = \underbrace{g(n)}_{\text{cost so far}} + \underbrace{h(n)}_{\text{admissible estimate}}.
$$

This is the workhorse of grid and lattice planning in [29-autonomy-planning-decision.md](29-autonomy-planning-decision.md). The Euclidean distance is the canonical admissible heuristic for spatial planning.

### 3.2 Other essential graph tools

- **BFS/DFS** — $O(V+E)$ traversal; BFS gives shortest paths in unweighted graphs.
- **Topological sort** — orders a DAG; schedules dependent tasks (mission sequencing).
- **Minimum spanning tree** (Kruskal/Prim) — cheapest connecting network; sensor coverage, comms relay placement.
- **Max-flow / min-cut** (Ford–Fulkerson, $O(VE^2)$ for Edmonds–Karp) — the duality $\text{max-flow} = \text{min-cut}$ models bottlenecks and, via min-cut, image segmentation in perception.

```python
import heapq

def a_star(start, goal, neighbors, heuristic):
    """A* search. `neighbors(n)` yields (next, edge_cost);
    `heuristic` must be admissible (never overestimate cost-to-go)."""
    open_set = [(heuristic(start), 0.0, start)]      # (f, g, node)
    g_best = {start: 0.0}
    came_from = {}
    while open_set:
        f, g, node = heapq.heappop(open_set)
        if node == goal:
            return reconstruct(came_from, node), g
        for nxt, cost in neighbors(node):
            tentative = g + cost
            if tentative < g_best.get(nxt, float("inf")):
                g_best[nxt] = tentative
                came_from[nxt] = node
                heapq.heappush(open_set, (tentative + heuristic(nxt), tentative, nxt))
    return None, float("inf")                        # goal unreachable

def reconstruct(came_from, node):
    path = [node]
    while node in came_from:
        node = came_from[node]
        path.append(node)
    return path[::-1]
```

---

## 4. Dynamic programming — optimal substructure

When a problem's optimal solution is built from optimal solutions to subproblems, **dynamic programming (DP)** avoids exponential recomputation by memoizing. Two ingredients: *optimal substructure* and *overlapping subproblems*.

### 4.1 The Bellman recurrence

DP is the algorithmic embodiment of the Bellman equation seen in control and decision theory:

$$
V(s) = \min_a \big[ c(s,a) + V(\text{next}(s,a)) \big].
$$

The same recurrence underlies LQR (Riccati), MDP value iteration ([105-foundations-decision-and-game-theory.md](105-foundations-decision-and-game-theory.md)), the Viterbi algorithm (most-likely state sequence in HMMs — used in SLAM and tracking), edit distance, and the DP layer of A\*. Recognizing a problem as DP collapses an exponential brute force to polynomial. Example: knapsack by brute force is $O(2^n)$; by DP it is $O(nW)$ — pseudo-polynomial, the practical algorithm.

---

## 5. Computability and the limits of the possible

Some problems admit *no* algorithm at all. The **Halting Problem** — deciding whether an arbitrary program halts — is undecidable (Turing, 1936). The proof is a diagonalization: assume a decider $H$, build a program that halts iff $H$ says it loops, and derive a contradiction. Rice's theorem generalizes: every nontrivial semantic property of programs is undecidable. The practical takeaway for autonomy: you *cannot* write a general verifier that proves arbitrary autonomous code is safe — which is why verification relies on restricted, decidable formalisms (model checking, type systems) rather than full generality. This is a hard boundary, not an engineering gap.

---

## 6. NP-hardness — the problems we cannot solve exactly (probably)

The most consequential idea for an autonomy engineer: many natural planning problems are **NP-hard**, meaning no known polynomial algorithm exists and one almost certainly does not.

### 6.1 P, NP, and reductions

- **P** — solvable in polynomial time.
- **NP** — solutions *verifiable* in polynomial time.
- **NP-complete** — the hardest problems in NP; if any one is in P, then $\text{P}=\text{NP}$ (the central open question).
- **NP-hard** — at least as hard as NP-complete (may not be in NP).

We prove hardness by **reduction**: transform a known NP-hard problem $A$ into your problem $B$ in polynomial time; if you could solve $B$ fast, you could solve $A$ fast. Cook–Levin established SAT as the first NP-complete problem.

### 6.2 The autonomy problems that are NP-hard

| Problem | Where it appears |
|---|---|
| Traveling Salesman | multi-target route, ISR tasking |
| Vehicle Routing | swarm delivery / coverage |
| Bin Packing | payload/asset allocation |
| Graph Coloring | spectrum/frequency assignment |
| Set Cover | sensor placement |
| Integer Programming | discrete mission optimization |

When you meet these, **stop looking for an exact polynomial algorithm** — there isn't one. Switch strategy to approximation or heuristics.

---

## 7. Coping with intractability — approximation and heuristics

NP-hardness is a worst-case statement, not a death sentence. Four escape routes:

1. **Approximation algorithms** with provable ratios. The greedy algorithm for **Set Cover** achieves a $\ln n$ approximation — proven optimal unless P=NP. For metric TSP, **Christofides** guarantees a tour within $\tfrac32$ of optimal:

   $$
   \text{cost(Christofides)} \le \tfrac{3}{2}\,\text{cost(OPT)}.
   $$

2. **Heuristic search** — A\* with a good heuristic, branch-and-bound, beam search: exponential worst case but fast in practice.
3. **Randomized / metaheuristic** — simulated annealing, genetic algorithms, ant colony: no guarantee, but good solutions to huge instances.
4. **Exploit structure** — many "NP-hard" instances in practice are sparse, low-treewidth, or near-Euclidean, where special-case polynomial algorithms apply (e.g., DP on bounded-treewidth graphs).

The engineering judgment — *which* escape route, and how to bound the optimality gap — is exactly the cost/benefit reasoning of [01_first_principles_systems_engineering.md](01_first_principles_systems_engineering.md).

---

## 8. Real-time constraints — complexity meets the deadline

Autonomy adds a dimension classical complexity ignores: the **hard deadline**. A control loop at 1 kHz has 1 ms to produce an answer, optimal or not. This reshapes algorithm choice:

- Prefer **anytime algorithms** (RRT\*, ARA\*) that return a feasible answer immediately and improve it if time remains.
- Bound the **worst-case execution time (WCET)**, not the average — a planner that is usually 1 ms but occasionally 50 ms can crash a vehicle.
- Trade optimality for **predictable latency**: a slightly suboptimal path delivered on time beats an optimal one delivered late.
- Mind **memory hierarchy**: cache-friendly $O(n)$ can beat cache-hostile $O(\log n)$ at real sizes; the constant factors that asymptotics ignore are the difference between meeting and missing a frame.

| Property | Offline planning | Real-time autonomy |
|---|---|---|
| Metric | total runtime | worst-case latency |
| Optimality | exact preferred | bounded-suboptimal OK |
| Algorithm | exact / IP solver | anytime / heuristic |
| Failure mode | slow | missed deadline = crash |

This is where complexity theory becomes operational: the same A\* that is "optimal" in a textbook must be budgeted, bounded, and made anytime to survive on a vehicle.

---

## 9. The complexity map of an autonomy stack

| Subsystem | Core algorithm | Complexity |
|---|---|---|
| Path planning | A\* / Dijkstra | $O((V+E)\log V)$ |
| Sampling-based planning | RRT\* | $O(n\log n)$ per query |
| SLAM back-end | sparse factor-graph solve | $\sim O(n^{1.5})$ exploiting sparsity |
| Nearest neighbor (LiDAR) | k-d tree | $O(\log n)$ avg |
| MPC step | QP (interior point) | polynomial per step |
| Multi-target assignment | Hungarian algorithm | $O(n^3)$ |
| Task allocation | NP-hard → approximation | provable ratio |

Reading this map is the skill: every box is a complexity-class decision, and the difference between a stack that closes its real-time budget and one that does not is whether each box was chosen with this table in mind.

---

## Sources & further study

- Cormen, Leiserson, Rivest & Stein (CLRS), *Introduction to Algorithms* — the comprehensive standard for everything above.
- Kleinberg & Tardos, *Algorithm Design* — superb on graph algorithms, DP, and NP-completeness with intuition.
- Sipser, *Introduction to the Theory of Computation* — computability, decidability, and the P vs NP framing.
- Garey & Johnson, *Computers and Intractability* — the classic NP-completeness reference and reduction catalog.
- Vazirani, *Approximation Algorithms* — provable-ratio coping strategies.
- LaValle, *Planning Algorithms* — the bridge from these algorithms to robot motion planning (free online).
- Skiena, *The Algorithm Design Manual* — the practitioner's catalog of which algorithm to reach for.

> Framing note: Complexity theory is the engineer's humility and the engineer's leverage. It tells you when a problem is genuinely intractable so you stop wasting effort on an exact solution that cannot exist — and it tells you which data structure or approximation turns an impossible loop into a real-time one. On a vehicle, the binding constraint is rarely the language or the CPU; it is whether you recognized the problem's complexity class and chose accordingly. Master this, and you spend finite compute like a strategist, not a spender.
