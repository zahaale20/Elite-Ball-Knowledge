# Trust, Safety, OPSEC & Digital Resilience — Protecting People, Teams & Operations

> **Why this exists.** Understanding the information environment (modules 31–35) is
> only half the job. The other half is **protecting yourself, your team, and your
> operations** within it. This module covers operational security (OPSEC), personal
> and organizational information hygiene, insider-risk awareness, social-engineering
> and phishing defense, and healthy analytic tradecraft. It is defensive throughout:
> the goal is resilience, not offense. For defense-tech and clearance-track work,
> this is also a professional baseline that employers expect.

Closes the `31–36` band. It complements the formal security material in
[16-career-security-clearance.md](16-career-security-clearance.md) and the assurance
mindset in [09-foundations-safety-assurance.md](09-foundations-safety-assurance.md).

---

## 1. OPSEC as a process

Operational security is not a checklist; it is a repeatable risk process. The
classic five-step OPSEC cycle:

1. **Identify critical information.** What, if known by an adversary, would cause
   harm? (Travel plans, system capabilities, schedules, relationships, vulnerabilities,
   program details.)
2. **Analyze threats.** Who would want it, and what are they capable of?
3. **Analyze vulnerabilities.** How could that information leak — technically,
   socially, or through patterns of behavior?
4. **Assess risk.** Combine likelihood and impact to prioritize.
5. **Apply countermeasures.** Reduce the highest risks with proportionate measures,
   then iterate.

The central OPSEC insight: **individually harmless pieces of public information can
aggregate into something sensitive.** Adversaries assemble mosaics. Module 35's OSINT
techniques are exactly what an adversary would use against *you* — OPSEC is OSINT
turned defensive.

---

## 2. Your digital footprint and the aggregation problem

- Every public post, profile, check-in, photo (with metadata), and connection is a
  tile in a mosaic about you.
- **Metadata leaks.** Photos can carry location and device data; documents carry
  authorship and revision history; posting times reveal routines and time zones.
- **Pattern-of-life.** Regular, observable behavior (routes, schedules, habits) is
  often more revealing than any single secret and is the basis of both physical and
  digital targeting.
- **Cross-platform correlation.** Reused usernames, photos, and writing style let
  separate accounts be linked into one identity.
- **Privacy hygiene.** Minimize what you publish, review platform privacy settings,
  strip metadata when sharing, separate personal and professional identities, and
  periodically audit your own footprint by searching for yourself the way an analyst
  would.

For sensitive or clearance-track roles, assume a capable adversary is patient and
will aggregate over time. See
[16-career-security-clearance.md](16-career-security-clearance.md).

---

## 3. Social engineering and phishing defense

Most breaches start by exploiting people, not code — the cognitive levers from
module 33 (urgency, authority, fear, trust) weaponized for access.

**Common techniques to recognize**
- **Phishing / spear-phishing.** Deceptive messages (often personalized using OSINT)
  that induce you to click, log in, or reveal information.
- **Pretexting.** A fabricated scenario and identity to extract information or access.
- **Authority and urgency pressure.** "This is the CEO, I need this *right now*" —
  designed to bypass deliberate (System 2) thinking.
- **Baiting and quid pro quo.** Offering something (a file, a reward, "help") in
  exchange for access or information.
- **MFA fatigue / push bombing.** Flooding you with approval prompts hoping you
  approve one to make it stop.

**Defensive habits**
- **Verify out-of-band.** Confirm unusual requests through a *separate, known*
  channel before acting.
- **Slow down under pressure.** Manufactured urgency is itself a warning sign
  (module 33: treat urgency as a flag).
- **Check sender and link details**, but don't rely on them alone — they can be
  spoofed.
- **Use phishing-resistant MFA** (hardware security keys / passkeys) and a password
  manager with unique credentials per site.
- **Never approve an MFA prompt you didn't initiate.**
- **Report, don't just delete.** Reporting protects the whole team.

---

## 4. Insider risk awareness

Insider risk is sensitive and must be framed carefully and humanely. It is about
**protective process**, not suspicion of colleagues.

- **Categories.** Malicious insiders (intentional harm), negligent insiders
  (careless mistakes — the most common), and compromised insiders (credentials or
  person manipulated by an outside actor).
