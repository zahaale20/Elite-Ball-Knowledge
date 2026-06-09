# Sensors & Instrumentation — Measuring the Physical World Accurately

> **Why this exists.** Autonomy, control, and test all rest on one foundation:
> measurement. A flight controller can only stabilize what its gyro reports; an EKF can
> only fuse what its sensors observe; a safety case can only certify what an instrument
> recorded. Every sensor lies a little — it adds bias, noise, drift, scale error,
> latency, and nonlinearity — and the engineer's job is to know *exactly how* it lies and
> to correct for it. The gap between a sensor's datasheet and its behavior on your
> vibrating, hot, electrically noisy vehicle is where most "mystery" failures live.
>
> **What mastering it makes you.** The engineer who can read an IMU Allan-variance plot
> and state the gyro's bias-instability floor; who knows why a magnetometer near a motor
> is useless without hard/soft-iron calibration; who sizes an ADC's bits and a filter's
> bandwidth from the signal, not the catalog; and who treats time-stamping and grounding
> as first-class measurement problems.

Sensors are the front end of the estimation stack: their outputs feed the fusion of
[52-autonomy-sensor-fusion.md](../autonomy/52-sensor-fusion.md) and the state estimators of
[53-autonomy-state-estimation-advanced.md](../autonomy/53-state-estimation-advanced.md),
and they close the loops of the actuators in
[73-engineering-mechatronics-and-actuation.md](73-mechatronics-and-actuation.md).
The probability and statistics are from [03-foundations-mathematics.md](../foundations/03-mathematics.md);
the first-principles error budget from [01_first_principles_systems_engineering.md](../foundations/01-first_principles_systems_engineering.md).
Signal conditioning lives on the board of [78-engineering-pcb-and-electronics-design.md](78-pcb-and-electronics-design.md);
sensor reliability and drift over life are governed by
[77-engineering-reliability-and-failure-analysis.md](77-reliability-and-failure-analysis.md);
calibration is a verification activity per
[06-foundations-simulation-test-verification.md](../foundations/06-simulation-test-verification.md).
GNSS denial and spoofing — a sensor-integrity problem — is developed in
[26-autonomy-gnss-jamming-spoofing.md](../autonomy/26-gnss-jamming-spoofing.md).

---

## Table of Contents

