# Electromagnetics — Fields, Waves & Why Antennas and Radar Work

> **Why this exists.** Modern autonomy is blind and deaf without electromagnetics. GPS, datalinks, radar, electronic warfare, electro-optical sensors — all are EM phenomena. A jammed GNSS receiver, a radar that cannot detect a low-RCS target, an antenna with the wrong pattern: each failure is a Maxwell's-equations problem in disguise. If you cannot reason about wave propagation, impedance matching, and antenna gain, you cannot design or defeat the sensing and communications that make a vehicle autonomous in contested space. EM is the physics of *perceiving and being perceived* at a distance.

> **What mastering it makes you.** The engineer who can compute a link budget in their head, explain why a stealth shape scatters energy away from the radar, size an antenna for a given beamwidth, and reason about how a jammer raises the noise floor your GPS must overcome. You become the bridge between the abstract "the link is up" and the physical reality of fields propagating through a contested, lossy, adversarial medium.

This module underpins the RF and sensing physics of [67-engineering-rf-and-spectrum.md](67-engineering-rf-and-spectrum.md), the GNSS jamming/spoofing analysis in [26-autonomy-gnss-jamming-spoofing.md](26-autonomy-gnss-jamming-spoofing.md), and counter-UAS electronic warfare in [27-autonomy-counter-uas-ew.md](27-autonomy-counter-uas-ew.md). The vector calculus (divergence, curl, Laplacian) is developed in [03-foundations-mathematics.md](03-foundations-mathematics.md); the wave/oscillation mathematics parallels [102-foundations-physics-for-engineers.md](102-foundations-physics-for-engineers.md); the flux/divergence intuition mirrors fluid continuity in [103-foundations-thermodynamics-and-fluids.md](103-foundations-thermodynamics-and-fluids.md). Sensor implications feed [50-autonomy-perception-deep.md](50-autonomy-perception-deep.md).

---

## 1. Maxwell's equations — all of classical EM on a postcard

Four equations govern every electric field $\mathbf E$ and magnetic field $\mathbf B$. In differential form (SI units):

$$
\begin{aligned}
\nabla\cdot\mathbf E &= \frac{\rho}{\varepsilon_0} && \text{(Gauss: charge sources } \mathbf E) \\
\nabla\cdot\mathbf B &= 0 && \text{(no magnetic monopoles)} \\
\nabla\times\mathbf E &= -\frac{\partial \mathbf B}{\partial t} && \text{(Faraday: changing } \mathbf B \text{ induces } \mathbf E) \\
\nabla\times\mathbf B &= \mu_0\mathbf J + \mu_0\varepsilon_0\frac{\partial \mathbf E}{\partial t} && \text{(Ampère–Maxwell)}
\end{aligned}
$$

The genius is Maxwell's **displacement current** $\mu_0\varepsilon_0 \,\partial\mathbf E/\partial t$ — without it the equations are inconsistent with charge conservation, and *with* it they predict self-propagating waves. The divergence equations are the EM analogues of fluid continuity; the curl equations couple $\mathbf E$ and $\mathbf B$ into a single entity, the electromagnetic field.

---

## 2. Deriving the wave equation — light falls out of the math

Take the curl of Faraday's law in free space ($\rho = 0$, $\mathbf J = 0$):

$$
\nabla\times(\nabla\times\mathbf E) = -\frac{\partial}{\partial t}(\nabla\times\mathbf B).
$$

Use the identity $\nabla\times(\nabla\times\mathbf E) = \nabla(\nabla\cdot\mathbf E) - \nabla^2\mathbf E = -\nabla^2\mathbf E$ (since $\nabla\cdot\mathbf E=0$), and substitute Ampère–Maxwell:

$$
\boxed{\;\nabla^2\mathbf E = \mu_0\varepsilon_0 \frac{\partial^2 \mathbf E}{\partial t^2}.\;}
$$

This is a wave equation with propagation speed

$$
c = \frac{1}{\sqrt{\mu_0\varepsilon_0}} \approx 3\times10^8 \text{ m/s}.
$$

Maxwell computed this number from electrostatic and magnetostatic measurements and realized it equaled the measured speed of light — *therefore light is an electromagnetic wave*. One of the great unifications in physics, and the foundation of every wireless link.

### 2.1 Plane-wave solutions

A solution is $\mathbf E = \mathbf E_0 e^{j(\mathbf k\cdot\mathbf r - \omega t)}$ with dispersion $\omega = c|\mathbf k|$, wavelength $\lambda = 2\pi/|\mathbf k| = c/f$. $\mathbf E$, $\mathbf B$, and $\mathbf k$ are mutually perpendicular (transverse wave), with $|\mathbf E| = c|\mathbf B|$. Energy flows along the **Poynting vector**

