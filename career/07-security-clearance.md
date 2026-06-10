# Security Clearance & the SF-86 Process

> The clearance is the gate. For a huge fraction of defense autonomy work —
> a leading defense-technology company, Boeing, Lockheed, Northrop, the classified side of SpaceX, Shield AI —
> your code, your drone stack, and your résumé don't matter until you can be
> trusted with controlled information. This file is the operator's manual for
> that gate: what clearances are, how the investigation actually works, what the
> adjudicators look for, and how to present yourself as **clearable** today and
> **cleared** as fast as possible. [03-career-software-engineering.md](03-software-engineering.md) §1
> gives the one-paragraph version; this is the full system.

This is not legal advice and it is not about *gaming* the system. The single most
durable strategy for getting and keeping a clearance is to **live a clearable
life and tell the truth on the form.** Everything below serves that.

---

## 0. The One-Paragraph Version (If You Read Nothing Else)

If you are a **U.S. citizen** with a **clean criminal record**, **managed
finances**, **no current illegal drug use**, and **limited/declarable foreign
entanglements**, you are *clearable today*. You cannot grant yourself a
clearance — a **sponsoring employer** initiates it after they hire you. So your
job right now is two-fold: (1) keep your life clearable, and (2) signal
"U.S. citizen, clearable, willing to undergo investigation" clearly on your
résumé and in screening calls. The rest of this guide makes each of those words
precise.

---

## 1. Why This Exists: Controlled Information

The U.S. government classifies information whose unauthorized disclosure would
damage national security. The damage tiers map directly to clearance levels:

| Classification | Damage from unauthorized disclosure | Clearance to access |
|---|---|---|
| **Confidential** | "Damage" | Confidential (rare standalone today) |
| **Secret** | "Serious damage" | Secret |
| **Top Secret** | "Exceptionally grave damage" | Top Secret |
| **SCI / SAP** | Compartmented sources, methods, programs | TS + SCI eligibility / program read-in |

A clearance is a **judgment about you as a person**: that you are reliable,
trustworthy, of good character, and not vulnerable to coercion or poor judgment.
It is *not* a reward for being smart. A brilliant engineer with hidden debt and
undisclosed foreign contacts is a worse clearance risk than a mediocre one who is
boring, solvent, and honest. Internalize that framing — it explains every
adjudicative decision below.

> Mental model: the investigator is not asking "is this person good?" They are
> asking "if a foreign intelligence service wanted leverage over this person,
> what would they find — and did the person hide it from us?"

---

## 2. Citizenship: The Hard Prerequisite

- **U.S. citizenship is required for virtually all clearances.** No clearance
  pathway exists for non-citizens for classified work. A green card is not enough.
- Dual citizenship is **not automatically disqualifying**, but it is a flag under
  the *Foreign Preference* guideline. Actively *exercising* foreign citizenship
  (using a foreign passport, voting abroad, serving in a foreign military, taking
  foreign government benefits) is the problem — not the mere existence of dual
  status. Many people clear after agreeing to **renounce/relinquish** a foreign
  passport.
- **ITAR / EAR** (export-control law) separately restricts who can touch a lot of
  defense hardware and technical data to **U.S. persons** (citizens + lawful
  permanent residents), independent of clearance. So even *uncleared* defense
  engineering jobs often require U.S.-person status.
- If you are **not** a U.S. citizen: target the (smaller) set of commercial,
  ITAR-exempt, or dual-use roles — see [03-career-software-engineering.md](03-software-engineering.md)
  for which new-defense roles are reachable, and consider naturalization timing
  as a deliberate career move.

> Action: confirm your status in writing for yourself — citizen / naturalized /
> dual. If dual, decide now whether you'd relinquish the foreign passport for a
> TS/SCI role. Having that answer ready removes friction later.

---

## 3. The Clearance Ladder

You don't pick your level — the **position** does. A job is designated at a level;
you're investigated to that level. Know the ladder so you can read job postings.

### 3.1 Public Trust (not technically a "clearance")
- For positions of **trust** that handle sensitive-but-unclassified data or
  systems (IT, finance, PII). Tiers: **Tier 1** (low risk) and **Tier 2 / Tier 4**
  (moderate / high risk public trust).
