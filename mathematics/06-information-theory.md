# Information Theory — Entropy, Channels & the Limits of Communication

> **Why this exists.** Information theory answers the deepest questions in your autonomy
> stack with hard numbers: *How much can this data be compressed? How many bits can this
> radio link reliably carry through jamming? How much does a sensor actually tell me about
> the world? How different are two probability distributions?* Claude Shannon proved in
> 1948 that information is a measurable, physical quantity with absolute limits — limits no
> cleverness can beat. Those limits govern your telemetry downlink, your sensor-fusion
> gains, your neural network's loss function, and your ability to operate in a contested RF
> environment. Entropy is not an abstraction; it is the currency in which uncertainty,
> communication, and learning are all denominated.
>
> **What mastering it makes you.** The engineer who can say *exactly* how much a new sensor
> reduces uncertainty, why a comms link fails at a given SNR no matter the modulation, and
> why minimizing cross-entropy is the same act as maximizing likelihood — and who therefore
> designs systems against fundamental limits rather than rules of thumb.

This module is the cross-cutting capstone of the foundations band. It is built on the
probability of [02-foundations-probability-and-stochastic.md](02-probability-and-stochastic.md)
and the general math of [03-foundations-mathematics.md](../foundations/03-mathematics.md); its
divergences are minimized by [01-foundations-optimization.md](01-optimization.md);
its channels are sampled and filtered per
[05-foundations-signal-processing.md](05-signal-processing.md). It quantifies what
sensors deliver in [09-autonomy-gnc.md](../autonomy/09-gnc.md), defines the loss functions of
[01-autonomy-ml-ai.md](../autonomy/01-ml-ai.md), informs the value-of-information in
[10-autonomy-planning-decision.md](../autonomy/10-planning-decision.md), and bounds the links that
control loops in [06-autonomy-control-theory.md](../autonomy/06-control-theory.md) depend on.

---

## Table of Contents

