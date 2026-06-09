# Reinforcement Learning for Control & Autonomy

> **Why this exists.** Classical control and trajectory optimization need a model
> of the dynamics and a hand-crafted cost. But some behaviors are too complex to
> model — recovering from an arbitrary tumble, manipulating deformable objects,
> racing a drone at the edge of its envelope — yet are easy to *evaluate*.
> Reinforcement learning attacks exactly this regime: learn a policy by trial and
> error against a reward signal, with no explicit model required. It is the
> technology behind superhuman game play, robust locomotion controllers, and
> increasingly the high-performance edge of real autonomous systems. But RL is also
> a minefield of instability, reward hacking, and sim-to-real gaps — and an
> autonomy engineer must know exactly where it belongs and where it is malpractice.
>
> **What mastering it makes you.** The engineer who can decide when a learned policy
> earns its place over an MPC, who can design a reward that produces the intended
> behavior instead of a clever exploit, and who treats sim-to-real and safety as the
> central engineering problems rather than afterthoughts.

RL formalizes the decision-making of
[29-autonomy-planning-decision.md](29-planning-decision.md) as an MDP and
is the learning counterpart to the model-based optimization of
[55-autonomy-trajectory-optimization.md](55-trajectory-optimization.md). It
shares the neural-network and gradient machinery of
[20-autonomy-ml-ai.md](20-ml-ai.md), rests on the probability and
optimization of [03-foundations-mathematics.md](../foundations/03-mathematics.md), and
ultimately commands the dynamics studied in
[25-autonomy-control-theory.md](25-control-theory.md). It pairs tightly
with [57-autonomy-imitation-and-learning-from-demo.md](57-imitation-and-learning-from-demo.md),
and every learned policy must be stress-tested per
[06-foundations-simulation-test-verification.md](../foundations/06-simulation-test-verification.md).

---

## Table of Contents

