# Pre-Send Compliance Checklist

Run through this **before every campaign**. It is ordered from "will get you in legal trouble"
to "will get you blacklisted." Both end your outreach — treat them as equally fatal.

## CAN-SPAM (United States — applies to commercial email)

- [ ] **Accurate header info** — "From," "Reply-To," and routing identify you/your business
      truthfully. (`outreach.py` sends only from your real SMTP account.)
- [ ] **Honest subject line** — describes the actual message; no bait-and-switch.
- [ ] **Identified as outreach** — the message doesn't pretend to be something it isn't.
- [ ] **Valid physical postal address** in every email. (Set in `sender_config.json` →
      auto-appended.)
- [ ] **Clear opt-out mechanism** in every email. (Auto-appended unsubscribe line.)
- [ ] **Honor opt-outs promptly** — add anyone who replies STOP/UNSUBSCRIBE to
      `suppression.csv` (CAN-SPAM requires honoring within 10 business days; do it same-day).
      `outreach.py` skips everyone on the suppression list.
- [ ] **No harvested or dictionary-generated addresses** — these are *aggravated* violations.
      Only use legitimately sourced leads (see README Step 2).

## CASL (Canada — stricter; if any recipients are Canadian)

- [ ] You have **consent** (express or a valid implied-consent basis, e.g., an existing business
      relationship or a conspicuously published business address relevant to their role).
- [ ] Message includes **sender identification** and a **working unsubscribe** honored within 10
      business days.
- [ ] Note: CASL penalties are severe and the default is *no* unsolicited mail without a consent
      basis. When unsure about Canadian recipients, don't send — get explicit opt-in first.

## GDPR / UK GDPR (EU / UK recipients)

- [ ] You have a **lawful basis** (often "legitimate interest" for B2B role-based contact, after
      a balancing test) and can document it.
- [ ] Easy **opt-out / objection** honored immediately; you can fulfill access/erasure requests.
- [ ] You only hold data you actually need (data minimization) and have a privacy notice.
- [ ] For individuals (not generic role addresses), the bar is higher — prefer opt-in.

## Financial-services overlay (ONLY if you sell securities/insurance products)

- [ ] **Principal pre-approval** of every public communication / template (FINRA Rule 2210).
- [ ] Content is **fair and balanced**, with **no guarantees**, no exaggerated or unwarranted
      claims, and **no predictions of performance**.
- [ ] Required **disclosures** and risk language present; testimonials carry disclosures.
- [ ] **Recordkeeping** — communications retained per firm policy (typically ≥3 years).
- [ ] **Do-not-call / cold-contact rules** observed for any phone follow-up.
- [ ] Recommendations meet **Reg BI** (best interest) and **Form CRS** is delivered to retail
      customers where applicable.
- [ ] When in doubt, your firm's compliance officer signs off **before** the first send.

## Deliverability (protects your domain so anything lands at all)

- [ ] **SPF, DKIM, and DMARC** configured on your sending domain.
- [ ] Sending from a **secondary domain** (not your primary), warmed up gradually.
- [ ] **Slow ramp** — start ~20–30/day, increase over weeks. (`--rate` and `--daily-cap` in
      `outreach.py`.)
- [ ] List is **clean** — verified addresses, no role-account spam traps, bounces removed.
- [ ] Every send is **personalized** and relevant to a tight ICP — generic blasts tank
      reputation and reply rates alike.

## Operating discipline

- [ ] Ran `outreach.py` in **dry-run first** and read every draft.
- [ ] Confirmed each lead is an appropriate **business** contact for **business** outreach.
- [ ] Replies, bounces, and opt-outs are processed promptly into `leads.csv` / `suppression.csv`.

> **Rule of thumb:** if you'd be uncomfortable having a recipient (or a regulator) read your
> email and your list-sourcing aloud, don't send it. The compliant version almost always
> converts better anyway.
