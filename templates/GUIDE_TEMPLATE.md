<!--
  GUIDE TEMPLATE
  --------------
  Copy this file into a topic folder and rename it to NN-your-slug.md, where NN is the
  next free number in that folder. Or just run:  ./scripts/new-guide.sh <folder> "Title"
  Then delete these comments and fill in every PLACEHOLDER.
  See CONTRIBUTING.md for the full conventions.
-->

# PLACEHOLDER TITLE — Optional Em-Dash Subtitle

> **Why this exists.** One short paragraph: what this guide teaches, who it's for, and
> how it relates to the rest of the library. Link 2–4 sibling guides so readers can
> navigate, e.g. it builds on [Optimization](../mathematics/01-optimization.md) and
> feeds into [Planning & Decision-Making](../autonomy/10-planning-decision.md).
>
> **What mastering it makes you.** One sentence on the capability a reader walks away with.

**Companion material (optional).** If this guide anchors to code, a dataset, or another
guide, name it here with relative links.

---

## Table of Contents

1. [First Section](#1-first-section)
2. [Second Section](#2-second-section)
3. [Where to Go Next](#3-where-to-go-next)

---

## 1. First Section

Open with the *why* from first principles before the *how*. Assume a smart reader who
has not seen this specific topic.

- Anchor strong claims to a derivation, a source, or repo code.
- Show math only when it earns its place: inline $a^2 + b^2 = c^2$, or block:

$$
\nabla_\theta J(\theta) = \mathbb{E}\big[\nabla_\theta \log \pi_\theta(a\mid s)\, A(s,a)\big]
$$

```python
# Keep code minimal and runnable; tag the language.
def example():
    return "replace me"
```

## 2. Second Section

Depth over breadth. Prefer one topic explained completely to five skimmed.

## 3. Where to Go Next

Close by linking onward to related guides so the library reads as a connected whole,
e.g. [Trajectory Optimization](../autonomy/16-trajectory-optimization.md).

---

*Remember to add a row for this guide to [`01-mastery-curriculum.md`](../01-mastery-curriculum.md).*

*This guide is **AI-assisted synthesis**, curated and
reviewed — a starting point, not a primary source. Verify anything load-bearing before
you rely on it. See the [README](../README.md) for the full note.*
