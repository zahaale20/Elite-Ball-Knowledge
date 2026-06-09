# Missiles, Guided Munitions & Hypersonics — The Sharp End of Guidance

> **Why this exists.** This repository teaches guidance, navigation and control
> for *vehicles that come back* — drones that loiter, survey, and land. The
> defense customer also fields a class of vehicles that **don't come back**:
> guided munitions, missiles, and hypersonic weapons. The math is the same
> [28-gnc](09-gnc.md) loop run to its most demanding extreme — intercepting a
> maneuvering target in seconds, with no second chance and no human in the loop at
> terminal phase. [27-counter-uas-ew](08-counter-uas-ew.md) teaches you to *defeat*
> threats; this teaches you how the threats themselves are guided, which is the
> other half of the same problem. An autonomy engineer in defense who cannot
> reason about a seeker, a proportional-navigation law, or a hypersonic glide
> trajectory is missing the domain's center of gravity.

> **What mastering it makes you.** The engineer who can derive proportional
> navigation from line-of-sight geometry, explain why a missile pulls lead instead
> of chasing, reason about seeker types and countermeasures, and articulate why
> hypersonics break the existing defense architecture. The person who understands
> the *physics and ethics* of the kill chain's terminal link.

> **A note on framing.** This is taught for **understanding, defense, and
> systems-engineering literacy** — the same posture as
> [124-ethics-export-control](../career/20-ethics-export-control.md) and
> [27-counter-uas-ew](08-counter-uas-ew.md). It is not a build guide; it is the
> conceptual fluency a defense autonomy engineer is expected to have. Real systems
> are export-controlled (ITAR) for exactly this reason.

This is [28-gnc](09-gnc.md) and [25-control-theory](06-control-theory.md) at the
hardest operating point, fed by the seeker-side perception of
[60-lidar-radar](21-lidar-radar-processing.md) and
[67-rf-and-comms](../engineering/03-rf-and-comms-systems.md), constrained by the
aerothermodynamics of [70-aerodynamics](../engineering/06-aerodynamics-and-flight-mechanics.md)
and [103-thermodynamics-and-fluids](../mathematics/09-thermodynamics-and-fluids.md).

---

## 1. The three phases of a guided weapon

Every guided munition runs the same arc; each phase is a different GNC regime.

- **Boost / launch.** Get off the rail or out of the tube and reach flight speed
  (the propulsion of [05](../engineering/05-propulsion-and-electric-propulsion.md)).
  Open-loop or simple attitude control.
- **Midcourse.** Fly efficiently toward a predicted intercept point, usually on
  inertial navigation ([28-gnc](09-gnc.md)) with optional datalink updates. The
  goal is to arrive in the **seeker's acquisition basket** with energy to spare.
- **Terminal.** The seeker acquires the target and the homing guidance law takes
  over for the endgame — the most demanding control problem in the repo: close a
  shrinking range on a possibly maneuvering target in seconds. Everything below is
  mostly about this phase.

```
 BOOST ──────► MIDCOURSE ──────────────► TERMINAL
 (get fast)    (INS + datalink to the    (seeker + homing law:
               predicted basket)          PN closes the endgame)
```

---

## 2. Proportional navigation — the elegant heart of homing

The defining insight of missile guidance: **don't chase the target, chase the
*intercept point*.** If you steer to keep the line-of-sight (LOS) to the target
from rotating, you are on a collision course — exactly how a sailor judges a
collision at sea ("constant bearing, decreasing range").

**Proportional Navigation (PN)** makes the missile's turn rate proportional to the
LOS rotation rate:

$$ a_{cmd} = N\, V_c\, \dot{\lambda} $$

where $a_{cmd}$ is commanded lateral acceleration, $\dot{\lambda}$ is the
LOS rate (measured directly by the seeker), $V_c$ is the closing velocity, and
$N$ (typically 3–5) is the navigation constant. Read the genius of it:

- It nulls the LOS rate, forcing a collision-triangle (lead pursuit), not a
  tail-chase. A pure pursuer (always pointing *at* the target) wastes energy in a
  curving tail-chase and often can't catch a crossing target at all.
- It needs only what a simple seeker measures — **LOS rate and closing speed** —
  not the target's absolute position. That minimalism is why PN has dominated for
  70 years.
- **Augmented PN (APN)** adds a term for known target acceleration; modern
  variants use optimal/estimator-based guidance, but PN is the conceptual spine.

This is the same line-of-sight geometry that the **collision-avoidance** logic in
[54-motion-planning](15-motion-planning.md) and the COLREGs reasoning in
[131-maritime-and-undersea-autonomy](26-maritime-and-undersea-autonomy.md) use —
inverted from "avoid the collision triangle" to "achieve it."

---

## 3. Seekers — the perception system of a weapon

