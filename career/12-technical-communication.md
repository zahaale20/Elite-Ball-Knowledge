# Technical Communication: Writing, Speaking & Influence

> A standalone companion to [03-software-engineering.md](03-software-engineering.md)
> and [09-resume-portfolio.md](09-resume-portfolio.md). Your code is only as
> valuable as your ability to make other people *understand, trust, and act on*
> it. Communication is not a soft skill bolted onto engineering — it is the
> interface through which all of your technical work reaches the world.

Here is the uncomfortable leverage point of an engineering career: past the
mid-level, you are paid less for what you personally build and more for how much
*correct decision-making* you cause in others. The two engineers with identical
technical skill diverge entirely on this axis. The one who can write a crisp
design doc, give a calm review, and explain a tradeoff to a program manager gets
the scope, the staff, and the title. This file teaches that skill as an
engineering discipline.

---

## 1. The Core Model: Communication Is Compression with a Decoder in Mind

Every act of communication is **lossy compression of your mental model, decoded by
a brain that does not share your context.** Good communication minimizes the
decoding cost for *that specific audience*.

- **Know the decoder.** A principal engineer, a program manager, and a general
  decode the same message completely differently. Same facts, different encoding.
- **Lead with the answer (BLUF — Bottom Line Up Front).** State the conclusion,
  recommendation, or ask in the first sentence. Then support it. Engineers bury
  the lede in chronological narrative; executives and reviewers will not dig.
- **Optimize for the reader's time, not your effort.** A message that takes you
  longer to write but saves 20 readers five minutes each is a 100x trade. Doing
  the compression *for* them is a gift and a status move.

---

## 2. Writing: The Highest-Leverage Skill in Engineering

Writing scales infinitely and asynchronously. One excellent design doc aligns a
team of 30 across three time zones without a meeting.

**The design doc** is the master form. A strong one has:
- **Context & problem** — what's broken, why now, what happens if we do nothing.
- **Goals / non-goals** — explicitly bounding scope prevents 80% of review churn.
- **The proposed approach** — and at least one rejected alternative with the
  *reason* it lost. Showing the road not taken is what earns trust.
- **Tradeoffs & risks** — stated plainly. Hiding the weakness destroys
  credibility; naming it builds it.
- **A decision ask** — what you need from the reader, by when.

**Principles that travel everywhere:**
- **One idea per paragraph; topic sentence first.**
- **Concrete beats abstract** — "cut p99 latency from 80ms to 12ms" not "improved
  performance."
- **Delete ruthlessly.** The second draft is the first draft minus 30%. Every word
  that doesn't earn its place taxes the reader.
- **Active voice, short sentences, real verbs.** "The planner rejects infeasible
  paths" not "infeasible paths are rejected by the planning subsystem."

---

## 3. Explaining Hard Things Simply

The ability to make a complex system *click* for a non-expert is a superpower and a
reliable signal of true understanding.

- **Start from the listener's existing model** and modify it, rather than building
  from scratch. Analogy is a bridge from known to unknown.
- **Use the ladder of abstraction** — give the one-sentence version first, then add
  a layer only if they want it. Let the listener pull detail, don't push it.
- **Name the thing, then explain it** — humans hold a concept better once it has a
  handle.
- **The Feynman test:** if you can't explain it to a smart non-specialist, you
  don't fully understand it yet. Explaining is a debugging tool for your own
  knowledge.

---

## 4. Speaking: Meetings, Reviews & Presentations

- **Design reviews:** your job is to make it *easy to find the flaw*, not to
  defend. Present the risk you're most worried about first. Reviewers trust
  engineers who surface their own weaknesses.
- **Status updates:** red/yellow/green with the *one thing* that matters and the
  *one decision* you need. Never a chronological log.
- **Presentations:** one idea per slide, picture > words, words > tables of
  numbers on a screen. The slide supports you; it is not your notes.
- **Speak to the most senior decoder in the room** but don't lose the engineers.
  Calibrate to the person who will act.
- **Comfort with silence.** After you make an ask, stop talking. The pause does the
  work; filling it gives away leverage.

---

## 5. Communicating Up, Down & Sideways

Same facts, three encodings:

| Audience | They want | Lead with | Avoid |
|---|---|---|---|
| **Up** (leadership/PM) | Decisions, risk, impact, cost | The ask + the bottom line | Implementation detail, jargon |
| **Sideways** (peer eng) | Correctness, tradeoffs, interfaces | The approach + the hard parts | Over-explaining basics |
| **Down** (your reports) | Context, the *why*, clear next step | The goal + the constraints | Vagueness, false certainty |

**Managing up** specifically: give your manager *no surprises*. Surface bad news
early and with a proposed path. The engineer who says "this will slip two weeks,
here's the recovery plan" on day 3 is worth ten who say it the day of the deadline.

---

## 6. Writing That Persuades Without Manipulating

Honest persuasion is making the *true* and *good* option the *easy* and *obvious*
one to choose.

- **Argue the other side first.** Steelman the alternative, then show why yours
  wins. Disarms resistance and signals you actually thought.
- **Quantify the stakes.** Decisions move on numbers and consequences, not
  adjectives.
- **Make the recommended path the path of least resistance** — pre-write the
  decision, the doc, the next step. Reduce the activation energy to say yes.
- **Never oversell.** Calibrated confidence ("70% this works, here's the failure
  mode") earns far more long-run trust than false certainty. Your credibility is a
  bank account; one oversell is an expensive withdrawal.

---

## 7. Documentation, Async & Distributed Communication

In remote and cross-time-zone teams, written async communication *is* the
organization.

- **Write it down once, well, in a findable place** beats explaining it ten times
  in DMs. Documentation is leverage that compounds.
- **Make messages self-contained** — context, the point, the ask. No "ping" with
  no payload; no thread that requires you online to decode.
- **Decisions need a durable record** — who decided what, when, and why. Memory and
  Slack both rot.

---

## 8. Defense-Context Communication

- **Classification discipline shapes everything** — know what can be said where,
  to whom, on which system. (See [20-ethics-export-control.md](20-ethics-export-control.md)
  and [07-security-clearance.md](07-security-clearance.md).)
- **Translate between worlds** — engineers, program managers, and uniformed
  customers speak different languages. The person who translates cleanly between
  them is disproportionately valuable.
- **Briefings to senior officers** reward extreme brevity, the bottom line first,
  and total calm under hard questions. Practice the one-slide, two-minute version
  of everything you own.

---

## 9. Deliberate Practice

- **Write a doc and cut it by a third.** Repeat until cutting hurts.
- **Explain something you just learned to someone who doesn't know it** — same day.
- **Record yourself presenting** once; the cringe is the fastest teacher you'll
  find.
- **Steal structure** from writers and speakers you admire; imitate, then make it
  yours.
- **Get edited.** Hand your writing to someone blunter than you and absorb it
  without defending.

---

### Connections
- [03-software-engineering.md](03-software-engineering.md) — the technical work this
  communicates.
- [09-resume-portfolio.md](09-resume-portfolio.md) — communication aimed at getting
  hired.
- [13-personal-brand-public-presence.md](13-personal-brand-public-presence.md) —
  communication at scale, in public.
- [10-leadership-growth.md](10-leadership-growth.md) — communication as the core of
  leadership.
