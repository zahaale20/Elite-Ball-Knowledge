# Flight Control Theory & Vehicle Dynamics

> The control deep-dive referenced by [01-mastery-curriculum.md](../01-mastery-curriculum.md)
> and [28-autonomy-gnc.md](28-gnc.md). GNC's "C" gets its own file
> because control is where math meets the physical machine — and where most
> autonomy bugs that *crash hardware* actually live.

Estimation tells you **where you are**. Planning tells you **where to go**.
Control is the loop that makes the vehicle actually **get there**, against
gravity, wind, and its own imperfect actuators, dozens to thousands of times per
second.

---

## 1. The Shape of the Problem

A controller's job: drive the **error** (desired state − actual state) to zero
and keep it there, while staying stable, fast enough, and not saturating the
actuators. Every autopilot, from a $5 hobby board to a cruise missile, is some
version of this loop:

```
setpoint → [ controller ] → actuator → [ plant/vehicle ] → sensor → state
              ↑__________________ error ____________________|
```

The art is choosing the controller so the closed loop is **stable**, **accurate**
(low steady-state error), **fast** (good rise/settling time), and **robust**
(tolerant of model error and disturbance).

---

## 2. PID — The Workhorse You Must Truly Understand

90% of deployed flight control is PID. PX4's rate and attitude loops are PID at
their core. Master it before anything fancier.

$$u(t) = K_p \, e(t) + K_i \int_0^t e(\tau)\,d\tau + K_d \frac{de(t)}{dt}$$

- **P (proportional)** — push proportional to current error. Too low: sluggish.
  Too high: oscillation.
- **I (integral)** — accumulates past error; kills steady-state offset (e.g.,
  holding altitude against a constant downward bias). The danger: **integral
  windup** when actuators saturate — must be clamped/anti-windup.
- **D (derivative)** — responds to *rate of change* of error; adds damping,
  predicts overshoot. Amplifies sensor noise, so it's usually filtered.

**Tuning intuition (the order that works):** raise P until it oscillates, back
off; add D to damp the oscillation; add just enough I to remove residual offset.
Cascade matters: PX4 tunes the **inner rate loop first**, then the outer
attitude loop.

**Cascaded control** is the key architecture: a fast inner loop (angular rate)
nested inside a slower outer loop (attitude), inside an even slower one
(velocity), inside position. Each loop only needs to be ~3–5× faster than the
one outside it.

---

## 3. Vehicle Dynamics — What the Controller Is Fighting

You can't tune what you don't understand. The plant is the vehicle's physics.

- **6 degrees of freedom (6-DOF):** 3 translational (x, y, z) + 3 rotational
  (roll φ, pitch θ, yaw ψ). State is position, velocity, attitude, angular rate.
- **Multirotor:** thrust is always along the body z-axis. To move horizontally
  you must *tilt first* — position and attitude are coupled. This is why
  multirotors are **underactuated** (4 inputs, 6 DOF).
- **Fixed-wing:** lift from airflow over wings; control via ailerons (roll),
  elevator (pitch), rudder (yaw), throttle (speed). Must keep airspeed above
  stall. Stable in cruise, but can't hover.
- **VTOL (your airframe):** the hard case — it must be *both*, and the
  **transition** between hover and forward flight is the riskiest control regime.
  Tiltrotor allocation changes as motors rotate; control authority migrates from
  props to aerodynamic surfaces mid-maneuver.
- **Coordinate frames:** body frame (fixed to vehicle), NED/ENU world frame,
  and the rotations between them (Euler angles vs. quaternions). **Use
  quaternions** in code — Euler angles hit gimbal lock at ±90° pitch.

---

## 4. Control Allocation (Mixing)

The controller outputs *desired torques and thrust*; the **mixer/allocator**
turns those into individual motor/servo commands.

- For a quad: 4 desired generalized forces (thrust, roll, pitch, yaw torque) → 4
  motor speeds, via the (invertible) mixing matrix.
- For a tiltrotor VTOL: the allocation is **over-actuated and configuration-
  dependent** — it changes with tilt angle and flight phase. PX4 calls this the
  control allocation module.