1. [The measurement chain & error taxonomy](#1-the-measurement-chain--error-taxonomy)
2. [Inertial sensors — accelerometers & gyros](#2-inertial-sensors--accelerometers--gyros)
3. [Allan variance — characterizing drift](#3-allan-variance--characterizing-drift)
4. [GNSS, magnetometer, barometer, pressure](#4-gnss-magnetometer-barometer-pressure)
5. [Optical, range & proximity sensors](#5-optical-range--proximity-sensors)
6. [Noise, sampling & the ADC](#6-noise-sampling--the-adc)
7. [Signal conditioning & filtering](#7-signal-conditioning--filtering)
8. [Calibration & error modeling](#8-calibration--error-modeling)
9. [Practice this week](#9-practice-this-week)
10. [Sources & further study](#10-sources--further-study)

---

## 1. The measurement chain & error taxonomy

Every measurement passes through a chain, and each stage adds error:

```
physical → transducer → conditioning → ADC → digital → timestamp → estimator
quantity   (V,Ω,Hz)     (amp,filter)   (bits)  (counts)  (clock)
```

A sensor's true output relates to the measurand $x$ by an affine-plus-noise model that
you must identify:

$$ y = (1+s)\,x + b + n, \qquad n \sim \mathcal{N}(0,\sigma^2) $$

where $s$ is **scale-factor error**, $b$ is **bias** (offset), and $n$ is random
**noise**. The error taxonomy every instrument engineer carries:

| Error | Symptom | Cause | Fix |
|---|---|---|---|
| Bias / offset | constant shift | manufacturing, temperature | calibrate, estimate online |
| Scale factor | gain wrong | gain tolerance | calibrate against reference |
| Nonlinearity | curved response | physics, saturation | lookup table / polynomial |
| Drift | slow wander | temperature, aging | thermal model, recalibration |
| Random noise | jitter | thermal/electronic | filter, average |
| Quantization | stair-step | finite ADC bits | more bits, dither |
| Latency | lag | filtering, comms | timestamp, compensate |
| Cross-axis | one axis bleeds into another | misalignment | calibration matrix |

**Accuracy vs precision:** accuracy is closeness to truth (bias), precision is
repeatability (noise). They are independent — a sensor can be precise and wrong.

---

## 2. Inertial sensors — accelerometers & gyros

An **accelerometer** measures specific force (proper acceleration), not coordinate
acceleration. At rest it reads $+g$ upward — gravity and the supporting force are
indistinguishable from inertia (equivalence principle). MEMS accelerometers sense the
displacement of a proof mass on springs via a capacitive bridge:

$$ a = \frac{F}{m} = \frac{k\,\Delta x}{m} $$

A **gyroscope** measures angular rate. MEMS gyros use the **Coriolis effect**: a
vibrating mass driven at velocity $\vec v$ experiences a Coriolis force when the frame
rotates at $\vec\Omega$:

$$ \vec F_c = -2m\,\vec\Omega \times \vec v $$

The sensed orthogonal displacement is proportional to rate. Fiber-optic (FOG) and
ring-laser (RLG) gyros use the **Sagnac effect** — a phase shift between
counter-propagating light proportional to rotation — and are vastly lower-drift (and
costlier) than MEMS.

| Grade | Gyro bias instability | Used in |
|---|---|---|
| Consumer MEMS | 10–100 °/hr | phones, hobby drones |
| Industrial MEMS | 1–10 °/hr | UAVs, robotics |
| Tactical | 0.1–1 °/hr | guided munitions |
| Navigation (FOG/RLG) | 0.001–0.01 °/hr | aircraft INS, submarines |

The fundamental problem: integrating a biased gyro gives angle error that grows
**linearly** with time; integrating accelerometer error gives position error that grows
**quadratically**. This is why inertial-only navigation drifts and must be aided — the
core argument of [52-autonomy-sensor-fusion.md](../autonomy/52-sensor-fusion.md).

---

## 3. Allan variance — characterizing drift

You cannot characterize a gyro with a single noise number; its error has structure
across time scales. **Allan variance** (originally for clocks) reveals it. Log a
stationary sensor for hours, then compute the variance of the average over cluster time
$\tau$:

$$ \sigma_A^2(\tau) = \frac{1}{2(N-1)}\sum_{i}\left(\bar y_{i+1} - \bar y_i\right)^2 $$

Plotting $\sigma_A(\tau)$ vs $\tau$ log-log exposes each noise process by its slope:

```
σ_A(τ)
  |   \                              /
  |    \  -1/2 slope            +1/2 /  rate random walk
  |     \ (angle random walk)      /
  |      \____________            /
  |        bias instability  \__/  (flat floor = min)
  +------------------------------------> τ (log)
```

| Slope | Noise process | Datasheet name |
|---|---|---|
| $-1$ | quantization | — |
| $-1/2$ | white noise | Angle/Velocity Random Walk (ARW/VRW) |
| $0$ (floor) | bias instability | the headline spec |
| $+1/2$ | rate random walk | RRW |
| $+1$ | rate ramp | drift |

The **bias-instability floor** is the lowest the curve reaches — the best you can do by
averaging before drift takes over. The $-1/2$ region's value at $\tau=1\,$s is the
ARW (°/√hr), which sets how much a gyro can be smoothed. Tools: the `allan_variance_ros`
package, or a short NumPy script. This is the rigorous way to compare two IMUs.

---

## 4. GNSS, magnetometer, barometer, pressure

**GNSS** measures pseudorange to ≥4 satellites and solves for position + clock bias.
Single-point accuracy is a few meters; RTK/PPK with carrier phase reaches centimeters.
Error sources: ionosphere/troposphere delay, multipath, satellite geometry (DOP), and —
critically — jamming and spoofing per
[26-autonomy-gnss-jamming-spoofing.md](../autonomy/26-gnss-jamming-spoofing.md). GNSS is
slow (1–10 Hz), absolute, and the canonical aiding source for an INS.

**Magnetometer** senses Earth's field (~25–65 µT) for heading. It is corrupted by:
- **Hard-iron** offset: permanent magnetic sources on the vehicle → constant bias $\vec b$.
- **Soft-iron** distortion: ferrous material warps the field → a $3\times3$ matrix $A$.

The calibration model and its fix:
$$ \vec m_\text{true} = A^{-1}(\vec m_\text{meas} - \vec b) $$
Recover $A,\vec b$ by rotating the sensor through all orientations; the raw data forms
an ellipsoid that calibration maps to a sphere. Near a running motor the field swamps
Earth's — keep magnetometers far from current paths (see
[78-engineering-pcb-and-electronics-design.md](78-pcb-and-electronics-design.md)).

**Barometer / pressure** sensors give altitude from the barometric formula:
$$ h = \frac{T_0}{L}\left[1 - \left(\frac{p}{p_0}\right)^{\frac{RL}{g M}}\right] $$
Resolution of modern MEMS baros (~10 cm) makes them excellent vertical aids, but they
drift with weather pressure changes — relative, not absolute, altitude.

---

## 5. Optical, range & proximity sensors

| Sensor | Principle | Output | Limits |
|---|---|---|---|
| Camera | photons → pixel charge | image | light, motion blur, scaleless |
| LiDAR | time-of-flight of laser | point cloud | fog, rain, cost, reflectivity |
| Radar | RF reflection + Doppler | range+velocity | low resolution, multipath |
| Ultrasonic | acoustic ToF | range (short) | wind, soft targets |
| ToF / structured light | modulated IR | depth image | sunlight, range |
| Optical flow | image motion | velocity over ground | texture, altitude |
| Encoder (optical) | codewheel | angle (see §6 of [73](73-mechatronics-and-actuation.md)) | dust |

**Time-of-flight** range: $d = c\,\Delta t / 2$. The precision is set by timing
resolution — a 1 ns timing error is ~15 cm. LiDAR achieves mm precision via picosecond
timing or phase measurement. **Radar** adds Doppler: a relative velocity $v$ shifts the
return frequency by $f_d = 2vf_0/c$, giving velocity directly — invaluable in fog where
optical sensors fail. The complementary-strengths table is the heart of why perception
fuses modalities ([50-autonomy-perception-deep.md](../autonomy/50-perception-deep.md),
[52-autonomy-sensor-fusion.md](../autonomy/52-sensor-fusion.md)).

---

## 6. Noise, sampling & the ADC

Analog signals become numbers in the **ADC**. Two specs dominate: resolution (bits) and
sample rate. An $N$-bit ADC over range $V_\text{ref}$ has quantization step (LSB):

$$ q = \frac{V_\text{ref}}{2^N}, \qquad \sigma_q = \frac{q}{\sqrt{12}} $$

The ideal signal-to-noise ratio of an $N$-bit converter:
$$ \text{SNR}_\text{dB} = 6.02\,N + 1.76 $$

So each bit buys ~6 dB. The **effective number of bits (ENOB)** accounts for real noise
and distortion — always below the nominal $N$.

**Nyquist:** sample at more than twice the highest signal frequency, else aliasing folds
high frequencies onto low ones irreversibly:
$$ f_s > 2 f_\text{max} $$

You *must* place an analog **anti-aliasing filter** before the ADC to kill content above
$f_s/2$ — no digital filter can undo aliasing after sampling. **Oversampling + averaging**
trades speed for resolution: averaging $4^k$ samples gains $k$ effective bits (with a
white-noise, dithered signal). This and proper grounding (§7) are where bench accuracy
meets vehicle reality.

---

## 7. Signal conditioning & filtering

Between transducer and ADC sits conditioning: amplify, level-shift, filter, isolate.

- **Instrumentation amplifier:** high-impedance, high-CMRR differential gain for tiny
  bridge/thermocouple signals; rejects common-mode pickup.
- **Anti-aliasing filter:** analog low-pass below Nyquist (§6).
- **Low-pass / band-pass:** shape the noise. A first-order RC has corner
  $f_c = 1/(2\pi RC)$ and rolls off −20 dB/decade.

A discrete low-pass (exponential moving average) is the workhorse in firmware:
$$ y_k = \alpha\,x_k + (1-\alpha)\,y_{k-1}, \qquad \alpha = \frac{dt}{\tau + dt} $$

Filtering trades **noise vs latency**: more smoothing means more lag, which in a control
loop costs phase margin (see [25-autonomy-control-theory.md](../autonomy/25-control-theory.md)).
The right cut is the lowest bandwidth that still passes the signal you need.

**Grounding & shielding** ruin more measurements than algorithms. Ground loops inject
mains hum; long unshielded leads pick up EMI from motors and switching supplies.
Single-point grounds, twisted differential pairs, guard traces, and Kelvin (4-wire)
sensing for low resistances are the standard cures, detailed in
[78-engineering-pcb-and-electronics-design.md](78-pcb-and-electronics-design.md).

---

## 8. Calibration & error modeling

Calibration estimates the parameters $(s, b, A, \dots)$ of the error model so the
software can invert them. The general IMU model with misalignment, scale, and bias:

$$ \vec y = M\,\vec x + \vec b + \vec n, \qquad
M = \underbrace{S}_{\text{scale}}\underbrace{T}_{\text{misalignment}} $$

Calibration strategies:
- **Six-position (accelerometer):** measure $\pm g$ on each axis → recover bias and scale
  per axis (gravity is the reference).
- **Rate-table (gyro):** spin at known rates → scale and bias.
- **Ellipsoid fit (magnetometer):** rotate through all attitudes; least-squares fit an
  ellipsoid, map to sphere → hard/soft-iron.
- **Temperature calibration:** sweep temperature, fit bias/scale as polynomials in $T$;
  store the model and compensate online (MEMS bias is strongly thermal).
- **Online estimation:** carry sensor biases as states in the EKF
  ([52-autonomy-sensor-fusion.md](../autonomy/52-sensor-fusion.md)) so they are tracked in
  flight rather than assumed constant.

Every calibration claim must be **verified against an independent reference** and
documented — calibration is part of the verification regime of
[06-foundations-simulation-test-verification.md](../foundations/06-simulation-test-verification.md)
and, for certified systems, part of the assurance evidence in
[09-foundations-safety-assurance.md](../foundations/09-safety-assurance.md).

```python
# Magnetometer hard/soft-iron calibration (sketch)
raw = collect_rotating_samples()          # rotate through all attitudes
A, b = fit_ellipsoid_to_sphere(raw)       # least-squares ellipsoid fit
def calibrate(m):                         # apply online
    return A_inv @ (m - b)                # -> field on unit sphere
```

---

## 9. Practice this week

1. Log a stationary IMU for 2+ hours and compute its Allan variance; read off ARW and
   bias instability, and compare to the datasheet.
2. Calibrate a magnetometer by ellipsoid fit; plot raw vs calibrated as a sphere.
3. Sample a signal above and below Nyquist; observe aliasing, then add an anti-aliasing
   filter and confirm it disappears.
4. Build a thermal-bias model for a MEMS gyro by sweeping temperature; compensate and
   measure the residual drift improvement.

---

## 10. Sources & further study

- **Groves — *Principles of GNSS, Inertial, and Multisensor Integrated Navigation Systems*.** The reference for inertial and GNSS error modeling.
- **Titterton & Weston — *Strapdown Inertial Navigation Technology*.** Deep IMU physics and error propagation.
- **IEEE Std 952 / 1554** — gyro and accelerometer specification and Allan-variance methods.
- **Fraden — *Handbook of Modern Sensors*.** Physics of nearly every transducer.
- **Horowitz & Hill — *The Art of Electronics*.** Signal conditioning, noise, grounding done right.
- **Kester (Analog Devices) — *Data Conversion Handbook*.** ADC theory, ENOB, sampling.
- **El-Sheimy et al. — Allan-variance papers** for inertial sensor characterization.

> Framing note: A sensor reading is a claim, not a fact. The instrumentation engineer's
> craft is to know the error model — bias, scale, drift, noise, latency — characterize it
> with tools like Allan variance, correct it with calibration, and propagate honest
> uncertainty downstream. Systems navigate well not because their sensors are perfect, but
> because their engineers measured exactly how imperfect they are.
