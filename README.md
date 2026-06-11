# Elite Ball Knowledge Curriculum

A self-contained, first-principles study library — **177 in-depth guides across 14
topic folders** — covering everything an autonomy / defense-technology engineer needs,
from the math and control theory under a flight stack to the career, strategy, and
human-operating-system skills that decide how far that knowledge takes you.

> **How this was made.** This repository is a compilation of questions people have
> asked me, which I answered with the help of **AI tools** and **Claude Opus
> 4.8**. The guides are AI-assisted synthesis curated and reviewed by me — not original
> primary research. Read them as a starting point, verify anything load-bearing against
> authoritative sources, and keep that context in mind before treating any claim as
> gospel.

## Start here

**▶ [The Mastery Curriculum](01-mastery-curriculum.md)** — the master index. It explains
how to read the library, maps every guide, and gives ordered **learning paths** so you
don't try to boil the ocean.

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
- **License** → [CC BY 4.0](LICENSE) (content) — free to share and adapt with credit

## Separate collection — Machine Learning course materials

The [`machine learning/`](machine%20learning) folder is **not part of the mastery
curriculum**. It is a standalone set of university ML course materials (CPSC 5310):
lecture decks, hands-on notebooks (CNN, RNN, Transformer, and RAG), and four review
documents — [STUDY_GUIDE.md](machine%20learning/STUDY_GUIDE.md) (deep learning + RAG),
[STUDY_GUIDE_CLASSICAL_ML.md](machine%20learning/STUDY_GUIDE_CLASSICAL_ML.md) (regression,
classification, Bayes, SVM, ensembles, clustering, PCA),
[CHEATSHEET.md](machine%20learning/CHEATSHEET.md) (exact configs and formulas), and
[FINAL_PRACTICE_EXAM.md](machine%20learning/FINAL_PRACTICE_EXAM.md).
