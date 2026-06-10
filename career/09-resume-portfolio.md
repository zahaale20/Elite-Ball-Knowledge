# Resume, Portfolio & Personal Brand

> Most engineers are *under-marketed* relative to what they can do. The fix is
> available to anyone who builds: ship one **substantial project you actually
> made** — a side project, an open-source library, a SaaS app, a production
> service, a data pipeline — and **almost no other candidate has a real, working
> system to point at.** This file is about converting that raw proof-of-work into
> an undeniable package: a résumé that gets the screen, a portfolio that closes
> the loop, and a brand that makes recruiters come to you. The interview
> ([08-interview-prep.md](08-interview-prep.md)) converts the screen to an offer;
> this file *gets the screen.*

The thesis in one line: **you are a builder — so package the build, not the
buzzwords.**

---

## 0. The Strategy: Proof of Work Beats Claims

Hiring managers are drowning in résumés that *claim* skills. What cuts through is
**evidence that you've already done the thing**:

- A claim: "Familiar with backend systems and APIs."
- Proof: "Built and shipped a service handling real traffic, with tests, CI, and a
  documented design — repo + live demo linked."

A substantial project you built and shipped is a **portfolio centerpiece** that
does what a degree and a keyword list cannot: it removes doubt. Everything in this
file orients around making that project (and this very study repo) **legible and
impressive** to a stranger in 60 seconds.

---

## 1. The Engineering Résumé: Structure

One page (two only if you have 8+ years). Clean, scannable, no graphics that break
ATS parsing. Order top to bottom:

1. **Name + one-line title** (e.g., "Backend / Full-Stack Engineer").
2. **Contact** — email, GitHub, LinkedIn, location. Make GitHub prominent.
3. **Work-eligibility line** — only if relevant (visa/authorization) (§4).
4. **Summary (2–3 lines, optional)** — only if it's *specific* and sharp.
5. **Skills** — grouped, honest, scannable (languages, frameworks, systems).
6. **Projects** — *for a builder, this can come before or rival Experience.*
   Lead with your **flagship project**.
7. **Experience** — reverse-chronological, impact bullets (§3).
8. **Education** — degree, school, relevant coursework if early-career.

> For someone whose strongest asset is a self-built, shipped system, a
> **Projects-forward** layout is legitimate and often *stronger* than burying it
> under unrelated jobs. Lead with your moat.

---

## 2. ATS & Format Hygiene

Applicant Tracking Systems parse your résumé before a human sees it. Don't get
filtered on formatting:

- **Single column**, standard fonts, real text (no text-in-images).
- **Standard section headers** ("Experience", "Projects", "Skills", "Education").
- **Mirror the job posting's keywords** *honestly* — if it says "TypeScript",
  "PostgreSQL", "distributed systems", and you do those, use those exact terms.
- **PDF** unless they ask otherwise; name it `First_Last_Resume.pdf`.
- No tables-within-tables, no headers/footers with critical info, no emojis.
- Quantify everything you can; numbers survive skimming.

---

## 3. Impact Bullets (Before / After)

The core skill of résumé writing is the **impact bullet**:
**`Action verb → what you did → technology → measurable result/why it mattered.`**
Weak bullets describe *responsibilities*; strong bullets describe *outcomes*.

### 3.1 The formula
> **[Strong verb] [specific thing] using [tech], [resulting in measurable
> impact].**

### 3.2 Before / after — from your flagship project
| ❌ Before (responsibility) | ✅ After (impact) |
|---|---|
| "Worked on a web app." | "Built and shipped a full-stack web app (React + Node/PostgreSQL) from scratch, taking it from prototype to a deployed product with real users." |
| "Did some API work." | "Designed a **REST/GraphQL API** with auth, rate limiting, and pagination, reducing client round-trips and cutting p95 latency." |
| "Added validation." | "Implemented an **input-validation and authorization layer** that rejects malformed/unauthorized requests before they hit the database, closing a class of security bugs." |
| "Used a test environment." | "Built a **CI test scaffold** so changes are validated automatically before merge, reducing regressions reaching production." |
| "Worked with data." | "Built a **data pipeline** ingesting and transforming third-party feeds; debugged throughput bottlenecks via profiling and structured logging." |

