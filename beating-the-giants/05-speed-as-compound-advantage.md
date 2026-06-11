# Speed as Compound Advantage — OODA, Cycle Time, and Learning Per Loop

> **Why this exists.** Speed is the underdog's only resource that scales *down* with size —
> a small team can iterate faster than a giant no matter how much capital the giant has. The
> [Startup Asymmetric Playbook](../companies/11-startup-asymmetric-playbook.md) and the SpaceX
> [rapid-iteration](../companies/02-spacex-rapid-iteration.md) study describe the *what*; this
> guide makes speed *quantitative and operational*, drawing the OODA loop from
> [History of Technology & War](../foundations/20-history-of-technology-and-war.md) and connecting to
> [Distribution](01-distribution-as-a-weapon.md) and [Pricing](02-pricing-and-unit-economics.md),
> where speed shows up as cheaper learning and lower unit cost.
>
> **What mastering it makes you.** Someone who can measure cycle time, maximize learning per
> loop, and protect the speed advantage as the organization grows.

---

## Table of Contents

1. [Why Speed Compounds](#1-why-speed-compounds)
2. [The OODA Loop, Quantified](#2-the-ooda-loop-quantified)
3. [Learning Per Cycle Is the Real Metric](#3-learning-per-cycle-is-the-real-metric)
4. [Instrumenting Cycle Time](#4-instrumenting-cycle-time)
5. [Where Speed Comes From (and Where It Leaks)](#5-where-speed-comes-from-and-where-it-leaks)
6. [Protecting Speed as You Scale](#6-protecting-speed-as-you-scale)
7. [Speed Without Recklessness](#7-speed-without-recklessness)
8. [Where to Go Next](#8-where-to-go-next)

---

## 1. Why Speed Compounds

Speed is not just "doing things faster"; it is *learning faster than the competition*, and
learning compounds. If you complete a build-measure-learn cycle in time $T$ and your rival
takes $2T$, then over a fixed window you take twice as many shots, accumulate twice as much
information about the market, and — because each cycle starts from what the last one taught —
your product diverges from theirs *exponentially*, not linearly.

Formally, if each cycle yields a multiplicative improvement factor $r > 1$ and you run $n$
cycles while the rival runs $n/2$, your relative advantage grows as $r^{n} / r^{n/2} =
r^{n/2}$ — exponential in the number of cycles. **This is the mathematical core of why a small
fast team beats a large slow one**, and why the incumbent's resource advantage cannot buy back
lost cycles.

## 2. The OODA Loop, Quantified

John Boyd's **Observe–Orient–Decide–Act** loop (see
[History of Technology & War](../foundations/20-history-of-technology-and-war.md)) is the canonical
model. The strategic claim is *relative tempo*: whoever cycles through OODA faster operates
"inside" the opponent's loop — by the time the slower actor orients to your last move, you've
already made two more, and their decisions are answering a world that no longer exists.

For a company, the loop maps to:

| OODA phase | Company activity | Where it slows down |
|---|---|---|
| Observe | Gather customer/market/telemetry signal | Slow or missing instrumentation |
| Orient | Make sense of it, update beliefs | Politics, sunk-cost, dogma |
| Decide | Choose the next move | Committees, approval chains |
| Act | Ship it | Heavy process, release friction |

Underdogs almost always win Decide and Act (few approvers, light release process) and lose
ground only if they neglect Observe (no instrumentation) or let ego corrupt Orient. The
incumbent's slowness lives mostly in Orient (it cannot afford to believe the disruptive
story) and Decide (process designed to prevent mistakes also prevents speed).

## 3. Learning Per Cycle Is the Real Metric

Raw speed is a trap if each cycle teaches you nothing. The quantity to maximize is
**learning per unit time**:

$$\text{Learning rate} = \frac{\text{information gained per cycle}}{\text{cycle time}}$$

This reframes two common mistakes:
- **Fast but blind** (ship constantly, measure nothing) — high denominator, near-zero
  numerator. This is motion, not progress.
- **Informative but glacial** (perfect experiments, quarterly cadence) — high numerator
  destroyed by a huge denominator.

The discipline: every cycle should be designed around the **riskiest unknown** — the single
assumption that, if wrong, kills the plan. Test that first, cheaply. This is the same
reasoning as risk-first engineering in [Test Scaffold](../autonomy/05-test-scaffold.md) and
the rationalist habit of [Decision-Making & Rationality](../foundations/15-decision-making-and-rationality.md):
buy the most belief-update per dollar and per day.

## 4. Instrumenting Cycle Time

You cannot compound what you don't measure. Minimum instrumentation by domain:

- **Software:** deployment frequency, lead time for changes, change-failure rate, mean time to
  recovery (the DORA metrics). Elite teams deploy on-demand with lead times under an hour;
  slow ones take weeks. The gap *is* the competitive gap.
- **Hardware / autonomy:** design-build-test-iterate turnaround per subsystem; test
  cadence (the SpaceX lesson — they win by *testing to failure often and cheaply*, see
  [SpaceX: Rapid Iteration](../companies/02-spacex-rapid-iteration.md)). Test infrastructure
  is itself a speed moat: whoever can run the next experiment cheapest iterates fastest.
- **Go-to-market:** sales-cycle length, time-to-first-value for new users
  ([Distribution as a Weapon](01-distribution-as-a-weapon.md) §7), experiment cadence on
  pricing and messaging.

Track the *trend*, not the absolute: a cycle time that is falling quarter over quarter is the
sign of a healthy, compounding organization.

## 5. Where Speed Comes From (and Where It Leaks)

Speed is an emergent property of structure, not exhortation. Its sources:

- **Small teams with full-loop ownership.** A team that can observe, decide, and ship without
  handoffs has no inter-team latency. Handoffs are where cycle time goes to die.
- **Low coordination cost.** Brooks's Law: adding people to a late project makes it later,
  because communication paths grow as $\binom{n}{2}$. Speed favors the small.
  (See [Leverage Over Headcount](08-leverage-over-headcount.md).)
- **Reversible decisions made fast.** Amazon's "Type 1 vs Type 2" doors
  ([Amazon Mechanisms](../companies/08-amazon-mechanisms-customer-obsession.md)): make
  reversible decisions immediately and at low level; reserve deliberation for the truly
  one-way doors.
- **Cheap experiments.** Tooling, simulation, and automation that lower the cost of one more
  iteration directly raise the learning rate.

Leaks: approval chains, meeting-driven decisions, fear of reversible mistakes, missing
instrumentation, and the slow creep of process added in response to each error.

## 6. Protecting Speed as You Scale

Speed is the first thing a growing company loses, usually by adding process to prevent the
last mistake until process *is* the mistake. Defenses:

- **Add process only for one-way doors.** Every new approval gate should have to justify its
  cost in cycle time against the cost of the error it prevents.
- **Preserve small autonomous teams** as the unit of execution even inside a large company
  (the "two-pizza team"). Scale the number of loops, not the size of each loop.
- **Keep Orient honest.** The deadliest slowdown at scale is psychological: success makes the
  organization defend its current product and disbelieve the next disruption — the
the Innovator's Dilemma ([Defense Primes: How Incumbents Win](../companies/14-defense-primes-how-incumbents-win.md))
  experienced from the inside. Speed of *belief-updating* is the hardest to preserve and the
  most valuable.

## 7. Speed Without Recklessness

Speed is a weapon, not a license. The places where moving fast is *wrong* are exactly the
one-way, high-consequence doors: safety-critical systems, irreversible financial or legal
commitments, anything touching human life or [export control](07-regulatory-judo-and-export-control.md).
The mature formulation is **"fast where reversible, careful where not"** — not "move fast and
break things" applied indiscriminately. Pairing rapid iteration with rigorous testing (the
SpaceX model) is what separates productive speed from the recklessness that kills companies and
people. Match the cadence to the cost of being wrong.

## 8. Where to Go Next

- Speed as cheaper customer acquisition: [Distribution as a Weapon](01-distribution-as-a-weapon.md).
- Speed as a cost moat (experience curve): [Pricing & Unit Economics](02-pricing-and-unit-economics.md).
- Where speed comes from structurally: [Leverage Over Headcount](08-leverage-over-headcount.md).
- The theory of tempo: [History of Technology & War](../foundations/20-history-of-technology-and-war.md).

---

*This guide is **AI-assisted synthesis**, curated and
reviewed — a starting point, not a primary source. Verify anything load-bearing before you
rely on it. See the [README](../README.md) for the full note.*