1. [Entropy — measuring uncertainty in bits](#1-entropy--measuring-uncertainty-in-bits)
2. [Joint, conditional entropy, and mutual information](#2-joint-conditional-entropy-and-mutual-information)
3. [KL divergence — the distance between beliefs](#3-kl-divergence--the-distance-between-beliefs)
4. [Source coding — the limit of compression](#4-source-coding--the-limit-of-compression)
5. [Channel capacity — the limit of communication](#5-channel-capacity--the-limit-of-communication)
6. [The Gaussian channel and Shannon-Hartley](#6-the-gaussian-channel-and-shannon-hartley)
7. [Information theory in ML and sensing](#7-information-theory-in-ml-and-sensing)
8. [Where information limits bind the stack](#8-where-information-limits-bind-the-stack)
9. [Sources & further study](#sources--further-study)

---

## 1. Entropy — measuring uncertainty in bits

How much uncertainty is in a random variable? Shannon's **entropy** answers it. For a discrete
$X$ with distribution $p(x)$:

$$
H(X) = -\sum_x p(x) \log_2 p(x) \quad \text{[bits]}.
$$

Read it as the **average surprise**: the surprise of an outcome of probability $p$ is
$\log_2(1/p)$ — rare events are surprising, certain events ($p=1$) carry zero information.
Entropy is the expected surprise, and equivalently the **minimum average number of bits needed
to encode** the outcomes. Key facts that pin down its meaning:

- $H(X) \ge 0$, with equality iff $X$ is deterministic (no uncertainty).
- For $n$ outcomes, $H(X)$ is **maximized at $\log_2 n$** by the *uniform* distribution —
  maximum ignorance. A fair coin has $H = 1$ bit; a biased coin carries less.
- Entropy is the unique measure (up to scale) satisfying continuity, monotonicity, and
  additivity over independent variables.

```python
import numpy as np

def entropy(p):
    """Shannon entropy in bits of a discrete distribution p.

    Each outcome contributes its probability times its surprise,
    log2(1/p). We mask zero probabilities since they contribute nothing
    and would otherwise produce a 0*(-inf) NaN.
    """
    p = np.asarray(p, dtype=float)
    p = p[p > 0]                            # 0 log 0 := 0
    return -np.sum(p * np.log2(p))
```

The **differential entropy** of a continuous variable replaces the sum with an integral,
$h(X) = -\int p(x)\log p(x)\,dx$. A central result: among all distributions with a fixed
variance $\sigma^2$, the **Gaussian maximizes entropy**, with $h = \tfrac12\log_2(2\pi e
\sigma^2)$ — the information-theoretic reason the Gaussian is the "least-assuming" noise model
(tying back to §4 of
[02-foundations-probability-and-stochastic.md](02-probability-and-stochastic.md)).

---

## 2. Joint, conditional entropy, and mutual information

For two variables, the **joint entropy** $H(X,Y) = -\sum_{x,y} p(x,y)\log_2 p(x,y)$ measures
their combined uncertainty. The **conditional entropy** measures what remains in $X$ once you
know $Y$:

$$
H(X \mid Y) = -\sum_{x,y} p(x,y)\log_2 p(x\mid y) = H(X,Y) - H(Y).
$$

Knowing $Y$ can only reduce (never increase) uncertainty about $X$: $H(X\mid Y) \le H(X)$. The
gap between them is the single most useful quantity for sensing — **mutual information**:

$$
I(X;Y) = H(X) - H(X\mid Y) = \sum_{x,y} p(x,y)\log_2 \frac{p(x,y)}{p(x)p(y)}.
$$

$I(X;Y)$ is **how many bits observing $Y$ tells you about $X$**. It is symmetric
($I(X;Y)=I(Y;X)$), non-negative, and zero exactly when $X$ and $Y$ are independent (a useless
sensor). This is the rigorous answer to "how much does this measurement actually help?" — and
the basis of **information-greedy active sensing**: point the sensor where mutual information
with the unknown state is highest. The relationships form a clean Venn picture:

$$
I(X;Y) = H(X) + H(Y) - H(X,Y).
$$

---

## 3. KL divergence — the distance between beliefs

The **Kullback-Leibler divergence** measures how far a distribution $q$ is from a reference
$p$ — the expected number of *extra* bits you waste coding samples from $p$ using a code built
for $q$:

$$
D_{\mathrm{KL}}(p \,\|\, q) = \sum_x p(x) \log_2 \frac{p(x)}{q(x)} \;\ge\; 0,
$$

with equality iff $p = q$ (Gibbs' inequality). It is **not symmetric** and not a true metric,
but it is the natural notion of "how wrong is my model." Mutual information is itself a KL
divergence: $I(X;Y) = D_{\mathrm{KL}}\big(p(x,y)\,\|\,p(x)p(y)\big)$ — the divergence of the
joint from the independent product.

KL is everywhere in learning and inference:

- **Variational inference** minimizes $D_{\mathrm{KL}}(q\|p)$ to approximate an intractable
  posterior $p$ with a tractable $q$.
- **Cross-entropy loss** decomposes as $H(p,q) = H(p) + D_{\mathrm{KL}}(p\|q)$; since $H(p)$ is
  fixed by the data, minimizing cross-entropy *is* minimizing KL divergence — and, for a model
  $q_\theta$, is equivalent to **maximizing likelihood**. That is why classifiers train on
  cross-entropy (see [01-autonomy-ml-ai.md](../autonomy/01-ml-ai.md)).
- **Policy regularization** (e.g. trust-region RL) bounds the KL step between successive
  policies to keep updates stable.

```python
import numpy as np

def kl_divergence(p, q, eps=1e-12):
    """KL divergence D(p || q) in bits between two distributions.

    It is the expected extra coding cost of using q's code for data drawn
    from p. We floor q to avoid log of zero; the result is non-negative
    and zero only when the distributions match.
    """
    p = np.asarray(p, float); q = np.asarray(q, float)
    mask = p > 0
    return np.sum(p[mask] * np.log2(p[mask] / np.maximum(q[mask], eps)))
```

---

## 4. Source coding — the limit of compression

**Shannon's source coding theorem** sets the hard floor on lossless compression: a source with
entropy $H(X)$ bits per symbol cannot be encoded, on average, in fewer than $H(X)$ bits per
symbol — and codes approaching $H(X)$ exist. You cannot compress below entropy; you can only
get arbitrarily close.

The practical machinery: assign **short codewords to likely symbols, long ones to rare
symbols**. **Huffman coding** builds the optimal prefix-free code symbol-by-symbol;
**arithmetic coding** and modern entropy coders (ANS) approach the entropy limit even more
tightly. The **prefix property** (no codeword is a prefix of another) makes the stream
instantly decodable, and the **Kraft inequality** $\sum_i 2^{-\ell_i} \le 1$ governs which
codeword lengths $\ell_i$ are even achievable. Every file zip, every compressed telemetry
stream, every JPEG's final stage is this theorem cashed out. The gap between a naive fixed-width
encoding and the entropy is the *redundancy* you are paying to transmit for free.

---

## 5. Channel capacity — the limit of communication

Now send information through a noisy channel. The channel is described by $p(y\mid x)$ — the
probability of receiving $y$ given you sent $x$. The **channel capacity** is the maximum mutual
information over all input distributions:

$$
C = \max_{p(x)} I(X;Y) \quad \text{[bits per channel use]}.
$$

**Shannon's channel coding theorem** — the most surprising result in the field — states: for
any rate $R < C$, there exist codes achieving **arbitrarily small error probability**; for
$R > C$, reliable communication is *impossible*. Noise does not force errors; it forces you to
*slow down*. As long as you stay under capacity, clever coding (adding structured redundancy)
drives the error rate to zero. This is why error-correcting codes (Hamming, Reed-Solomon,
LDPC, turbo codes) exist and why a link that looks hopelessly noisy can still carry perfect
data at a reduced rate.

**Example — the binary symmetric channel.** Each bit flips with probability $p$. Its capacity
is

$$
C = 1 - H_b(p), \qquad H_b(p) = -p\log_2 p - (1-p)\log_2(1-p).
$$

At $p=0$ (clean), $C=1$ bit. At $p=0.5$ (pure noise), $C=0$ — the output is independent of the
input, no information gets through. A 10% flip rate still leaves $C \approx 0.53$ bits per use,
recoverable with coding.

---

## 6. The Gaussian channel and Shannon-Hartley

The continuous channel that models real radios adds Gaussian noise of power $N$ to a signal of
power $S$ over bandwidth $B$. Its capacity is the celebrated **Shannon-Hartley theorem**:

$$
C = B \log_2\!\left(1 + \frac{S}{N}\right) \quad \text{[bits per second]}.
$$

This one equation governs every wireless link in your stack. Read what it says:

- Capacity grows **linearly with bandwidth** $B$ but only **logarithmically with SNR** —
  throwing power at a link gives diminishing returns; widening the band is far more effective.
  (This is why modern systems chase spectrum and spread-spectrum techniques.)
- In a **jamming/EW** scenario (see counter-UAS and GNSS-denial themes), the adversary's goal
  is to crush $S/N$ — raise $N$ with barrage noise, or force you to spread $S$ thin. The
  defender's response — frequency hopping, spread spectrum, directional antennas, coding —
  is a direct fight over the terms of this equation.
- It sets the **absolute** ceiling: no modulation or protocol can exceed $C$. When your
  telemetry downlink saturates, Shannon, not your firmware, is the wall.

```python
import numpy as np

def shannon_capacity(bandwidth_hz, snr_linear):
    """Shannon-Hartley capacity in bits/sec for a Gaussian channel.

    Capacity rises linearly with bandwidth but only logarithmically with
    signal-to-noise ratio, which is why widening the band beats raising
    power and why jammers attack the SNR term directly.
    """
    return bandwidth_hz * np.log2(1.0 + snr_linear)
```

---

## 7. Information theory in ML and sensing

Information theory is not just for comms — it is the quiet backbone of learning and estimation:

- **Cross-entropy / log-loss.** The default classification objective; minimizing it maximizes
  likelihood and minimizes $D_{\mathrm{KL}}$ between the data and the model (§3).
- **Maximum entropy modeling.** When several distributions fit your constraints, choose the
  one of *maximum entropy* — it assumes the least beyond what the data forces. This justifies
  the Gaussian noise model, the softmax, and exponential-family distributions.
- **The information bottleneck.** A representation $Z$ of input $X$ predicting target $Y$ should
  maximize $I(Z;Y)$ while minimizing $I(Z;X)$ — keep what predicts, discard the rest. A lens on
  what good features and deep representations are doing.
- **Mutual-information sensing.** Choose the next measurement (where to look, which sensor to
  task) to maximize $I(\text{measurement}; \text{state})$ — optimal active perception and
  experimental design.
- **Rate-distortion theory.** The lossy-compression counterpart: the minimum bits to represent
  a source within a tolerated distortion — the foundation of perceptual codecs and of deciding
  *what fidelity your link can afford*.

The unifying idea: learning, estimation, and communication are all about **moving information
efficiently** — extracting it from data, compressing it without loss of meaning, and pushing it
through noisy channels up to a hard limit.

---

## 8. Where information limits bind the stack

| Stack component | Information-theoretic limit |
|---|---|
| Telemetry / video downlink | Shannon-Hartley capacity (§6) |
| Error-correcting codes | channel coding theorem (§5) |
| Sensor value-of-information | mutual information (§2) |
| Active perception / where to look | maximize $I$ (§2, §7) |
| Classifier / detector training | cross-entropy = KL (§3, §7) |
| Telemetry compression | source coding / entropy (§4) |
| EW / jamming resilience | SNR vs. capacity tradeoff (§6) |
| Variational inference, RL policies | KL divergence (§3) |

The throughline: every channel, sensor, and model has a fundamental capacity set by entropy and
noise, and no engineering can exceed it — only approach it. The mature engineer designs *toward*
these limits, knowing exactly how much information a system can carry, extract, or learn, and
stops chasing impossible gains the moment Shannon says the wall is there.

---

## Sources & further study

- **Cover & Thomas, *Elements of Information Theory*** — the definitive modern text; entropy,
  mutual information, source and channel coding, rate-distortion, all rigorous and readable.
- **Shannon, *"A Mathematical Theory of Communication"* (1948)** — the founding paper; still
  remarkably clear and worth reading in the original.
- **MacKay, *Information Theory, Inference, and Learning Algorithms*** — ties information theory
  to Bayesian inference and machine learning; free online and superb.
- **Gallager, *Information Theory and Reliable Communication*** — deep on channel coding and
  capacity.
- **Proakis & Salehi, *Digital Communications*** — the engineering bridge from capacity to real
  modulation and coding.
- **Tishby et al., *"The Information Bottleneck Method"*** — the information-theoretic lens on
  representation learning.

> Framing note: Shannon's gift was to make *information* a physical quantity with conservation
> laws and hard limits, as real as energy or mass. Once you see uncertainty measured in bits,
> communication bounded by capacity, and learning as the minimization of divergence, a dozen
> separate engineering problems collapse into one question: *how much information is here, and
> how efficiently can I move it?* That question — asked of a sensor, a radio, or a model — is
> the most powerful diagnostic in this entire curriculum.