- Saturation handling lives here: when commands exceed motor limits, *which axis
  gets sacrificed*? (Usually yaw — you'd rather lose heading authority than
  altitude.)

---

## 5. State-Space & Modern Control

PID is single-input/single-output thinking. For coupled, multi-variable systems
you move to **state-space**:

$$\dot{x} = Ax + Bu, \qquad y = Cx + Du$$

- **Controllability / observability** — can you actually steer every state? Can
  you reconstruct every state from sensors? (Kalman observability ties directly
  into your EKF.)
- **LQR (Linear-Quadratic Regulator)** — computes an *optimal* full-state
  feedback gain by minimizing a cost trading state error against control effort.
  The principled upgrade from hand-tuned PID for coupled systems.
- **LQG** = LQR + Kalman filter (optimal estimator feeding optimal controller).
- **Pole placement** — directly assign closed-loop dynamics (speed, damping).

---

## 6. When Linear Isn't Enough

Real vehicles are nonlinear (aerodynamics, large attitudes, actuator limits).
The frontier of flight control:

- **Gain scheduling** — interpolate between linear controllers tuned at
  different operating points (airspeed, tilt angle). How most VTOLs ship today.
- **Model Predictive Control (MPC)** — at each step, solve a finite-horizon
  optimization that respects constraints (actuator limits, no-fly geometry).
  Powerful for aggressive maneuvers and explicit constraint handling; expensive.
- **Nonlinear Dynamic Inversion (NDI / INDI)** — cancel the known nonlinear
  dynamics so a simple linear controller sees a clean plant. Increasingly common
  in modern autopilots.
- **Adaptive & L1 control** — adjust gains online as the vehicle's parameters
  (mass, CG, damaged surfaces) change. Relevant for resilient/damaged-airframe
  flight.
- **Geometric control on SO(3)** — control attitude directly on the rotation
  manifold, avoiding singularities entirely. The rigorous basis for aggressive
  quadrotor flight (Lee, Leok, McClamroch).
- **Learned control (RL)** — neural policies that beat human pilots in drone
  racing (see [20-autonomy-ml-ai.md](20-ml-ai.md)); still maturing for
  safety-critical deployment.

---

## 7. Stability — The Property You Never Compromise

- **BIBO stability** — bounded input gives bounded output.
- **Lyapunov stability** — the rigorous, nonlinear notion: find an "energy"
  function that always decreases, and you've *proven* the system converges. The
  gold standard for nonlinear control proofs.
- **Phase & gain margins** — how much delay/gain error the loop tolerates before
  it oscillates. Real systems need margin for sensor lag, actuator dynamics, and
  model error. A controller that's perfect in sim and marginless will crash in
  wind.
- **Time delay is the silent killer** — every sensor filter, comms hop, and
  compute cycle adds lag that erodes margin. This is *why* the rate loop must run
  fast and deterministic (see [04-foundations-modern-cpp-realtime.md](../foundations/04-modern-cpp-realtime.md)).

---

## 8. How This Maps to Your PX4 Build

- PX4's `mc_rate_control` and `mc_att_control` are your cascaded PID loops.
- `control_allocator` is your mixer — for the VTOL it's the configuration-
  dependent allocator from §4.
- EKF2 (the estimator from [28-autonomy-gnc.md](28-gnc.md)) supplies
  the "actual state" the controller differences against.
- The VTOL transition logic is the gain-scheduling/allocation switch from §3–4.
- **Where to learn by doing:** tune the rate loop in SITL
  ([22-autonomy-px4-sitl.md](22-px4-sitl.md)), watch the step response
  in flight-review logs, then feel the same tune on hardware. Sim → log → metal
  is the loop that builds real control intuition.

---

## 9. Feedback From First Principles — Why Closed Loop At All

Before transfer functions and gains, internalize *why* feedback exists. You could
try **open-loop** control: model the plant perfectly, compute the exact input,
apply it, hope. It fails the instant reality diverges from the model — wind gusts,
a heavier payload, a sagging battery, a chipped prop. Open loop has **no
self-correction**.

