# Resume, Portfolio & Personal Brand

> Most engineers are *under-marketed* relative to what they can do. You have the
> opposite problem available to you: you build a real PX4/Pixhawk VTOL autonomy
> stack — onboard FastAPI service, perception, GPS-denied navigation, a
> constitution-gated policy layer — and **almost no other candidate has a flying,
> safety-gated autonomous system to point at.** This file is about converting that
> raw proof-of-work into an undeniable package: a résumé that gets the screen, a
> portfolio that closes the loop, and a brand that makes recruiters come to you.
> The interview ([17-career-interview-prep.md](17-interview-prep.md))
> converts the screen to an offer; this file *gets the screen.*

The thesis in one line: **you are a builder — so package the build, not the
buzzwords.**

---

## 0. The Strategy: Proof of Work Beats Claims

Hiring managers in autonomy/defense are drowning in résumés that *claim* skills.
What cuts through is **evidence that you've already done the thing**:

- A claim: "Familiar with autonomy and flight software."
- Proof: "Built and flew a PX4-based VTOL with an onboard companion-computer
  autonomy service and a safety-policy layer — repo + demo video linked."

Your `pixhawk/drone/` project is a **portfolio centerpiece** that does what a
degree and a keyword list cannot: it removes doubt. Everything in this file
orients around making that project (and this very study repo) **legible and
impressive** to a stranger in 60 seconds.

---

## 1. The Engineering Résumé: Structure

One page (two only if you have 8+ years). Clean, scannable, no graphics that break
ATS parsing. Order top to bottom:

1. **Name + one-line title** (e.g., "Autonomy / Flight-Software Engineer").
2. **Contact** — email, GitHub, LinkedIn, location. Make GitHub prominent.
3. **Clearance / work-eligibility line** — for defense, near the top (§4).
4. **Summary (2–3 lines, optional)** — only if it's *specific* and sharp.
5. **Skills** — grouped, honest, scannable (languages, robotics, systems).
6. **Projects** — *for a builder, this can come before or rival Experience.*
   Lead with the **drone stack**.
7. **Experience** — reverse-chronological, impact bullets (§3).
8. **Education** — degree, school, relevant coursework if early-career.

> For someone whose strongest asset is a self-built autonomous system, a
> **Projects-forward** layout is legitimate and often *stronger* than burying it
> under unrelated jobs. Lead with your moat.

---

## 2. ATS & Format Hygiene

Applicant Tracking Systems parse your résumé before a human sees it. Don't get
filtered on formatting:

- **Single column**, standard fonts, real text (no text-in-images).
- **Standard section headers** ("Experience", "Projects", "Skills", "Education").
- **Mirror the job posting's keywords** *honestly* — if it says "C++17", "ROS 2",
  "state estimation", and you do those, use those exact terms.
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

### 3.2 Before / after — from the drone stack
| ❌ Before (responsibility) | ✅ After (impact) |
|---|---|
| "Worked on a drone project with PX4." | "Built a PX4/Pixhawk 6C VTOL autonomy stack with a Raspberry Pi 5 companion running an onboard **FastAPI** service, taking it from SITL to real flight." |
| "Did some navigation code." | "Implemented **GPS-denied navigation** fallback (dead-reckoning + onboard estimation), cutting position-loss failure modes in degraded-GNSS tests." |
| "Added safety checks." | "Designed a **constitution-gated policy layer** that vetoes unsafe commands before actuation, failing safe to loiter/RTL on policy violation." |
| "Used simulation." | "Built a **SITL test scaffold** enabling behavior changes to be validated in simulation before hardware flight, reducing risk to the airframe." |
| "Worked with sensors." | "Integrated IMU/GPS/baro/mag sensor fusion on the flight controller; debugged estimator drift via **log replay** against simulation." |