### 3.3 Before / after — generic engineering
| ❌ Before | ✅ After |
|---|---|
| "Responsible for backend services." | "Designed and shipped an ingestion service handling ~5k msg/s with back-pressure handling and prioritized message processing." |
| "Improved performance." | "Cut request latency by removing N+1 queries and adding caching, holding a sub-100 ms p95 under load." |
| "Wrote tests." | "Added unit + integration test coverage and a regression suite, catching breaking changes before release." |

> If you can't measure it, describe the **scope and stakes** instead ("production",
> "high-throughput", "from scratch", "owned end-to-end"). Honesty first —
> never invent a metric, but *do* find the real one (request rate, latency,
> test count, time saved, bugs eliminated).

### 3.4 Verb bank
Built, designed, implemented, shipped, owned, architected, optimized, debugged,
integrated, automated, reduced, increased, led, instrumented, validated.

---

## 4. The Work-Eligibility Line (When It's Relevant)

Most roles don't need this, but where work authorization matters — visa
sponsorship, remote/onshore requirements, or government-adjacent work — a short,
honest line near the top saves everyone a screening round:

```
Authorized to work in [country] · No sponsorship required
```
or, if you need sponsorship, say so plainly:
```
Requires visa sponsorship (e.g., H-1B / work permit)
```

Rules:
- **Never overstate** your eligibility or hide a sponsorship need — it surfaces
  later and wastes the relationship.
- A clean, no-sponsorship-needed status is a *real, valuable* signal — state it.
- For roles with extra gates (e.g., citizenship or clearance requirements in
  defense/government work), check the specific posting and present only what is
  honestly true. See [07-security-clearance.md](07-security-clearance.md) if that
  applies to your targets.

---

## 5. Tailoring: One Project, Two Framings

The same project can be framed for different kinds of employers. Keep two résumé
variants and lead with what each side rewards.

| | **Established / enterprise** | **Startup / high-growth** |
|---|---|---|
| Lead with | Reliability + process + scale + ownership | Shipped product + ownership + velocity |
| Project framing | "Designed for maintainability, tested, documented" | "Built and shipped end-to-end; iterate fast" |
| Keywords | Architecture, code review, reliability, CI/CD | Full-stack, 0→1, product sense, ownership |
| Tone | Disciplined, quality-first | Builder, bias-to-action |
| Emphasis | Depth and rigor | Breadth and shipping speed |

Cross-link [01-aerospace-engineering.md](01-aerospace-engineering.md),
[02-defense-aerospace-playbook.md](02-defense-aerospace-playbook.md),
[03-software-engineering.md](03-software-engineering.md), and
[04-mechanical-engineering.md](04-mechanical-engineering.md) for the
domain vocabulary each field rewards.

---

## 6. The GitHub Portfolio (Your Strongest Asset)

For a builder, **GitHub is the real résumé.** Two repos do the heavy lifting:

1. **Your flagship project** — the substantial thing you built and shipped. *The*
   proof of work.
2. **This study repo** — a public, well-organized mastery curriculum demonstrating
   depth, range, and the ability to learn and document systematically. (Recruiters
   *love* visible, structured self-direction.)

### 6.1 What makes a portfolio repo impressive
- **A README that sells in 30 seconds** (§7) — what it is, a demo media, how to run.
- **Clean structure** — logical folders, no dead code, sensible naming.
- **Real commits over time** — shows sustained work, not a weekend dump.
- **Tests** — even modest test coverage signals professionalism (matches your own
  standard: design tests across unit/integration/exploratory levels and state the
  risks each prevents).
- **Documentation** — architecture notes, decisions, tradeoffs.
- **A LICENSE** and a clear "what's mine vs. upstream" note.

### 6.2 Repo hygiene checklist
- [ ] Top-level README with a hero demo (GIF/video) and architecture diagram.
- [ ] `docs/` or inline docs explaining the design and key decisions.
- [ ] Reproducible run instructions (local setup, then deploy).
- [ ] Tests + CI badge if feasible.
- [ ] Pinned repos on your GitHub profile pointing to the flagship project + this repo.
- [ ] A short **profile README** (`username/username` repo) summarizing who you are.

> **Security note:** before going public, scrub anything sensitive — no real keys,
> secrets, customer data, or proprietary code that shouldn't leave your machine.
> Personal/side-project work is fine; be deliberate about what you publish.

---

## 7. The README & Demo Video (Close the Deal)

A great README is the difference between "interesting repo" and "we need to talk
to this person."

