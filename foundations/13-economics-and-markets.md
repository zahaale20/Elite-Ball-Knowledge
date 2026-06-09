# Module 118 — Economics & Markets (First Principles)

> **Why this file exists.** Engineers are trained to optimize physical objective functions —
> minimize mass, maximize thrust — and then are baffled when the "better" product loses, the
> well-engineered company goes bankrupt, or the obviously-correct decision never gets funded. The
> missing variable is almost always **economics**: the study of how people and organizations
> allocate scarce resources under incentives. Economics is not "the stock market"; it is the
> operating system of every decision involving cost, value, scarcity, and incentives — which is to
> say, every decision that matters in a company, a program, or a market. An engineer who is
> economically illiterate is permanently confused about why good things fail and bad things win.
>
> **What mastering it makes you.** The person who can see the *incentive structure* behind a
> behavior, price a tradeoff correctly, reason about markets and competition, and tell the
> difference between a real moat and a temporary lead. It is the literacy that turns "I built a
> better thing" into "I built a thing that wins" — and it is the substrate under
> [08-foundations-company-strategy-moat.md](08-company-strategy-moat.md) and the entire
> companies band.

**Companion practice.** This is the first-principles layer beneath
[08-foundations-company-strategy-moat.md](08-company-strategy-moat.md), the
[companies band (37–49)](../companies/01-how-the-giants-win.md), and
[07-foundations-defense-acquisition.md](07-defense-acquisition.md) (the defense market is a *very*
strange market and you must know normal markets to see how). Decision-theoretic tools it relies on
are in [15-decision-making-and-rationality.md](15-decision-making-and-rationality.md); the
personal-finance application is [14-personal-finance-and-the-math-of-wealth.md](14-personal-finance-and-the-math-of-wealth.md).

---

## Table of Contents

