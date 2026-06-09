# Space Systems & Astronautics — Orbits, Spacecraft, and the Contested High Ground

> **Why this exists.** This repository is built around aerospace and defense
> autonomy, yet it had **no coverage of space at all** — the single largest
> domain gap for an aerospace engineer. The atmosphere ends; the mission does
> not. Every modern conflict already runs on space: GPS timing for everything in
> [07-autonomy-gnss-jamming-spoofing.md](../autonomy/07-gnss-jamming-spoofing.md),
> ISR from orbit, satellite comms (Starlink/Starshield) that keep drones flying
> when terrestrial links die, and missile warning that starts the kill chain.
> The propulsion physics in
> [05-engineering-propulsion-and-electric-propulsion.md](../engineering/05-propulsion-and-electric-propulsion.md)
> gets you off the pad; this guide is what happens **after** the rocket equation
> is satisfied — how things stay up, talk, sense, and fight in orbit.

> **What mastering it makes you.** The engineer who can reason from Kepler and
> the vis-viva equation to a real mission: pick an orbit, size a constellation,
> close a link budget, budget the power and thermal, and explain why a given
> architecture survives (or doesn't) in a contested space domain. The person who
> understands that space is not a sanctuary anymore — it is terrain.

Space is orbital mechanics ([95-optimization](../mathematics/01-optimization.md)
and the dynamics of [03-mathematics](../foundations/03-mathematics.md) made
celestial), plus the comms of
[67-rf-and-comms-systems](../engineering/03-rf-and-comms-systems.md), the power
and thermal of [04](../engineering/04-power-electronics.md)/[08](../engineering/08-thermal-management.md),
and the GNC of [28-gnc](../autonomy/09-gnc.md) applied where there is no air and
no ground.

---

## 1. The one equation that governs everything in orbit

An orbit is **continuous free fall** — the spacecraft moves sideways fast enough
that it keeps missing the Earth. Newton's gravitation plus the two-body
assumption gives the **vis-viva equation**, the workhorse of astrodynamics:

$$ v^2 = \mu\left(\frac{2}{r} - \frac{1}{a}\right) $$

where $\mu = GM_\oplus \approx 3.986\times10^{14}\ \mathrm{m^3/s^2}$ is Earth's
gravitational parameter, $r$ is the current distance from Earth's center, and $a$
is the orbit's semi-major axis. Read the levers directly: speed is set entirely
by *where you are* ($r$) and *how big the orbit is* ($a$). For a circular orbit
($r=a$):

$$ v_c = \sqrt{\frac{\mu}{r}}, \qquad T = 2\pi\sqrt{\frac{a^3}{\mu}} $$

The period law $T\propto a^{3/2}$ is **Kepler's third law** — it is why a low
satellite races around in ~90 minutes and a GEO satellite takes exactly one day
(and so appears to hang still). Memorize three numbers and you can sanity-check
almost any space conversation:

| Orbit | Altitude | Orbital speed | Period |
|---|---|---|---|
| LEO (ISS) | ~400 km | ~7.66 km/s | ~92 min |
| MEO (GPS) | ~20,200 km | ~3.87 km/s | ~12 h |
| GEO | ~35,786 km | ~3.07 km/s | ~24 h |

---

## 2. The six numbers that define any orbit

A spacecraft's state is six numbers (position + velocity), but engineers prefer
the **Keplerian elements** because they're nearly constant and physically
meaningful:

- **$a$ — semi-major axis**: orbit size → energy and period.
- **$e$ — eccentricity**: shape (0 = circle, <1 = ellipse).
- **$i$ — inclination**: tilt of the orbit plane vs. the equator. $i=0$
  equatorial; $i=90°$ polar; $i>90°$ retrograde.
- **$\Omega$ — RAAN** (right ascension of ascending node): where the orbit plane
  crosses the equator going north — "which way the plane is rotated."
- **$\omega$ — argument of perigee**: where the low point sits within the plane.
- **$\nu$ — true anomaly**: where the satellite is *right now*.

The orbit's energy lives entirely in $a$: $\varepsilon = -\mu/2a$. **Changing $a$
costs propellant; changing the plane ($i$, $\Omega$) costs a *lot* more**, which
is the single most important operational fact in space — you launch into the
plane you need, because changing it later is ruinously expensive (§4).

---

## 3. The orbit zoo — and why each exists

Orbit choice is a mission decision, not a preference. Each regime is a different
tradeoff of resolution, coverage, latency, and survivability.

- **LEO (160–2,000 km).** Close → high-resolution imaging, low-latency comms
  (Starlink ~25 ms), cheap to reach. Cost: each satellite sees only a small patch
  and whips past in minutes, so you need **constellations** (§5). Drag is real
  here and orbits decay.
- **SSO (Sun-synchronous), a special LEO.** Inclination (~98°, slightly
  retrograde) chosen so that **J2 nodal precession** exactly matches Earth's
  orbit around the Sun, making the satellite cross every latitude at the **same
  local solar time** every day — constant lighting, ideal for imaging. This is
  J2 (Earth's equatorial bulge) used as a feature, not a nuisance.
- **MEO (~20,000 km).** The GNSS sweet spot: a handful of satellites give global
  coverage with manageable geometry. GPS, Galileo, GLONASS, BeiDou all live here.
- **GEO (35,786 km, equatorial).** Period = sidereal day → the satellite appears
  fixed over one spot. Perfect for comms and persistent stare (missile warning,
  weather), at the cost of distance (long latency, weak signals, huge antennas)
  and a crowded, contested belt.
- **HEO / Molniya (high eccentricity, $i\approx63.4°$).** Perigee low, apogee
  very high; the satellite **loiters near apogee for hours** over high latitudes
  GEO can't see (Russia's classic use). The $63.4°$ inclination zeroes the
  argument-of-perigee drift.
- **Cislunar / NRHO.** The emerging contested volume between Earth and Moon
  (Gateway, lunar economy) — three-body dynamics, not two-body, and a new
  domain-awareness problem.

```
        GEO ─ comms, missile warning, weather (hangs still)
   MEO ───── GNSS (GPS) — global nav from ~24 birds
 LEO ─────── imaging, Starlink, ISR (fast, close, needs many)
Earth
```

---

## 4. Maneuvering — the tyranny of Δv, again

You don't "drive" in space; you change orbits with impulsive burns, and every
burn spends from a fixed $\Delta v$ budget set by the rocket equation
(see [69-propulsion](../engineering/05-propulsion-and-electric-propulsion.md)).
The canonical transfer between two circular orbits is the **Hohmann transfer** —
an ellipse tangent to both, requiring two burns:

$$ \Delta v_1 = \sqrt{\frac{\mu}{r_1}}\left(\sqrt{\frac{2r_2}{r_1+r_2}}-1\right),
\qquad
\Delta v_2 = \sqrt{\frac{\mu}{r_2}}\left(1-\sqrt{\frac{2r_1}{r_1+r_2}}\right) $$

It is the minimum-energy two-impulse transfer. Key operational truths:

- **Plane changes are brutal.** A pure inclination change of angle $\theta$ costs
  $\Delta v = 2v\sin(\theta/2)$. At LEO speeds, a 30° change costs ~4 km/s — more
  than reaching orbit from the ground costs in extra propellant. *You launch into
  your plane.*
- **Low-thrust spirals** (electric propulsion, $I_{sp}$ ~1500–4000 s) trade time
  for propellant: a Hall thruster can raise an orbit over weeks using a tenth of
  the propellant a chemical burn would need. This is why GEO comms sats and the
  Starlink fleet went electric.
- **Rendezvous & proximity operations (RPO)** — matching another object's orbit —
  is the foundation of servicing, refueling, debris removal, and, bluntly,
  co-orbital counterspace. The math is the **Clohessy-Wiltshire equations**
  (linearized relative motion), the orbital cousin of the relative-state
  estimation in [53-state-estimation-advanced](../autonomy/14-state-estimation-advanced.md).

---

## 5. Constellations — turning fast, near-sighted LEO into global coverage

A single LEO satellite is useless for persistence; a **constellation** is the
product. Design is a coverage-vs-cost optimization:

- **Walker constellations** parameterize the fleet as $i{:}t/p/f$ — inclination,
  total satellites $t$, planes $p$, and phasing $f$ — to spread coverage evenly.
- **Coverage** is set by each satellite's footprint (a function of altitude and
  minimum elevation angle) and the number of planes. **Revisit time** — how often
  a point on Earth is seen — is the imaging metric; **continuity** — never having
  zero satellites in view — is the comms metric.
