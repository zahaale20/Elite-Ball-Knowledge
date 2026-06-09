# Multi-Agent Systems & Swarm Autonomy — Many Vehicles, One Intent

> **Why this exists.** A single autonomous vehicle is a solved-enough problem for many missions; the frontier is getting *tens, hundreds, or thousands* of them to behave as one coherent system without a central brain that can be jammed, killed, or saturated. Swarm autonomy is where control theory, distributed systems, and game theory collide: each agent runs a local policy on noisy local information, yet the *collective* must satisfy a global intent — cover an area, escort a convoy, saturate a defense, map a building. The hard part is that emergence cuts both ways: good local rules produce robust global behavior, but subtle local bugs produce global pathologies (oscillation, fragmentation, deadlock) that no single agent can see. Mastering this means you can reason about a system whose behavior lives in the *interactions*, not in any one node.
>
> **What mastering it makes you.** The engineer who can design a coordination protocol that degrades gracefully when half the fleet drops off the mesh — and prove it converges. That skill is rare, defense-relevant, and directly monetizable.

Swarm autonomy sits downstream of single-agent competence: each member still needs the estimation of [53-autonomy-state-estimation-advanced.md](53-autonomy-state-estimation-advanced.md), the planning of [29-autonomy-planning-decision.md](29-autonomy-planning-decision.md), the control of [28-autonomy-gnc.md](28-autonomy-gnc.md), and the learning of [20-autonomy-ml-ai.md](20-autonomy-ml-ai.md). What changes is the *substrate*: coordination rides on the mesh networking and consistency models of [05_distributed_systems_comms_mesh.md](05_distributed_systems_comms_mesh.md), and the consensus math is pure linear algebra and graph theory from [03-foundations-mathematics.md](03-foundations-mathematics.md). It pairs tightly with motion planning ([54-autonomy-motion-planning.md](54-autonomy-motion-planning.md)) and feeds the foundation-model planners of [63-autonomy-foundation-models-robotics.md](63-autonomy-foundation-models-robotics.md).

---

## 1. The Core Problem: Global Intent from Local Rules

A multi-agent system is $N$ agents indexed $i \in \{1,\dots,N\}$, each with state $x_i \in \mathbb{R}^n$, control $u_i$, and access only to a **neighborhood** $\mathcal{N}_i$ — the agents it can sense or talk to. The communication topology is a graph $G = (V, E)$ where an edge $(i,j) \in E$ means $i$ and $j$ can exchange information. This graph is *time-varying* (vehicles move, links drop), which is the entire source of difficulty.

The design question: **what local update law $u_i = f(x_i, \{x_j : j \in \mathcal{N}_i\})$ produces a desired global property** (alignment, cohesion, coverage, task completion)?

```
   GLOBAL INTENT (mission)
        │  decomposed by
        ▼
  ┌─────────────────────────────┐
  │  Local policy on each agent  │  ← only sees neighbors
  └─────────────────────────────┘
        │  interactions over mesh
        ▼
   EMERGENT GLOBAL BEHAVIOR
        │  may or may not match intent
        ▼
   Verification problem (Sec. 9)
```

Two philosophies recur:
- **Reactive / behavior-based** (Reynolds, Brooks): cheap local rules, fast, robust, hard to guarantee.
- **Optimization / consensus-based**: each agent solves a piece of a global objective; provable convergence, heavier compute and comms.

Real systems blend both.

---

## 2. Reynolds Flocking — The Canonical Reactive Swarm

Craig Reynolds' 1987 *boids* model produces lifelike flocking from three steering rules acting on neighbors within a radius $r$:

1. **Separation** — steer away from crowding:
$$\mathbf{a}_i^{sep} = -k_s \sum_{j \in \mathcal{N}_i} \frac{\mathbf{p}_i - \mathbf{p}_j}{\|\mathbf{p}_i - \mathbf{p}_j\|^2}$$

2. **Alignment** — match neighbors' average velocity:
$$\mathbf{a}_i^{ali} = k_a \left( \frac{1}{|\mathcal{N}_i|} \sum_{j \in \mathcal{N}_i} \mathbf{v}_j - \mathbf{v}_i \right)$$

