# Signal Processing — From Continuous Reality to Digital Estimates

> **Why this exists.** The world is continuous; your computer is discrete. Every sensor on
> your vehicle — IMU, barometer, camera, GPS, magnetometer — takes a continuous physical
> quantity and hands you a stream of samples corrupted by noise, drift, and aliasing.
> Signal processing is the discipline that turns those samples back into trustworthy
> estimates: it tells you how fast you must sample to avoid lying to yourself, how to
> separate signal from noise, how to measure vibration that is shaking your attitude
> estimate, and how to build filters that respond fast without amplifying garbage. Before
> a Kalman filter ever sees your IMU, a chain of sampling and filtering decisions has
> already determined whether the data is usable.
>
> **What mastering it makes you.** The engineer who looks at a noisy gyro trace and sees a
> *spectrum* — who knows the 200 Hz spike is the prop, the slow ramp is bias, and the
> high-frequency fuzz is aliasing from too-slow sampling — and who designs the
> anti-aliasing and digital filtering to fix it at the source.

This module sits between the physical sensors and the estimators that consume them. The
Fourier and convolution math rests on
[97-foundations-linear-algebra-applied.md](97-foundations-linear-algebra-applied.md) and
[03-foundations-mathematics.md](03-foundations-mathematics.md); the noise it suppresses is
characterized in
[96-foundations-probability-and-stochastic.md](96-foundations-probability-and-stochastic.md);
the filters it designs are optimized using
[95-foundations-optimization.md](95-foundations-optimization.md) and run with the numerics of
[98-foundations-numerical-methods.md](98-foundations-numerical-methods.md). Its outputs feed
the estimators of [28-autonomy-gnc.md](28-autonomy-gnc.md), the controllers of
[25-autonomy-control-theory.md](25-autonomy-control-theory.md), and the perception of
[20-autonomy-ml-ai.md](20-autonomy-ml-ai.md). Its channel-capacity cousin is
[100-foundations-information-theory.md](100-foundations-information-theory.md).

---

## Table of Contents