$$
\mathbf S = \frac{1}{\mu_0}\,\mathbf E\times\mathbf B \quad [\text{W/m}^2],
$$

the power density that a receiving antenna intercepts.

---

## 3. Polarization and the wave's orientation

The direction of $\mathbf E$ defines **polarization** — linear, circular, or elliptical. It matters operationally:

- A linearly polarized receive antenna rejects a cross-polarized signal (up to $-20$ dB) — exploited for interference rejection and, adversarially, for polarization-mismatch denial.
- **Circular polarization** (GPS uses RHCP) is robust to vehicle rotation and rejects the opposite-hand multipath reflection.

Polarization is a free design axis for both communication robustness and electronic attack (see [27-autonomy-counter-uas-ew.md](27-autonomy-counter-uas-ew.md)).

---

## 4. Transmission lines and impedance matching

Before the wave radiates, it must travel from transmitter to antenna along a **transmission line** (coax, microstrip). The line obeys the telegrapher's equations and has a **characteristic impedance**

$$
Z_0 = \sqrt{L/C} \quad (\text{50 }\Omega \text{ by convention}).
$$

If the load impedance $Z_L \ne Z_0$, part of the wave reflects. The **reflection coefficient** and **VSWR** quantify the mismatch:

$$
\Gamma = \frac{Z_L - Z_0}{Z_L + Z_0}, \qquad \text{VSWR} = \frac{1 + |\Gamma|}{1 - |\Gamma|}.
$$

Power delivered to the antenna is $(1 - |\Gamma|^2)$ of incident power. A poorly matched antenna reflects energy back, heating the amplifier and shrinking range. **Impedance matching** (the Smith chart is the graphical tool) is half of practical RF engineering. This is exactly the layer where a beautifully designed link silently loses 3 dB.

---

## 5. Antennas — turning currents into radiated fields

An antenna converts guided waves to free-space waves. Two fundamental properties:

### 5.1 Gain and beamwidth

**Directivity** $D$ measures how concentrated the radiated power is versus an isotropic radiator. For an aperture of area $A$:

$$
G = \eta\, D = \eta\,\frac{4\pi A}{\lambda^2},
$$

with aperture efficiency $\eta$. Bigger aperture (in wavelengths) ⇒ higher gain ⇒ narrower beam. Approximate half-power beamwidth $\theta \approx \lambda/D_{\text{ap}}$. This is the fundamental tradeoff: a high-gain dish reaches far but must be *pointed*; an omni antenna covers everything but reaches little.

### 5.2 The Friis transmission equation — the link budget

Received power over a free-space path of range $R$:

$$
\boxed{\;P_r = P_t\, G_t\, G_r\,\left(\frac{\lambda}{4\pi R}\right)^2.\;}
$$

The $(\lambda/4\pi R)^2$ term is **free-space path loss** — power spreads over a sphere, falling as $1/R^2$. In decibels:

$$
P_r[\text{dBm}] = P_t + G_t + G_r - 20\log_{10}\!\frac{4\pi R}{\lambda}.
$$

Every datalink, GPS signal, and radar return obeys Friis. The link closes only if $P_r$ exceeds receiver sensitivity (noise floor + required SNR). A jammer's goal is simply to raise that noise floor — directly the analysis of [26-autonomy-gnss-jamming-spoofing.md](26-autonomy-gnss-jamming-spoofing.md).

### 5.3 Phased arrays

Replace one big dish with $N$ small elements and control their relative phase. The array factor steers the beam *electronically* — no moving parts, microsecond retargeting:

$$
\text{AF}(\theta) = \sum_{n=0}^{N-1} e^{\,j n (kd\sin\theta - \beta)},
$$

peaking when the progressive phase shift $\beta = kd\sin\theta_0$. Array gain scales as $N$; beamwidth narrows as $1/N$. Phased arrays are the heart of modern AESA radar and resilient, beam-nulling anti-jam antennas (CRPA) that place a null on a jammer.

---

## 6. Radar — sensing by your own reflected wave

Radar transmits a pulse and listens for the echo. The two-way path gives the **radar range equation**:

$$
\boxed{\;P_r = \frac{P_t\, G^2\, \lambda^2\, \sigma}{(4\pi)^3 R^4}.\;}
$$

The $1/R^4$ dependence (two-way spreading) is brutal: doubling range cuts return power 16-fold. The detectable range scales as

$$
R_{\max} \propto \left( \frac{P_t G^2 \lambda^2 \sigma}{\text{SNR}_{\min}\, kT B} \right)^{1/4},
$$

so quadrupling transmit power only doubles range. This $1/4$-power law is why low-observable design is so leveraged.

### 6.1 Radar cross section (RCS) and stealth

$\sigma$ (units m²) measures how much power a target scatters *back toward the radar*. Stealth design minimizes $\sigma$ by:

