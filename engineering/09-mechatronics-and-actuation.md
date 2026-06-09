# Mechatronics & Actuation — Motors, Servos, Gears & Closing the Loop

> **Why this exists.** Every robot, drone, missile fin, landing-gear retract, and
> camera gimbal turns electrical intent into mechanical motion through an actuator.
> Mechatronics is the discipline at the seam between the electrical, the mechanical,
> and the software — the place where a beautiful control law meets backlash, where a
> "fast enough" loop rate collides with motor inductance, and where the difference
> between a twitchy gimbal and a buttery one is a correctly identified plant. If you
> cannot size a motor, choose a gear ratio, read an encoder, and close a current loop,
> you cannot build a machine that moves in the real world.
>
> **What mastering it makes you.** The engineer who can look at a torque-speed
> requirement and pick the motor, gearbox, driver, and sensor as one coupled system;
> who knows why a servo hunts, why a harmonic drive ticks, and why a BLDC needs
> commutation; and who treats the actuator as a controllable plant with a transfer
> function rather than a black box that "should just work."

Actuation is where the control theory of [06-autonomy-control-theory.md](../autonomy/06-control-theory.md)
becomes torque on a shaft, and where the mechanical reasoning of
[04-career-mechanical-engineering.md](../career/04-mechanical-engineering.md) sets the
inertia and friction the controller must fight. The first-principles habit of
[01_first_principles_systems_engineering.md](../foundations/01-first_principles_systems_engineering.md)
keeps you sizing from physics, not catalogs. Sensors feeding the loop come from
[10-engineering-sensors-and-instrumentation.md](10-sensors-and-instrumentation.md);
the driver electronics from [14-engineering-pcb-and-electronics-design.md](14-pcb-and-electronics-design.md);
the energy budget from [15-engineering-batteries-and-energy-storage.md](15-batteries-and-energy-storage.md).
Reliability of the drivetrain is governed by [13-engineering-reliability-and-failure-analysis.md](13-reliability-and-failure-analysis.md),
manufacturability of the housing by [11-engineering-manufacturing-and-dfm.md](11-manufacturing-and-dfm.md),
and the whole actuator is a subsystem in the architecture of
[12-engineering-systems-engineering-mbse.md](12-systems-engineering-mbse.md).
Every motion claim is validated in simulation per
[06-foundations-simulation-test-verification.md](../foundations/06-simulation-test-verification.md).

---

## Table of Contents

