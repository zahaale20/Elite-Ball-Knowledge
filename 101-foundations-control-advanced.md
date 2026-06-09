# Advanced Control — Optimal, Robust & Model Predictive Control

> **Why this exists.** Basic PID gets a quadcopter to hover, but it does not tell you the *best* feedback law, nor what happens when your model is wrong, your sensors are noisy, or an adversary is jamming your GPS. Advanced control is the mathematics of doing the optimal thing under uncertainty and constraints — minimizing fuel while tracking a trajectory, guaranteeing stability margins against unmodeled dynamics, respecting actuator limits in real time. Every serious autonomy stack — guidance, attitude control, energy management — eventually graduates from hand-tuned gains to optimal and robust synthesis. This module is where intuition becomes provable guarantee.

> **What mastering it makes you.** The engineer who can stand in front of a flight-test review board and *prove* that the vehicle is stable with 6 dB of gain margin and 45° of phase margin, who can size an MPC horizon to respect thrust saturation, and who can explain why the Kalman filter and the LQR regulator are mathematically dual. You become the person trusted to certify the loop, not just close it.

This module is the rigorous continuation of [25-autonomy-control-theory.md](25-autonomy-control-theory.md) and feeds directly into guidance and navigation in [28-autonomy-gnc.md](28-autonomy-gnc.md) and decision-making in [29-autonomy-planning-decision.md](29-autonomy-planning-decision.md). The linear-algebra and calculus machinery comes from [03-foundations-mathematics.md](03-foundations-mathematics.md); the systems-engineering framing of *requirements as constraints* comes from [01_first_principles_systems_engineering.md](01_first_principles_systems_engineering.md). For the physics of the plants we control, see [102-foundations-physics-for-engineers.md](102-foundations-physics-for-engineers.md); for the estimation theory dual to optimal control, see [53-autonomy-state-estimation-advanced.md](53-autonomy-state-estimation-advanced.md). Decision-theoretic adversaries appear in [105-foundations-decision-and-game-theory.md](105-foundations-decision-and-game-theory.md).

---

## 1. The state-space picture and what "optimal" means

We model a plant as a linear time-invariant (LTI) system

$$
\dot{x} = A x + B u, \qquad y = C x + D u,
$$

where $x \in \mathbb{R}^n$ is the state, $u \in \mathbb{R}^m$ the control, $y \in \mathbb{R}^p$ the output. The pair $(A, B)$ is **controllable** if the controllability matrix

$$
\mathcal{C} = \begin{bmatrix} B & AB & A^2 B & \cdots & A^{n-1} B \end{bmatrix}
$$

has rank $n$ — meaning there exists an input that can drive the state anywhere. Dually, $(A, C)$ is **observable** if

$$
\mathcal{O} = \begin{bmatrix} C \\ CA \\ \vdots \\ CA^{n-1} \end{bmatrix}
$$

has rank $n$ — meaning the output history uniquely determines the state. These two conditions are the bedrock: you cannot optimally control what you cannot steer, and you cannot estimate what you cannot see.

"Optimal" requires a **cost functional**. The canonical choice — quadratic in state and control — gives the cleanest theory and surprisingly good practice:

$$
J = \int_0^\infty \left( x^\top Q x + u^\top R u \right) dt, \qquad Q = Q^\top \succeq 0, \; R = R^\top \succ 0.
$$

$Q$ penalizes deviation; $R$ penalizes effort. The ratio of their eigenvalues encodes the classic engineering tradeoff: aggressive tracking versus actuator wear and energy.

---

## 2. The Linear-Quadratic Regulator (LQR)

We seek the feedback $u = -Kx$ that minimizes $J$. The solution is one of the most beautiful results in control: it reduces to an algebraic matrix equation.

### 2.1 Derivation via the value function

Posit a quadratic value function $V(x) = x^\top P x$ with $P \succ 0$. The **Hamilton–Jacobi–Bellman (HJB)** equation for the infinite-horizon problem requires

$$
\min_u \left[ x^\top Q x + u^\top R u + \nabla V^\top (Ax + Bu) \right] = 0.
$$

With $\nabla V = 2Px$, differentiate the bracket with respect to $u$ and set to zero:

$$
2 R u + 2 B^\top P x = 0 \;\Longrightarrow\; u^\star = -R^{-1} B^\top P\, x.
$$

