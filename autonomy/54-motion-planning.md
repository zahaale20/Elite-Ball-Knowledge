# Motion Planning — From Configuration Space to Feasible Paths

> **Why this exists.** Estimation tells a robot where it is; control tells it how
> to track a setpoint. Motion planning is the layer in between that answers the
> question *what path should I even follow?* — finding a route from start to goal
> that is collision-free, respects the robot's geometry and dynamics, and is in
> some sense good. Without it, an autonomous system can hold position perfectly
> and still have no idea how to get through a doorway. Planning is what turns a
> stabilized platform into a vehicle that *goes places on its own*.
>
> **What mastering it makes you.** The engineer who knows when to reach for a
> grid search, when for a sampling planner, and when for an optimization, who can
> explain why RRT finds *a* path fast but an ugly one, and who understands that
> the hard part of planning is almost never the search — it is defining the
> configuration space and the cost correctly.

Motion planning consumes the maps of
[51-autonomy-slam-and-mapping.md](51-slam-and-mapping.md) and the state
estimates of [52-autonomy-sensor-fusion.md](52-sensor-fusion.md), sits
under the decision architecture of
[29-autonomy-planning-decision.md](29-planning-decision.md), and feeds the
trajectory optimizer of
[55-autonomy-trajectory-optimization.md](55-trajectory-optimization.md),
which smooths and dynamically refines the geometric path produced here. The graph
algorithms and geometry rest on
[03-foundations-mathematics.md](../foundations/03-mathematics.md), the dynamics on
[25-autonomy-control-theory.md](25-control-theory.md), and validation on
[06-foundations-simulation-test-verification.md](../foundations/06-simulation-test-verification.md).

---

## Table of Contents

