# GNSS, Jamming & Spoofing — Navigating When the Sky Lies

> A standalone deep-dive that the GPS-denied navigation work in
> [09-autonomy-gnc.md](09-gnc.md) and [01-autonomy-ml-ai.md](01-ml-ai.md)
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
  ORB-SLAM in [01-autonomy-ml-ai.md](01-ml-ai.md).)
- **Visual / Terrain-Relative Navigation:** match the live camera view to
  reference imagery or a terrain map to *absolutely* localize without GNSS — the
  modern revival of TERCOM/DSMAC cruise-missile guidance.
- **Optical flow + rangefinder:** cheap velocity hold for low-altitude flight.
- **Map-matching & feature landmarks:** localize against known structures.
- **Multi-sensor fusion (EKF):** the estimator that weights all of the above and
  **down-weights or rejects GNSS** when integrity checks fail. This is the
  payoff of [09-autonomy-gnc.md](09-gnc.md) — the filter is your immune
  system against a lying sky.

**Design principle:** every autonomy mode should have a defined behavior for
"GNSS just became untrustworthy mid-flight." If the answer is "crash" or "fly to
a spoofed home," the design is incomplete.

---

## 6. What to Build & Test in Your Stack

- Add a **GNSS-integrity monitor**: watch C/N₀, AGC, satellite count, and EKF
  innovation on the GPS measurement; declare "GPS untrusted" on anomaly.
- Make the EKF able to **drop GPS and hold on VIO/INS** — and test the handoff in
  SITL by killing the simulated GPS mid-mission ([03-autonomy-px4-sitl.md](03-px4-sitl.md)).
- Define a **fallback policy** in your decision layer
  ([10-autonomy-planning-decision.md](10-planning-decision.md)):
  loiter on inertial, switch to VIO, return via terrain-relative nav, or
  controlled descend — never "fly confidently on a possibly-spoofed fix."
- Log AGC/C/N₀ so you can recognize the signature later.

---

## 7. GNSS Signal Structure in Depth (So You Know Exactly What Breaks)

§1 gave the trilateration sketch. To reason about jamming, spoofing, and
detection, you need the *signal*. Three properties matter: it's weak, it's
spread-spectrum, and (for civil signals) it's unauthenticated.

**Frequencies (L-band).** Each constellation broadcasts on multiple carriers:

| Band | GPS freq | Carries |
|---|---|---|
| L1 | 1575.42 MHz | C/A code (civil), P(Y) & M-code (military) |
| L2 | 1227.60 MHz | P(Y), L2C (civil) |
| L5 | 1176.45 MHz | Safety-of-life civil signal, higher power |

Galileo (E1/E5/E6), GLONASS (FDMA around L1/L2), and BeiDou overlap this band.
**Multi-frequency, multi-constellation is itself a defense** — an adversary must
deny *all* of it, not one carrier (§10).

**Spread spectrum / CDMA.** Each satellite multiplies its 50 bps navigation data
by a unique high-rate pseudorandom **PRN code** (Gold codes for GPS). The C/A
code runs at **1.023 Mchips/s, repeating every 1 ms**; the military P(Y) code runs
10× faster (10.23 Mcps) and is encrypted. Because every satellite uses a different
near-orthogonal code on the same frequency, your receiver separates them by
**correlation** — sliding a local replica of each PRN until it locks.

**Processing gain — the only reason a sub-noise signal is usable.** The despreading
correlation collapses the wideband signal back to the narrowband data while
spreading any *non-matching* interference. The gain is roughly the ratio of code
rate to data rate:

```
processing gain ≈ 10·log10(1.023e6 / 50) ≈ 43 dB  (C/A)
```

That ~43 dB is what lifts a **−160 dBW** signal (well below the −approx −131 dBm
thermal floor) into a usable lock. **It is also your jam-resistance budget:** an
interferer must overcome both the path-loss advantage it enjoys *and* this
processing gain to break lock. P(Y)/M-code's faster chip rate buys ~10 dB more
(§10, military anti-jam).

**Code phase vs. carrier phase.** The receiver tracks two things: the **code phase**
(coarse range, the pseudorange) and the **carrier phase** (millimeter-precision,
used for RTK/PPK). Doppler shift from satellite motion (±~5 kHz) must be tracked
too. Spoofers attack the tracking *loops* that maintain these (§9).

---

## 8. Jamming Taxonomy & Link Budget

"Jamming" is not one thing. The type determines both effectiveness and the
detection signature your monitor should look for.