1. [The actuator zoo — picking the motion primitive](#1-the-actuator-zoo--picking-the-motion-primitive)
2. [The DC motor as a plant — first principles](#2-the-dc-motor-as-a-plant--first-principles)
3. [Motor sizing — torque, speed, thermal, duty](#3-motor-sizing--torque-speed-thermal-duty)
4. [BLDC and PMSM commutation](#4-bldc-and-pmsm-commutation)
5. [Gearing — ratio, reflected inertia, backlash](#5-gearing--ratio-reflected-inertia-backlash)
6. [Position sensing — encoders & resolvers](#6-position-sensing--encoders--resolvers)
7. [Closing the loop — cascaded current/velocity/position](#7-closing-the-loop--cascaded-currentvelocityposition)
8. [Compliance, backlash & resonance](#8-compliance-backlash--resonance)
9. [Practice this week](#9-practice-this-week)
10. [Sources & further study](#10-sources--further-study)

---

## 1. The actuator zoo — picking the motion primitive

Actuation begins with a requirement: a force or torque, over a range, at a speed, at
a precision, within a mass and power budget. The actuator family follows from those.

| Actuator | Motion | Strengths | Weaknesses | Typical use |
|---|---|---|---|---|
| Brushed DC | rotary | cheap, simple drive | brush wear, EMI | toys, small pumps |
| BLDC / PMSM | rotary | high power density, long life | needs commutation | drones, EVs, gimbals |
| Stepper | rotary (open-loop) | precise steps, no encoder | loses steps under load, low speed torque | 3D printers, CNC |
| Servo (RC) | rotary, bounded | integrated loop, cheap | low precision, plastic gears | UAV control surfaces |
| Hobby/industrial servo | rotary | closed-loop, high BW | cost, tuning | robot joints |
| Hydraulic | linear/rotary | enormous force density | leaks, weight, plumbing | landing gear, presses |
| Pneumatic | linear | fast, clean, compliant | hard to position precisely | grippers, valves |
| Voice coil | linear, short stroke | very high BW, frictionless | small stroke, force | autofocus, fast-steering mirrors |
| Piezo | nano stroke | sub-nm precision | tiny range, high voltage | optics, AFM |
| Shape-memory / EAP | linear | silent, soft | slow, hysteretic | soft robotics |

The selection logic is **first-principles**, per
[01_first_principles_systems_engineering.md](../foundations/01-first_principles_systems_engineering.md):
write the load's torque-speed operating points, add inertia and friction, then find
the family whose envelope contains them with margin — *before* opening a vendor page.

---

## 2. The DC motor as a plant — first principles

A permanent-magnet DC motor obeys two coupled equations: an electrical one
(Kirchhoff around the armature) and a mechanical one (Newton on the rotor).

Electrical:
$$ V = R\,i + L\frac{di}{dt} + K_e\,\omega $$

Mechanical:
$$ J\frac{d\omega}{dt} = K_t\,i - b\,\omega - \tau_L $$

where $R,L$ are armature resistance/inductance, $K_e$ the back-EMF constant
(V·s/rad), $K_t$ the torque constant (N·m/A — in SI, $K_t = K_e$), $J$ rotor inertia,
$b$ viscous friction, and $\tau_L$ the load torque. Taking Laplace transforms with
$\tau_L=0$, the transfer function from voltage to speed is:

$$ \frac{\Omega(s)}{V(s)} = \frac{K_t}{(Ls+R)(Js+b) + K_t K_e} $$

Because electrical dynamics are far faster than mechanical ($L/R \ll J/b$), engineers
often neglect $L$ to get the dominant first-order form:

$$ \frac{\Omega(s)}{V(s)} \approx \frac{1/K_e}{\tau_m s + 1}, \qquad
\tau_m = \frac{RJ}{K_t K_e} $$

$\tau_m$ is the **mechanical time constant** — the single most useful number on a
motor datasheet. The no-load speed is $\omega_0 = V/K_e$; the stall torque is
$\tau_s = K_t V / R$. The torque-speed line $\tau = \tau_s(1 - \omega/\omega_0)$ is the
motor's entire DC personality.

```
torque
  ^
τ_s|*                  operating point must sit
  | \                  UNDER this line with margin
  |  \   . (ω*, τ*)
  |   \ /
  |    X-------- continuous (thermal) limit
  |     \
  +------\----------> speed
        ω_0
```

---

## 3. Motor sizing — torque, speed, thermal, duty

Sizing is a **thermal** problem disguised as a torque problem. Continuous torque is
limited by $I^2R$ heating, not by magnetics. The governing quantity is the
**RMS torque** over the duty cycle:

$$ \tau_\text{rms} = \sqrt{\frac{1}{T}\int_0^T \tau(t)^2\,dt} $$

Sizing rules:
1. **Peak torque** (acceleration + load) must be below the motor's peak line:
   $\tau_\text{peak} = J_\text{total}\,\dot\omega_\text{max} + \tau_\text{friction} + \tau_\text{load}$.
2. **RMS torque** must be below the *continuous* rating, or the winding overheats:
   the thermal model is $\Delta T = R_{th}\,P_\text{loss}$ with
   $P_\text{loss} \approx I^2 R = (\tau_\text{rms}/K_t)^2 R$.
3. **Speed** at the operating point must be below $\omega_0$ with headroom for bus-voltage
   sag (see [15](15-batteries-and-energy-storage.md)).

A worked trapezoidal move (accelerate, cruise, decelerate, dwell) is the canonical
exercise: compute $\dot\omega$ in each phase, the torque in each phase, then
$\tau_\text{rms}$. If $\tau_\text{rms}$ exceeds continuous rating, gear it down (next
section) or pick a bigger frame. **Margin convention:** ≥ 25% on continuous torque,
≥ 50% on peak, per the derating philosophy in
[13-engineering-reliability-and-failure-analysis.md](13-reliability-and-failure-analysis.md).

---

## 4. BLDC and PMSM commutation

A brushless motor replaces mechanical brushes with electronic commutation: the
controller must energize the right phases as a function of rotor angle. Two control
philosophies dominate.

- **Trapezoidal (six-step):** simple, uses Hall sensors, but produces torque ripple at
  the commutation edges. Fine for fans and propellers.
- **Field-Oriented Control (FOC):** transform the three-phase currents into a rotating
  $(d,q)$ frame via the **Clarke** and **Park** transforms, then control torque-producing
  $i_q$ and flux $i_d$ independently with PI loops. Smooth, efficient, the standard for
  gimbals, EVs, and robot joints.

The Park transform (rotor-frame currents):
$$ \begin{bmatrix} i_d \\ i_q \end{bmatrix} =
\begin{bmatrix} \cos\theta & \sin\theta \\ -\sin\theta & \cos\theta \end{bmatrix}
\begin{bmatrix} i_\alpha \\ i_\beta \end{bmatrix} $$

Torque in the $dq$ frame for a surface-PM machine:
$$ \tau = \frac{3}{2}\,p\,\lambda_m\,i_q $$
where $p$ is pole pairs and $\lambda_m$ the rotor flux linkage. Setting $i_d=0$
maximizes torque-per-amp. FOC needs rotor angle — from Hall sensors, an encoder
(§6), or a sensorless observer estimating back-EMF. Tools like the
SimpleFOC library, ODrive, and ST's MC Workbench implement this; understand the math
before trusting the wizard.

---

## 5. Gearing — ratio, reflected inertia, backlash

A gearbox of ratio $N$ (output slower than input) multiplies torque and divides
speed: $\tau_\text{out} = \eta N\,\tau_\text{motor}$, $\omega_\text{out} = \omega_\text{motor}/N$,
with efficiency $\eta$. The subtle and crucial effect is on **reflected inertia**: a
load inertia $J_L$ seen from the motor shaft is divided by $N^2$:

$$ J_\text{reflected} = \frac{J_L}{N^2} + J_\text{motor} $$

This is why a high ratio makes a heavy load *feel* light to the motor — but it also
amplifies the motor's own inertia at the output and slows the achievable bandwidth.
**Inertia matching** ($J_\text{motor} \approx J_L/N^2$) gives the best acceleration and
the most robust loop; ratios far from match waste torque accelerating the wrong mass.

| Gear type | Ratio/stage | Backlash | Efficiency | Notes |
|---|---|---|---|---|
| Spur | up to ~10 | moderate | ~95% | cheap, noisy |
| Planetary | 3–10 | low–moderate | ~90% | compact, coaxial |
| Harmonic (strain wave) | 30–320 | near-zero | ~70–85% | robots; light, precise, low efficiency |
| Cycloidal | 10–100 | low | ~85% | high shock load |
| Worm | 5–100 | moderate | ~50–70% | self-locking |
| Belt/pulley | 1–5 | low | ~95% | compliant, quiet |

**Backlash** — the angular slop before teeth engage on reversal — is the enemy of
precise position control. It introduces a deadband and limit cycles (§8). Harmonic
drives are prized in robotics precisely because their flexspline gives near-zero
backlash, paying for it in efficiency and torsional compliance.

---

## 6. Position sensing — encoders & resolvers

You cannot close a position loop on a quantity you cannot measure. The sensor sets the
ceiling on precision.

| Sensor | Principle | Resolution | Absolute? | Robustness |
|---|---|---|---|---|
| Incremental optical encoder | light through codewheel | very high (>10⁴ CPR) | no (needs index) | dust/oil sensitive |
| Absolute optical | gray-code disk | high | yes | sensitive |
| Magnetic (AS5047, etc.) | Hall/AMR over magnet | 12–14 bit | yes (single-turn) | rugged, cheap |
| Resolver | rotating transformer | analog, high | yes | military-grade, hot/vibration |
| Hall (commutation) | 3 switches | 6 states/rev | coarse | very rugged |
| Potentiometer | resistive | analog, low | yes | wears out |

Quadrature decoding gives **4× resolution** and direction from two phase-shifted
channels A and B:

```
A  __--__--__--      counts +1 on each edge if B leads,
B  _--__--__--_      -1 if B lags.  4 edges per cycle.
```

A 1000-line encoder thus yields 4000 counts/rev. The control law's quantization noise
and velocity-estimate noise both scale with counts/rev — see how a coarse encoder
forces a low velocity-loop bandwidth via numerical differentiation, motivating filtered
or observer-based velocity estimation per
[10-engineering-sensors-and-instrumentation.md](10-sensors-and-instrumentation.md).

---

## 7. Closing the loop — cascaded current/velocity/position

Servo control is almost always **cascaded**: a fast inner current (torque) loop, a
velocity loop around it, and an outer position loop. Each inner loop must be several
times faster than the loop enclosing it.

```
   +---------+   +----------+   +---------+   +-------+
θ*→| pos PID |→ω*| vel PID  |→i*| cur PI  |→V| motor |→θ
   +----^----+   +----^-----+   +----^----+   +---+---+
        |             |              |            |
        θ  ←──────────┴── ω (diff) ──┴── i (shunt)┘
```

Why cascade rather than one big PID? Because each loop can be tuned against a plant the
inner loops have already linearized: the current loop turns the motor into a torque
source, so the velocity loop sees a near-ideal integrator $1/Js$, which is trivial to
tune. Typical bandwidths: current 1–5 kHz, velocity 100–500 Hz, position 10–50 Hz.

A position PID with velocity feedforward:
$$ V = K_p(\theta^* - \theta) + K_d(\dot\theta^* - \dot\theta) + K_i\!\int(\theta^*-\theta)\,dt + K_{ff}\dot\theta^* $$

```python
# Discrete cascaded servo step (pseudocode), dt = control period
err_p   = theta_ref - theta
omega_ref = Kp_pos * err_p + Kff * omega_traj          # outer
err_v   = omega_ref - omega_est
iq_ref  = Kp_vel * err_v + Ki_vel * vel_integral       # middle
err_i   = iq_ref - iq_meas
v_q     = Kp_cur * err_i + Ki_cur * cur_integral       # inner (FOC d-axis -> 0)
apply_svpwm(v_d=0, v_q=clamp(v_q, -Vbus, Vbus), theta_elec)
```

Anti-windup on every integrator (clamp or back-calculation) is mandatory — saturation
without it is the classic cause of overshoot after a large step.

---

## 8. Compliance, backlash & resonance

Real drivetrains are not rigid. A motor coupled to a load through a finite-stiffness
shaft is a **two-mass resonant system**:

$$ J_m\ddot\theta_m = \tau_m - k(\theta_m - \theta_l) - c(\dot\theta_m-\dot\theta_l) $$
$$ J_l\ddot\theta_l = k(\theta_m - \theta_l) + c(\dot\theta_m-\dot\theta_l) - \tau_L $$

This yields an anti-resonance/resonance pair in the open-loop transfer function. The
resonant frequency is approximately:

$$ \omega_r = \sqrt{k\left(\frac{1}{J_m} + \frac{1}{J_l}\right)} $$

If the velocity-loop bandwidth approaches $\omega_r$, the system rings or goes
unstable. Mitigations: stiffen the coupling (raise $k$), add a **notch filter** at
$\omega_r$, lower the loop gain, or use input shaping on the command.

**Backlash** adds a hard nonlinearity: within the deadband the load is decoupled, so a
position loop with integral action **limit-cycles** (buzzes) around the target as it
crosses the slop on every correction. Cures: preload (spring or dual-motor anti-backlash),
harmonic/cycloidal gearing, or a deadband-aware controller that stops correcting inside
the slop. These nonlinear effects are exactly the plant imperfections the idealized
laws of [06-autonomy-control-theory.md](../autonomy/06-control-theory.md) assume away —
mechatronics is where you pay for that assumption.

---

## 9. Practice this week

1. Pull a real BLDC datasheet (e.g., a T-Motor or Maxon part); extract $K_t$, $R$, $L$,
   $J$, compute $\tau_m$, $\omega_0$, $\tau_s$, and sketch the torque-speed line.
2. Size a motor+gearbox for a 2 kg robot joint doing a 90° trapezoidal move in 0.4 s;
   compute $\tau_\text{peak}$, $\tau_\text{rms}$, and verify inertia matching.
3. Spin a motor under FOC with ODrive or SimpleFOC; tune the current loop, then the
   velocity loop, and observe how inner bandwidth caps outer bandwidth.
4. Deliberately introduce backlash (loose coupling) and watch the position loop
   limit-cycle; add a notch filter for a compliant shaft and measure the ring decay.

---

## 10. Sources & further study

- **Maxon Motor — *Formulae Handbook* and Academy.** The cleanest practical motor-sizing reference.
- **Krishnan — *Electric Motor Drives: Modeling, Analysis, and Control*.** FOC, PMSM, BLDC from first principles.
- **Ohnishi, Shibata & Murakami — disturbance-observer papers** for robust motion control.
- **Hughes & Drury — *Electric Motors and Drives*.** Intuitive, hardware-grounded.
- **De Silva — *Mechatronics: An Integrated Approach*.** Systems view of sensors, actuators, control.
- **ODrive / SimpleFOC documentation.** Open hardware/software you can actually run, pairing with [14-engineering-pcb-and-electronics-design.md](14-pcb-and-electronics-design.md).
- **NASA-HDBK-5300 and machine-design texts (Shigley)** for the mechanical drivetrain, linking to [04-career-mechanical-engineering.md](../career/04-mechanical-engineering.md).

> Framing note: A motor is not a "part you buy" — it is a controllable plant with a
> transfer function, a thermal limit, and a resonance. The engineers who build machines
> that move precisely are the ones who size from the duty cycle, match inertia through
> the gearbox, respect the encoder's resolution ceiling, and design the loop around the
> drivetrain's real compliance rather than the rigid one in the textbook.
