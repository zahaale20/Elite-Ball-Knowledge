# Elite Ball Knowledge Curriculum

A self-contained, first-principles study library — **177 in-depth guides across 14
topic folders** — covering everything an autonomy / defense-technology engineer needs,
from the math and control theory under a flight stack to the career, strategy, and
human-operating-system skills that decide how far that knowledge takes you.

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

**This library is open to everyone — you don't have to be the original author to add
to it.** The structure is designed so contributions never collide: each folder is
numbered independently, numbers are permanent (never renumbered), and you simply take
the next free number when you add a guide.

Fastest path to your first contribution:

```bash
./scripts/new-guide.sh <folder> "Your Guide Title"   # scaffolds the next-numbered file
```

Then write it, add one row to the [curriculum index](01-mastery-curriculum.md), and
open a pull request. Full conventions, style guide, and the quality bar live in
**[CONTRIBUTING.md](CONTRIBUTING.md)**. Prefer to start small? Open a
[New guide proposal](.github/ISSUE_TEMPLATE/new-guide-proposal.yml) or a
[Correction / improvement](.github/ISSUE_TEMPLATE/correction-or-improvement.yml) issue.

- **How to contribute** → [CONTRIBUTING.md](CONTRIBUTING.md)
- **Guide template** → [templates/GUIDE_TEMPLATE.md](templates/GUIDE_TEMPLATE.md)
- **Community standards** → [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- **License** → [CC BY 4.0](LICENSE) (content) — free to share and adapt with credit

## Separate collection — Machine Learning course materials

The [`machine learning/`](machine%20learning) folder is **not part of the mastery
curriculum**. It is a standalone set of university ML course materials (CPSC 5310):
lecture decks, hands-on notebooks (CNN, RNN, Transformer, and RAG), and two review
documents — [STUDY_GUIDE.md](machine%20learning/STUDY_GUIDE.md) and
[FINAL_PRACTICE_EXAM.md](machine%20learning/FINAL_PRACTICE_EXAM.md).