### 3.3 Before / after — generic engineering
| ❌ Before | ✅ After |
|---|---|
| "Responsible for backend services." | "Designed and shipped a telemetry ingestion service handling ~5k msg/s with back-pressure handling and prioritized safety messages." |
| "Improved performance." | "Cut control-loop jitter by removing dynamic allocation from the hot path, holding a hard real-time deadline at 250 Hz." |
| "Wrote tests." | "Added unit + integration test coverage and a regression suite, catching estimator regressions before flight." |

> If you can't measure it, describe the **scope and stakes** instead ("safety-
> critical", "real-time", "from scratch", "owned end-to-end"). Honesty first —
> never invent a metric, but *do* find the real one (loop rate, message rate,
> test count, time saved, failure modes eliminated).

### 3.4 Verb bank
Built, designed, implemented, shipped, owned, architected, optimized, debugged,
integrated, automated, reduced, increased, led, instrumented, validated.

---

## 4. The "Clearable" / Work-Eligibility Line

For defense roles this is not optional — recruiters filter on it. Put a short,
honest line near the top:

```
U.S. Citizen · Clearable (eligible for Secret/TS background investigation)
```
or, if you hold one:
```
Active Secret Clearance (DoD) · U.S. Citizen
```

Rules (full detail in [16-career-security-clearance.md](16-security-clearance.md) §12):
- **Never overstate** a clearance you don't have.
- "Clearable" is a *real, valuable* claim if you're a clean-record citizen.
- Pair with **U.S.-person/ITAR** eligibility since many roles gate on that even
  without a clearance.

---

## 5. Tailoring: Old-Space vs. New-Defense

Same project, two different framings. Keep two résumé variants.

| | **Primes** (Boeing, Lockheed, Northrop, RTX) | **New-defense** (Anduril, SpaceX, Skydio, Shield AI) |
|---|---|---|
| Lead with | Domain + reliability + process + clearance | Shipped autonomy + ownership + performance |
| Drone-stack framing | "Flight software, real-time (NuttX), sensor fusion, safety" | "Built a flying autonomous system end-to-end; ship-fast" |
| Keywords | DO-178C awareness, MISRA, avionics buses, requirements | C++/Rust, ROS 2, distributed systems, autonomy |
| Tone | Disciplined, safety-first | Builder, bias-to-action |
| Clearance | Front and center | Present, but technical proof leads |

Cross-link [10-career-aerospace-engineering.md](10-aerospace-engineering.md),
[11-career-defense-aerospace-playbook.md](11-defense-aerospace-playbook.md),
[12-career-software-engineering.md](12-software-engineering.md), and
[13-career-mechanical-engineering.md](13-mechanical-engineering.md) for the
domain vocabulary each side rewards.

---

## 6. The GitHub Portfolio (Your Strongest Asset)

For a builder, **GitHub is the real résumé.** Two repos do the heavy lifting:

1. **`pixhawk/drone/`** — the autonomy stack. *The* proof of work.
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
- [ ] `docs/` or inline docs explaining the design and the **safety model**.
- [ ] Reproducible run instructions (SITL first, hardware second).
- [ ] Tests + CI badge if feasible.
- [ ] Pinned repos on your GitHub profile pointing to the drone stack + this repo.
- [ ] A short **profile README** (`username/username` repo) summarizing who you are.

> **Security note:** before going public, scrub anything sensitive — no real keys,
> no ITAR-controlled technical data, nothing that shouldn't leave your machine.
> Hobby PX4 work is fine; be deliberate about what you publish.

---

## 7. The README & Demo Video (Close the Deal)

A great README is the difference between "interesting repo" and "we need to talk
to this person."