1. [Scarcity, opportunity cost, and the economic way of thinking](#1-scarcity-opportunity-cost-and-the-economic-way-of-thinking)
2. [Marginal thinking — the engineer's natural ally](#2-marginal-thinking--the-engineers-natural-ally)
3. [Supply, demand, and prices as information](#3-supply-demand-and-prices-as-information)
4. [Incentives: the master key](#4-incentives-the-master-key)
5. [Market structures and competition](#5-market-structures-and-competition)
6. [Market failures: externalities, public goods, asymmetric information](#6-market-failures-externalities-public-goods-asymmetric-information)
7. [Firms, costs, and economies of scale](#7-firms-costs-and-economies-of-scale)
8. [Moats: the economics of durable advantage](#8-moats-the-economics-of-durable-advantage)
9. [Macro literacy: growth, inflation, interest rates, cycles](#9-macro-literacy-growth-inflation-interest-rates-cycles)
10. [The defense market as a special case](#10-the-defense-market-as-a-special-case)
11. [Failure modes and economic fallacies](#11-failure-modes-and-economic-fallacies)
12. [Practice this month](#12-practice-this-month)
13. [Sources & Citations](#sources--citations)

---

## 1. Scarcity, opportunity cost, and the economic way of thinking

Economics begins with one unavoidable fact: **resources are scarce and wants are not.** Every choice
to use a resource one way is a choice *not* to use it another way. This gives rise to the single most
important idea in the whole field:

**Opportunity cost** — the true cost of anything is *the value of the best alternative you gave up to
get it.* The cost of a year spent building feature A is not the salary spent; it is feature B you
*didn't* build, and the market position you didn't take. The cost of $100k of cash sitting idle is
the return it could have earned. Engineers routinely undercount opportunity cost because it's
invisible — it never shows up on an invoice — but it is the *real* cost of every decision.

The "economic way of thinking" is a posture: people respond to incentives; there are no solutions,
only tradeoffs; every benefit has a cost; the relevant question is always "compared to what?" and
"and then what?" (second-order effects). Hold these and you will out-reason people with far more
domain knowledge but no economic frame.

> **Senior tell.** A junior asks "can we afford to do this?" A senior asks "what's the opportunity
> cost — what do we *not* do if we do this?" The budget is rarely the binding constraint; attention
> and time are.

---

## 2. Marginal thinking — the engineer's natural ally

Economics is, mathematically, the discipline of **derivatives** — and engineers already think this
way, they just need to apply it to value. The right decision question is almost never "is X good?"
but **"is one more unit of X worth one more unit of cost?"** — i.e., marginal benefit vs marginal
cost. You keep doing a thing until the marginal benefit equals the marginal cost; that's the
optimum, and it's the same first-order condition as any engineering optimization.

This dissolves a huge class of confusion:

- **Sunk costs are irrelevant to the decision.** Money or effort already spent and unrecoverable
  should not enter the forward-looking margin. "We've already put two years into this architecture"
  is not a reason to continue; only future marginal benefit vs future marginal cost is. The
  **sunk-cost fallacy** — throwing good money after bad to "not waste" the bad — is one of the most
  expensive cognitive errors in engineering organizations.
- **Averages mislead; margins decide.** A product line that's profitable *on average* may be losing
  money *at the margin* (the next unit costs more than it earns). Optimize the margin.
- **Diminishing marginal returns** are nearly universal: the second engineer on a task adds less
  than the first, the tenth far less. This is why "throw more people at it" fails (Brooks's Law) and
  why you stop adding resources well before "more would still help a little."

---

## 3. Supply, demand, and prices as information

The supply-and-demand model is the most useful single diagram in social science. Demand slopes down
(higher price → less wanted); supply slopes up (higher price → more produced); the **equilibrium
price** clears the market.

```
   price
     │  S (supply)
     │ ╱
  P* │╳ ← equilibrium: quantity supplied = quantity demanded
     │ ╲
     │   D (demand)
     └──────────────── quantity
          Q*
```

But the deep insight, Hayek's, is that **a price is a compressed signal carrying distributed
information no central planner could assemble.** When cobalt gets scarce, its price rises, and that
single number tells every battery engineer on Earth to economize on cobalt and every miner to dig
more — without anyone knowing *why* or coordinating. Prices are how a decentralized system computes
allocation. This is why centrally-planned economies fail at scale: they destroy the information
channel. It's also why "the price is high" is usually *information about scarcity*, not a moral
failing to be fixed by decree (price controls predictably produce shortages by killing the signal).

**Elasticity** measures responsiveness: how much quantity changes when price changes. Inelastic
goods (insulin, fuel) barely respond; elastic goods (one brand among many) respond sharply.
Elasticity governs pricing power, tax incidence, and who bears a cost.

---

## 4. Incentives: the master key

If you remember one word from this module, make it **incentives.** "People respond to incentives" is
the closest thing economics has to a law, and it explains more real-world behavior than any technical
analysis. The corollary is the operating principle of every well-run organization and the epitaph of
every badly-run one: **you get what you reward, not what you want.**

- **Incentives are often misaligned with stated goals.** A team rewarded for "lines of code" writes
  bloat; rewarded for "bugs closed" closes easy bugs and games the metric; a defense contractor paid
  cost-plus has no incentive to control cost. The behavior follows the reward, not the mission
  statement.
- **The principal–agent problem.** Whenever one party (principal) hires another (agent) to act on
  their behalf, their interests diverge and the agent has private information. Executives vs
  shareholders, contractors vs the government, your vendor vs you. Good contracts and org design are
  exercises in *aligning* the agent's incentives with the principal's goal.
- **Goodhart's Law** — "when a measure becomes a target, it ceases to be a good measure." Any metric
  you optimize hard enough gets gamed and decouples from the thing it proxied. This is why metric
  design is so hard and why over-optimizing a single number is dangerous.
- **Perverse incentives** — the cobra effect: a bounty on dead cobras led people to *farm* cobras.
  Reward the proxy and you get the proxy, not the goal.

The practical skill: when you see puzzling behavior, **don't ask "why are they irrational?" — ask
"what are they being rewarded for?"** The behavior is almost always a rational response to an
incentive you hadn't seen. (This is the engine behind much of
[02-politics-navigation.md](../mindset-and-society/02-politics-navigation.md) and
[08-amazon-mechanisms-customer-obsession.md](../companies/08-amazon-mechanisms-customer-obsession.md).)

---

## 5. Market structures and competition

How a market behaves depends on its structure, which sits on a spectrum:

| Structure | Sellers | Pricing power | Example | Key dynamic |
|---|---|---|---|---|
| **Perfect competition** | Many, identical product | None (price-taker) | Commodity grain | Profits competed to ~zero |
| **Monopolistic competition** | Many, differentiated | Some | Restaurants, most software | Differentiation is everything |
| **Oligopoly** | Few | Significant | Defense primes, GPUs, airliners | Strategic interaction (game theory) |
| **Monopoly** | One | High | A patented drug, a utility | Regulation or moat-driven |

The central economic engine is **competition driving profits toward zero.** In a perfectly
competitive market, anyone earning excess profit attracts entrants until profits are competed away.
Therefore **all durable profit comes from some barrier to competition** — a moat (§8). This is the
deepest strategic truth in business: *the goal of strategy is to escape perfect competition.* Peter
Thiel's "competition is for losers" is this idea stated provocatively — you want to be doing
something hard to copy, not fighting in a commoditized red ocean. Oligopoly (few players, strategic
interaction) is where most serious technology and defense markets actually live, which is why game
theory ([11](../mathematics/11-decision-and-game-theory.md)) is the right tool there.

---

## 6. Market failures: externalities, public goods, asymmetric information

Markets allocate efficiently *under conditions that often don't hold*. Where they break is exactly
where policy, regulation, and clever business models live:

- **Externalities** — costs or benefits that fall on third parties not in the transaction. Pollution
  (negative) and R&D spillovers or vaccination (positive). The market over-produces negative
  externalities and under-produces positive ones because the actor doesn't bear/capture the full
  cost/benefit. Remedies: taxes/subsidies (Pigouvian), tradable permits, or assigning property
  rights (Coase).
- **Public goods** — non-excludable and non-rival (national defense, basic research, GPS itself).
  Markets under-provide them because of free-riding — you can't charge people who benefit anyway.
  This is *the* economic justification for government provision of defense, and thus for the entire
  market you may work in.
- **Asymmetric information** — one side knows more than the other. Akerlof's "market for lemons":
  if buyers can't tell good used cars from bad, good cars exit the market and quality collapses.
  Remedies are **signaling** (a warranty, a credential, a clearance) and **screening** (the buyer
  designs a test). Much of hiring, insurance, and procurement is managing information asymmetry.
- **Monopoly power** — under-produces and over-prices relative to the competitive ideal; the
  rationale for antitrust.

Recognizing a market failure is often a *business opportunity*: many great companies exist precisely
because they solved an information asymmetry (eBay's ratings, Carfax) or internalized an externality.

---

## 7. Firms, costs, and economies of scale

Why do firms exist at all, instead of everything being individual market transactions? Ronald Coase's
answer: **transaction costs.** Using the market has costs — finding, negotiating, contracting,
enforcing — and when those exceed the cost of doing it in-house, you build a firm. This single idea
explains the boundary of every company: **make vs buy** is a transaction-cost calculation, and it's
the economic engine behind Tesla's vertical integration
([05](../companies/05-tesla-vertical-integration-data.md)) and Apple's
([07](../companies/07-apple-integration-taste.md)).

Cost structure shapes strategy:

- **Fixed vs variable costs.** Software and hardware-with-big-NRE (non-recurring engineering) have
  huge fixed costs and tiny marginal costs — the first unit costs $100M, the millionth costs $5.
  This creates **economies of scale**: average cost falls as volume rises, so scale is a weapon and
  winner-take-most dynamics emerge.
- **Network effects** — the product gets more valuable as more people use it (Lattice, an OS, a
  marketplace). This is increasing returns to *demand* and produces the strongest moats.
- **Learning curves / Wright's Law** — unit cost falls a predictable percentage with each doubling
  of cumulative production. This is the economic backbone of SpaceX and Tesla: *build more to get
  cheaper to build more.* It's also why being first to volume can be decisive.

---

## 8. Moats: the economics of durable advantage

Since competition destroys profit (§5), the only source of durable value is a **moat** — a
structural barrier that protects returns from competition. Warren Buffett's framing; the canonical
taxonomy:

1. **Economies of scale / cost advantage** — you can profitably underprice anyone smaller (SpaceX,
   Amazon, TSMC).
2. **Network effects** — value grows with users; late entrants face a chicken-and-egg wall
   (marketplaces, platforms, Lattice).
3. **Switching costs / lock-in** — once embedded, ripping you out is painful and risky (enterprise
   software, Palantir's ontology, CUDA in [06](../companies/06-nvidia-platform-ecosystem.md)).
4. **Intangible assets** — brand, patents, regulatory approvals, security clearances, accreditation.
   (In defense, *accreditation and trust* are a real moat — see
   [08](08-company-strategy-moat.md) and [09](09-safety-assurance.md).)
5. **Counter-positioning** — you do something incumbents *can't copy without destroying their own
   business* (software-first defense challengers selling products vs primes' cost-plus model —
   [03](../companies/03-productized-defense.md)).

The strategic question for anything you build is therefore not "is it good?" but **"why won't this
be competed away, and how does the moat get *stronger* as I grow?"** A lead is not a moat; a lead
that compounds (data flywheel, scale, network effects) is. This is the economic core of the entire
companies band.

---

## 9. Macro literacy: growth, inflation, interest rates, cycles

You don't need to be a macroeconomist, but you must be literate enough to not be fooled:

- **GDP / growth** — the size and growth rate of the whole economy. Long-run growth comes almost
  entirely from **productivity** (output per worker), which comes from technology and capital — the
  thing engineers actually create. This is why innovation matters at the civilizational scale.
- **Inflation** — a general rise in prices / fall in money's value. Erodes cash and fixed debts,
  distorts price signals, and is why "just hold cash" silently loses you money every year
  (connects to [14](14-personal-finance-and-the-math-of-wealth.md)).
- **Interest rates** — the price of money/time, set heavily by central banks. *The* master variable
  for valuation: when rates are low, future cash flows are worth more (cheap money → high valuations,
  funded moonshots); when rates rise, the discount rate rises and long-dated bets get crushed. The
  2021→2023 swing in startup funding *was* an interest-rate story. Understanding discounting (a
  future dollar is worth less than a present one) is essential — it's the same time-value-of-money
  math as [14](14-personal-finance-and-the-math-of-wealth.md).
- **Business cycles** — economies oscillate between expansion and recession; credit and sentiment
  amplify the swings. You can't predict the timing, but knowing cycles exist keeps you from
  extrapolating a boom forever (or a bust).
- **Comparative advantage** (Ricardo) — even if one party is better at *everything*, both gain by
  specializing where their *relative* advantage is greatest and trading. This is the economic case
  for trade, for specialization within a team, and for not doing everything yourself.

---

## 10. The defense market as a special case

Everything above assumes a roughly normal market. The defense market violates most of those
assumptions, and you must see *how* to operate in it (full treatment in
[07-foundations-defense-acquisition.md](07-defense-acquisition.md)):

- **A monopsony buyer.** Often there is essentially *one* customer (the government), which inverts
  normal market power and makes the buyer's procurement rules, not consumer demand, the binding
  force.
- **The product is a public good** (§6) funded by taxation, not voluntary purchase, so "willingness
  to pay" is mediated by politics and budgets, not markets.
- **Cost-plus contracting** historically *removed* the incentive to control cost (you're reimbursed
  cost plus a margin → margin grows with cost → perverse incentive, §4). The SpaceX/productized-defense thesis
  is partly an *incentive* arbitrage: sell fixed-price products and capture the efficiency the
  cost-plus incumbents have no reason to chase.
- **Barriers to entry are regulatory and trust-based** (clearances, accreditation, the
  relationships and compliance machinery), not purely technological — which is both the incumbents'
  moat and, when counter-positioned against, their vulnerability.

Knowing normal-market economics is exactly what lets you *see* how strange and exploitable the
defense market is.

---

## 11. Failure modes and economic fallacies

| Fallacy | What it is | Correction |
|---|---|---|
| **Sunk-cost fallacy** | Continuing because of past spend | Only future marginal cost/benefit matters |
| **Ignoring opportunity cost** | Counting only out-of-pocket cost | "Compared to what?" — value the best alternative |
| **Lump-of-labor / fixed-pie** | Believing one's gain is another's loss | Trade and growth are positive-sum |
| **Broken-window fallacy** | Counting the visible benefit, ignoring the unseen cost | Bastiat: account for what is *not* seen |
| **Confusing price with value/cost** | "It's expensive so it's bad/overpriced" | Price is a scarcity signal, not a verdict |
| **Goodhart / metric gaming** | Optimizing a proxy to death | Expect gaming; use balanced, hard-to-game measures |
| **Ignoring incentives** | Assuming people will "do the right thing" | Design the reward; behavior follows it |
| **Static thinking** | "And then what?" never asked | Trace second-order and equilibrium effects |

The meta-lesson, from Bastiat: **the good economist accounts for the effects you *don't* see** — the
opportunity cost, the unseen alternative, the second-order response — while the bad one stops at the
visible first effect. Most economic mistakes are failures of imagination about the unseen.

---

## 12. Practice this month

- **Compute the real opportunity cost** of your current biggest project: not the budget, but the
  next-best thing you and your team are *not* doing.
- **Find one puzzling behavior** at work or in the news and explain it purely through incentives —
  "what is this person/org rewarded for?" Resist calling anyone irrational.
- **Map the moat (or absence of one)** for a product you admire using the §8 taxonomy. Ask whether
  the advantage *compounds* with scale or just exists.
- **Trace one price** (a chip, a metal, GPU rental) and write down what its recent move is *telling*
  you about real-world scarcity.
- **Identify a market failure** (externality, info asymmetry, public good) and sketch a business or
  policy that profits by fixing it.

---

## Sources & Citations

**Canonical works**
- Thomas Sowell — *Basic Economics* — the economic way of thinking, no math, deeply clarifying.
- Charles Wheelan — *Naked Economics* — accessible, modern, broad.
- Frédéric Bastiat — *That Which Is Seen, and That Which Is Not Seen* (free) — opportunity cost and
  the unseen, in the 1850 original.
- Friedrich Hayek — *The Use of Knowledge in Society* (free essay) — prices as information.
- Ronald Coase — *The Nature of the Firm* and *The Problem of Social Cost* — firms and externalities.
- Steven Landsburg — *The Armchair Economist* — marginal thinking and incentives, vividly.
- Peter Thiel — *Zero to One* — competition, monopoly, and escaping the red ocean (strategy lens).
- Hamilton Helmer — *7 Powers* — the rigorous taxonomy of moats.

**Cross-links**
- Strategy application: [08-foundations-company-strategy-moat.md](08-company-strategy-moat.md) and the
  [companies band (37–49)](../companies/01-how-the-giants-win.md).
- Strategic interaction / oligopoly: [11-decision-and-game-theory.md](../mathematics/11-decision-and-game-theory.md).
- Personal application: [14-personal-finance-and-the-math-of-wealth.md](14-personal-finance-and-the-math-of-wealth.md).
- The weird defense market: [07-foundations-defense-acquisition.md](07-defense-acquisition.md).
