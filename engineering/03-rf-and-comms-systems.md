# RF & Communications Systems — Link Budgets, Antennas & SDR

> **Why this exists.** A drone is only as useful as its ability to send video back and receive commands; a missile is only as guided as its datalink and seeker; a GPS receiver is only as accurate as its ability to pull a signal weaker than the thermal noise floor out of the air. Every one of these is governed by the same unforgiving physics: electromagnetic waves spreading through space, losing power as the square of distance, corrupted by noise, interference, and an adversary who wants to jam you. The engineer who can compute a link budget on a napkin, choose a modulation that survives the channel, and reason about antennas and propagation is the one who decides whether the system works at 1 km or 100 km — and whether it keeps working when someone is trying to break the link.

> **What mastering it makes you.** The person who turns "we need a 50 km secure video link that survives jamming" from a wish into a specification with margins, the engineer trusted with the most failure-prone subsystem in any unmanned or guided platform.

RF is applied [03-foundations-mathematics.md](../foundations/03-mathematics.md): Fourier analysis, complex baseband, and probability are the native language of the channel. The digital back-ends that make modern radios possible are the FPGAs of [02-engineering-fpga-and-hardware-accel.md](02-fpga-and-hardware-accel.md) and the firmware of [01-engineering-embedded-firmware.md](01-embedded-firmware.md). The systems-level tradeoffs — range vs. data rate vs. power vs. probability of intercept — are exactly the kind of first-principles balancing of [01_first_principles_systems_engineering.md](../foundations/01-first_principles_systems_engineering.md). This module connects directly to the electronic-warfare and GNSS material in [07-autonomy-gnss-jamming-spoofing.md](../autonomy/07-gnss-jamming-spoofing.md) and [08-autonomy-counter-uas-ew.md](../autonomy/08-counter-uas-ew.md): a link budget is also a *jam* budget, and the antenna that closes your link is the aperture an adversary exploits.

---

## 1. Maxwell's equations — where all of it comes from

Everything in RF descends from four equations. You will rarely solve them directly, but you must know that they are the source of propagation, antennas, and impedance.

$$ \nabla \cdot \mathbf{E} = \frac{\rho}{\varepsilon_0}, \qquad \nabla \cdot \mathbf{B} = 0 $$
$$ \nabla \times \mathbf{E} = -\frac{\partial \mathbf{B}}{\partial t}, \qquad \nabla \times \mathbf{B} = \mu_0 \mathbf{J} + \mu_0 \varepsilon_0 \frac{\partial \mathbf{E}}{\partial t} $$

In free space with no sources they combine into the wave equation, whose solutions are waves traveling at $c = 1/\sqrt{\mu_0 \varepsilon_0} \approx 3\times10^8$ m/s. The single most-used consequence is the wavelength relation:

$$ \lambda = \frac{c}{f} $$

This number sets antenna size (antennas are fractions of a wavelength), diffraction behavior, and atmospheric interaction. At 2.4 GHz, $\lambda \approx 12.5$ cm — which is why a quarter-wave whip on a drone is ~3 cm. At 100 MHz it's 3 m, which is why VHF antennas are large. Internalize the band map:

| Band | Frequency | λ | Typical use |
|---|---|---|---|
| HF | 3–30 MHz | 100–10 m | Over-horizon, skywave |
| VHF | 30–300 MHz | 10–1 m | Aviation comms, FM |
| UHF | 0.3–3 GHz | 1–0.1 m | Drone C2, GPS (L-band) |
| SHF | 3–30 GHz | 10–1 cm | Radar, SATCOM, datalinks |
| EHF | 30–300 GHz | 10–1 mm | mmWave, imaging |

---

## 2. Decibels — the only sane way to do RF math

RF spans ~20 orders of magnitude in power. Working in decibels turns multiplication into addition, which is why every link budget is in dB.

$$ P_{\text{dB}} = 10 \log_{10}\!\left(\frac{P}{P_{\text{ref}}}\right), \qquad P_{\text{dBm}} = 10 \log_{10}\!\left(\frac{P}{1\text{ mW}}\right) $$

Memorize: +3 dB ≈ ×2, +10 dB = ×10, +20 dB = ×100, −30 dB = ÷1000. A receiver sensitivity of −100 dBm means 0.1 picowatts. The entire art of link design is bookkeeping gains and losses in dB until the number at the receiver clears the noise by enough margin.

---

## 3. The link budget — the master equation

The link budget answers: *will the receiver hear the transmitter well enough?* It is the single most important calculation in this module. Power received follows the **Friis transmission equation**:

$$ P_r = P_t + G_t + G_r - L_{\text{path}} - L_{\text{misc}} \quad [\text{dB form}] $$

where free-space path loss is:

$$ L_{\text{path}} = 20\log_{10}\!\left(\frac{4\pi d}{\lambda}\right) = 20\log_{10}(d) + 20\log_{10}(f) + 32.45 \quad [d \text{ in km}, f \text{ in MHz}] $$

The $20\log_{10}(d)$ term is the brutal truth of RF: **doubling range costs 6 dB**, quadrupling costs 12 dB. Range is expensive.

The link *closes* if the received power, after subtracting noise, leaves enough signal-to-noise ratio for your modulation:

$$ \text{Link margin} = P_r - (N + \text{SNR}_{\text{req}}) \;>\; 0 $$

with the thermal noise floor:

$$ N = kTB = -174\text{ dBm/Hz} + 10\log_{10}(B) + NF $$

Here $k$ is Boltzmann's constant, $T$ the temperature, $B$ the bandwidth, and $NF$ the receiver noise figure. The −174 dBm/Hz is a physical constant you should memorize: it's the thermal noise in 1 Hz at room temperature.

**Worked example — a drone video link.** Transmit 1 W (+30 dBm) at 2.4 GHz, 2 dBi antennas both ends, 20 MHz bandwidth, 6 dB noise figure, QPSK needing ~10 dB SNR, range 5 km:

```
P_t                          +30.0 dBm
G_t                           +2.0 dB
G_r                           +2.0 dB
Path loss (5 km, 2400 MHz)  −114.0 dB   ← 20log(5)+20log(2400)+32.45
─────────────────────────────────────
P_r                          −80.0 dBm

Noise: −174 + 10log(20e6) + 6 = −95 dBm
SNR available = −80 − (−95)  = 15 dB
SNR required (QPSK)          = 10 dB
Link margin                  =  5 dB  ✓ (closes, but thin)
```

A 5 dB margin is marginal — rain, multipath, or pointing error eats it. Real designs target 10–20 dB of margin, which is why you see directional antennas and higher power as range grows.

---

## 4. Modulation — encoding bits onto a carrier

A modulation scheme maps bits onto changes in a sinusoid's amplitude, phase, or frequency. The fundamental tradeoff: higher-order modulations carry more bits per symbol but need more SNR.

A general passband signal in **complex baseband (I/Q)** form:

$$ s(t) = \Re\!\left\{ \big(I(t) + jQ(t)\big)\, e^{j2\pi f_c t} \right\} = I(t)\cos(2\pi f_c t) - Q(t)\sin(2\pi f_c t) $$

The constellation diagram plots symbols in the I/Q plane. Spectral efficiency vs. required SNR:

| Scheme | Bits/symbol | Req. SNR (BER 10⁻⁶) | Robustness |
|---|---|---|---|
| BPSK | 1 | ~10.5 dB | Highest |
| QPSK | 2 | ~13.5 dB | High |
| 16-QAM | 4 | ~20 dB | Medium |
| 64-QAM | 6 | ~26 dB | Low |
| 256-QAM | 8 | ~32 dB | Fragile |

The bit-error probability for coherent BPSK in additive white Gaussian noise is the canonical result:

$$ P_b = Q\!\left(\sqrt{\frac{2E_b}{N_0}}\right) $$

where $E_b/N_0$ is energy per bit over noise density — the normalized SNR that lets you compare schemes fairly. **Adaptive modulation** (used in modern datalinks and Wi-Fi) drops to QPSK when the link is weak and climbs to 256-QAM when it's strong, trading range for rate dynamically.

The ultimate ceiling is **Shannon capacity** — the maximum error-free rate the channel allows:

$$ C = B \log_2(1 + \text{SNR}) \quad [\text{bits/s}] $$

No modulation or code beats this. It tells you immediately whether a requirement (e.g., 50 Mbps over a −80 dBm link) is even physically possible.

---

## 5. Antennas — the transducer between circuit and space

An antenna converts guided waves on a transmission line into radiated waves and vice versa. Two properties dominate design.

**Gain and directivity.** An isotropic radiator spreads power equally in all directions (0 dBi). A directional antenna concentrates power into a beam, trading coverage for range. Gain relates to aperture:

$$ G = \frac{4\pi A_e}{\lambda^2}\eta $$

Bigger aperture (relative to wavelength) and higher efficiency $\eta$ → more gain → narrower beam. The beamwidth of a dish:

$$ \theta_{\text{3dB}} \approx \frac{70\lambda}{D} \quad [\text{degrees}, D = \text{diameter}] $$

**Polarization.** Linear (vertical/horizontal) or circular. Cross-polarization loss is severe (~20 dB), so a vertically polarized transmitter and horizontally polarized receiver barely talk. Circular polarization (RHCP/LHCP) is common on drones and GPS because it tolerates orientation changes — a tumbling vehicle keeps the link.

Common antenna types:

| Antenna | Gain | Pattern | Use |
|---|---|---|---|
| Dipole / monopole | 2–5 dBi | Omni (donut) | Drone telemetry, handhelds |
| Patch | 6–9 dBi | Hemispheric | GPS, ground stations |
| Yagi | 10–15 dBi | Directional | Long-range C2 |
| Helical | 10–15 dBi | Circular pol. | Satellite, drone video |
| Parabolic dish | 20–40 dBi | Pencil beam | SATCOM, radar |
| Phased array | Steerable | Electronically scanned | Modern radar, SATCOM |

**Phased arrays** deserve emphasis: many small elements, each fed with a controlled phase, synthesize and electronically *steer* a beam with no moving parts. By the array factor, $N$ elements give $\sim 10\log_{10}(N)$ dB of gain and a beam you can sweep in microseconds — the technology behind AESA radar and modern SATCOM terminals.

---

## 6. Transmission lines and impedance matching

Between the radio and the antenna sits a transmission line (coax, microstrip), and at RF a wire is not a wire — it has a **characteristic impedance** $Z_0$ (usually 50 Ω). Any impedance mismatch reflects power back, measured by the reflection coefficient and VSWR:

$$ \Gamma = \frac{Z_L - Z_0}{Z_L + Z_0}, \qquad \text{VSWR} = \frac{1 + |\Gamma|}{1 - |\Gamma|} $$

A VSWR of 2:1 reflects ~11% of power; worse mismatches can cook a power amplifier with reflected energy. The telegrapher's equations govern the line:

$$ \frac{\partial V}{\partial x} = -L\frac{\partial I}{\partial t}, \qquad \frac{\partial I}{\partial x} = -C\frac{\partial V}{\partial t}, \qquad Z_0 = \sqrt{\frac{L}{C}} $$

Matching networks (L-networks, stubs, baluns) transform impedances to minimize reflection. The Smith chart is the graphical tool RF engineers use to design these — worth learning to read. This connects to the PCB and transmission-line realities of [01-engineering-embedded-firmware.md](01-embedded-firmware.md) at high speed.

---

## 7. Propagation — what actually happens between antennas

Free-space loss is the optimistic baseline. Reality adds:

- **Multipath fading.** Signals arrive via multiple reflected paths and interfere. Rayleigh/Rician fading can drop the received signal 20–30 dB in a deep fade. OFDM and diversity antennas combat this.
- **Diffraction & terrain.** Beyond line of sight, signals diffract over obstacles (knife-edge diffraction) with extra loss. The **Fresnel zone** — an ellipsoid between antennas that must stay ~60% clear — sets antenna height requirements.
- **Atmospheric absorption.** Oxygen (60 GHz) and water vapor (22, 183 GHz) create absorption peaks; rain attenuates heavily above ~10 GHz (rain fade is the bane of Ku/Ka SATCOM).
- **Earth curvature.** Radio horizon for height $h$ (meters): $d \approx 4.12\sqrt{h}$ km — slightly beyond optical because of refraction.

$$ d_{\text{horizon}} \approx 4.12\left(\sqrt{h_t} + \sqrt{h_r}\right) \quad [\text{km}] $$

This is why drone range is altitude-limited: a vehicle at 100 m and a ground station at 10 m have a ~54 km radio horizon, and no power closes the link beyond it without a relay or over-horizon technique.

---

## 8. Spread spectrum and anti-jam

For contested environments, raw modulation isn't enough. **Spread spectrum** spreads the signal over far more bandwidth than the data needs, buying processing gain against jamming and low probability of intercept.

$$ G_p = \frac{B_{\text{spread}}}{B_{\text{data}}} = 10\log_{10}\!\left(\frac{R_c}{R_b}\right) \quad [\text{dB}] $$

Two families:

- **DSSS (Direct Sequence).** Multiply data by a fast pseudorandom code; the receiver de-spreads, collapsing the signal back to a narrow band while spreading any narrowband jammer. GPS uses this — the C/A code gives ~43 dB of processing gain, which is how you receive a signal below the noise floor.
- **FHSS (Frequency Hopping).** Hop the carrier across many channels on a secret schedule; a jammer that can't follow the hop wastes power on empty channels. Bluetooth and many military datalinks (e.g., Link-16/SINCGARS lineage) use this.

This is the direct bridge to [07-autonomy-gnss-jamming-spoofing.md](../autonomy/07-gnss-jamming-spoofing.md): a jammer's job is to overcome your processing gain with raw power; the **jam-to-signal ratio** the receiver tolerates is the design battleground.

---

## 9. MIMO and spatial multiplexing

Multiple-Input Multiple-Output uses several antennas at each end to either (a) gain diversity against fading or (b) send parallel data streams over the same frequency, multiplying capacity. The channel becomes a matrix $\mathbf{H}$:

$$ \mathbf{y} = \mathbf{H}\mathbf{x} + \mathbf{n} $$

With $N_t$ transmit and $N_r$ receive antennas in rich multipath, capacity scales with $\min(N_t, N_r)$:

$$ C = \sum_{i=1}^{\min(N_t,N_r)} B\log_2(1 + \text{SNR}\cdot\sigma_i^2) $$

where $\sigma_i$ are the singular values of $\mathbf{H}$. This is why Wi-Fi, 5G, and modern tactical radios stack antennas. **Beamforming** (a MIMO mode) steers energy toward the receiver and nulls toward jammers — a software-defined directional antenna.

---

## 10. Software-Defined Radio — the modern architecture

SDR moves the radio's intelligence from fixed analog circuits into reconfigurable digital processing. The antenna feeds a wideband front-end (LNA, mixer, filter), an ADC digitizes a chunk of spectrum, and **everything after that — demodulation, filtering, decoding — is software/FPGA.**

```
Antenna ─► LNA ─► Mixer ─► Filter ─► ADC ─► [ FPGA/CPU: DDC, demod, decode ]
                    ▲                              SDR = where DSP meets the air
                    │
                    LO (tunable)
```

The key enabler is **direct/IF sampling** and the **digital down-converter (DDC)**: shift the band of interest to baseband digitally and decimate. Nyquist sets the floor — sample at least twice the bandwidth:

$$ f_s \ge 2B $$

SDR platforms (USRP/Ettus, BladeRF, HackRF, RFSoC) plus GNU Radio let you build a working receiver or transmitter in a flowgraph in an afternoon, then push the heavy lifting into an FPGA for real-time performance — the exact PS/PL split of [02-engineering-fpga-and-hardware-accel.md](02-fpga-and-hardware-accel.md). SDR is also the universal tool for EW, signals intelligence, and GPS research: one box, reprogrammable to any waveform.

---

## 11. Putting it together — designing a real datalink

The end-to-end design process for, say, a 30 km secure drone C2 + video link:

1. **Pick a band.** Trade λ (antenna size, diffraction) against available spectrum and regulations. UHF for robust C2, SHF for high-rate video.
2. **Set the link budget.** Choose power, antenna gains, and bandwidth so margin ≥ 10 dB at max range, accounting for the radio horizon.
3. **Choose modulation + coding.** QPSK + LDPC/Turbo FEC for the C2 (robust, low rate); adaptive QAM for video. Forward error correction buys several dB of coding gain — effectively free margin.
4. **Add anti-jam.** Frequency hopping or DSSS sized to the expected jammer.
5. **Design antennas.** Directional on the ground (tracking), omni or steerable on the air vehicle.
6. **Verify with SDR** before committing to fixed hardware — capture real channel data, test the waveform.
7. **Budget for the adversary.** Every gain you add (higher power, bigger antenna) also raises your probability of intercept. Low probability of intercept/detection (LPI/LPD) is a first-class requirement in defense links.

---

## 12. Tooling and ecosystem

| Need | Tools |
|---|---|
| Link/system modeling | MATLAB, Python (NumPy/SciPy), Octave |
| SDR frameworks | GNU Radio, SoapySDR, REDHAWK |
| SDR hardware | Ettus USRP, BladeRF, HackRF, LimeSDR, RFSoC |
| Antenna/EM sim | ANSYS HFSS, CST, NEC, openEMS |
| RF circuit design | Keysight ADS, Qucs, Smith chart tools |
| Spectrum analysis | Spectrum analyzer, VNA (for VSWR/S-params) |
| Channel/protocol | GNU Radio, srsRAN, OpenAirInterface |

---

## Sources & further study

- John G. Proakis & Masoud Salehi, *Digital Communications* — the standard graduate text on modulation and detection.
- Constantine Balanis, *Antenna Theory: Analysis and Design* — the antenna bible.
- David Pozar, *Microwave Engineering* — transmission lines, matching, S-parameters.
- Bernard Sklar, *Digital Communications: Fundamentals and Applications* — exceptionally clear link-budget and coding treatment.
- Andrea Goldsmith, *Wireless Communications* — fading, MIMO, capacity.
- Theodore Rappaport, *Wireless Communications: Principles and Practice* — propagation models.
- Horowitz & Hill, *The Art of Electronics* — the analog front-end reality.
- Eric Tester / GNU Radio tutorials and the USRP documentation — hands-on SDR.

> Framing note: RF is the discipline where you negotiate with physics for every decibel. Free space takes 6 dB per range doubling and gives nothing back; noise is a hard floor set by temperature; and an adversary is adding power to your noise on purpose. The engineer who can hold the whole link budget in their head — and find the 10 dB of margin that makes a system robust instead of a demo — owns the most fragile and most strategic subsystem on the platform.