- Investigated, adjudicated, but **does not grant access to classified material.**
- Common entry point for government IT and some contractor support roles.

### 3.2 Secret
- The workhorse clearance for defense engineering. **Most** defense-tech and prime
  engineering roles that need clearance start here.
- Investigation tier: **Tier 3** (formerly NACLC). Reinvestigation historically
  every ~10 years; now folded into **continuous vetting** (see §7).
- Covers a **10-year** scope of your history (residences, employment, etc.).

### 3.3 Top Secret (TS)
- For "exceptionally grave damage" information. Investigation tier: **Tier 5**
  (formerly SSBI — Single Scope Background Investigation).
- **Deeper and broader** than Secret: subject interview, more references,
  expanded financial review, foreign-contact scrutiny.
- Covers a **10-year** scope but investigated far more intensively, including an
  **Enhanced Subject Interview**.

### 3.4 TS/SCI (Sensitive Compartmented Information)
- TS clearance **plus** eligibility for SCI, then **read-in** to specific
  compartments on a strict **need-to-know** basis.
- Granted/administered through the intelligence community; access controlled per
  program. You can hold TS but not be SCI-eligible, or be SCI-eligible but not
  read into a given compartment.

### 3.5 Polygraph (an add-on, not a level)
- Some TS/SCI billets require a **CI (counterintelligence) polygraph** (focused on
  espionage, foreign contact, mishandling) or a **full-scope / lifestyle
  polygraph** (adds personal conduct, drug use, criminal history).
- Polygraph is most common at the three-letter agencies (NSA, CIA, NRO) and some
  highly classified defense programs ("SAPs" — Special Access Programs).

```
Public Trust ── Secret ── Top Secret ── TS/SCI ── + Polygraph (CI / full-scope)
 (Tier 1/2)     (Tier 3)   (Tier 5)      (IC adj.)   (program-specific)
   ▲ no classified         ▲ "the real one for engineers"   ▲ deepest scrutiny
```

> Reality for a builder like you: aim to be **hired into a Secret-designated
> role**, perform, then let the employer upgrade you to TS / TS/SCI as program
> needs grow. Each step you already hold makes you dramatically more hireable —
> an active clearance is one of the most valuable line items on a defense résumé.

---

## 4. SAPs, Caveats, and "Need to Know"

Two concepts trip up newcomers:

- **Need-to-know** is *orthogonal* to clearance level. Holding TS does **not**
  entitle you to all TS material — only what your job requires. Compartments and
  SAPs enforce this.
- **Special Access Programs (SAPs)** layer additional controls (special read-ins,
  unacknowledged or "waived" programs). Leading defense-tech firms and primes like Lockheed/Northrop run plenty of
  SAP work. You're "read in" to a program with a separate briefing and "read out"
  when you leave it.

You don't apply to these. They find you once you're trusted and positioned.

---

## 5. The Form: SF-86 / e-QIP / eApp

The **SF-86 (Standard Form 86, "Questionnaire for National Security Positions")**
is the foundational document. You complete it electronically through **e-QIP**
(being replaced by **eApp** on the NBIS platform). It is long (often 100+ pages
generated), detailed, and **everything you write is verified.**

### 5.1 What the SF-86 asks (major sections)
| Area | What you must provide | Common pain point |
|---|---|---|
| Identity | Names, aliases, SSN, DOB, place of birth | Maiden/former names |
| **Residences** | Every address, ~10 years, with **verifiers** | Forgotten short-term moves |
| **Employment** | Every job, gaps explained, supervisors | Unexplained gaps, contact info |
| Education | Schools, degrees, dates | Out-of-country study |
| **Foreign contacts** | Close/continuing foreign nationals | Underreporting friends/family |
| **Foreign travel** | Personal trips abroad, ~7–10 years | Forgetting border-hop trips |
| **Foreign activities** | Foreign property, business, bank accounts | Crypto on foreign exchanges |
| **Financial** | Bankruptcies, delinquencies, judgments, taxes | Old collections, unfiled taxes |
| **Drug use** | Illegal drug use, incl. marijuana, **even where legal** | Honesty vs. fear |
| Alcohol | Treatment, alcohol-related incidents | Underreporting |
| **Criminal** | Arrests, charges (even dismissed/sealed) | "It was expunged so I'll omit it" — wrong |
| Mental health | Court-ordered treatment (narrow) | Over-disclosing routine therapy (see §6.7) |
| Technology | Unauthorized IT/system access, misuse | Past "hacking" stories |
| Associations | Orgs advocating force to overthrow govt | Rare but asked |
| References | People who know you well | Stale contacts |

