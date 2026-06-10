# Ethics, Export Control & Professional Responsibility

> A standalone companion to [07-security-clearance.md](07-security-clearance.md),
> [05-dod-politics.md](05-dod-politics.md), and
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
  closes doors permanently (ties to [07-security-clearance.md](07-security-clearance.md)).
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
  [12-technical-communication.md](12-technical-communication.md) and OPSEC in
  [06-trust-safety-opsec-and-digital-resilience.md](../information-environment/06-trust-safety-opsec-and-digital-resilience.md).)
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
  [10-planning-decision.md](../autonomy/10-planning-decision.md) and
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
- [07-security-clearance.md](07-security-clearance.md) — the clearance these
  obligations protect.
- [09-safety-assurance.md](../foundations/09-safety-assurance.md) — the engineering
  discipline of proving systems safe.
- [05-dod-politics.md](05-dod-politics.md) — the institutional context of these rules.
- [06-trust-safety-opsec-and-digital-resilience.md](../information-environment/06-trust-safety-opsec-and-digital-resilience.md)
  — operational security and information discipline.

---

## ⚡ The Insider Layer — What the Field Knows but Rarely Writes Down

> Compliance literacy only. This section explains the *structure* of publicly
> published U.S. export-control and professional-responsibility frameworks so you
> can recognize obligations and route them to the right experts. It is **not**
> legal advice and contains **no** guidance on circumventing any control — the
> entire posture here is to stay far from every line and ask the empowered
> officials when in doubt.

### Two regimes, two agencies — getting the jurisdiction wrong *is* the violation
The public framework splits into **ITAR** (administered by the State Department's
DDTC, governing defense articles and services on the U.S. Munitions List) and
**EAR** (administered by Commerce's BIS, governing dual-use items on the Commerce
Control List). The foundational literacy point: *jurisdiction determination comes
first*, because treating an ITAR-controlled item as if it were merely EAR (or
uncontrolled) is itself how violations happen. This is not a judgment call to
make alone in your head — it is a determination for your organization's export
compliance officer and counsel, and the published guidance exists precisely so
non-experts know *when to ask* rather than guess.

### "Deemed exports" — an export can happen without anything crossing a border
The concept that most surprises engineers and trips up labs and startups: under
the public rules, *releasing* controlled technical data to a foreign person—even
in the same room, in the United States—can be "deemed" an export to that person's
country. A whiteboard session, a shared drive, a code review with a foreign-
national colleague can implicate the controls. The literacy takeaway is simply to
*recognize the trigger* and route the situation to compliance before sharing —
not to improvise. Universities and companies handle this routinely with proper
licensing and technology control plans; the failure mode is the engineer who
didn't know the category existed.

### Strict liability and the narrowness of the public-domain exclusion
Two realities the framework makes explicit. First, many export-control
violations are *strict liability* — intent is not required, and "I didn't know"
is not a defense; penalties published in statute are both civil and criminal,
assessed per violation. Second, the **fundamental research / public-domain
exclusion** is real but *narrower than people assume*: genuinely published,
generally accessible information may fall outside control, but the exclusion is
easy to misread, and it does not launder a controlled article just because you
wrote about it. Because the boundary is subtle, the correct move is conservative
— when unsure whether something is publishable, treat it as controlled and ask.
This is also the link to your public presence
([13-personal-brand-public-presence.md](13-personal-brand-public-presence.md)):
build your reputation on the safely-publishable layer of fundamentals and open
work.

### The aggregation problem and everyday data hygiene
OPSEC and classification share a counterintuitive property the cleared world
internalizes: individually-unclassified facts can become sensitive — even
classified — *in combination*. Need-to-know is therefore about the information,
not your rank, and CUI (Controlled Unclassified Information) is a real category
with handling rules even though it carries no classification stamp. The practical,
publicly-sensible hygiene that follows: don't move work to personal email or
consumer cloud, and — the modern trap — **don't paste controlled or sensitive
code, specs, or data into public AI tools**, which can constitute both a spillage
and, potentially, an export. The convenience of the tool does not change the
obligation attached to the data.

### The cover-up is worse than the violation — and raising concerns is protected
The single most important cultural fact, fully public: U.S. export regimes offer
**voluntary self-disclosure**, and a good-faith VSD typically results in
substantially reduced penalties, whereas concealment is treated as an
aggravating factor. The engineer who flags a possible problem early is doing
exactly what the system is built to reward; the one who hides it converts a
fixable error into a career-ending one. The same logic governs safety and ethics
— raising a concern through the proper channel is protected and expected, not
disloyal ([09-safety-assurance.md](../foundations/09-safety-assurance.md)).

### Dual-use responsibility and the reputation that compounds
Beyond the letter of the law sits the professional-responsibility layer the
codes of bodies like IEEE articulate: the engineer bears some responsibility for
what their work is used to do, and "I just built the technology" has limits as a
moral position — a live debate in autonomy and lethal-autonomy discussions. You
don't have to resolve the philosophy to act well: know the rules cold, stay far
from every line, put your jurisdiction questions in *writing* to the empowered
official (the paper trail protects you), and decline the gray-area shortcut. The
quiet payoff is that *impeccable judgment about sensitive things* is one of the
most durable and valuable reputations in this field — compliance is not friction
to your career, it is a moat around it.
