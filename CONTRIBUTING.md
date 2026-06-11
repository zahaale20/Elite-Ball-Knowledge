# Contributing

Thanks for wanting to add to this library. It is a **self-contained, first-principles
study collection**, and it gets better the more sharp minds contribute. This guide
exists so that **anyone** — not just the original author — can add a guide, fix an
error, or propose a whole new topic without guessing at the conventions.

**This is a curated, owner-gated library.** Every change goes through the repository
owner first. Open an issue, wait for sign-off, then do the work. Do **not** push
directly or open unsolicited pull requests.

If you read nothing else, read **[The 60-second version](#the-60-second-version)**.

---

## The 60-second version

1. **Propose first** → open a
   [New guide proposal](.github/ISSUE_TEMPLATE/new-guide-proposal.yml) describing what
   you want to add, and **wait for the owner to approve it and assign the next number.**
2. **Fork** the repo and create a branch: `git checkout -b add/<topic-slug>`.
3. **Scaffold the guide** with the helper (it picks the next number for you):
   ```bash
   ./scripts/new-guide.sh foundations "Your Guide Title"
   ```
   …or copy [`templates/GUIDE_TEMPLATE.md`](templates/GUIDE_TEMPLATE.md) by hand.
4. **Write it** following the [style guide](#style-guide). Anchor claims to sources.
5. **Add one row** for your guide to the relevant table in
   [`01-mastery-curriculum.md`](01-mastery-curriculum.md).
6. **Run the validator** to catch broken links, numbering clashes, and a stale
   guide count before you push:
   ```bash
   ./scripts/check-repo.py
   ```
   It exits cleanly when the library is consistent (cross-repo `drone/` code
   references are reported as harmless warnings).
7. **Open a Pull Request** referencing the approved issue, using the template. The
   owner reviews and merges at their discretion.

Numbers are permanent IDs, so once the owner assigns you the next free number your work
never collides with anyone else's. The structure below explains why.

---

## Why this repo is safe to contribute to (the structure)

The single thing that used to make this feel like a one-person project was the
**numbering**. Here is the rule that fixes it:

> **Numbers are permanent IDs and ordering hints — never renumber an existing
> guide.** Renumbering breaks every inbound link. To add a guide, take the **next
> free number** in the folder. Gaps are fine. Two people can add `30` and `31`
> in parallel and nothing breaks.

That one rule means:

- You never have to reorganize anyone else's work to add yours.
- Inbound links (`../autonomy/09-gnc.md`) stay valid forever.
- The order you *read* the library in lives in the index, not in the filenames.

### Folder = topic band

Each top-level folder is a topic band, numbered **independently from `01`**:

| Folder | Theme |
|---|---|
| `foundations/` | The spine + cross-cutting literacy |
| `autonomy/` | The autonomy & robotics stack + domain verticals |
| `career/` | Job-hunt mechanics + career meta-skills |
| `companies/` | How the giants win |
| `engineering/` | Hardware & physical-engineering breadth |
| `software/` | Production software, compute & infrastructure |
| `mathematics/` | The math & physics under every layer |
| `mindset-and-society/` | The human operating system |
| `information-environment/` | Platforms, cognition, OSINT & OPSEC |
| `general/` | Accessible explainers for a general reader |
| `compute-and-hardware/` | Silicon, power & AI data centers |
| `space/` | Space systems & astronautics |
| `products/` | High-impact tools worth adopting |
| `tooling/` | Power prompts for building with AI |

> The `machine learning/` folder is a **separate** university-course collection, not
> part of the mastery curriculum. Contribute there only for CPSC 5310 materials.

---

## Naming conventions

- **Filename:** `NN-kebab-case-slug.md` — a two-digit number, a hyphen, then a short
  hyphenated slug. Example: `15-motion-planning.md`.
  - `NN` = the next free number in the folder (the scaffolder finds it for you).
  - Some older files use `under_scores`; **match the dominant hyphen style** for new
    files and don't rename existing ones.
- **One guide = one `.md` file.** Don't split a topic across files unless it's genuinely
  two topics.
- **H1 title** is a descriptive headline, optionally with an em-dash subtitle, e.g.
  `# Motion Planning — From Configuration Space to Real-Time Replanning`.

---

## Anatomy of a guide

Every guide follows the same shape so readers can move between them fluidly. The
[template](templates/GUIDE_TEMPLATE.md) has all of this pre-filled:

1. **H1 title** — descriptive, first-principles framing.
2. **"Why this exists" callout** (`>` blockquote) — how the guide relates to the rest
   of the library, with links to 2–4 sibling guides, followed by a one-line
   **"What mastering it makes you."** This is the convention the library actually uses;
   match it rather than inventing a new opener.
3. **Table of Contents** — for anything longer than a few screens.
4. **Body** — numbered or named sections, depth over breadth.
5. **Cross-links** — link generously to related guides with **relative paths**
   (`../mathematics/01-optimization.md`).

---

## Style guide

- **First principles first.** Explain *why* before *how*. Assume a smart reader who
  hasn't seen this specific topic.
- **Anchor every strong claim.** Tie it to a derivation, a source, or code in the repo.
  Don't assert numbers you can't support.
- **Show the math when it earns its place.** Use KaTeX: inline `$...$`, block `$$...$$`.
- **Code in fenced blocks** with a language tag. Keep snippets minimal and runnable.
- **Use relative links** between guides so they survive forks and moves.
- **Plain, direct prose.** Short sentences. Define jargon on first use.
- **Stay accurate over impressive.** If you're unsure, mark it `> TODO:` rather than
  bluffing — a reviewer can help fill it in.
- **No secrets, no export-controlled specifics, no operational targeting detail.** Keep
  everything at the level of open, educational first principles. See
  [`information-environment/`](information-environment) for the OPSEC framing.

---

## Adding a brand-new topic folder

Only do this when a guide genuinely doesn't fit any existing band. **Pitch the idea
first** by opening a
[New topic folder](.github/ISSUE_TEMPLATE/new-topic-folder.yml) issue and waiting for
the owner to approve it. Once approved:

1. Create the folder with a lowercase, hyphenated name (e.g. `cyber/`).
2. Add your first guide as `01-...md`.
3. Add the folder to the table in [`README.md`](README.md) and to
   [`01-mastery-curriculum.md`](01-mastery-curriculum.md).
4. Call it out in your PR description so reviewers know a new band appeared.

---

## Submitting your contribution

1. **Branch** off `main`: `git checkout -b add/<topic-slug>` (or `fix/...`).
2. **Commit** with a clear message: `Add autonomy/30: <title>` or
   `Fix: correct GNSS spoofing detection math in 07-gnss...`.
3. **Open a PR** and fill in the [pull request template](.github/PULL_REQUEST_TEMPLATE.md).
4. A maintainer reviews for accuracy, style, and links. Expect a friendly back-and-forth.

### Not ready to write a full guide?

- **Propose a guide** → open a
  [New guide proposal](.github/ISSUE_TEMPLATE/new-guide-proposal.yml) issue.
- **Report an error or suggest an improvement** → open a
  [Correction / improvement](.github/ISSUE_TEMPLATE/correction-or-improvement.yml) issue.
- **Pitch a new topic band** → open a
  [New topic folder](.github/ISSUE_TEMPLATE/new-topic-folder.yml) issue.

Small, well-scoped PRs merge fastest. A single tight guide beats a sprawling one.

---

## Quality bar (what reviewers check)

- [ ] Filename follows `NN-kebab-case.md` and uses the next free number.
- [ ] No existing guide was renumbered or its links broken.
- [ ] The guide has the H1 title, "Why this exists" callout, and (if long) a ToC.
- [ ] Strong claims are anchored; math/code render correctly.
- [ ] Added a row to [`01-mastery-curriculum.md`](01-mastery-curriculum.md).
- [ ] Relative links resolve; no secrets or export-controlled detail.

---

## Code of Conduct & License

By contributing you agree to the [Code of Conduct](CODE_OF_CONDUCT.md) and to license
your contribution under the repository's [LICENSE](LICENSE) (Creative Commons
Attribution 4.0 — content is free to share and adapt with credit).

Welcome aboard. The library is better with you in it.
