# Sim-to-Real — Crossing the Reality Gap

> **Why this exists.** Simulation is the only place you can run a million crashes before breakfast, train a policy on dangerous edge cases without risking hardware, and iterate on autonomy at a speed physical testing can never match. But a policy trained in simulation almost always *fails on the real robot* — the dynamics differ, the sensors lie differently, the lighting is wrong, the friction is off. This chasm between "works in sim" and "works in reality" is the **reality gap**, and it is the single largest tax on data-driven robotics. Sim-to-real is the engineering discipline of designing simulations, training procedures, and validation regimes so that the gap is small enough to cross — or so that the policy is robust enough not to care. Get it right and simulation becomes a force multiplier; get it wrong and you've trained an expert at a game no real robot plays.
>
> **What mastering it makes you.** The engineer who can train a controller in sim on Friday and deploy it to hardware on Monday with quantified confidence — turning the simulator from a demo toy into the primary development environment.

Sim-to-real is the bridge between the learning of [01-autonomy-ml-ai.md](01-ml-ai.md) and the physical world, and it is inseparable from the simulation, test, and verification rigor of [06-foundations-simulation-test-verification.md](../foundations/06-simulation-test-verification.md). It is how control policies ([06-autonomy-control-theory.md](06-control-theory.md), [09-autonomy-gnc.md](09-gnc.md)) and planners ([10-autonomy-planning-decision.md](10-planning-decision.md)) are trained safely, how the perception of [11-autonomy-perception-deep.md](11-perception-deep.md) and [20-autonomy-computer-vision.md](20-computer-vision.md) gets synthetic training data, and how the foundation-model policies of [24-autonomy-foundation-models-robotics.md](24-foundation-models-robotics.md) are pretrained. The PX4 SITL workflow of [03-autonomy-px4-sitl.md](03-px4-sitl.md) and the test scaffolding of [05-autonomy-test-scaffold.md](05-test-scaffold.md) are its tooling; the statistics live in [03-foundations-mathematics.md](../foundations/03-mathematics.md).

---

## 1. Anatomy of the Reality Gap

The gap is not one thing — it's a sum of mismatches, each of which can sink a transfer:

| Source of gap | Example | Typical fix |
|---|---|---|
| **Dynamics** | Wrong mass, inertia, friction, motor lag, latency | System ID + domain randomization |
| **Sensors** | Idealized noise-free camera/IMU/LiDAR in sim | Noise models, sensor randomization |
| **Actuation** | Perfect torque vs. real motor saturation, backlash, delay | Actuator modeling, action latency |
| **Appearance** | Clean textures vs. messy real lighting | Photorealistic rendering / visual DR |
| **Contact** | Rigid-body contact is notoriously hard to simulate | Better solvers, randomize contact params |
| **Unmodeled physics** | Aerodynamics, deformation, cable drag | Robustness margins, residual learning |

```
         SIMULATION                          REALITY
   ┌─────────────────────┐   reality   ┌─────────────────────┐
   │ idealized dynamics  │     gap     │ true dynamics       │
   │ clean sensors       │  ◄───────►  │ noisy, biased sensors│
   │ scripted lighting   │             │ messy world         │
   └─────────────────────┘             └─────────────────────┘
   Goal: make the policy invariant to, or aware of, every arrow above.
```

The deepest insight: **the gap you don't model is the gap that kills you.** Contact and latency are the usual silent assassins — a policy that learned to exploit a frictionless simulated gripper or zero-latency control loop has learned a strategy reality forbids.

---

## 2. Domain Randomization — Robustness by Variety

The dominant sim-to-real strategy is **domain randomization (DR)**: instead of trying to make one simulation perfectly match reality (impossible), randomize the simulation's parameters so widely that *reality looks like just another sample* from the training distribution. If a policy works across thousands of randomized worlds, the real world is likely inside that envelope.

Formally, sample parameters $\xi \sim p(\xi)$ (masses, frictions, textures, lighting, latencies) each episode and train to maximize expected return over the distribution:

$$\pi^* = \arg\max_\pi \; \mathbb{E}_{\xi \sim p(\xi)} \Big[ \mathbb{E}_{\tau \sim \pi, \xi}\big[ R(\tau) \big] \Big]$$

This trades peak performance for *robustness*: the policy can't overfit to any single physics instance, so it learns a strategy that works across the spread. Two flavors:

- **Visual DR** (Tobin et al. 2017): randomize textures, colors, lighting, camera pose, distractor objects. A detector trained on absurd randomized scenes transfers to real images because it learned shape, not appearance.
- **Dynamics DR** (OpenAI Dactyl, 2018): randomize physical parameters. The robot hand that solved a Rubik's cube was trained entirely in sim with randomized mass, friction, and even simulated actuator failures.

**Automatic / adaptive DR** is the modern refinement: rather than fixing the randomization ranges by hand, *expand them automatically* as the policy masters the current spread (curriculum), or *tune them* so simulated trajectories match real ones (see SysID, Sec. 4). Too narrow and you don't cover reality; too wide and the task becomes unlearnable — finding the right envelope is the central DR skill.