3. **Cohesion** — steer toward the local centroid:
$$\mathbf{a}_i^{coh} = k_c \left( \frac{1}{|\mathcal{N}_i|} \sum_{j \in \mathcal{N}_i} \mathbf{p}_j - \mathbf{p}_i \right)$$

The commanded acceleration is the weighted sum $\mathbf{a}_i = \mathbf{a}_i^{sep} + \mathbf{a}_i^{ali} + \mathbf{a}_i^{coh}$, clipped to actuator limits. Separation uses an inverse-square (or inverse) weighting so it dominates at short range, preventing collisions while cohesion keeps the flock together.

```python
def boid_step(p, v, neighbors, ks=1.5, ka=1.0, kc=0.6, r=8.0):
    sep = ali = coh = np.zeros(3)
    n = 0
    for q, w in neighbors:                  # q=position, w=velocity
        d = p - q
        dist = np.linalg.norm(d) + 1e-6
        if dist < r:
            sep += d / (dist * dist)        # push apart, stronger when close
            ali += w                        # accumulate neighbor velocity
            coh += q                         # accumulate neighbor position
            n += 1
    if n == 0:
        return np.zeros(3)
    ali = ali / n - v                       # match average heading
    coh = coh / n - p                       # pull toward local center
    return ks * sep + ka * ali + kc * coh
```

**Olfati-Saber's flocking** (2006) made this rigorous: it replaces the heuristic rules with the gradient of a *smooth pairwise potential* $\psi(\|\mathbf{p}_i - \mathbf{p}_j\|)$ plus a velocity-consensus term, and proves with a Lyapunov function that the flock reaches a lattice-like α-formation with velocity matching, even with obstacles (β-agents) and a virtual leader (γ-agent). This is the bridge from "looks like birds" to "provably stable."

---

## 3. Consensus — The Mathematical Heart of Coordination

Most distributed coordination reduces to **agreeing on a value**: a rendezvous point, an average measurement, a clock, a leader's command. The continuous-time consensus protocol is

$$\dot{x}_i = -\sum_{j \in \mathcal{N}_i} a_{ij}(x_i - x_j), \qquad \dot{\mathbf{x}} = -L\mathbf{x}$$

where $L = D - A$ is the **graph Laplacian** ($A$ = adjacency, $D$ = degree diagonal). The Laplacian is the single most important object in swarm theory.

**Key spectral facts** (from [03-foundations-mathematics.md](03-foundations-mathematics.md)):
- $L \succeq 0$, rows sum to zero, so $\mathbf{1}$ is an eigenvector with eigenvalue $0$.
- The number of zero eigenvalues equals the number of connected components.
- The **algebraic connectivity** $\lambda_2$ (second-smallest eigenvalue, the *Fiedler value*) governs convergence speed: larger $\lambda_2$ ⇒ faster mixing.

For a connected graph, consensus converges to the average $\bar{x} = \frac{1}{N}\sum x_i(0)$ at rate $e^{-\lambda_2 t}$. This is *average consensus* and it is how a swarm computes a global statistic with only local talk.

**Discrete form** (what you actually code, gossiping over the mesh):
$$x_i[k{+}1] = x_i[k] + \epsilon \sum_{j \in \mathcal{N}_i} (x_j[k] - x_i[k]), \quad 0 < \epsilon < \tfrac{1}{\Delta_{max}}$$
with $\Delta_{max}$ the max degree. Step too aggressively and you oscillate; this is the discrete-time stability bound.

| Property | Depends on |
|---|---|
| *Whether* consensus is reached | Graph connectivity (over time, for switching topologies) |
| *How fast* | Fiedler value $\lambda_2$ |
| *Robustness to dropout* | Redundant paths, $k$-connectivity |
| *Value agreed on* | Weights $a_{ij}$ (uniform ⇒ average) |

Switching topologies (Jadbabaie–Lin–Morse result): even if no single instantaneous graph is connected, consensus still holds if the union of graphs over bounded intervals is connected. This is why swarms work despite flickering links.

---

## 4. Formation Control

Beyond agreement, we often want a *specific geometry*: a wedge, a line abreast, a grid for sensor coverage. Three formulations:

**Displacement-based.** Each agent knows desired relative offsets $\mathbf{d}_{ij}$ in a common frame:
$$u_i = -\sum_{j \in \mathcal{N}_i} \big[(\mathbf{p}_i - \mathbf{p}_j) - (\mathbf{d}_i - \mathbf{d}_j)\big]$$
Requires shared orientation (compass / GNSS heading). This is consensus on the *error* from the desired offset.

**Distance-based.** Maintain inter-agent distances $\|\mathbf{p}_i - \mathbf{p}_j\| = d_{ij}^*$ using gradient descent on $\sum (\|\mathbf{p}_i-\mathbf{p}_j\|^2 - d_{ij}^{*2})^2$. Needs only relative position, no shared frame, but the formation's global position/orientation is free. **Rigidity theory** tells you which distance constraint sets uniquely fix a shape (a framework is *infinitesimally rigid* iff its rigidity matrix has rank $2N-3$ in 2D).

**Leader–follower.** One or more leaders carry the mission trajectory; followers track relative poses. Simple and common (escort, convoy) but a single point of failure unless leadership can be re-elected.

```
   Distance-based formation (no shared frame needed)
        d12              d23
   (1)───────(2)───────(3)
     \        |        /
      \  d13  | d24   /     each edge = one constraint;
       \      |      /      enough independent edges ⇒ rigid shape
        (4)──────(5)
```

---

## 5. Distributed Task Allocation

Given $N$ agents and $M$ tasks, who does what? This is a **combinatorial assignment** problem that must be solved *without* a central optimizer.

**Auction algorithms** (Bertsekas; CBBA = Consensus-Based Bundle Algorithm, Choi/Brunt/How 2009): agents bid on tasks based on local utility (e.g., negative travel cost), iteratively raising prices on contested tasks until a conflict-free assignment emerges. CBBA runs two phases that alternate over the mesh:

```
Phase 1 — BUNDLE BUILD (local, greedy):
  each agent adds tasks to its bundle that maximize
  marginal score, recording bid = score for each task

Phase 2 — CONSENSUS (over neighbors):
  exchange winning-bid and winning-agent vectors;
  apply deterministic conflict-resolution rules;
  drop tasks you lost → return to Phase 1
Repeat until no changes propagate (converges in O(N·M) comm rounds)
```

CBBA guarantees a conflict-free, at-least-50%-of-optimal assignment for submodular score functions and is robust to message loss because it only ever *needs* the latest winning-bid vector. For tasks with time windows and coupled constraints, you escalate to distributed constraint optimization (DCOP) solvers like Max-Sum, trading optimality for message complexity.

| Method | Optimality | Comms | Handles dynamic tasks |
|---|---|---|---|
| Greedy local | Poor | None | Yes |
| Hungarian (central) | Optimal | N/A (central) | Rebuild |
| Auction / CBBA | ≥50% (submodular) | Moderate | Yes, incremental |
| Max-Sum DCOP | Near-optimal | Heavy | Yes |

---

## 6. Coverage, Search & Coordinated Sensing

A swarm's killer app is **distributed coverage**: spread out to monitor a region optimally. The classic tool is **Lloyd's algorithm** on a **Voronoi partition**. Each agent owns the region of space closest to it; it moves toward the *centroid* of its Voronoi cell weighted by an importance density $\phi(\mathbf{q})$:

$$\mathbf{c}_i = \frac{\int_{V_i} \mathbf{q}\,\phi(\mathbf{q})\,d\mathbf{q}}{\int_{V_i} \phi(\mathbf{q})\,d\mathbf{q}}, \qquad u_i = k(\mathbf{c}_i - \mathbf{p}_i)$$

This descends the **locational cost** $\mathcal{H} = \sum_i \int_{V_i} \|\mathbf{q}-\mathbf{p}_i\|^2 \phi(\mathbf{q})\,d\mathbf{q}$ and converges to a centroidal Voronoi configuration — optimal sensor placement. Cortés & Bullo proved it's distributed: each agent only needs Voronoi neighbors. Raise $\phi$ where targets are likely and the swarm self-concentrates there.