1. **Shaping** — flat, angled facets reflect energy *away* from the source (specular redirection).
2. **Materials** — radar-absorbent material (RAM) converts incident energy to heat.
3. **Edge/traveling-wave control** — managing diffraction off discontinuities.

Because $R_{\max}\propto \sigma^{1/4}$, cutting RCS by 10,000× (40 dB) only halves *and-then-some* detection range — but it shrinks the detection *volume* dramatically and buys reaction time. The physics of scattering (Rayleigh regime $\sigma\propto f^4$ for small targets, optical regime for large) explains why counter-stealth often moves to lower frequency (VHF). This is the field-theory basis for both designing low-RCS UAVs and countering them ([27-autonomy-counter-uas-ew.md](27-autonomy-counter-uas-ew.md)).

### 6.2 Doppler and pulse-Doppler

A moving target shifts the return frequency by $f_d = 2v_r/\lambda$ (two-way Doppler). Pulse-Doppler radar uses this to separate moving targets from stationary clutter — essential for detecting small, slow drones against ground return.

```python
import numpy as np

def radar_max_range(Pt, G, lam, sigma, SNR_min, T=290, B=1e6, F=3):
    """Maximum detection range from the radar range equation (meters)."""
    k = 1.38e-23
    noise = k * T * B * 10 ** (F / 10)        # receiver noise power
    num = Pt * G**2 * lam**2 * sigma
    den = (4 * np.pi) ** 3 * SNR_min * noise
    return (num / den) ** 0.25

# Halving RCS barely changes range — the 4th-root law in action.
for sigma in (1.0, 0.5, 0.1, 0.01):
    R = radar_max_range(1000, 10**3, 0.03, sigma, 10**1.3)
    print(f"RCS {sigma:>5} m^2 -> R_max {R/1000:6.1f} km")
```

---

## 7. Propagation in the real world

Free space is the easy case. Reality adds:

- **Reflection / multipath** — ground and structure bounces cause fading; the two-ray model gives a $1/R^4$ falloff beyond a breakpoint.
- **Diffraction** — waves bend around obstacles (Fresnel zones); longer wavelengths bend more.
- **Atmospheric absorption** — water-vapor and oxygen lines (e.g., 22, 60 GHz) attenuate millimeter waves, shaping which bands are usable.
- **Ionospheric delay** — frequency-dependent ($\propto 1/f^2$); the dominant GPS error source, corrected by dual-frequency receivers.

Each effect is a boundary-value problem on Maxwell's equations, and each shapes where, when, and how a link or radar works. The frequency-dependence of these effects is *why spectrum allocation is strategy*, not just regulation — see [67-engineering-rf-and-spectrum.md](67-engineering-rf-and-spectrum.md).

---

## 8. The contested-spectrum picture

| Phenomenon | Governing relation | Autonomy/defense consequence |
|---|---|---|
| Path loss | Friis $1/R^2$ | link budget, comms range |
| Radar return | range eq. $1/R^4$ | detection range, stealth payoff |
| Jamming | raises $kTB$ noise floor | GNSS/datalink denial |
| Beam steering | array factor | AESA, anti-jam nulling |
| RCS | scattering physics | survivability |
| Ionosphere | $\propto 1/f^2$ delay | GPS accuracy |

Electromagnetics is the single physics that decides whether an autonomous vehicle can *see*, *talk*, and *hide* in a contested environment. The adversarial use of these same equations — jamming, spoofing, low-observability — is where field theory becomes warfare, connecting directly to [26-autonomy-gnss-jamming-spoofing.md](26-autonomy-gnss-jamming-spoofing.md) and [27-autonomy-counter-uas-ew.md](27-autonomy-counter-uas-ew.md).

---

## Sources & further study

- Griffiths, *Introduction to Electrodynamics* (4th ed.) — the gold-standard undergraduate text; Maxwell to waves with clarity.
- Jackson, *Classical Electrodynamics* — the rigorous graduate reference.
- Balanis, *Antenna Theory: Analysis and Design* — the definitive antenna text.
- Pozar, *Microwave Engineering* — transmission lines, impedance matching, the Smith chart.
- Skolnik, *Introduction to Radar Systems* — the classic on radar and the range equation.
- Richards, *Fundamentals of Radar Signal Processing* — pulse-Doppler, detection, clutter.
- Knott, Shaeffer & Tuley, *Radar Cross Section* — the stealth/RCS reference.

> Framing note: Maxwell's four equations are the most leveraged physics an autonomy engineer can own — they govern every sensor, every link, and every form of electronic attack and defense. The Friis equation tells you if you can talk; the radar equation tells you if you can be seen; the array factor tells you where to point your energy. Master the fields, and the contested electromagnetic spectrum stops being a black box and becomes a battlefield you can reason about quantitatively.