1. [The Markov Decision Process](#1-the-markov-decision-process)
2. [Value functions and the Bellman equation](#2-value-functions-and-the-bellman-equation)
3. [Value-based methods — Q-learning to DQN](#3-value-based-methods--q-learning-to-dqn)
4. [Policy gradients and actor-critic](#4-policy-gradients-and-actor-critic)
5. [The modern workhorses — PPO and SAC](#5-the-modern-workhorses--ppo-and-sac)
6. [Model-based RL](#6-model-based-rl)
7. [Sim-to-real, reward design, and safety](#7-sim-to-real-reward-design-and-safety)
8. [Practice this week](#8-practice-this-week)
9. [Sources & further study](#9-sources--further-study)

---

## 1. The Markov Decision Process

RL is the theory of acting in a **Markov Decision Process** $(\mathcal{S}, \mathcal{A}, P, R, \gamma)$:
states $\mathcal{S}$, actions $\mathcal{A}$, transition kernel
$P(s' \mid s, a)$, reward $R(s, a)$, and discount $\gamma \in [0,1)$. A **policy**
$\pi(a \mid s)$ maps states to action distributions. The goal is to maximize the
expected discounted return:

$$
J(\pi) = \mathbb{E}_{\tau \sim \pi}\left[ \sum_{t=0}^{\infty} \gamma^t R(s_t, a_t) \right].
$$

The **Markov property** — the future depends on the past only through the present
state — is what makes the problem tractable, and *designing a state that is actually
Markov* is the first and most underrated engineering decision. A control problem
that looks non-Markov (velocity matters but you only observe position) becomes
Markov once you augment the state correctly; get this wrong and no algorithm can
succeed. Partial observability is handled formally by a **POMDP**, where the agent
acts on a belief over states (linking back to the filters of
[52-autonomy-sensor-fusion.md](52-sensor-fusion.md)).

---

## 2. Value functions and the Bellman equation

The **value function** $V^\pi(s)$ is the expected return starting from $s$ under
$\pi$; the **action-value** $Q^\pi(s,a)$ conditions also on the first action. Both
satisfy a recursive self-consistency — the **Bellman equation**:

$$
V^\pi(s) = \mathbb{E}_{a\sim\pi}\Big[ R(s,a) + \gamma\,\mathbb{E}_{s'}\big[V^\pi(s')\big] \Big],
$$

$$
Q^\pi(s,a) = R(s,a) + \gamma\,\mathbb{E}_{s'\sim P}\Big[ \mathbb{E}_{a'\sim\pi} Q^\pi(s', a') \Big].
$$

The **optimal** value function satisfies the **Bellman optimality equation**, which
replaces the expectation over actions with a maximum:

$$
Q^*(s,a) = R(s,a) + \gamma\,\mathbb{E}_{s'}\Big[ \max_{a'} Q^*(s', a') \Big].
$$

This equation is the load-bearing wall of RL. The optimal policy is greedy with
respect to $Q^*$: $\pi^*(s) = \arg\max_a Q^*(s,a)$. Every algorithm below is, at
heart, a way to approximate a solution to this fixed-point equation when $P$ is
unknown and the state space is too large to enumerate. The Bellman operator is a
**$\gamma$-contraction** in the sup-norm, which is *why* value iteration converges —
the same contraction-mapping logic from dynamic programming.

---

## 3. Value-based methods — Q-learning to DQN

**Q-learning** learns $Q^*$ from sampled transitions $(s,a,r,s')$ without a model,
by nudging $Q$ toward the Bellman target:

$$
Q(s,a) \leftarrow Q(s,a) + \alpha\Big[ \underbrace{r + \gamma \max_{a'} Q(s', a')}_{\text{TD target}} - Q(s,a) \Big].
$$

The bracketed quantity is the **temporal-difference (TD) error** — the surprise
between predicted and bootstrapped value. Q-learning is **off-policy**: it learns
the optimal policy while behaving exploratorily (e.g., $\varepsilon$-greedy).

**Deep Q-Networks (DQN)** scale this to high-dimensional states with a neural
approximator $Q_\theta$, stabilized by two essential tricks:
- **Experience replay** — store transitions and sample minibatches, breaking the
  temporal correlation that destabilizes SGD.
- **Target network** — a slowly-updated copy $Q_{\theta^-}$ provides the TD target,
  preventing the "chasing a moving target" divergence.

$$
\mathcal{L}(\theta) = \mathbb{E}\Big[ \big( r + \gamma \max_{a'} Q_{\theta^-}(s', a') - Q_\theta(s,a) \big)^2 \Big].
$$

DQN works for **discrete** actions; continuous control (steering, thrust) needs
policy methods.

---

## 4. Policy gradients and actor-critic

For continuous actions, parameterize the policy $\pi_\theta(a\mid s)$ directly and
ascend $J(\theta)$ by gradient. The **policy gradient theorem** gives an estimator
that needs no model:

$$
\nabla_\theta J(\theta) = \mathbb{E}_{\tau\sim\pi_\theta}\left[ \sum_t \nabla_\theta \log \pi_\theta(a_t\mid s_t)\, A^\pi(s_t, a_t) \right],
$$

where $A^\pi(s,a) = Q^\pi(s,a) - V^\pi(s)$ is the **advantage** — how much better
action $a$ is than the policy's average. The intuition is direct: increase the
log-probability of actions that beat expectation, decrease it for those that fall
short.

**Actor-critic** methods learn both an actor $\pi_\theta$ and a critic
$V_\phi$ (or $Q_\phi$) that estimates the advantage, drastically reducing the
variance of the raw Monte-Carlo gradient. The **Generalized Advantage Estimator
(GAE)** trades bias against variance with a parameter $\lambda$:

$$
\hat{A}_t = \sum_{l=0}^{\infty} (\gamma\lambda)^l \delta_{t+l}, \qquad
\delta_t = r_t + \gamma V_\phi(s_{t+1}) - V_\phi(s_t).
$$

---

## 5. The modern workhorses — PPO and SAC

### 5.1 PPO — the robust default

Vanilla policy gradients take destructive steps when the policy changes too much in
one update. **Proximal Policy Optimization (PPO)** clips the policy ratio
$r_t(\theta) = \pi_\theta(a_t\mid s_t)/\pi_{\theta_\text{old}}(a_t\mid s_t)$ so no
single update moves the policy too far:

$$
\mathcal{L}^{\text{PPO}}(\theta) = \mathbb{E}_t\Big[ \min\big( r_t(\theta)\hat{A}_t,\ \mathrm{clip}(r_t(\theta), 1-\epsilon, 1+\epsilon)\hat{A}_t \big) \Big].
$$

PPO is on-policy, simple, and astonishingly robust — the default for locomotion,
manipulation, and most real robot RL. It is what trains the quadruped and humanoid
controllers now running on ANYmal, Spot-class robots, and Cassie.

### 5.2 SAC — sample-efficient off-policy

**Soft Actor-Critic (SAC)** maximizes reward *plus entropy*, encouraging
exploration and robustness, and is off-policy (reuses a replay buffer) so it is far
more sample-efficient than PPO:

$$
J(\pi) = \mathbb{E}\left[ \sum_t \gamma^t \big( R(s_t,a_t) + \alpha\, \mathcal{H}(\pi(\cdot\mid s_t)) \big) \right].
$$

The entropy term $\mathcal{H}$ keeps the policy stochastic until the reward justifies
commitment, which empirically yields smoother, more robust real-robot policies. The
temperature $\alpha$ is auto-tuned to hit a target entropy.

| Algorithm | On/off-policy | Action space | Sample efficiency | Stability |
|---|---|---|---|---|
| DQN | off | discrete | medium | needs tricks |
| PPO | on | both | low | very high |
| SAC | off | continuous | high | high |
| TD3 | off | continuous | high | high (twin critics) |

---

## 6. Model-based RL

Model-free RL (above) needs millions of environment steps — fine in simulation,
ruinous on hardware. **Model-based RL** learns a dynamics model
$\hat{P}_\psi(s'\mid s,a)$ and plans or trains against it, slashing the real-world
sample count by orders of magnitude.

- **Dyna-style:** use the learned model to generate synthetic transitions that
  augment real data.
- **MPC with a learned model (e.g., PETS):** plan actions by optimizing predicted
  return over the learned model each step — RL meets the MPC of
  [55-autonomy-trajectory-optimization.md](55-trajectory-optimization.md).
- **Latent-imagination (Dreamer):** learn a compact latent dynamics model and train
  the policy purely "in imagination" by rolling out the latent model.

The central risk is **model exploitation**: the policy finds and abuses the regions
where the learned model is wrong (predicting free reward where the real world gives
none). Remedies — ensembles to quantify model uncertainty, penalizing actions that
venture into high-uncertainty states — are the heart of practical model-based RL.

---

## 7. Sim-to-real, reward design, and safety

This section is where RL succeeds or fails as *engineering*.

### 7.1 The sim-to-real gap

A policy trained in simulation meets a real world with different friction, latency,
mass, and sensor noise. The dominant bridge is **domain randomization**: train
across a distribution of simulated dynamics so the policy learns a strategy robust
to the *range* that contains reality.

$$
\max_\theta\; \mathbb{E}_{\xi\sim p(\xi)}\, \mathbb{E}_{\tau\sim\pi_\theta,\,\xi}\!\left[ \sum_t \gamma^t R_t \right],
$$

where $\xi$ parameterizes randomized physics (friction, mass, delays, sensor bias).
A policy that survives this distribution typically survives reality. Complementary
tactics: **system identification** to center the randomization on the true robot,
and **domain adaptation** to fine-tune on a little real data.

### 7.2 Reward design and reward hacking

The reward function *is* the specification. RL optimizes it literally and ruthlessly,
so a misspecified reward yields **reward hacking** — the boat that spins in circles
collecting points instead of finishing the race, the arm that vibrates to trick a
"contact" sensor. Principles:
- Reward the **outcome**, shape sparingly. Heavy reward shaping leaks the designer's
  (possibly wrong) idea of the solution and invites exploits.
- **Potential-based shaping** $F(s,s') = \gamma\,\Phi(s') - \Phi(s)$ is the only
  shaping form *proven* not to change the optimal policy — use it when you must shape.
- Add explicit **penalty terms** for the exploit the moment you observe it; expect
  to iterate the reward many times.

### 7.3 Safe RL

A policy that learns by trial and error cannot be turned loose on hardware where a
mistake means a crash. The standard architecture wraps the learned policy in a
**safety layer** that the policy cannot override — exactly the "slow proposes, fast
disposes" trust boundary from
[29-autonomy-planning-decision.md](29-planning-decision.md):
- **Constrained MDPs (CMDP):** maximize reward subject to an expected-cost
  constraint $\mathbb{E}[\sum \gamma^t C_t] \le d$, solved by Lagrangian methods
  (CPO, Lagrangian-PPO).
- **Control-barrier-function shields:** a verified filter projects the policy's
  action onto the nearest safe action that keeps the system in a provably invariant
  safe set.
- **Recovery / fallback controllers:** a classical, verified controller that takes
  over the instant a safety monitor trips.

The discipline: **never let an unbounded learned model command an unbounded
actuator without a verified outer guard.** This is the single rule that separates a
research demo from a fieldable autonomous system.

---

## 8. Practice this week

1. Implement tabular Q-learning on FrozenLake / a gridworld; visualize the learned
   $Q^*$ and confirm it satisfies the Bellman optimality equation.
2. Train PPO on CartPole and HalfCheetah with Stable-Baselines3; plot return and
   tune GAE $\lambda$.
3. Train SAC on a continuous task and compare its sample efficiency to PPO.
4. Deliberately mis-specify a reward to induce reward hacking, then fix it with a
   potential-based shaping term and an explicit penalty.
5. Add domain randomization to a simulated cart-pole and measure robustness to a
   mass/friction shift.

---

## 9. Sources & further study

- **Sutton & Barto — *Reinforcement Learning: An Introduction*** (2nd ed., free).
  The foundational text: MDPs, Bellman, TD, policy gradients.
- **Schulman et al. — "Proximal Policy Optimization Algorithms"** (2017) and
  **"High-Dimensional Continuous Control Using GAE"** (2016).
- **Haarnoja et al. — "Soft Actor-Critic"** (ICML, 2018).
- **Mnih et al. — "Human-Level Control through Deep Reinforcement Learning" (DQN)**
  (Nature, 2015).
- **Hafner et al. — "Dream to Control" (Dreamer)** and **Chua et al. — "PETS".**
- **Tobin et al. — "Domain Randomization for Transferring Deep Neural Networks from
  Simulation to the Real World"** (IROS, 2017).
- **Achiam et al. — "Constrained Policy Optimization"** (ICML, 2017); **Ames et al.
  — "Control Barrier Functions" survey.**
- **Hwangbo et al. — "Learning Agile and Dynamic Motor Skills for Legged Robots"**
  (Science Robotics, 2019) — landmark sim-to-real.

> Framing note: Reinforcement learning is not a replacement for control theory — it
> is a tool for the regime where modeling is hard but evaluation is easy. The
> engineers who deploy it safely are the ones who obsess over the reward as a
> specification, who treat sim-to-real as the core problem, and who never remove the
> verified guard between a learned policy and a real actuator.
