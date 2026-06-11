# Quantum Technologies for Defense — Sensing, Computing, and Securing the Unhackable

> **Why this exists.** [26-gnss-jamming-spoofing](../autonomy/07-gnss-jamming-spoofing.md)
> ends on an honest, unsolved note: when GPS is denied, you fall back on inertial
> navigation that *drifts*. [87-cryptography-applied](../software/08-cryptography-applied.md)
> rests on math problems that a future computer might break. Both of these
> frontiers have the same answer, and this repository never covered it: **quantum
> technology**. Quantum sensing promises navigation with no GPS and no drift;
> quantum computing threatens to break today's cryptography; quantum communication
> promises physically unbreakable links. These are no longer physics curiosities —
> they are funded defense programs, and an engineer who can't separate the real
> physics from the hype is exposed on both the opportunity and the threat side.

> **What mastering it makes you.** The engineer who understands *what quantum
> mechanics actually buys you* — and what it doesn't — well enough to reason about
> a quantum inertial navigator for GPS-denied flight, to take the post-quantum
> cryptography migration seriously, and to call hype when a vendor oversells a
> noisy 100-qubit chip. The person who connects the GNSS-denial problem, the
> crypto problem, and the sensing problem to one body of physics.

This closes the open problems of [26-gnss](../autonomy/07-gnss-jamming-spoofing.md)
(GPS-denied nav), [87-cryptography](../software/08-cryptography-applied.md)
(post-quantum security), and [74-sensors](../engineering/10-sensors-and-instrumentation.md)
(next-generation sensing), grounded in the physics of
[Physics for Engineers](../mathematics/08-physics-for-engineers.md) and the
information theory of [100-information-theory](../mathematics/06-information-theory.md).

---

## 1. The three quantum properties you actually need

You don't need the full formalism to reason about quantum tech as an engineer.
Three properties do almost all the work:

- **Superposition.** A quantum system (a **qubit**) can be in a combination of
  states at once — $\alpha|0\rangle + \beta|1\rangle$ — until measured. This is
  what lets a quantum computer explore many possibilities in parallel, and what
  makes certain sensors exquisitely responsive to their environment.
- **Entanglement.** Two systems can share a joint state such that measuring one
  instantly constrains the other, no matter the distance. "Spooky," but real, and
  the basis of quantum communication's security and of sensing schemes that beat
  the classical noise limit.
- **Measurement collapse.** Observing a quantum system *changes* it — you can't
  copy an unknown quantum state (the **no-cloning theorem**) and you can't measure
  it without disturbing it. This is a *weakness* for building hardware (decoherence,
  §5) but a *superpower* for security: an eavesdropper unavoidably leaves a
  fingerprint (§4).

Every defense application below is one of these three turned into an engineering
advantage.

---

## 2. Quantum sensing — the most mature and the most relevant

This is the quietest and most important quantum field for autonomy, because it
attacks the exact problem [26-gnss](../autonomy/07-gnss-jamming-spoofing.md) leaves
open: **how do you navigate when the sky lies?** The mechanism is that quantum
systems make superb sensors — atoms are identical, stable references, and
superposition makes them extraordinarily sensitive to acceleration, rotation,
time, and fields.

- **Quantum inertial navigation (cold-atom accelerometers & gyroscopes).** Atom
  interferometry measures acceleration and rotation against the immutable
  properties of atoms, with **drift orders of magnitude lower** than the
  mechanical/optical IMUs of [28-gnc](../autonomy/09-gnc.md). A navigation-grade
  quantum INS could dead-reckon for hours or days with little drift — **GPS-denied
  navigation that actually holds**, the holy grail for the
  [07](../autonomy/07-gnss-jamming-spoofing.md) and
  [131-maritime](../autonomy/26-maritime-and-undersea-autonomy.md) problems (a
  submarine that never surfaces for a fix).
- **Quantum clocks.** Atomic-clock precision drives GNSS itself; chip-scale quantum
  clocks let a platform **hold precise time without GPS**, preserving timing-based
  navigation and secure comms when the satellite signal is gone.
