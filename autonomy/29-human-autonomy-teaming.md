# Human-Autonomy Teaming & Human Factors — The Operator Is Part of the System

> **Why this exists.** This repository teaches you to build autonomy — perception,
> estimation, planning, control. But almost no fielded autonomous system is fully
> autonomous; it is **operated, supervised, trusted, and overridden by humans**,
> and the seam between the human and the machine is where most real systems
> actually fail. A drone that flies perfectly but presents a confusing interface,
> erodes the operator's trust, or hands off control at the wrong moment will be
> rejected in the field no matter how good its algorithms are. The entire
> [09-safety-assurance](../foundations/09-safety-assurance.md) argument, the
> [29-planning-decision](../autonomy/10-planning-decision.md) authority question,
> and the [124-ethics-export-control](../career/20-ethics-export-control.md)
> accountability problem all live at this seam — and this repo had no guide on it.

> **What mastering it makes you.** The engineer who designs the *whole* system —
> machine plus human — instead of throwing an interface over a finished
> autonomy stack. The person who can reason about levels of autonomy, calibrate
> trust, manage operator workload and mode confusion, and place the human at the
> right point in the loop for each decision. The skill that turns a demo into a
> deployed, accepted, certifiable system.

This is the human-side complement to the decision layer
([29-planning-decision](../autonomy/10-planning-decision.md)), the safety case
([09-safety-assurance](../foundations/09-safety-assurance.md)), the technical
communication of [116-technical-communication](../career/12-technical-communication.md),
and the cognition of [33-cognitive-bias](../information-environment/03-cognitive-bias-attention-and-narratives.md).

---

## 1. The core idea — the human and the machine are one system

The mistake naïve engineers make is to optimize the autonomy in isolation and
treat the human as an afterthought ("we'll add a UI later"). The correct frame,
from human-factors engineering, is that **the joint human-machine system** is what
you are designing and what you must make safe and effective. The autonomy doesn't
replace the human; it **redistributes the work**, and bad redistribution creates
new failure modes that didn't exist before automation.

The classic warning is the **"ironies of automation"** (Bainbridge, 1983): the
more you automate, the more the human's remaining job becomes *monitoring* — the
one task humans are worst at — and the harder it becomes for them to step in when
the automation fails, because they've lost situational awareness and hands-on
skill. Automation that handles the easy 95% and dumps the hard 5% on an
out-of-the-loop human at the worst moment is a trap, and it is the root cause of
many automation-related accidents.

---

## 2. Levels of autonomy — the spectrum, not a switch

Autonomy is not binary; it is a spectrum of **who decides and who acts**. Several
taxonomies exist; the durable mental model is the Sheridan-Verplank scale and its
defense shorthand:

- **In-the-loop** — the human makes every decision; the machine executes
  (teleoperation). Maximum control, minimum scale, brittle to latency
  ([131-maritime](../autonomy/26-maritime-and-undersea-autonomy.md) shows why this
  fails undersea).
- **On-the-loop** — the machine decides and acts, the human **monitors and can
  veto/override**. The dominant model for supervised autonomy and armed systems.
- **Out-of-the-loop / full autonomy** — the machine decides and acts within
  delegated authority; the human sets intent and boundaries beforehand. Necessary
  when comms are denied or timelines are too fast for a human
  ([132-missiles](../autonomy/27-missiles-guided-munitions-hypersonics.md),
  [133-directed-energy](../autonomy/28-directed-energy-and-electronic-warfare.md)).

The engineering decision is **not "how autonomous can we make it"** but **"what is
the right level for *this decision, in this context*?"** A single mission mixes
levels — autonomous navigation, on-the-loop targeting, in-the-loop for a
weapons-release decision. **Adjustable / sliding autonomy** — the ability to move
along this spectrum as the situation, trust, and comms change — is the modern goal.

---

## 3. Trust — the currency of the relationship

A system is only as useful as the operator's willingness to rely on it, and trust
is a measurable, dynamic quantity with two failure modes:

- **Undertrust (disuse).** The operator doesn't believe the autonomy, so they
  override it, babysit it, or turn it off — and you've gained nothing. Common after
  a single visible failure, because trust drops fast and rebuilds slowly.