### 5.2 The cardinal rules of the form
1. **Tell the truth. Completely. The first time.** A *deliberate omission or
   falsification* is itself disqualifying under the **Personal Conduct** guideline
   and is a **federal crime** (18 U.S.C. § 1001). Many people who would have
   cleared *with* a problem get denied for *lying about* the problem.
2. **Disclose, don't litigate.** The form is not the place to argue innocence.
   List the event; you'll explain context later (subject interview).
3. **"Expunged / sealed / dismissed" still gets disclosed** if the question's
   timeframe and wording capture it. The government sees more than you think. Read
   each question's exact scope.
4. **Over-precision beats vagueness on facts, but don't volunteer non-asked
   detail.** Answer the question asked, fully and accurately.
5. **Keep a personal "clearance binder."** You'll thank yourself (see §10).

> The single most repeated piece of real adjudicator wisdom: *the cover-up is
> worse than the conduct.* Drug use in college? Often mitigable. Lying about it on
> the SF-86? Frequently fatal.

---

## 6. The 13 Adjudicative Guidelines (SEAD 4)

Clearance decisions are made against **Security Executive Agent Directive 4
(SEAD 4)** — the **National Security Adjudicative Guidelines**, organized into
**13 guideline areas (A–M)**. Each has **disqualifying conditions** and
**mitigating conditions**. The adjudicator weighs the **whole person** — totality,
recency, frequency, age at the time, and evidence of reform.

| ID | Guideline | The core question |
|---|---|---|
| A | **Allegiance to the United States** | Loyalty; advocacy of overthrow (rarely an issue) |
| B | **Foreign Influence** | Could foreign ties create coercion/divided loyalty? |
| C | **Foreign Preference** | Do you act in another nation's interest over the U.S.? |
| D | **Sexual Behavior** | Conduct that's criminal, compulsive, or exploitable |
| E | **Personal Conduct** | Honesty, reliability — **lying on the form lives here** |
| F | **Financial Considerations** | Debt/irresponsibility → vulnerability to bribery |
| G | **Alcohol Consumption** | Pattern indicating impaired judgment |
| H | **Drug Involvement & Substance Misuse** | Illegal use; current use disqualifying |
| I | **Psychological Conditions** | Only conditions impairing judgment/reliability |
| J | **Criminal Conduct** | Pattern of breaking the law |
| K | **Handling Protected Information** | History of mishandling classified/sensitive data |
| L | **Outside Activities** | Outside work creating conflict (e.g., foreign employer) |
| M | **Use of Information Technology** | Unauthorized access, misuse of systems |

### 6.1 Guideline B — Foreign Influence (the big one for global lives)
The most common *real* hurdle for talented engineers with international roots.
- **Disqualifying:** close/continuing contact with foreign nationals who could be
  exploited; foreign family in countries hostile to the U.S.; foreign financial
  interests substantial enough to create conflict.
- **Mitigating:** the relationship is casual; you can be expected to favor U.S.
  interests; contacts are minimal; foreign assets are small relative to net worth;
  the foreign country is a close ally with rule of law.
- **It is not disqualifying to have a foreign-born spouse, parents, or friends.**
  It *is* a problem to **hide** them, or to have deep entanglement in an
  adversary state. **Report them. Accurately.**

### 6.2 Guideline F — Financial Considerations (the #1 cause of denials)
Money problems are the **most common reason clearances are denied or revoked** —
because debt is the classic coercion lever.
- **Disqualifying:** unpaid delinquencies, charge-offs, bankruptcies, unpaid
  taxes, gambling debt, living beyond means, unexplained affluence.