- **Quantum magnetometry & gravimetry.** Ultra-sensitive magnetic and gravity
  sensors enable **map-matching navigation** — match measured local magnetic or
  gravity anomalies against a stored map to fix position with no emissions at all
  (the terrain-aided-nav idea of
  [51-slam](../autonomy/12-slam-and-mapping.md)/[131-maritime](../autonomy/26-maritime-and-undersea-autonomy.md),
  using fields instead of terrain). Also enables detection of submarines and buried
  objects.
- **Why it's first:** sensing tolerates noise far better than computing does — you
  need a sensitive quantum system, not a fault-tolerant *computer* — so quantum
  sensing is closest to fielding. This is the quantum payoff an autonomy engineer
  should track most closely.

---

## 3. Quantum computing — the real threat and the narrower promise

Quantum computers use superposition and entanglement to attack certain problems,
but the engineering reality is sober: today's machines are **NISQ** (Noisy
Intermediate-Scale Quantum) — tens to hundreds of error-prone qubits, far from the
**fault-tolerant** machines the famous algorithms require.

- **The genuine threat — Shor's algorithm.** A large, fault-tolerant quantum
  computer could factor large numbers and solve discrete logs efficiently, which
  **breaks RSA and elliptic-curve cryptography** — the public-key foundation of
  [87-cryptography-applied](../software/08-cryptography-applied.md) and essentially
  all secure communication today. This is not hypothetical enough to ignore (§4).
- **The narrower promise — Grover's algorithm** gives a quadratic speedup for
  unstructured search (it *halves* effective symmetric-key strength — defended by
  doubling key size, not catastrophic), and **quantum simulation** genuinely helps
  chemistry and materials (batteries
  [15](../engineering/15-batteries-and-energy-storage.md), new materials
  [07](../engineering/07-structures-and-materials.md)) — likely the first real
  economic payoff.
- **The honest engineering picture.** Qubits **decohere** — they lose their quantum
  state to environmental noise in microseconds to milliseconds — so you need
  **quantum error correction**, which costs hundreds to thousands of physical
  qubits per usable *logical* qubit. A cryptographically relevant machine is a
  millions-of-physical-qubit engineering problem. Treat any "we have N qubits"
  claim by asking: physical or logical? error rate? coherence time? Those three
  numbers separate signal from hype.

---

## 4. The crypto reckoning — "harvest now, decrypt later"

The quantum-computing threat changes [87-cryptography](../software/08-cryptography-applied.md)
**today**, even before a quantum computer exists, because of one adversary
strategy:

- **Harvest now, decrypt later.** An adversary records your encrypted traffic now
  and stores it, betting that a quantum computer will decrypt it in 10–20 years.
  Anything that must stay secret that long (intelligence, weapons design, identity
  keys) is **already at risk**. This is why the migration is urgent, not
  futuristic.
- **Post-Quantum Cryptography (PQC).** The defense is *not* exotic quantum hardware
  — it's **new classical algorithms** based on math problems (lattices, hashes,
  codes) believed hard even for quantum computers. NIST has standardized the first
  set (ML-KEM/Kyber for key exchange, ML-DSA/Dilithium and SPHINCS+ for
  signatures). The work is a massive, unglamorous **migration** of every protocol,
  certificate, and device — **crypto-agility** is the engineering goal: build
  systems that can swap algorithms without a redesign. This is a near-term,
  fundable, do-it-now task for the software bands
  ([07](../software/07-cybersecurity-engineering.md),
  [08](../software/08-cryptography-applied.md)).
- **Quantum Key Distribution (QKD)** is the *other* defense — using measurement
  collapse (§1) so any eavesdropper is detected — but it needs special hardware and
  links, and most defense planners treat **PQC as the practical answer** and QKD as
  a niche for the highest-assurance links. Knowing the difference (PQC = new math on
  normal computers; QKD = new physics on special hardware) is the mark of someone
  who actually understands the field.

---

## 5. Quantum communication & networking — the long game

The third pillar uses entanglement and no-cloning to build links whose security
rests on **physics, not on the assumed hardness of a math problem**.

