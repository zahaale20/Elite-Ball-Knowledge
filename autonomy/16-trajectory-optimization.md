# Trajectory Optimization — Smooth, Dynamically Feasible Motion

> **Why this exists.** A motion planner returns a *geometric* path — a sequence of
> collision-free waypoints — but a robot cannot execute a jagged polyline. It needs
> a *trajectory*: a time-parameterized motion that is smooth, respects actuator
> limits, satisfies the system dynamics, and minimizes effort. Trajectory
> optimization is the discipline that turns "here is a route" into "here is exactly
> how to move through it, second by second, without exceeding thrust or violating
> dynamics." It is what makes a quadrotor flip through a window, a manipulator move
> with grace, and a self-driving car merge smoothly rather than lurch.
>
> **What mastering it makes you.** The engineer who can formulate a maneuver as a
> QP or NLP and know which one, who understands why minimum-snap trajectories are
> the right basis for quadrotors, and who can build a real-time MPC that stays
> feasible when the solver runs out of time.

Trajectory optimization takes the geometric path from
[15-autonomy-motion-planning.md](15-motion-planning.md), respects the
dynamics from [06-autonomy-control-theory.md](06-control-theory.md) and
[09-autonomy-gnc.md](09-gnc.md), and produces the reference the
controller tracks. The optimization theory (Lagrangians, KKT, convexity) is from
[03-foundations-mathematics.md](../foundations/03-mathematics.md); it shares the
nonlinear least-squares machinery of
[14-autonomy-state-estimation-advanced.md](14-state-estimation-advanced.md).
Learned policies that bypass explicit optimization appear in
[17-autonomy-reinforcement-learning.md](17-reinforcement-learning.md). Test
every trajectory in simulation per
[06-foundations-simulation-test-verification.md](../foundations/06-simulation-test-verification.md).

---

## Table of Contents