The seeker is the munition's [50-perception-deep](11-perception-deep.md) sensor,
and seeker type drives everything about how the weapon is used and countered.

- **RF / radar seekers.**
  - **Active** — the missile carries its own radar (fire-and-forget; "launch and
    leave"). Robust, all-weather, but the emission can be detected/jammed.
  - **Semi-active** — the launch platform "paints" the target; the missile homes
    on the reflection. Cheaper missile, but the shooter must keep illuminating.
  - **Passive / anti-radiation** — homes on the target's *own* emissions (a radar
    that's tracking you), the heart of SEAD/defense-suppression.
- **IR / electro-optical seekers.** Home on heat (an engine, an exhaust plume) or
  on imaged shape. **Imaging IR (IIR)** seekers do onboard
  [59-computer-vision](20-computer-vision.md) target recognition and aimpoint
  selection — modern short-range and precision weapons. Passive (no emission), but
  weather- and countermeasure-sensitive (flares, the IR analog of chaff).
- **GPS/INS-guided** (the JDAM class). For fixed/slow targets, "guidance" is just
  precise [26-gnss](07-gnss-jamming-spoofing.md) + [28-gnc](09-gnc.md) navigation
  to a coordinate — which is exactly why GNSS denial and the GPS-denied techniques
  of [07](07-gnss-jamming-spoofing.md) and quantum PNT
  ([16](../engineering/16-quantum-technologies.md)) matter so much.
- **Multi-mode / dual-seeker** weapons fuse RF + IR to defeat single-mode
  countermeasures — the [52-sensor-fusion](13-sensor-fusion.md) argument applied
  to the endgame.

---

## 4. The counter-game — why guidance is an arms race

Every seeker invites a countermeasure, and every countermeasure invites a
counter-counter. This is [27-counter-uas-ew](08-counter-uas-ew.md) and
[133-directed-energy-and-electronic-warfare](28-directed-energy-and-electronic-warfare.md)
viewed from the weapon's side.

- **Soft kill:** jamming the RF seeker, decoying the IR seeker with **flares**, the
  radar seeker with **chaff**, towed decoys, and DRFM (digital RF memory)
  repeaters that feed the seeker a false return. The defense in
  [26-gnss](07-gnss-jamming-spoofing.md) is the same family of tricks against a
  different seeker.
- **Hard kill:** intercept the incoming weapon (an interceptor missile, a gun like
  Phalanx, or a directed-energy weapon from
  [28](28-directed-energy-and-electronic-warfare.md)).
- **Maneuver & signature:** the target maneuvers to stress the guidance law (force
  the PN law past the missile's acceleration limit) or reduces signature (low
  observability) so the seeker acquires late.
- **The engineering lesson:** robustness comes from **multi-mode sensing,
  resistance to deception, and acceleration margin** — the same resilience
  principles as GPS-denied navigation and contested comms throughout the repo.

---

## 5. Hypersonics — why everyone is suddenly talking about them

"Hypersonic" means **Mach 5+**, but the strategic novelty is not just speed
(ballistic warheads have been hypersonic for decades) — it's **maneuvering at
hypersonic speed within the atmosphere**, which breaks the prediction that missile
defense relies on. Two classes:

- **Hypersonic Glide Vehicle (HGV).** Boosted high by a rocket, then **glides and
  maneuvers** in the upper atmosphere on a flat, unpredictable trajectory — far
  lower and more maneuverable than a ballistic arc, so it's harder to track and to
  intercept.
- **Hypersonic Cruise Missile (HCM).** Powered the whole way by an air-breathing
  **scramjet** (supersonic-combustion ramjet — the air never slows below
  supersonic in the engine), sustaining Mach 5+ in level flight. The propulsion
  frontier of [05](../engineering/05-propulsion-and-electric-propulsion.md).

The hard engineering problems are all physics from this repo, turned to extremes:

- **Aerothermodynamics.** At Mach 5+ the air ahead is heated to thousands of
  degrees; surfaces glow. Thermal protection and materials
  ([72-thermal](../engineering/08-thermal-management.md),
  [71-structures](../engineering/07-structures-and-materials.md)) are the limiting
  technology — the same reentry-heating problem as
  [130-space-systems §7](../space/01-space-systems-and-astronautics.md).
- **The plasma sheath.** The superheated, ionized air around the vehicle
  **attenuates radio** — GPS and datalink black out, and the seeker must see
  through plasma. A genuinely unsolved sensing/comms problem (the EM physics of
  [10](../mathematics/10-electromagnetics.md)).
- **Guidance under extreme dynamics.** Control authority, timing, and estimation
  at Mach 7 leave almost no margin — [25-control-theory](06-control-theory.md) at
  the edge of the envelope.
- **The defensive consequence:** HGVs compress the warning and engagement timeline
  so far that the answer is shifting to **space-based tracking**
  ([01](../space/01-space-systems-and-astronautics.md)) and **directed energy**
  ([28](28-directed-energy-and-electronic-warfare.md)) — which is why these three
  guides belong in one band.

---

## 6. Loitering munitions — where this band meets the drone

The line between "drone" and "missile" has blurred, and the blur is the
fastest-growing category in modern war. A **loitering munition** ("kamikaze
drone," Switchblade/Lancet/Shahed class) is a drone that *is* the warhead: it
loiters like a UAV ([21-vtol-roadmap](02-vtol-roadmap.md),
[29-planning-decision](10-planning-decision.md)), then terminal-homes like a
missile (§2–3).

- It uses the **same autonomy stack as the rest of this repo** — perception,
  navigation, planning — plus a terminal homing law. Your drone skills transfer
  directly.
- It collapses cost: a few-thousand-dollar loitering munition can kill a
  multi-million-dollar target, the **cost-asymmetry** thesis of
  [47-startup-asymmetric-playbook](../companies/11-startup-asymmetric-playbook.md)
  and [39-productized-defense](../companies/03-productized-defense.md) made lethal.
- It forces the **ethics and autonomy-level** questions head-on: how much terminal
  decision authority does the machine have? This is the
  [134-human-autonomy-teaming](29-human-autonomy-teaming.md) and
  [124-ethics-export-control](../career/20-ethics-export-control.md) problem at its
  sharpest — the human-on-the-loop vs. human-in-the-loop line, drawn in seconds.

---

## 7. The kill chain — where a weapon is one link

A weapon is useless without the chain that finds, fixes, tracks, targets, and
assesses — the **F2T2EA** kill chain of
[07-defense-acquisition](../foundations/07-defense-acquisition.md) and
[40-palantir-forward-deployed](../companies/04-palantir-forward-deployed.md).

- **Find/Fix/Track** is ISR and sensor fusion ([13](13-sensor-fusion.md),
  [21](21-lidar-radar-processing.md)) — often from the
  [130-space](../space/01-space-systems-and-astronautics.md) and drone layers.
- **Target** is the decision ([29-planning-decision](10-planning-decision.md)) and
  the human authority ([29](29-human-autonomy-teaming.md)).
- **Engage** is this guide.
- **Assess** (BDA) closes the loop and feeds the next cycle.
- **The systems lesson:** the missile is the *cheap, replaceable* end of an
  expensive chain. Modern advantage comes from **compressing the chain** (sensor
  to shooter in seconds) and making it **resilient** to the EW/cyber/space attacks
  in [08](08-counter-uas-ew.md), [28](28-directed-energy-and-electronic-warfare.md),
  and [01](../space/01-space-systems-and-astronautics.md). Whoever closes the
  loop faster wins, independent of who has the better warhead.

---

## Drills

1. **PN intuition.** Sketch a crossing-target engagement; show why pure pursuit
   curves into a tail-chase and PN flies the straight collision triangle. Compute
   $a_{cmd}$ for a given $\dot\lambda$, $V_c$, and $N=4$.
2. **Seeker selection.** For (a) a fixed bridge, (b) a maneuvering jet, (c) an
   enemy search radar — pick a seeker type and justify it, then name the
   countermeasure each invites.
3. **Hypersonic tracking.** Explain in two sentences why an HGV is harder to
   intercept than a ballistic warhead, and why the answer pushes sensing to space.
4. **Plasma blackout.** Given radio attenuation in the reentry/hypersonic plasma
   sheath, propose which sensing modality you'd trust in terminal phase and why.
5. **Ethics line.** For a loitering munition, write the rule for what the machine
   may decide autonomously vs. what requires a human, and defend it against
   [20](../career/20-ethics-export-control.md).

---

## Where this connects

- **Core:** GNC/control ([09](09-gnc.md), [06](06-control-theory.md)), seeker
  perception ([11](11-perception-deep.md), [20](20-computer-vision.md),
  [21](21-lidar-radar-processing.md)), fusion ([13](13-sensor-fusion.md)).
- **Physics:** aero & aerothermo ([06](../engineering/06-aerodynamics-and-flight-mechanics.md),
  [09](../mathematics/09-thermodynamics-and-fluids.md)), propulsion
  ([05](../engineering/05-propulsion-and-electric-propulsion.md)), thermal/structures
  ([08](../engineering/08-thermal-management.md),
  [07](../engineering/07-structures-and-materials.md)).
- **The counter-game & context:** counter-UAS/EW ([08](08-counter-uas-ew.md)),
  directed energy ([28](28-directed-energy-and-electronic-warfare.md)), space
  tracking ([01](../space/01-space-systems-and-astronautics.md)), human authority
  ([29](29-human-autonomy-teaming.md)), ethics/ITAR
  ([20](../career/20-ethics-export-control.md)).