### 7.1 README skeleton for your flagship project
```markdown
# [Project Name] — [one-line description]

![demo](docs/demo.gif)   <!-- 15–30s: the core flow / feature in action -->

A self-built [web app / API / data pipeline / library]: [stack summary], with
[key capability], [key capability], and a [reliability/security] layer that
fails gracefully.

## What it does
- Core feature 1 (and the tech behind it)
- Core feature 2; how data/requests flow through the system
- Reliability/security layer: invalid or unauthorized input is rejected safely
- Validated by automated tests before every release

## Architecture
[diagram: client → API → validation/auth → business logic → data store]

## Run it (local)
1. ...
2. ...

## Reliability / security model
How the validation/auth layer works, what it rejects, graceful-failure behavior.

## Tests
Unit + integration + regression. What each layer protects against.

## Roadmap / known limitations
What's next, what's intentionally out of scope.
```

### 7.2 The demo video / GIF (do not skip this)
- **15–60 seconds**, shows the system *doing something*: the core user flow, a key
  feature working, the failure path handled gracefully. Real product footage is gold.
- Put it **at the top** of the README and link a longer version (YouTube/Vimeo).
- Narrate or caption the architecture so a non-expert gets it.
- A 30-second clip of *your* system actually working is worth more than a page
  of bullet points. **People believe what they can see run.**

---

## 8. Technical Writing & Blogging

Writing compounds: it deepens your own understanding *and* builds an audience that
brings opportunities. This study repo already proves you can do it — now point it
outward.

- **What to write:** build logs and deep-dives from your flagship project —
  "Designing a request-validation layer that fails safe", "Cutting p95 latency on
  a budget", "From prototype to first production deploy", "Keeping a hot path
  fast under load".
- **Where:** a personal site/blog, GitHub Pages, dev.to, Medium, or even
  well-structured repo `docs/`. Cross-post to LinkedIn.
- **Style:** the same house style you're reading — direct, concrete, code +
  diagrams, lessons learned. Show the *judgment*, not just the result.
- **Why it works:** a hiring manager who reads your write-up on, say, scaling a
  service walks into the interview already convinced. Writing is **asynchronous
  proof of expertise.**

> Turn each meaningful chunk of the project into one artifact: code (repo),
> a short write-up (blog), and a clip (video). One project → many proofs.

---

## 9. LinkedIn (The Inbound Channel)

LinkedIn is where recruiters *hunt*. Optimize it to be found:

- **Headline:** specific, not generic. "Backend Engineer · Go/Python · Distributed
  systems · Open to opportunities" beats "Software Engineer."
- **About:** 3–4 short paragraphs — who you are, your flagship project as headline
  proof, what you're targeting, and (if relevant) your work-eligibility status.
- **Featured:** pin the project repo, the demo video, and a top blog post.
- **Skills/keywords:** the terms recruiters search (the languages, frameworks,
  and systems you actually work with).
- **Open to work** (recruiter-only visibility) toward the targets you want.
- **Engage:** comment thoughtfully on posts in your field; connect with engineers
  at companies you admire. Warm > cold.

> Recruiters search LinkedIn with exact keywords. If the terms that describe your
> work aren't on your profile, you don't exist to them. Put them there
> (honestly).

---

## 10. Conference Talks & Community

The highest-trust signal short of being referred: standing up and teaching.

- **Targets:** language/framework meetups, regional tech conferences, online
  communities, university clubs. Start small (a meetup lightning talk on your
  build).
- **Talk seed:** "Building and shipping a [project] as a solo engineer"
  — architecture, the hard tradeoffs, prototype→production, lessons. You already
  have the material.
- **Open-source contributions:** a merged PR to a project you use is a
  *credential* — it proves you can work in a real, reviewed codebase. Even small,
  well-scoped fixes count. (See [03-software-engineering.md](03-software-engineering.md)
  §closing for the "ship one PR" action.)

---

## 11. Turning the Project Into Undeniable Proof

A checklist to convert your flagship project from "a thing you do" into "the thing
that gets you hired":

- [ ] **Repo:** clean, documented, tested, public-safe (scrubbed).
- [ ] **README:** hero demo + architecture diagram + design notes + run steps.
- [ ] **Demo video:** 30–60s of it working, top of README.
- [ ] **Architecture diagram** you can also whiteboard from memory (for the
      interview project round — [08-interview-prep.md](08-interview-prep.md) §7).
