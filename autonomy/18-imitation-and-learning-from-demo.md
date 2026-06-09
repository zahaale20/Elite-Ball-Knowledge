# Imitation Learning & Learning from Demonstration

> **Why this exists.** Reinforcement learning needs a reward function and millions
> of trials. But often the easiest way to specify a behavior is to *show* it: a
> human drives the route, teleoperates the grasp, or flies the maneuver. Imitation
> learning turns demonstrations into policies — bypassing reward design entirely and
> learning complex, hard-to-specify skills directly from expert data. It is the
> fastest path from "a person can do this" to "the robot can do this," and it
> underpins much of modern self-driving, robot manipulation, and the new wave of
> generalist robot policies. But it carries a subtle, deadly failure mode —
> compounding error from distribution shift — that every practitioner must
> understand cold.
>
> **What mastering it makes you.** The engineer who knows why naïve behavioral
> cloning drifts off the road after a few seconds, who can choose between DAgger,
> inverse RL, and a diffusion policy for a given problem, and who treats the gap
> between the expert's state distribution and the policy's own as the central
> technical challenge.

Imitation learning is the demonstration-driven counterpart to the reward-driven
methods of [17-autonomy-reinforcement-learning.md](17-reinforcement-learning.md),
shares the supervised-learning and neural-network machinery of
[01-autonomy-ml-ai.md](01-ml-ai.md), and produces policies that command the
dynamics of [06-autonomy-control-theory.md](06-control-theory.md). It is a
learned alternative to the explicit planners of
[15-autonomy-motion-planning.md](15-motion-planning.md) and
[16-autonomy-trajectory-optimization.md](16-trajectory-optimization.md),
rests on the probability of
[03-foundations-mathematics.md](../foundations/03-mathematics.md), and must be
validated against distribution shift per
[06-foundations-simulation-test-verification.md](../foundations/06-simulation-test-verification.md).

---

## Table of Contents