- **Overtrust (misuse / automation complacency).** The operator believes the
  autonomy *too much*, stops monitoring, and follows it into a failure it wasn't
  designed to handle — the GPS-into-a-lake problem, the Tesla-autopilot-inattention
  problem. This is the dangerous one because it's invisible until it kills.

The goal is **calibrated trust** — reliance that matches the system's *actual*
reliability, context by context. Calibration is an engineering deliverable, not a
personality trait of the operator. You build it with:

- **Transparency** — the system communicates *what it's doing, why, and how
  confident it is* (§4).
- **Predictability** — it behaves consistently, so the operator can form an
  accurate mental model.
- **Honest competence boundaries** — the system signals when it's leaving its
  reliable envelope (low confidence, out-of-distribution input from
  [62-sim-to-real](../autonomy/23-sim-to-real.md)) *before* it fails, not after.

---

## 4. Transparency & explainability — letting the human see the machine's mind

Calibrated trust requires the human to understand the autonomy's state and intent.
This is where [20-ml-ai](../autonomy/01-ml-ai.md) meets human factors: a black-box
model that's right 99% of the time but can't say *why* or *how sure* is hard to
trust correctly.

- **Communicate uncertainty.** Surface calibrated confidence
  ([117-applied-statistics](../foundations/12-applied-statistics-and-causal-inference.md))
  — "I am 60% sure this is the target" — so the human can weight their own judgment.
  A confident wrong answer is far more dangerous than an honest uncertain one.
- **Communicate intent.** Show the *plan*, not just the current action — where the
  vehicle intends to go and why — so the operator can intervene early, while there's
  still time, instead of reacting to a surprise.
- **Right-size the explanation.** Too little information breeds undertrust and mode
  confusion; too much causes information overload and the operator tunes it out.
  The art is conveying the *decision-relevant* state at the *decision-relevant*
  moment — the [116-technical-communication](../career/12-technical-communication.md)
  discipline applied to a real-time interface.

---

## 5. The classic failure modes you must design against

Decades of human-factors research (much of it written in aviation accident blood)
name the recurring failures. Designing against them is the job.

- **Mode confusion.** The human thinks the system is in one mode; it's in another
  ("what is it doing now? why won't it...?"). A leading cause of automation
  accidents. Defense: make the active mode and authority *unmistakable* at all
  times.
- **Automation surprise.** The autonomy does something the operator didn't expect
  and can't explain — destroys trust instantly. Defense: predictability and
  intent transparency (§4).
- **Loss of situational awareness (SA).** Endsley's three levels — *perceive* the
  elements, *comprehend* the situation, *project* the future. Automation that keeps
  the human out of the loop erodes all three, so when control is handed back, the
  human is behind the aircraft. Defense: keep the human informed even while not
  acting.
- **Workload extremes.** Both **overload** (too many vehicles/alerts at once — the
  span-of-control problem in [58-multi-agent-swarm](../autonomy/19-multi-agent-swarm.md))
  and **underload** (passive monitoring → vigilance decrement, boredom, missed
  signals) degrade performance. Aim for the sustainable middle.
- **Alarm fatigue.** Too many false alarms and the operator ignores all of them,
  including the real one. Tune false-alarm rates ([12](../foundations/12-applied-statistics-and-causal-inference.md))
  as a human-factors requirement, not just a detection-performance number.
- **The handoff problem.** Transferring control between human and machine
  (especially machine→human in an emergency) is the most dangerous moment in the
  whole interaction — the human needs time and SA they often don't have. Design
  handoffs explicitly, with lead time and context, or avoid them.

---

## 6. Designing the interface — the operator's window into the system

The HMI is not decoration; it is the [09-safety-assurance](../foundations/09-safety-assurance.md)
control surface and often the difference between acceptance and rejection.

- **Show state, intent, and confidence** (§4), at a glance, with the most critical
  information most salient — the discipline of signal-vs-noise from
  [116-technical-communication](../career/12-technical-communication.md).
- **Make the safe action easy and the dangerous action hard.** Affordances,
  confirmations on irreversible actions ([27](../autonomy/27-missiles-guided-munitions-hypersonics.md)
  weapons release), and graceful degradation paths
  ([09](../foundations/09-safety-assurance.md)).
