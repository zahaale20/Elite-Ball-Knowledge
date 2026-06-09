# Observability & SRE — Running Systems That Stay Up

> **Why this exists.** A flight controller that works on the bench and a fleet of autonomous vehicles that stays alive through a six-month deployment are separated by one discipline: operating software you cannot physically reach. When a swarm of UAS is loitering over contested airspace and the ground station shows a frozen telemetry pane, you do not get to attach a debugger — you get the signals the system was designed to emit, and nothing else. Observability is the practice of building systems that explain their own behavior; Site Reliability Engineering (SRE) is the practice of running them to an explicit, measured standard of reliability. Without both, "it works" is a hope, not an engineering claim. This module makes you the person who knows whether the system is healthy *before* the customer tells you it isn't.

> **What mastering it makes you.** The engineer who can take a screenshot of a dashboard at 3 a.m. and say "the p99 latency on the perception service crossed budget eleven minutes ago, here is the trace, here is the rollback" — and be right. The rarest combination in software: someone who can both build the thing and keep it running under fire.

Observability is where the systems-thinking of [01_first_principles_systems_engineering.md](../foundations/01-first_principles_systems_engineering.md) becomes a daily operational reality, and where the test-and-verification mindset of [06-foundations-simulation-test-verification.md](../foundations/06-simulation-test-verification.md) extends from pre-flight into production. The career framing of [12-career-software-engineering.md](../career/12-software-engineering.md) explains why SRE roles command leverage; the real-time discipline of [04-foundations-modern-cpp-realtime.md](../foundations/04-modern-cpp-realtime.md) is what your latency budgets are spent on. This module opens the back half of the "Software, Compute & Infrastructure" band and pairs tightly with [89-software-cloud-and-kubernetes.md](89-cloud-and-kubernetes.md) (where your services run), [92-software-performance-engineering.md](92-performance-engineering.md) (why a latency SLO is violated), [93-software-api-and-system-design.md](93-api-and-system-design.md) (what you are observing), and [94-software-testing-and-verification-deep.md](94-testing-and-verification-deep.md) (the pre-production half of the same loop). It builds on the distributed-systems foundations in [05_distributed_systems_comms_mesh.md](../foundations/05-distributed_systems_comms_mesh.md).

---

## 1. Observability vs. monitoring — a real distinction

Monitoring answers questions you already knew to ask: "Is CPU above 90%?" Observability is the property that lets you ask *new* questions of a running system without shipping new code. The formal idea borrows from control theory: a system is **observable** if its internal state can be reconstructed from its outputs. For software, the "outputs" are the telemetry it emits, and the test is brutal — when a novel failure appears, can you diagnose it from existing signals, or do you have to redeploy with more logging?

| | **Monitoring** | **Observability** |
|---|---|---|
| Question shape | Known-unknowns ("is X up?") | Unknown-unknowns ("why is this one request slow?") |
| Data model | Pre-aggregated counters | High-cardinality, raw events |
| Failure mode it catches | Anticipated | Novel / emergent |
| Typical artifact | Threshold alert | Ad-hoc query over traces |

The practical implication: instrument for **high cardinality**. A counter `requests_total` is monitoring. An event carrying `{request_id, customer_id, region, vehicle_id, route_version, latency_ms}` is observability — because six months from now you can group by `route_version` to find that one bad deploy without having predicted you'd need to.

---

## 2. The three pillars: metrics, logs, traces

These are the substrate. Each answers a different question; mature systems carry all three and correlate them.

### Metrics — cheap numbers over time

A metric is a numeric measurement sampled at intervals: a counter, a gauge, or a histogram. They are cheap to store (a few bytes per data point), cheap to aggregate, and the right tool for *trends and alerts*. The dominant model is the Prometheus exposition format — dimensional time series identified by a name plus key/value labels.

```
# HELP http_request_duration_seconds Request latency.
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{route="/track",le="0.01"} 24054
http_request_duration_seconds_bucket{route="/track",le="0.05"} 31922
http_request_duration_seconds_bucket{route="/track",le="0.1"}  32108
http_request_duration_seconds_bucket{route="/track",le="+Inf"} 32140
http_request_duration_seconds_sum{route="/track"} 1190.4
http_request_duration_seconds_count{route="/track"} 32140
```

Histograms are the workhorse: they let you compute percentiles *after the fact* across many instances. The critical instinct: **never alert on averages.** A mean latency of 40 ms can hide a p99 of 4 seconds that is timing out every hundredth user. Watch the tail.

