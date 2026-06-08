# Flight Control Theory & Vehicle Dynamics

> The control deep-dive referenced by [01-mastery-curriculum.md](01-mastery-curriculum.md)
> and [28-autonomy-gnc.md](28-autonomy-gnc.md). GNC's "C" gets its own file
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
  racing (see [20-autonomy-ml-ai.md](20-autonomy-ml-ai.md)); still maturing for
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
  fast and deterministic (see [31-systems-embedded-linux-realtime.md](31-systems-embedded-linux-realtime.md)).

---

## 8. How This Maps to Your PX4 Build

- PX4's `mc_rate_control` and `mc_att_control` are your cascaded PID loops.
- `control_allocator` is your mixer — for the VTOL it's the configuration-
  dependent allocator from §4.
- EKF2 (the estimator from [28-autonomy-gnc.md](28-autonomy-gnc.md)) supplies
  the "actual state" the controller differences against.
- The VTOL transition logic is the gain-scheduling/allocation switch from §3–4.
- **Where to learn by doing:** tune the rate loop in SITL
  ([22-autonomy-px4-sitl.md](22-autonomy-px4-sitl.md)), watch the step response
  in flight-review logs, then feel the same tune on hardware. Sim → log → metal
  is the loop that builds real control intuition.

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