Feedback measures the actual output and *acts on the discrepancy*. That single
idea buys you three things no feedforward term can:

1. **Disturbance rejection** — the loop fights gusts it never modeled.
2. **Insensitivity to plant error** — you don't need a perfect model, just a
   good-enough one inside a loop with margin.
3. **Reference tracking** — drive a measured quantity to a commanded value and
   *hold it* despite the world pushing back.

Formally, the loop is described by two functions of frequency. Let `L = C·P` be
the open-loop (controller × plant). Then:

- **Sensitivity** `S = 1 / (1 + L)` — how much a disturbance leaks to the output.
- **Complementary sensitivity** `T = L / (1 + L)` — how the output follows the
  reference (and how much sensor noise leaks through).

The iron law: **S + T = 1, at every frequency.** You cannot make both small. This
is the **waterbed effect** — push sensitivity down in one band (good disturbance
rejection at low frequency) and it pops up somewhere else (noise amplification or
peaking near crossover). Bode's integral theorem makes it precise: the log of
sensitivity, integrated over frequency, is conserved. **You are always trading,
never winning for free.** Every tuning argument in this file is ultimately a
negotiation over where on the waterbed you push.

> Mental model for your VTOL: low-frequency loop gain holds altitude against a
> steady downdraft (small S down low); high-frequency content is dominated by IMU
> noise and you *want* the loop to ignore it (small T up high). The crossover
> between them is where you live or die.

---

## 10. Transfer Functions, Poles & Zeros

To reason about a loop you need its **transfer function** — the input→output
relationship in the Laplace domain (see the linear-algebra and calculus footing
in [03-foundations-mathematics.md](../foundations/03-mathematics.md)):

`G(s) = output(s) / input(s) = N(s) / D(s)`

- **Poles** = roots of the denominator `D(s)` = the system's **natural modes**.
  Their location *is* the dynamics:
  - Left-half-plane (negative real part) → stable, decays.
  - Right-half-plane (positive real part) → **unstable, grows** → crash.
  - On the imaginary axis → marginal, rings forever.
- **Zeros** = roots of the numerator `N(s)` — they shape transient response and
  can block or boost certain frequencies.

A canonical second-order pole pair captures most of what a flight loop feels like:

`G(s) = ωn² / (s² + 2ζ·ωn·s + ωn²)`

- `ωn` — **natural frequency**: how fast it wants to move.
- `ζ` — **damping ratio**: how much it overshoots and rings.

| ζ | Behavior | Feel |
|---|---|---|
| 0 | Undamped | Rings forever — never ship this |
| 0.3 | Lightly damped | Bouncy, ~37% overshoot |
| 0.7 | Well damped | ~5% overshoot, fast settle — the usual target |
| 1.0 | Critically damped | No overshoot, slowest non-ringing |
| >1 | Overdamped | Sluggish, no overshoot |

Useful closed-form intuition for a 2nd-order step:
- Percent overshoot ≈ `exp(−π·ζ / sqrt(1−ζ²))`.
- Settling time (2%) ≈ `4 / (ζ·ωn)`.
- Rise time ≈ `1.8 / ωn`.

**Right-half-plane (non-minimum-phase) zeros** deserve a warning: they make the
output initially move the *wrong way* before correcting, and they hard-cap your
achievable bandwidth. A multirotor's altitude-via-tilt coupling and certain
aero-elastic effects introduce them. When a loop "dips before it climbs" in your
logs, suspect a RHP zero — and stop cranking gain, because no gain fixes it.

---

## 11. Frequency Response, Bode & Stability Margins (Worked)

You can't always solve for poles by hand, but you can *always* look at the loop's
**frequency response** — its gain and phase versus frequency — on a **Bode plot**.
This is the single most practical control-analysis tool.

Key frequency: the **gain crossover** `ωc`, where loop gain `|L| = 1` (0 dB). Near
there, two margins decide whether you fly or oscillate:

- **Phase margin (PM)** — how much *extra phase lag* the loop can absorb at `ωc`
  before total phase hits −180° (the oscillation condition). Measured in degrees.