For *search* (unknown target locations), agents maintain a shared occupancy/probability map (consensus-fused) and steer up the information gradient — mutual-information or coverage-frontier objectives, linking to the active-perception ideas in [50-autonomy-perception-deep.md](50-autonomy-perception-deep.md).

---

## 7. Coordination over a Real Mesh

Everything above assumes messages arrive. They don't. Swarm comms is where [05_distributed_systems_comms_mesh.md](05_distributed_systems_comms_mesh.md) becomes survival-critical:

- **Topology is RF-limited.** Range, line-of-sight, multipath, and jamming define $G$, not your wishes. Algebraic connectivity $\lambda_2$ can be *controlled* — agents can steer to keep links alive (connectivity maintenance), trading mission progress for network health.
- **Gossip, not broadcast.** Flooding doesn't scale; epidemic/gossip protocols spread state in $O(\log N)$ rounds with bounded bandwidth.
- **Eventual consistency.** You will never have a globally consistent snapshot. Design protocols (like CBBA) that converge to the *correct* answer from *stale* inputs — CRDTs and monotone state are your friends.
- **Byzantine resilience.** A spoofed or captured node can inject lies. Robust consensus (e.g., **W-MSR**: discard the $F$ highest and $F$ lowest neighbor values before averaging) tolerates up to $F$ adversaries if the graph is sufficiently *robust* (a stronger condition than connectivity).
- **Time sync.** Many protocols need a shared clock; distributed time sync is itself a consensus problem (average-consensus on clock offsets).

```
            JAMMER
              ╳ ╳ ╳
   (1)──(2)   ╳   (4)──(5)
     \   \    ╳    /   /
      \   (3)─╳───(6) /     link 3-6 severed → graph splits.
       Union-over-time connectivity lost ⇒ two sub-swarms
       must operate autonomously until rejoin.
```

**Design rule:** every swarm algorithm must answer *"what happens when the network partitions?"* The good ones keep doing useful work in each partition and merge cleanly on reconnection.

---

## 8. Emergent Behavior — Friend and Foe

Emergence is the property that the whole exhibits behavior absent from any part. It's why swarms are powerful and why they're terrifying to certify.

**Constructive emergence:** flocking, self-organized lanes, division of labor, collective gradient sensing (a swarm "smells" a chemical gradient no individual could resolve — *swarm taxis*).

**Pathological emergence:**
- **Oscillation / chattering** from competing rules or delayed feedback.
- **Fragmentation** when cohesion loses to separation at scale.
- **Deadlock / livelock** in mutual collision avoidance (the "robot dance" where two agents repeatedly dodge into each other).
- **Cascading failure** when one agent's spurious state propagates through consensus.

The defense against pathology is *analysis*, not just testing. Lyapunov functions prove convergence; mean-field / continuum models (treating the swarm as a density $\rho(\mathbf{x},t)$ obeying a PDE) predict large-$N$ behavior analytically; and reachability analysis bounds worst-case trajectories.

$$\frac{\partial \rho}{\partial t} + \nabla \cdot (\rho\, \mathbf{v}[\rho]) = 0 \quad \text{(continuity / mean-field swarm model)}$$

---

## 9. Verification & Test for Swarms

> The user expects test design in every engineering artifact — and swarms are the hardest thing to test because behavior lives in interactions and scales combinatorially.

A layered test strategy (echoing [06-foundations-simulation-test-verification.md](06-foundations-simulation-test-verification.md) and [24-autonomy-test-scaffold.md](24-autonomy-test-scaffold.md)):

| Level | What it checks | Method / tooling |
|---|---|---|
| **Unit** | Single agent's local policy (separation never increases collision risk; bid math correct) | Property tests on `boid_step`, CBBA conflict rules |
| **Pairwise** | Two-agent invariants: no collision, mutual avoidance terminates | Exhaustive relative-state sweep; deadlock detection |
| **Integration** | $N$-agent emergent properties: convergence, no fragmentation, coverage ≥ target | Monte-Carlo over topologies in Gazebo/Isaac, ROS 2 multi-robot |
| **Adversarial** | Network partition, Byzantine node, jamming, dropout | Fault injection on the mesh; W-MSR resilience tests |
| **Acceptance** | Mission-level intent satisfied within bounds | Scenario suite, statistical pass criteria |
| **Exploratory** | Find *unexpected* emergent failures | Randomized "swarm fuzzing," scale-up sweeps |