```promql
# p99 latency over 5 minutes, in seconds
histogram_quantile(
  0.99,
  sum by (le, route) (rate(http_request_duration_seconds_bucket[5m]))
)
```

The Four Golden Signals (from Google's SRE book) are the default starting set for any user-facing service:

| Signal | What it measures | Why it matters |
|---|---|---|
| **Latency** | Time to serve a request (split success vs error!) | User-perceived speed; tail = pain |
| **Traffic** | Demand on the system (req/s, msgs/s) | Context for everything else |
| **Errors** | Rate of failed requests | Direct correctness signal |
| **Saturation** | How "full" the system is (queue depth, CPU, mem) | Predicts imminent failure |

### Logs — the high-fidelity narrative

A log line is a timestamped, ideally **structured** record of an event. The single highest-leverage change a team can make is moving from free-text logs to structured (JSON) logs, because structured logs are queryable.

```json
{"ts":"2026-06-09T14:22:01.118Z","level":"error","service":"perception",
 "trace_id":"a1b2c3d4","vehicle_id":"uas-074","event":"frame_drop",
 "camera":"front","queue_depth":48,"latency_ms":312,"cause":"gpu_oom"}
```

Now `cause:"gpu_oom" AND vehicle_id:"uas-074"` is a query, not a `grep` through gigabytes. Discipline: log *decisions and state transitions*, not noise. Every line should be one a tired on-call engineer would want at 3 a.m. Logs are expensive at volume; sample aggressively for high-traffic success paths, keep everything for errors.

### Traces — causality across services

In a system where one request touches a dozen services, metrics tell you *that* it's slow and logs tell you *what* each service saw, but only a distributed **trace** tells you *where the time went*. A trace is a tree of spans, each span a timed operation, linked by a propagated `trace_id` and `parent_span_id`.

```
trace_id=a1b2c3d4   total=312ms
├─ ingest            [■■............]  18ms
├─ perception        [..■■■■■■■■....] 210ms   ← the culprit
│  ├─ gpu_infer      [...■■■■■■.....] 160ms
│  └─ postprocess    [.........■■...]  44ms
├─ fusion            [...........■.]  22ms
└─ planner           [............■]  31ms
```

**OpenTelemetry (OTel)** is now the vendor-neutral standard: one set of SDKs and a wire protocol (OTLP) that emits all three pillars and lets you swap backends (Jaeger, Tempo, a commercial vendor) without re-instrumenting. The strategic move is to instrument with OTel and treat the backend as replaceable.

The pillars converge through **correlation**: stamp the `trace_id` into every log line and into exemplars on your metrics. Then the workflow becomes: alert fires on a metric → jump to an exemplar trace → jump to the logs for the slow span. That chain is the whole game.

---

## 3. SLIs, SLOs, and error budgets — reliability as a number

Reliability without a number is an argument. SRE replaces the argument with a contract.

- **SLI (Service Level Indicator):** a measured ratio of good events to valid events. *"Proportion of `/track` requests served in < 200 ms with a 2xx."*
- **SLO (Service Level Objective):** the target for that SLI over a window. *"99.9% over 28 days."*
- **SLA (Service Level Agreement):** the contractual, often financial, consequence if you miss the SLO. Engineers set SLOs; lawyers write SLAs.

$$ \text{SLI} = \frac{\text{good events}}{\text{valid events}}, \qquad \text{Error budget} = (1 - \text{SLO}) \times \text{total events} $$

The **error budget** is the genius of the model. If your SLO is 99.9%, you are *permitted* 0.1% failure. That budget is a currency:

| SLO | Allowed downtime / 30 days | Allowed downtime / year |
|---|---|---|
| 99% ("two nines") | ~7.2 hours | ~3.65 days |
| 99.9% ("three nines") | ~43.2 minutes | ~8.76 hours |
| 99.99% ("four nines") | ~4.3 minutes | ~52.6 minutes |
| 99.999% ("five nines") | ~26 seconds | ~5.26 minutes |

Each extra nine is roughly 10× the cost and engineering effort. **Do not buy nines you do not need.** A batch analytics pipeline does not need the SLO of a flight-safety telemetry link.

The error budget resolves the eternal dev-vs-ops fight. If the budget is *unspent*, you can ship aggressively — risk is affordable. If the budget is *exhausted*, you freeze features and spend the next cycle on reliability. The policy is mechanical, not political; that is why it works. Burn-rate alerting turns this into an early-warning system:

```promql
# Page if we're burning 14.4x the budget over 1h (fast-burn):
# at this rate a 30-day budget is gone in ~2 days.
(
  1 - (
    sum(rate(slo_good_total[1h])) / sum(rate(slo_valid_total[1h]))
  )
) > (14.4 * (1 - 0.999))
```

Multi-window, multi-burn-rate alerts (a fast 1h window *and* a slow 6h window must both fire) cut false pages dramatically — the heart of the Google SRE workbook's alerting chapter.

---

## 4. Incident response — the system around the outage

Outages are not exceptional; they are a baseline rate you manage. A mature incident process is what keeps a 20-minute blip from becoming a 6-hour catastrophe.

**Roles (ICS-style, borrowed from emergency services):**

| Role | Owns |
|---|---|
| **Incident Commander (IC)** | Coordination, decisions, the single source of truth. *Not* hands-on debugging. |
| **Operations / Ops lead** | Actually touching the system: rollbacks, mitigations. |
| **Communications lead** | Status page, stakeholder updates, customer-facing comms. |
| **Scribe** | Timeline of what happened and when — feeds the postmortem. |

The cardinal rule: **mitigate first, diagnose later.** If a bad deploy is burning the budget, *roll it back now* — understanding the root cause is a luxury you earn after the bleeding stops. Severity levels (SEV1 = customer-facing outage, SEV3 = degraded, internal) set the response intensity and who gets paged.

**Blameless postmortems** are the cultural keystone. The premise: humans operating in good faith inside a system are not the root cause; the system that *allowed* a single human error to cause an outage is. A postmortem names contributing factors, builds a timeline, and emits concrete, owned, dated action items. The moment postmortems become about punishment, engineers stop reporting near-misses, and you go blind. This is the same logic as aviation's no-fault reporting culture — see the safety-assurance arguments in [09-foundations-safety-assurance.md](../foundations/09-safety-assurance.md).

```
POSTMORTEM  —  Perception service p99 breach, 2026-06-09
Impact:    7% of /track requests > 1s for 31 min. Error budget: 18% consumed.
Trigger:   Deploy v2.14 enabled a new GPU batch size.
Timeline:  14:22 alert fires → 14:29 IC declared → 14:33 rollback started
           → 14:41 latency recovered.
Root-ish:  Batch size 64 exceeded GPU memory under peak traffic → OOM → retries.
Why not caught: Load test used batch 32; peak-traffic path untested.
Actions:   [P1] Load test at production batch size  (owner: A.Z., due 06-16)
           [P2] Add GPU-mem saturation SLI + alert    (owner: SRE, due 06-20)
           [P3] Canary deploys for perception svc      (owner: platform, due 06-30)
```

---

## 5. On-call — making humans sustainable

On-call is where SRE meets human factors. A rotation that burns people out produces worse reliability, because exhausted engineers make worse decisions and the good ones leave.

- **Every page must be actionable and urgent.** If a page does not require a human to do something *now*, it should be a ticket, not a page. Alert fatigue — pages that are routinely ignored — is the deadliest failure mode, because the one real page hides among the noise.
- **Sustainable load:** a common SRE norm caps actionable pages at roughly **two per on-call shift**; more than that is a signal to fix the system, not the human.
- **Compensation and time:** on-call is labor. It is paid or comped, and a heavy night earns recovery time the next day.
- **Runbooks:** every alert links to a runbook — a checklist of "what this means, how to confirm, how to mitigate." Runbooks turn a 3 a.m. panic into a procedure, and let less-experienced engineers hold the line.
- **Follow-the-sun** rotations across time zones avoid waking anyone at 3 a.m. when the team is distributed enough to support it.

The meta-principle: **toil is the enemy.** Toil is manual, repetitive, automatable operational work that scales linearly with traffic. SRE explicitly budgets a fraction of engineering time (Google's target: ≥50%) to *engineering away* toil. If you are doing the same manual remediation weekly, the real bug is the absence of automation.

---

## 6. Capacity planning & load — staying ahead of demand

You cannot keep a system up if you run out of capacity. Capacity planning is the quantitative discipline of provisioning ahead of demand, and its mathematics come straight from queueing theory.

**Little's Law** is the one equation every SRE keeps in their head. For any stable system, the average number of items in the system equals arrival rate times average time in system:

$$ L = \lambda W $$

where $L$ is concurrency (requests in flight), $\lambda$ is arrival rate (req/s), and $W$ is average latency (s). If you serve 500 req/s at 200 ms average latency, you have $L = 500 \times 0.2 = 100$ requests in flight on average — so a thread pool of 50 will queue and your latency will blow up. This single relation predicts saturation before it happens.

The deeper warning comes from queueing theory's **utilization curve**. As utilization $\rho$ approaches 1, queueing delay diverges non-linearly — roughly proportional to $\rho / (1 - \rho)$:

```
Latency
  │                                   *
  │                              *
  │                        *
  │                  *
  │           *
  │     *
  │ *  *
  └──────────────────────────────────  Utilization ρ
  0%        50%       70%   85%  95%  →100%
```

This is why **you never run hot.** A system at 95% CPU is not "efficient"; it is one traffic spike from a latency cliff. Target headroom (commonly 50–70% steady-state utilization) so that bursts and instance failures are absorbable. Capacity planning combines: a demand forecast (organic growth + known launches), a per-instance capacity number from **load testing**, and a safety margin for the curve above. Load testing must hit the *real* peak path — the postmortem above failed precisely because the load test used the wrong batch size.

Autoscaling (covered operationally in [89-software-cloud-and-kubernetes.md](89-cloud-and-kubernetes.md)) handles short-term elasticity, but it is not a substitute for capacity planning: scaling has a lag, and you cannot autoscale past a quota or a downstream bottleneck you forgot to provision.

---

## 7. The maturity ladder — where teams actually are

Observability and SRE are adopted in stages. Knowing the rung you are on tells you the next move.

| Level | State | Symptom | Next step |
|---|---|---|---|
| 0 | "ssh in and tail the log" | Outages found by customers | Centralize logs |
| 1 | Centralized logs + basic host metrics | "Is it up?" answerable | Add app-level metrics + dashboards |
| 2 | Golden-signal dashboards, threshold alerts | Alert fatigue begins | Define SLOs, alert on budget burn |
| 3 | SLOs, error budgets, distributed tracing | Diagnose novel failures fast | Blameless postmortems, toil budget |
| 4 | Budget-driven release policy, <50% toil | Reliability is a planned number | Chaos engineering, capacity modeling |

Most real teams live at Level 1–2 and believe they are at 3. The honest test is Section 1's: when something *new* breaks, can you diagnose it from existing telemetry? If the answer is "we added more logging and redeployed," you are not yet observable.

A final synthesis: observability and SRE are the production-side mirror of the verification discipline in [06-foundations-simulation-test-verification.md](../foundations/06-simulation-test-verification.md) and [94-software-testing-and-verification-deep.md](94-testing-and-verification-deep.md). Testing proves the system correct *before* release against known scenarios; observability proves it healthy *after* release against the messy real world. A system you can deploy but cannot observe is a system you cannot honestly claim to operate.

---

## Sources & further study

- **Betsy Beyer et al., *Site Reliability Engineering: How Google Runs Production Systems*** — the foundational text; read the SLO and error-budget chapters twice.
- **Betsy Beyer et al., *The Site Reliability Workbook*** — the practical companion: SLO implementation, alerting math, on-call.
- **Charity Majors, Liz Fong-Jones & George Miranda, *Observability Engineering*** — the high-cardinality, events-first modern view (Honeycomb school).
- **Cindy Sridharan, *Distributed Systems Observability*** (free O'Reilly report) — concise framing of the three pillars.
- **Brendan Gregg, *Systems Performance*** — the saturation/USE-method lens that underpins capacity work.
- **Nicole Forsgren, Jez Humble & Gene Kim, *Accelerate*** — why reliability and delivery speed correlate (DORA metrics).
- **Google SRE "Four Golden Signals"** and the **OpenTelemetry** docs — keep both bookmarked.
- **John Allspaw, "Blameless PostMortems and a Just Culture"** (Etsy engineering blog) — the cultural keystone in one essay.

> Framing note: Building a system is a finite act; operating it is an unbounded one. The engineer who can only build ships a demo. The engineer who can also observe, measure, and keep a system inside an explicit reliability budget ships a *product* — and in autonomy and defense, where the system runs unattended in places you cannot reach, that second engineer is the one whose work is actually trusted with lives.