- [ ] **3–5 résumé impact bullets** drawn from it (§3.2).
- [ ] **8–10 STAR stories** drawn from it (interview prep §7.2).
- [ ] **1–3 blog write-ups** on the hard parts (§8).
- [ ] **A demo clip + featured links on LinkedIn** (§9).
- [ ] **One open-source PR** to a project you use (§10).

When all nine are done, a stranger can go from your name → repo → video → "this
person builds real, working systems" in under five minutes. That is the goal.

---

## 12. Networking & Referrals (Multiplier on Everything)

A referral beats a cold application by a wide margin. Your portfolio makes
referrals *easy to give* — people refer candidates they can vouch for, and your
repo + video does the vouching.

- Reach out to engineers (not just recruiters) at target companies with a
  **specific, short** message + your demo link. "I built X; you work on Y; can I
  ask you two questions?" converts far better than "looking for opportunities."
- Convert every interaction into a relationship, not a transaction.
- Use the comp/leverage framing in
  [06-negotiation-compensation.md](06-negotiation-compensation.md):
  multiple processes in parallel = leverage.

---

## 13. Common Résumé/Portfolio Mistakes

| Mistake | Fix |
|---|---|
| Listing responsibilities, not impact | Rewrite as impact bullets with metrics (§3) |
| Burying the flagship project on page 2 | Lead with it; Projects-forward layout |
| No demo media | Add a 30–60s video/GIF to the README (§7.2) |
| Keyword-stuffing dishonestly | Mirror the posting *only* for things you actually do |
| Misstating work eligibility | State it plainly and honestly; never hide a sponsorship need |
| Graphic-heavy résumé that breaks ATS | Single-column, plain text, PDF (§2) |
| One generic résumé for all targets | Maintain enterprise vs. startup variants (§5) |
| Repo with no README/tests | Treat repos like production: README + tests (§6) |
| Invisible on LinkedIn | Add keywords + featured demo (§9) |
| Publishing sensitive/proprietary data | Scrub before public; personal work only (§6.2 note) |

---

## 14. How This Connects to the Rest of the Curriculum

- [08-interview-prep.md](08-interview-prep.md) — this file gets the
  screen; that file converts it. Your project deep-dive and STAR stories come
  straight from here.
- [07-security-clearance.md](07-security-clearance.md) — if your targets
  require clearance, the eligibility line that lives near the top of the résumé.
- [03-software-engineering.md](03-software-engineering.md) — the
  skills you're packaging; the open-source PR action.
- [02-defense-aerospace-playbook.md](02-defense-aerospace-playbook.md)
  — the targeting strategy (which companies, which framing) if defense is a target.
- [06-negotiation-compensation.md](06-negotiation-compensation.md) —
  a strong brand creates multiple offers = leverage.
- [10-leadership-growth.md](10-leadership-growth.md) — your brand and
  writing are also how you build influence *after* you're hired.
- [02-ten-year-mastery-plan.md](../foundations/02-ten-year-mastery-plan.md) — treat "package and
  publish the build" as a standing track, refreshed each time the project advances.

---

## Sources & Citations

**Résumé & engineering-career references**
- Google — "How to write a resume / interview prep" (Tech Dev Guide):
  https://techdevguide.withgoogle.com/paths/interview/
- *Cracking the Coding Interview* (McDowell) — résumé chapter, CareerCup.
- The Tech Resume Inside Out (Gergely Orosz): https://thetechresume.com
- Harvard Office of Career Services — résumé/cover-letter guides:
  https://careerservices.fas.harvard.edu

**Portfolio, writing & brand**
- GitHub Docs — profile README & repo best practices: https://docs.github.com
- GitHub Pages (free project sites): https://pages.github.com
- Julia Evans — on technical blogging (widely cited): https://jvns.ca/blog/
- dev.to: https://dev.to  ·  Medium: https://medium.com
- Red Blob Games — exemplar of explaining technical work visually:
  https://www.redblobgames.com

**Community & open source**
- ROSCon (example of a domain conference): https://roscon.ros.org
- Open-source contribution guides: https://opensource.guide
- Meetup (find local tech meetups): https://www.meetup.com

**Work-eligibility presentation**
- USCIS (U.S. work authorization basics): https://www.uscis.gov
- For roles that require clearance, see [07-security-clearance.md](07-security-clearance.md).

*This is general career guidance reflecting widely held conventions and publicly
available information. Résumé conventions, ATS behavior, and platform features
change — verify against current sources, and always scrub any sensitive or
proprietary material before publishing a portfolio.*