- **Mitigating:** the debt arose from circumstances beyond your control (medical,
  job loss, divorce) **and** you acted responsibly — payment plans, credit
  counseling, good-faith resolution. **A managed debt beats a hidden one.**
- **Practical defense:** pull your credit reports now (free at
  annualcreditreport.com), resolve or set up plans on delinquencies, **file all
  tax returns**, and keep documentation of every resolution.

### 6.3 Guideline H — Drug Involvement & Substance Misuse
- **Current illegal use is essentially disqualifying.** "Current" is judged
  generously against recency and pattern.
- **Marijuana is illegal federally regardless of state law** — using it where it's
  state-legal is **still** a federal drug-involvement issue for clearance
  purposes. Many programs require you to **stop and stay stopped.**
- **Past experimentation** (especially years ago, infrequent, and *disclosed*) is
  frequently mitigable, *especially* with a credible statement of intent not to
  use again. The killers are **recent use, a pattern, and lying about it.**
- **Action:** if you want a clearance, **stop now** and let time pass. Recency is
  the single biggest factor.

### 6.4 Guideline E — Personal Conduct (where deception is punished)
This is the catch-all for **honesty and reliability**, and it's where
**falsifying the SF-86** is adjudicated. A small underlying issue + a lie about it
= denial under Guideline E *even if the underlying issue was mitigable.* This is
why §5.2 rule #1 matters more than any other sentence in this file.

### 6.5 Guideline J & K — Criminal Conduct / Handling Protected Information
- Disclose **all** arrests and charges in scope (even dismissed). A single old,
  minor offense with a clean decade since is usually mitigable as a pattern issue.
- Any past **mishandling of classified or sensitive data** (e.g., taking work
  home, emailing yourself proprietary files) is a serious flag — don't do it on
  current jobs, and disclose history honestly.

### 6.6 Guidelines A, C, D, G, I, L, M — the rest
- **A/C (Allegiance/Preference):** rarely an issue unless you've acted against
  U.S. interests or actively exercise foreign citizenship.
- **D (Sexual Behavior):** only matters if criminal, compulsive, or **exploitable
  (i.e., something you could be blackmailed over).** Disclosure removes the
  blackmail lever.
- **G (Alcohol):** DUIs, treatment, alcohol-related incidents.
- **I (Psychological):** see §6.7 — narrow and frequently misunderstood.
- **L (Outside Activities):** a side gig for a foreign company, undisclosed
  consulting, etc.
- **M (IT misuse):** unauthorized access, "I rooted my school's server" stories,
  pirating on work machines.

### 6.7 The mental-health myth (important)
**Seeking mental-health care does not, by itself, jeopardize a clearance.** The
SF-86's mental-health question (Section 21) is **narrow** — it focuses on
court-ordered treatment and conditions affecting judgment, and explicitly carves
out routine counseling related to grief, family, or **service-related** issues.
The government has worked hard to remove stigma so people **get help instead of
hiding**. Do not avoid therapy out of clearance fear; an untreated problem is the
risk, not the treatment.

---

## 7. The Investigation & Continuous Vetting

### 7.1 Who does it
- **DCSA — Defense Counterintelligence and Security Agency** conducts the vast
  majority of background investigations for DoD and contractors (it absorbed the
  old NBIB/OPM investigations function).
- **Trusted Workforce 2.0** is the modern framework; **NBIS (National Background
  Investigation Services)** is the IT system replacing e-QIP.