- **Inter-satellite links (ISLs)**, usually optical, let a constellation route
  data across the sky without touching the ground — the key to low-latency global
  comms and to ISR that doesn't depend on a downlink station near the target.
- **The economic revolution:** when launch cost collapses (reusability, §7) and
  satellites become mass-produced commodities, the optimal architecture flips
  from *a few exquisite, expensive birds* to *thousands of cheap, attritable
  ones*. Starlink/Starshield, the SDA's proliferated warfighter constellations,
  and Earth-observation fleets (Planet) are all this thesis. It is the
  [38-spacex-rapid-iteration](../companies/02-spacex-rapid-iteration.md) and
  [41-tesla-vertical-integration](../companies/05-tesla-vertical-integration-data.md)
  playbooks applied to orbit.

---

## 6. The spacecraft as a system — the subsystems that keep it alive

A satellite is a tightly coupled set of subsystems, each a chapter of this repo
relocated to vacuum. The bus serves the payload; everything else is overhead the
mission tolerates.

- **Structure & mechanisms** — survive launch loads (the most violent part of the
  mission), deploy solar arrays and antennas. See
  [71-structures-and-materials](../engineering/07-structures-and-materials.md).
- **Power** — solar arrays + batteries sized for the worst-case **eclipse**
  (a LEO satellite is in shadow ~35 min every orbit). Power budgeting is relentless;
  see [68-power-electronics](../engineering/04-power-electronics.md) and
  [79-batteries](../engineering/15-batteries-and-energy-storage.md).
