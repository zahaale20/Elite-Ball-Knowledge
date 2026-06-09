# Module 126 — Law, Contracts & IP for Builders

> **Why this file exists.** Engineers are trained to think the real work is the technology and the
> legal layer is paperwork someone else handles — and that belief routinely destroys careers,
> companies, and inventions. The founder who signed away their IP in an employment agreement they
> didn't read; the startup that died because its co-founders never papered the equity split; the
> engineer who unknowingly carried a competitor's trade secrets across jobs and got sued; the company
> that built its product on a license that forbade exactly that use — these are not rare. **Law is
> the operating system of the commercial and institutional world**, and like any operating system,
> not understanding it doesn't exempt you from its rules; it just means it runs *against* you. You
> don't need to be a lawyer. You need enough literacy to spot the issues, ask the right questions,
> know when you genuinely need a lawyer, and not sign away your future in the meantime.
>
> **What mastering it makes you.** The person who can read a contract and understand what they're
> actually agreeing to, who protects their inventions and their company's IP, who structures a
> venture so it doesn't blow up over predictable legal failures, and who knows the difference between
> "I can handle this myself" and "I need a specialist *now*." In defense and deep-tech especially —
> with ITAR/EAR, government contracts, and IP-heavy products — this literacy is not optional.

**Companion practice.** This module connects to
[07-foundations-defense-acquisition.md](07-defense-acquisition.md) (government contracting, ITAR/EAR,
which are law-heavy), [13-economics-and-markets.md](13-economics-and-markets.md) (contracts as the
machinery that lowers transaction costs and aligns incentives),
[14-personal-finance-and-the-math-of-wealth.md](14-personal-finance-and-the-math-of-wealth.md) and
[17-negotiation-and-persuasion.md](17-negotiation-and-persuasion.md) (equity and deal terms), and
[07-career-security-clearance.md](../career/07-security-clearance.md) (the compliance baseline).

> **Not legal advice.** This is legal *literacy* — concepts and issue-spotting. Law varies by
> jurisdiction and changes; for any real decision with stakes, retain a qualified attorney. The
> single most valuable thing this module can do is help you *recognize when you need one.*

---

## Table of Contents

