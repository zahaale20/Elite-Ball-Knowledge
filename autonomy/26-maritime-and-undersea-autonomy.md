# Maritime & Undersea Autonomy — The Domain Where Light Dies and Sound Rules

> **Why this exists.** The autonomy band of this repository is entirely **aerial
> and ground** — perception by camera and LiDAR, navigation by GPS and visual
> odometry. The ocean breaks all of those assumptions at once: GPS does not
> penetrate water, radio dies in meters, cameras see nothing in turbid or deep
> water, and the medium itself moves. Yet maritime is one of the fastest-growing
> defense-autonomy frontiers — the [121-new-defense-tech-cohort](../companies/19-new-defense-tech-cohort.md)
> guide already names Saronic (autonomous surface vessels) and Anduril's Dive
> (undersea), and the Navy's "hellscape" of attritable uncrewed boats is now
> doctrine. An autonomy engineer who only knows the air is fluent in one of three
> domains.

> **What mastering it makes you.** The engineer who can design an autonomy stack
> for a world where **sound replaces light** — close a sonar detection budget,
> navigate for hours with no GPS fix, plan through currents and traffic-separation
> law, and explain why an undersea vehicle is a fundamentally different machine
> from a drone. The person who can move the [28-gnc](../autonomy/09-gnc.md) and
> [50-perception-deep](../autonomy/11-perception-deep.md) loop underwater and have
> it still work.

This is the [28-gnc](../autonomy/09-gnc.md) estimation/control loop, the
[54-motion-planning](../autonomy/15-motion-planning.md) decision layer, and the
[52-sensor-fusion](../autonomy/13-sensor-fusion.md) fusion stack, re-derived for a
medium where the physics of [99-signal-processing](../mathematics/05-signal-processing.md)
and [104-electromagnetics](../mathematics/10-electromagnetics.md) behave nothing
like they do in air.

---

## 1. The medium changes everything

Before any algorithm, internalize the four physical facts that make the ocean a
different planet for autonomy:

1. **Radio (and GPS) cannot penetrate seawater.** Seawater is a conductor;
   EM waves attenuate over centimeters to a few meters. A submerged vehicle has
   **no GPS, no satcom, no Wi-Fi**. Communication and navigation must use sound.
2. **Light dies fast.** Even clear water absorbs and scatters light over tens of
   meters; coastal water over a few. Cameras are short-range and often useless;
   the primary sense is **acoustic**.
3. **Sound, by contrast, travels superbly** — for kilometers — which is why sonar
   is to the ocean what radar is to the air. The entire perception stack is built
   on acoustics.
4. **The medium moves and the platform is buoyant.** Currents, tides, waves, and
   density layers act on the vehicle continuously. Unlike a drone that can hover,
   an underwater glider or a surface boat is always negotiating with the water.

```
Air domain:  EM rules (radar, GPS, comms, cameras)  — light & radio cheap
Sea surface: EM works above, sound works below — the seam both exploit
Undersea:    SOUND rules; EM is dead — navigate & sense & talk by acoustics
```

---

## 2. The platforms — USV, UUV, glider, and the hybrids