- **Thermal** — no air, so heat moves only by **radiation and conduction**. One
  side bakes in sun, the other radiates to ~3 K space. Multi-layer insulation,
  radiators, heaters, and louvers hold electronics in range. See
  [72-thermal-management](../engineering/08-thermal-management.md).
- **ADCS (Attitude Determination & Control)** — point the payload. Sensors (star
  trackers, sun sensors, gyros, magnetometers) feed an estimator; actuators
  (**reaction wheels**, magnetorquers, thrusters) apply torque. This is the
  [28-gnc](../autonomy/09-gnc.md) estimation/control loop in three rotational
  axes, where reaction wheels **store** angular momentum and thrusters
  periodically **desaturate** them.
- **Propulsion** — station-keeping (fighting drag, J2, solar pressure, lunisolar
  perturbations) and maneuvering; chemical for big burns, electric for efficiency.
- **C&DH (Command & Data Handling)** — the rad-hardened flight computer. Space
  radiation flips bits (**single-event upsets**), so you use EDAC memory,
  watchdogs, and triple-modular redundancy — the reliability discipline of
  [77-reliability](../engineering/13-reliability-and-failure-analysis.md) under
  a particle flux.
- **Comms / TT&C** — telemetry, tracking & command plus the payload downlink. The
  whole thing lives or dies on the link budget (§8).

---

## 7. Getting there and getting down — launch, reentry, and reuse