---

## ⚡ The Insider Layer — What the Field Knows but Rarely Writes Down

The templates teach you formatting. What they don't tell you is that a résumé is a
document read twice — once by software, once by a human in a hurry — and almost
every rule that matters follows from those two brutal facts.

### You get six to ten seconds and the top third of the page
Recruiters skim, they don't read, and eye-tracking studies put the dwell time in
seconds with attention concentrated on the **top third**. Everything follows from
this: your strongest, most quantified bullet goes *first*, not buried under
"Education"; your most impressive project leads the projects section; the
bottom half of page one is nearly invisible. Design for the skim — if a stranger
can't extract "what they did and how well" in one pass, the content quality is
irrelevant because it was never read.

### The ATS does literal string matching — mirror the posting's exact words
Before a human sees it, an applicant-tracking system parses your résumé and scores
keyword overlap against the job description. It is not semantic: it often won't
equate "GNC" with "guidance, navigation, and control," or "C++" with "modern
C++," so you must include the posting's *exact* nouns (spelled out *and*
abbreviated). The defensible, non-gaming version of this: read the JD, and
wherever you genuinely have the skill, use *their* phrasing for it. Fancy
two-column templates with text in graphics frequently parse to garbage — a clean
single-column layout is an ATS feature, not a lack of taste.

### The impact bullet is the entire game: verb → what → quantified result
The difference between a résumé that lands and one that dies is almost entirely
bullet construction. "Responsible for flight software" is a job description;
"Wrote the EKF attitude estimator in C++; cut heading drift 40% and flew it on a
Pixhawk-class board" is *evidence*. Every bullet should answer **what did you do,
and how do we know it mattered** — with a number wherever one can possibly be
attached. Quantify scope when you can't quantify outcome ("across 12k LOC," "on a
6-person team"). Bullets without numbers read as claims; bullets with numbers read
as facts.

### Green squares are a myth; a clean README is the real portfolio
Nobody hiring you cares about your GitHub contribution graph — the "commit every
day" advice is folklore. What a reviewer actually clicks is your *pinned repo's
README*, and they decide in seconds whether you're serious: a crisp problem
statement, an architecture diagram, a **GIF or short video of the thing working**,
and setup instructions that run. One polished project with a demo beats twenty
abandoned tutorials. The demo clip in particular is an unfair advantage because it
collapses all the reviewer's doubt about whether you really built it — most
candidates never make one.

### One project, mined for many artifacts, beats many shallow projects
A single substantial build — say, an autonomy stack — can legitimately generate a
résumé bullet, a portfolio README, a demo video, a technical blog post, a
conference-talk proposal, and a LinkedIn post. Depth is a *multiplier*: the same
work, presented through five surfaces, looks like a body of work, while five
half-finished repos look like a graveyard. Reviewers read depth as the ability to
*finish*, which is the rarest and most valued signal of all.

### LinkedIn is an inbound channel recruiters keyword-search — optimize it as one
Most people treat LinkedIn as a static résumé mirror. Recruiters actually use it
as a *search engine*, running boolean queries on skills, titles, and locations —
so your headline and skills section are query bait, and "Open to Work" plus the
right keywords turns it into passive inbound. The asymmetry is enormous: a strong
LinkedIn presence makes opportunities come to *you*, inverting the entire outbound
application grind. Fill the skills section with the literal terms your target
roles search for.

### The referral makes the résumé a formality — so optimize for the human, not the bot
When someone inside refers you, your résumé stops being a gate and becomes a
briefing document for an interviewer already inclined to like you. This flips the
optimization: keyword-stuffing for the ATS matters less, and a *clear, compelling
narrative* a human can act on matters more. The strategic implication for your
whole job search is that effort spent earning one genuine referral often
out-returns hours spent tuning bullets for software. See
[08-interview-prep.md](08-interview-prep.md).

### Scrub secrets before you publish — it's a clearance and ITAR tripwire
A public portfolio is a permanent, indexed artifact, and pushing API keys, a
former employer's proprietary data, or anything export-controlled is a genuine
risk — not just embarrassing, but potentially an ITAR violation or a personal-conduct
problem on a clearance file. Before any repo goes public: rotate and remove keys,
confirm nothing traces to controlled technical data, and assume a future
background investigator will read every commit. The discipline of *what you don't
publish* is part of the professional signal.