1. [Why legal literacy is an engineer's responsibility](#1-why-legal-literacy-is-an-engineers-responsibility)
2. [Contracts: what they are and how to read one](#2-contracts-what-they-are-and-how-to-read-one)
3. [The clauses that actually bite](#3-the-clauses-that-actually-bite)
4. [Intellectual property: the four kinds](#4-intellectual-property-the-four-kinds)
5. [Who owns what you make: employment and invention assignment](#5-who-owns-what-you-make-employment-and-invention-assignment)
6. [NDAs, non-competes, and trade secrets](#6-ndas-non-competes-and-trade-secrets)
7. [Software licensing and open source](#7-software-licensing-and-open-source)
8. [Business entities and liability](#8-business-entities-and-liability)
9. [Founders, equity, and the agreements that prevent blowups](#9-founders-equity-and-the-agreements-that-prevent-blowups)
10. [Regulation, liability, and the defense overlay](#10-regulation-liability-and-the-defense-overlay)
11. [When to handle it yourself vs hire a lawyer](#11-when-to-handle-it-yourself-vs-hire-a-lawyer)
12. [Failure modes](#12-failure-modes)
13. [Practice this month](#13-practice-this-month)
14. [Sources & Citations](#sources--citations)

---

## 1. Why legal literacy is an engineer's responsibility

The fiction that "legal is someone else's job" fails for the same reason it fails in ethics
([16](16-ethics-of-force-and-engineering-responsibility.md)): **the consequential decisions get
made at *your* desk, before any lawyer sees them.** You sign the employment agreement that assigns
your inventions. You choose the open-source license that determines whether your company can ship its
product. You carry (or don't) knowledge between jobs. You decide whether to paper the co-founder
agreement. By the time a lawyer is involved, the issue is often already created. Legal literacy is
*issue-spotting*: knowing enough to recognize "this is a legal moment, I should slow down / read
carefully / ask a professional" *before* you act, rather than discovering it in a lawsuit.

The asymmetry is brutal and worth internalizing: the cost of *reading* a contract or asking a lawyer
a question up front is tiny; the cost of the predictable disaster you walk into by not doing so is
enormous and often irreversible. This is pure asymmetric-bet / via-negativa reasoning
([15](15-decision-making-and-rationality.md)) applied to law — a small, cheap action that removes a
fat-tailed downside.

> **Senior tell.** A junior signs documents to "get it over with." A senior *reads* them, knows
> which clauses matter, and treats a signature as the serious, often-irreversible commitment it is.

---

## 2. Contracts: what they are and how to read one

A contract is a legally enforceable agreement — a promise (or set of promises) the law will back with
remedies. The classic elements: an **offer**, **acceptance**, **consideration** (each side gives
something of value — this is why "$1 and other good consideration" appears), and mutual intent to be
bound, between parties with capacity. But the practical skill isn't the doctrine; it's **reading one
without your eyes glazing over.** How to actually read a contract:

- **Read every word before signing. Actually.** "I didn't read it" is not a defense — courts
  generally hold you to what you signed. The boring clauses are where the danger hides precisely
  because no one reads them.
- **Find the obligations: who must do what, by when, and what happens if they don't.** Strip the
  legalese and ask: what am I promising? What are they promising? What are the deadlines and
  conditions?
- **Hunt the risk-allocation clauses** (§3) — these are the ones that determine who eats the loss
  when things go wrong, and they're where the real negotiation lives.
- **Look for what's *missing*** as much as what's present — no termination clause, no IP carve-out,
  no liability cap.
- **Ambiguity is decided against the drafter** (contra proferentem) — but don't rely on that; get it
  clear instead.
- **Definitions matter enormously.** Capitalized terms have specific defined meanings (often buried
  in a definitions section) that can completely change a clause. Read the definitions.
- **The contract overrides assumptions and verbal promises** (the "entire agreement" / integration
  clause means side conversations don't count). If it's not written, it doesn't exist.

---

## 3. The clauses that actually bite

In any contract you sign, a handful of clauses carry most of the real risk. Know these by name:

| Clause | What it does | Why it bites |
|---|---|---|
| **Indemnification** | You agree to cover the other party's losses/legal costs | Can make you liable for far more than the deal's value |
| **Limitation of liability** | Caps (or disclaims) what one side can owe | If *theirs* is capped and *yours* isn't, you bear the risk |
| **Termination** | How/when either side can exit | A deal you can't get out of is a trap |
| **IP assignment / ownership** | Who owns what's created (§5) | Can silently transfer *your* work product |
| **Non-compete / non-solicit** | Restricts where you can work next (§6) | Can lock you out of your own field |
| **Confidentiality / NDA** | What you can't disclose or use (§6) | Overbroad versions can taint your future work |
| **Warranties & representations** | Promises about facts/quality | You're liable if they're false |
| **Governing law & venue / arbitration** | Which law applies, where disputes are heard | Can force you to litigate far away, or waive a jury |
| **Assignment** | Whether the contract can be transferred to others | You may end up bound to a party you never chose |
| **Auto-renewal / evergreen** | Renews unless you cancel in a window | Locks you in by inertia |

The two most dangerous in everyday engineering life are **indemnification** (unbounded downside) and
**IP assignment** (silently giving away your work) — read those twice, every time, and push back on
anything uncapped or overbroad. The general principle of contract negotiation (which is
[17](17-negotiation-and-persuasion.md) applied): contracts allocate **risk** and **incentives**;
the negotiation is fundamentally about *who bears which risk*, and you want symmetry and caps on your
exposure.

---

## 4. Intellectual property: the four kinds

IP is how the law turns intangible creations into ownable, defensible assets — and in a knowledge
economy it's often the *most valuable thing a company owns* (a real moat,
[118 §8](13-economics-and-markets.md)). The four types, each protecting something different:

- **Patents** — protect *inventions* (a novel, non-obvious, useful process, machine, or composition)
  for ~20 years, in exchange for *public disclosure*. Powerful but expensive, slow, and territorial.
  Key traps: an invention disclosed publicly (a paper, a demo, a sale) before filing can become
  *unpatentable* (the US has a 1-year grace period; much of the world does not — file before you
  disclose). Patents are a *right to exclude others*, not a right to practice (you can infringe
  someone else's patent even while holding your own).
- **Copyright** — protects *original expression* fixed in a tangible medium (code, text, designs,
  music) automatically on creation, for a long term. It protects the *expression*, not the
  underlying idea or function. This is what governs software ownership and open-source licenses (§7).
- **Trademarks** — protect *brand identifiers* (names, logos) that distinguish your goods, indefinitely
  if used and defended. About preventing customer confusion, not protecting technology.
- **Trade secrets** — protect *confidential business information* that derives value from being secret
  (the formula, the algorithm, the customer list, the process) for as long as you keep it secret and
  take reasonable steps to protect it. No registration, no expiry — but zero protection once it's out
  (independently discovered or reverse-engineered, it's gone). The strategic choice of *patent vs
  trade secret* (disclose-and-exclude vs keep-secret) is a real one: patent if it's reverse-
  engineerable and you want a defensible term; trade-secret if it's genuinely hideable and you want
  indefinite protection (Coca-Cola's formula).

---

## 5. Who owns what you make: employment and invention assignment

This is the single highest-stakes legal issue for a working engineer, and the one most people sign
away without reading. The default rules and the traps:

- **Work made for hire.** Work you create *within the scope of your employment* generally belongs to
  your **employer**, not you — automatically. The code you write for your job is theirs.
- **Invention assignment agreements** go further: most tech employment contracts include a clause
  assigning to the employer *any* inventions you create — sometimes sweepingly broad ("anything
  related to the company's business," "anything using company resources," even "anything during your
  employment"). **This can capture your nights-and-weekends side project.** Read this clause before
  you sign, and understand that your startup idea may legally belong to your current employer if it
  overlaps with their business or used their resources/time.
- **Carve-outs and prior inventions.** Many agreements let you *list* pre-existing inventions to
  exclude them — *use this*. If you have prior IP or a side project, disclose and exclude it in
  writing at signing, or risk it being swept in. Some jurisdictions (e.g. California Labor Code §2870)
  legally limit how far assignment can reach (it can't capture truly independent work done on your own
  time with your own resources unrelated to the employer's business) — but you must still navigate it
  carefully.
- **The clean-hands move for a side venture:** do it on your own time, your own equipment, unrelated
  to your employer's business, disclose where required, and — if it's serious — get it reviewed. The
  graveyard of startups killed by a former employer's IP claim is large and entirely avoidable.

This is also why **bringing your prior employer's code, documents, or trade secrets to a new job is
radioactive** (§6) — it exposes you and your new employer to trade-secret litigation. Leave with your
skills and general knowledge; leave their *materials* behind.

---

## 6. NDAs, non-competes, and trade secrets

The cluster of agreements that govern what you can take, say, and do next:

- **NDAs (non-disclosure agreements / confidentiality).** You agree not to disclose or use the other
  party's confidential information. Standard and reasonable in principle, but watch for *overbroad*
  ones that define "confidential" so widely they constrain your future work, or that lack a time
  limit or carve-outs (for information you already knew, that's public, or independently developed).
  A mutual NDA is more balanced than a one-way one.
- **Non-competes.** Agreements not to work for competitors (or start one) for a period after leaving.
  Their enforceability varies *enormously* by jurisdiction — some (notably California) largely *void*
  them; others enforce reasonable ones; the US FTC has moved to restrict them. Never assume a
  non-compete is either toothless *or* ironclad — it depends on where you are and the specific terms.
  Don't sign one casually, and get advice before relying on (or violating) one.
- **Non-solicitation.** Narrower — you agree not to poach the company's employees or customers for a
  period. Generally more enforceable than non-competes.
- **Trade-secret law** (§4) is the backstop even *without* an NDA: misappropriating a trade secret
  (taking it improperly, or using it knowing it was improperly obtained) is independently unlawful
  (e.g. the US Defend Trade Secrets Act). This is the legal teeth behind "don't take materials between
  jobs," and it's why companies care intensely about departing engineers.

The practical posture: **your skills, expertise, and general know-how are yours and portable; the
employer's specific confidential materials, code, and documented trade secrets are not.** Keep that
line clean and most of this risk evaporates.

---

## 7. Software licensing and open source

Every line of third-party code you incorporate comes with a *license* — a contract governing how you
may use it — and getting this wrong can force you to open-source your proprietary product or expose
you to infringement. The literacy:

- **There is no "it's on GitHub so it's free."** Code without a license is, by default, "all rights
  reserved" — you have *no* right to use it. A license is what *grants* you rights.
- **Permissive licenses** (MIT, BSD, Apache 2.0) let you use, modify, and redistribute — including in
  closed-source products — with minimal obligations (usually: keep the copyright notice; Apache 2.0
  adds a patent grant). These are generally safe for commercial/proprietary use.
- **Copyleft licenses** (GPL, AGPL, LGPL) require that derivative works be released under the *same*
  license — i.e., if you build on GPL code and distribute it, you may have to **open-source your own
  code**. The **AGPL** extends this even to software provided over a network (SaaS). Using strong
  copyleft in a proprietary product without understanding it is how companies get forced to either
  open-source or rip-and-replace. *This is a real, recurring, expensive mistake.*
- **License compatibility and the patent/defense overlay.** Licenses can be incompatible with each
  other; and in **defense/ITAR** contexts, open-source contribution and use raise additional
  export-control and supply-chain (SBOM) concerns ([07](07-defense-acquisition.md)).
- **The discipline:** track your dependencies and their licenses (a software bill of materials),
  know which licenses your product can tolerate, and treat "what license is this?" as a required
  question before adopting any third-party code. Your own choice of license, when you *publish* code,
  similarly determines how others — including competitors — may use it.

---

## 8. Business entities and liability

If you ever start or join a venture, the *legal structure* matters enormously, primarily because of
**liability** and **taxes**:

- **The core reason entities exist: limited liability.** A sole proprietorship or general partnership
  exposes your *personal* assets to the business's debts and lawsuits. Forming a corporation or LLC
  creates a separate legal "person" that — if you respect its formalities — shields your personal
  assets behind the "corporate veil." This single feature is why you almost never run a real business
  as yourself.
- **The common forms** (US-centric; analogues exist elsewhere): **LLC** (flexible, pass-through
  taxation, simple — good for many small businesses); **S-corp** (pass-through with payroll-tax
  nuances); **C-corp** (separate taxation, but the *required* form for venture-backed startups
  because investors and stock options need it — Delaware C-corp is the startup default).
- **Piercing the corporate veil.** The liability shield is *not* absolute — courts can pierce it if
  you commingle personal and business funds, don't follow formalities, or use the entity for fraud.
  Keep finances separate and observe the formalities, or the protection you set up evaporates.
- **Match the entity to the goal.** A lifestyle consultancy and a venture-backed deep-tech startup
  want different structures. Getting this right early is cheap; restructuring later (or fixing a bad
  early choice) is expensive and sometimes founder-fatal.

---

## 9. Founders, equity, and the agreements that prevent blowups

A huge fraction of startup deaths are *legal/relational* failures, not technical or market ones — and
they're almost all preventable with a few documents signed *early*, while everyone still likes each
other:

- **Founder agreement + vesting.** Split equity *and put it on a vesting schedule* (classically 4
  years with a 1-year cliff) from day one. Without vesting, a co-founder who leaves after three months
  can walk away owning a third of the company forever — a catastrophe that has killed many startups.
  Vesting means you *earn* your equity over time; it protects the committed founders.
- **Paper everything, even (especially) among friends.** "We'll figure out equity later" and
  handshake deals between friends are how friendships *and* companies die. The discomfort of the
  early explicit conversation is trivial next to the lawsuit. Get the cap table, roles, IP
  assignment (founders must assign their IP *to* the company), and decision rights in writing.
- **Understand the financing instruments** ([119 §9](14-personal-finance-and-the-math-of-wealth.md)):
  SAFEs and convertible notes (early), priced equity rounds, **dilution** (each round shrinks your
  percentage), **liquidation preferences** (investors get paid first — a big "exit" can pay founders
  far less than the headline), **option pools**, and **vesting**. Signing a term sheet without
  understanding these is signing blind.
- **Get a real startup lawyer for formation and financings.** This is squarely in the "hire a
  professional" zone (§11) — the cost is small and the standard documents (e.g. YC's SAFE, standard
  incorporation) are well-trodden, but the failure modes are company-ending.

---

## 10. Regulation, liability, and the defense overlay

Beyond contracts and IP, builders operate inside a web of regulation and liability that's especially
dense in defense and physical/autonomous products:

- **Product liability.** If you build physical things (or autonomous systems that act in the world),
  you can be liable for harm they cause — under negligence (you didn't exercise reasonable care) or
  strict liability (liable for a defective product regardless of fault). This is the *legal*
  counterpart to the safety engineering of [09](09-safety-assurance.md) and the ethics of
  [16](16-ethics-of-force-and-engineering-responsibility.md): your design and testing rigor is also
  your liability defense, and your decision logs are evidence.
- **Regulatory regimes** govern what you can build and sell: the FAA (drones/airspace), FCC
  (RF/spectrum — [03](../engineering/03-rf-and-comms-systems.md)), and sector-specific rules. "Move
  fast and break things" collides with regulated, safety-critical domains, and ignorance of the
  applicable regime is not a defense.
- **The defense overlay — ITAR/EAR export controls.** This is the big one for this curriculum's
  domain. Defense-related technology and technical data are **export-controlled**: ITAR (munitions)
  and EAR (dual-use) restrict not just shipping hardware abroad but *sharing technical data* with
  foreign persons — even a conversation or a GitHub repo can be a "deemed export." Violations carry
  severe criminal penalties. If you work in defense, you *must* know which of your work is controlled
  and handle it accordingly ([07](07-defense-acquisition.md),
  [07](../career/07-security-clearance.md)). Government contracting adds another whole legal layer
  (FAR/DFARS, data rights, compliance) that is genuinely specialist territory.
- **Data and privacy law** (GDPR, CCPA, and sectoral rules) governs any system that collects personal
  data — increasingly relevant as autonomy systems sense the world.

---

## 11. When to handle it yourself vs hire a lawyer

Legal literacy's most important output is *calibration* about your own limits. A rough guide:

**You can usually handle yourself (with literacy + good templates):**
- Reading and understanding standard agreements before signing.
- Standard NDAs and simple, low-stakes contracts using vetted templates.
- Choosing an open-source license for a personal project.
- Knowing what questions to ask and what red flags to escalate.

**Hire a lawyer (the cost is small vs the downside):**
- Anything with significant money, equity, or liability at stake.
- Company formation, founder agreements, and any financing round.
- Patent filings and serious IP strategy.
- Employment agreements with broad IP-assignment or non-compete terms you're worried about.
- Anything involving litigation, a dispute, or a threat.
- Anything defense/ITAR/government-contract related — specialist territory, full stop.
- Any contract you don't fully understand where the stakes are real.

The meta-rule: **the worse the downside and the less you understand it, the more you need a
professional** — and the up-front cost of an hour of a lawyer's time is almost always trivial against
the asymmetric risk of getting a high-stakes legal decision wrong ([120 §9](15-decision-making-and-rationality.md)).
Penny-wise-pound-foolish on legal advice is one of the most expensive false economies there is.

---

## 12. Failure modes

| Failure mode | What it is | Fix |
|---|---|---|
| **Not reading what you sign** | Signing on trust/inertia | Read every word; "I didn't read it" is no defense |
| **Ignoring IP assignment** | Side project secretly owned by employer | Read the clause; carve out prior/independent work in writing |
| **Carrying materials between jobs** | Bringing ex-employer's code/secrets | Take skills, not materials; trade-secret law is real |
| **Misusing copyleft** | GPL/AGPL forcing your code open | Track dependency licenses; know what your product can tolerate |
| **No founder vesting** | Departing co-founder keeps full equity | 4-year vesting, 1-year cliff, from day one |
| **Handshake deals** | Unpapered equity/roles among friends | Paper everything early, especially with friends |
| **Running a business as yourself** | Personal assets exposed | Form an entity; respect the formalities |
| **Ignoring ITAR/EAR** | Treating defense tech as shareable | Know what's controlled; severe penalties for getting it wrong |
| **DIY on high-stakes law** | Saving on a lawyer, courting disaster | Match professional help to the downside |
| **Unbounded indemnification** | Agreeing to uncapped liability | Cap and balance risk-allocation clauses |

---

## 13. Practice this month

- **Read your own current employment agreement** — specifically the IP-assignment, confidentiality,
  and any non-compete clauses. Understand exactly what you've assigned and what (if anything) you
  carved out. If you have a side project, check whether it's at risk.
- **Audit one project's open-source dependencies** for their licenses. Are any copyleft (GPL/AGPL)?
  Could any force obligations you didn't intend?
- **Read one real contract closely** (an NDA, a ToS, a lease) and identify the §3 clauses that bite —
  indemnification, liability cap, termination, governing law. Practice issue-spotting.
- **Pick the IP strategy** for one invention or idea you have: patent vs trade secret vs copyright —
  and articulate *why*, including the disclosure timing trap.
- **If you're near a venture:** sketch the entity choice and a founder/vesting structure, then list
  exactly which items you'd take to a startup lawyer (§9, §11).
- **If you work in defense:** identify which parts of your work are likely ITAR/EAR controlled and
  confirm you're handling technical data correctly.

---

## Sources & Citations

**Canonical / practical works**
- Constance Bagley & Craig Dauchy — *The Entrepreneur's Guide to Business Law* — the standard,
  comprehensive reference for founders and builders.
- Brad Feld & Jason Mendelson — *Venture Deals* — term sheets, equity, dilution, liquidation
  preferences; essential for anyone touching startup financing.
- Stephen Fishman (Nolo) — *Patent It Yourself* and Nolo's IP/business guides — accessible, practical
  IP and entity literacy.
- Charles Petit / "Contract drafting" references and the **Choose a License** site
  (https://choosealicense.com) and the **Open Source Initiative** (https://opensource.org) for
  software licensing.
- Y Combinator's legal resources and standard documents (SAFE, formation) — https://ycombinator.com
  — the well-trodden startup defaults.

**Official / authoritative sources**
- USPTO (https://uspto.gov) — patents and trademarks.
- U.S. Copyright Office (https://copyright.gov).
- Directorate of Defense Trade Controls (ITAR) and Bureau of Industry and Security (EAR) — export
  control, the defense overlay (see [07-foundations-defense-acquisition.md](07-defense-acquisition.md)).

**Cross-links**
- Government contracting, ITAR/EAR context: [07-foundations-defense-acquisition.md](07-defense-acquisition.md),
  [07-career-security-clearance.md](../career/07-security-clearance.md).
- Contracts as incentive/risk machinery; IP as a moat: [13-economics-and-markets.md](13-economics-and-markets.md).
- Equity terms and valuation: [14-personal-finance-and-the-math-of-wealth.md](14-personal-finance-and-the-math-of-wealth.md),
  [06-career-negotiation-compensation.md](../career/06-negotiation-compensation.md).
- Negotiating contract terms: [17-negotiation-and-persuasion.md](17-negotiation-and-persuasion.md).
- Product liability ↔ safety/ethics: [09-foundations-safety-assurance.md](09-safety-assurance.md),
  [16-ethics-of-force-and-engineering-responsibility.md](16-ethics-of-force-and-engineering-responsibility.md).
- Asymmetric-risk reasoning behind "hire the lawyer": [15-decision-making-and-rationality.md](15-decision-making-and-rationality.md).