- **USV (Uncrewed Surface Vessel).** A boat with no crew. Keeps GPS and radio
  (it's on the surface), so it's the "easy" maritime autonomy problem — but it
  must obey **COLREGs** (the maritime rules of the road, §6) and survive sea
  states that would shred a drone. This is Saronic's and the Navy's attritable
  "hellscape" thesis: many cheap boats beating a few expensive ones — the
  [47-startup-asymmetric-playbook](../companies/11-startup-asymmetric-playbook.md)
  applied to the sea.
- **UUV (Uncrewed Undersea Vehicle).** Submerged. Subdivided into **ROVs**
  (tethered, human-piloted — power and comms over the cable) and **AUVs**
  (untethered, autonomous — the hard problem, since they get no GPS and no comms
  once they dive). Anduril Dive-LD and the Navy's Orca XLUUV are AUVs.
- **Underwater glider.** No propeller — it changes its **buoyancy** and uses wings
  to glide forward in a sawtooth, sipping power so it can patrol for **months**.
  The endurance champion, at the cost of speed and control authority.
- **The endurance spectrum is the design driver:** a torpedo-shaped AUV trades
  hotel load against mission length; a glider trades speed against months of
  persistence. Energy, as always
  ([79-batteries](../engineering/15-batteries-and-energy-storage.md)), sets the
  mission.

---

## 3. Underwater acoustics — the physics you cannot skip

Everything underwater senses and communicates by sound, so the propagation
physics *is* the engineering. The speed of sound in seawater is ~1500 m/s
(roughly 4.4× faster than in air) and — critically — **it varies with
temperature, salinity, and pressure (depth)**. That variation bends sound rays.

- **Sound speed profile (SSP) and refraction.** Because sound speed changes with
  depth, rays bend toward lower speed (Snell's law). This creates **shadow
  zones** a sonar cannot see into and **sound channels** (the SOFAR channel) where
  sound travels for thousands of kilometers. A sonar operator who ignores the SSP
  will look in the wrong place.
- **Transmission loss.** Sound spreads (spherical/cylindrical) and is absorbed,
  and absorption rises steeply with frequency:
  $$ TL = 20\log_{10}(r) + \alpha r $$
  Low frequencies travel far but resolve poorly; high frequencies image finely but
  fade fast. This is the master tradeoff of all sonar design.
- **The sonar equation** — the [67-rf link budget](../engineering/03-rf-and-comms-systems.md)
  of the sea. For active sonar:
  $$ SNR = SL - 2\,TL + TS - (NL - DI) $$
  source level, two-way transmission loss, target strength, ambient noise, and
  array directivity index. You "close the sonar budget" exactly as you close a
  link or radar budget — and ambient noise (waves, biologics, shipping) is the
  floor you fight.

---

## 4. Perception — sonar is the camera of the deep

The [50-perception-deep](../autonomy/11-perception-deep.md) stack moves to
acoustics, with optical and other modalities filling short-range gaps.

- **Active sonar** transmits a ping and listens for echoes — ranging and imaging,
  but it announces your presence (bad for stealth). **Passive sonar** only
  listens — covert, and the heart of anti-submarine warfare, but it can't range a
  silent target directly.
- **Sonar types by job:**
  - **Side-scan sonar** — drags two fan beams to image the seafloor in strips
    (mine-hunting, wreck/pipeline survey). The workhorse of survey AUVs.
  - **Multibeam echosounder** — bathymetric mapping (3D seafloor).
  - **Forward-looking sonar (FLS)** — obstacle avoidance and navigation, the
    acoustic analog of a forward camera/LiDAR.
  - **Synthetic Aperture Sonar (SAS)** — the acoustic cousin of SAR radar
    ([60-lidar-radar](../autonomy/21-lidar-radar-processing.md)): synthesize a long
    array from motion to get range-independent, centimeter resolution. The current
    state of the art for mine detection.
- **Classification** is then a [59-computer-vision](../autonomy/20-computer-vision.md)
  / [20-ml-ai](../autonomy/01-ml-ai.md) problem on sonar imagery — detect, classify
  (mine vs. rock vs. clutter), and decide. Sonar imagery is noisy, low-resolution,
  and aspect-dependent, which makes the ML genuinely hard and the false-alarm
  management critical.

---

## 5. Navigation without GPS — the defining undersea problem

This is where maritime autonomy is *most* relevant to the rest of the repo: it is
[26-gnss-jamming-spoofing](../autonomy/07-gnss-jamming-spoofing.md) taken to its
limit — there is **no GPS at all**, ever, while submerged. The toolkit:

- **Inertial Navigation System (INS).** A high-grade IMU integrated forward gives
  position, but **drifts** without aiding (the dead-reckoning problem of
  [28-gnc](../autonomy/09-gnc.md)). Drift is the enemy.
- **Doppler Velocity Log (DVL).** Acoustic beams measure velocity relative to the
  seafloor (bottom-lock) or water. Fusing DVL velocity with the INS dramatically
  bounds drift — the single most important undersea nav aid. This is the
  [52-sensor-fusion](../autonomy/13-sensor-fusion.md) EKF with a velocity
  measurement instead of GPS.
- **Acoustic positioning** — fixed or surface references:
  - **LBL (Long Baseline)** — seafloor transponders, survey-grade accuracy in a
    fixed work area.
  - **USBL (Ultra-Short Baseline)** — a single ship-mounted array measures range
    and bearing to the vehicle; ship-relative positioning.
- **Terrain-aided navigation (TAN).** Match measured bathymetry against a known
  seafloor map to fix position — the undersea version of the terrain/visual map
  matching in [51-slam-and-mapping](../autonomy/12-slam-and-mapping.md) and
  exactly the technique that backs up GPS-denied flight.
- **Surfacing for a GPS fix** is the cheap reset — periodically pop up, get GPS,
  re-zero the INS — but it costs covertness and time. The whole nav design is a
  tradeoff between drift rate and how often you can afford to surface.

The mental model: **undersea navigation is a relentless fight against drift**,
won by fusing every available constraint (DVL, acoustic, terrain, occasional
surface fix) in the same Bayesian estimator you'd use in the air — just with GPS
permanently removed.

---

## 6. Decision-making at sea — currents, COLREGs, and the long horizon

The [29-planning-decision](../autonomy/10-planning-decision.md) and
[54-motion-planning](../autonomy/15-motion-planning.md) layers gain new
constraints:

- **Planning in a moving medium.** A path is planned *through water that is
  itself moving*. Energy-optimal routing exploits currents (gliders ride them);
  ignoring them wastes the entire energy budget. This is graph/trajectory
  optimization with a vector field overlaid.
- **COLREGs** (International Regulations for Preventing Collisions at Sea) are the
  legal-and-safety rules a USV **must** encode — give-way vs. stand-on vessel,
  crossing/overtaking/head-on geometry, and the requirement to act "in accordance
  with good seamanship." This is a rare case where the rules of the road are
  written law, and autonomous compliance is both a safety and a legal-acceptance
  problem (the [124-ethics-export-control](../career/20-ethics-export-control.md)
  and [09-safety-assurance](../foundations/09-safety-assurance.md) concern at sea).
- **Long-horizon autonomy.** A months-long glider mission or a multi-day AUV
  survey cannot phone home for decisions — the vehicle must handle faults, replan,
  and manage energy **on its own**, the strongest argument in the whole repo for
  genuine onboard autonomy over teleoperation.

---

## 7. Communication — talking through water

The [05-distributed_systems_comms_mesh](../foundations/05-distributed_systems_comms_mesh.md)
problem is brutal underwater because radio is dead:

- **Acoustic modems** are the only option for real range, and they are *terrible*
  by terrestrial standards: kilobits per second at best, latency of **seconds**
  (sound is slow), multipath-riddled, and easily disrupted. You design protocols
  assuming tiny, delayed, lossy messages — closer to deep-space comms than to
  Wi-Fi.
- **Optical** (blue-green laser) gives high bandwidth but only over short range
  and clear water — useful for docking and data offload, not command.
- **The architectural consequence:** undersea autonomy must be **highly
  autonomous** precisely because you cannot stream commands. Surface gateways
  (a USV or buoy) bridge the acoustic-to-radio seam, relaying terse status up to
  satellite and terse tasking down. The comms reality *forces* the autonomy.

---

## 8. The strategic picture — why navies are buying robots

- **Attritable mass at sea.** The same thesis as drones: many cheap, autonomous
  boats and undersea vehicles impose cost and risk on an adversary that a few
  exquisite manned ships cannot — the Navy's "hellscape," Saronic's pitch, the
  Replicator initiative. See
  [39-productized-defense](../companies/03-productized-defense.md) and
  [121-new-defense-tech-cohort](../companies/19-new-defense-tech-cohort.md).
- **The dull, dirty, dangerous missions** are the beachhead: mine countermeasures
  (don't send a sailor near a mine), seabed/cable survey and protection, persistent
  ISR, and anti-submarine search. Each is a perception + endurance problem an
  autonomous system does better and cheaper.
- **The undersea domain is contested and opaque.** Seabed infrastructure (cables,
  pipelines) is now a target; undersea domain awareness is the maritime cousin of
  the space domain awareness in
  [130-space-systems](../space/01-space-systems-and-astronautics.md). Whoever
  sees and operates in the deep holds an asymmetric advantage.

---

## Drills

1. **Sonar budget.** Pick a 100 kHz survey sonar; using the absorption term
   $\alpha$, estimate practical range, then drop to 10 kHz and explain the
   range/resolution flip.
2. **Drift budget.** For an AUV with a 0.1°/hr gyro and a DVL, estimate position
   drift over a 6-hour dive with and without DVL aiding. Decide how often it must
   surface for a GPS reset.
3. **SSP reasoning.** Sketch a summer thermocline sound-speed profile and mark the
   shadow zone a surface ship's sonar can't see into. Explain where a submarine
   would hide.
4. **COLREGs encoding.** Write the decision logic for a USV in a crossing
   situation with a give-way obligation. State what it does and why, and how you'd
   *prove* it safe ([09](../foundations/09-safety-assurance.md)).
5. **Comms-forced autonomy.** Given a 1 kbps, 4-second-latency acoustic link,
   redesign a tasking protocol for a 3-vehicle AUV team. Notice how little you can
   say and how much the vehicles must decide alone.

---

## Where this connects

- **Core loop, relocated:** GNC/estimation ([09](../autonomy/09-gnc.md)), sensor
  fusion ([13](../autonomy/13-sensor-fusion.md)), SLAM/terrain matching
  ([12](../autonomy/12-slam-and-mapping.md)), planning
  ([15](../autonomy/15-motion-planning.md)).
- **Physics:** signal processing ([05](../mathematics/05-signal-processing.md)),
  the GPS-denial limit ([07](../autonomy/07-gnss-jamming-spoofing.md)), the
  contested-domain framing of space
  ([01](../space/01-space-systems-and-astronautics.md)).
- **Strategy:** the defense cohort ([19](../companies/19-new-defense-tech-cohort.md)),
  productized/attritable defense ([03](../companies/03-productized-defense.md)),
  safety assurance at sea ([09](../foundations/09-safety-assurance.md)).

---

## ⚡ The Insider Layer — What the Field Knows but Rarely Writes Down

The air-and-ground autonomy world keeps wanting to treat the ocean as "the same stack, just wet." It isn't. Every cheap, fast assumption from the aerial domain inverts underwater, and the people who actually field marine systems live inside those inversions.

### Navigation is dead reckoning married to acoustics, and bottom-lock is sacred

Submerged, there is no GPS — so the entire game is bounding the drift of an inertial solution with whatever aiding you can get. The workhorse is the **Doppler Velocity Log (DVL)**: it pings the seafloor and measures velocity over ground, and a tightly-coupled INS+DVL with **bottom-lock** holds roughly $0.1\%$ of distance traveled. The dreaded transition is **losing bottom-lock** — go deeper than the DVL's range and you fall back to INS-only "water-mass" tracking, where drift balloons. Operationally you plan to **surface for a GPS fix** to reset the growing error, or you set acoustic beacons (LBL) or use a ship's **USBL** to get external position. The unwritten skill is *managing a drift budget over hours* — knowing how long you can stay down before the position is fiction.

### You cannot teleoperate underwater — the comms physics forbid it

Sound travels at ~1500 m/s, so a vehicle a kilometer away is a *second* of latency each way, and the channel carries **kilobits, not megabits**, with shallow-water multipath shredding even that. There is no live video, no joystick, no real-time intervention. This single fact makes **genuine autonomy mandatory** rather than optional: the vehicle must handle its own contingencies because help is, at best, a slow trickle of acoustic acknowledgements. Mission design centers on *disconnection as the default state* — you send compressed intent, the vehicle executes for hours, and you reconcile when it surfaces. Engineers from the drone world consistently underestimate how total this constraint is.

### Sonar is the camera, and the sonar equation is your detection budget

Light dies in meters; **sound is the sensing modality**. You trade the radar/LiDAR intuition for the **passive-vs-active dilemma**: active sonar gives you range and resolution but is a beacon announcing your presence; passive sonar is covert but only bears, not ranges. Detection is governed by the **sonar equation** ($SL - TL + TS - (NL - DI)$ versus a detection threshold) — the acoustic sibling of the radar equation, and the first thing a serious marine engineer learns to close. And the medium fights you: the **thermocline** bends sound rays (refraction by the vertical sound-speed gradient), creating **shadow zones** where a target below the layer is acoustically invisible to a sensor above it. Sound-speed profiles and ray tracing are not academic — they decide whether you detect the contact at all.

### Buoyancy and energy are existential, which is why everything is slow

An AUV that floods or loses buoyancy doesn't "land" — it is *gone*, beyond crush depth, unrecoverable. The pressure housing and its seals are the highest-consequence subsystem on the vehicle. And there is **no solar underwater**: battery is the entire energy economy, so vehicles cruise deliberately slow (a couple of knots) to conserve, and every watt of compute trades directly against endurance. The aerial reflex of "throw more sensors and compute at it" runs straight into a hard energy wall.

### Surface vessels live or die on COLREGs and a moving ground plane

For uncrewed surface vessels, the dominant hard problem isn't perception in the abstract — it's **legal-grade COLREGs compliance**: the system must give-way and stand-on like a crewed vessel, and *proving* that behavior to a classification society or the Coast Guard is a certification problem as much as an autonomy one. Add that the "ground plane" itself heaves with sea state, wakes confuse radar and vision, and salt spray fouls optics, and you have a domain where the rules of the road are a software requirement.

### The environment is a slow adversary, and recovery is the dangerous part

Nobody warns newcomers that **biofouling** — marine growth on the hull and sensor faces over weeks — and corrosion silently degrade the platform; a clean vehicle and a month-deployed vehicle are different machines. And the riskiest moment of most missions is not the autonomy at all — it's **launch and recovery** in sea state, where the vehicle and crew are most likely to be damaged. Field-time wisdom in marine autonomy is disproportionately about the boat, the deck, and the weather window, not the algorithm.