So the optimal gain is $K = R^{-1} B^\top P$. Substituting $u^\star$ back and requiring the bracket to vanish for all $x$ yields the **Continuous Algebraic Riccati Equation (CARE)**:

$$
\boxed{\,A^\top P + P A - P B R^{-1} B^\top P + Q = 0.\,}
$$

The unique stabilizing $P \succ 0$ exists whenever $(A,B)$ is controllable and $(A, Q^{1/2})$ is observable. The closed loop $\dot x = (A - BK)x$ is then guaranteed asymptotically stable.

### 2.2 Worked example — double integrator

Take a unit-mass point: $\ddot p = u$, so $A = \begin{bmatrix} 0 & 1 \\ 0 & 0 \end{bmatrix}$, $B = \begin{bmatrix} 0 \\ 1 \end{bmatrix}$. Choose $Q = \operatorname{diag}(q, 0)$, $R = r$. Solving CARE gives the gain

$$
K = \begin{bmatrix} \sqrt{q/r} & \sqrt{2}\,(q/r)^{1/4} \end{bmatrix},
$$

a position gain growing as $\sqrt{q/r}$ and a velocity (damping) gain producing closed-loop poles at $-\omega_n(\tfrac{1}{\sqrt2} \pm j\tfrac{1}{\sqrt2})$ with $\omega_n = (q/r)^{1/4}$ — exactly a damping ratio $\zeta = 1/\sqrt2 \approx 0.707$, the "maximally flat" Butterworth response. The cost functional *automatically* produced the textbook-ideal damping.

```python
import numpy as np
from scipy.linalg import solve_continuous_are

A = np.array([[0., 1.], [0., 0.]])
B = np.array([[0.], [1.]])
Q = np.diag([1.0, 0.0])
R = np.array([[0.01]])

P = solve_continuous_are(A, B, Q, R)
K = np.linalg.inv(R) @ B.T @ P
print("Gain K =", K)                       # [10.0, 4.47]
print("Closed-loop poles:", np.linalg.eigvals(A - B @ K))
```

### 2.3 Guaranteed margins

A remarkable property: every LQR loop has an **infinite gain margin** (you can multiply the loop gain by any factor $\geq \tfrac12$) and at least **60° of phase margin**. This robustness is *free* in the single-input case — a key reason LQR is the default for inner-loop attitude control on real aircraft.

---

## 3. Estimation and LQG — separation and duality

In practice $x$ is not measured directly. Model process and sensor noise:

$$
\dot x = Ax + Bu + w, \qquad y = Cx + v,
$$

with $w \sim \mathcal{N}(0, W)$, $v \sim \mathcal{N}(0, V)$. The optimal state estimate is produced by the **Kalman–Bucy filter**

$$
\dot{\hat x} = A\hat x + Bu + L\,(y - C\hat x), \qquad L = \Sigma C^\top V^{-1},
$$

where $\Sigma$ solves the *dual* Riccati equation

$$
A\Sigma + \Sigma A^\top - \Sigma C^\top V^{-1} C \Sigma + W = 0.
$$

Compare to CARE: $A \leftrightarrow A^\top$, $B \leftrightarrow C^\top$, $Q \leftrightarrow W$, $R \leftrightarrow V$. **Control and estimation are mathematical duals.** This is why mastering one halves the work of learning the other (see [53-autonomy-state-estimation-advanced.md](53-autonomy-state-estimation-advanced.md)).

The **Separation Principle** states that the optimal output-feedback controller is simply $u = -K\hat x$: design the regulator and the estimator independently, then plug the estimate into the gain. The combined controller is called **LQG (Linear-Quadratic-Gaussian)**.

> **Caution.** LQG has *no* guaranteed robustness margins (the famous Doyle 1978 counterexample). The clean LQR margins are destroyed by the estimator. This motivates loop-transfer recovery and, more fundamentally, robust control.

---

## 4. Robust control — designing for the model you don't have

Real plants differ from the model $P_0$ by an uncertainty $\Delta$. We want stability for *every* plant in a set $\{ P_0(I + \Delta W) : \|\Delta\|_\infty \le 1\}$.

### 4.1 The small-gain theorem

For a feedback interconnection of stable systems $M$ and $\Delta$, the loop is stable if

$$
\|M\|_\infty \, \|\Delta\|_\infty < 1,
$$