| Type | What it does | Notes |
|---|---|---|
| **Barrage / broadband** | Floods a wide band with noise | Brute force; needs high power; easy to detect |
| **Spot / CW (single tone)** | One frequency, max power density | Efficient if tuned to L1; narrow |
| **Swept / chirp** | Sweeps a tone across the band rapidly | **The cheap commercial jammer** — "personal privacy devices"; very effective |
| **Pulsed** | On/off bursts | Lower average power, evades some detectors, degrades tracking |
| **Matched / protocol-aware** | Mimics signal structure to defeat processing gain | Sophisticated, more efficient per watt |

**The link-budget reality (why jamming is easy).** A satellite is ~20,000 km away;
a ground jammer might be 5 km away. Free-space loss scales with distance squared,
so the jammer enjoys an enormous geometric advantage *before* it even turns up
power. What stands against it is only the **processing gain** (§7) and any
**spatial nulling** (§10). The governing quantity is the **jamming-to-signal ratio
(J/S)**: once `J/S` exceeds the receiver's tolerance (roughly processing gain plus
margin, ~40–45 dB for C/A), tracking collapses.

- **Burn-through range** — as the vehicle flies *away* from a jammer, `J/S` falls
  with distance²; beyond some range the real signal wins again. Useful for mission
  planning: know the jammer, estimate the denied bubble.
- **Honest takeaway (unchanged from §2):** from the air you rarely *defeat* a
  jammer — you **survive** it by not depending on GNSS (§5, §11).

**Detection signatures by type** feed your integrity monitor: barrage drives AGC
hard and crushes *all* C/N₀ together; chirp shows periodic AGC modulation; pulsed
shows intermittent C/N₀ dropouts. AGC moving *before* the fix drops is your
earliest warning.

---

## 9. Spoofing Taxonomy & Capture Mechanics

Spoofing ranges from trivial to nation-state. The ladder matters because each rung
defeats different detectors.

| Sophistication | Method | Beats |
|---|---|---|
| **Meaconing** | Record real signals, rebroadcast with delay | Cheapest; introduces a detectable common delay/AoA |
| **Simplistic** | Generate fake signals, not synchronized to the real ones | Naive receivers; a sharp C/N₀/clock jump on capture |
| **Intermediate (synchronized)** | Match true position & timing, then *slowly* drag the solution (Humphreys-style) | Most receivers; the dangerous practical threat |
| **Sophisticated** | Multi-antenna, phase-aligned, nulls the real signal | AoA and many SQM checks |

**Capture mechanics (how the lie is installed).** A competent spoofer doesn't just
shout. It:

1. Transmits counterfeit PRNs **aligned** to the true signals the receiver is
   already tracking, at slightly higher power.
2. The tracking loops, locked to the strongest correlation peak, **drag onto the
   spoofer's peak** ("lift-off") without ever losing lock — no alarm fires.
3. The spoofer then **walks** code phase / pseudoranges away gradually, steering
   the computed position or time wherever it wants. The vehicle flies confidently
   to the wrong place.

**Two attack goals, both bad:**

- **Position spoofing** — the obvious one: false location → flies into a no-fly
  zone, returns to a fake "home," triggers adversary-chosen geofence behavior.
- **Time spoofing** — often *more* damaging at scale: GNSS is the world's clock.
  Walking the receiver's time desynchronizes power-grid PMUs, telecom, and finance
  timestamps. For your vehicle it corrupts every time-tagged measurement the EKF
  fuses.

**Why civil GPS is spoofable at all:** the open L1 C/A signal is **unauthenticated**
by design — anyone can generate a structurally valid signal. Authentication
(Galileo OSNMA, military M-code) is the cryptographic answer (§4, §10).

---

## 10. Detection & Integrity in Depth (Defense in Layers)

No single check is sufficient; integrity comes from stacking independent ones so an
attacker must defeat *all* simultaneously.

- **AGC monitoring.** The receiver's automatic gain control reacts to total RF
  power. A jammer (or strong spoofer) drives AGC to an extreme **before** the fix
  is lost — the cheapest, earliest tripwire. Log it (§6).
- **C/N₀ statistics.** Carrier-to-noise per satellite. Spoofers often produce
  *abnormally uniform* or unusually high C/N₀ across satellites (real ones vary by
  elevation). Sudden collapse across all SVs = jamming.
- **RAIM / FDE.** With **more than 4** satellites the position solution is
  over-determined; **Receiver Autonomous Integrity Monitoring** forms the
  measurement residuals, runs a chi-square consistency test, and **detects** (and
  with enough redundancy **excludes**) a faulty/spoofed satellite. **ARAIM** extends
  this across constellations with published integrity parameters.
- **Clock-bias monitoring.** The receiver clock solution should evolve smoothly; a
  spoof that walks time produces an anomalous clock-bias jump or drift.
