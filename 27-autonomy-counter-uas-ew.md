# Counter-UAS & Electronic Warfare — A Defender's Primer

> Context for why autonomy is built the way it is. The threats in
> [26-autonomy-gnss-jamming-spoofing.md](26-autonomy-gnss-jamming-spoofing.md)
> are one slice of a larger discipline: **electronic warfare (EW)** and the
> systems built to **detect, track, and defeat drones (Counter-UAS / C-UAS).**

If you want to build autonomy that survives contact with a real adversary, you
have to understand the people whose job is to stop it. This file is the
**defender's-eye view** — written so you design resilient systems, not so you
build weapons. It stays at the openly-published, conceptual level.

---

## 1. The Electromagnetic Spectrum Is a Battlespace

Every drone is a node radiating and receiving energy: GNSS reception, command-
and-control (C2) radio, video downlink, telemetry. EW is the fight over that
spectrum, traditionally split into three:

- **Electronic Support (ES)** — *listening*: detect, intercept, and direction-
  find emissions. (Where is that drone's controller transmitting from?)
- **Electronic Attack (EA)** — *denying*: jamming, spoofing, directed energy.
- **Electronic Protection (EP)** — *surviving*: frequency hopping, encryption,
  spread spectrum, low-probability-of-intercept (LPI) waveforms, emission control.

For an autonomy engineer, **EP is your discipline.** Every design choice that
reduces dependence on a single exploitable link is electronic protection.

---

## 2. The C-UAS Kill Chain

Counter-UAS systems follow a sense → decide → defeat pipeline. Understanding each
stage tells you what makes a drone hard to counter.

1. **Detect** — something is out there.
2. **Track** — keep continuous custody of it.
3. **Identify / classify** — friend, foe, bird, or hobbyist? (The hardest and
   most legally fraught step.)
4. **Decide** — rules of engagement; is action authorized?
5. **Defeat** — neutralize it.

A drone is "survivable" to the degree it's hard at **every** stage, not just one.

---

## 3. Detection & Tracking Modalities

C-UAS sensors are multi-modal because no single sensor is enough:

- **Radar** — detects motion/range; struggles with small, slow, low-flying
  drones against ground clutter (the "low-slow-small" problem). Specialized
  drone radars use micro-Doppler (the spectral signature of spinning props).
- **RF detection** — passively detects and direction-finds the drone's C2/video
  emissions. Defeated by autonomy: **a drone with no radio link emits nothing to
  find.** This is a core reason onboard autonomy matters militarily.
- **EO/IR (cameras)** — visual/thermal detection and classification; range- and
  weather-limited; increasingly ML-driven.
- **Acoustic** — microphone arrays detect prop noise; short range, good for cued
  alerting in cluttered environments.
- **Fusion** — modern systems fuse all of the above to cut false alarms (birds,
  aircraft) and maintain track.

**Design takeaway:** the harder a system is to detect (RF-silent autonomy, low
visual/thermal/acoustic signature, terrain masking), the further left in the kill
chain it defeats the defender.

---

## 4. Defeat Mechanisms (Conceptual)

Broadly, "soft kill" (electronic) and "hard kill" (kinetic):

- **RF jamming** — sever the C2/video link or deny GNSS, forcing the drone to
  fail-safe (hover, return, land). **Useless against a fully autonomous,
  RF-silent, GNSS-independent vehicle** — which is exactly why those properties
  are valuable.
- **GNSS denial/spoofing** — covered in
  [26-autonomy-gnss-jamming-spoofing.md](26-autonomy-gnss-jamming-spoofing.md).
- **Cyber/protocol takeover** — exploit weak command links or unauthenticated
  protocols. Defeated by encrypted, authenticated C2 (see
  [05_distributed_systems_comms_mesh.md](05_distributed_systems_comms_mesh.md)).
- **Directed energy** — high-power microwave (HPM) to fry electronics; lasers to
  burn airframes. Emerging, line-of-sight, power-hungry.
- **Kinetic** — guns, nets, interceptor drones, trained raptors. Effective but
  with collateral and cost-exchange problems.
- **The cost-exchange problem** — the strategic crux: a $1,000 drone that forces
  a $1,000,000 interceptor is *winning economically* even when shot down. Cheap,
  autonomous, attritable mass is the entire thesis behind companies like Anduril.

---

## 5. Why This Shapes Autonomy Design

Every counter above maps to a design principle for resilient autonomy:

| Counter | Design response |
|---|---|
| RF direction-finding | **Onboard autonomy, RF-silent / emission control** |
| Link jamming | **No dependence on continuous C2; mission completes offline** |
| GNSS jam/spoof | **VIO / INS / terrain-relative nav; GNSS-integrity monitoring** |
| Cyber takeover | **Encrypted + authenticated links; secure boot; signed firmware** |
| Kinetic / DE | **Low signature, maneuver, mass & attritability, swarm redundancy** |
| Classification | **Behavior that complicates ID; (and ethically, robust IFF for friendlies)** |

This is the throughline of the whole `learning/` folder: the autonomy in
[20-autonomy-ml-ai.md](20-autonomy-ml-ai.md), the GPS-denied navigation in
[28-autonomy-gnc.md](28-autonomy-gnc.md), and the decision logic in
[29-autonomy-planning-decision.md](29-autonomy-planning-decision.md) are all,
ultimately, electronic-protection measures.

---

## 6. Electronic Warfare in Depth — ES / EA / EP

§1 named the three divisions; here is the substance, because **EP is the lens you
design through.**

**Electronic Support (ES) — listening.** Passive detection, interception, and
**direction finding (DF)** of emissions; the input to SIGINT/ELINT.

- **DF & geolocation.** A single sensor gets a **bearing** (angle of arrival). Two
  or more sensors get a **fix** by triangulation, or by **TDOA** (time difference
  of arrival — same emission reaches sensors at different times) and **FDOA**
  (frequency difference from relative motion/Doppler). This is how a defender
  locates your *operator* from the C2 uplink. The defeat is to **not emit** — see
  EP below.
- **Threat warning.** A radar-warning-style receiver that tells a platform it's
  being illuminated or its link is being hunted.

**Electronic Attack (EA) — denying.** Active use of EM energy to degrade an
adversary:

- **Noise jamming** (barrage / spot / swept) — raise the noise floor on the link or
  GNSS band ([26-autonomy-gnss-jamming-spoofing.md](26-autonomy-gnss-jamming-spoofing.md) §8).
- **Deception jamming / DRFM.** Digital RF Memory captures a signal, modifies it,
  and replays it to create false targets or false ranges — the radar analog of
  GNSS spoofing.
- **GNSS denial/spoofing** — covered in [26-autonomy-gnss-jamming-spoofing.md](26-autonomy-gnss-jamming-spoofing.md).
- **Directed energy** — high-power microwave / laser (§9).

**Electronic Protection (EP) — surviving.** Everything that keeps *your* systems
working under EA. This is your job as an autonomy engineer:

| EP technique | What it defeats |
|---|---|
| **Frequency hopping (FHSS)** | Spot/follower jammers, narrowband DF |
| **Direct-sequence spread spectrum (DSSS)** | Narrowband jamming (processing gain) |
| **Encryption + authentication** | Cyber takeover, spoofing, meaconing |
| **LPI/LPD waveforms** | ES detection (low probability of intercept/detect) |
| **EMCON (emission control / RF-silent)** | DF, TDOA/FDOA geolocation of the operator |
| **Nulling antennas (CRPA)** | Directional jammers/spoofers |
| **Anti-jam GNSS (M-code / CRPA)** | GNSS denial |
| **Power management / directionality** | Interception range, geolocation accuracy |

The throughline: **every dependency on a single exploitable emission is a
vulnerability; every technique that removes or hardens it is EP.**

---

## 7. The EW Spectrum Picture

You cannot reason about EW without a feel for *where in the spectrum* the fight
happens. Drones and their counters live across these bands:

| Band | Rough range | Used for |
|---|---|---|
| HF | 3–30 MHz | Long-range/OTH; rare for small UAS |
| VHF/UHF | 30 MHz–1 GHz | Some C2, telemetry (900 MHz ISM), legacy radar |
| L | 1–2 GHz | **GNSS (1.2–1.6 GHz)**, some radar/telemetry |
| S | 2–4 GHz | **2.4 GHz ISM C2/video**, surveillance radar |
| C | 4–8 GHz | **5.8 GHz ISM video/C2**, weather radar |
| X | 8–12 GHz | Tracking/fire-control radar, some drone radar |
| Ku/Ka | 12–40 GHz | SATCOM, high-res radar, datalinks |

```
 freq → 0.9G    1.2–1.6G        2.4G         5.8G          8–12G
        │        │               │            │             │
       C2/    GNSS L-band   ISM C2/video   ISM video    fire-control
       tele                                              radar
```

Key intuitions:
- **Lower frequency** = better range, diffraction around terrain, but bigger
  antennas and less bandwidth.
- **Higher frequency** = more bandwidth (video), smaller antennas, but
  line-of-sight and weather-attenuated.
- A typical hobby/commercial drone is **loud** on 2.4/5.8 GHz (C2 + video) and
  **listening** on GNSS L-band — exactly the three emissions a C-UAS system hunts.
  An autonomous, RF-silent vehicle removes two of the three (§10).

---

## 8. Detection Modalities — The Physics & Limits

Why C-UAS is multi-modal: each sensor has a regime where it fails, and the
"low-slow-small" (LSS) drone sits in all of those gaps at once.

- **Radar.** Transmits, listens for the echo. A small drone has a **radar cross
  section (RCS) ~0.01 m²** (1000× smaller than a fighter), flies **slow and low**,
  and hides in **ground clutter** — the LSS problem. Specialized drone radars
  exploit **micro-Doppler**: the spinning props create a distinctive spectral
  modulation around the body return, separating a quadcopter from a bird. Range
  scales weakly with target RCS (radar equation: received power ∝ RCS / range⁴), so
  detecting a tiny RCS at useful range demands a lot of transmit power and
  processing.
- **RF detection (passive).** Listens for the drone's C2/video/telemetry emissions
  and **direction-finds** them (§6 DF/TDOA/FDOA). Cheap, long-range, and it also
  locates the *operator*. **Completely defeated by an RF-silent autonomous
  vehicle** — the single biggest reason onboard autonomy matters militarily.
- **EO/IR (cameras).** Visual and thermal imaging plus ML detection/tracking.
  Detection range is aperture- and contrast-limited; weather and night reduce it;
  thermal contrast against sky is small for an electric drone. Increasingly the
  *identification* sensor once another modality cues it.
- **Acoustic.** Microphone arrays pick up prop noise out to ~300–500 m, with
  array geometry giving a bearing. Short range, but cheap and useful for cued
  alerting in cluttered urban terrain where radar struggles.
- **Fusion.** Modern systems combine all four to **cut false alarms** (birds,
  aircraft, wind) and maintain continuous track — the track-fusion problem your own
  stack solves on the friendly side ([28-autonomy-gnc.md](28-autonomy-gnc.md)).

**Design takeaway (reinforcing §3):** every signature you reduce — RF (EMCON),
visual/thermal (low-contrast airframe, small size), acoustic (quieter props),
radar (terrain masking, low altitude) — pushes the defender *further left* in the
kill chain, before they can even track you.

### Worked: how a defender geolocates your operator

This is the concrete reason EMCON (§6, §10) matters. Suppose your ground station
transmits a C2 uplink and three networked ES sensors hear it:

1. **Single sensor → bearing only.** Sensor A measures angle-of-arrival, drawing a
   line of bearing toward you. One line is a *direction*, not a fix.
2. **Two sensors → triangulation.** Sensors A and B each get a bearing; the
   intersection is a position estimate. Accuracy degrades badly when the target is
   near the baseline (shallow crossing angle).
3. **Three+ sensors → TDOA hyperbolas.** Your emission reaches each sensor at a
   slightly different time. Each *pair* of sensors yields a hyperbola of constant
   time difference; intersecting two or more hyperbolas pins the location. Timing
   resolution drives accuracy — nanoseconds of TDOA error map to meters on the
   ground, so the sensors need a shared precise clock (often **GNSS-disciplined** —
   a nice irony, and a reason timing attacks in
   [26-autonomy-gnss-jamming-spoofing.md](26-autonomy-gnss-jamming-spoofing.md) §9
   cut both ways).
4. **Add motion → FDOA.** If sensors (or the target) move, the Doppler difference
   adds another constraint, tightening the fix.

```
        sensor A ●
                 \   bearing
          TDOA    \        ● sensor B
        hyperbola  \      /
                    \    /  intersection ≈ operator location
                     \  /
                      ✕  ← you, if you transmitted
                     /
        sensor C ●──/
```

The defeat is not a better radio — it's **transmitting less, or not at all.** Every
second of uplink is a second of exposure to this process; an autonomous vehicle that
completes its task with **zero emissions** hands the defender no hyperbolas to
intersect. That single fact reorders the whole kill chain (§11).

---

## 9. Defeat Mechanisms — Deep

Splitting the §4 overview into mechanism and effectiveness, especially against an
autonomous platform.

**Soft kill (electronic):**

- **RF link jamming.** Barrage (always on, power-hungry) or **reactive/follower**
  (jam only when the target transmits — efficient, defeats simple FHSS). Severs C2
  and video, forcing the drone into fail-safe (hover/RTL/land). **Useless against a
  vehicle that needs no link** — the autonomy is the countermeasure.
- **GNSS denial/spoofing.** Deny the fix or walk it — full treatment in
  [26-autonomy-gnss-jamming-spoofing.md](26-autonomy-gnss-jamming-spoofing.md).
  Defeated by VIO/INS/map-match and integrity monitoring.
- **Cyber / protocol takeover.** Exploit unauthenticated or weakly-authenticated
  command links to hijack the vehicle. Defeated by encrypted, **authenticated** C2,
  secure boot, and signed firmware (see [05_distributed_systems_comms_mesh.md](05_distributed_systems_comms_mesh.md)).
- **DRFM deception.** Against the C-UAS *radar* — false targets to mask the real
  one; more relevant to larger platforms.

**Hard kill (kinetic / energy):**

- **Kinetic.** Nets (drone-mounted or launched), interceptor drones, guns, even
  trained raptors. Effective but with collateral risk and a brutal **cost-exchange**
  problem (below).
- **Directed energy.** **High-power microwave (HPM)** couples energy into the
  drone's electronics through **front-door** (antennas) or **back-door**
  (seams/cables) paths to upset or fry them — can hit a swarm in a cone. **Lasers**
  put kilowatts on target and **dwell** until the airframe burns through —
  precise, deep magazine, but line-of-sight, power-hungry, and weather-limited.

**The cost-exchange problem (the strategic crux).** A $1,000 drone that forces a
$1,000,000 interceptor is **winning economically even when it's shot down**. Cheap,
autonomous, **attritable mass** is the entire thesis behind the modern defense-tech
wave (Anduril, etc.). Directed energy exists largely to fix this exchange ratio —
trading cents of electricity per shot for a drone — which is why every serious
C-UAS roadmap invests in it.

---

## 10. Hardening the Autonomous Platform (EP Checklist)

Translate the threats into concrete electronic protection for the `pixhawk/drone/`
stack. This is §5's table made into an engineering checklist:

| Threat | Concrete EP measure in your stack |
|---|---|
| RF direction-finding of operator | **EMCON / RF-silent mission** — complete the task with no uplink |
| C2 / video jamming | **Onboard autonomy** — mission runs offline; no continuous link required |
| GNSS jam / spoof | **VIO + map-match + EKF2 EV fusion**, GNSS-integrity monitor (link [26](26-autonomy-gnss-jamming-spoofing.md)) |
| Cyber / protocol takeover | **Encrypted + authenticated + frequency-hopping C2** when a link *is* used; secure boot; signed firmware ([32](05_distributed_systems_comms_mesh.md)) |
| Radar detection | **Low altitude, terrain masking**, small RCS, minimize metallic flat plates |
| EO/IR detection | **Low visual/thermal signature**, matte finish, manage motor heat |
| Acoustic detection | **Quieter props**, altitude, route away from sensor arrays |
| Kinetic / directed energy | **Maneuver, low signature, mass & attritability, swarm redundancy** |
| Classification / ID | **Robust friendly IFF**; behavior that complicates hostile ID (within LOAC, §12) |

Two design rules tie it together:

1. **No single point of exploitable dependence.** If losing the link, or GPS, or
   one sensor ends the mission, the design is fragile. Layer until no single EA
   stops you.
2. **Fail-safe must not betray you.** A naive "lost link → climb and broadcast RTL"
   behavior hands the defender both a DF beacon and a predictable trajectory.
   Fail-safe under EA should be *quiet* and *unpredictable to the adversary* while
   remaining safe and auditable
   ([09-foundations-safety-assurance.md](09-foundations-safety-assurance.md),
   [29-autonomy-planning-decision.md](29-autonomy-planning-decision.md)).

---

## 11. The Kill Chain vs. Your Design — Defeating Left

Map each kill-chain stage (§2) to how a hardened autonomous platform defeats it,
and note that **the earlier you break the chain, the cheaper and safer your
survival** ("defeating left"):

| Kill-chain stage | How the platform defeats it |
|---|---|
| **Detect** | EMCON (no RF), low radar/EO/IR/acoustic signature, terrain masking — nothing to find |
| **Track** | Low signature + maneuver breaks continuous custody; multi-modal fusion is denied clean data |
| **Identify** | No emissions to fingerprint; small visual signature delays classification |
| **Decide** | Compressed timelines from late detection erode the defender's ROE/decision window |
| **Defeat** | RF/GNSS-independent autonomy ignores soft kill; mass/attritability beats the cost-exchange of hard kill |

A platform that is hard at **detect** never reaches **defeat**. That is why the
autonomy in [20-autonomy-ml-ai.md](20-autonomy-ml-ai.md), the GPS-denied navigation
in [26-autonomy-gnss-jamming-spoofing.md](26-autonomy-gnss-jamming-spoofing.md), the
estimation/control in [28-autonomy-gnc.md](28-autonomy-gnc.md) and
[25-autonomy-control-theory.md](25-autonomy-control-theory.md), and the decision
logic in [29-autonomy-planning-decision.md](29-autonomy-planning-decision.md) are —
viewed through this file — **all electronic-protection measures**. Building toward
that integrated picture is a through-line of the
[02-ten-year-mastery-plan.md](02-ten-year-mastery-plan.md).

---

## 12. The Legal & Ethical Frame (Non-Optional)

- In the U.S., **most active C-UAS (jamming, spoofing, intercept, takeover) is
  illegal for civilians and even most government entities** without specific
  statutory authority. Authorities are narrowly granted (e.g., to DoD, DHS, DOE,
  DOJ under specific titles). The FAA prohibits interfering with aircraft.
- **Spectrum is regulated** — transmitting on GNSS or C2 bands without
  authorization violates FCC rules (and equivalents abroad).
- Lethal autonomy raises serious Law of Armed Conflict (LOAC) and policy
  questions — distinction, proportionality, meaningful human control. This is why
  a **policy/decision-logging layer** (your `policy/` constitution) isn't
  optional bureaucracy; it's the auditable record that a human remained
  accountable. See [14-career-dod-politics.md](14-career-dod-politics.md).

> This file is a **conceptual, defensive primer** for designing resilient,
> lawful autonomy. It is not an operational guide and deliberately omits any
> build/employment detail for jamming, spoofing, or weapons. Do nothing in the
> RF or kinetic domain without proper authority, licensing, and a controlled
> test environment.

---

## Sources & Citations

**Doctrine & official**
- U.S. DoD — *Joint Publication 3-85, Joint Electromagnetic Spectrum Operations*:
  https://www.jcs.mil/doctrine
- DoD *Counter-Small UAS Strategy* (2021): https://media.defense.gov
- FAA — UAS & counter-UAS authorities: https://www.faa.gov/uas
- DHS/CISA — Counter-UAS resources & legal advisory: https://www.cisa.gov/topics/physical-security/counter-unmanned-aircraft-systems
- GAO reports on counter-UAS: https://www.gao.gov

**Background reading**
- Adamy, D. — *EW 101: A First Course in Electronic Warfare*, Artech House (the
  standard accessible intro to EW).
- Kopp, C. — open analyses of EW and air defense (Air Power Australia archive).
- CRS — *Department of Defense Counter-Unmanned Aircraft Systems* reports:
  https://crsreports.congress.gov
- Scharre, P. — *Army of None: Autonomous Weapons and the Future of War*, Norton
  (policy/ethics of autonomy).

**On the cost-exchange / attritable-mass thesis**
- Brose, C. — *The Kill Chain: Defending America in the Future of High-Tech
  Warfare*, Hachette.

*This primer reflects openly published doctrine and analysis. Threat and counter
capabilities evolve rapidly and much detail is classified; treat the principles
as durable and verify specifics against current authoritative sources.*
