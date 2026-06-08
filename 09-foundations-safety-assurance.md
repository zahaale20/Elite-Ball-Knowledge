# Module 09 — Safety Engineering & Assurance

> **Why this file exists.** Everything else in this curriculum makes the drone *capable*. This
> module makes it *trustworthy* — and in defense autonomy, trustworthy is the gate that capable
> has to pass through before it ever flies a real mission. Safety engineering is the discipline of
> answering, with evidence a skeptic will accept, one question: **"why is this safe to fly?"** It
> is not paperwork. It is a way of thinking — about hazards, failure modes, and the
> *unsafe interactions* between parts that are each working correctly — that, done well, is
> indistinguishable from being a great systems engineer. Nancy Leveson, whose work anchors this
> file, puts it bluntly: most accidents in modern software-intensive systems are not component
> failures; they are *control failures* — the system did exactly what it was told, and what it
> was told was unsafe.
>
> **What mastering it makes you.** The engineer who can stand in front of a safety review board,
> or a colonel, or a test pilot, and *make the argument* that a system is safe — structured,
> evidenced, honest about residual risk — and be believed because the argument is sound. That
> skill is the capstone of this curriculum: it ties together your verification work (Module 06),
> your understanding of the customer's trust requirement (Module 07), and the assurance moat
> (Module 08) into the thing that actually lets autonomy fly.

**Companion code.** This module is anchored to the assurance machinery in the author's `drone/`
stack: the **constitution-gated command policy** (`policy/constitution.py`) as a run-time safety
monitor, the **intent gate** (`policy/intent.py`) guarding LLM-suggested actions, the
**hash-chained tamper-evident decision log** (`policy/decisions.py`) as the accountability record,
and the geofence/failsafe modules (`onboard/geofence.py`) as the safety envelope. The verification
evidence that feeds every safety claim comes from
[06-foundations-simulation-test-verification.md](06-foundations-simulation-test-verification.md);
the customer's *demand* for this assurance is
[07-foundations-defense-acquisition.md](07-foundations-defense-acquisition.md); and the reason it's
a business moat is [08-foundations-company-strategy-moat.md](08-foundations-company-strategy-moat.md).

---

## Table of Contents