- **Launch** is the $\Delta v \approx 9.4$ km/s climb out of the gravity well
  (the ~7.8 km/s orbital speed plus gravity and drag losses), staged to beat the
  rocket equation's exponential (see
  [69-propulsion §2](../engineering/05-propulsion-and-electric-propulsion.md)).
  **Reusability** (land the booster, fly it again) is the cost revolution that
  makes proliferated constellations economic — the dominant strategic fact in
  modern space.
- **Reentry** is the reverse problem: you have ~7.8 km/s of kinetic energy to get
  rid of, and you dump it as **heat** into the atmosphere. The vehicle flies a
  blunt body to push a bow shock ahead of it (most heat goes into the air, not the
  vehicle) and threads a narrow **reentry corridor** — too steep burns up or
  crushes, too shallow skips off. Thermal protection (ablative or reusable tiles)
  is the enabling technology; the physics is the hypersonic aerothermodynamics of
  [132-missiles-guided-munitions-hypersonics](../autonomy/27-missiles-guided-munitions-hypersonics.md).
- **Disposal** is now mandatory engineering: deorbit within 5 years (LEO) or boost
  to a graveyard orbit (GEO). The alternative is **Kessler syndrome** — a
  collisional cascade of debris that could render orbits unusable (§9).

---

## 8. The link budget — why space comms is hard

Everything a satellite does for you arrives as a radio (or optical) link, and the
link budget is the unforgiving accounting of [67-rf-and-comms](../engineering/03-rf-and-comms-systems.md)
stretched over thousands of kilometers. The received power:

$$ P_r = P_t + G_t + G_r - L_{fs} - L_{other}, \qquad
L_{fs} = 20\log_{10}\!\left(\frac{4\pi d}{\lambda}\right) $$

Free-space path loss grows as **distance squared and frequency squared** — a GEO
link 100× farther than a LEO link loses 40 dB just to range. The figure of merit
is **$E_b/N_0$** (energy per bit over noise density); fall below the threshold for
your modulation/coding and the link simply stops. The levers:

- **More antenna gain** (bigger dish, phased arrays, tight beams) — but tighter
  beams demand better pointing (back to ADCS).
- **Higher frequency** (Ka-band, optical) — more bandwidth, but more rain fade and
  harder pointing.
- **Better coding** (LDPC, turbo) buys you margin in dB for free, the
  [100-information-theory](../mathematics/06-information-theory.md) channel-coding
  payoff made physical.
- **Optical inter-satellite links** dodge spectrum congestion and jamming
  entirely — a laser beam is hard to intercept or interfere with.

---

## 9. Space as a contested domain — the part most engineers miss

Space is no longer a sanctuary; it is **terrain**, with its own warfighting
domain (U.S. Space Force, established 2019) and an arms competition. An autonomy
engineer who depends on space assets must understand how they're threatened — it
is the orbital extension of [27-counter-uas-ew](../autonomy/08-counter-uas-ew.md)
and [26-gnss](../autonomy/07-gnss-jamming-spoofing.md).

- **The threat ladder, reversible → irreversible:** jamming/spoofing of uplinks
  and downlinks (cheap, deniable, everyday) → laser dazzling of imaging sensors →
  cyber attack on ground stations (often the weakest link) → co-orbital
  RPO/grappling (a "inspector" that can also disable) → direct-ascent ASAT
  (a missile that shatters a satellite — and creates debris that endangers
  everyone, as the 2007 Chinese and 2021 Russian tests showed).
- **Space Domain Awareness (SDA)** is the orbital sensor-fusion and tracking
  problem: maintain a catalog of tens of thousands of objects from radar and
  optical sensors, predict conjunctions, and detect maneuvers that signal intent.
  It is [52-sensor-fusion](../autonomy/13-sensor-fusion.md) and
  [60-lidar-radar](../autonomy/21-lidar-radar-processing.md) at planetary scale.