1. [The imitation learning problem](#1-the-imitation-learning-problem)
2. [Behavioral cloning and its fatal flaw](#2-behavioral-cloning-and-its-fatal-flaw)
3. [Distribution shift and compounding error](#3-distribution-shift-and-compounding-error)
4. [DAgger — fixing the distribution](#4-dagger--fixing-the-distribution)
5. [Inverse reinforcement learning](#5-inverse-reinforcement-learning)
6. [Generative and diffusion policies](#6-generative-and-diffusion-policies)
7. [Practice and pitfalls in the real world](#7-practice-and-pitfalls-in-the-real-world)
8. [Practice this week](#8-practice-this-week)
9. [Sources & further study](#9-sources--further-study)

---

## 1. The imitation learning problem

Given a dataset of expert demonstrations
$\mathcal{D} = \{(s_i, a_i)\}_{i=1}^{N}$ drawn from an expert policy $\pi^*$,
learn a policy $\pi_\theta$ that reproduces the expert's behavior. There are two
fundamentally different framings:

| Approach | Learns | Assumption | Strength |
|---|---|---|---|
| **Behavioral cloning (BC)** | the policy directly, $\pi_\theta \approx \pi^*$ | states are i.i.d. (false!) | simple, one supervised fit |
| **Inverse RL (IRL)** | the *reward* the expert optimizes, then RL on it | expert is (near-)optimal | generalizes, recovers intent |

BC asks "what action did the expert take here?"; IRL asks "what was the expert
*trying to achieve*?" The second is harder but transfers far better to new
situations, because a reward generalizes where a memorized state-action map does
not.

---

## 2. Behavioral cloning and its fatal flaw

Behavioral cloning is plain supervised learning: minimize the discrepancy between
the policy's action and the expert's over the demonstration states.

$$
\theta^* = \arg\min_\theta \mathbb{E}_{(s,a)\sim\mathcal{D}}\big[ \ell(\pi_\theta(s), a) \big],
$$

with $\ell$ a cross-entropy (discrete) or regression (continuous) loss. It is
trivial to implement and works *during training*. NVIDIA's end-to-end
**PilotNet** (camera-to-steering) and countless manipulation policies are BC.

The fatal flaw is that the i.i.d. assumption of supervised learning is **false for
sequential decisions**. The policy is trained on the *expert's* state distribution
$d_{\pi^*}$ but at deployment it visits *its own* distribution $d_{\pi_\theta}$. The
moment it makes a small error it enters a state the expert never demonstrated, where
its action is undefined, causing a larger error — a runaway feedback loop.

---

## 3. Distribution shift and compounding error

The theory (Ross & Bagnell) makes the failure precise. If BC achieves per-step error
$\epsilon$ under the expert distribution, the *worst-case* return gap over a horizon
$T$ grows **quadratically**:

$$
J(\pi^*) - J(\pi_\theta) \;\le\; \mathcal{O}(\epsilon\, T^2).
$$

The $T^2$ — not $T$ — is the whole story. A 1% per-step error does not give a 1%
worse trajectory; it gives a trajectory that diverges catastrophically because each
error moves the policy into less-familiar states, raising the next error.

```
   expert distribution d_π*        policy drifts outside it
   ┌───────────────────┐
   │  ●●●●●●●●●●●●      │   small error →  ╲
   │  demonstrated      │                   ╲  no training data here,
   │  states            │                    ╲ error compounds →
   └───────────────────┘                      ✗ off the road
```

This is why a BC self-driving policy can follow the lane for ten seconds and then
veer off: it was never shown how to *recover* from the off-center states its own
mistakes create. The cure is to make the training distribution match the policy's
own — the insight behind DAgger.

---

## 4. DAgger — fixing the distribution

**DAgger (Dataset Aggregation)** breaks the compounding loop by gathering expert
labels *on the states the policy actually visits*. Roll out the current policy, ask
the expert what it *would* have done at each visited state, add those labels to the
dataset, and retrain — iterating until the policy's distribution and the labels
agree.

```python
def dagger(expert, env, iters):
    D = collect_expert_demos(expert, env)     # seed
    pi = train_bc(D)
    for _ in range(iters):
        states = rollout(pi, env)             # policy's OWN distribution
        labels = [expert.action(s) for s in states]   # expert labels them
        D += zip(states, labels)              # aggregate
        pi = train_bc(D)                      # retrain on all data
    return pi
```

DAgger converts the quadratic $\mathcal{O}(\epsilon T^2)$ bound into a **linear**
$\mathcal{O}(\epsilon T)$ one — the difference between a policy that drifts and one
that holds. Its cost is an **interactive expert**: a human (or a privileged
controller) must be available to label new states, which is cheap in simulation but
expensive and sometimes unsafe with a real expert in the loop. Variants — DART
(inject noise during demos to cover nearby states), HG-DAgger (human-gated) — reduce
that burden.

---

## 5. Inverse reinforcement learning

IRL recovers *why* the expert acts — the reward $R_\psi$ — then runs RL to obtain a
policy. This generalizes far beyond the demonstrated states because a reward is a
compact, transferable description of intent.

### 5.1 The ill-posedness and the max-entropy fix

IRL is ill-posed: many rewards explain the same behavior (including the trivial
$R\equiv 0$). **Maximum-entropy IRL** (Ziebart) resolves the ambiguity by assuming
the expert is *noisily* optimal — trajectories are exponentially preferred in
return, with the least committed (highest-entropy) distribution consistent with the
data:

$$
p(\tau) \propto \exp\big( R_\psi(\tau) \big), \qquad R_\psi(\tau) = \sum_t R_\psi(s_t, a_t).
$$

Fitting $\psi$ matches the expert's expected features to the model's, and the
gradient is the difference of feature expectations under expert and learner.

### 5.2 Adversarial imitation — GAIL

**Generative Adversarial Imitation Learning (GAIL)** skips recovering an explicit
reward and instead trains a discriminator $D_\omega$ to tell expert
state-action pairs from policy ones, using $-\log(1 - D_\omega(s,a))$ as the reward
for a policy-gradient learner — a GAN over trajectories:

$$
\min_\theta \max_\omega\; \mathbb{E}_{\pi_\theta}\!\big[\log D_\omega(s,a)\big] + \mathbb{E}_{\pi^*}\!\big[\log(1 - D_\omega(s,a))\big].
$$

GAIL and its descendant **AIRL** match expert behavior with dramatically fewer
demonstrations than BC and without the interactive expert DAgger needs — at the cost
of adversarial-training instability.

---

## 6. Generative and diffusion policies

Recent imitation learning treats action prediction as **generative modeling** of the
demonstration distribution, which fixes a second BC weakness: human demonstrations
are **multimodal** (there are several good ways to go around an obstacle), and a
regression policy averages them into a bad compromise down the middle.

**Diffusion policies** (Chi et al.) model the action distribution with a denoising
diffusion model conditioned on the observation: start from noise and iteratively
denoise into an action *sequence*, learning the full multimodal distribution rather
than its mean.

$$
\mathbf{a}^{k-1} = \alpha\big( \mathbf{a}^k - \gamma\,\epsilon_\theta(\mathbf{a}^k, s, k) \big) + \mathcal{N}(0, \sigma^2 I),
$$

denoising from step $K$ to $0$ conditioned on observation $s$. Predicting an
*action chunk* (a short horizon) rather than a single step further suppresses
compounding error and produces smooth, temporally consistent motion. Related lines —
**Action Chunking Transformers (ACT)**, **Implicit BC** (energy-based), and the
large **Vision-Language-Action** models (RT-2, OpenVLA) — are the current frontier
of generalist robot policies, all rooted in the imitation framing.

---

## 7. Practice and pitfalls in the real world

| Pitfall | Cause | Mitigation |
|---|---|---|
| Drift / runaway | distribution shift (§3) | DAgger, action chunking, recovery demos |
| Mode averaging | unimodal regression on multimodal data | diffusion / energy-based / VAE policy |
| Causal confusion | policy keys on a spurious correlate (e.g., its own past action visible in input) | remove leaked features, intervene |
| Demonstrator suboptimality | humans are inconsistent | filter / weight demos, or use IRL with noise model |
| Covariate shift at deploy | real sensors ≠ training | domain randomization, robust features |

Two hard-won disciplines:
1. **Collect recovery data deliberately.** Demonstrate not just the nominal task but
   how to return from the off-nominal states the policy will create. This single
   practice fixes most BC drift in the field.
2. **Guard the learned policy.** As in
   [17-autonomy-reinforcement-learning.md](17-reinforcement-learning.md) and
   [10-autonomy-planning-decision.md](10-planning-decision.md), wrap the
   imitation policy in a verified safety layer. A cloned policy has *no* guarantees
   off-distribution, so the outer guard is not optional.

---

## 8. Practice this week

1. Train a behavioral-cloning policy on an expert in a driving or CartPole sim;
   roll it out and *watch* it drift as it leaves the expert distribution.
2. Implement DAgger with a scripted expert and confirm the drift disappears as the
   aggregated dataset grows.
3. Run GAIL (e.g., via `imitation` library) and compare demonstration efficiency to
   BC on the same task.
4. Train a diffusion policy on a multimodal demonstration set (two valid paths around
   an obstacle) and confirm it captures both modes where regression averages them.

---

## 9. Sources & further study

- **Ross, Gordon & Bagnell — "A Reduction of Imitation Learning and Structured
  Prediction to No-Regret Online Learning" (DAgger)** (AISTATS, 2011). The
  distribution-shift analysis and its fix.
- **Pomerleau — "ALVINN"** (1989) and **Bojarski et al. — "End to End Learning for
  Self-Driving Cars" (PilotNet)** (2016). Foundational BC.
- **Ziebart et al. — "Maximum Entropy Inverse Reinforcement Learning"** (AAAI, 2008).
- **Ho & Ermon — "Generative Adversarial Imitation Learning" (GAIL)** (NeurIPS, 2016);
  **Fu et al. — "AIRL".**
- **Chi et al. — "Diffusion Policy: Visuomotor Policy Learning via Action Diffusion"**
  (RSS, 2023); **Zhao et al. — "ACT".**
- **Argall et al. — "A Survey of Robot Learning from Demonstration"** (Robotics and
  Autonomous Systems, 2009).
- **Osa et al. — "An Algorithmic Perspective on Imitation Learning"** (Foundations &
  Trends, 2018). The comprehensive modern survey.

> Framing note: Imitation learning is seductive because the demo is so easy to give —
> and treacherous because the policy must perform in states the demo never showed. The
> engineers who ship it understand that the real problem is not copying the expert but
> covering the distribution the policy creates for itself, and they never deploy a
> cloned policy without recovery data and a verified guard behind it.
