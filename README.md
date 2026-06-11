# Elite Ball Knowledge Curriculum

[![Guides](https://img.shields.io/badge/guides-177-blue)](01-mastery-curriculum.md)
[![Topic folders](https://img.shields.io/badge/topic%20folders-14-blueviolet)](01-mastery-curriculum.md)
[![License: CC BY 4.0](https://img.shields.io/badge/license-CC%20BY%204.0-green)](LICENSE)
[![Contributions: owner-gated](https://img.shields.io/badge/contributions-owner--gated-orange)](CONTRIBUTING.md)
[![Made with: AI tools](https://img.shields.io/badge/made%20with-AI%20tools-8A2BE2)](#)
[![Status: AI-assisted — verify before relying](https://img.shields.io/badge/AI--assisted-verify%20before%20relying-critical)](#how-this-library-was-made--read-this-first)

A self-contained, first-principles study library — **177 in-depth guides across 14
topic folders** — covering everything an autonomy / defense-technology engineer needs,
from the math and control theory under a flight stack to the career, strategy, and
human-operating-system skills that decide how far that knowledge takes you.

**Who it's for.** Engineers, students, and career-changers who want the "inside the
building" knowledge of elite autonomy and defense-tech teams — explained from first
principles, not gatekept.

> **How this library was made — read this first.** This repository is a compilation of
> real questions people have asked me, answered with the help of **AI tools** and
> **AI tools**. It is **AI-assisted synthesis that I curate and review** — not
> original primary research, and not a substitute for authoritative sources. Treat every
> guide as a strong, structured *starting point*: learn the shape of a topic here, then
> verify anything load-bearing against primary sources before you rely on it, cite it, or
> build on it. Holding that line is the whole point — it keeps all of us honest.

## Start here in 60 seconds

New here? Don't try to read all guides. Pick the lane that matches you and start
with one:

- **I want to build autonomy** → [Guidance, Navigation & Control](autonomy/09-gnc.md),
  then [Sensor Fusion](autonomy/13-sensor-fusion.md).
- **I want to think like a chief engineer** →
  [First Principles & Systems Engineering](foundations/01-first_principles_systems_engineering.md).
- **I want a job in defense-tech** →
  [The Defense-Aerospace Playbook](career/02-defense-aerospace-playbook.md), then
  [Interview Prep](career/08-interview-prep.md).
- **I want the strategy / business side** →
  [How the Giants Win](companies/01-how-the-giants-win.md).
- **I'm just curious how this stuff works** →
  [How AI & LLMs Actually Work](general/04-how-ai-and-llms-actually-work.md).

Want the full map and ordered learning paths instead?
**▶ [The Mastery Curriculum](01-mastery-curriculum.md)** is the master index — it explains
how to read the library, maps every guide, and gives ordered paths so you don't try to
boil the ocean.

## How it's organized

Every folder is numbered **independently from `01`**. The library is grouped into bands:

| Folder | Range | Band |
|---|---|---|
| [`foundations/`](foundations) | 01–21 | The spine (01–09) plus cross-cutting literacy (10–21) |
| [`autonomy/`](autonomy) | 01–29 | The full autonomy & robotics stack, plus domain verticals |
| [`career/`](career) | 01–20 | Job-hunt mechanics plus the meta-skills that move careers |
| [`companies/`](companies) | 01–20 | How the giants win — and how to beat them |
| [`engineering/`](engineering) | 01–16 | Hardware & physical-engineering breadth |
| [`software/`](software) | 01–15 | Production software, compute & infrastructure |
| [`mathematics/`](mathematics) | 01–12 | The math & physics under every layer |
| [`mindset-and-society/`](mindset-and-society) | 01–17 | The human operating system |
| [`information-environment/`](information-environment) | 01–06 | Platforms, cognition, OSINT & OPSEC (defense-oriented) |
| [`general/`](general) | 01–14 | Accessible explainers for a general reader |
| [`compute-and-hardware/`](compute-and-hardware) | 01–04 | Silicon, power & AI data centers |
| [`space/`](space) | 01 | Space systems & astronautics |
| [`products/`](products) | 01 | High-impact tools worth adopting |
| [`tooling/`](tooling) | 01 | Power prompts for building with AI |

See the [curriculum index](01-mastery-curriculum.md) for a per-module table of every
guide and what it makes you.

## Contributing

**All contributions and communication must go through the repository owner.** This
library is maintained as a curated collection, so nothing is merged or changed without
the owner's review and approval first. Do **not** push directly, open unsolicited pull
requests, or treat any folder as open self-serve.

Before doing any work, **contact the owner first** and wait for sign-off:

- Open a [New guide proposal](.github/ISSUE_TEMPLATE/new-guide-proposal.yml) or a
  [Correction / improvement](.github/ISSUE_TEMPLATE/correction-or-improvement.yml) issue
  describing what you want to add or change, and
- Wait for the owner to approve the proposal and assign you the next free number.

Only after the owner approves should you scaffold and write the guide:

```bash
./scripts/new-guide.sh <folder> "Your Guide Title"   # scaffolds the next-numbered file
```

Then add one row to the [curriculum index](01-mastery-curriculum.md) and open a pull
request **referencing the approved issue**. Every pull request is reviewed by the owner
and merged at the owner's discretion. Full conventions, style guide, and the quality bar
live in **[CONTRIBUTING.md](CONTRIBUTING.md)**.

- **How to contribute** → [CONTRIBUTING.md](CONTRIBUTING.md)
- **Guide template** → [templates/GUIDE_TEMPLATE.md](templates/GUIDE_TEMPLATE.md)
- **Community standards** → [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- **License** → Creative Commons Attribution 4.0 International ([CC BY 4.0](LICENSE)) — content is free to share and adapt with credit

## Also in this repo (outside the curriculum)

A few folders live alongside the curriculum but are **not part of it** — they're
standalone collections kept here for convenience. They aren't counted in the 177-guide
total and aren't tracked by the curriculum index.

- **[`sie/`](sie)** — an in-depth study guide and rapid-review question bank for FINRA's
  Securities Industry Essentials (SIE) exam.
- **[`outreach/`](outreach)** — a compliant-by-design B2B lead-generation and outreach
  toolkit (templates, scripts, and a compliance checklist).
- **[`sports/`](sports)** — a couple of standalone sports analysis write-ups.

The same honesty note at the top of this README applies to these too: they're
AI-assisted, and you should verify anything load-bearing before relying on it.