**Boundary cases that matter most:** $N{=}1$ (degenerate), $N{=}2$ (deadlock-prone), the moment a partition heals (state merge), the agent that joins late with stale state, the agent that never receives a critical message. Test these explicitly — they are where real swarms fail. Frame the whole effort as *risk prevention*: you're building confidence that emergence stays in the constructive regime, not merely hunting individual bugs.

```python
def test_no_fragmentation_under_dropout():
    # Risk: link loss splits the flock into non-recombining clusters.
    swarm = SimSwarm(n=50, topology="random_geometric", radius=8.0)
    swarm.enable_random_link_dropout(prob=0.3)   # 30% of links flicker
    swarm.run(steps=2000)
    # Acceptance: union-over-time connectivity preserved ⇒ one cluster.
    assert swarm.num_connected_components_over_window() == 1
    # Boundary: even the worst-served agent stays within cohesion radius.
    assert swarm.max_agent_centroid_distance() < swarm.cohesion_radius
```

---

## 10. The Stack in Practice

A deployable swarm node looks like:

```
┌──────────────────────────────────────────────┐
│  Mission / intent layer (may use LLM planner, │  ← ch. 63
│  CBBA task allocation)                         │
├──────────────────────────────────────────────┤
│  Coordination: consensus, formation, coverage │  ← this chapter
├──────────────────────────────────────────────┤
│  Local autonomy: planning, GNC, estimation    │  ← ch. 28/29/53/54
├──────────────────────────────────────────────┤
│  Mesh comms: gossip, time-sync, partition mgmt│  ← ch. 05
├──────────────────────────────────────────────┤
│  ROS 2 / DDS middleware, micro-ROS on MCU     │
└──────────────────────────────────────────────┘
```

Real systems and references: **ROS 2** with multi-robot DDS domains, **Gazebo / NVIDIA Isaac Sim** for swarm simulation, **Crazyswarm / Crazyflie** for indoor drone-swarm research, **PX4** with onboard MAVLink mesh for outdoor fleets ([22-autonomy-px4-sitl.md](22-autonomy-px4-sitl.md)), and the academic lineage of Olfati-Saber, Bullo, and the GRASP/Kumar lab quadrotor swarms. Production defense swarms layer in robust consensus, anti-jam waveforms, and human-on-the-loop intent injection.

---

## Sources & further study

- **Bullo, Cortés & Martínez — *Distributed Control of Robotic Networks*** (free online). The rigorous text: Laplacians, coverage, rendezvous, with proofs.
- **Mesbahi & Egerstedt — *Graph Theoretic Methods in Multiagent Networks*.** Definitive on consensus, formation, rigidity, controllability of networks.
- **Reynolds (1987), "Flocks, Herds and Schools"** — the original boids paper.
- **Olfati-Saber (2006), "Flocking for Multi-Agent Dynamic Systems"**, *IEEE TAC* — rigorous flocking with Lyapunov proofs.
- **Olfati-Saber, Fax & Murray (2007), "Consensus and Cooperation in Networked Multi-Agent Systems"**, *Proc. IEEE* — the canonical consensus survey.
- **Choi, Brunet & How (2009), "Consensus-Based Decentralized Auctions" (CBBA)**, *IEEE T-RO*.
- **Cortés, Martínez, Karatas & Bullo (2004), "Coverage Control for Mobile Sensing Networks"** — Lloyd/Voronoi coverage.
- **LeBlanc, Zhang, Koutsoukos & Sundaram (2013), "Resilient Asymptotic Consensus" (W-MSR)** — Byzantine resilience.
- **Brambilla, Ferrante, Birattari & Dorigo (2013), "Swarm Robotics: A Review"** — engineering taxonomy.

> Framing note: A swarm is not a fleet you command; it is a *field* you shape. You write the local rules and the network substrate, then the global behavior is *grown*, not authored. The engineers who win this domain think like physicists studying an emergent phase — they reason about densities, connectivity, and stability margins — while still shipping code that runs on a 200-gram drone with a flaky radio. Hold both views at once.