1. [The optimal control problem](#1-the-optimal-control-problem)
2. [Direct vs indirect methods](#2-direct-vs-indirect-methods)
3. [Shooting and collocation](#3-shooting-and-collocation)
4. [Differential flatness and minimum-snap](#4-differential-flatness-and-minimum-snap)
5. [Model Predictive Control](#5-model-predictive-control)
6. [Solving the QP/NLP in real time](#6-solving-the-qpnlp-in-real-time)
7. [Constraints, feasibility, and robustness](#7-constraints-feasibility-and-robustness)
8. [Practice this week](#8-practice-this-week)
9. [Sources & further study](#9-sources--further-study)
10. [The Insider Layer — what the field knows but rarely writes down](#-the-insider-layer--what-the-field-knows-but-rarely-writes-down)

---

## 1. The optimal control problem

Every trajectory optimization is an instance of the continuous **optimal control
problem (OCP)**: find a state trajectory $\mathbf{x}(t)$ and control $\mathbf{u}(t)$
that minimize a cost subject to dynamics and constraints.

$$
\min_{\mathbf{x}(\cdot),\,\mathbf{u}(\cdot)} \;
\underbrace{\phi(\mathbf{x}(T))}_{\text{terminal}}
+ \int_0^T \underbrace{L(\mathbf{x}(t), \mathbf{u}(t))}_{\text{running cost}}\,dt
$$

subject to

$$
\dot{\mathbf{x}} = f(\mathbf{x}, \mathbf{u}) \;\text{(dynamics)}, \quad
\mathbf{g}(\mathbf{x}, \mathbf{u}) \le 0 \;\text{(path constraints)}, \quad
\mathbf{x}(0) = \mathbf{x}_0.
$$

The running cost $L$ encodes what "good" means — minimize energy
$\|\mathbf{u}\|^2$, time, jerk, or deviation from a reference. The dynamics
constraint is what separates trajectory optimization from mere path smoothing: the
result is *executable*, not just pretty.

---

## 2. Direct vs indirect methods

There are two philosophies for solving the OCP.

| | Indirect ("optimize then discretize") | Direct ("discretize then optimize") |
|---|---|---|
| Idea | derive optimality conditions (Pontryagin), solve the resulting BVP | parameterize $\mathbf{x},\mathbf{u}$ by finitely many variables, hand to an NLP solver |
| Math | Pontryagin's Minimum Principle, costate $\boldsymbol\lambda$ | nonlinear program with KKT conditions |
| Pros | high accuracy, deep insight | robust, handles inequality constraints naturally, dominant in practice |
| Cons | tiny region of convergence, hard with inequalities | discretization error |

**Pontryagin's Minimum Principle** introduces the costate $\boldsymbol\lambda(t)$
and the Hamiltonian $H = L + \boldsymbol\lambda^\top f$; optimality requires

$$
\dot{\boldsymbol\lambda} = -\frac{\partial H}{\partial \mathbf{x}}, \qquad
\mathbf{u}^* = \arg\min_{\mathbf{u}} H(\mathbf{x}, \mathbf{u}, \boldsymbol\lambda).
$$

This is beautiful and occasionally essential (bang-bang time-optimal control falls
out of it), but the modern engineering default is the **direct** approach because
it handles actuator limits and obstacle constraints without heroics.

---

## 3. Shooting and collocation

The two dominant direct transcriptions:

### 3.1 Direct single/multiple shooting

**Single shooting** treats only the controls as decision variables, integrating the
dynamics forward to evaluate the cost. Simple, but errors compound over a long
horizon and the problem becomes ill-conditioned. **Multiple shooting** breaks the
horizon into segments, makes each segment's initial state a variable, and adds
*continuity constraints* between segments:

$$
\mathbf{x}_{k+1} = \text{integrate}(\mathbf{x}_k, \mathbf{u}_k, \Delta t), \qquad
\text{enforce } \mathbf{x}_{k+1}^{seg} = \mathbf{x}_{k}^{end}.
$$

The extra variables decouple the segments, dramatically improving conditioning —
the structure used by ACADO and acados.

### 3.2 Direct collocation

**Collocation** makes *both* states and controls decision variables at discrete
knot points and enforces the dynamics by requiring the derivative of the
interpolating polynomial to match $f$ at collocation points. For Hermite–Simpson,
the defect constraint at each interval is

$$
\mathbf{x}_{k+1} - \mathbf{x}_k = \frac{\Delta t}{6}\big(f_k + 4 f_{k+1/2} + f_{k+1}\big),
$$

with the midpoint state $\mathbf{x}_{k+1/2}$ defined by a Hermite interpolant.
Collocation yields large, *sparse* NLPs (every constraint touches only adjacent
knots) that solvers exploit — the approach behind GPOPS, Drake's trajectory
optimization, and CasADi-based tools.

---

## 4. Differential flatness and minimum-snap

For some systems, trajectory optimization simplifies enormously thanks to
**differential flatness**: the entire state and control can be written as functions
of a few **flat outputs** and their derivatives, with no integration. A quadrotor is
differentially flat in its position and yaw $(\,x, y, z, \psi\,)$ — given those and
their derivatives, you can algebraically recover attitude, angular rates, and motor
commands.

This is why quadrotor planning is done in the flat-output space directly.
Mellinger & Kumar's **minimum-snap** formulation minimizes the integral of the
4th derivative of position (snap), because thrust and body rates depend on
acceleration and jerk — penalizing snap yields trajectories gentle on the motors:

$$
\min_{p(t)} \int_0^T \left\| \frac{d^4 p(t)}{dt^4} \right\|^2 dt,
\qquad p(t) = \sum_{i=0}^{n} c_i\, t^i \;\text{(piecewise polynomial)}.
$$

With the cost quadratic in the polynomial coefficients $\mathbf{c}$ and the
waypoint/continuity conditions linear, the problem is a **quadratic program**:

$$
\min_{\mathbf{c}} \mathbf{c}^\top Q\,\mathbf{c} \quad \text{s.t.}\quad A\mathbf{c} = \mathbf{d},
$$

solvable in closed form. The descendants — **min-snap with corridor constraints**,
**polynomial trajectory generation** (Richter et al.), and the time-allocation
refinement — are the backbone of aggressive quadrotor flight.

---

## 5. Model Predictive Control

**MPC** is trajectory optimization run *in a loop*: at each control step, solve a
finite-horizon OCP from the current measured state, apply only the first control,
then re-solve at the next step with fresh state. This **receding horizon** turns
open-loop optimization into closed-loop feedback that rejects disturbances.

The discrete-time MPC problem over horizon $N$:

$$
\min_{\mathbf{u}_{0:N-1}} \sum_{k=0}^{N-1} \Big( \|\mathbf{x}_k - \mathbf{x}_k^{ref}\|^2_Q + \|\mathbf{u}_k\|^2_R \Big) + \|\mathbf{x}_N - \mathbf{x}_N^{ref}\|^2_{Q_f}
$$

subject to

$$
\mathbf{x}_{k+1} = A\mathbf{x}_k + B\mathbf{u}_k, \quad
\mathbf{u}_{\min} \le \mathbf{u}_k \le \mathbf{u}_{\max}, \quad
\mathbf{x}_{\min} \le \mathbf{x}_k \le \mathbf{x}_{\max}.
$$

For linear dynamics and quadratic cost this is a **convex QP** solved to global
optimality every cycle. For nonlinear dynamics, **NMPC** linearizes and solves a QP
per **SQP** iteration (real-time iteration scheme). The terminal cost $Q_f$ and a
terminal constraint set are what guarantee **recursive feasibility and stability** —
without them, MPC can paint itself into a corner where no feasible control exists.

```
   t                t+1               t+2
   │   ┌─ horizon ─┐                  
   ●───┼───────────┤  solve OCP, apply u₀
       ●───────────┼───────────┤  re-solve from new state
           ●───────┼───────────┼───────────┤
        apply only first control each time (receding horizon)
```

---

## 6. Solving the QP/NLP in real time

A trajectory optimizer is useless if it cannot return before the control deadline.
The numerical structure decides feasibility.

- **QP solvers:** OSQP (operator-splitting, warm-startable, robust), qpOASES
  (active-set, excellent warm starts for MPC), HPIPM (interior-point tailored to
  the MPC block structure).
- **NLP solvers:** IPOPT (interior-point, the workhorse for offline collocation),
  SNOPT (SQP, active-set).
- **Frameworks:** CasADi (automatic differentiation + interfaces to all the above),
  acados (real-time embedded NMPC), Drake.

Two tricks make real-time work:
1. **Warm starting** — seed each solve with the previous solution shifted by one
   step. Because MPC problems change little between cycles, the solver converges in
   a handful of iterations.
2. **Sparsity-exploiting linear algebra** — the OCP's banded KKT system (block
   tridiagonal in time) is factorized in $O(N)$ via a Riccati recursion rather than
   $O(N^3)$ dense factorization.

The KKT system solved each Newton/SQP step:

$$
\begin{bmatrix} H & A^\top \\ A & 0 \end{bmatrix} \begin{bmatrix} \delta\mathbf{z} \\ \delta\boldsymbol\lambda \end{bmatrix} = -\begin{bmatrix} \nabla_z \mathcal{L} \\ \mathbf{c} \end{bmatrix},
$$

where $H$ is the Lagrangian Hessian, $A$ the constraint Jacobian, and the structure
of $H, A$ (banded in time) is what makes it tractable at kHz rates.

---

## 7. Constraints, feasibility, and robustness

### 7.1 Hard vs soft constraints

A hard state constraint (stay in the corridor) can render the QP **infeasible** when
a disturbance pushes the state outside it — and an infeasible MPC has no control to
apply, a safety catastrophe. The standard fix is **soft constraints** via slack
variables $\mathbf{s} \ge 0$ penalized in the cost:

$$
\mathbf{g}(\mathbf{x},\mathbf{u}) \le \mathbf{s}, \qquad \text{add } \rho\,\|\mathbf{s}\|_1 \text{ to cost}.
$$

The $\ell_1$ penalty with large $\rho$ keeps constraints satisfied when possible but
*always* returns a control — graceful degradation instead of a crash.

### 7.2 Robust and tube MPC

Disturbances and model error mean the nominal trajectory will be deviated from.
**Tube MPC** plans a nominal trajectory plus an ancillary feedback controller that
keeps the true state within a bounded "tube" around it, tightening the constraints
by the tube width so the *actual* trajectory stays feasible. This is the principled
way to handle the gap between the model and reality — the same robustness mindset
the controller module brings.

### 7.3 The feasibility-first discipline

The order of priorities for any deployed optimizer: **feasible first, optimal
second.** A slightly suboptimal trajectory that always returns beats an optimal one
that occasionally fails to converge. Always cap solver iterations, always provide a
safe fallback (e.g., the previous trajectory or an emergency brake), and treat a
non-converged solve as a failure to be handled, not ignored.

---

## 8. Practice this week

1. Solve a 1D double-integrator minimum-time problem analytically (bang-bang) via
   Pontryagin, then reproduce it with direct collocation in CasADi.
2. Implement minimum-snap quadrotor trajectory generation through 5 waypoints as a
   closed-form QP; plot position, velocity, acceleration, jerk, snap.
3. Build a linear MPC for a cart-pole with input limits using OSQP; warm-start it
   and measure solve time per cycle.
4. Make a hard state constraint infeasible with a disturbance, then soften it with
   slacks and confirm the controller degrades gracefully.

---

## 9. Sources & further study

- **Betts — *Practical Methods for Optimal Control and Estimation Using Nonlinear
  Programming*.** The reference on direct collocation and shooting.
- **Rawlings, Mayne & Diehl — *Model Predictive Control: Theory, Computation, and
  Design*.** The MPC bible: stability, feasibility, robustness.
- **Mellinger & Kumar — "Minimum Snap Trajectory Generation and Control for
  Quadrotors"** (ICRA, 2011).
- **Kelly — "An Introduction to Trajectory Optimization"** (SIAM Review, 2017). The
  clearest single tutorial.
- **Andersson et al. — "CasADi"** and **Verschueren et al. — "acados".** The
  practical toolchains.
- **Stellato et al. — "OSQP: An Operator Splitting Solver for Quadratic Programs."**
- **Tedrake — *Underactuated Robotics*** (free course notes). Trajectory
  optimization, LQR, and the link to
  [06-autonomy-control-theory.md](06-control-theory.md).

> Framing note: Trajectory optimization is where geometry becomes physics — where a
> path turns into a motion the airframe can actually fly. The engineers who ship
> aggressive, reliable motion are the ones who respect the dynamics in the
> constraints, who exploit flatness and sparsity for speed, and who hold feasibility
> sacred: an optimizer that always returns a safe answer beats a brilliant one that
> sometimes returns none.

---

## ⚡ The Insider Layer — What the Field Knows but Rarely Writes Down

The OCP is clean on paper. Real-time trajectory optimization is a knife fight
with the solver clock, and the winners have a set of habits that rarely make it
into the derivations.

### Warm-starting is the whole game in MPC

The reason MPC runs at 100+ Hz is *not* a fast solver from scratch — it is that
consecutive problems are nearly identical, so you **seed each solve with the
previous solution shifted by one step.** A cold-started NLP that takes 50 ms
warm-starts in 2 ms. This single trick is the difference between MPC being a
research toy and a shipped controller, and it carries a hidden danger: when the
situation changes abruptly (a new obstacle, a mode switch), the warm start is now
a *bad* guess and the solver stalls exactly when you need it most. Veterans keep a
cold-start fallback and a watchdog. The literature presents the QP; the field
presents the warm-start bookkeeping.

### "Feasibility is sacred" means you ship a solver that always returns something

The catastrophic real-time failure is a solver that, given a hard problem and a
deadline, returns *nothing* (infeasible or not converged) while the vehicle is
moving. So production trajectory optimizers are engineered to **always return a
safe, suboptimal answer**: soft-constrain everything that can be soft-constrained
(slack variables with high penalty so constraint violation is expensive but never
makes the problem infeasible), cap iterations, and keep the last feasible
trajectory as a fallback. An MPC that occasionally returns an ugly but safe plan
beats one that returns the optimum 99% of the time and a fault the other 1%. This
"always have an answer" engineering is underemphasized because it's inelegant.

### Differential flatness is a cheat code, and quadrotors are the poster child

For a flat system you can plan the trajectory in the **flat output space** (for a
quadrotor: position + yaw) and recover the full state and controls by
differentiation — no integration of the dynamics, no shooting, the whole
trajectory becomes a polynomial QP. This is *why* minimum-snap quadrotor
trajectories are a solved problem and why aggressive drone flight looks easy in
videos. The non-obvious part: flatness is fragile — add a constraint the flat
parameterization can't express (a thrust limit that depends on battery sag, an
aero effect) and the trick degrades. Knowing whether *your* system is flat, and
how flatness breaks, separates people who can reproduce the demo from people who
think it's magic.

### Collocation vs. shooting is a numerical-conditioning decision

Single shooting is intuitive (integrate forward, optimize the controls) and
**numerically terrible** for anything unstable or long-horizon — small early
control changes blow up at the end, the Jacobian is ill-conditioned, the solver
crawls. Direct collocation discretizes states *and* controls and enforces
dynamics as constraints, trading a bigger but *sparse and well-conditioned*
problem for vastly better convergence. The insider rule of thumb: **shooting for
short, stable horizons; collocation for everything aggressive or unstable.**
People who pick shooting for a rocket-ascent problem learn this the hard way when
the solver won't converge and they blame the model.

### Numbers and norms worth carrying

- **Discretization (number of knot points) is a tax you pay in real time.** Too
  few → the trajectory cheats between nodes (clips obstacles, violates dynamics
  between collocation points); too many → you blow the solve-time budget. This
  knob is tuned empirically per platform, never derived.
- **OSQP / qpOASES for QPs; IPOPT / SNOPT / ACADO / acados for NLPs.** Knowing
  which solver suits your structure (sparse QP vs. dense, SQP vs. interior-point)
  saves orders of magnitude. acados exists specifically to make embedded NLP-MPC
  real-time.
- **MPC's prediction horizon is a stability-vs-cost trade.** Too short and the
  controller is myopic and can drive itself into a corner it can't escape (loss
  of recursive feasibility); too long and you can't solve in time. Terminal cost
  and terminal constraint sets are how you buy stability without a long horizon —
  the part of MPC theory people skip and then wonder why their controller goes
  unstable.
- **Convexify when you possibly can.** Sequential convex programming (SCP) and
  successive convexification turned hard problems (powered rocket landing) into
  things that solve reliably on embedded hardware. A convex problem has a global
  optimum and a time bound; an NLP has neither.

The meta-lesson the textbooks under-sell: trajectory optimization in the lab is
about finding the optimum; in the field it is about *guaranteeing an answer
inside the deadline, every cycle, forever.* The engineers who ship aggressive,
reliable motion hold feasibility sacred, warm-start religiously, and pick the
discretization and solver to match the physics — then let the controller track
what the optimizer promised.