- **Design for the degraded case, not the demo.** Real operation is at night,
  under stress, with intermittent comms, by a tired operator managing several
  vehicles. The interface must work *then*, not just in the showroom — the
  realistic-conditions discipline of [62-sim-to-real](../autonomy/23-sim-to-real.md).
- **Single operator, many vehicles.** Scaling one human across a swarm
  ([58-multi-agent-swarm](../autonomy/19-multi-agent-swarm.md)) flips the design
  from per-vehicle piloting to **management-by-exception** — the human supervises
  intent and only touches the vehicles that need attention. This is the only way
  the attritable-mass thesis of
  [121-new-defense-tech-cohort](../companies/19-new-defense-tech-cohort.md) and
  [131-maritime](../autonomy/26-maritime-and-undersea-autonomy.md) actually works.

---

## 7. Accountability, ethics & the meaningful-human-control debate

The human-machine seam is also where moral and legal responsibility lives, which
ties this guide directly to [124-ethics-export-control](../career/20-ethics-export-control.md)
and [121-ethics-of-force](../foundations/16-ethics-of-force-and-engineering-responsibility.md).

- **Meaningful human control.** For consequential actions — especially the use of
  force ([132-missiles](../autonomy/27-missiles-guided-munitions-hypersonics.md)) —
  doctrine and ethics demand that a human retain genuine, informed authority, not a
  rubber-stamp "consent" button on a decision they can't actually evaluate in the
  time given. Designing *real* (not theatrical) human control is an engineering
  problem: the human needs the information, the time, and the authority to truly
  decide.
- **The accountability gap.** When a joint human-machine system fails, who is
  responsible — the operator, the engineer, the commander? Clear authority and
  good records (the logging discipline of
  [09-safety-assurance](../foundations/09-safety-assurance.md)) are how you keep the
  gap from swallowing accountability.
- **Automation bias as an ethical hazard.** If the interface nudges an overloaded
  human to defer to the machine ("the computer says it's a valid target"), you have
  engineered away the human control you claimed to preserve. The interface's job is
  to *enable* genuine judgment, not to manufacture compliance — the honest-influence
  posture of [111-psychological-manipulation-defense](../mindset-and-society/01-psychological-manipulation-defense.md).

---

## Drills

1. **Pick the level.** For a strike drone's (a) navigation, (b) target
   identification, and (c) weapons release, choose in/on/out-of-the-loop and
   justify each against comms, timeline, and ethics
   ([20](../career/20-ethics-export-control.md)).
2. **Trust calibration.** Your detector is 95% reliable in clear weather, 60% in
   fog. Design how the interface communicates this so the operator's reliance
   tracks the truth in each condition.
3. **Mode-confusion audit.** Take any autonomy mode-switch in this repo's stack and
   write how the operator always knows the current mode and authority.
4. **Span of control.** One operator, twelve drones
   ([19](../autonomy/19-multi-agent-swarm.md)). Design the management-by-exception
   interface: what's shown always, what's shown only on exception, what requires a
   human touch.
5. **Handoff.** Design a machine→human emergency handoff that gives the operator
   the situational awareness and lead time to actually take over. State the minimum
   warning time and why.

---

## Where this connects

- **The decision & safety spine:** planning/decision authority
  ([10](../autonomy/10-planning-decision.md)), safety assurance & logging
  ([09](../foundations/09-safety-assurance.md)), swarm span-of-control
  ([19](../autonomy/19-multi-agent-swarm.md)).
- **Cognition & communication:** human bias and SA
  ([03](../information-environment/03-cognitive-bias-attention-and-narratives.md)),
  technical communication ([12](../career/12-technical-communication.md)),
  calibrated uncertainty ([12](../foundations/12-applied-statistics-and-causal-inference.md)).
- **Ethics & the sharp end:** ethics/ITAR
  ([20](../career/20-ethics-export-control.md)), ethics of force
  ([16](../foundations/16-ethics-of-force-and-engineering-responsibility.md)),
  weapons authority ([27](../autonomy/27-missiles-guided-munitions-hypersonics.md)),
  honest influence
  ([01](../mindset-and-society/01-psychological-manipulation-defense.md)).

---

