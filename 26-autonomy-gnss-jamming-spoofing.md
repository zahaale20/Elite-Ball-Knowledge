# GNSS, Jamming & Spoofing — Navigating When the Sky Lies

> A standalone deep-dive that the GPS-denied navigation work in
> [28-autonomy-gnc.md](28-autonomy-gnc.md) and [20-autonomy-ml-ai.md](20-autonomy-ml-ai.md)
> assumes. In modern conflict, **GNSS is the first thing the adversary takes
> away.** An autonomy stack that only works with a clean GPS fix is a toy.

Ukraine, the Eastern Mediterranean, and the Baltic have made one thing clear:
GNSS denial is no longer exotic. It is the **default contested condition**.
Building navigation that degrades gracefully — rather than failing — is one of
the most valuable skills in defense autonomy.

---

## 1. How GNSS Actually Works (So You Know How It Breaks)

GNSS (the umbrella term; GPS is the U.S. constellation, alongside Galileo, GLONASS,
BeiDou) works by **trilateration from time-of-flight**:

- Each satellite broadcasts its position and a precise timestamp.
- Your receiver measures the tiny delay to each satellite → distance (pseudorange).
- With ≥4 satellites you solve for 3D position **and** clock bias.
- The signals are **astonishingly weak** — roughly -160 dBW at the antenna,
  *below the thermal noise floor*. This is the core vulnerability: a transmitter
  millions of times closer than a satellite trivially overwhelms it.

That weakness is the whole story. Everything below follows from it.

---

## 2. Jamming — Denial by Noise

**Jamming = drowning the real signal in noise/interference** so the receiver
can't lock.

- **Mechanism:** a transmitter on the GNSS frequency (L1 ≈ 1575.42 MHz, L2, L5)
  raises the noise floor; the receiver loses tracking and reports "no fix."
- **Cheap and effective:** a few-watt jammer denies GNSS over kilometers. Illegal
  "personal privacy devices" already cause real-world airport disruptions.
- **Signature:** sudden loss of *all* satellites at once, abnormally high
  carrier-to-noise (C/N₀) degradation, fix dropout correlated with position.
- **Detection:** monitor C/N₀ and **AGC (automatic gain control)** — a jammer
  drives AGC to extremes even before the fix drops. AGC anomaly is an early
  warning the autopilot can act on.
- **The honest reality:** you usually can't *defeat* jamming from the air — you
  **survive** it by not depending on GNSS in the first place (§5).

---

## 3. Spoofing — Denial by Deception (The Dangerous One)

**Spoofing = transmitting *counterfeit* GNSS signals** so the receiver computes a
**false but confident** position. Far more dangerous than jamming because the
system thinks it's fine.

