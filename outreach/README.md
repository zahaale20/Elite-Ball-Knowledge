# Client Acquisition Toolkit — Compliant B2B Lead-Gen & Outreach

> **What this is.** A practical, *compliant-by-design* system for finding business buyers,
> building a clean targeted contact list, and running personalized outreach that you review and
> send. It is built to make money the way cold outreach actually works in 2026 — **relevance and
> deliverability**, not volume — and to keep you on the right side of CAN-SPAM, CASL, GDPR, and
> (if you sell regulated financial products) FINRA Rule 2210 / Reg BI.

> **Why "compliant" is also "effective."** Spam filters, not regulators, are your first enemy.
> Harvested lists and mass blasts get your domain blacklisted within days, after which *nothing*
> you send lands — even to warm leads. Every rule below (real addresses, opt-out, slow ramp,
> personalization) is *also* a deliverability tactic. The legal path and the profitable path are
> the same path.

---

## ⚖️ Read this first — the boundaries this toolkit respects

This toolkit **does** help you:
- Find and organize **business** contacts from **legitimate sources** (paid data providers with
  their own license terms, public company pages, opt-in directories, your own network/CRM).
- Enrich a list of company **domains you supply** using licensed APIs (Hunter, Apollo,
  Clearbit, etc.) under *their* terms.
- Draft personalized, honest outreach and track replies.
- Send on a **slow, rate-limited, opt-out-respecting** cadence that you operate.