1. [Safety is a system property, not a component property](#1-safety-is-a-system-property-not-a-component-property)
2. [Vocabulary: hazard, risk, failure, accident](#2-vocabulary-hazard-risk-failure-accident)
3. [Hazard analysis: the starting point](#3-hazard-analysis-the-starting-point)
4. [FMEA / FMECA — bottom-up failure analysis](#4-fmea--fmeca--bottom-up-failure-analysis)
5. [Fault Tree Analysis — top-down failure analysis](#5-fault-tree-analysis--top-down-failure-analysis)
6. [STPA — the modern, control-theoretic method](#6-stpa--the-modern-control-theoretic-method)
7. [Redundancy: fail-safe vs fail-operational](#7-redundancy-fail-safe-vs-fail-operational)
8. [Run-time assurance & safety monitors](#8-run-time-assurance--safety-monitors)
9. [The airworthiness mindset: DO-178C & ARP4754A](#9-the-airworthiness-mindset-do-178c--arp4754a)
10. [Safety cases & assurance arguments (GSN)](#10-safety-cases--assurance-arguments-gsn)
11. [How to argue "this is safe to fly"](#11-how-to-argue-this-is-safe-to-fly)
12. [Practice this month](#12-practice-this-month)
13. [Sources & Citations](#sources--citations)

---

## 1. Safety is a system property, not a component property

Begin with the single idea that reorganizes everything: **safety is an emergent property of the
whole system, not a sum of the safety of its parts.** You cannot make a system safe by making each
component reliable, because the most dangerous accidents in software-intensive systems happen when
*every component works exactly as specified* and the *interaction* between them is unsafe.

### 1.1 The Leveson reframe

The traditional view (born in mechanical/reliability engineering) treats accidents as chains of
component *failures*: a part breaks, that breaks the next thing, dominoes fall, accident. That
model is fine for a simple mechanism and dangerously incomplete for an autonomy stack. Nancy
Leveson's central insight (STAMP — Systems-Theoretic Accident Model and Processes) is that in
modern systems, accidents are better understood as **inadequate control**: the system's control
structure allowed it into an unsafe state, even though no component "failed."

```
   OLD MODEL (reliability)              LEVESON MODEL (control)
   ───────────────────────             ───────────────────────
   accident = chain of failures        accident = inadequate control / unsafe interaction
   "what broke?"                       "what unsafe state was the system allowed to enter,
                                        and why didn't a controller prevent it?"
   fix = make components reliable       fix = strengthen the control structure & constraints
   misses software & interaction        captures the way software actually causes accidents
   accidents
```

### 1.2 Why this is the right model for your drone

Consider a real autonomy accident shape: the GPS estimate drifts (the GPS isn't "broken," it's
degraded under jamming), the planner — working perfectly — commands a path based on the drifted
estimate, the controller — working perfectly — flies that path precisely, and the drone flies
precisely into a hill. **Nothing failed.** Every component did exactly its job. The accident was a
*control* failure: nothing in the control structure enforced the constraint "do not act on a
position estimate you can't trust." This is why your **constitution-gated command policy** exists —
it is a *controller* that enforces safety constraints regardless of what the (correctly
functioning) planner suggests. Hold this example; it recurs through the whole module.

> **Senior tell.** A junior asks "is each part reliable?" A senior asks "what unsafe states can
> this system enter even when every part works, and what *controller* prevents each one?" The
> second question is the entire discipline.

---

## 2. Vocabulary: hazard, risk, failure, accident

Safety has precise terms, and conflating them produces muddled analysis. Lock these down.

| Term | Definition | Drone example |
|---|---|---|
| **Accident / mishap** | An undesired event causing loss (injury, death, damage) | The drone strikes a person |
| **Hazard** | A system *state* that, with worst-case environment, leads to an accident | The drone is airborne over people with a corrupted position estimate |
| **Failure** | A component not performing its intended function | The GPS receiver outputs a wrong fix |
| **Fault** | The underlying defect/cause of a failure | A jamming signal saturating the GPS front-end |
| **Error** | A discrepancy between actual and correct internal state | The EKF's position state is 30 m off |
| **Risk** | (Severity of accident) × (likelihood of the hazard) | "catastrophic × remote" |
| **Safety constraint** | A rule that, if always held, prevents the hazard | "Never act on a position estimate flagged untrustworthy" |

### 2.1 The crucial distinction: hazard vs failure

A **hazard is a system state**, not a broken part. "GPS failure" is a failure; "drone airborne
over people relying on an untrustworthy estimate" is the *hazard*. The reframe matters because you
control hazards by enforcing **safety constraints** on system *states*, which you can do even when
components fail. You can't prevent every component from ever failing (GPS *will* get jammed). You
*can* enforce "if the estimate is untrustworthy, don't fly over people on it" — that's a constraint
on a state, and it's enforceable by a controller (your gate). **Safety engineering is the practice
of identifying hazardous states and designing controllers that keep the system out of them.**

### 2.2 Severity and likelihood — the risk matrix

Risk is two-dimensional, and you must always carry both axes:

```
   severity →   negligible   marginal    critical    catastrophic
  likelihood ┌───────────────────────────────────────────────────┐
   frequent  │   low         medium      HIGH        HIGH         │
   probable  │   low         medium      HIGH        HIGH         │
   occasional│   low         medium      medium      HIGH         │
   remote    │   low         low         medium      HIGH ◄──── still HIGH!
   improbable│   low         low         low         medium       │
            └───────────────────────────────────────────────────┘
```

The cell that catches engineers out is **catastrophic × remote**: rare but lethal. The instinct is
to dismiss it ("it almost never happens"). The discipline is to treat it as high risk *because the
consequence is catastrophic*, and rarity means it's never been debugged in the field. This is
exactly the top-left quadrant of the test-prioritization map in Module 06 — the same risk logic,
now applied to safety.

---

## 3. Hazard analysis: the starting point

You cannot prevent hazards you haven't identified. **Hazard analysis** is the systematic search
for the system states that could lead to loss. It is the first activity in any safety program and
the source from which every test, constraint, and safety-case claim ultimately derives.

### 3.1 The Preliminary Hazard List (PHL) for your VTOL

Brainstorm the accidents, then trace each to the hazardous states that cause it. A starter PHL:

| # | Hazard (system state) | Leads to (accident) | Severity |
|---|---|---|---|
| H1 | Airborne over people with untrustworthy position estimate | Strike a person | Catastrophic |
| H2 | Transition (MC↔FW) attempted outside safe airspeed envelope | Stall, uncontrolled descent | Catastrophic |
| H3 | Flight outside the authorized geofence | Collision, airspace violation | Critical |
| H4 | Loss of command link with no safe fallback behavior | Flyaway | Critical |
| H5 | Battery depleted below safe-return threshold while far out | Crash from power loss | Critical |
| H6 | Autonomy commands an action violating ROE | Fratricide / unlawful effect | Catastrophic |
| H7 | Motor/actuator failure in a non-redundant flight phase | Loss of control | Critical |
| H8 | Decision provenance unrecoverable after an incident | Cannot prove what happened (trust loss) | Marginal→Critical |

### 3.2 From hazard to safety constraint to code

The entire method is this chain, and you should be able to run it for any hazard:

```
  HAZARD  ──►  SAFETY CONSTRAINT  ──►  CONTROLLER that enforces it  ──►  TEST that proves it
  ──────       ─────────────────       ─────────────────────────       ──────────────────────
  H1: untrust- "do not fly over        constitution gate checks         test_gps_loss_*
  worthy        people on an un-        estimate-trust flag before       (Module 06 §8.2):
  estimate      trustworthy estimate"   permitting over-people flight    inject GPS loss,
  over people                                                            assert gate denies
```

This is the spine connecting this module to the rest of the curriculum: **hazard analysis
produces the safety constraints; the constitution-gated policy is the controller that enforces
them; the test scaffold (Module 06) is the evidence that the controller works; the safety case
(§10) is the argument that ties it all together.** Every row of the PHL should be traceable to a
constraint, a controller, and a test. A hazard with no enforcing controller is an open risk you
must consciously accept or mitigate.

### 3.3 Hazard analysis is iterative

You never finish the PHL on day one. Each design change can introduce new hazards; each
exploratory-test finding (Module 06 §3.2) or near-miss in flight reveals a hazard you missed. The
PHL is a living document, and the loop — *find new hazard → add constraint → add controller → add
test* — is the same cultural ratchet as the test ratchet in Module 06. Safety, like verification,
is something you accrue, not something you finish.

---

## 4. FMEA / FMECA — bottom-up failure analysis

**Failure Modes and Effects Analysis** is the classic *bottom-up* method: walk through each
component, enumerate the ways it can fail, and trace the effect of each failure up to the system
level. **FMECA** adds *Criticality* — weighting each failure mode by severity and likelihood. It's
inductive ("given this part fails, what happens?") and exhaustive within its scope.

### 4.1 The FMEA worksheet

For each component × failure mode, you fill a row:

| Component | Failure mode | Cause | Local effect | System effect | Sev | Detection | Mitigation |
|---|---|---|---|---|---|---|---|
| GPS receiver | No fix | Jamming | Position invalid | Nav degrades; H1 risk | Cat | Estimate-trust flag, NIS spike | Gate blocks over-people flight; vision/INS fallback |
| Battery | Sudden voltage sag | Cell fault, cold | Brownout risk | H5/H2 | Crit | Voltage monitor | Reserve threshold → RTL; abort transition |
| Front tilt servo | Stuck mid-tilt | Mechanical/elec | Asymmetric thrust | H7 loss of control | Crit | Position feedback mismatch | Abort transition to stable MC mode |
| Command link | Drops | Jamming/range | No operator input | H4 flyaway | Crit | Heartbeat timeout | Failsafe: loiter/RTL per policy |
| IMU | NaN / spike | Sensor glitch | Filter poisoning | Estimate diverges → H1 | Cat | Range/finiteness check | Reject sample; don't fuse (Module 06 §8.1) |

### 4.2 The RPN and its trap

FMECA often computes a **Risk Priority Number** = Severity × Occurrence × Detection (each rated
1–10), to rank what to fix first. Useful, with one famous trap: **multiplying the three can hide a
catastrophic severity behind a low occurrence**, producing a deceptively small RPN for something
that can kill. The discipline: *severity has a veto.* Any catastrophic-severity failure mode (a 9
or 10 on severity) gets top-priority attention **regardless of its RPN**. Never let arithmetic
talk you out of mitigating a lethal failure just because it's rare — that's the catastrophic ×
remote cell of §2.2 again.

### 4.3 What FMEA is good and bad at

```
  GOOD AT                              BAD AT
  ───────                              ──────
  + exhaustive component coverage      − combinations (two failures together)
  + finding single-point failures      − interaction hazards where NOTHING fails
  + concrete, traceable mitigations    − human/software/organizational causes
  + reliability-style hardware faults   − emergent, system-level unsafe behavior
```

FMEA's blind spot is exactly the Leveson reframe (§1): it's built around *components failing*, so
it structurally misses the accident where every component works and the *interaction* is unsafe
(the GPS-drift-into-a-hill scenario). That gap is why you also need top-down (FTA) and
control-theoretic (STPA) methods. FMEA is necessary, not sufficient.

---

## 5. Fault Tree Analysis — top-down failure analysis

**Fault Tree Analysis** inverts FMEA: start from a **top event** (an accident or hazard) and work
*downward* through Boolean logic to find all the combinations of lower-level events that could
cause it. It's deductive ("for this accident to happen, what must be true?") and excels at exactly
what FMEA misses: **combinations** of failures.

### 5.1 Reading a fault tree

Gates are Boolean: **AND** (all inputs required) and **OR** (any input suffices). A fragment for
hazard H1 (strike a person):

```
                        ┌────────────────────────────┐
                        │ TOP EVENT: drone strikes a  │
                        │ person                      │
                        └─────────────┬──────────────┘
                                   ┌──AND──┐   (BOTH must hold for the accident)
                          ┌────────┴──┐  ┌──┴───────────────┐
                          │ drone over │  │ drone flies into  │
                          │ people     │  │ a person (loss of │
                          │            │  │ safe separation)  │
                          └─────┬──────┘  └────────┬─────────┘
                                │              ┌───OR───┐
                            (mission           │        │
                             context)   ┌──────┴──┐ ┌───┴──────────┐
                                        │untrust-  │ │ controller   │
                                        │worthy    │ │ commands bad │
                                        │estimate  │ │ path         │
                                        │+ gate     │ └──────────────┘
                                        │FAILS to   │   ┌──AND──┐
                                        │block      │   │       │
                                        └────┬──────┘  est.bad  gate
                                          ┌──AND──┐    │        bypassed
                                          │       │    │        /buggy
                                       GPS lost  gate
                                                 fails
```

### 5.2 Minimal cut sets — the payoff

The reason FTA is powerful: it computes **minimal cut sets** — the smallest combinations of basic
events that, together, cause the top event. A cut set of size 1 (a single basic event that alone
causes the accident) is a **single point of failure** and is your highest-priority target. A cut
set of size 2+ means you need *multiple* independent things to go wrong — which is the whole
argument for redundancy (§7).

For H1 above, a critical cut set is **{GPS lost, gate fails to block}**. The accident requires
*both*. This tells you something precise and actionable: **the gate is the independent barrier that
turns a single GPS failure into a survivable event.** As long as the gate works, GPS loss alone
cannot cause the strike. That is *exactly* why the constitution gate exists and why its correctness
(proven by the property tests in Module 06 §10.3) is safety-critical: it's the second element of
the cut set that keeps the first from being lethal alone.

### 5.3 FTA + FMEA together

```
  FMEA (bottom-up)   ──►  finds single failure modes & their effects
        │
        ▼  feed the basic events into...
  FTA (top-down)     ──►  finds COMBINATIONS & single points of failure (cut sets)
        │
        ▼
  redundancy / barriers placed to break the dangerous cut sets (§7)
```

They're complementary: FMEA enumerates the basic events; FTA assembles them into the combinations
that matter and reveals where one independent barrier (like the gate) breaks a whole class of
accidents. Neither, however, fully handles the *no-component-failed* accident — for that, STPA.

---

## 6. STPA — the modern, control-theoretic method

**STPA** (System-Theoretic Process Analysis), Leveson's method built on STAMP, is the technique
purpose-built for software-intensive autonomy. Instead of asking "what can fail?", it asks "**what
control actions, given or not given, in what context, are unsafe?**" — capturing the accidents
where nothing failed but the control was inadequate. For an autonomy engineer, this is the most
important hazard-analysis method to internalize.

### 6.1 The control-structure view

STPA models the system as a hierarchy of **controllers** issuing **control actions** to
**controlled processes**, with **feedback** closing the loop. Your drone, drawn this way:

```
   ┌──────────────────┐  intent / commands   ┌────────────────────────┐
   │ Operator / C2    │ ───────────────────► │ Autonomy controller    │
   │ (human + policy) │ ◄─────────────────── │ (planner + constitution│
   └──────────────────┘  telemetry/feedback  │  gate)                 │
                                             └───────────┬────────────┘
                                       control actions   │  feedback
                                       (setpoints, mode) │  (state, estimate trust)
                                                         ▼
                                             ┌────────────────────────┐
                                             │ Flight controller (PX4)│
                                             └───────────┬────────────┘
                                                         ▼
                                             ┌────────────────────────┐
                                             │ Airframe + environment │
                                             └────────────────────────┘
```

Safety, in this view, is enforced by **constraints on control actions.** The hazard happens when a
controller issues an unsafe control action (or fails to issue a needed one) given its — possibly
wrong — model of the process state.

### 6.2 The four ways a control action can be unsafe

STPA's engine: for each control action, examine four categories of **Unsafe Control Actions
(UCAs)**:

| UCA type | Meaning | Drone example (transition command) |
|---|---|---|
| **1. Not provided** | A needed control action isn't given | Failsafe NOT commanded when link is lost → flyaway (H4) |
| **2. Provided** | An unsafe control action is given | Transition commanded below stall airspeed (H2) |
| **3. Wrong timing/order** | Right action, wrong time | RTL commanded *after* battery already too low (H5) |
| **4. Wrong duration** | Applied too long / stopped too early | Transition held through a brownout instead of aborting |

Each UCA you identify becomes a **safety constraint** ("the controller must NOT command transition
when airspeed < V_min"), which becomes a controller behavior (the gate checks airspeed), which
becomes a test (Module 06's `test_transition_aborts_on_low_airspeed`). Same chain as §3.2, now
generated systematically from the control structure.

### 6.3 Loss scenarios — why the UCA happens

STPA's second step asks *why* each UCA could occur — the **loss scenarios** — and this is where it
shines for software. Causes include: the controller's **process model is wrong** (the planner
thinks the estimate is good, but it's drifted — the GPS-jamming case!); feedback is missing,
delayed, or wrong; the control algorithm is flawed; or a control action is sent but not executed.
The GPS-into-a-hill accident drops out naturally: the autonomy controller's *process model of
position is wrong* (drifted estimate), so it issues a control action that is unsafe *in the true
state* though it looks safe *in its model.* STPA names this directly — and the mitigation is
exactly the estimate-trust flag + gate that breaks the FTA cut set in §5.2.

> **Why STPA is the autonomy method.** FMEA and FTA are organized around *failures.* STPA is
> organized around *control*, so it captures the dominant accident class in autonomy — correct
> components, wrong process model, unsafe-but-locally-rational action. If you learn one
> hazard-analysis method deeply, learn this one, because it matches how autonomy actually hurts
> people.

---

## 7. Redundancy: fail-safe vs fail-operational

Once hazard analysis reveals the dangerous cut sets, you break them with **redundancy and
barriers.** But "redundancy" is not one thing — the central design choice is *what the system does
when something fails*, and getting that choice right per-hazard is core safety design.

### 7.1 The two postures

```
   FAIL-SAFE                              FAIL-OPERATIONAL
   ─────────                              ────────────────
   on failure → enter a SAFE state        on failure → KEEP OPERATING (degraded ok)
   (stop, land, loiter, RTL)              (survive the failure, finish the function)
   cheaper; one backup not required to    needs redundancy: a backup that takes over
   keep flying                            seamlessly
   right when stopping IS safe            right when stopping is itself dangerous
   e.g. link lost → loiter then RTL       e.g. one IMU fails → keep flying on the other
```

**Fail-safe** assumes there *is* a safe state to fall into (land, return, loiter). **Fail-operational**
is required when failing into a "safe state" is itself unsafe — e.g., you can't just "stop" a
fixed-wing in cruise; you must keep flying. The choice is per-function and per-flight-phase, and
naming it explicitly for each hazard is the design discipline.

### 7.2 The redundancy patterns

| Pattern | How it works | Cost | Use when |
|---|---|---|---|
| **Hot standby** | Backup runs in parallel, takes over instantly | High | Fail-operational, no glitch tolerable |
| **Cold standby** | Backup spun up on demand | Medium | Brief outage acceptable |
| **N-modular (e.g. TMR)** | N copies vote; majority wins | High | Tolerate a faulty unit silently |
| **Dissimilar redundancy** | Backups of *different design* | Highest | Defeat *common-mode* faults |
| **Analytical redundancy** | Estimate a lost signal from others | Low ($) | Sensor loss (vision/INS for GPS) |

### 7.3 The common-mode trap

The deepest redundancy pitfall: **common-mode failure** — one cause defeats all your redundant
copies at once. Three identical GPS receivers give you *zero* protection against jamming, because
jamming takes out all three simultaneously (same cause, same vulnerability). Real protection
against GPS loss comes from **dissimilar/analytical redundancy** — a *different* navigation source
(vision, INS dead-reckoning) that doesn't share GPS's vulnerability. This is why your GPS-denied
nav pipeline is a *safety* feature, not just a capability: it's the dissimilar-redundant barrier
that breaks the "GPS lost" cut set at the *sensing* layer, complementing the gate that breaks it at
the *control* layer. Two independent barriers, different mechanisms — that's defense in depth.

### 7.4 Defense in depth

```
   threat: untrustworthy position estimate over people (H1)
   ┌──────────────────────────────────────────────────────────────────┐
   │ barrier 1: dissimilar nav (vision/INS) bounds drift when GPS lost  │ (sensing)
   │ barrier 2: estimate-trust flag (NIS monitor) detects untrust state │ (detection)
   │ barrier 3: constitution gate blocks over-people flight on bad est. │ (control)
   │ barrier 4: geofence keeps the vehicle away from populated areas    │ (envelope)
   │ barrier 5: failsafe RTL/land if multiple barriers degrade          │ (recovery)
   └──────────────────────────────────────────────────────────────────┘
   the accident requires ALL barriers to fail — a tiny cut set probability
```

No single barrier is trusted to be perfect; safety comes from *independent* barriers whose joint
failure is the only path to the accident. This is the Swiss-cheese model: each slice has holes, but
the holes don't line up. Your job in design is to ensure the barriers are *genuinely independent*
(no common mode) so the holes can't align.

---

## 8. Run-time assurance & safety monitors

Hazard analysis happens at design time. **Run-time assurance (RTA)** is its complement: a
*real-time* component that watches the system in flight and enforces safety constraints as they're
about to be violated — the controller that keeps the system out of hazardous states *while it
flies.* This is the most directly relevant safety concept to your stack, because your
constitution-gated policy *is* an RTA monitor.

### 8.1 The Simplex / "safety monitor" architecture

The canonical RTA pattern (Sha's Simplex architecture) separates a complex, high-performance,
hard-to-verify controller from a simple, trusted **safety monitor** that has veto power:

```
   ┌─────────────────────────┐
   │ Complex controller       │  proposed
   │ (planner, LLM intent,    │  action
   │  fancy autonomy)         │ ─────────────┐
   │  — high performance,     │              ▼
   │    hard to fully verify  │      ┌──────────────────────┐   safe
   └─────────────────────────┘      │ SAFETY MONITOR        │  action
                                    │ (simple, TRUSTED,     │ ─────────►  actuators
   ┌─────────────────────────┐      │  fully verifiable)    │
   │ Safety controller        │ ───►│  • check constraints  │
   │ (simple, always-safe      │     │  • veto/clamp/replace │
   │  fallback, e.g. loiter)  │      │  • log the decision   │
   └─────────────────────────┘      └──────────────────────┘
```

The genius: you get to use a powerful-but-unverifiable controller (a learned planner, an LLM
suggesting actions) *safely*, because a simple monitor you *can* fully verify sits between it and
the actuators, vetoing anything that violates a safety constraint and falling back to the trusted
safe controller. You don't have to prove the fancy autonomy is safe; you have to prove the *monitor*
is — a vastly smaller, tractable verification problem.

### 8.2 Your constitution gate is a safety monitor

This is the satisfying mapping. The author's `policy/` layer is a textbook RTA architecture:

| Simplex element | Your stack |
|---|---|
| Complex controller | The planner + LLM-suggested intents (`policy/intent.py`) |
| Safety monitor | The constitution gate (`policy/constitution.py`) — simple, verifiable rules |
| Constraint check | Geofence, airspeed envelope, ROE, estimate-trust before permitting an action |
| Safe fallback | Failsafe loiter/RTL (`onboard/geofence.py`, failsafe modules) |
| Accountability | Hash-chained decision log (`policy/decisions.py`) records every veto/permit |

Because the gate is *simple and rule-based*, you can verify it exhaustively (property tests,
Module 06 §10.3) — which means you can let the *complex* autonomy be as smart and unverifiable as
you like, and still make a sound safety argument, because nothing reaches the actuators without
passing a monitor you've proven correct. **This is how you field LLM-class autonomy responsibly:
not by trusting the LLM, but by gating it behind a verifiable monitor and logging everything.**

### 8.3 The decision log as the assurance backbone

The hash-chained decision log earns its keep here. Every monitor decision — what the complex
controller proposed, what the gate permitted or vetoed and why — is recorded in a tamper-evident
chain. This does three safety jobs at once:

1. **Accountability:** after any incident, you can prove *exactly* what the autonomy decided and
   why — the difference between "we think it did X" and "here is the cryptographically verifiable
   record." (This addresses hazard H8.)
2. **Run-time monitoring:** the same stream feeds health monitors (a NIS spike, a surge of gate
   vetoes) that can trigger failsafe — the log isn't just forensic, it's a live safety signal.
3. **Assurance evidence:** the log *is* a piece of the safety case (§10) — verifiable evidence that
   the monitor operated as designed across every flight.

A safety monitor that *acts* but doesn't *record* gives you safety without accountability. The
combination — verifiable monitor **plus** tamper-evident log — is what lets you both *be* safe and
*prove* you were. That pairing is the assurance moat of Module 08, expressed as engineering.

---

## 9. The airworthiness mindset: DO-178C & ARP4754A

You don't need to *certify* your drone to civil-aviation standards, but you need the **mindset** of
the standards that govern when software-intensive aircraft are allowed to fly. This is literacy
that earns instant credibility with anyone from aerospace, and it shapes how you structure
evidence even at hobby/prototype scale.

### 9.1 The standards landscape

```
   ARP4754A  ── development of the whole AIRCRAFT/SYSTEM; allocates safety
               requirements down to subsystems; "how to develop a safe system"
        │
        ├── ARP4761 ── the safety-assessment methods (FHA, PSSA, SSA; FTA/FMEA live here)
        │
        ├── DO-178C ── SOFTWARE aspects of airborne systems certification
        │
        └── DO-254  ── airborne electronic HARDWARE
```

The hierarchy: **ARP4754A** governs developing the whole system and flows safety requirements down;
**ARP4761** provides the safety-assessment methods (the FHA/FTA/FMEA you met above); **DO-178C**
governs the *software*; **DO-254** the electronic hardware. They interlock into one assurance story.

### 9.2 Design Assurance Levels — rigor scales with consequence

The central idea you must absorb from DO-178C is **Design Assurance Level (DAL)**: how rigorously
you must develop and verify software scales with **how bad it is if the software fails.**

| DAL | Failure condition | Effect | Rigor |
|---|---|---|---|
| **A** | Catastrophic | Loss of aircraft/life | Maximum (incl. structural-coverage proof, MC/DC) |
| **B** | Hazardous | Severe injury, large safety margin loss | Very high |
| **C** | Major | Significant but survivable | High |
| **D** | Minor | Slight | Moderate |
| **E** | No safety effect | None | Minimal |

The principle is **proportionate assurance**: you spend verification effort in proportion to
consequence. The constitution gate and failsafe logic in your stack are DAL-A-flavored (their
failure is catastrophic → verify to exhaustion); the telemetry-formatting code is DAL-E-flavored
(no safety effect → light testing). This is *exactly* the risk-based test prioritization of Module
06 §11, now named in the aviation idiom. You're already doing DO-178C *thinking* when you test the
gate harder than the telemetry shaper.

### 9.3 What MC/DC teaches you (even unofficially)

For DAL-A software, DO-178C requires **Modified Condition/Decision Coverage (MC/DC)** — not just
that every line ran (statement coverage) or every branch (decision coverage), but that **each
condition in a boolean decision has been shown to independently affect the outcome.** For a gate
like `if estimate_trustworthy and over_people and not authorized: deny`, MC/DC forces you to prove
each of those three conditions independently changes the decision — catching the bug where one
condition is dead or wrong. You don't need formal MC/DC tooling on a hobby project, but the *habit*
— "have I shown each condition in this safety-critical decision actually matters?" — is exactly the
mutation-testing instinct from Module 06 §11.3, and it's the right rigor for the gate.

### 9.4 The transferable mindset

You won't ship a DO-178C certification package. What you take from it:

- **Proportionate rigor** (DAL): verify in proportion to consequence.
- **Requirements-based testing**: every test traces to a requirement; every requirement to a test
  (the V-model, Module 06 §2.1).
- **Traceability**: hazard → constraint → requirement → code → test → evidence, end to end.
- **Independence**: the person/process verifying isn't the one who built it (or, at least, the
  verification is structurally separate).
- **Configuration control**: you know *exactly* what software flew, reproducibly.

Adopt these and your prototype, while uncertified, is built like serious aviation software — which
is precisely the signal that makes an aerospace or defense employer trust you (Module 08's
assurance moat, again, and the credibility play in
[11-career-defense-aerospace-playbook.md](11-career-defense-aerospace-playbook.md)).

---

## 10. Safety cases & assurance arguments (GSN)

All the analysis above produces evidence. A **safety case** is the structured *argument* that
marshals that evidence into a coherent claim: **"this system is acceptably safe to operate in this
context, and here is why."** It is the deliverable that a safety board, a customer's T&E authority,
or a test pilot actually evaluates. Building one well is the capstone skill of this module.

### 10.1 What a safety case is (and isn't)

A safety case is **not** a pile of test reports. It is an *argument* with three parts (the
Claim–Argument–Evidence structure):

```
   CLAIM        "The system is acceptably safe to fly mission M in context C."
     │  (supported by)
   ARGUMENT     "...because every identified hazard has an enforced safety constraint,
     │           independently verified, with bounded residual risk."
     │  (grounded in)
   EVIDENCE     hazard analysis (§3–6), test results (Module 06), the decision log,
                redundancy analysis (§7), monitor verification (§8).
```

The *argument* is the load-bearing part. Evidence without an argument is a heap; an argument
without evidence is a wish. The safety case is where you connect them, explicitly, so a skeptic can
follow the reasoning from "safe to fly" all the way down to a specific passing test — and find no
gap.

### 10.2 GSN — Goal Structuring Notation

**GSN** is the standard graphical notation for assurance arguments. It decomposes a top **goal**
(claim) into sub-goals via an explicit **strategy**, stated in a **context**, until each leaf goal
is discharged by a **solution** (evidence). A fragment for your drone:

```
   ┌─────────────────────────────────────────┐
   │ G1: Drone is acceptably safe to fly the  │   (top goal / claim)
   │     ISR mission over the test range      │
   └───────────────────┬─────────────────────┘
                       │  S1: argue over all identified hazards (H1–H8)
          ┌────────────┼─────────────────────────────┐
          ▼            ▼                              ▼
   ┌──────────────┐ ┌──────────────────────┐  ┌──────────────────────┐
   │ G2: H1 (strike│ │ G3: H2 (unsafe        │  │ G8: H8 (provenance   │
   │ via bad est.) │ │ transition) mitigated │  │ recoverable)         │
   │ mitigated     │ │                       │  │                      │
   └──────┬───────┘ └──────────┬───────────┘  └──────────┬───────────┘
          │ S2: defense in depth │ S3: envelope gate       │ S8: hash-chain log
     ┌────┴────┐            ┌────┴────┐               ┌─────┴─────┐
     ▼         ▼            ▼         ▼               ▼           ▼
  ┌──────┐ ┌────────┐  ┌────────┐ ┌────────┐    ┌──────────┐ ┌──────────┐
  │Sn: GPS│ │Sn: gate│  │Sn: air-│ │Sn: abort│   │Sn: chain │ │Sn: tamper│
  │-denied│ │property│  │speed   │ │ SITL    │   │verify    │ │ test     │
  │ nav    │ │tests   │  │ check  │ │ test    │   │ test     │ │ (M06)    │
  │evidence│ │(M06)   │  │evidence│ │(M06)    │   │(M06)     │ │          │
  └──────┘ └────────┘  └────────┘ └────────┘    └──────────┘ └──────────┘
```

Read it top-down as "how do I argue this?" and bottom-up as "what does this evidence prove?" Every
leaf is a specific artifact from your verification work (Module 06) or your safety analysis. The
GSN makes the argument *inspectable*: a reviewer can walk any branch from the top claim to a
concrete test and challenge any link. If a leaf has no evidence, the gap is visible — that's a
hazard you haven't actually mitigated, exposed by the structure.

### 10.3 The honesty requirement: residual risk

A *credible* safety case states what it does **not** cover. Every real system has **residual risk**
— hazards mitigated but not eliminated, conditions outside the tested envelope, assumptions that
could be wrong. A safety case that claims zero risk is not trustworthy; it's naive or dishonest,
and a good reviewer will reject it on sight. The mature move: enumerate residual risks, state why
each is acceptable (low likelihood × mitigations × operating restrictions), and name the
*assumptions* the argument rests on ("assumes the test range is cleared of non-participants";
"assumes GPS-denied nav is validated only up to 60 s of dropout"). Honesty about limits is what
makes the rest of the argument believable.

### 10.4 Assurance for learned/autonomous components

The hard frontier — and where defense autonomy lives — is arguing safety for components you
*can't* fully verify (learned perception, LLM-class planners). The answer is the §8 architecture
expressed as a safety-case strategy: **don't argue the learned component is safe; argue the
*monitor* gating it is safe, and that the monitor's safe behavior bounds the system regardless of
what the learned component does.** Your GSN branch for an LLM-suggested action doesn't claim "the
LLM is correct"; it claims "any action the LLM suggests is checked by the verified constitution
gate, vetoed if it violates a constraint, and logged — therefore the LLM cannot drive the system
into a hazardous state." That's a sound argument over an unsound component, and it's the only known
way to field this class of autonomy responsibly.

---

## 11. How to argue "this is safe to fly"

Synthesis. When someone asks you the capstone question — *why is this safe to fly?* — here is the
structure of a sound answer, the thing this whole module exists to make you able to say.

### 11.1 The argument, in order

```
  1. CONTEXT   "Safe to fly mission M, over range R, with restrictions X — not unconditionally."
  2. HAZARDS   "We identified the hazards (H1–H8) via PHL, FMEA, FTA, and STPA. Here they are."
  3. CONSTRAINTS "Each hazard has a safety constraint that, if held, prevents it."
  4. CONTROLS  "Each constraint is enforced by a controller — the gate, geofence, failsafe,
               dissimilar nav — arranged in independent layers (defense in depth)."
  5. EVIDENCE  "Each controller is verified: property tests on the gate, SITL fault-injection for
               failsafe, NEES/NIS for the estimator, replay regression on the nav filter."
  6. MONITORING "At run time, the safety monitor enforces constraints live, and the tamper-evident
               log records every decision for accountability and health monitoring."
  7. RESIDUAL  "Here is what we do NOT cover, why each residual risk is acceptable, and the
               assumptions the argument rests on."
  8. CLAIM     "Therefore, within this context, the system is acceptably safe to fly."
```

### 11.2 Why this beats "it worked in testing"

"It worked when we tested it" is the answer that gets airframes — and people — killed, because it
makes no claim about the *untested* states, names no hazards, and offers no argument for why the
*next* flight, in conditions you didn't test, will be safe. The structured argument above is
falsifiable, inspectable, and honest: it tells the reviewer exactly what you're claiming, on what
evidence, and what you're *not* claiming. A skeptic can attack any link — and the fact that they
*can*, and it holds, is what makes it trustworthy. That is the difference between an engineer who
*hopes* the system is safe and one who can *argue* it is.

### 11.3 The whole curriculum, converging

This module is the capstone because it consumes everything before it:

```
  Module 01 (systems eng) ─► hazard analysis IS systems thinking applied to loss
  Module 06 (verification)─► produces the EVIDENCE every safety claim rests on
  Module 07 (acquisition) ─► the customer's TRUST requirement is WHY this matters
  Module 08 (strategy)    ─► assurance + integration IS the moat this enables
  Module 09 (this file)   ─► the ARGUMENT that ties evidence into "safe to fly"
            │
            ▼
  the constitution-gated, logged, tested, GPS-denied-capable drone is not just capable —
  it is DEFENSIBLE, in both senses: it can be argued safe, and that argument is the moat.
```

The drone you've built is, at its core, a machine for making this argument: a verifiable safety
monitor (the gate) over capable-but-unverifiable autonomy, with a tamper-evident record (the log)
that turns "we believe it's safe" into "here is the evidence and the argument." Master this module
and you can not only build that machine — you can stand in front of the people who decide whether it
flies, and convince them.

---

## 12. Practice this month

1. **Write the PHL for your drone.** Reproduce and extend the §3.1 table for *your* airframe and
   missions. For each hazard, fill the §3.2 chain: hazard → constraint → controller → test. Find
   the hazard with no controller — that's your next sprint.
2. **Run one STPA pass on the transition command.** List the four UCA types (§6.2) for "command
   MC→FW transition," derive a safety constraint from each, and check whether your gate enforces
   it. You will find at least one UCA you hadn't guarded.
3. **Build one fault tree.** Take hazard H1 or H4, draw the tree to its basic events, and find the
   minimal cut sets. Identify any single point of failure and the barrier (like the gate) that
   breaks the dangerous size-2 cut sets.
4. **Map your gate to Simplex.** Write the §8.2 table for your actual `policy/` code, and articulate
   in one paragraph why a *verifiable monitor over unverifiable autonomy* lets you field LLM-class
   intent safely. This is a top-tier interview answer.
5. **Draft a one-page safety case in GSN.** Top goal "safe to fly the SITL acceptance mission,"
   decomposed over your top three hazards, with leaves pointing at real tests in `drone/test/`.
   Include a residual-risk section — practice the honesty.
6. **Answer the capstone out loud.** Using the §11.1 structure, give the 90-second spoken answer to
   "why is this safe to fly?" for your drone. Record it. Tighten it. That answer, delivered with
   evidence behind every claim, is the skill this entire curriculum was building toward.

---

## Sources & Citations

**Books — the safety canon**
- Leveson, Nancy G. — *Engineering a Safer World: Systems Thinking Applied to Safety* (MIT Press,
  2011) — STAMP and STPA; **the** foundational text for this module. Available openly:
  https://direct.mit.edu/books/book/2908/Engineering-a-Safer-World
- Leveson, Nancy G. — *Safeware: System Safety and Computers* (the earlier classic on
  software-related accidents).
- Leveson & Thomas — *STPA Handbook* (the practical how-to for STPA):
  https://psas.scripts.mit.edu/home/get_file.php?name=STPA_handbook.pdf
- Ericson, Clifton — *Hazard Analysis Techniques for System Safety* (FMEA, FTA, and the full
  toolkit).
- Vesely et al. — *Fault Tree Handbook* (NUREG-0492), the canonical FTA reference:
  https://www.nrc.gov/reading-rm/doc-collections/nuregs/staff/sr0492/
- Kletz, Trevor — *An Engineer's View of Human Error* (why "operator error" is usually a system
  design failure — a Leveson-adjacent classic).

**Standards & official guidance (literacy level)**
- RTCA DO-178C — *Software Considerations in Airborne Systems and Equipment Certification*
  (software DALs, MC/DC, requirements-based testing).
- SAE ARP4754A — *Guidelines for Development of Civil Aircraft and Systems*.
- SAE ARP4761 — *Guidelines and Methods for Conducting the Safety Assessment Process* (FHA, FTA,
  FMEA, common-mode analysis).
- RTCA DO-254 — airborne electronic hardware.
- MIL-STD-882E — *DoD Standard Practice for System Safety* (the defense system-safety process and
  risk matrix): https://www.dau.edu/ (System Safety references).
- U.S. military airworthiness frameworks (e.g., MIL-HDBK-516, Army AR 70-62) — for the defense
  airworthiness mindset.

**Papers & notation**
- Sha, Lui — "Using Simplicity to Control Complexity" (the Simplex architecture / safety monitor,
  §8).
- GSN Community Standard (Goal Structuring Notation), Assurance Case Working Group:
  https://scsc.uk/gsn
- Rushby, John — papers on assurance cases and run-time assurance for autonomous systems.

**Sibling guides (read alongside)**
- [06-foundations-simulation-test-verification.md](06-foundations-simulation-test-verification.md)
  — the verification evidence every safety claim in §10 depends on.
- [07-foundations-defense-acquisition.md](07-foundations-defense-acquisition.md) — why the customer
  *demands* this assurance before fielding (T&E, airworthiness).
- [08-foundations-company-strategy-moat.md](08-foundations-company-strategy-moat.md) — why
  assurance + integration is the durable moat (§11.2 there).
- [01_first_principles_systems_engineering.md](01_first_principles_systems_engineering.md) — hazard
  analysis as applied systems thinking; reliability & margins.
- [11-career-defense-aerospace-playbook.md](11-career-defense-aerospace-playbook.md) — how the
  airworthiness mindset signals credibility to aerospace/defense employers.
- [27-autonomy-counter-uas-ew.md](27-autonomy-counter-uas-ew.md) — the GPS-denial/EW threat that
  drives hazard H1 and the dissimilar-redundancy argument.

*Repository references (the constitution-gated command policy as a run-time safety monitor, the
intent gate, the hash-chained tamper-evident decision log, and the geofence/failsafe modules) trace
to the author's own `drone/` project. The safety-engineering framing draws on Nancy Leveson's STAMP/
STPA work and standard system-safety and airworthiness literature; the application to defense
autonomy reflects the author's engineering goals and publicly available information, and the system
described is a prototype, not a certified aircraft.*