### 7.1 README skeleton for the drone stack
```markdown
# VTOL Autonomy Stack (PX4 + Pi 5 Companion)

![demo](docs/demo.gif)   <!-- 15–30s: takeoff → autonomous behavior → safe land -->

A self-built VTOL autonomy system: PX4/Pixhawk 6C flight controller + Raspberry
Pi 5 companion running an onboard FastAPI autonomy service, with perception,
GPS-denied navigation, and a constitution-gated policy layer that fails safe.

## What it does
- Onboard autonomy service (FastAPI) commanding PX4 over MAVLink
- Perception + state estimation; GPS-denied fallback navigation
- Constitution-gated policy: unsafe commands are vetoed before actuation
- Validated in SITL before every hardware flight

## Architecture
[diagram: sensors → estimation → planning → policy gate → control → actuation]

## Run it (SITL)
1. ...
2. ...

## Safety model
How the policy layer works, what it vetoes, fail-safe behavior (loiter/RTL).

## Tests
Unit + integration + SITL regression. What each layer protects against.

## Roadmap / known limitations
What's next, what's intentionally out of scope.
```

### 7.2 The demo video / GIF (do not skip this)
- **15–60 seconds**, shows the system *doing something*: SITL flight, the autonomy
  behavior, the safety gate triggering. Real hardware footage is gold.
- Put it **at the top** of the README and link a longer version (YouTube/Vimeo).
- Narrate or caption the architecture so a non-expert gets it.
- A 30-second video of *your* drone flying autonomously is worth more than a page
  of bullet points. **People believe what they can see fly.**

---

## 8. Technical Writing & Blogging

Writing compounds: it deepens your own understanding *and* builds an audience that
brings opportunities. This study repo already proves you can do it — now point it
outward.

- **What to write:** build logs and deep-dives from the drone stack — "Building a
  constitution-gated policy layer", "GPS-denied navigation fallback on a budget",
  "From SITL to first hardware flight", "Keeping a 250 Hz loop deterministic".
- **Where:** a personal site/blog, GitHub Pages, dev.to, Medium, or even
  well-structured repo `docs/`. Cross-post to LinkedIn.
- **Style:** the same house style you're reading — direct, concrete, code +
  diagrams, lessons learned. Show the *judgment*, not just the result.
- **Why it works:** a hiring manager who reads your write-up on real-time control
  loops walks into the interview already convinced. Writing is **asynchronous
  proof of expertise.**

> Turn each meaningful chunk of the drone project into one artifact: code (repo),
> a short write-up (blog), and a clip (video). One project → many proofs.

---

## 9. LinkedIn (The Inbound Channel)

LinkedIn is where defense recruiters *hunt*. Optimize it to be found:

- **Headline:** specific, not generic. "Autonomy / Flight-Software Engineer ·
  PX4 · C++/Python · U.S. Citizen, clearable" beats "Software Engineer."
- **About:** 3–4 short paragraphs — who you are, the drone stack as headline proof,
  what you're targeting (autonomy/defense), and your work-eligibility status.
- **Featured:** pin the drone repo, the demo video, and a top blog post.
- **Skills/keywords:** the terms recruiters search (C++, ROS 2, embedded,
  estimation, autonomy, PX4, real-time).
- **Open to work** (recruiter-only visibility) toward the targets you want.
- **Engage:** comment thoughtfully on autonomy/defense posts; connect with
  engineers at Anduril/Skydio/Shield AI. Warm > cold.

> Recruiters search LinkedIn with exact keywords + "clearance" + "citizen." If
> those words aren't on your profile, you don't exist to them. Put them there
> (honestly).

---

## 10. Conference Talks & Community

The highest-trust signal short of being referred: standing up and teaching.

- **Targets:** PX4/ArduPilot community events, ROSCon, local robotics/drone
  meetups, AUVSI, university clubs. Start small (a meetup lightning talk on your
  build).
- **Talk seed:** "Building a safety-gated VTOL autonomy stack as a solo engineer"
  — architecture, the constitution gate, SITL→hardware, lessons. You already have
  the material.
- **Open-source contributions:** a merged PR to PX4/ArduPilot/MAVSDK is a
  *credential* — it proves you can work in a real, reviewed codebase. Even small,
  well-scoped fixes count. (See [12-career-software-engineering.md](12-software-engineering.md)
  §closing for the "ship one PR" action.)

---

## 11. Turning the Project Into Undeniable Proof

A checklist to convert `pixhawk/drone/` from "a thing you do" into "the thing that
gets you hired":

