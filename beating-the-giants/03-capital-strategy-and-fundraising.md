# Capital Strategy & Fundraising — Sources, Dilution Math, and Founder Control

> **Why this exists.** Capital is fuel and leash at once. Raise too little and a faster-funded
> rival out-iterates you; raise too much (or from the wrong source) and you lose the control
> that let you move fast in the first place. The library covers personal
> [Financial Literacy](../career/15-financial-literacy-wealth.md) and the
> [Engineer-to-Founder](../career/17-engineer-to-founder.md) leap, but had no guide on how a
> challenger *finances the fight*. This one closes that gap and pairs with
> [Pricing & Unit Economics](02-pricing-and-unit-economics.md) (your economics set how much
> you need) and [Leverage Over Headcount](08-leverage-over-headcount.md) (less burn, less
> raise).
>
> **What mastering it makes you.** Someone who can choose a capital source for its incentives,
> compute dilution and control in their head, and reason honestly about the founder-vs-early-
> employee expected-value tradeoff.

---

## Table of Contents

1. [Capital Is an Incentive Structure, Not Just Money](#1-capital-is-an-incentive-structure-not-just-money)
2. [The Menu of Capital Sources](#2-the-menu-of-capital-sources)
3. [Dilution Math You Can Do in Your Head](#3-dilution-math-you-can-do-in-your-head)
4. [Control: Boards, Votes, and Terms That Bite](#4-control-boards-votes-and-terms-that-bite)
5. [How Much to Raise and When](#5-how-much-to-raise-and-when)
6. [The Founder-vs-Early-Employee Expected Value](#6-the-founder-vs-early-employee-expected-value)
7. [Defense and Deep-Tech Capital](#7-defense-and-deep-tech-capital)
8. [Where to Go Next](#8-where-to-go-next)

---

## 1. Capital Is an Incentive Structure, Not Just Money

Every dollar arrives with a *return expectation and a time horizon attached*, and those terms
shape your decisions long after the cash is spent. Venture capital needs a fund-returning
outcome (a 10×+, sold within ~7–10 years), so VC dollars push you toward swing-for-the-fences
growth whether or not that fits your market. A customer's pre-payment wants a working product
and aligns you with revenue. A government contract wants a fielded capability and patience.
**Choose the source whose incentives you'd want even if the money were free.**

This is a corollary of the principal–agent logic in
[Economics & Markets](../foundations/13-economics-and-markets.md): you are taking on a
principal whose objective function you will partly inherit.

## 2. The Menu of Capital Sources

| Source | What it wants | Dilution | Speed | Best when |
|---|---|---|---|---|
| Bootstrapping / revenue | Profit, autonomy | None | Slow | Strong early unit economics |
| Customer pre-payment / contracts | A working product | None (non-dilutive) | Medium | Clear buyer, defensible scope |
| Grants (SBIR, research) | Capability, milestones | None | Slow | Deep-tech, dual-use |
| Angels / pre-seed | Big outcome, founder bet | Low | Fast | Earliest, story-stage |
| Venture capital | 10×+ exit in fund life | Medium–high | Medium | Winner-take-most markets, capital is the accelerant |
| Venture debt | Repayment + warrants | Low | Medium | Extending runway post-revenue |
| Strategic / corporate VC | Access, option on you | Medium | Slow | Distribution > cash, eyes open on conflicts |
| Sovereign / defense funds | Capability + sovereignty | Varies | Slow | Hard-tech with national relevance |

The capital-efficiency lesson recurs throughout the [companies](../companies/01-how-the-giants-win.md)
case studies: the *least*-diluted path that still keeps pace with rivals is almost always the
best one. Non-dilutive capital (revenue, contracts, grants) is strictly better when you can
get it, because it buys time *without selling control or upside*.

## 3. Dilution Math You Can Do in Your Head

The fundamental identity of a priced round:

$$\text{Post-money} = \text{Pre-money} + \text{Amount raised}, \qquad
\text{Dilution} = \frac{\text{Amount raised}}{\text{Post-money}}$$

Raising \$4M on a \$16M pre-money is a \$20M post-money and **20% dilution** — every existing
shareholder's ownership is multiplied by 0.8. Two facts founders consistently get wrong:

- **Dilution compounds.** Three rounds of 20% leave founders with $0.8^3 \approx 51\%$ of what
  they started with, *before* the option pool. Each round's pool top-up usually comes out of
  the *pre-money* — i.e. mostly out of the founders.
- **Price matters more than people think, but not infinitely.** A higher valuation reduces
  dilution but ratchets up expectations and can set a down-round trap if you can't grow into
  it. Optimize for the *right* investor and clean terms over the last turn of valuation.

A useful sanity check before any raise: simulate the cap table through to a plausible exit
and look at what *you* own at the end. If the answer is demoralizing, you're either raising
too much, too early, or at too low a price.

## 4. Control: Boards, Votes, and Terms That Bite

Ownership percentage and *control* are different things, and losing the second is how
fast-moving founders become passengers. Watch:

- **Board composition.** Who controls the board controls the CEO's job and the big decisions.
  Founders routinely give up board control well before they give up 50% of equity.
- **Liquidation preferences.** A 1× non-participating preference is standard; participating or
  multiple preferences mean investors take their money *and* a share of the rest — which can
  zero out common stock in a modest exit.
- **Protective provisions / consent rights.** Vetoes over budgets, hires, financings, or a
  sale. These quietly transfer operational control.
- **Anti-dilution (ratchets).** Protects investors in a down round by shifting more dilution
  onto founders and employees precisely when things are hardest.

The throughline: **read terms for who decides, not just who owns.** Speed — the underdog's
core weapon ([guide 05](05-speed-as-compound-advantage.md)) — depends on keeping decision
rights concentrated enough to act without a committee.

## 5. How Much to Raise and When

Raise to hit the **next value-inflection milestone plus a margin of safety**, not to a round
number or a runway fashion. Over-raising feels like winning and is often the opposite: it
dilutes more, sets a valuation you must outgrow, and removes the constraint that forces
efficiency (Parkinson's law applies brutally to burn).

A practical frame:
- Identify the milestone that materially de-risks the company (a working product, first
  paying customers, a fielded pilot, a unit-economics proof).
- Estimate the burn to get there with margin, using the **burn multiple** from
  [Pricing & Unit Economics](02-pricing-and-unit-economics.md) as a discipline.
- Time the raise from *strength* — when metrics are improving — not when the runway forces it,
  because desperation is visible and prices it in against you.

## 6. The Founder-vs-Early-Employee Expected Value

A question this library's audience faces directly (the
[Engineer-to-Founder](../career/17-engineer-to-founder.md) decision): is it better to found,
or to be early employee #5? A back-of-envelope expected-value comparison clarifies it.

Let a successful exit value the company at $X$. The founder might hold ~20% at exit after
dilution; an early employee might hold ~0.5–1%. But the *probabilities and the downside
differ sharply*:

$$\mathbb{E}[\text{founder}] = p_f \cdot s_f \cdot X - C_{\text{opportunity+risk}}, \qquad
\mathbb{E}[\text{employee}] = p_e \cdot s_e \cdot X$$

where $s$ is ownership share, $p$ is the probability of a meaningful outcome *for that person*
(a founder can be fired and lose unvested equity; an employee can leave with vested stock),
and $C$ captures the founder's larger opportunity cost and personal risk. The honest takeaways:

- The founder's *upside* is ~20–40× the employee's per-share, but their *risk-adjusted,
  opportunity-cost-adjusted* EV is far closer than the headline equity numbers suggest.
- Early-employee equity is often the **better risk-adjusted bet** for building wealth, while
  founding is the better bet for control, learning rate, and the tail outcome.
- Both dominate "comfortable senior employee at a giant" on *learning per year* — which, per
  [Career Capital](../career/14-job-search-career-capital.md), is the asset that compounds.

The point is not a single answer but to *run the numbers for your own situation* rather than
defaulting to the romantic story in either direction.

## 7. Defense and Deep-Tech Capital

Hard-tech and defense have a distinctive capital stack: **non-dilutive first** (SBIR/STTR,
research grants, OTAs, customer-funded development per
[Defense Acquisition](../foundations/07-defense-acquisition.md)), then dilutive growth capital
once a capability is proven. The new defense cohort
([The New Defense-Tech Cohort](../companies/19-new-defense-tech-cohort.md)) succeeded by
stacking these: grants and contracts to fund the science and field early units, venture to
fund scale, and dual-use commercial revenue to fund iteration speed the primes can't match.
Sovereignty concerns also create patient, mission-aligned capital that a pure-commercial
startup can't access — at the cost of slower processes and export-control constraints
([guide 07](07-regulatory-judo-and-export-control.md)).

## 8. Where to Go Next

- The economics that set how much you need: [Pricing & Unit Economics](02-pricing-and-unit-economics.md).
- Spend less to need less: [Leverage Over Headcount](08-leverage-over-headcount.md).
- The story that closes the round: [Narrative as Strategy](04-narrative-as-strategy.md).
- Personal money mechanics: [Financial Literacy & Wealth](../career/15-financial-literacy-wealth.md).

---

*This guide is **AI-assisted synthesis** (AI tools), curated and
reviewed — a starting point, not a primary source. Verify anything load-bearing before you
rely on it. See the [README](../README.md) for the full note.*