## ⚡ The Insider Layer — What the Field Knows but Rarely Writes Down

The human-factors textbooks give you taxonomies and acronyms. What they underplay is that almost every one of those neat models has a *paradox* baked into it, and the paradoxes are where fielded systems actually break.

### Levels of autonomy are a per-task fiction sold as a global dial

The Sheridan-Verplank ten-level scale and SAE's L0–L5 are taught as if a system *has* a level. The practitioner truth is that **autonomy is task-and-context-specific**: the same drone is fully autonomous for attitude stabilization, supervised for navigation, and human-authorized for weapons release — all at once. Designing to a single global "level" produces interfaces that are wrong for most of the tasks they cover. The mature framing is **adjustable/adaptive autonomy**: the right authority allocation per function, per phase, per risk — and the hard part is making the *transitions* between them legible to the human.

### The irony of automation: reliability is what disarms the human

Lisanne Bainbridge named it in 1983 and it has aged perfectly: **the better the automation, the worse the human is positioned to take over.** A system that handles 99.9% of cases trains its operator to stop paying attention, lose manual skill, and lose situational awareness — so the human is *least* prepared at the exact 0.1% moment the machine throws control back. This is the through-line from Air France 447 to highway driver-assist disengagements. **Mode confusion** — "what is it doing now, and why?" — compounds it. The design implication is brutal: you cannot use "the human will catch it" as a cheap mitigation, because the automation you built is actively eroding that human's ability to catch it.

### Calibrated trust beats maximized trust

Newcomers try to make operators trust the system *more*. The real objective is **calibration** — trust that tracks actual reliability. Both failure directions are documented and dangerous: **over-trust / automation bias** (accepting a wrong machine recommendation over one's own correct judgment — measured in real studies as commission and omission errors) and **under-trust / disuse** (ignoring a good system, or switching it off). Transparency and explanation are engineering tools whose *purpose is calibration*, not decoration — you surface confidence and reasoning so the human knows *when* to trust, not so the UI looks friendly.

### Handoffs need lead time; the "instant takeover" is a myth

A human pulled from **out-of-the-loop** supervision does not regain situational awareness instantly — rebuilding it takes many seconds, and the literature on takeover requests treats that latency as a first-class design parameter. Systems that demand instant human intervention at the moment of crisis are designed to fail. The fix is **graceful, early, predictable** handoffs — warn before you need to, hand off on a schedule the human can anticipate, and design a safe-state fallback for when the human *won't* be ready in time.

### Workload is a U-curve, and underload is the sneaky killer

Yerkes-Dodson applies: both **overload** (too many alarms, too many vehicles) and **underload** degrade performance. Overload produces **alarm fatigue** — the boy-who-cried-wolf effect where operators silence nuisance alarms and then miss the real one. Underload is subtler: long, reliable autonomous missions create the **vigilance decrement**, where a bored, unstimulated monitor simply stops detecting events. Practitioners measure this for real — **NASA-TLX** for workload, **SAGAT** freeze-probes for situational awareness, validated trust scales — rather than asserting "the operator will manage."

### Span of control flips piloting into management-by-exception

One operator to many vehicles is not piloting scaled up — it's a different job: **supervising and intervening by exception**. The governing quantity is **fan-out**, bounded by the ratio of a vehicle's **neglect tolerance** (how long it runs safely unattended) to the **interaction time** each intervention costs (Goodrich/Olsen). Double the autonomy's neglect tolerance and you roughly double the swarm one human can hold. This is the concrete link to [19-multi-agent-swarm.md](19-multi-agent-swarm.md): swarm span-of-control is a human-factors equation as much as a coordination one.

### Predictability outranks raw accuracy, and the human is a fragile mitigation

Two closing truths the field knows. First, operators trust a **consistent, slightly-worse** autonomy over an **erratic, slightly-better** one — a predictable system lets the human build an accurate mental model and anticipate it, which is worth more than a few points of performance. Second, the certification reality nobody likes to say aloud: you certify the **human-plus-machine** system, and when the safety case leans on "the operator will intervene," it is leaning on the **least reliable component in the loop**. A safety argument whose load-bearing mitigation is human vigilance is a fragile argument — and the irony of automation is busy making it more fragile every flight.