where the $\mathcal{H}_\infty$ norm $\|M\|_\infty = \sup_\omega \bar\sigma\!\big(M(j\omega)\big)$ is the peak gain over all frequencies (the largest singular value). This is the multivariable generalization of "keep the loop gain below 1 where the model is uncertain."

### 4.2 $\mathcal{H}_\infty$ synthesis

We shape the closed-loop **sensitivity** $S = (I + PK)^{-1}$ and **complementary sensitivity** $T = PK(I+PK)^{-1}$, which obey the algebraic identity $S + T = I$ — you cannot make both small at the same frequency. The mixed-sensitivity problem minimizes

$$
\left\| \begin{matrix} W_S S \\ W_T T \end{matrix} \right\|_\infty,
$$

with weighting filters $W_S$ (low-frequency tracking/disturbance rejection) and $W_T$ (high-frequency robustness). The solution comes from a pair of coupled Riccati equations (Doyle–Glover–Khargonekar–Francis, 1989). The payoff: a controller with *certified* stability against a quantified uncertainty ball — exactly what flight certification demands.

| Method | Optimizes | Robustness guarantee | Handles constraints? |
|---|---|---|---|
| PID | hand-tuned | none formal | no |
| LQR | quadratic cost | $\infty$ gain / 60° phase (SISO) | no |
| LQG | cost + noise | none guaranteed | no |
| $\mathcal{H}_\infty$ | worst-case gain | $\|\Delta\|_\infty < 1$ | no |
| MPC | cost over horizon | nominal (tube-MPC: robust) | **yes** |

---

## 5. Lyapunov stability — the universal certificate

Optimal-control proofs and nonlinear stability both rest on **Lyapunov's direct method**. For $\dot x = f(x)$ with equilibrium at the origin, if there exists $V(x) > 0$ (positive definite) with

$$
\dot V = \nabla V^\top f(x) < 0 \quad \text{for all } x \neq 0,
$$

then the origin is asymptotically stable. $V$ is a generalized "energy" that always decreases. The LQR value function $V = x^\top P x$ is itself a Lyapunov function: along the closed loop,

$$
\dot V = x^\top\!\big( (A-BK)^\top P + P(A-BK) \big) x = -x^\top (Q + K^\top R K)\, x < 0.
$$

So solving CARE simultaneously yields the optimal gain *and* the stability certificate. For nonlinear systems, **control Lyapunov functions (CLFs)** generalize this: any $u$ making $\dot V < 0$ stabilizes the system, and you can pick the one that also minimizes effort. CLF–QP controllers are now standard in legged robotics and aggressive UAV maneuvering.

---

## 6. Model Predictive Control (MPC)

MPC is the workhorse when **constraints** matter — thrust saturation, no-fly zones, battery limits. At each timestep, solve a finite-horizon optimization, apply the first control, then re-solve (receding horizon).

### 6.1 The QP formulation

For the discrete model $x_{k+1} = A_d x_k + B_d u_k$, solve over horizon $N$:

$$
\min_{u_0,\dots,u_{N-1}} \; \sum_{k=0}^{N-1} \big( x_k^\top Q x_k + u_k^\top R u_k \big) + x_N^\top P x_N
$$

$$
\text{s.t.}\quad x_{k+1} = A_d x_k + B_d u_k, \quad u_{\min} \le u_k \le u_{\max}, \quad x_k \in \mathcal{X}.
$$

With linear dynamics and quadratic cost this is a **convex quadratic program (QP)**, solvable in microseconds by interior-point or active-set solvers (OSQP, qpOASES) — fast enough for kHz-rate attitude loops.

### 6.2 Stability of the receding horizon

Naively truncating the horizon can *destabilize*. The fix: choose the terminal cost $P$ as the LQR solution and add a terminal constraint $x_N \in \mathcal{X}_f$ (an invariant set under the LQR law). Then the optimal cost-to-go is a Lyapunov function and recursive feasibility guarantees stability. This is the bridge between MPC and LQR: **MPC with an infinite horizon and no active constraints *is* LQR.**

