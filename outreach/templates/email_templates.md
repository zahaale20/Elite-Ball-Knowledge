# Email Templates — Honest, High-Reply B2B Outreach

> Loaded by `outreach.py`. Format rules: each template starts with `## <name>`, then a line
> `Subject: ...`, then the body. Placeholders like `{first_name}`, `{company}`, `{title}` are
> filled from the leads CSV. The sender automatically appends your name, company, **physical
> mailing address, and opt-out line** (from `sender_config.json`) — do not duplicate them here.

**Writing rules (these drive replies AND keep you compliant):**
- One specific, honest value claim. No hype, no false urgency, **no guarantees**.
- 50–125 words. One ask. Mobile-readable.
- Personalize the first line with something real (`{personalization}` — fill it per lead).
- Subject must honestly describe the body (CAN-SPAM + trust).
- If you sell regulated products, every template needs **principal/compliance approval** before
  use, and must follow FINRA Rule 2210 (fair, balanced, no performance predictions).

---

## intro
Subject: quick question about {company}

Hi {first_name},

{personalization}

I'll keep this short: I work with {target_segment} on {value_prop}, and given {trigger} at
{company} I thought it might be relevant to you as {title}.

Worth a 15-minute call to see if it's a fit? If it's not the right time or not your area, just
let me know and I won't follow up.

Thanks for reading.

## follow_up_1
Subject: re: quick question about {company}

Hi {first_name},

Floating this back to the top of your inbox in case it got buried. The short version: we help
{target_segment} with {value_prop_short}.

If this isn't a priority right now, no problem at all — just reply "not now" and I'll close the
loop. Otherwise, are you open to a brief call next week?

## value_add
Subject: thought this might be useful for {company}

Hi {first_name},

No pitch here — I put together a short {resource_type} on {topic} that {target_segment} have
found genuinely useful, and thought it might help your team at {company}.

Happy to send it over. And if {value_prop_short} is ever on your radar, I'm glad to talk; if
not, ignore me guilt-free.

## breakup
Subject: closing the loop, {first_name}

Hi {first_name},

I've reached out a couple of times and haven't heard back, which usually means the timing's off
or it's not a fit — both totally fine. I'll stop here so I'm not cluttering your inbox.

If anything changes around {value_prop_short}, my door's open. Wishing you and {company} well.