- **Gain margin (GM)** — how much *extra gain* you could add before the loop goes
  unstable at the phase-crossover frequency. Measured in dB.

Practical targets for flight loops: **PM ≈ 30–60°, GM ≥ 6 dB.** Less than that
and the vehicle is technically stable but feels twitchy and dies in wind.

**Why delay is the silent killer (worked):** a pure time delay `τ` adds phase lag
`φ = −ωc·τ` radians — *linear in frequency*. Suppose your rate loop crosses over
at `ωc = 50 rad/s` and you have 4 ms of accumulated lag (sensor filter + scheduler
jitter + actuator rise):

```
phase lost = ωc · τ = 50 · 0.004 = 0.20 rad ≈ 11.5°
```

That 11.5° comes straight out of your phase margin. Stack a heavier IMU low-pass,
a slower loop, and a laggy ESC and you can burn 30–40° without touching a single
gain — turning a crisp tune into a divergent one. **This is the entire argument
for a fast, deterministic rate loop** (see the real-time discussion in
[04-foundations-modern-cpp-realtime.md](../foundations/04-modern-cpp-realtime.md)).
Margin is the budget you spend on latency.

---

## 12. PID Tuning Theory in Depth

§2 gave you the intuition; here is the machinery you actually need when a tune
won't settle.

**The discrete PID PX4 actually runs** (per loop tick, `dt` = sample period):

```
e        = setpoint - measurement
P_term   = Kp * e
I_term  += Ki * e * dt          # accumulate
D_meas   = (measurement - prev_measurement) / dt   # derivative ON MEASUREMENT
D_term   = -Kd * lowpass(D_meas, N)                # filtered, sign accounts for d/dt
u_raw    = P_term + I_term + D_term + feedforward
u        = clamp(u_raw, u_min, u_max)
```

Four refinements separate a textbook PID from a flyable one:

1. **Derivative on measurement, not error.** Differentiating the error spikes the
   output every time you step the setpoint ("derivative kick"). Differentiate the
   *measurement* instead — same damping, no kick on command changes.
2. **Derivative low-pass filter (`N`).** Raw `de/dt` amplifies IMU noise into the
   motors. A first-order filter (PX4's `*_RATE_D` is paired with gyro/D-term
   filtering, `IMU_GYRO_CUTOFF`, `MC_ROLLRATE_D` etc.) tames it. Too aggressive a
   filter, though, *adds delay* and eats phase margin (see §11) — a real tradeoff.
3. **Anti-windup.** When the motors saturate, the integrator keeps accumulating
   error it can't act on; when you finally come out of saturation it dumps a huge
   correction and overshoots wildly. Two fixes: **clamp** the integrator, or
   **back-calculation** — feed the difference `(u − u_raw)` back into the
   integrator with a tracking time `Tt` so it "unwinds" as fast as it saturated.
4. **Feedforward.** Feedback only reacts *after* error appears. Add a feedforward
   term proportional to the commanded rate/acceleration so the controller acts
   *before* the error exists. PX4 exposes this (`*_RATE_FF`, `MPC_*_FF`); it's how
   you get crisp tracking without cranking P into oscillation.

**Tuning methods beyond "raise P till it rings":**

- **Ziegler–Nichols (ultimate gain).** Raise pure-P gain until sustained
  oscillation; record the ultimate gain `Ku` and period `Tu`. Then for a classic
  PID: `Kp = 0.6·Ku`, `Ki = 1.2·Ku/Tu`, `Kd = 0.075·Ku·Tu`. It's aggressive
  (designed for ~25% overshoot) — a *starting point*, not a final tune, and risky
  to do on real hardware. Prefer the **PX4 auto-tuner** (relay-based system ID)
  in SITL first.
- **Relay autotune.** Drive the loop with a relay (bang-bang) to provoke a limit
  cycle, measure amplitude/period, infer `Ku`/`Tu` without manually hunting for
  instability. This is essentially what PX4's autotune does.

PX4 rate-loop parameter map (commit this to memory for log work):