```python
import numpy as np, cvxpy as cp

A_d = np.array([[1., 0.1],[0., 1.]]); B_d = np.array([[0.005],[0.1]])
Q, R = np.eye(2), np.array([[0.1]]); N = 20
x0 = np.array([5., 0.]); u_max = 1.0

x = cp.Variable((2, N+1)); u = cp.Variable((1, N))
cost, cons = 0, [x[:, 0] == x0]
for k in range(N):
    cost += cp.quad_form(x[:, k], Q) + cp.quad_form(u[:, k], R)
    cons += [x[:, k+1] == A_d @ x[:, k] + B_d @ u[:, k]]
    cons += [cp.abs(u[:, k]) <= u_max]          # actuator saturation
cp.Problem(cp.Minimize(cost), cons).solve()
print("First optimal control:", u.value[0, 0])
```

---

## 7. Adaptive control — learning the plant online

When parameters drift (mass changes as fuel burns, aerodynamic coefficients vary with Mach), **adaptive control** estimates them in the loop. Model Reference Adaptive Control (MRAC) drives the plant to follow a reference model $\dot x_m = A_m x_m + B_m r$. With parameter error $\tilde\theta$, the **MIT/Lyapunov adaptation law**

$$
\dot{\hat\theta} = -\gamma\, e\, \phi(x),
$$

is derived by choosing $V = e^\top P e + \tfrac1\gamma \tilde\theta^\top \tilde\theta$ and forcing $\dot V \le 0$. The tracking error $e$ and the regressor $\phi$ drive parameter learning while Lyapunov theory guarantees boundedness. $\mathcal{L}_1$ adaptive control later decoupled adaptation speed from robustness, enabling fast adaptation with guaranteed transients — now flown on experimental UAVs.

---

## 8. Putting it together — the autonomy control stack

| Loop | Rate | Method | Why |
|---|---|---|---|
| Inner attitude | 500–1000 Hz | LQR / robust | margins, simplicity, speed |
| Position / velocity | 50–200 Hz | MPC | thrust & tilt constraints |
| Trajectory / guidance | 1–10 Hz | optimal control / DDP | fuel-optimal paths |
| Mission / decision | < 1 Hz | game theory, planning | adversaries, logic |

This cascade mirrors the systems-engineering principle of separating timescales (see [01_first_principles_systems_engineering.md](01_first_principles_systems_engineering.md)). The outer loops set references; the inner loops enforce them with certified stability. The guidance layer connects to [28-autonomy-gnc.md](28-autonomy-gnc.md), and the adversarial mission layer to [105-foundations-decision-and-game-theory.md](105-foundations-decision-and-game-theory.md) and [29-autonomy-planning-decision.md](29-autonomy-planning-decision.md).

---

## 9. Common failure modes and how the theory catches them

- **Integrator windup** under saturation — MPC handles it natively; PID needs anti-windup clamping.
- **Right-half-plane zeros** impose fundamental bandwidth limits (Bode integral: $\int_0^\infty \ln|S(j\omega)|\,d\omega = \pi \sum \mathrm{Re}(p_k)$ — the "waterbed effect"; suppress sensitivity here, it pops up there).
- **Time delay** erodes phase margin at $-\omega\tau$ radians; Smith predictors or robust design recover it.
- **Unmodeled flexible modes** alias into the loop — $W_T$ weighting in $\mathcal{H}_\infty$ rolls off the loop before they bite.

---

## Sources & further study

- Åström & Murray, *Feedback Systems: An Introduction for Scientists and Engineers* (2nd ed.) — the canonical modern reference; free online.
- Anderson & Moore, *Optimal Control: Linear Quadratic Methods* — LQR/LQG with full rigor.
- Zhou, Doyle & Glover, *Robust and Optimal Control* — the definitive $\mathcal{H}_\infty$ text.
- Rawlings, Mayne & Diehl, *Model Predictive Control: Theory, Computation, and Design* — stability theory of MPC.
- Khalil, *Nonlinear Systems* (3rd ed.) — Lyapunov theory and adaptive control.
- Bertsekas, *Dynamic Programming and Optimal Control* — the DP/HJB foundation.
- Ioannou & Sun, *Robust Adaptive Control* — MRAC and $\mathcal{L}_1$ background.

> Framing note: Optimal control answers "what is the best feedback?", robust control answers "best against which plants?", and MPC answers "best subject to which constraints?". Real autonomy needs all three answers simultaneously, layered by timescale. The engineer who internalizes the LQR–Kalman duality and the $S+T=I$ tradeoff is no longer tuning gains — they are *negotiating* with physics, and they know exactly what they are giving up.
