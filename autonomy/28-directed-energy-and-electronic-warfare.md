# Directed Energy & Electronic Warfare — Fighting at the Speed of Light and in the Spectrum

> **Why this exists.** [27-counter-uas-ew](08-counter-uas-ew.md) introduces the
> counter-drone fight and touches electronic warfare; [26-gnss-jamming-spoofing](07-gnss-jamming-spoofing.md)
> covers one slice of it. But two enormous, fast-moving domains were never given
> their own treatment: **directed-energy weapons** (lasers and high-power
> microwave — the leading answer to cheap drone swarms) and **the full electronic
> warfare / electromagnetic spectrum operations** picture that every modern sensor,
> radio, and weapon in this repo lives inside. If you build autonomy that emits or
> receives anything — radar, GPS, datalink, comms
> ([03](../engineering/03-rf-and-comms-systems.md),
> [05](../foundations/05-distributed_systems_comms_mesh.md)) — you are operating in
> contested spectrum whether you planned for it or not.

> **What mastering it makes you.** The engineer who understands why a laser is the
> economically inevitable counter to a $500 drone, can reason about beam quality,
> dwell time, and atmospheric propagation, and can place any system in the
> electromagnetic spectrum fight — detect, deny, deceive, destroy — on both the
> offensive and the defensive side. The person who designs systems that *survive*
> in contested spectrum instead of assuming a clean one.

This is the [104-electromagnetics](../mathematics/10-electromagnetics.md) and
[99-signal-processing](../mathematics/05-signal-processing.md) physics turned into
weapons and countermeasures, the defensive complement to
[27-counter-uas-ew](08-counter-uas-ew.md), and the offensive-spectrum context for
[26-gnss](07-gnss-jamming-spoofing.md) and the whole comms stack.

---

## 1. Two families of directed energy

**Directed-energy weapons (DEW)** put energy on a target at the speed of light, in
a straight line, with a "magazine" limited only by power — the structural answer
to the cost-asymmetry problem that cheap drones impose
([47-startup-asymmetric-playbook](../companies/11-startup-asymmetric-playbook.md),
[132-missiles](27-missiles-guided-munitions-hypersonics.md)). Two physically
different families:

- **High-Energy Laser (HEL).** A tightly focused beam of light that deposits heat
  on one point until something fails — burns through a structure, cooks a seeker,
  detonates ordnance. **Precise** (one target at a time, surgical aimpoint) but
  needs **dwell time** on a small spot and is degraded by weather.
- **High-Power Microwave (HPM).** A broad pulse of RF energy that **fries
  electronics** across an area — it doesn't burn a hole, it induces destructive
  currents in circuits. **Area effect** (kills a whole swarm in the beam at once),
  weather-robust, but indiscriminate and shorter-ranged. (CHAMP, Leonidas, THOR
  are public examples.)

```
 HEL  ─ pencil beam, melts/burns ONE target, needs dwell, hates clouds
 HPM  ─ wide pulse, fries ALL electronics in the cone at once, weatherproof
```

The strategic point: against a swarm of cheap attritable drones, firing a
million-dollar interceptor at each is a losing trade. A laser's cost-per-shot is
**the price of the electricity** — a few dollars — and HPM kills many at once.
This is *the* reason DEW went from lab curiosity to procurement priority.

---

## 2. Why lasers are hard — the physics that limits them

A laser weapon is an exercise in [104-electromagnetics](../mathematics/10-electromagnetics.md),
optics, and thermal management ([08](../engineering/08-thermal-management.md)),
and the difficulties are all physical, not political:

- **Diffraction sets the spot size.** A beam of wavelength $\lambda$ from an
  aperture of diameter $D$ spreads to a spot of angular radius $\sim\lambda/D$. At
  range $R$ the spot diameter is roughly:
  $$ d_{spot} \approx \frac{2.44\,\lambda R}{D} $$
  So you want **short wavelength and a big, high-quality aperture** to keep energy
  concentrated. Bigger beam director, tighter spot, faster kill.
- **Power on target, not power out.** Lethality is **irradiance × dwell time** —
  you must hold the spot on the same point on a moving, possibly spinning target
  long enough to deposit killing energy. That makes **fine beam pointing and
  tracking** (the [28-gnc](09-gnc.md) control loop at microradian precision) the
  hardest subsystem, not the laser itself.