1. [Signals, systems, and convolution](#1-signals-systems-and-convolution)
2. [The Fourier transform — the frequency view](#2-the-fourier-transform--the-frequency-view)
3. [Sampling and the Nyquist theorem](#3-sampling-and-the-nyquist-theorem)
4. [The DFT and FFT](#4-the-dft-and-fft)
5. [Digital filters: FIR and IIR](#5-digital-filters-fir-and-iir)
6. [The Z-transform and filter stability](#6-the-z-transform-and-filter-stability)
7. [Spectral analysis and sensor filtering in practice](#7-spectral-analysis-and-sensor-filtering-in-practice)
8. [Where signal processing runs in the stack](#8-where-signal-processing-runs-in-the-stack)
9. [Sources & further study](#sources--further-study)

---

## 1. Signals, systems, and convolution

A **signal** is a function of time (or space): $x(t)$ continuous, or $x[n]$ a sampled
sequence. A **system** maps an input signal to an output. The systems we can analyze cleanly
are **linear time-invariant (LTI)**: linearity (scaling and superposition) plus
time-invariance (a delayed input gives a delayed output). An LTI system is *completely*
characterized by its **impulse response** $h[n]$ — its output when fed a unit impulse. Any
input is a sum of shifted impulses, so the output is the **convolution**:

$$
y[n] = (x * h)[n] = \sum_{k=-\infty}^{\infty} x[k]\, h[n-k].
$$

Convolution is "slide, multiply, sum." It is how a filter blends nearby samples, how a blur
spreads a pixel, and how the past influences the present. The single most useful fact in this
whole module is what convolution becomes in the frequency domain (§2): a **product**.

---

## 2. The Fourier transform — the frequency view

Any reasonable signal can be written as a sum of sinusoids. The **Fourier transform** is the
change of basis that reveals *how much of each frequency* a signal contains:

$$
X(f) = \int_{-\infty}^{\infty} x(t)\, e^{-i 2\pi f t}\, dt, \qquad
x(t) = \int_{-\infty}^{\infty} X(f)\, e^{i 2\pi f t}\, df.
$$

The complex exponential $e^{i2\pi ft}$ is the eigenfunction of every LTI system: feed a
sinusoid in, get the same-frequency sinusoid out, only scaled and phase-shifted. That is why
the frequency domain is so powerful — it **diagonalizes** convolution. The crown jewel is the
**convolution theorem**:

$$
y = x * h \quad\Longleftrightarrow\quad Y(f) = X(f)\,H(f).
$$

Filtering in time (an expensive convolution) becomes *multiplication* in frequency. $H(f)$ is
the **frequency response** — it tells you exactly which frequencies the filter passes
($|H|\approx 1$) and which it kills ($|H|\approx 0$). Design a filter and you are really
shaping $H(f)$. Other indispensable properties: **linearity**, **time-shift ↔ phase ramp**
($x(t-t_0)\leftrightarrow e^{-i2\pi ft_0}X(f)$), and **Parseval's theorem** (energy is
conserved across domains).

---

## 3. Sampling and the Nyquist theorem

To digitize $x(t)$ you sample every $T_s$ seconds, at rate $f_s = 1/T_s$. Sampling multiplies
the signal by an impulse train, which in frequency **replicates** the spectrum at every
multiple of $f_s$. If the copies overlap, frequencies fold back and masquerade as lower ones —
**aliasing** — and the original is unrecoverable. The **Nyquist-Shannon sampling theorem** is
the law that prevents this:

$$
f_s > 2 f_{\max},
$$

where $f_{\max}$ is the highest frequency present. Sample above twice the bandwidth and the
spectral copies do not overlap, so a perfect reconstruction exists (sinc interpolation).
Sample below it and a real 90 Hz vibration at $f_s = 100$ Hz appears as a fake 10 Hz wobble
that no downstream filter can ever remove — *it is now indistinguishable from a true 10 Hz
signal*. This is why every digitizing sensor needs an **analog anti-aliasing filter** *before*
the ADC, band-limiting the signal so the theorem's premise holds. Get this wrong and your IMU
hands the EKF lies that look exactly like real motion.

```python
import numpy as np

def alias_frequency(f_true, fs):
    """Return the apparent frequency of f_true sampled at rate fs.

    Frequencies above the Nyquist limit fs/2 fold back into the baseband.
    This shows numerically why an undersampled vibration masquerades as a
    lower-frequency signal that downstream filtering can never undo.
    """
    f = f_true % fs
    return min(f, fs - f)                    # fold around Nyquist
```

---

## 4. The DFT and FFT

For a finite sequence of $N$ samples the **Discrete Fourier Transform (DFT)** gives $N$
frequency bins:

$$
X[k] = \sum_{n=0}^{N-1} x[n]\, e^{-i 2\pi k n / N}, \qquad k = 0,\dots,N-1.
$$

Bin $k$ corresponds to physical frequency $k f_s / N$, so the **bin resolution** is
$\Delta f = f_s/N$ — longer records give finer frequency resolution. Computed directly the DFT
costs $O(N^2)$; the **Fast Fourier Transform (FFT)** exploits the recursive symmetry of the
roots of unity to do it in

$$
O(N \log N),
$$

the algorithm that made real-time spectral analysis possible. Two practical cautions:
**spectral leakage** (a frequency that does not land exactly on a bin smears across neighbors)
is tamed with a **window function** (Hann, Hamming) that tapers the record edges; and the DFT
assumes the signal is **periodic** with period $N$, so discontinuities at the wrap-around
create artifacts. The FFT is how you turn a chunk of gyro samples into the vibration spectrum
that tells you the prop is unbalanced.

---

## 5. Digital filters: FIR and IIR

A digital filter is an LTI system you implement in code. Two families:

**FIR (Finite Impulse Response)** — the output is a weighted sum of recent *inputs* only:

$$
y[n] = \sum_{k=0}^{M} b_k\, x[n-k].
$$

FIR filters are **always stable** (no feedback), can have *exactly linear phase* (no waveform
distortion, just a constant delay — vital when you fuse multiple sensors and must keep their
timing aligned), but need many taps for a sharp cutoff.

**IIR (Infinite Impulse Response)** — the output also depends on past *outputs* (feedback):

$$
y[n] = \sum_{k=0}^{M} b_k\, x[n-k] - \sum_{k=1}^{N} a_k\, y[n-k].
$$

IIR filters achieve a sharp response with far fewer coefficients (a 2nd-order biquad can do
what a 50-tap FIR does), mirroring analog designs (Butterworth, Chebyshev), but they can be
**unstable** and have nonlinear phase. The simplest useful IIR is the **exponential moving
average**, $y[n] = \alpha x[n] + (1-\alpha)y[n-1]$ — one multiply, one state, a tunable
low-pass that is the bread-and-butter smoother on resource-constrained flight controllers.

| Filter | Stability | Phase | Cost for sharp cutoff |
|---|---|---|---|
| FIR | always stable | can be linear | many taps |
| IIR | can be unstable | nonlinear | few coefficients |

```python
import numpy as np

def ema_filter(x, alpha):
    """Single-pole low-pass (exponential moving average).

    Each output blends the new sample with the previous output. Smaller
    alpha means heavier smoothing and more lag; this one-line IIR is the
    workhorse smoother for noisy sensor channels on small flight stacks.
    """
    y = np.empty_like(x, dtype=float)
    y[0] = x[0]
    for n in range(1, len(x)):
        y[n] = alpha * x[n] + (1 - alpha) * y[n - 1]
    return y
```

---

## 6. The Z-transform and filter stability

The **Z-transform** is the discrete-time analog of the Laplace transform — the tool for
analyzing digital filters' stability and frequency response:

$$
X(z) = \sum_{n=-\infty}^{\infty} x[n]\, z^{-n}, \qquad z \in \mathbb{C}.
$$

A filter's **transfer function** $H(z) = B(z)/A(z)$ has **zeros** (roots of the numerator,
where it nulls frequencies) and **poles** (roots of the denominator, where it resonates). The
frequency response is $H(z)$ evaluated on the **unit circle**, $z = e^{i\omega}$ — distance
from poles and zeros to the circle shapes the gain. The stability law is crisp:

$$
\text{a causal digital filter is stable} \iff \text{all poles lie strictly inside the unit circle } |z| < 1.
$$

This is the discrete mirror of the continuous "poles in the left half-plane" rule from
[25-autonomy-control-theory.md](25-autonomy-control-theory.md); the bilinear transform maps one
to the other. An IIR filter whose pole drifts onto or outside the unit circle will ring or blow
up — which is exactly why you check pole locations before trusting a hand-tuned biquad in a
control loop.

---

## 7. Spectral analysis and sensor filtering in practice

Theory meets the airframe here. A few patterns recur constantly:

- **IMU vibration.** Motors and props inject narrow-band vibration (often hundreds of Hz). The
  FFT of a gyro channel reveals the offending frequencies; a **notch filter** (a pair of zeros
  on the unit circle at that frequency) surgically removes them without killing the broadband
  motion signal the estimator needs. Modern flight stacks even *track* the prop frequency from
  RPM and steer the notch dynamically.
- **Low-pass before differentiation.** Differentiating a noisy signal amplifies high-frequency
  noise (the derivative's gain rises with frequency). Always low-pass first, or use a filter
  that differentiates and smooths together.
- **Complementary filter.** Fuse a noisy-but-unbiased accelerometer (good at low frequency)
  with a smooth-but-drifting gyro (good at high frequency) by low-passing one and high-passing
  the other so their responses sum to one: $\hat\theta = \alpha(\hat\theta + \omega\,dt) +
  (1-\alpha)\theta_{\text{acc}}$. It is the cheap, robust cousin of the Kalman filter and runs
  on the smallest microcontrollers.
- **Power spectral density.** To characterize noise, estimate the PSD (Welch's method: average
  FFTs of overlapping windows). A flat PSD is white noise; a $1/f$ slope is drift/flicker. This
  is how you get the $Q$ and $R$ covariances that the EKF in
  [96-foundations-probability-and-stochastic.md](96-foundations-probability-and-stochastic.md)
  demands — *measured*, not guessed.

The discipline: never feed raw samples to an estimator. Know your bandwidth, anti-alias before
sampling, characterize the noise spectrum, and filter with a design whose poles and phase you
understand.

---

## 8. Where signal processing runs in the stack

| Stack component | Signal-processing tool |
|---|---|
| IMU pre-filtering | anti-alias + notch + low-pass (§3, §5, §7) |
| Vibration diagnosis | FFT / PSD (§4, §7) |
| Attitude from IMU | complementary filter (§7) |
| Sensor noise covariance ($Q$, $R$) | spectral estimation (§7) |
| Derivative estimation | low-pass + differentiate (§5, §7) |
| Camera / image processing | 2-D convolution & Fourier (§1, §2) |
| Control-loop anti-aliasing | sample-rate & filter design (§3, §6) |
| GPS / RF front ends | sampling, mixing, filtering (§2, §3) |

The throughline: between the analog world and the clean state estimate sits a chain of
sampling and filtering choices, and every one of them can quietly corrupt the data or quietly
save it. Master the spectrum and you control what your estimator is even allowed to believe.

---

## Sources & further study

- **Oppenheim & Schafer, *Discrete-Time Signal Processing*** — the canonical DSP text;
  convolution, DFT, Z-transform, filter design, done rigorously.
- **Oppenheim & Willsky, *Signals and Systems*** — the continuous-time companion; Fourier and
  Laplace foundations and LTI intuition.
- **Smith, *The Scientist and Engineer's Guide to Digital Signal Processing*** — intuition-first,
  free online, excellent for the practical side of FIR/IIR and the FFT.
- **Lyons, *Understanding Digital Signal Processing*** — practitioner-focused, strong on
  real-world filtering and spectral analysis.
- **Brigham, *The Fast Fourier Transform and Its Applications*** — deep on the FFT and windowing.
- **Kay, *Fundamentals of Statistical Signal Processing*** — the bridge from filtering to
  estimation theory (and to the Kalman filter).

> Framing note: a sensor does not give you the truth; it gives you a *measurement of the truth,
> sampled and shaken*. Signal processing is the humility to ask what the measurement could
> secretly be hiding — an alias pretending to be motion, a vibration pretending to be drift —
> and the craft to band-limit, sample, and filter so that by the time your estimator sees the
> data, the lies have been removed at the source. Get this layer right and everything above it
> gets easier; get it wrong and no amount of clever filtering upstream can save you.