| Param | Role |
|---|---|
| `MC_ROLLRATE_P` / `_I` / `_D` | Inner roll-rate PID |
| `MC_PITCHRATE_*`, `MC_YAWRATE_*` | Pitch/yaw rate PIDs |
| `MC_ROLL_P`, `MC_PITCH_P`, `MC_YAW_P` | Outer attitude P (rate setpoint = P·angle error) |
| `MPC_XY_VEL_*`, `MPC_Z_VEL_*` | Velocity-loop PIDs |
| `*_RATE_FF`, `MPC_*_FF` | Feedforward |
| `IMU_GYRO_CUTOFF`, `IMU_DGYRO_CUTOFF` | D-term / gyro filtering (latency vs noise) |

---

## 13. State-Space Deep Dive

PID is one-input-one-output. For coupled, multi-state systems (and to *prove*
properties rather than tune by feel), use the state-space model from §5:
`ẋ = Ax + Bu`, `y = Cx + Du`. Two structural questions come first.

**Controllability — can you steer every state?** Build the controllability matrix:

```
𝒞 = [ B  AB  A²B  …  Aⁿ⁻¹B ]
```

If `𝒞` has full rank (= number of states), every state is reachable with some
input. If not, some mode is uncontrollable — no controller, however clever, can
move it. (Practical example: a perfectly symmetric quad has a yaw mode that's only
weakly controllable, which is why yaw is the axis you sacrifice under saturation —
see §4 and §15.)

**Observability — can you reconstruct every state from sensors?** Dual matrix:

```
𝒪 = [ C ; CA ; CA² ; … ; CAⁿ⁻¹ ]
```

Full rank → every state is inferable from the outputs. This is *exactly* the
condition your EKF needs to estimate states you don't measure directly
(velocity/bias from position+IMU). Observability ties control to estimation; the
GNC loop in [28-autonomy-gnc.md](28-gnc.md) lives or dies on it.

**LQR — optimal full-state feedback.** Instead of hand-placing poles, minimize a
quadratic cost that trades state error against control effort:

```
J = ∫ ( xᵀQx  +  uᵀRu ) dt
```

- `Q` (state weight) — how much you punish being off-target. Bigger Q → tighter,
  more aggressive.
- `R` (input weight) — how much you punish actuator effort. Bigger R → gentler,
  saves motors/battery.

The optimal law is constant full-state feedback `u = −Kx`, where
`K = R⁻¹ Bᵀ P` and `P` solves the **algebraic Riccati equation**
`AᵀP + PA − PBR⁻¹BᵀP + Q = 0`. You don't solve that by hand — `lqr()` in
MATLAB/Python control does — but you *do* hand-pick `Q` and `R`, which is just
"how aggressive vs. how gentle," one number per state/input. Far fewer knobs than
a coupled mess of PIDs.

**Worked sketch — double integrator** (`p̈ = u`, the essence of a position axis):
states `x = [position, velocity]`, `A = [[0,1],[0,0]]`, `B = [[0],[1]]`. Pick
`Q = diag(q_pos, q_vel)`, `R = r`. Solving the Riccati gives a feedback
`u = −k_p·position − k_d·velocity` — i.e., **LQR rediscovers PD control**, but
with the gains *derived* from your cost weights instead of guessed. That's the
whole appeal: principled gains for systems too coupled to eyeball.

**LQG = LQR + Kalman filter.** The **separation principle** says you may design the
optimal estimator (Kalman, your EKF2) and the optimal controller (LQR)
*independently* and bolt them together — the combination is still optimal. This is
the theoretical license behind "EKF estimates state, controller acts on it."

**Integral action in state-space:** augment the state with the integral of
tracking error to kill steady-state offset, the LQR analog of PID's `I` term.

---

## 14. Discrete-Time, Sampling & Latency

Your controller is not continuous — it runs on a Pi 5 / Pixhawk at a fixed rate.
That changes everything about stability margins.