- **Multi-constellation / multi-frequency cross-check.** Spoofing all of GPS +
  Galileo + GLONASS + BeiDou across L1/L5 coherently is far harder than spoofing
  L1 C/A. Disagreement between independent sources flags the attack.
- **Angle-of-arrival / CRPA.** Real satellites arrive from many sky directions; a
  single ground spoofer arrives from **one** direction. Multi-element antennas
  (CRPA, §4) measure AoA and can **null** the offending direction.
- **Signal-quality monitoring (SQM).** During the lift-off (§9), the correlation
  peak is briefly **distorted/doubled** as the spoofer drags the receiver off the
  true peak. Monitoring correlator-tap symmetry catches this transient.
- **Consistency with non-GNSS sensors (your strongest layer).** Compare the GNSS
  position/velocity against the **INS/VIO** dead-reckon. A spoof that disagrees with
  what your accelerometers and camera *physically felt* produces a large **EKF
  innovation** — and the filter can reject it. This is where detection meets §11.

| Layer | Catches | Cost |
|---|---|---|
| AGC | Jamming (early), strong spoof | ~free |
| C/N₀ | Jamming, crude spoof | ~free |
| RAIM/ARAIM | Single-SV spoof/fault | software |
| Clock-bias | Time spoof | software |
| Multi-const/freq | Most practical spoofers | better receiver |
| AoA/CRPA | Ground spoofers, jammers | hardware $$ |
| OSNMA/M-code | Forged nav data | crypto / clearance |
| **INS/VIO consistency** | **Any spoof that defies physics** | **your stack (§11)** |

---

## 11. The GPS-Denied Pipeline in Your Stack (Repo-Anchored)

This is the payoff. Your `pixhawk/drone/` autonomy stack treats GNSS as **one
untrusted sensor** and keeps flying without it. The pipeline:

```
 cameras ──► Visual Odometry ──► relative motion (drift-bounded short-term)
    │                                   │
    └──► Map-Matching ──► absolute fix against cached reference imagery/terrain
                                        │
 IMU ──────────────────────────────────┼──► EKF2 (external vision fusion, EV)
 GNSS (gated) ──► integrity monitor ────┘        │
                                                 ▼
                                   fused state  ──► control loops (25), policy (29)
```

How the pieces wire into PX4/EKF2:

- **Visual odometry** supplies relative pose; **map-matching** against pre-cached
  reference imagery/terrain supplies the **absolute** correction that bounds VO
  drift — the modern revival of TERCOM/DSMAC (§5).