- **Protective principles (not surveillance prescriptions):**
  - **Least privilege.** People should have only the access they need.
  - **Separation of duties.** Critical actions require more than one person.
  - **Auditability.** Sensitive actions are logged and reviewable.
  - **Healthy culture.** Reduce the pressures (burnout, grievance, financial stress)
    that contribute to insider incidents; make it safe to report mistakes early.
- **Your role.** Follow data-handling policy, don't over-collect or hoard access,
  report your own mistakes promptly, and treat security as a shared responsibility
  rather than someone else's job.

The cultural point matters: organizations that punish honest mistakes drive them
underground, which *increases* risk. This mirrors the blameless-postmortem ethos in
[09-foundations-safety-assurance.md](09-foundations-safety-assurance.md).

---

## 5. Organizational information hygiene

- **Data classification.** Know what is public, internal, confidential, or
  controlled, and handle each appropriately. For defense work, understand the
  difference between public, CUI, and classified — and never mix them.
- **Need-to-know.** Share sensitive information only with those who require it.
- **Secure communication.** Use approved, encrypted channels for sensitive material;
  don't route work data through personal accounts or unsanctioned tools.
- **Clean device practices.** Patch promptly, encrypt disks, lock screens, separate
  work and personal devices, and be cautious with removable media.
- **Records discipline.** Durable, accurate records support both security and good
  analysis (module 35) and counter hindsight bias (module 33).
- **Vendor and supply-chain awareness.** Third-party tools and dependencies are part
  of your attack surface.

---

## 6. Healthy analytic tradecraft (psychological resilience)

Working in the information environment — especially with adversarial or distressing
content — has real cognitive and emotional costs. Resilience is a professional skill.

- **Avoid information overload.** Curate inputs deliberately; constant high-volume
  consumption degrades judgment (module 31's learned-helplessness failure mode).
- **Separate signal from emotional contagion.** Distressing content can bias
  analysis; notice when affect is driving your conclusions (module 33).
- **Build sustainable routines.** Fatigue depletes the deliberate reasoning that
  catches manipulation and bias.
- **Maintain epistemic humility.** Hold conclusions provisionally; update on
  evidence; record uncertainty (module 35).
- **Protect against radicalization-by-immersion.** Prolonged immersion in extreme
  content shifts one's own baseline; deliberate distance and peer review are
  protective.
- **Use peer support and review.** Both for accuracy and for well-being — isolation
  worsens both.

---

## 7. A personal & team resilience checklist

**Personal**
1. Audit your own digital footprint the way an analyst would.
2. Use phishing-resistant MFA and a password manager everywhere.
3. Verify unusual or urgent requests out-of-band before acting.
4. Strip metadata and minimize what you publish about routines and plans.
5. Separate personal and professional identities and devices.

**Team / organization**
1. Enforce least privilege, separation of duties, and auditability.
2. Classify data and apply need-to-know.
3. Use approved encrypted channels; keep work off personal accounts.
4. Build a blameless reporting culture for mistakes and near-misses.
5. Run periodic phishing and social-engineering awareness exercises.
6. Treat insider risk as a humane protective process, not surveillance.

---

## 8. Relevance to defense-tech and autonomy

- **Clearance and program baseline.** OPSEC and information hygiene are expected
  competencies in defense work
  ([16-career-security-clearance.md](16-career-security-clearance.md)).
- **Assurance mindset.** The same defense-in-depth, least-privilege, and auditability
  principles apply to securing autonomous systems and their data pipelines
  ([09-foundations-safety-assurance.md](09-foundations-safety-assurance.md)).
- **Adversary modeling.** Designing your own OPSEC trains you to think like an
  adversary, which improves system design against real threats (modules 34–35).
- **Trustworthy operations.** Operator trust depends on the integrity of the data and
  systems behind it — security and trust are inseparable.

---

## Sources & further study

- NIST Cybersecurity Framework and NIST SP 800-series (security and OPSEC practice).
- U.S. OPSEC (NSDD-298) five-step process — the canonical OPSEC cycle.
- CISA — phishing, MFA, and social-engineering defense guidance.
- Bruce Schneier — *Secrets and Lies* / *Beyond Fear* (security thinking).
- CERT Insider Threat resources (Carnegie Mellon SEI) — protective, process-oriented
  framing of insider risk.

> Framing note: every technique here is **defensive** — protecting people, teams, and
> operations. Understanding how attacks and aggregation work is how you defend against
> them; the purpose is resilience and integrity.