- **Sampling rate `fs`.** PX4's rate loop targets ~1 kHz; attitude ~250 Hz;
  position ~50 Hz. **Nyquist:** you can only control dynamics below `fs/2`; the
  practical rule is to sample **10–20× faster** than your loop bandwidth, because
  the sampler itself injects up to half a sample period of delay.
- **Discretization.** A continuous design becomes a difference equation via
  zero-order hold (ZOH) or **Tustin/bilinear** (`s → (2/Ts)·(z−1)/(z+1)`). Tustin
  preserves stability and is the usual choice for filters/controllers.
- **Delay = phase you can't get back.** A pure delay of `τ` seconds is `e^{−sτ}`,
  contributing `−ωτ` of phase (§11). The **delay margin** is simply
  `τ_max = PM / ωc` — phase margin *is* a latency budget. A 40° PM at `ωc = 50
  rad/s` tolerates `0.70/50 ≈ 14 ms` of total loop delay. Blow past it and you
  oscillate.
- **Sources of that delay budget:** sensor sample-and-hold (½ period),
  anti-alias + IMU low-pass filters (group delay), scheduler **jitter** (the case
  for an RT kernel), ESC/motor rise time, and any comms hop. Every one is real and
  additive.
- **Aliasing.** Vibration above `fs/2` folds down into your control band and looks
  like real motion. You *must* anti-alias (analog + the gyro low-pass) before it
  poisons the rate loop — a classic cause of "phantom" oscillation that no gain
  change fixes.

> The discrete view is why "just lower the loop rate to save CPU" is dangerous:
> you simultaneously shrink usable bandwidth *and* add delay — a double hit to
> margin. Treat loop rate and filter cutoffs as safety parameters
> ([09-foundations-safety-assurance.md](../foundations/09-safety-assurance.md)).

---

## 15. Control Allocation for the Tilt-Tricopter (Deep)

§4 introduced the mixer; here's the real structure for your airframe — a **tilt-
tricopter VTOL** (three lift motors + tilting front nacelles). The controller
produces a desired generalized-force vector `τ = [thrust, roll, pitch, yaw]ᵀ`; the
allocator finds actuator commands `u` (motor thrusts + tilt-servo angles) such
that `B·u = τ`, where `B` is the **control-effectiveness matrix** encoding each
actuator's contribution to each axis.

- **Square & invertible (classic quad):** `u = B⁻¹·τ`. One unique solution.
- **Over-actuated (your tilt-tricopter):** more effective DOF than required axes,
  so `B` is wide and there are *infinitely many* solutions. Pick the
  minimum-effort one with the **Moore–Penrose pseudoinverse**:

  ```
  u = B⁺ · τ = Bᵀ (B Bᵀ)⁻¹ · τ
  ```

  A **weighted** pseudoinverse `u = W⁻¹Bᵀ(BW⁻¹Bᵀ)⁻¹τ` lets you bias the solution
  — e.g., prefer differential thrust over fast tilt-servo motion to spare the
  servos and reduce gyroscopic coupling.

- **Configuration-dependent `B(α)`.** The effectiveness matrix is a function of
  the tilt angle `α`. In hover (`α≈90°`) the props provide all control; in
  forward flight (`α≈0°`) thrust points forward and the **aero surfaces take over
  pitch/yaw authority.** During **transition**, `B(α)` morphs continuously — this
  is the riskiest regime in the flight (§3) and where allocation bugs crash
  hardware.

- **Saturation & prioritization.** When the desired `τ` exceeds what the actuators
  can deliver, *something must give*. PX4's allocator supports prioritized /
  null-space redistribution: hold the high-priority axes (thrust to not fall,
  roll/pitch to stay upright) and **bleed yaw first** — you'd rather spin slightly
  off-heading than drop out of the sky. This is the controllability hierarchy from
  §13 made operational.

PX4 module: `control_allocator` with the VTOL configuration; the geometry lives in
the airframe's actuator/effectiveness config. Get this matrix wrong and the loops
upstream are tuning a lie.

---

## 16. Cascaded Loops in PX4 — Rate → Attitude → Position (Deep)

The whole stack is **nested loops**, each ~3–5× slower than the one it wraps so
they don't fight each other (bandwidth separation, §11):

