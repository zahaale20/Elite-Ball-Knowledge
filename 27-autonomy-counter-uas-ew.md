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
  [32-systems-cybersecurity-autonomy.md](32-systems-cybersecurity-autonomy.md)).
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

## 6. The Legal & Ethical Frame (Non-Optional)

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