```python
def randomized_episode(env, rng):
    # Sample a fresh physics instance so the policy can't overfit to one world.
    env.set_param("friction",   rng.uniform(0.5, 1.5))   # ground friction
    env.set_param("mass_scale", rng.uniform(0.8, 1.2))   # payload uncertainty
    env.set_param("motor_lag",  rng.uniform(0.0, 0.03))  # actuation delay (s)
    env.set_param("imu_noise",  rng.uniform(0.0, 0.05))  # sensor noise sigma
    env.randomize_textures()                              # visual invariance
    return env.reset()
```

---

## 3. The Bias–Robustness Trade-off

DR is not free. Widening the randomization distribution is a **conservatism dial**: more variety buys robustness but costs peak performance and sample efficiency, because the policy must hedge against worlds it will never actually face.

$$\underbrace{\text{narrow } p(\xi)}_{\text{high performance, fragile transfer}} \quad\longleftrightarrow\quad \underbrace{\text{wide } p(\xi)}_{\text{robust transfer, conservative, harder to train}}$$

The art is to randomize **only the dimensions you're genuinely uncertain about, with ranges that bracket reality** — and to measure that bracket, not guess it. This is where system identification enters: it shrinks the randomization to the *real* uncertainty rather than a paranoid over-estimate.

---

## 4. System Identification — Shrinking the Gap Directly

The complementary strategy to "be robust to everything" is "*measure* the real system and match the simulator to it." **System identification (SysID)** estimates the true physical parameters $\xi_{real}$ from real-robot data, then sets the simulator to match.

Given recorded real trajectories $\{(\mathbf{x}_t, \mathbf{u}_t)\}$, fit simulator parameters that minimize the discrepancy between simulated and observed dynamics:

$$\xi^* = \arg\min_\xi \sum_t \big\| \mathbf{x}_{t+1}^{real} - f_{sim}(\mathbf{x}_t, \mathbf{u}_t; \xi) \big\|^2$$

Approaches range from classical least-squares on linear models, to gradient-based fitting through **differentiable simulators** (where you backprop through the physics to the parameters), to Bayesian SysID that returns a *posterior* over $\xi$ — which then becomes the principled randomization distribution for DR. The frontier combines them: **SimOpt / real-to-sim-to-real** loops alternate between (a) training in randomized sim and (b) using real rollouts to tighten the distribution toward reality.

**Residual / hybrid models** acknowledge that no parametric simulator is perfect: learn a small correction network $g_\theta$ on top of analytic physics, $\hat{\mathbf{x}}_{t+1} = f_{sim}(\mathbf{x}_t,\mathbf{u}_t) + g_\theta(\mathbf{x}_t,\mathbf{u}_t)$, fitting only the *residual* the model misses. This keeps the data-efficiency and interpretability of physics while capturing the unmodeled remainder.

---

## 5. Photorealism vs. Physics Fidelity

A persistent confusion: sim-to-real has *two different gaps* and they need *different fidelity*.

- **Perception transfer** (camera-based policies, detectors) cares about **visual** fidelity — does the rendered image distribution overlap the real one? Solved by photorealistic rendering (ray tracing, **NVIDIA Isaac Sim**, Unreal-based **CARLA**), neural rendering (NeRF/Gaussian-splat scene replicas), or — counterintuitively — by *abandoning* realism for aggressive visual DR.
- **Control transfer** (dynamics policies) cares about **physical** fidelity — contact, friction, latency, mass. A beautifully rendered scene with sloppy contact physics will produce gorgeous training video and a policy that face-plants on hardware.

| Need | High-fidelity axis | Tool examples |
|---|---|---|
| Perception models | Visual / rendering | Isaac Sim, CARLA, Unreal, NeRF replicas |
| Control / RL policies | Physics / contact / latency | MuJoCo, Isaac Gym/Lab, PyBullet, Drake |
| Both (end-to-end) | Both — hardest | Isaac Lab, photoreal + GPU physics |

The trap is spending your fidelity budget on the wrong axis — a perception engineer over-tuning contact dynamics, or a controls engineer over-tuning textures. Diagnose *which* gap dominates your failure before investing.

---

## 6. Beyond DR — Other Transfer Strategies

DR and SysID are the backbone, but the toolbox is richer:

- **Domain adaptation:** explicitly align sim and real feature distributions (adversarial alignment à la GANs, or self-supervised adaptation on unlabeled real data). Common for perception: train on sim labels, adapt features to real images (e.g., **CyCADA**, sim-to-real GANs).
- **Real-to-sim:** build the simulator *from* reality — scan the real environment (LiDAR/photogrammetry/NeRF) to create a digital twin the policy trains in, collapsing the appearance and geometry gap.
- **Meta-learning / rapid adaptation:** train a policy that *adapts online* to the real dynamics from a few seconds of interaction (**RMA — Rapid Motor Adaptation**, used in legged locomotion: an encoder infers the environment parameters from recent state history and the policy conditions on them).
- **Conservative / robust RL:** optimize worst-case rather than average return ($\max_\pi \min_\xi$), giving guarantees against the adversarial corner of the distribution.
- **Sim-in-the-loop fine-tuning:** transfer a sim-trained policy, then fine-tune cautiously on hardware with safety constraints — bridging the last few percent of gap with real data.

