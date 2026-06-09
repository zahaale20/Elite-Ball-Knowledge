# Ethics, Export Control & Professional Responsibility

> A standalone companion to [16-security-clearance.md](16-security-clearance.md),
> [14-dod-politics.md](14-dod-politics.md), and
> [09-safety-assurance.md](../foundations/09-safety-assurance.md). This is the file
> that protects your career from the one category of mistake that no amount of
> technical brilliance can recover from: a compliance, legal, or ethical violation.
> In defense and autonomy, the rules here are not bureaucratic friction — they are
> federal law with criminal penalties, and they are a core part of being a
> professional in this field.

You can recover from a failed project, a missed deadline, even a fired-from job. You
cannot easily recover from an ITAR violation, a clearance revoked for cause, or being
the engineer who knowingly shipped something unsafe. This file is the guardrail band.
It is written so that you understand the *structure* of these obligations well enough
to stay far from every line — and to be the person whose judgment is trusted with the
hardest, most sensitive work.

> **Disclaimer:** This is professional literacy, not legal advice. Export control and
> classification rules are complex and fact-specific. When in doubt, *stop and ask your
> company's export/security/legal team* — that instinct is itself the most important
> skill in this file.

---

## 1. Why This Matters More in Defense Than Anywhere Else

- **The stakes are physical and irreversible.** Autonomy and weapons-adjacent systems
  can cause real harm; engineering decisions here carry moral weight that a typical
  app does not.
- **The rules are law, not policy.** ITAR/EAR violations carry civil *and criminal*
  penalties — fines and prison — for individuals, not just companies.
- **Trust is the currency of the cleared world.** Your access to the most interesting
  work depends entirely on a reputation for sound judgment and discretion. One lapse
  closes doors permanently (ties to [16-security-clearance.md](16-security-clearance.md)).
- **"I didn't know" is not a defense.** Professional responsibility includes knowing
  the rules that govern your work. This file gets you to "I know enough to know when
  to ask."

---

## 2. Export Control: ITAR & EAR (the big one)

US export-control law governs how defense and dual-use technology, data, and know-how
move across borders **and to foreign persons** — including inside the US.

- **ITAR** (International Traffic in Arms Regulations, State Dept / DDTC) governs
  defense articles and services on the **USML** (US Munitions List). Most
  defense-specific autonomy and weapons technology lives here.
- **EAR** (Export Administration Regulations, Commerce / BIS) governs dual-use items
  on the **CCL** (Commerce Control List) — commercial tech with military
  applications.
- **A "deemed export" is the trap engineers fall into:** disclosing controlled
  technical data to a *foreign person inside the United States* — a coworker, a
  contractor, an intern on a visa — counts as an export to their country. You can
  violate ITAR without anything ever crossing a border, just by showing the wrong
  diagram to the wrong colleague.
- **"Technical data" is broad** — drawings, schematics, source code, specifications,
  even verbal know-how about controlled items. Email, a GitHub repo, a conference
  slide, or a casual hallway explanation can all be exports.
- **The practical rules of thumb:**
  - Assume defense technical data is controlled until told otherwise.
  - Never put controlled data on personal devices, personal cloud, or public repos.
  - Know which colleagues are US persons before sharing controlled material; rely on
    your company's processes, not your own guess.
  - Foreign travel, foreign nationals, and foreign collaboration all trigger
    export-control questions — flag them *before* acting.
  - **When unsure, stop and ask the empowered official / export-control team.** This
    is the single most career-protecting habit in defense engineering.

---

## 3. Classification & Information Handling

- **Classification levels** (Confidential / Secret / Top Secret, plus SCI/SAP
  compartments) define who can see what, where, and on which systems. Handling is
  governed by need-to-know *and* clearance level — both are required.
- **Spillage** — putting classified information on an unclassified system — is a
  serious incident even when accidental. Know which network you're on, always.
- **Marking, storage, transmission, and destruction** all have strict rules; follow
  your facility's procedures exactly rather than improvising.
- **Don't talk around it.** Discussing classified work in unclassified settings —
  even vaguely, even with cleared friends outside the need-to-know — is a violation.
  (Connects to communication discipline in
  [116-technical-communication.md](116-technical-communication.md) and OPSEC in
  [36-trust-safety-opsec-and-digital-resilience.md](../information-environment/36-trust-safety-opsec-and-digital-resilience.md).)
- **CUI** (Controlled Unclassified Information) and **CMMC** compliance govern
  sensitive-but-unclassified data and the cybersecurity standards contractors must
  meet — increasingly central to defense work.

---

## 4. Engineering Ethics & Professional Responsibility

Beyond the law, there's the professional duty engineers owe to the public and to the
truth.

- **Safety is a non-negotiable duty.** The engineer's first obligation is to public
  safety (the spirit of every engineering code of ethics). The discipline of proving
  a system safe lives in [09-safety-assurance.md](../foundations/09-safety-assurance.md);
  the *duty* to do so lives here.
- **Intellectual honesty about risk and capability.** Don't overstate what a system
  can do, don't hide a failure mode, don't let a schedule pressure you into "it's
  probably fine." The Challenger and similar disasters trace to engineers who knew and
  were overruled — and to the duty to escalate clearly and on the record.
- **The duty to dissent and escalate.** When you believe something is unsafe or wrong,
  professional responsibility requires raising it through the right channels, in
  writing, calmly, and persistently — even when it's unwelcome.
- **Avoid conflicts of interest** and handle proprietary/third-party IP cleanly — both
  are integrity *and* legal issues.

---

## 5. The Hard Questions: Autonomy, Weapons & Conscience

Defense-tech engineers work near systems that can take life. Thinking clearly about
this is part of the job, not separate from it.

- **Know where you stand and choose deliberately.** You will face decisions about what
  you're willing to build. Make those choices consciously and in advance, informed
  rather than reflexive, so you're not improvising your ethics under pressure.
- **Understand the frameworks** — the laws of armed conflict, rules of engagement, the
  active debates around lethal autonomy and "meaningful human control." Engaging with
  these seriously makes you a *better and more trusted* engineer, not a reluctant one.
- **Human accountability is a design requirement,** not just a philosophy — who is
  responsible for the system's actions, and how the design preserves human judgment,
  are engineering questions you'll help answer (ties to
  [29-planning-decision.md](../autonomy/29-planning-decision.md) and
  [09-safety-assurance.md](../foundations/09-safety-assurance.md)).
- **Integrity is the through-line** — the same honesty that makes you trustworthy with
  classified data and safety claims is what lets you live with the work.

---

## 6. Practical Habits That Keep You Safe

- **Default to asking.** The instinct to stop and check with export-control/security/
  legal *before* acting is the master skill. It is never the wrong call.
- **Keep work on approved systems only** — no controlled or classified data on
  personal devices, personal email, personal cloud, or public code hosts, ever.
- **Document decisions and escalations** — a written record protects you and the
  public when a hard call is made.
- **Refresh your training and treat it seriously** — the annual compliance training is
  not a checkbox; it's the map of the minefield.
- **Cultivate the reputation** of the engineer with impeccable judgment about
  sensitive things. It is one of the most valuable and durable career assets in this
  field.

---

### Connections
- [16-security-clearance.md](16-security-clearance.md) — the clearance these
  obligations protect.
- [09-safety-assurance.md](../foundations/09-safety-assurance.md) — the engineering
  discipline of proving systems safe.
- [14-dod-politics.md](14-dod-politics.md) — the institutional context of these rules.
- [36-trust-safety-opsec-and-digital-resilience.md](../information-environment/36-trust-safety-opsec-and-digital-resilience.md)
  — operational security and information discipline.