1. [Configuration space — the right abstraction](#1-configuration-space--the-right-abstraction)
2. [Graph-search planning — Dijkstra, A*, D* Lite](#2-graph-search-planning--dijkstra-a-d-lite)
3. [Sampling-based planning — PRM, RRT, RRT*](#3-sampling-based-planning--prm-rrt-rrt)
4. [Kinodynamic and lattice planning](#4-kinodynamic-and-lattice-planning)
5. [Constraints — nonholonomy and manifolds](#5-constraints--nonholonomy-and-manifolds)
6. [Completeness, optimality, and complexity](#6-completeness-optimality-and-complexity)
7. [The planning stack in practice](#7-the-planning-stack-in-practice)
8. [Practice this week](#8-practice-this-week)
9. [Sources & further study](#9-sources--further-study)

---

## 1. Configuration space — the right abstraction

The foundational idea, due to Lozano-Pérez: plan not in the world but in
**configuration space** $\mathcal{C}$, the space of all parameters that fully
specify the robot's pose. A planar mobile robot has $\mathcal{C} = \mathbb{R}^2 \times S^1$
(position + heading); a 7-DoF arm has $\mathcal{C} = (S^1)^7$. The robot becomes a
*single point* in $\mathcal{C}$, and the obstacles inflate into the
**configuration-space obstacle** $\mathcal{C}_{obs}$ — the set of configurations
where the robot's body intersects an obstacle.

$$
\mathcal{C}_{free} = \mathcal{C} \setminus \mathcal{C}_{obs}, \qquad
\text{plan: find a continuous } \tau:[0,1]\to\mathcal{C}_{free},\ \tau(0)=q_{start},\ \tau(1)=q_{goal}.
$$

This reframing is the whole game: a complicated geometry problem (a robot sweeping
through a cluttered world) becomes a *point*-navigation problem in a
higher-dimensional space. The cost is that $\mathcal{C}_{obs}$ is expensive — often
impossible — to compute explicitly, which is exactly why sampling planners (§3)
exist: they probe $\mathcal{C}_{free}$ with a collision checker instead of building
$\mathcal{C}_{obs}$.

---

## 2. Graph-search planning — Dijkstra, A*, D* Lite

Discretize $\mathcal{C}_{free}$ into a grid or lattice and the problem becomes
shortest path on a graph.

### 2.1 A* — the workhorse

A* finds the optimal path by expanding nodes in order of $f(n) = g(n) + h(n)$,
where $g$ is cost-so-far and $h$ is a heuristic estimate of cost-to-go:

```python
def astar(start, goal, neighbors, cost, h):
    open = PriorityQueue(); open.push(start, h(start))
    g = {start: 0}
    while open:
        n = open.pop()
        if n == goal: return reconstruct(n)
        for m in neighbors(n):
            tentative = g[n] + cost(n, m)
            if tentative < g.get(m, inf):
                g[m] = tentative
                open.push(m, tentative + h(m))   # f = g + h
    return FAILURE
```

A* is **optimal** iff the heuristic is **admissible** ($h(n) \le h^*(n)$, never
overestimates) and **consistent** ($h(n) \le c(n,m) + h(m)$). For a grid,
Euclidean distance is admissible; the octile distance is the tight admissible
heuristic for 8-connected grids. **Weighted A*** inflates the heuristic by
$\varepsilon > 1$ to trade optimality for speed, returning a path at most
$\varepsilon$ times optimal far faster.

### 2.2 Replanning — D* Lite

When the map changes as the robot drives (new obstacle detected), replanning from
scratch wastes work. **D* Lite** (Koenig & Likhachev) repairs the previous search
incrementally, updating only the affected portion of the cost-to-go — the planner
behind countless ground rovers operating on partially known maps.

---

## 3. Sampling-based planning — PRM, RRT, RRT*

In high dimensions (a 7-DoF arm), grids explode combinatorially — the **curse of
dimensionality**. Sampling planners sidestep it by randomly probing
$\mathcal{C}_{free}$ and connecting samples with a cheap **collision checker**,
never building $\mathcal{C}_{obs}$ explicitly.

### 3.1 Probabilistic Roadmaps (PRM)

For *multi-query* problems (same map, many start/goal pairs), PRM builds a reusable
graph: sample $N$ collision-free configurations, connect each to its near neighbors
with collision-free straight-line edges, then run A* on the roadmap. PRM is
**probabilistically complete** — the probability of finding a path if one exists
goes to 1 as $N\to\infty$.

### 3.2 Rapidly-exploring Random Trees (RRT)

For *single-query* problems, RRT grows a tree from the start by repeatedly sampling
a random configuration and extending the nearest tree node toward it:

```python
def rrt(start, goal, sample, near, steer, free):
    T = Tree(start)
    for _ in range(N):
        q_rand = sample()
        q_near = T.nearest(q_rand)
        q_new  = steer(q_near, q_rand, step)      # move a bounded step
        if free(q_near, q_new):                   # collision check edge
            T.add(q_near, q_new)
            if dist(q_new, goal) < tol: return T.path_to(q_new)
    return FAILURE
```

The **Voronoi bias** of RRT — nodes in unexplored regions have larger Voronoi
cells and are thus more likely targeted — makes it explore aggressively. RRT finds
*a* path quickly but it is jagged and far from optimal.

### 3.3 RRT* — asymptotic optimality

**RRT\*** (Karaman & Frazzoli) adds two steps — *choose-parent* and *rewire* —
that locally re-optimize the tree as it grows:

$$
\text{cost}(q_{new}) = \min_{q \in \mathcal{Q}_{near}} \big[\text{cost}(q) + c(q, q_{new})\big],
$$

then rewire any near node whose cost would improve by routing through $q_{new}$.
This makes RRT\* **asymptotically optimal**: the solution cost converges to the
optimum as samples $\to\infty$. The connection radius shrinks as

$$
r_n = \gamma \left(\frac{\log n}{n}\right)^{1/d},
$$

balancing connectivity against the per-iteration cost in dimension $d$. Variants —
**Informed RRT\*** (sample only the ellipsoid that could improve the current
solution), **BIT\*** (batch informed trees) — accelerate convergence dramatically.
All are implemented in **OMPL**, the standard planning library.

---

## 4. Kinodynamic and lattice planning

Geometric planners assume the robot can move in any direction — false for a car
(can't move sideways) or a fixed-wing aircraft (can't stop). **Kinodynamic
planning** plans in the *state* space $(\mathbf{q}, \dot{\mathbf{q}})$ and connects
states with motions that satisfy the dynamics $\dot{\mathbf{x}} = f(\mathbf{x}, \mathbf{u})$.

A **state lattice** discretizes the state space and precomputes a set of
**motion primitives** — dynamically feasible short maneuvers — that connect lattice
states exactly. Planning then becomes graph search over primitives, combining A*'s
optimality with dynamic feasibility:

```
   motion primitives from one heading state:
        ___              feasible arcs that
       /   \             respect the turning
   ───●     ●───         radius and end on
       \___/             lattice headings
```

This is the planner behind many self-driving stacks and the DARPA Urban Challenge
vehicles. **Hybrid A\*** (Dolgov et al.) relaxes the lattice to continuous heading
while keeping a discrete grid for the closed set — the method that parks cars in
tight spaces.

---

## 5. Constraints — nonholonomy and manifolds

### 5.1 Nonholonomic constraints

A car obeys a **nonholonomic** constraint: it cannot translate perpendicular to its
heading. The constraint is on velocities, not configurations:

$$
\dot{x}\sin\theta - \dot{y}\cos\theta = 0.
$$

Such constraints reduce the locally reachable directions without reducing the
reachable *set* — a car can reach any pose, just not by sliding. Planners must
respect this by steering with feasible primitives (Reeds–Shepp / Dubins curves for
cars, which give the shortest paths under a minimum turning radius).

### 5.2 Manifold-constrained planning

A manipulator wiping a table must keep its end-effector on a 2D surface — the valid
configurations form a lower-dimensional **constraint manifold** embedded in
$\mathcal{C}$, of measure zero. Random sampling never lands on it. **CBiRRT** and
projection-based planners sample freely then **project** each sample onto the
manifold by Newton iteration on the constraint $F(\mathbf{q}) = 0$:

$$
\mathbf{q} \leftarrow \mathbf{q} - J_F^{+}\,F(\mathbf{q}), \qquad J_F = \frac{\partial F}{\partial \mathbf{q}}.
$$

---

## 6. Completeness, optimality, and complexity

Planners are classified by their guarantees — know which you have before you trust
one with a vehicle.

| Property | Meaning | Examples |
|---|---|---|
| **Complete** | finds a path if one exists, reports failure otherwise | A*, exact cell decomposition |
| **Resolution-complete** | complete up to discretization | grid A* |
| **Probabilistically complete** | $P(\text{found}) \to 1$ as samples $\to\infty$ | RRT, PRM |
| **Asymptotically optimal** | cost $\to$ optimum as samples $\to\infty$ | RRT\*, PRM\*, BIT\* |

The general motion-planning problem (the **Piano Mover's Problem**) is
**PSPACE-hard** in the number of DoF — proof that *no* algorithm is fast in the
worst case, and the reason the field embraces randomized and approximate methods.
The practical takeaway: completeness is cheap in low dimensions (grids), and only
probabilistic completeness is affordable in high dimensions (sampling).

---

## 7. The planning stack in practice

Real systems layer planners by horizon and rate, mirroring the autonomy stack of
[29-autonomy-planning-decision.md](29-planning-decision.md):

```
┌──────────────────────────────────────────────────────────┐
│ GLOBAL PLANNER   (0.1–1 Hz)  full map, A*/RRT* → route    │
├──────────────────────────────────────────────────────────┤
│ LOCAL PLANNER    (5–20 Hz)   local costmap, kinodynamic   │
│                              → dynamically feasible path  │
├──────────────────────────────────────────────────────────┤
│ TRAJECTORY OPT   (10–100 Hz) smooth + time-parameterize   │
│                              → see Module 55              │
├──────────────────────────────────────────────────────────┤
│ CONTROLLER       (50–1000 Hz) track → see Module 25      │
└──────────────────────────────────────────────────────────┘
```

The global planner finds a topologically correct route on the full (possibly stale)
map; the local planner reacts to freshly sensed obstacles within a rolling window;
the trajectory optimizer (next module) makes the result smooth and dynamically
executable. ROS 2 Nav2 and the MoveIt stack are concrete embodiments. The cardinal
discipline: **the global plan is a suggestion; the local layer has authority over
collision** — the same "slow proposes, fast disposes" rule from the decision module.

---

## 8. Practice this week

1. Implement A* on a 2D occupancy grid with an octile heuristic; compare path cost
   and node expansions against weighted A* for $\varepsilon \in \{1, 1.5, 3\}$.
2. Implement RRT and RRT\* in 2D with obstacles; plot solution cost versus samples
   and watch RRT\* converge while RRT plateaus.
3. Use OMPL to plan for a 7-DoF arm (or its tutorials); compare RRT-Connect, RRT\*,
   and BIT\*.
4. Implement Dubins-curve steering and plan for a car with a minimum turning radius
   using Hybrid A\*.

---

## 9. Sources & further study

- **LaValle — *Planning Algorithms*** (free online). The comprehensive reference:
  configuration space, sampling, completeness, kinodynamics.
- **Choset et al. — *Principles of Robot Motion*.** Cell decomposition, potential
  fields, roadmaps, with rigorous geometry.
- **Karaman & Frazzoli — "Sampling-based Algorithms for Optimal Motion Planning"**
  (IJRR, 2011). The RRT\*/PRM\* optimality paper.
- **Koenig & Likhachev — "D\* Lite."** Incremental replanning.
- **Dolgov, Thrun et al. — "Path Planning for Autonomous Vehicles in Unknown
  Semi-structured Environments"** (Hybrid A\*).
- **Şucan, Moll & Kavraki — "The Open Motion Planning Library" (OMPL).** The
  practical toolkit.
- **Gammell, Srinivasa & Barfoot — "Informed RRT\*" and "BIT\*".**

> Framing note: The search algorithm is the easy, well-understood part of planning.
> The engineering judgment lives in defining the configuration space, the cost
> function, and the collision model correctly — get those wrong and the world's best
> planner cheerfully returns the optimal path into a wall. Plan in the right space,
> and let the optimizer of the next module make the path beautiful.