The legged-robotics community (ETH ANYmal, MIT/Unitree) is the proof point: quadrupeds trained *entirely in massively-parallel randomized sim* (Isaac Gym, ~thousands of robots in parallel) now walk over rubble in the real world, using DR + RMA-style adaptation. That pipeline — train millions of episodes in randomized GPU sim, deploy with online adaptation — is the current state of the art.

---

## 7. Evaluation — Trusting the Transfer

> Per the house testing discipline, sim-to-real *is* a testing discipline: the entire point is quantifying confidence that sim performance predicts real performance, as risk prevention before hardware deployment.

The cardinal sin is **evaluating only in the simulator you trained in** — that measures memorization, not transfer. Sound evaluation:

| Level | Target | Method |
|---|---|---|
| **In-distribution sim** | Did it learn the task? | Train-env return |
| **Held-out sim** | Does it generalize across $\xi$? | Test on randomization ranges *not* seen in training |
| **Sim-real correlation** | Does sim score predict real score? | Rank policies in sim, validate ordering on hardware |
| **Hardware (safe)** | Real-world performance | Constrained, instrumented real trials |
| **Robustness / OOD** | Behavior outside the envelope | Push past training ranges; measure graceful degradation |
| **Exploratory** | Find exploited sim artifacts | Adversarial probing for "sim cheats" |

**Boundary cases to force:** parameters at the *edge* of (and just beyond) the randomization range, the worst-case combination of adverse parameters simultaneously (low friction + high latency + heavy payload), and degeneracies the policy might exploit in sim (e.g., learning to abuse a contact solver bug). The key metric is **sim-real correlation**: if a policy that scores higher in sim reliably scores higher on hardware, your simulator is a valid proxy and you can iterate fast; if the ranking inverts, your sim is lying and no amount of sim performance is trustworthy.

```python
def test_held_out_dynamics_transfer():
    # Risk: policy overfits the training randomization and fails just outside it.
    policy = load("trained_in_sim.pt")
    # Evaluate strictly OUTSIDE the training distribution edges.
    ood = make_env(friction=0.45, mass_scale=1.25, latency=0.035)  # beyond ranges
    score = rollout(policy, ood, episodes=100).mean_return
    # Acceptance: graceful degradation, not collapse, just outside the envelope.
    assert score > 0.6 * nominal_return, "policy is brittle at the DR boundary"
```

---

## 8. The Practical Stack

- **Physics / RL sims:** **MuJoCo** (now open-source, gold standard for contact), **NVIDIA Isaac Sim / Isaac Lab** (GPU-parallel, photoreal), **Isaac Gym** (massively parallel RL), **PyBullet**, **Drake** (model-based, contact-rich), **Gazebo** (ROS-native).
- **Driving / perception sims:** **CARLA**, **NVIDIA DRIVE Sim**, Unreal/Unity-based pipelines, NeRF/Gaussian-splat scene replicas.
- **SITL for vehicles:** **PX4 SITL / jMAVSim / Gazebo** ([03-autonomy-px4-sitl.md](03-px4-sitl.md)).
- **Calibration / SysID:** differentiable sims (Brax, Tiny Differentiable Simulator, Warp), Bayesian SysID toolkits.
- **Deployment:** the trained policy is quantized and run onboard via [25-autonomy-edge-inference-deployment.md](25-edge-inference-deployment.md).

---

## Sources & further study

- **Tobin et al. (2017), "Domain Randomization for Transferring Deep Neural Networks from Simulation to the Real World,"** IROS. The DR origin paper.
- **OpenAI et al. (2019/2020), "Solving Rubik's Cube with a Robot Hand"** and "Learning Dexterous In-Hand Manipulation" — automatic DR at scale.
- **Peng et al. (2018), "Sim-to-Real Transfer of Robotic Control with Dynamics Randomization,"** ICRA.
- **Chebotar et al. (2019), "Closing the Sim-to-Real Loop" (SimOpt)** — real rollouts to tune randomization.
- **Kumar et al. (2021), "RMA: Rapid Motor Adaptation for Legged Robots,"** RSS.
- **Lee et al. (2020), "Learning quadrupedal locomotion over challenging terrain,"** *Science Robotics* (ANYmal).
- **Zhao, Queralta & Westerlund (2020), "Sim-to-Real Transfer in Deep Reinforcement Learning for Robotics: a Survey."**
- **Todorov, Erez & Tassa (2012), "MuJoCo: A physics engine for model-based control."**

> Framing note: Sim-to-real reframes the simulator from a place you *demo* in to the place you *develop* in. The reality gap is never fully closed — it is *managed*, by modeling what you can, randomizing what you can't, measuring the residual honestly, and validating transfer rather than memorization. The engineers who win treat the simulator as a hypothesis about reality and every hardware trial as the experiment that tests it — and they trust sim-real correlation, not sim performance, as the number that matters.