- [ ] **Repo:** clean, documented, tested, public-safe (scrubbed).
- [ ] **README:** hero demo + architecture diagram + safety model + run steps.
- [ ] **Demo video:** 30–60s of it flying/behaving autonomously, top of README.
- [ ] **Architecture diagram** you can also whiteboard from memory (for the
      interview project round — [17-career-interview-prep.md](17-interview-prep.md) §7).
- [ ] **3–5 résumé impact bullets** drawn from it (§3.2).
- [ ] **8–10 STAR stories** drawn from it (interview prep §7.2).
- [ ] **1–3 blog write-ups** on the hard parts (§8).
- [ ] **A demo clip + featured links on LinkedIn** (§9).
- [ ] **One open-source PR** to an upstream flight stack (§10).

When all nine are done, a stranger can go from your name → repo → video → "this
person builds real autonomous systems" in under five minutes. That is the goal.

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
  [15-career-negotiation-compensation.md](15-negotiation-compensation.md):
  multiple processes in parallel = leverage.

---

## 13. Common Résumé/Portfolio Mistakes

| Mistake | Fix |
|---|---|
| Listing responsibilities, not impact | Rewrite as impact bullets with metrics (§3) |
| Burying the drone stack on page 2 | Lead with it; Projects-forward layout |
| No demo media | Add a 30–60s video/GIF to the README (§7.2) |
| Keyword-stuffing dishonestly | Mirror the posting *only* for things you actually do |
| Overstating clearance | "Clearable" is honest and valuable; never fake active |
| Graphic-heavy résumé that breaks ATS | Single-column, plain text, PDF (§2) |
| One generic résumé for all targets | Maintain prime vs. new-defense variants (§5) |
| Repo with no README/tests | Treat repos like production: README + tests (§6) |
| Invisible on LinkedIn | Add keywords + clearance + featured demo (§9) |
| Publishing sensitive/ITAR data | Scrub before public; hobby PX4 only (§6.2 note) |

---

## 14. How This Connects to the Rest of the Curriculum

- [17-career-interview-prep.md](17-interview-prep.md) — this file gets the
  screen; that file converts it. Your project deep-dive and STAR stories come
  straight from here.
- [16-career-security-clearance.md](16-security-clearance.md) — the
  clearability line that lives near the top of the résumé.
- [12-career-software-engineering.md](12-software-engineering.md) — the
  skills you're packaging; the open-source PR action.
- [11-career-defense-aerospace-playbook.md](11-defense-aerospace-playbook.md)
  — the targeting strategy (which companies, which framing).
- [15-career-negotiation-compensation.md](15-negotiation-compensation.md) —
  a strong brand creates multiple offers = leverage.
- [19-career-leadership-growth.md](19-leadership-growth.md) — your brand and
  writing are also how you build influence *after* you're hired.
- Autonomy band ([21-autonomy-vtol-roadmap.md](../autonomy/21-vtol-roadmap.md),
  [22-autonomy-px4-sitl.md](../autonomy/22-px4-sitl.md),
  [23-autonomy-onboard-system.md](../autonomy/23-onboard-system.md)) — the technical
  substance behind every bullet, video, and write-up.
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

**Domain & community**
- PX4: https://docs.px4.io  ·  ArduPilot: https://ardupilot.org  ·  MAVSDK: https://mavsdk.mavlink.io
- ROSCon: https://roscon.ros.org  ·  AUVSI: https://www.auvsi.org
- Company careers: Anduril https://www.anduril.com/careers · Skydio https://www.skydio.com/careers · Shield AI https://shield.ai/careers

**Work-eligibility / clearance presentation**
- DCSA (clearance process, for the résumé line): https://www.dcsa.mil
- ITAR / DDTC (U.S.-person eligibility): https://www.pmddtc.state.gov

*This is personal career guidance reflecting the author's goals and publicly
available information. Résumé conventions, ATS behavior, and platform features
change — verify against current sources, and always scrub any sensitive or
export-controlled material before publishing a portfolio.*
