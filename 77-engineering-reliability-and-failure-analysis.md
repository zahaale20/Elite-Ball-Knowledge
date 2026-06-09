# Reliability & Failure Analysis — Designing Things That Don't Break

> **Why this exists.** In aerospace and defense, a failure is not an inconvenience — it is
> a lost aircraft, a missed intercept, a casualty, or a grounded fleet. Reliability
> engineering is the quantitative discipline of predicting, measuring, and improving how
> long things work before they fail, and of designing so that *when* a part fails the
> system survives. It turns "it should be reliable" into numbers: MTBF, failure rate,
> probability of mission success, and the redundancy needed to hit a required safety
> target. Without it, you are gambling with hardware you cannot afford to lose.
>
> **What mastering it makes you.** The engineer who can read a Weibull plot and tell
> whether a population is dying of infant mortality or wear-out; who runs an FMEA that
> finds the dangerous failure mode before the field does; who derates a component so it
> lasts; and who computes how much redundancy buys how much availability — and what it
> costs.

Reliability is the quantitative core of the safety assurance argued in
[09-foundations-safety-assurance.md](09-foundations-safety-assurance.md): a safety case is
only as credible as its failure-rate evidence. It draws on the probability of
[03-foundations-mathematics.md](03-foundations-mathematics.md), constrains the
architecture and redundancy of [76-engineering-systems-engineering-mbse.md](76-engineering-systems-engineering-mbse.md),
and is fed by the manufacturing variation of [75-engineering-manufacturing-and-dfm.md](75-engineering-manufacturing-and-dfm.md).
It governs the drivetrains of [73-engineering-mechatronics-and-actuation.md](73-engineering-mechatronics-and-actuation.md),
the boards of [78-engineering-pcb-and-electronics-design.md](78-engineering-pcb-and-electronics-design.md),
and the packs of [79-engineering-batteries-and-energy-storage.md](79-engineering-batteries-and-energy-storage.md).
Sensor drift over life ([74-engineering-sensors-and-instrumentation.md](74-engineering-sensors-and-instrumentation.md))
is a reliability problem, and every reliability claim is demonstrated through the test
regime of [06-foundations-simulation-test-verification.md](06-foundations-simulation-test-verification.md).

---

## Table of Contents