```
position SP → [ POSITION P ] → velocity SP → [ VELOCITY PID ] → thrust + tilt SP
   (~50 Hz)                                        |
attitude SP → [ ATTITUDE (geometric) ] → rate SP   ↓
  (~250 Hz)                                  [ CONTROL ALLOCATION ]  (§15)
   rate SP → [ RATE PID ] → torque demand → motors/servos
  (~1 kHz)        ↑__ gyro (vehicle_angular_velocity)
```

- **Rate loop (innermost, fastest).** Pure PID on body angular rate vs. gyro.
  Highest authority over stability and the one most sensitive to delay/filtering
  (§11, §14). Tune it **first**, in isolation.
- **Attitude loop.** PX4 uses a **geometric / quaternion** attitude controller
  (`mc_att_control`): it computes the shortest-arc rotation from current to desired
  attitude and outputs a proportional rate setpoint (`MC_ROLL_P` etc.). Quaternions
  avoid gimbal lock (§3) — essential for the large attitudes a tiltrotor sees.
- **Velocity & position loops (outermost, slowest).** `mc_pos_control` turns
  position error → velocity setpoint (P) → thrust vector / acceleration setpoint
  (PID + feedforward), which becomes attitude + collective thrust commands.
- **The actual state** that every loop differences against comes from **EKF2**
  ([28-autonomy-gnc.md](28-gnc.md)) — and in GPS-denied flight from the
  vision pipeline in
  [26-autonomy-gnss-jamming-spoofing.md](26-gnss-jamming-spoofing.md). A
  laggy or noisy estimate corrupts *every* loop above it; control quality is capped
  by estimation quality.

**Why inner-first tuning is non-negotiable:** the outer loops *assume* the inner
loop already tracks its rate/attitude setpoints cleanly. Tune position before the
rate loop is solid and you're stacking a slow controller on a shaky foundation —
the oscillation you see at the top actually lives at the bottom.

---

## 17. MPC Preview & When to Reach For It

**Model Predictive Control** is PID's heavyweight cousin: at every step, use a
model to *predict* the vehicle's response over a finite horizon and solve an
optimization for the input sequence that minimizes a cost **subject to explicit
constraints**, then apply only the first input and repeat (receding horizon).

```
minimize   Σ over horizon ( ‖x_k − x_ref‖²_Q + ‖u_k‖²_R )
subject to  x_{k+1} = f(x_k, u_k)        # prediction model
            u_min ≤ u_k ≤ u_max          # actuator limits — HARD
            vehicle stays outside no-fly geometry, etc.
```

What MPC buys you that cascaded PID can't:

- **Constraints are first-class.** Actuator saturation, tilt-rate limits, and
  geometric keep-out volumes are *honored*, not patched after the fact.
- **Preview.** If the trajectory ahead is known
  ([29-autonomy-planning-decision.md](29-planning-decision.md)), MPC acts
  on what's *coming*, not just present error — superb for aggressive maneuvers and
  transition scheduling.

Costs and cautions:

- **Compute.** Solving a QP at every step is heavy. On a Pi 5 it's feasible for
  position/trajectory rates (tens of Hz) but **not** for the 1 kHz rate loop — keep
  PID inside, MPC outside.
- **Model dependence.** MPC is only as good as `f(·)`; a bad model gives confident
  wrong moves. **Tube MPC** and robust variants add a margin "tube" around the
  nominal trajectory to tolerate model error and disturbance.
- **Explicit MPC** precomputes the solution as a lookup table for systems small
  enough to afford it, dodging the online solve.

Reach for MPC when constraints and preview genuinely matter (tight obstacle fields,
transition, payload delivery); otherwise the cascaded PID stack in §16 is simpler,
faster, and easier to certify ([09-foundations-safety-assurance.md](../foundations/09-safety-assurance.md)).

---

## 18. Reading a `.ulog` — Tuning by Diagnosis (Worked)