- These enter EKF2 as **external vision** via `vehicle_visual_odometry` /
  `vehicle_visual_odometry` and the EV aiding path. Key parameters to know cold:
  - `EKF2_GPS_CTRL` — which GPS aiding is enabled (you toggle this *down* under
    denial).
  - `EKF2_EV_CTRL` — enable external-vision position/velocity/yaw fusion.
  - `EKF2_HGT_REF` — primary height source (don't let a spoofed GPS own altitude).
  - `EKF2_EV_DELAY` — **time-offset compensation** so the (latent) vision estimate
    is fused at the correct timestamp; getting this wrong injects the very lag that
    eats control margin ([06-autonomy-control-theory.md](06-control-theory.md) §14).
- **Frame alignment.** EV is in its own frame; it must be rotated/aligned into
  EKF2's NED (and yaw-aligned) before fusion, or the filter fights itself.

**The integrity state machine (your immune response):**

```
GPS_GOOD ──[AGC/C/N₀/RAIM/innovation anomaly]──► GPS_SUSPECT
GPS_SUSPECT ──[anomaly persists]──► GPS_DENIED  (EKF2_GPS_CTRL → off)
GPS_DENIED ──[hold on VIO+INS, map-match for absolute]──► continue mission
GPS_DENIED ──[clean signal returns & passes re-validation]──► GPS_GOOD
```

The transition from `GPS_SUSPECT` to trusting vision must be **constitution-gated**
in your `policy/` layer ([10-autonomy-planning-decision.md](10-planning-decision.md))
— the switch that abandons GPS is safety-critical and must be auditable
([09-foundations-safety-assurance.md](../foundations/09-safety-assurance.md)). The
filter math that makes the handoff smooth is the observability story from
[09-autonomy-gnc.md](09-gnc.md); the linear-algebra footing is in
[03-foundations-mathematics.md](../foundations/03-mathematics.md).

---

## 12. Operating in Contested Environments — CONOPS

Resilient navigation is a *concept of operations*, not just a sensor. Think in a
**PNT hierarchy** — most-trusted to least — and design the mission to slide down it
gracefully:

```
RTK GPS  >  multi-const GPS  >  GPS + INS  >  VIO + map-match + INS  >  INS-only  >  controlled descent
   (cm)         (m)              (drift-bridged)   (GPS-denied nav)      (dead-reckon)    (last resort)
```

- **Pre-mission.** Survey and **cache map/terrain tiles** for the area of
  operations so map-matching has reference imagery offline. Estimate jammer bubbles
  (§8 burn-through) and plan legs that stay on terrain-relative features.
- **In mission.** Practice **EMCON** (emission control, see
  [08-autonomy-counter-uas-ew.md](08-counter-uas-ew.md)) — an RF-silent,
  GNSS-independent vehicle is far harder to detect *and* far harder to deny. Plan
  routes with terrain masking and known visual landmarks.
- **Degraded-mode ladder.** Every autonomy mode needs a defined answer to "GNSS
  just became untrustworthy": loiter on inertial → switch to VIO/map-match →
  return via terrain-relative nav → controlled descend. **Never** "fly confidently
  on a possibly-spoofed fix."
- **After-action.** Log AGC/C/N₀/innovation/state-machine transitions so you can
  reconstruct *when* denial began and validate the handoff — closing the
  sim → log → metal loop the same way you tune control.

This connects directly to the broader contested-spectrum picture and the
electronic-protection mindset in
[08-autonomy-counter-uas-ew.md](08-counter-uas-ew.md), and is a core
milestone on the [02-ten-year-mastery-plan.md](../foundations/02-ten-year-mastery-plan.md).

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

---

## ⚡ The Insider Layer — What the Field Knows but Rarely Writes Down

### AGC and C/N₀ are your cheapest, most honest jam detectors

Before the fix even drops, the receiver's **automatic gain control** swings to fight rising interference — so an AGC anomaly is an *earlier* warning than loss-of-fix. Pair it with per-satellite carrier-to-noise: normal C/N₀ sits around 35–50 dB-Hz; a uniform collapse across *all* satellites signals jamming, while selective oddities hint at spoofing. Many u-blox-class receivers expose both over their protocol. Logging and threshold-alarming these is the single highest-value, fully *legal* defensive thing you can build, and most amateur stacks simply don't.

### Spoofing detection is mostly consistency-checking, not cryptography

Civilian GPS is unauthenticated, so you detect spoofing by *contradiction*, not by decoding a signature. GPS says you teleported but the IMU, baro, and visual odometry disagree. C/N₀ is suspiciously high and uniform. All satellites suddenly share one apparent direction-of-arrival. The clock-bias estimate jumps. RAIM (receiver autonomous integrity monitoring) is the classical formalization. The robust architecture never "trusts GPS less" by a knob — it fuses GPS as *one* noisy sensor an EKF can reject as an outlier when the others outvote it.

### The honest truth: you cannot beat jamming from the air

A few-watt ground jammer outguns a satellite by orders of magnitude at your antenna — GNSS arrives near $-160$ dBW, below the thermal noise floor, and the jammer is millions of times closer. No airborne receiver "burns through" that. Every fieldable answer is about **graceful degradation**: detect denial early, fall back to inertial plus visual/terrain navigation, and execute a *coded* behavior (loiter, dead-reckon home, land) rather than reaching for a magic anti-jam box. Designing for "GPS is gone" as the *default* condition is the actual skill the market pays for.

### Antenna and placement beat exotic processing on a budget

A good RHCP antenna with a real ground plane, mounted with a clear sky view and kept away from the RF hash of the Pi and ESCs, buys more jam and multipath resistance than most software. **CRPA** — controlled-reception-pattern, null-steering antenna arrays — genuinely defeat jamming by spatially nulling the threat direction, but they are heavier, costlier, and the genuinely capable military variants are **export-controlled (ITAR/EAR)**. *That specific performance envelope is restricted; the public-domain understanding is simply that a phased-array antenna can place a spatial null on an interferer.*

### Inertial coasting has a half-life — know yours

When GPS drops you're on the IMU's clock. A consumer MEMS IMU drifts position on the order of meters within seconds to tens of seconds; tactical- and navigation-grade units do far better and are themselves largely export-controlled. The number that matters operationally isn't the Allan-variance plot — it's *how long can I dead-reckon inside my error budget before I must re-acquire or land?* Compute that time, then fly to it as a hard limit, not a hope.

### Most of what "works" in conflict zones stays unpublished

The genuinely effective, current counter-spoofing and anti-jam techniques used operationally are largely classified or vendor-proprietary, and detail evolves with each conflict. Treat published academic signatures (AGC, C/N₀, RAIM, multi-sensor consistency) as the durable, legal, open core — and don't infer restricted specifics from them.