1. [The vocabulary of reliability](#1-the-vocabulary-of-reliability)
2. [The bathtub curve & failure-rate physics](#2-the-bathtub-curve--failure-rate-physics)
3. [The Weibull distribution](#3-the-weibull-distribution)
4. [FMEA & FMECA](#4-fmea--fmeca)
5. [Fault tree analysis](#5-fault-tree-analysis)
6. [Derating & margin](#6-derating--margin)
7. [Redundancy & system reliability](#7-redundancy--system-reliability)
8. [Accelerated life testing](#8-accelerated-life-testing)
9. [Practice this week](#9-practice-this-week)
10. [Sources & further study](#10-sources--further-study)

---

## 1. The vocabulary of reliability

**Reliability** $R(t)$ is the probability a system survives to time $t$ without failure.
It is the complement of the cumulative failure distribution $F(t)$:

$$ R(t) = 1 - F(t) = P(T > t) $$

The **failure rate** (hazard rate) $\lambda(t)$ is the instantaneous rate of failure
*given survival so far* — the conditional failure intensity:

$$ \lambda(t) = \frac{f(t)}{R(t)} = -\frac{1}{R(t)}\frac{dR}{dt} $$

For the common constant-rate regime, $\lambda(t)=\lambda$, reliability is exponential:
$$ R(t) = e^{-\lambda t} $$

**MTBF** (mean time between failures, for repairable systems) or **MTTF** (mean time to
failure, non-repairable) is the expected life:
$$ \text{MTBF} = \int_0^\infty R(t)\,dt = \frac{1}{\lambda} \quad\text{(exponential case)} $$

A crucial subtlety: MTBF of 10,000 hours does **not** mean the part lasts 10,000 hours. In
the exponential model, $R(\text{MTBF}) = e^{-1} \approx 0.37$ — only 37% survive to the
MTBF. MTBF is a rate, not a lifetime. **Availability** for repairable systems combines
MTBF and mean-time-to-repair (MTTR):
$$ A = \frac{\text{MTBF}}{\text{MTBF} + \text{MTTR}} $$

---

## 2. The bathtub curve & failure-rate physics

Real populations show a failure rate that varies over life — the famous **bathtub curve**,
the superposition of three mechanisms:

```
λ(t)
  |\                                      /
  | \  infant                    wear-out/
  |  \ mortality                        /
  |   \   (defects)                    /
  |    \____________________________ /
  |     constant rate (random)  ___/
  +------------------------------------------> t
   burn-in        useful life        end of life
```

- **Infant mortality (decreasing $\lambda$):** manufacturing defects, weak parts. Screened
  out by **burn-in** — running parts under stress to fail the weaklings before shipment.
- **Useful life (constant $\lambda$):** random failures from external stress; this is the
  exponential regime where MTBF rules.
- **Wear-out (increasing $\lambda$):** fatigue, corrosion, electromigration, bearing wear,
  battery aging. Managed by **scheduled replacement** before the rate climbs.

Each region maps to a Weibull shape (§3). The engineering levers differ per region:
burn-in attacks infant mortality, derating and quality attack the random regime,
and life-limiting/replacement attacks wear-out. Knowing *which* region a field failure
came from tells you *what* to fix — the heart of failure analysis.

---

## 3. The Weibull distribution

The **Weibull** is reliability's workhorse because its shape parameter $\beta$ captures all
three bathtub regions in one model. Its reliability and hazard functions:

$$ R(t) = e^{-(t/\eta)^\beta}, \qquad
\lambda(t) = \frac{\beta}{\eta}\left(\frac{t}{\eta}\right)^{\beta-1} $$

where $\eta$ is the **characteristic life** (the time at which 63.2% have failed) and
$\beta$ is the **shape**:

| $\beta$ | Hazard | Bathtub region | Physical meaning |
|---|---|---|---|
| $\beta < 1$ | decreasing | infant mortality | defects, screen with burn-in |
| $\beta = 1$ | constant | useful life | random (Weibull = exponential) |
| $\beta > 1$ | increasing | wear-out | fatigue, aging, corrosion |
| $\beta \approx 3.5$ | ~normal | wear-out | tightly-grouped wear failures |

**Weibull analysis** fits field/test failure times to recover $\beta$ and $\eta$ — usually
by plotting $\ln\ln(1/R)$ vs $\ln t$, which linearizes the Weibull (the slope is $\beta$):

$$ \ln\ln\frac{1}{R(t)} = \beta\ln t - \beta\ln\eta $$

A $\beta$ of 0.6 says "you have a manufacturing problem, add burn-in"; a $\beta$ of 4 says
"you have wear-out, set a replacement interval." This single number redirects the entire
fix strategy. Median-rank regression or maximum likelihood (in Minitab, ReliaSoft, or
`scipy.stats.weibull_min`) does the fit; censored data (units still running) is handled
properly by these tools.

---

## 4. FMEA & FMECA

**Failure Modes and Effects Analysis** is the systematic, bottom-up hunt for how each part
can fail and what happens when it does. **FMECA** adds *criticality*. It is done early
(design FMEA) and on the process (process FMEA), per MIL-STD-1629A / SAE J1739.

For each component, enumerate: failure mode → cause → local effect → system effect →
detection → mitigation. Then prioritize by the **Risk Priority Number**:

$$ \text{RPN} = S \times O \times D $$

where Severity, Occurrence, and Detection are each rated 1–10 (Detection: 10 = undetectable).

```
Item     Failure mode    Effect            S  O  D  RPN  Action
-------  --------------  ----------------  -- -- -- ---  ----------------
Motor    bearing seizes  loss of thrust    9  3  4  108  add temp monitor
ESC      MOSFET short    motor runaway     10 2  6  120  add current limit
Battery  cell vent       fire              10 2  3   60  cell fusing, BMS
Sensor   bias drift      bad estimate      6  5  7  210  online calibration
```

The discipline forces you to confront *every* failure mode before the field does. High-RPN
items get design changes; the FMEA is then re-scored to show risk reduction. Critically,
FMEA finds **single points of failure** — modes with no mitigation and severe effect — that
must be designed out or made redundant (§7). FMEA outputs feed directly into the safety
case of [09-foundations-safety-assurance.md](09-foundations-safety-assurance.md) and the
fault trees of §5.

---

## 5. Fault tree analysis

FMEA is bottom-up (part → effect); **Fault Tree Analysis (FTA)** is top-down (undesired
*event* → all the ways it can happen). Start with a catastrophic top event and decompose
through logic gates to basic events.

```
              [ Loss of aircraft ]
                      |
                    (OR)
        ┌─────────────┼─────────────┐
   [Power loss]  [Control loss]  [Structural]
        |              |
      (AND)          (OR)
   ┌────┴────┐    ┌────┴────┐
[Batt A] [Batt B] [FC fail][Servo fail]
 fails    fails
```

- **OR gate:** the output occurs if *any* input occurs → probabilities add (rare-event
  approximation): $P \approx \sum P_i$.
- **AND gate:** the output occurs only if *all* inputs occur → probabilities multiply (for
  independent events): $P = \prod P_i$.

The AND gate is the mathematics of redundancy: two independent batteries each with
$P_\text{fail}=10^{-3}$ give a combined power-loss probability of $10^{-6}$ — a
thousand-fold improvement, *if they are truly independent*. The **minimal cut sets** (the
smallest combinations of basic events that cause the top event) reveal the system's
weakest paths; a single-element cut set is a single point of failure. FTA quantifies the
top-event probability against the safety target (e.g., $< 10^{-9}$/flight-hour for
catastrophic, per DO-178C/ARP4761), linking directly to
[09-foundations-safety-assurance.md](09-foundations-safety-assurance.md).

---

## 6. Derating & margin

The cheapest reliability improvement is to **not run parts near their limits**. Derating
operates a component below its rated stress so it lives longer. The physics: most failure
mechanisms are stress- and temperature-accelerated, and the **Arrhenius** relation makes
temperature the master variable:

$$ \lambda(T) = \lambda_0 \exp\!\left(-\frac{E_a}{k_B T}\right) $$

A common rule of thumb from Arrhenius: failure rate roughly **doubles per 10 °C** rise. So
keeping a junction 20 °C cooler can quarter its failure rate — which is why thermal design
is reliability design.

| Component | Derate to | Why |
|---|---|---|
| Capacitor (electrolytic) | ≤ 50–60% rated V | life ∝ voltage & temperature |
| Resistor | ≤ 50% rated power | temperature rise |
| Semiconductor junction | ≤ 110–125 °C | Arrhenius |
| Connector | ≤ 50% rated current | contact heating |
| Mechanical fastener | ≤ 25% proof | fatigue margin |

Derating standards (MIL-STD-1547, NASA EEE-INST-002) codify these factors for space and
defense. Derating trades size/cost/mass for life — a deliberate margin decision that
belongs in the trade studies of
[76-engineering-systems-engineering-mbse.md](76-engineering-systems-engineering-mbse.md).

---

## 7. Redundancy & system reliability

System reliability is built from component reliabilities by the architecture's structure.

**Series** (all must work — no redundancy): reliability multiplies, so it is always *lower*
than the worst part:
$$ R_\text{series} = \prod_{i=1}^{n} R_i $$
A system of 100 parts each at $R=0.99$ has only $0.99^{100}\approx 0.37$ system reliability —
the tyranny of series complexity.

**Parallel** (any one suffices — active redundancy): unreliability multiplies, so
reliability rises sharply:
$$ R_\text{parallel} = 1 - \prod_{i=1}^{n}(1 - R_i) $$
Two parallel units at $R=0.9$ give $1-(0.1)^2 = 0.99$.

**k-out-of-n** (need $k$ of $n$, e.g., triplex voting 2oo3) uses the binomial:
$$ R_{k/n} = \sum_{i=k}^{n}\binom{n}{i}R^i(1-R)^{n-i} $$

Redundancy's hidden enemy is **common-cause failure**: shared power, shared software, shared
environment, or a common manufacturing defect can take out "independent" channels together.
True redundancy demands *dissimilar* design (different suppliers, different software, physical
separation) — the lesson behind triple-redundant flight computers with diverse processors.
This is the same fault-tolerance logic as
[09-foundations-safety-assurance.md](09-foundations-safety-assurance.md) and the
distributed-systems redundancy of [05_distributed_systems_comms_mesh.md](05_distributed_systems_comms_mesh.md).

---

## 8. Accelerated life testing

You cannot wait 10,000 hours to learn a 10,000-hour MTBF. **Accelerated Life Testing (ALT)**
stresses parts beyond normal use to provoke failures faster, then extrapolates back via a
physics-of-failure model.

The **acceleration factor** from the Arrhenius model between test temperature $T_t$ and use
temperature $T_u$:
$$ AF = \exp\!\left[\frac{E_a}{k_B}\left(\frac{1}{T_u} - \frac{1}{T_t}\right)\right] $$

One hour at elevated temperature then equals $AF$ hours of field life. Other accelerants:
voltage (inverse power law), thermal cycling (Coffin–Manson for solder fatigue), humidity
(Peck model), vibration.

- **HALT (Highly Accelerated Life Test):** ramp stress (temperature, vibration) until the
  product breaks, to *find* weak links and design margins — a discovery test, not a pass/fail.
- **HASS (Highly Accelerated Stress Screen):** a production screen using the margins HALT
  found, to catch infant-mortality escapes (§2) before shipment.
- **Reliability demonstration:** run $n$ units for time $t$ with zero failures to
  *demonstrate* a reliability at a confidence level (the zero-failure formula gives the
  sample size from the chi-squared distribution).

ALT is how reliability claims get *evidence* rather than assertion — the bridge between the
math here and the verification regime of
[06-foundations-simulation-test-verification.md](06-foundations-simulation-test-verification.md).

---

## 9. Practice this week

1. Fit a Weibull to a set of failure times (use `scipy.stats.weibull_min` or a Weibull plot);
   read off $\beta$ and decide infant-mortality vs wear-out, and the right fix.
2. Run an FMEA on a small subsystem (motor + ESC + battery): enumerate modes, score RPN,
   and propose mitigations for the top three.
3. Build a fault tree for one catastrophic event; compute the top-event probability and
   identify the minimal cut sets and any single points of failure.
4. Compute the reliability of a 50-part series system, then add parallel redundancy to the
   two weakest parts and quantify the improvement — and the common-cause caveat.

---

## 10. Sources & further study

- **O'Connor & Kleyner — *Practical Reliability Engineering*.** The standard textbook; broad and rigorous.
- **MIL-STD-1629A — *Procedures for Performing FMECA*.** The defense FMEA standard.
- **MIL-HDBK-217 / Telcordia SR-332** — component failure-rate prediction (dated but foundational).
- **NIST/SEMATECH e-Handbook of Statistical Methods** — Weibull, ALT, reliability math, free online.
- **SAE ARP4761 — *Guidelines for Conducting Safety Assessment*.** FTA/FMEA for aerospace, pairing with [09-foundations-safety-assurance.md](09-foundations-safety-assurance.md).
- **Nelson — *Accelerated Testing*.** The ALT reference.
- **ReliaSoft / Minitab documentation** for hands-on Weibull and reliability analysis.

> Framing note: Reliability is not luck or quality slogans — it is a quantitative
> engineering discipline with its own mathematics. The engineers who build systems that
> survive are the ones who know whether they are fighting infant mortality or wear-out,
> who find dangerous failure modes with FMEA before the field does, who derate for thermal
> margin, and who buy availability with *truly independent* redundancy rather than the
> illusion of it.