- **Resilience by architecture:** the strategic answer to fragile, exquisite
  satellites is **proliferation and disaggregation** — many cheap, attritable
  nodes so killing one changes nothing. This is exactly why SDA's transport and
  tracking layers and Starshield exist, and it is the same attritability thesis
  driving the drone cohort in
  [121-new-defense-tech-cohort](../companies/19-new-defense-tech-cohort.md).
- **Kessler syndrome** is the shared-commons failure mode: debris begets
  collisions beget more debris. Counterspace that creates debris poisons the well
  for the attacker too — the orbital tragedy of the commons.

---

## 10. The new space economy — why this is a career, not a footnote

The cost of mass to orbit fell ~20× in a decade, and the consequences ripple
through every band of this repo:

- **Launch** became a commodity (reusable boosters, rideshare), unlocking
  proliferated LEO.
- **Earth observation** turned into a data business — daily global imaging feeding
  the [40-palantir-forward-deployed](../companies/04-palantir-forward-deployed.md)
  and [20-ml-ai](../autonomy/01-ml-ai.md) analysis stacks.
- **Comms** (Starlink/Starshield, OneWeb, Kuiper) became the backbone that keeps
  forward forces and drones connected when terrestrial networks are denied —
  directly relevant to the resilient-comms problem of
  [05-distributed_systems_comms_mesh](../foundations/05-distributed_systems_comms_mesh.md).
- **Defense space** (SDA, missile warning/tracking, responsive launch) is one of
  the fastest-growing budget lines and a core part of the
  [11-defense-aerospace-playbook](../career/02-defense-aerospace-playbook.md).

The thesis of this guide: space is the high ground over every other domain in
this repository. The autonomy you build flies on GPS timing, talks over satellite
comms, and is cued by orbital ISR. Understanding the layer above you is what turns
a drone engineer into a *systems* engineer.

---

## Drills (do these, don't just read)

1. **Vis-viva sanity check.** Compute orbital speed and period for a 550 km
   Starlink orbit. Confirm it matches the ~95-minute, ~7.6 km/s ballpark.
2. **Hohmann budget.** Compute the two-burn $\Delta v$ to raise a satellite from
   400 km to GEO. Then compute the $\Delta v$ for a 28.5°→0° plane change at GEO
   speed and notice which dominates.
3. **Link budget.** Take a 20 W Ka-band downlink from LEO (550 km) vs. GEO and
   compute the free-space path loss difference in dB. Explain why GEO needs a much
   bigger antenna.
4. **Constellation sizing.** Estimate how many satellites at 550 km (with a 25°
   minimum elevation) you need for continuous coverage of a single mid-latitude
   point. Notice how the number explodes — and why ISLs matter.
5. **Threat reasoning.** For a drone mission that depends on GPS + Starlink, list
   every space-segment dependency and the cheapest adversary action that degrades
   each. Map it back to [07](../autonomy/07-gnss-jamming-spoofing.md) and
   [08](../autonomy/08-counter-uas-ew.md).

---

## Where this connects

- **Up the stack:** propulsion physics
  ([05](../engineering/05-propulsion-and-electric-propulsion.md)), GNC/estimation
  ([09](../autonomy/09-gnc.md)), RF/comms
  ([03](../engineering/03-rf-and-comms-systems.md)).
- **Across:** GNSS denial ([07](../autonomy/07-gnss-jamming-spoofing.md)),
  counter-UAS/EW ([08](../autonomy/08-counter-uas-ew.md)), hypersonics & reentry
  ([27](../autonomy/27-missiles-guided-munitions-hypersonics.md)), quantum PNT
  for when GPS is gone ([16](../engineering/16-quantum-technologies.md)).
- **Strategy:** SpaceX ([02](../companies/02-spacex-rapid-iteration.md)), the new
  defense cohort ([19](../companies/19-new-defense-tech-cohort.md)), the defense
  playbook ([02](../career/02-defense-aerospace-playbook.md)).