This toolkit **does not** and **will not**:
- Scrape or "harvest" emails from websites/social networks (explicitly an aggravated violation
  under CAN-SPAM, and a breach of most sites' terms).
- Run dictionary attacks or guess addresses at scale.
- Blast unsolicited mail to purchased/scraped lists.
- Hide your identity, fake headers, or omit an unsubscribe path.

> If you sell **securities or insurance products**, layer two more rules on top: every public
> communication needs **principal pre-approval** and must follow **FINRA Rule 2210** (fair,
> balanced, no guarantees, no performance predictions). Cold-contact rules and **do-not-call**
> lists also apply to *phone* outreach. Loop in your firm's compliance officer before the first
> send — this is not optional in a regulated context.

---

## The system at a glance

```
   1. TARGET            2. SOURCE                3. ENRICH             4. OUTREACH            5. TRACK
  ┌──────────┐        ┌────────────┐          ┌────────────┐        ┌────────────┐        ┌──────────┐
  │ Ideal    │        │ Legitimate │          │ enrich.py  │        │ outreach.py│        │ leads.csv│
  │ Customer │ ─────► │ providers  │ ───────► │ (Hunter/   │ ─────► │ (drafts +  │ ─────► │ status & │
  │ Profile  │        │ + your CRM │          │  Apollo)   │        │  send;     │        │ replies  │
  │ (ICP)    │        │ + referrals│          │ → leads.csv│        │  dry-run)  │        │          │
  └──────────┘        └────────────┘          └────────────┘        └────────────┘        └──────────┘
                                                                          │
                                                                          ▼
                                                                  suppression.csv
                                                              (opt-outs, never contact)
```

Files in this folder:

| File | Purpose |
|---|---|
| [README.md](README.md) | This playbook + ideas (start here) |
| [scripts/enrich_leads.py](scripts/enrich_leads.py) | Turn a list of **company domains you supply** into role-based contacts via a licensed API |
| [scripts/outreach.py](scripts/outreach.py) | Personalize, **dry-run by default**, rate-limited, suppression-aware sender |
| [templates/email_templates.md](templates/email_templates.md) | Honest, high-reply cold-email + follow-up copy |
| [templates/leads.example.csv](templates/leads.example.csv) | The lead schema |
| [templates/suppression.example.csv](templates/suppression.example.csv) | Opt-out / do-not-contact list |
| [COMPLIANCE_CHECKLIST.md](COMPLIANCE_CHECKLIST.md) | Pre-send checklist (CAN-SPAM/CASL/GDPR/2210) |

---

## Step 1 — Define the Ideal Customer Profile (ICP)

Most outreach fails because it targets *everyone*. A tight ICP is the single biggest lever on
reply rate. Fill in:

- **Industry / vertical:** who has the problem your product solves *acutely*?
- **Company size:** employee count / revenue band where the budget and pain both exist.
- **Geography:** which regions (also sets which laws apply — see checklist).
- **Trigger events:** hiring sprees, funding, new regulations, leadership changes, expansion —
  these make outreach *timely* and lift replies massively.
- **The buyer's role:** who signs? who feels the pain? (Often two different people.)
- **Disqualifiers:** who looks like a fit but never buys? Exclude them up front.

> Write this down before sourcing a single contact. A 200-name list that *is* your ICP beats a
> 20,000-name list that isn't — in revenue and in deliverability.

## Step 2 — Source contacts the legitimate way

Ranked by quality (and by how much regulators/spam filters like them):

1. **Warm/referral** — your network, existing customers' referrals, mutual connections. Highest
   conversion, zero list risk. Build a referral ask into every closed deal.
2. **Inbound** — a simple landing page + lead magnet (a useful checklist, a calculator, a short
   guide). People who opt in are gold and fully consented.
3. **Licensed B2B data providers** — Apollo.io, ZoomInfo, Lusha, Cognism, Hunter.io. You pay,
   they carry the licensing/consent compliance, and you use within *their* terms. This is what
   `enrich_leads.py` is built for.
4. **Public professional directories & company "Contact"/"Careers" pages** — for *business*
   role addresses (e.g., a published `hiring@` or a named HR director on the company site).
   Manual, low-volume, generally defensible for B2B.
5. **Events, associations, LinkedIn outreach** — relationship-first, platform-native messaging
   (note: LinkedIn messages aren't email and have their own etiquette/limits).

> **Never** buy a scraped "10 million emails" list. It is the fastest way to get blacklisted and
> the worst-converting data that exists.

## Step 3 — Enrich into a clean list

Use [scripts/enrich_leads.py](scripts/enrich_leads.py). You provide a CSV of **company domains**
(from Step 2) and your own API key for a provider; it returns role-based business contacts and
writes them into the [leads schema](templates/leads.example.csv). It will not invent or
brute-force addresses — it only returns what the licensed provider verifies.

## Step 4 — Write outreach that earns a reply

The whole game is **relevance > volume**. See [templates/email_templates.md](templates/email_templates.md).
Principles:

- **One clear, specific value claim** tied to *their* situation (use a trigger event).
- **Short** — 50–125 words. Mobile-readable. One ask.
- **No hype, no false urgency, no guarantees** (and in a regulated context, none allowed at all).
- **Personalize the first line** with something real about them — this is what separates a reply
  from the trash.
- **Honest subject line** that matches the body (CAN-SPAM requires this *and* it improves trust).
- **A visible opt-out** and your real physical mailing address in the footer.

## Step 5 — Send slowly and track

Use [scripts/outreach.py](scripts/outreach.py). It:

- Runs in **dry-run by default** (prints what it *would* send; you pass `--send` to actually send).
- Skips anyone on `suppression.csv` and anyone already replied/opted-out.
- **Rate-limits** (default ~30/hour, configurable) and supports a daily cap — a slow ramp
  protects your domain reputation.
- Injects the **unsubscribe link + physical address** footer automatically.
- Requires **your own SMTP credentials** (env vars) — it never sends from anything but your
  account.

Then warm up: authenticate your domain (**SPF, DKIM, DMARC**), start at ~20–30/day from a
*secondary* domain, and increase gradually. Reply handling and opt-outs go straight into
`suppression.csv`.

---

## Beyond cold email — higher-leverage angles for procuring clients

Cold email is one channel and rarely the best on its own. Ranked roughly by ROI for a
commission seller:

1. **Referral engine (highest ROI).** Systematize asking. After every win: *"Who else do you
   know with this exact problem?"* Offer a referral incentive where your compliance allows.
   Warm intros convert 3–5× cold.
2. **Account-based, multi-touch sequences.** Pick 50–100 dream accounts. Touch each across
   email + LinkedIn + a value-add (a relevant article, an intro, a useful insight) over weeks.
   Depth beats spray.
3. **Content + inbound.** Publish genuinely useful material for your ICP (a short guide, a
   "5 mistakes" post, a calculator). Inbound leads arrive pre-qualified and consented — the
   opposite of cold-list risk. Your study-guide-writing instinct transfers directly here.
4. **Niche down the messaging.** "I help *[specific vertical]* do *[specific outcome]*" out-pulls
   a generic pitch every time. Build a separate template per vertical.
5. **Partnerships / channel.** Find non-competing people who already sell to your ICP
   (accountants, consultants, complementary vendors) and set up mutual referrals.
6. **Re-engage dormant & lost deals.** The cheapest pipeline is people who already know you.
   A quarterly "still relevant?" touch to past no's and old customers routinely reopens deals.
7. **Local/association presence.** Industry groups, chambers, conferences — relationship-first
   channels with no list-risk and high trust.
8. **Trigger-event monitoring.** Set alerts (funding, hiring, new-office, regulatory change) for
   your ICP and reach out *when the pain is fresh*. Timeliness beats persistence.

> **The meta-point:** you're a commission seller, so your scarce resource is *attention on the
> right accounts*. Spend it on warm, timely, specific outreach to a tight ICP — and let cold
> email be the *fill* around a referral-and-content core, not the whole strategy.

---

## A note on our arrangement

You mentioned commission. I'm an AI assistant — I can't accept payment, hold accounts, or take a
cut, and I won't send anything on your behalf or operate any account for you. What I *can* do is
keep building and refining this toolkit, your templates, your ICP, and your sequences so the
system earns its keep. Treat everything here as yours to run, under your credentials and your
firm's compliance sign-off.

*See the [compliance checklist](COMPLIANCE_CHECKLIST.md) before your first send.*