Control intuition is built by closing the **sim → log → metal** loop (§8). The log
is where theory meets evidence. Pull the `.ulog` into PX4 Flight Review (or
`pyulog`/`pyFlightAnalysis`) and read the **rate-tracking** plot first: desired
(`vehicle_rates_setpoint`) overlaid on actual (`vehicle_angular_velocity`). The gap
between them tells you almost everything.

| Log symptom | Likely cause | Fix (theory) |
|---|---|---|
| Actual lags setpoint, sluggish | Too little P / bandwidth too low | Raise `*_RATE_P`; add feedforward (§12) |
| Sustained oscillation, fixed frequency | P too high → near zero phase margin (§11) | Lower P; check loop delay/filters |
| High-freq buzz on D-term & motors | D amplifying gyro noise (§12) | Lower `*_RATE_D` or tighten `IMU_DGYRO_CUTOFF` (watch added delay, §14) |
| Overshoots then settles | Too little damping (low ζ, §10) | Add D |
| Slow constant offset never closes | Too little I, or integrator clamped/windup (§12) | Raise `*_RATE_I`; check anti-windup |
| Big overshoot *after* a saturated maneuver | Integral windup (§12) | Enable/clamp anti-windup; back-calculation |
| Oscillation only at high throttle/airspeed | Operating point moved; fixed gains wrong (§6) | Gain-schedule; check `B(α)` allocation (§15) |
| Output dips wrong way before correcting | RHP (non-minimum-phase) zero (§10) | Don't add gain; reduce bandwidth demand |
| Random jitter, no clean frequency | Aliased vibration or scheduler jitter (§14) | Fix mounting/anti-alias; RT scheduling |

**Worked example.** You see clean low-frequency tracking but a persistent ~30 Hz
oscillation that grows with throttle, and the D-term plot is fuzzy. Walk the chain:
fuzzy D-term ⇒ noise amplification (§12); grows with throttle ⇒ more motor
vibration coupling in; ~30 Hz is well inside your rate-loop band. Diagnosis: gyro
noise driving the derivative path, eroding phase margin until the loop limit-cycles.
Fix order: tighten `IMU_DGYRO_CUTOFF` *a little* (cheap, but spend phase-margin
budget carefully, §11/§14), reduce `MC_ROLLRATE_D`, re-fly, re-check the rate-track
plot. Confirm in SITL first ([22-autonomy-px4-sitl.md](22-px4-sitl.md)),
then on hardware. That diagnostic discipline — symptom → mechanism → minimal fix →
re-measure — is the difference between a tuner and a guesser, and it's the same
muscle the [02-ten-year-mastery-plan.md](../foundations/02-ten-year-mastery-plan.md) is built to
grow.

---

## Sources & Citations

**Textbooks**
- Åström, K. & Murray, R. — *Feedback Systems: An Introduction for Scientists and
  Engineers* (free, the best modern intro): https://fbswiki.org
- Ogata, K. — *Modern Control Engineering*, Pearson (classical PID/state-space).
- Stevens, Lewis & Johnson — *Aircraft Control and Simulation*, Wiley.
- Beard, R. & McLain, T. — *Small Unmanned Aircraft: Theory and Practice*,
  Princeton Univ. Press (the UAV-specific bible).
- Brian Douglas — *Control System Lectures* (free video intuition): https://engineeringmedia.com

**Papers**
- Lee, Leok & McClamroch — *Geometric Tracking Control of a Quadrotor UAV on
  SE(3)* (IEEE CDC 2010).
- Mellinger & Kumar — *Minimum Snap Trajectory Generation and Control for
  Quadrotors* (ICRA 2011).
- Kaufmann et al. — *Champion-level drone racing using deep reinforcement
  learning (Swift)*, Nature 2023.

**Official docs**
- PX4 controller architecture & tuning: https://docs.px4.io/main/en/flight_stack/controller_diagrams.html
- PX4 control allocation: https://docs.px4.io/main/en/concept/control_allocation.html
- PX4 VTOL configuration: https://docs.px4.io/main/en/config_vtol/

*Equations are standard textbook results. The mapping to PX4 modules reflects the
PX4 `main` architecture; verify module names against your checked-out version.*