### 7.2 What actually happens
1. **You submit the SF-86** (via e-QIP/eApp) after a conditional job offer.
2. **Automated records checks** — credit, criminal, terror/watchlists, etc.
3. **Record verification** — they confirm residences, employment, education.
4. **Reference & source interviews** — they call the people you listed *and*
   "develop" their own sources (neighbors, coworkers you didn't list).
5. **Subject interview (for TS/SSBI):** a face-to-face where an investigator walks
   your history and **asks about every flag.** This is your chance to provide
   context — be calm, honest, and consistent with the form.
6. **Adjudication** — a trained adjudicator applies SEAD 4 (the 13 guidelines) and
   makes a **whole-person** eligibility determination.
7. **Grant / deny / SOR.** If there are concerns, you may get a **Statement of
   Reasons (SOR)** and the chance to **respond/appeal** before a final decision.

### 7.3 Continuous Vetting (CV) — the new normal
The old model (investigate once, reinvestigate in 5–10 years) is **gone**. Under
Trusted Workforce 2.0, cleared people are enrolled in **Continuous Vetting**:
automated, near-real-time monitoring of criminal, financial, terrorism, and other
records. **A new arrest, a new big delinquency, or a foreign-contact change can
surface immediately.** Two implications:
- **Self-report promptly.** You have an ongoing duty to report new derogatory
  info (arrests, financial trouble, foreign contacts/travel, etc.) to your
  security officer. Self-reporting is *protective*; getting flagged by CV first is
  not.
- **Clearable is a lifestyle, not a one-time exam.** The habits that get you
  cleared are the habits that keep you cleared.

---

## 8. Timelines (Set Realistic Expectations)

Timelines vary enormously by level, workload, and the complexity of *your*
history. Rough, current ballparks:

| Level | Typical processing time | What drives it longer |
|---|---|---|
| **Secret** | ~weeks to a few months | Foreign ties, finances, many residences |
| **Top Secret** | ~several months to ~a year+ | Subject interview scheduling, foreign scope |
| **TS/SCI + poly** | TS time **plus** poly scheduling | Compartment read-ins, poly backlog |

- **Interim clearances** are common: an employer can request an **interim Secret
  (or interim TS)** that lets you start work on a *preliminary* review while the
  full investigation completes. A clean, simple background gets interims fast.
- The biggest delay multiplier is **incomplete/inconsistent paperwork.** A tight,
  accurate SF-86 with reachable references is the single best thing you control.

> Practical: never quit a current job the day you get a conditional offer that
> depends on a clearance. Understand the start timeline and interim plan first.

---

## 9. Foreign Travel & Foreign Contacts (Live the Right Habits Now)

Even before you hold a clearance, build habits that keep you clearable:

- **Keep a travel log.** Every international trip: country, dates, purpose. The
  SF-86 asks ~7–10 years of personal foreign travel; reconstructing it from memory
  is miserable. Start a simple file today.
- **Know your foreign contacts.** Close and continuing relationships with foreign
  nationals are reportable. Keep a list (name, country, nature, frequency). You're
  not in trouble for *having* foreign friends — you're in trouble for *hiding*
  them.
- **Be careful with foreign-government or adversary-state entanglements.** Foreign
  bank accounts, property, employment, or benefits all get scrutinized (Guideline
  B/C). Avoid creating new ones casually.
- **Once cleared, pre-report foreign travel** per your facility's rules, and be
  alert to **elicitation** (foreign-intel attempts to befriend/recruit cleared
  personnel). Report contacts as instructed.

---

## 10. Build Your Clearance Binder (Do This Before You Need It)

A private, secured file (encrypted; you'll handle SSNs) that makes the SF-86 a
copy-paste job instead of a two-week archaeology dig:

- [ ] **Residence history** — every address for 10+ years, move-in/out dates, and
      a **verifier** (someone who knew you there) with current contact info.
- [ ] **Employment history** — every employer, dates, supervisor names + reachable
      contacts, reason for leaving, and explanations for any **gaps**.
- [ ] **Education** — schools, degrees, dates, locations.
- [ ] **Foreign travel log** — country/dates/purpose, 10 years.
- [ ] **Foreign contacts list** — name, citizenship, relationship, frequency.
- [ ] **Financial snapshot** — current credit reports, any delinquencies + the
      resolution plan/proof, **confirmation all tax returns are filed.**
- [ ] **Legal events** — any arrest/charge/citation with dates and dispositions
      (even dismissed/expunged), so you can answer in-scope questions accurately.
- [ ] **References** — 3+ people who've known you well for years, reachable.
- [ ] **Drug/alcohol honesty notes** — for *your* memory, so your form and subject
      interview are consistent.

> The binder is also your **continuous-vetting insurance**: when something changes,
> you update the binder and self-report in one motion.

---

## 11. How Employers Sponsor (and How to Get Picked)

- **You can't initiate a clearance.** A cleared **facility** (the employer, holding
  a facility clearance / FCL) sponsors you for a *specific position* with a
  validated **need**. No job, no sponsorship.
- **A leading defense-tech company** invests heavily in clearing engineers — it's core to its business
  with the IC and DoD. **Boeing / Lockheed / Northrop** have mature security
  offices that process clearances at scale; expect a structured, paperwork-heavy
  but well-trodden path.
- **Already-cleared candidates jump the queue.** An **active Secret/TS** is a
  major hiring advantage because the company avoids the time and cost of
  sponsorship. This is why "current clearance" appears as a hard requirement on so
  many postings.
- **Crossover (reciprocity):** clearances are generally **reciprocal** across
  agencies — a TS granted at one agency is typically honored at another, though
  **SCI read-ins and polygraphs** may need to be re-accomplished per program.
- **It follows the job, with a grace period.** When you leave a cleared job, your
  clearance becomes **inactive**; it can usually be **reactivated** by a new
  sponsor within ~24 months without a full new investigation. Don't let it lapse
  carelessly.

---

## 12. Presenting "Clearable" / "Cleared" on a Résumé

This is the concrete deliverable. Put your status where a recruiter sees it in
five seconds — typically a **Clearance** line near the top, under your name/contact
or in a summary band.

**If you have no clearance yet but qualify:**
```
Clearance: U.S. Citizen — clearable; eligible for and willing to undergo
           background investigation (Secret / TS).
```

**If you hold an active clearance:**
```
Clearance: Active Secret (DoD), granted 2025 — eligible for upgrade.
```
or
```
Clearance: TS/SCI (active), CI poly — current and transferable.
```

**If your clearance is inactive but reactivatable:**
```
Clearance: TS/SCI (inactive, last active 2024) — reactivation-eligible.
```

Rules:
- **Never overstate.** Claiming a clearance you don't have is a fast way to be
  permanently un-hireable (and it's a Guideline E problem). "Clearable" is the
  honest, valuable claim when you're a clean-record citizen.
- **Be specific but unclassified.** State level, status (active/inactive), and
  granting domain (DoD/IC) — **never** name programs, compartments, or anything
  classified about your work.
- **Mirror the posting's language.** If it says "active Secret required," and you
  have it, say "Active Secret" verbatim.
- Pair it with your **U.S.-person/ITAR** eligibility, since many defense roles
  gate on that even without a clearance.

See [09-career-resume-portfolio.md](09-resume-portfolio.md) for where this
line lives in the overall résumé layout, and
[08-career-interview-prep.md](08-interview-prep.md) for how to talk about
clearance status in screening calls without oversharing.

---

## 13. Common Failure Modes (and How to Avoid Them)

| Failure mode | Why it kills you | The fix |
|---|---|---|
| **Lying / omitting on the SF-86** | Guideline E; federal crime; the cover-up beats the crime | Disclose everything in scope, the first time |
| **Unresolved debt / unfiled taxes** | Guideline F — #1 denial cause; coercion risk | Pull credit now; payment plans; **file all taxes** |
| **Recent illegal drug use (incl. legal-state weed)** | Guideline H; "current use" disqualifying | Stop now; let recency build; disclose past honestly |
| **Hidden foreign contacts/assets** | Guideline B; concealment compounds it | Report them accurately; minimize new adversary-state ties |
| **Inconsistent story (form vs. interview)** | Reads as deception | Keep the binder; tell the same true story everywhere |
| **Avoiding therapy out of fear** | Untreated issue is the real risk | Section 21 is narrow; get help; it rarely matters |
| **Stale/unreachable references** | Stalls the investigation for months | Keep contacts current in your binder |
| **Letting a clearance lapse** | Loses your biggest hiring edge | Track inactive window; line up a sponsor in time |

---

## 14. 30 / 60 / 90-Day Clearability Plan

**Days 1–30 — Audit & clean.**
- [ ] Pull all three credit reports; list and address any delinquencies.
- [ ] Confirm every tax return is filed; fix any that aren't.
- [ ] If you use marijuana or any illegal drug, **stop** — start the recency clock.
- [ ] Start the residence/employment/travel/foreign-contact binder (§10).

**Days 31–60 — Document & verify.**
- [ ] Reconstruct 10 years of addresses and jobs with verifiers/contacts.
- [ ] Reconstruct your foreign-travel log.
- [ ] List close/continuing foreign contacts honestly.
- [ ] Line up 3+ strong, reachable references.

**Days 61–90 — Position & signal.**
- [ ] Add the correct **Clearance/U.S.-person line** to your résumé (§12).
- [ ] Practice a 20-second, honest clearance answer for screening calls.
- [ ] Target Secret-designated roles at sponsors (top defense-tech companies, Boeing, Lockheed) and let
      your real drone stack (see [09-career-resume-portfolio.md](09-resume-portfolio.md))
      carry the technical case while your clearability carries the gate.

---

## 15. How This Connects to the Rest of the Curriculum

- [03-career-software-engineering.md](03-software-engineering.md) — the
  technical bar that *follows* clearability; this file is its §1 expanded.
- [02-career-defense-aerospace-playbook.md](02-defense-aerospace-playbook.md)
  — overall path into defense; clearance is a recurring checkpoint there.
- [05-career-dod-politics.md](05-dod-politics.md) — why classification and
  access controls exist; the institutional context (SEAD 4, ODNI, DCSA).
- [06-career-negotiation-compensation.md](06-negotiation-compensation.md)
  — an active clearance is **leverage**; price it in when you negotiate.
- [01-career-aerospace-engineering.md](01-aerospace-engineering.md) and
  [04-career-mechanical-engineering.md](04-mechanical-engineering.md) —
  hardware-side roles that still gate on U.S.-person/ITAR status.
- [01-mastery-curriculum.md](../01-mastery-curriculum.md) /
  [02-ten-year-mastery-plan.md](../foundations/02-ten-year-mastery-plan.md) — slot "become and
  stay clearable" as a standing, low-effort, high-leverage track.

---

## Sources & Citations

**Primary / official**
- Defense Counterintelligence and Security Agency (DCSA) — background investigations
  & clearance process: https://www.dcsa.mil
- Office of the Director of National Intelligence (ODNI) — Security Executive Agent
  Directives, incl. **SEAD 4** (adjudicative guidelines): https://www.dni.gov/index.php/ncsc-how-we-work/ncsc-security-executive-agent
- **SF-86 (Standard Form 86)** and other standard forms — U.S. OPM / GSA:
  https://www.opm.gov/forms/standard-forms/  ·  https://www.gsa.gov/reference/forms
- **Trusted Workforce 2.0 / Continuous Vetting** — performance.gov & DCSA:
  https://www.dcsa.mil/Personnel-Security/
- National Background Investigation Services (NBIS / eApp) — DCSA:
  https://www.dcsa.mil/is/nbis/
- ITAR / export control (Directorate of Defense Trade Controls): https://www.pmddtc.state.gov
- 18 U.S.C. § 1001 (false statements): https://www.law.cornell.edu/uscode/text/18/1001

**Reference & practitioner**
- ClearanceJobs — news and explainers on the clearance process: https://news.clearancejobs.com
- *Security Clearance Adjudicative Guidelines* overview (ClearanceJobs / DCSA summaries).
- Federation of American Scientists (FAS) — classification policy background: https://fas.org

*This is personal career guidance reflecting the author's goals and publicly
available, unclassified information. It is not legal advice. Clearance policy,
forms, timelines, and systems (e-QIP → eApp/NBIS, Trusted Workforce 2.0) change —
verify every specific against the primary DCSA/ODNI/OPM sources above, and when in
doubt, **tell the truth on the form.***

---

## ⚡ The Insider Layer — What the Field Knows but Rarely Writes Down

Everything below is drawn from public policy — SEAD 4's adjudicative guidelines,
the SF-86, and DCSA/ODNI guidance. *The non-public mechanics of polygraph sessions
and the internal deliberations of adjudicators are deliberately out of scope here;
where this guide would have to speculate about closed processes, it stops and says
so rather than invent.* What follows is the published reality that nonetheless
surprises almost everyone going through it the first time.

### The cover-up sinks more clearances than the conduct
The single most counterintuitive, publicly documented truth: people lose
clearances over **Guideline E (Personal Conduct)** — lying on the form or in the
interview — far more often than over the underlying behavior they were hiding.
Past marijuana use, a long-ago arrest, a debt: these are frequently *mitigable*
under the whole-person concept. A deliberate omission is much harder to mitigate,
and a knowing false statement on the SF-86 is its own federal exposure under
18 U.S.C. § 1001. The entire system is engineered to reward candor and punish
concealment — so the dominant strategy is radical, complete disclosure, even when
it's embarrassing.

### Finances are the number-one reason clearances are denied
Year after year, the published statistics put **Guideline F (Financial
Considerations)** at the top of the denial list — above drugs, above foreign
contacts. The logic is documented and pragmatic: unmanaged debt is treated as a
vulnerability to coercion and as a window into judgment and reliability. The
mitigation is equally documented — a debt you're *actively addressing* on a
written plan adjudicates very differently from one you're ignoring. Practical,
public-knowledge takeaway: pull your own credit report before you ever submit, and
walk in with a paper trail for anything adverse.

### Recency runs the clock on drugs — and marijuana is still federally illegal
Under Guideline H, *when* matters as much as *whether*. Published guidance treats
distant, discontinued use very differently from recent use, and a credible,
written intent not to use again is part of the mitigation framework. The trap that
catches people: **marijuana remains a Schedule I substance federally**, so state
legalization is irrelevant to a federal clearance, and casual "it's legal here"
reasoning has ended candidacies. The clean public move is simply to stop well
before you apply and document the date.

### Continuous Vetting changed the game from a snapshot to a movie
**Trusted Workforce 2.0 / Continuous Vetting** replaced the old periodic
reinvestigation with ongoing automated monitoring of records — a publicly
announced shift. The practical consequence most people miss: your **continuous
duty to self-report** (new foreign contacts, certain financial events, arrests)
is now the live mechanism, not a once-every-five-years cleanup. Cleared status is
a standard you maintain daily, not a credential you earn once. Self-reporting
promptly is itself favorable conduct; getting flagged by the system first is not.

### "Clearable" is a real, nameable résumé asset — use it
You cannot sponsor your own clearance, which creates the well-known chicken-and-egg.
The public workaround is to be *demonstrably clearable* — U.S. citizen, clean
finances, no current drug use, declarable (not disqualifying) foreign ties — and to
say exactly that on your résumé and in screens. An **interim clearance** can be
granted relatively quickly on a clean preliminary review, letting you start work
while the full investigation runs, which is why a tidy background is effectively a
schedule asset an employer can price. See
[06-negotiation-compensation.md](06-negotiation-compensation.md).

### Reciprocity is policy, not a guarantee — expect friction
In principle a clearance transfers between agencies and contractors; in published
practice **reciprocity has gaps**, especially across the line into SCI access or
where a polygraph is required by the gaining program. A Secret or even a TS does
not automatically carry every access you held, and crossover can take time. The
realistic expectation — supported by ODNI's own reciprocity guidance — is that
moving between programs is usually *smoother*, not instant or frictionless.

### The mental-health stigma is largely outdated — by design
A persistent myth says seeking counseling tanks a clearance. The SF-86's mental
health question (historically Section 21) has been *deliberately narrowed* and now
explicitly carves out grief, family, and most routine counseling, and policy has
been public-messaged to encourage care. What's actually adjudicated under
Guideline I is a *condition that affects judgment or reliability* — not the act of
responsibly getting help. The documented, government-endorsed position is that
seeking treatment is generally viewed as a sign of strength, not a red flag.

### Keep a clearance binder — the SF-86 is an exercise in documentation, not memory
The form demands 10 years of addresses, employments, foreign travel, and contacts,
and it is verified. The people who breeze through it keep a running file:
residences with dates, supervisors, every foreign trip, foreign-national contacts.
The people who struggle try to reconstruct a decade from memory under time
pressure and create inconsistencies that *look* like deception even when they
aren't. Start the binder before you need it — accuracy and consistency are the
whole game.