- **Mechanism:** the spoofer broadcasts fake satellite signals, first matching
  the true position (to capture the receiver's tracking loops), then slowly
  "walking" the solution away. The drone flies confidently to the wrong place.
- **Famous cases:** the 2011 RQ-170 capture (alleged), the 2013 University of
  Texas yacht spoof (Humphreys et al.), and mass "circle spoofing" around
  sensitive sites where receivers worldwide suddenly report being at an airport.
- **Why it's worse:** a jammed vehicle *knows* it's lost. A spoofed vehicle is
  lied to and acts on the lie — flying into a no-fly zone, returning to a false
  "home," or triggering geofence behavior the adversary controls.
- **Civil-GPS is unauthenticated** by design, which is exactly why spoofing the
  open L1 C/A signal is feasible.

---

## 4. Defenses That Actually Exist

No single fix; defense is layered.

- **Antenna-side (hardware):**
  - **CRPA (Controlled Reception Pattern Antenna)** — multi-element antennas that
    null out interference from the jammer's direction. The gold standard, but
    expensive and bulky.
  - **Choke-ring / null-steering** antennas reject low-elevation (ground-based)
    spoofers.
- **Receiver-side (signal processing):**
  - **RAIM (Receiver Autonomous Integrity Monitoring)** — cross-checks redundant
    satellites for consistency; flags an outlier.
  - **AGC / C/N₀ / clock-bias monitoring** — detect the statistical fingerprints
    of jamming and spoofing.
  - **Angle-of-arrival checks** — real satellites come from the sky; a spoofer
    usually comes from one ground direction.
- **Cryptographic:**
  - **Galileo OSNMA** (Open Service Navigation Message Authentication) — signs the
    navigation message so spoofed data fails verification. A real, deployed step
    forward for civil users.
  - Military **M-code** (encrypted, authenticated, higher power) for cleared
    platforms.
- **System-side:** sensor fusion that *distrusts* GNSS and can reject it (§5).

---

## 5. The Real Answer — Don't Depend on GNSS

The mature defense isn't a better receiver; it's an autonomy stack that treats
GNSS as **one untrusted sensor among many** and navigates without it.

- **Inertial Navigation (INS/IMU):** dead-reckon from accelerometers + gyros.
  Drifts over time (the whole problem), but bridges short outages perfectly.
  Tactical-grade IMUs drift slowly; MEMS drift fast — fusion is essential.
- **Visual-Inertial Odometry (VIO):** fuse camera + IMU to estimate motion with
  no external signal. The backbone of GPS-denied flight. (See VINS-Mono,
  ORB-SLAM in [20-autonomy-ml-ai.md](20-autonomy-ml-ai.md).)
- **Visual / Terrain-Relative Navigation:** match the live camera view to
  reference imagery or a terrain map to *absolutely* localize without GNSS — the
  modern revival of TERCOM/DSMAC cruise-missile guidance.
- **Optical flow + rangefinder:** cheap velocity hold for low-altitude flight.
- **Map-matching & feature landmarks:** localize against known structures.
- **Multi-sensor fusion (EKF):** the estimator that weights all of the above and
  **down-weights or rejects GNSS** when integrity checks fail. This is the
  payoff of [28-autonomy-gnc.md](28-autonomy-gnc.md) — the filter is your immune
  system against a lying sky.

**Design principle:** every autonomy mode should have a defined behavior for
"GNSS just became untrustworthy mid-flight." If the answer is "crash" or "fly to
a spoofed home," the design is incomplete.

---

## 6. What to Build & Test in Your Stack

- Add a **GNSS-integrity monitor**: watch C/N₀, AGC, satellite count, and EKF
  innovation on the GPS measurement; declare "GPS untrusted" on anomaly.
- Make the EKF able to **drop GPS and hold on VIO/INS** — and test the handoff in
  SITL by killing the simulated GPS mid-mission ([22-autonomy-px4-sitl.md](22-autonomy-px4-sitl.md)).
- Define a **fallback policy** in your decision layer
  ([29-autonomy-planning-decision.md](29-autonomy-planning-decision.md)):
  loiter on inertial, switch to VIO, return via terrain-relative nav, or
  controlled descend — never "fly confidently on a possibly-spoofed fix."
- Log AGC/C/N₀ so you can recognize the signature later.

---

## Sources & Citations

**Foundational / academic**
- Humphreys, T. et al. — *Assessing the Spoofing Threat: Development of a
  Portable GPS Civilian Spoofer* (ION GNSS 2008) — the canonical spoofing paper.
- Psiaki, M. & Humphreys, T. — *GNSS Spoofing and Detection* (Proceedings of the
  IEEE, 2016).
- Kaplan, E. & Hegarty, C. — *Understanding GPS/GNSS: Principles and
  Applications*, Artech House (the standard reference).
- Groves, P. — *Principles of GNSS, Inertial, and Multisensor Integrated
  Navigation Systems*, Artech House.

**Official / standards**
- U.S. GPS program & signal specs: https://www.gps.gov
- European GNSS (Galileo) & OSNMA: https://www.gsc-europa.eu
- FAA / RAIM and WAAS integrity: https://www.faa.gov/about/office_org/headquarters_offices/ato/service_units/techops/navservices/gnss/
- DHS/CISA — Resilient PNT (Positioning, Navigation, Timing) guidance:
  https://www.cisa.gov/resources-tools/resources/resilient-positioning-navigation-and-timing-pnt
- PX4 EKF2 / GPS-denied & vision fusion: https://docs.px4.io

**Open-source navigation**
- VINS-Mono: https://github.com/HKUST-Aerial-Robotics/VINS-Mono
- ORB-SLAM3: https://github.com/UZ-SLAMLab/ORB_SLAM3
- PX4 ECL/EKF2: https://github.com/PX4/PX4-ECL

> ⚠️ **Scope note:** This file is about **defensive navigation resilience** —
> detecting denial and continuing to navigate. It deliberately does not describe
> how to build or operate jamming/spoofing equipment, which is illegal in most
> jurisdictions and out of scope. Use a licensed lab/anechoic setup and follow
> spectrum regulations (FCC Part 15 / national equivalents) for any RF testing.

*Threat cases are drawn from published academic and press accounts; specifics of
ongoing conflicts evolve. Treat detection signatures as durable principles and
verify against current literature.*