- **QKD** distributes encryption keys with eavesdrop detection guaranteed by
  quantum mechanics — provably secure key exchange, at the cost of range
  (fiber loss) and hardware. Satellite QKD
  ([130-space-systems](../space/01-space-systems-and-astronautics.md)) extends the
  range; China's Micius satellite demonstrated it.
- **Quantum repeaters & the quantum internet** aim to entangle nodes across long
  distances — early-stage research, but the long-term vision of distributed quantum
  sensing and computing.
- **Engineering reality:** range, cost, and integration keep this niche for now.
  The defensible takeaway: quantum comms is a **specialized, high-assurance tool**,
  not a replacement for the resilient classical mesh of
  [05-distributed_systems_comms_mesh](../foundations/05-distributed_systems_comms_mesh.md)
  and PQC.

---

## 6. The engineer's bottom line — what to believe and what to do

Quantum is real but unevenly mature; calibrate your attention accordingly:

- **Track quantum *sensing* hardest** — it directly solves the GPS-denied
  navigation problem ([07](../autonomy/07-gnss-jamming-spoofing.md),
  [26](../autonomy/26-maritime-and-undersea-autonomy.md)) that limits real
  autonomy, and it's closest to fielding because it tolerates noise.
- **Act on PQC now** — the "harvest now, decrypt later" threat makes
  crypto-agility a present-day requirement
  ([07](../software/07-cybersecurity-engineering.md),
  [08](../software/08-cryptography-applied.md)), not a future one.
- **Be sober about quantum *computing*** — transformative *if* fault tolerance is
  achieved, but that's a long, hard road; interrogate every qubit claim
  (physical vs. logical, error rate, coherence).
- **The asymmetry to remember:** the defensive move (PQC, quantum sensing) is
  available to a small, sharp team *today*; the offensive move (a cryptographically
  relevant quantum computer) is a nation-state, decade-scale effort. That asymmetry
  — defenders can adopt cheaply, attackers must build something enormous — is the
  strategic shape of the whole field, and it's good news for the
  [47-asymmetric-playbook](../companies/11-startup-asymmetric-playbook.md) builder.

---

## Drills

1. **Navigation payoff.** Compare the drift of a tactical-grade IMU
   ([09](../autonomy/09-gnc.md)) over 6 hours with a notional quantum INS two
   orders of magnitude better. Decide what missions that unlocks for
   [07](../autonomy/07-gnss-jamming-spoofing.md) and
   [26](../autonomy/26-maritime-and-undersea-autonomy.md).
2. **Hype filter.** A vendor announces a "256-qubit quantum computer." List the
   three questions you ask before believing it threatens RSA.
3. **PQC migration.** For a system using RSA/ECC today
   ([08](../software/08-cryptography-applied.md)), sketch the steps to crypto-agility
   and which data is most exposed to "harvest now, decrypt later."
4. **Sensing vs. computing.** Explain in two sentences why quantum *sensing* is
   fieldable before quantum *computing* (hint: noise tolerance and error
   correction).
5. **PQC vs. QKD.** State the difference in one line each, and pick which you'd
   deploy across a drone fleet's links and why.

---

## Where this connects

- **Solves open problems:** GPS-denied nav ([07](../autonomy/07-gnss-jamming-spoofing.md)),
  undersea nav ([26](../autonomy/26-maritime-and-undersea-autonomy.md)),
  next-gen sensing ([10](../engineering/10-sensors-and-instrumentation.md)),
  GNC drift ([09](../autonomy/09-gnc.md)).
- **The security reckoning:** cryptography
  ([08](../software/08-cryptography-applied.md)), cybersecurity
  ([07](../software/07-cybersecurity-engineering.md)), resilient comms
  ([05](../foundations/05-distributed_systems_comms_mesh.md)).
- **Physics & strategy:** physics ([08](../mathematics/08-physics-for-engineers.md)),
  information theory ([06](../mathematics/06-information-theory.md)), satellite
  links ([01](../space/01-space-systems-and-astronautics.md)), the asymmetric
  builder's playbook ([11](../companies/11-startup-asymmetric-playbook.md)).
