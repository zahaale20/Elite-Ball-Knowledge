# Module 116 — Writing & Technical Communication

> **Why this file exists.** A brilliant analysis that no one understands has the same impact as no
> analysis at all. In every organization that matters — the primes, a two-person startup,
> a DoD program office — the engineers who rise are not always the best *engineers*; they are the
> ones who can make a complex idea **legible to the person who controls resources**. Writing is the
> act of thinking made transmissible. Amazon famously banned slides and runs on six-page memos for
> exactly this reason: you cannot hide muddled thinking inside good prose the way you can inside a
> bulleted slide. This module teaches the most leveraged non-coding skill an engineer can own.
>
> **What mastering it makes you.** The person whose design docs get approved, whose proposals win,
> whose bug reports get fixed first, whose Slack messages don't spawn three confused follow-ups,
> and who gets handed scope because leadership can *follow your reasoning*. Clear writing is clear
> thinking made visible — and visible clear thinking is how trust and authority accrue.

**Companion practice.** This module pairs with the *narrative* skills in
[03-cognitive-bias-attention-and-narratives.md](../information-environment/03-cognitive-bias-attention-and-narratives.md)
(communicating under uncertainty), the *systems narrative* in
[01-first_principles_systems_engineering.md](01-first_principles_systems_engineering.md) §7, and the
career-facing presentation guides ([08](../career/08-interview-prep.md),
[09](../career/09-resume-portfolio.md)). Where those teach what to say, this teaches how to make it
land.

---

## Table of Contents