- **The atmosphere fights you.** Three effects degrade the beam:
  - **Absorption/scattering** — clouds, fog, rain, dust attenuate the beam
    (laser's main weakness).
  - **Turbulence** — refractive-index variations smear and wander the spot,
    fought with **adaptive optics** (a deformable mirror that pre-distorts the
    beam, the same idea astronomers use).
  - **Thermal blooming** — the beam heats the air it passes through, defocusing
    itself; worse at higher power. A nonlinear ceiling on brute force.
- **Beam quality ($M^2$).** A real beam is worse than an ideal one; the figure of
  merit $M^2$ (1.0 = perfect) folds into the spot-size budget. **Fiber and slab
  solid-state lasers** combined ("spectral beam combining") are how modern systems
  reach hundreds of kilowatts.

The design loop is therefore: maximize power *and* beam quality *and* aperture
*and* pointing precision, while the atmosphere caps your effective range.

---

## 3. High-power microwave — the swarm killer

HPM trades the laser's precision for breadth:

- **Mechanism:** a high-power RF pulse couples into a target's electronics through
  any aperture (antenna, seam, cable) and induces voltages that **upset (soft
  kill)** or **destroy (hard kill)** the circuitry — the destructive cousin of the
  signal-integrity and EMC concerns in
  [78-pcb-and-electronics-design](../engineering/14-pcb-and-electronics-design.md).
- **Effects ladder:** deny/disrupt (temporary) → degrade → damage (permanent),
  depending on coupled energy. Front-door (through the antenna) vs. back-door
  (through seams) coupling determines hardening strategy.
- **The defense is EMC hardening:** shielding, filtering, transient suppression,
  and Faraday-cage design — exactly the discipline that protects *your* autonomy
  electronics. Understanding HPM is understanding how to harden against it.
- **Use case:** counter-swarm and counter-electronics — disable many drones, or a
  vehicle's engine control, in a single pulse, where a laser would have to service
  each target serially.

---

## 4. The electromagnetic spectrum — the battlespace everything shares

Step back: lasers, radar, GPS, datalinks, comms, and HPM all live in the
**electromagnetic spectrum**, and modern doctrine treats the spectrum itself as a
**maneuver space** ("electromagnetic spectrum operations," EMSO). Every emitter in
this repo is both a capability and a vulnerability. The classical EW triad:

- **Electronic Support (ES)** — *listen*. Detect, identify, and locate emitters
  (SIGINT/ELINT). This is the [99-signal-processing](../mathematics/05-signal-processing.md)
  and [52-sensor-fusion](13-sensor-fusion.md) problem of finding signals in noise
  and geolocating them. ES feeds everything else — you can't jam or kill what you
  can't find.
- **Electronic Attack (EA)** — *deny/deceive/destroy*. Jamming (raise the noise
  floor, as in [26-gnss](07-gnss-jamming-spoofing.md)), spoofing/deception (DRFM
  repeaters that feed a radar false targets), and directed energy (§1–3).
- **Electronic Protection (EP)** — *survive*. Make your own emitters resilient:
  frequency hopping, spread spectrum, LPI/LPD waveforms (low probability of
  intercept/detection), nulling antennas (CRPA from
  [26-gnss](07-gnss-jamming-spoofing.md)), and emission control (EMCON — sometimes
  the best protection is to **not transmit**).

```
        ES (listen/locate) ──► targeting
              │
        EA (jam/spoof/burn) ◄──► EP (hop/spread/null/stay quiet)
              the move and counter-move of the spectrum fight
```

---

## 5. Cognitive & adaptive EW — where this becomes an autonomy problem

The spectrum fight has become too fast and too crowded for fixed jammers and
hand-tuned waveforms, which is precisely where the rest of this repo re-enters:

- **Cognitive EW** uses [20-ml-ai](01-ml-ai.md) and
  [56-reinforcement-learning](17-reinforcement-learning.md) to **sense an unknown
  emitter, classify it, and synthesize a countermeasure in real time** — learning
  the adversary's waveform on the fly instead of relying on a pre-loaded threat
  library. It is online perception + decision under adversarial uncertainty, the
  [29-planning-decision](10-planning-decision.md) loop in the spectrum.
- **Adaptive radar/comms** hop, shape, and null dynamically to stay one move ahead
  — a [105-game-theory](../mathematics/11-decision-and-game-theory.md) pursuit in
  frequency, time, and space.
- **Spectrum situational awareness** is a sensor-fusion and SDA-like cataloguing
  problem ([13](13-sensor-fusion.md)) — know every emitter in the battlespace,
  including your own, and manage interference (deconfliction) so your systems don't
  jam each other.
- **The design imperative for your autonomy:** assume contested spectrum. Build
  GPS-denied navigation ([07](07-gnss-jamming-spoofing.md),
  [135-quantum](../engineering/16-quantum-technologies.md)), resilient mesh comms
  ([05](../foundations/05-distributed_systems_comms_mesh.md)), and graceful
  degradation ([09-safety-assurance](../foundations/09-safety-assurance.md)) as
  first-class requirements, not afterthoughts.

---

## 6. The systems & strategy picture

- **Layered air/drone defense.** No single effector wins. The mature architecture
  layers **EW (cheapest, soft-kill jamming) → HPM (counter-swarm) → HEL (precise
  hard-kill) → kinetic interceptors/guns (the expensive backstop)** — graduated
  response matched to threat value, the counter to the cost-asymmetry of cheap
  drones in [27-counter-uas-ew](08-counter-uas-ew.md) and
  [132-missiles](27-missiles-guided-munitions-hypersonics.md).
- **Power and platform are the real constraints.** A laser needs hundreds of
  kilowatts of clean, pulsed power and brutal thermal management — the
  [68-power-electronics](../engineering/04-power-electronics.md),
  [79-batteries](../engineering/15-batteries-and-energy-storage.md), and
  [72-thermal](../engineering/08-thermal-management.md) problem decides whether a
  DEW fits on a truck, a ship, or never leaves the lab. **Magazine depth = power
  generation.**
- **The asymmetry that makes DEW strategic.** Cost-per-shot collapses from
  $millions (interceptor missile) to dollars (electricity). Against mass-produced
  attritable threats, that flips the economics back in the defender's favor — the
  single most important reason DEW is a budget priority and a career field.
- **Spectrum dominance is a precondition for everything else.** ISR, precision
  weapons ([27](27-missiles-guided-munitions-hypersonics.md)), networked
  autonomy, and space ([01](../space/01-space-systems-and-astronautics.md)) all
  assume the spectrum works. Whoever controls the spectrum controls whether the
  other side's autonomy functions at all.

---

## Drills

1. **Spot-size budget.** For a 1 µm laser with a 0.5 m aperture at 5 km, estimate
   the diffraction-limited spot diameter. Halve the wavelength and double the
   aperture; explain the lethality change.
2. **Laser vs. HPM selection.** For (a) a single fixed-wing UAS at 4 km in clear
   air and (b) a 30-drone swarm at 800 m, pick HEL or HPM and justify on dwell,
   weather, and cost-per-kill.
3. **EW triad.** For your own drone's datalink, identify the ES, EA, and EP
   considerations: how is it detected, how is it attacked, and how do you protect
   it (hop/spread/EMCON)?
4. **Power reality.** Estimate the prime power and cooling a 100 kW laser needs at
   ~20% wall-plug efficiency. Decide which platforms can host it.
5. **Cognitive EW.** Sketch an RL formulation for adapting a jamming waveform
   against an unknown, hopping radar: state, action, reward. Tie it to
   [17](17-reinforcement-learning.md).

---

## Where this connects

- **Physics:** electromagnetics ([10](../mathematics/10-electromagnetics.md)),
  signal processing ([05](../mathematics/05-signal-processing.md)), RF/comms
  ([03](../engineering/03-rf-and-comms-systems.md)), power/thermal
  ([04](../engineering/04-power-electronics.md),
  [08](../engineering/08-thermal-management.md)).
- **The fight:** counter-UAS ([08](08-counter-uas-ew.md)), GNSS denial
  ([07](07-gnss-jamming-spoofing.md)), missiles & seekers
  ([27](27-missiles-guided-munitions-hypersonics.md)), resilient comms
  ([05](../foundations/05-distributed_systems_comms_mesh.md)).
- **Autonomy & strategy:** cognitive EW via ML/RL ([01](01-ml-ai.md),
  [17](17-reinforcement-learning.md)), game theory
  ([11](../mathematics/11-decision-and-game-theory.md)), the asymmetric playbook
  ([11](../companies/11-startup-asymmetric-playbook.md)), space spectrum
  ([01](../space/01-space-systems-and-astronautics.md)).