1. [Writing is thinking, not transcription](#1-writing-is-thinking-not-transcription)
2. [Know the reader and the job the document does](#2-know-the-reader-and-the-job-the-document-does)
3. [Structure: BLUF, the pyramid, and the inverted pyramid](#3-structure-bluf-the-pyramid-and-the-inverted-pyramid)
4. [The sentence: clarity at the smallest scale](#4-the-sentence-clarity-at-the-smallest-scale)
5. [The design doc — the engineer's core artifact](#5-the-design-doc--the-engineers-core-artifact)
6. [Persuasive and decision documents](#6-persuasive-and-decision-documents)
7. [Communicating uncertainty and bad news](#7-communicating-uncertainty-and-bad-news)
8. [Visuals, diagrams, and when not to use them](#8-visuals-diagrams-and-when-not-to-use-them)
9. [Speaking: meetings, briefings, and the verbal channel](#9-speaking-meetings-briefings-and-the-verbal-channel)
10. [Editing: where the quality actually comes from](#10-editing-where-the-quality-actually-comes-from)
11. [Failure modes](#11-failure-modes)
12. [Practice this month](#12-practice-this-month)
13. [Sources & Citations](#sources--citations)

---

## 1. Writing is thinking, not transcription

The naïve model says you think a thought, then write it down. The real model is that **writing is
how you discover whether you have a thought at all.** Fuzzy prose is the fingerprint of fuzzy
thinking; the act of forcing an idea into a grammatical sentence with a subject, a verb, and a
logical connector to the next sentence *is* the act of clarifying it. This is why "write it up" is
such a powerful forcing function in engineering organizations: the document is a lie detector for
half-baked ideas.

The consequence for you: **never treat a writing task as mere documentation of a finished thought.**
Treat the draft as the place where the thinking gets finished. You will routinely discover, three
paragraphs in, that your design has a hole — and that discovery, made at the writing desk, is far
cheaper than the same discovery made in production.

> **Senior tell.** When a senior engineer can't write a clean one-paragraph summary of their own
> proposal, they don't conclude "I'm bad at writing." They conclude "my idea isn't done yet" — and
> go finish the idea.

---

## 2. Know the reader and the job the document does

Every document has exactly one job: **to change something in a specific reader's head or hands** — a
decision, an action, an understanding. Before writing a word, answer three questions:

1. **Who is the reader, and what do they already know?** A memo to your tech lead, your VP, and a
   government program manager are three different documents about the same thing. The VP doesn't
   want the register-level detail; the program manager needs the mission framing; the tech lead
   needs the failure modes. Writing the same text for all three serves none of them.
2. **What do you want them to *do* after reading?** Approve a design? Fund a program? Fix a bug?
   Change their mental model? If you can't name the desired post-read action in one sentence, you're
   not ready to write.
3. **What does the reader fear or doubt?** Every persuasive document is implicitly answering an
   objection. Surface the strongest objection and address it head-on; readers trust writers who
   name the counterargument before they do.

The cardinal sin is **writer-centric writing** — organizing the document around the order in which
*you* discovered things rather than the order in which the *reader* needs them. Your discovery
journey is irrelevant to the reader; their decision path is everything.

---

## 3. Structure: BLUF, the pyramid, and the inverted pyramid

**BLUF — Bottom Line Up Front.** Borrowed from military communication and universally correct:
state the conclusion, recommendation, or ask in the *first sentence or two*, then support it.
Readers are busy and read top-down; burying the conclusion at the end (the way you were taught to
write essays in school) is actively hostile to a working reader. "We should adopt the EKF over the
particle filter for the nav stack; here's why" beats three pages of build-up ending in the same
sentence.

**The Minto Pyramid Principle.** Barbara Minto's structure, the backbone of consulting and good
technical writing: **lead with the answer; group supporting arguments; order them logically.**

```
              ┌─────────── THE ANSWER / RECOMMENDATION ───────────┐
              │  "Adopt the EKF for the nav stack."                │
              └───────────────────┬───────────────────────────────┘
            ┌───────────┬─────────┴──────────┬───────────┐
        Reason 1     Reason 2            Reason 3
       (cheaper)   (well-understood)   (good enough accuracy)
          │            │                    │
      evidence     evidence             evidence
```

Each level answers the "why?" or "how?" raised by the level above it, and each group of supporting
points should be **mutually exclusive and collectively exhaustive** (MECE) — no overlaps, no gaps.
The reader can stop at any level and have a complete, correct, appropriately-detailed answer.

**The inverted pyramid** (journalism's version): most important information first, descending detail
after, so the document degrades gracefully — a reader who stops at any point has the most important
remaining information. Both structures share the same DNA: *front-load the payload.*

---

## 4. The sentence: clarity at the smallest scale

Structure gets the reader to the right paragraph; the sentence is where comprehension actually
happens. A few rules carry most of the weight:

- **Prefer subject-verb-object, active voice.** "The watchdog resets the controller" beats "the
  controller is reset by the watchdog," which beats the truly evasive "a reset of the controller is
  performed." Active voice names the actor — and naming the actor is often where accountability and
  clarity live.
- **One idea per sentence.** When you find a sentence with three clauses and two "and"s, it is
  usually three sentences wearing a trench coat. Split it.
- **Cut every word that does no work.** "In order to" → "to." "Due to the fact that" → "because."
  "At this point in time" → "now." George Orwell's rule still holds: *if it is possible to cut a
  word out, cut it out.* Concision is respect for the reader's time.
- **Use concrete nouns and strong verbs; distrust abstractions and nominalizations.** "We made an
  improvement to the performance" hides the action; "we cut latency 40%" shows it.
- **Define jargon once, then use it.** Precise terminology is a tool for compression among experts
  and a wall to everyone else. Match it to your reader (§2).
- **Parallel structure for parallel ideas.** Lists and comparisons should be grammatically parallel;
  the parallelism does cognitive work, signaling "these things are of a kind."

> **Senior tell.** The mark of a strong technical writer is not big words; it is the *absence* of
> friction. You finish their paragraph and realize you never had to re-read a sentence. That
> smoothness is engineered, not natural.

---

## 5. The design doc — the engineer's core artifact

The design document (RFC, "one-pager," ADR) is the single highest-leverage thing most engineers
write, because it converts a private plan into a *reviewable, durable, asynchronous* artifact. A
good design doc gets the disagreement out *before* the code is written, when it's cheap. A reusable
skeleton:

1. **Title, author, date, status** (draft / in review / approved / superseded).
2. **Summary / BLUF** — one paragraph: what this proposes and why, readable on its own.
3. **Context & problem statement** — what's true today, what's broken or missing, why now.
4. **Goals and explicit non-goals** — non-goals are where you prevent scope-creep and
   misunderstanding; they are often the most valuable section.
5. **Proposed design** — the actual approach, with the key decisions made explicit.
6. **Alternatives considered, and why rejected** — this is what separates a real design doc from a
   sales pitch. Reviewers trust an author who has genuinely weighed options. (This is decision
   reasoning from [15-decision-making-and-rationality.md](15-decision-making-and-rationality.md).)
7. **Risks, failure modes, and open questions** — name them honestly; hiding them only delays the
   reckoning and burns your credibility when they surface.
8. **Rollout / test / validation plan** — how you'll know it works (ties to
   [06-foundations-simulation-test-verification.md](06-simulation-test-verification.md)).

The discipline of writing the "alternatives considered" and "non-goals" sections is where most of
the *thinking* value of a design doc comes from — they force you to have actually considered the
space rather than the first idea that worked.

---

## 6. Persuasive and decision documents

When the document's job is to get a *decision* (funding, approval, a strategic choice), additional
moves apply:

- **Lead with the decision you're asking for and the recommendation**, BLUF-style. Decision-makers
  resent having to extract the ask.
- **Frame around the reader's goals, not your enthusiasm.** "This will let the program hit its
  fielding date" beats "this is a really elegant architecture." Connect to *their* objective
  function (see [13-economics-and-markets.md](13-economics-and-markets.md) on incentives).
- **Quantify.** A number beats an adjective. "Cuts integration time from 6 weeks to 2" is
  persuasive; "significantly faster" is noise.
- **Steelman the opposing view, then answer it.** Showing you understand the strongest case against
  your proposal is the fastest way to earn the reader's trust.
- **Make the recommendation the path of least resistance.** Spell out the concrete next step so
  saying yes is easy and saying no requires effort.

Amazon's **six-pager** and **PR/FAQ** ("working backwards" from a press release) are the gold
standard here and are covered as operating mechanisms in
[08-amazon-mechanisms-customer-obsession.md](../companies/08-amazon-mechanisms-customer-obsession.md).
The core idea: a narrative document forces *complete, connected reasoning* in a way bullet points
never can.

---

## 7. Communicating uncertainty and bad news

Engineers constantly have to convey things that are uncertain, probabilistic, or bad. Doing it well
is a distinct and rare skill:

- **Quantify uncertainty instead of hiding it.** "~70% confident we hit the date; the schedule risk
  is the sensor supplier" is vastly more useful than either false confidence or vague hedging. Give
  ranges and name the dominant risk. (Calibration is from
  [15-decision-making-and-rationality.md](15-decision-making-and-rationality.md).)
- **Separate what you know from what you believe from what you're guessing.** Label them. A reader
  who can see your evidential basis can act on it appropriately.
- **Deliver bad news early, directly, and with a plan.** "The flight test failed; root cause is X;
  here's the recovery plan and revised date" preserves trust. Burying it, softening it into
  unrecognizability, or surprising people late destroys it. Leaders are judged far more by how they
  handle the bad news than the good.
- **Never let optimism masquerade as a status report.** "Should be fine" is not a status. Greens
  that turn red overnight ("watermelon status" — green outside, red inside) are how programs die.

---

## 8. Visuals, diagrams, and when not to use them

A diagram is worth its weight only when it carries *relational* information that prose carries
poorly — architecture, data flow, state machines, timelines, distributions. The rules:

- **One idea per figure.** A diagram that needs a paragraph to decode has failed.
- **Label everything; assume no caption is read.** A figure should stand alone.
- **Edward Tufte's principle: maximize the data-ink ratio.** Delete chart junk — 3-D effects,
  gratuitous gridlines, decorative gradients. Every pixel should carry information.
- **Choose the chart for the question.** Trend → line; comparison → bar; distribution → histogram;
  correlation → scatter. A pie chart almost always loses to a bar chart.
- **Beware the slide deck as a thinking tool.** Slides reward fragments and hide logical gaps, which
  is exactly why Amazon and many serious teams write prose for decisions and reserve slides for
  *live talks with a presenter*. A deck read without its presenter is usually incoherent — that's a
  design flaw of the medium, not the author.

---

## 9. Speaking: meetings, briefings, and the verbal channel

The verbal channel is lower-bandwidth and unrecoverable (no re-reading), so it demands even more
front-loading:

- **State your conclusion first, in one breath.** "I recommend we slip the date two weeks; here's
  why." Then take questions. Do not build suspense; this is not storytelling.
- **Match depth to the room in real time.** Read whether the audience wants the headline or the
  mechanism, and adjust. Watch faces; senior audiences signal "go deeper" or "move on" constantly.
- **For a briefing, prepare three depths:** the 30-second version, the 3-minute version, and the
  full version — and be ready to give whichever the room asks for.
- **Answer the question asked, then stop.** Over-answering signals nervousness and wastes the
  scarcest resource in the room. If you don't know, say "I don't know; I'll find out by Friday" —
  it builds more trust than a confident guess that later proves wrong.
- **Silence is a tool.** A pause after a key point lets it land; rushing past it wastes it.

---

## 10. Editing: where the quality actually comes from

Almost no one writes a good first draft, and believing you should is the main source of writer's
block. **Separate drafting from editing** — they use different mental muscles and fighting them
together produces neither. The workflow:

1. **Draft fast and badly**, getting the whole skeleton down without stopping to perfect sentences.
   A complete bad draft is infinitely more workable than a perfect first paragraph.
2. **Edit ruthlessly, top-down:** first structure (is the argument in the right order? is the BLUF
   up front?), then paragraphs (one idea each?), then sentences (active, concise?), then words.
3. **Cut.** The strongest single edit is deletion. Most drafts shrink 20–40% with no loss of meaning
   and a large gain in force. "I would have written a shorter letter, but I did not have the time"
   (attributed to Pascal) names the real cost: brevity is *expensive*, which is exactly why it's
   valued.
4. **Read it aloud** (or have a tool read it). Your ear catches clumsiness your eye skips. Sentences
   you stumble over, the reader stumbles over too.
5. **Sleep on anything important** and re-edit cold. Distance reveals the flaws that proximity hides.

---

## 11. Failure modes

| Failure mode | Symptom | Fix |
|---|---|---|
| **Buried lede** | Conclusion in the last paragraph | BLUF — put it first |
| **Writer-centric order** | Organized by your discovery journey | Reorganize around the reader's decision path |
| **Wall of text** | No structure, no headings, no whitespace | Pyramid structure; headings; lists |
| **Hedging fog** | "Should," "probably fine," no numbers | Quantify confidence and name the risk |
| **Jargon wall** | Reader outside your team is lost | Match vocabulary to the actual reader |
| **No ask** | Reader finishes unsure what to do | Name the desired action explicitly |
| **First-draft-as-final** | Clumsy, bloated, unedited | Separate drafting from ruthless editing |
| **Slideware reasoning** | Logic gaps hidden in bullets | Write the argument in prose first |

---

## 12. Practice this month

- **Write a real design doc** for one component of your `drone/` stack using the §5 skeleton — and
  force yourself to fill the "alternatives considered" and "non-goals" sections honestly.
- **Rewrite your three longest recent Slack/email messages** with BLUF: conclusion first, then
  support. Notice how much shorter they get.
- **Take any 500-word thing you wrote and cut it by 30%** with no loss of meaning. Do it again next
  week. Concision is a trainable muscle.
- **Practice the three-depths briefing:** prepare a 30-second, 3-minute, and full version of one
  technical topic and deliver each to someone.
- **Apply the Feynman test from [10](10-learning-how-to-learn.md):** explain a hard concept in
  writing in plain language. The points where your prose gets vague are the points your
  understanding is vague.

---

## Sources & Citations

**Canonical works**
- Barbara Minto — *The Pyramid Principle: Logic in Writing and Thinking* — the structural backbone
  of professional technical and business writing.
- William Strunk & E.B. White — *The Elements of Style* — the classic on the sentence.
- William Zinsser — *On Writing Well* — clarity, simplicity, and cutting.
- Joseph M. Williams — *Style: Lessons in Clarity and Grace* — the deepest treatment of *why*
  sentences read clearly.
- Steven Pinker — *The Sense of Style* — a modern, cognitively-grounded guide.
- Edward Tufte — *The Visual Display of Quantitative Information* — the standard on data graphics.
- George Orwell — *Politics and the English Language* (free essay) — the rules on cutting and
  concrete language.

**Practitioner references**
- Amazon's six-pager / PR-FAQ "working backwards" method (see
  [08-amazon-mechanisms-customer-obsession.md](../companies/08-amazon-mechanisms-customer-obsession.md)).
- Google's engineering design-doc and code-review writing guides (publicly documented).

*Cross-links: pairs with [03-cognitive-bias-attention-and-narratives.md](../information-environment/03-cognitive-bias-attention-and-narratives.md)
(communicating under uncertainty), [15-decision-making-and-rationality.md](15-decision-making-and-rationality.md)
(reasoning you're making legible), and the career presentation guides ([08](../career/08-interview-prep.md),
[09](../career/09-resume-portfolio.md)).*
