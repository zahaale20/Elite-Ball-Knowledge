# Module 117 — Applied Statistics & Causal Inference

> **Why this file exists.** The probability module ([02](../mathematics/02-probability-and-stochastic.md))
> gives you the formal machinery of random variables; this module is about the harder, dirtier,
> higher-stakes skill of **drawing correct conclusions from real data** — flight logs, A/B tests,
> reliability trials, field telemetry, sensor characterization. Almost every expensive mistake in a
> technical organization is, at root, a statistics mistake: a feature shipped on a fluke result, a
> reliability claim built on a biased sample, a "the new controller is better" conclusion that was
> noise, a correlation mistaken for a cause. The difference between an engineer who *runs numbers*
> and one who *understands what the numbers can and cannot say* is enormous and rare.
>
> **What mastering it makes you.** The person in the room who can look at a chart and say "that
> difference is within noise," or "that sample is biased and here's how," or "correlation isn't
> causation here — you have a confounder," and be right. In a world drowning in dashboards, the
> ability to extract *valid causal conclusions* from messy data is one of the most leveraged
> analytical skills there is.

**Companion practice.** This module deepens [02-probability-and-stochastic.md](../mathematics/02-probability-and-stochastic.md)
toward *inference and causality*, supplies the rigor behind
[06-foundations-simulation-test-verification.md](06-simulation-test-verification.md) (how many
trials, what does "passed" mean statistically), and underpins the data-flywheel claims in
[05-tesla-vertical-integration-data.md](../companies/05-tesla-vertical-integration-data.md). The
decision-theoretic uses of these tools live in
[15-decision-making-and-rationality.md](15-decision-making-and-rationality.md).

---

## Table of Contents

1. [Description vs inference vs causation](#1-description-vs-inference-vs-causation)
2. [Sampling: where most errors are born](#2-sampling-where-most-errors-are-born)
3. [Estimation, standard error, and confidence intervals](#3-estimation-standard-error-and-confidence-intervals)
4. [Hypothesis testing and what a p-value actually means](#4-hypothesis-testing-and-what-a-p-value-actually-means)
5. [Errors, power, and effect size](#5-errors-power-and-effect-size)
6. [The replication crisis and how to not be part of it](#6-the-replication-crisis-and-how-to-not-be-part-of-it)
7. [Bayesian inference: updating beliefs with data](#7-bayesian-inference-updating-beliefs-with-data)
8. [Regression and the dangers within it](#8-regression-and-the-dangers-within-it)
9. [Causal inference: the ladder, confounders, and DAGs](#9-causal-inference-the-ladder-confounders-and-dags)
10. [Experiments, A/B tests, and quasi-experiments](#10-experiments-ab-tests-and-quasi-experiments)
11. [Failure modes and statistical fallacies](#11-failure-modes-and-statistical-fallacies)
12. [Practice this month](#12-practice-this-month)
13. [Sources & Citations](#sources--citations)

---

## 1. Description vs inference vs causation

Three distinct questions get blurred together constantly, and keeping them separate is half the
discipline:

- **Description** — what is true *in this dataset*? (the mean latency was 12 ms). No uncertainty
  about the data itself; you measured it.
- **Inference** — what can I conclude about the *broader population/process* that generated this
  data? (the true mean latency is 12 ± 2 ms with 95% confidence). This is where sampling and
  uncertainty enter.
- **Causation** — if I *intervene* and change X, what happens to Y? (switching controllers *causes*
  3 ms lower latency). This is a fundamentally stronger claim than correlation and requires
  fundamentally stronger evidence — usually an experiment or a credible causal model.

The single most common analytical crime is **promoting a descriptive or correlational finding to a
causal claim** without earning it. "Drones running firmware v2 had fewer crashes" is descriptive; it
becomes causal only if v2 was *assigned* in a way that rules out the alternative that better pilots,
newer hardware, or calmer weather happened to coincide with v2.

> **Senior tell.** A junior says "X is correlated with Y, so X drives Y." A senior immediately asks
> "what else could produce that correlation?" — reverse causation, a common cause, selection, or
> chance — and only then considers causation.

---

## 2. Sampling: where most errors are born

No statistical method can rescue a biased sample; the bias is baked in before any math runs. The
foundational requirement of inference is that your sample is *representative* of the population you
want to conclude about. The classic ways this breaks:

- **Selection bias** — the sample is systematically different from the population. Testing your
  autopilot only on calm days and concluding it's reliable; surveying only users who didn't churn.
- **Survivorship bias** — you only see the survivors. The canonical story: Abraham Wald and the WWII
  bombers — the returning planes showed bullet holes in the wings and fuselage, and the naïve
  conclusion was "armor those areas." Wald's insight: armor the areas with *no* holes (engines,
  cockpit), because planes hit *there* didn't come back to be measured. The data you can see is
  conditioned on survival. This shows up everywhere: "successful founders dropped out, so dropping
  out helps" ignores the invisible graveyard of dropouts who failed.
- **Non-response / participation bias** — who opts in differs from who doesn't.
- **Measurement bias** — the instrument itself skews the reading (a miscalibrated sensor, a leading
  survey question).

```
   POPULATION (what you want to conclude about)
        │  sampling process  ← bias enters HERE, and no later math removes it
        ▼
   SAMPLE (what you measured) ──▶ statistics ──▶ inference
```

The practical mandate: **before trusting any analysis, interrogate how the data was collected.**
Most of the time, the fatal flaw is upstream of the computation, in a sampling decision nobody
wrote down.

---

## 3. Estimation, standard error, and confidence intervals

When you estimate a quantity (a mean, a failure rate) from a sample, the estimate has uncertainty,
and quantifying it is the whole point. Key ideas:

- **Standard error (SE)** measures how much your *estimate* would vary across repeated samples. For a
  sample mean, $SE = \sigma/\sqrt{n}$ — note the $\sqrt{n}$: **to halve your uncertainty you need
  four times the data.** This diminishing return governs every "how many trials do we need?"
  conversation.
- **The Central Limit Theorem** is why this works: the distribution of a sample mean tends toward
  Gaussian as $n$ grows, *regardless of the underlying distribution's shape* (given finite
  variance). This is the engine that lets you put error bars on almost anything.
- **A confidence interval (CI)** is a range that, under repeated sampling, would contain the true
  value a stated fraction (e.g. 95%) of the time. The correct interpretation is subtle and almost
  universally botched: a 95% CI does **not** mean "95% probability the true value is in this
  specific interval" (that's a Bayesian credible-interval statement). It means "the *procedure*
  that produced this interval captures the truth 95% of the time." For practical purposes, treat the
  CI as your honest statement of precision — and always report it. **A point estimate without an
  interval is half a result.**

The behavioral upshot: when someone shows you "v2 is 8% better," your first question is "± what?"
If the interval comfortably includes zero, there is no result yet, only noise wearing a number.

---

## 4. Hypothesis testing and what a p-value actually means

The Null Hypothesis Significance Testing (NHST) framework is the lingua franca of empirical claims,
and it is almost universally misunderstood. The machinery:

1. State a **null hypothesis** $H_0$ (usually "no effect" — the two controllers have equal mean
   latency) and an alternative $H_1$.
2. Compute a **test statistic** and, from it, a **p-value**: *the probability of observing data at
   least this extreme **if the null were true.***
3. If $p$ is below a threshold $\alpha$ (conventionally 0.05), reject $H_0$ as "statistically
   significant."

What a p-value **is not** — and these errors cause real damage:

- It is **not** the probability the null is true. $P(\text{data}\mid H_0) \neq P(H_0 \mid \text{data})$.
  Confusing them is the **prosecutor's fallacy**.
- It is **not** the probability your result is a fluke, nor a measure of effect size. A tiny,
  meaningless effect can be wildly "significant" with enough data; a large, important effect can be
  "non-significant" with too little.
- "Not significant" is **not** "no effect." Absence of evidence isn't evidence of absence — you may
  simply have lacked the power to detect a real effect (§5).

The honest way to use it: a small p-value says "this data would be surprising under the null,"
which is *weak evidence* against the null — to be combined with effect size, prior plausibility,
and replication, not treated as a verdict. The 0.05 line is an arbitrary convention, not a law of
nature, and treating it as a bright line between "true" and "false" is the source of much bad
science.

---

## 5. Errors, power, and effect size

Every test trades off two error types:

| | $H_0$ true | $H_0$ false |
|---|---|---|
| **Reject $H_0$** | Type I error (false positive), rate $\alpha$ | Correct (true positive) |
| **Fail to reject** | Correct | Type II error (false negative), rate $\beta$ |

- **Type I (false positive):** you claim an effect that isn't real. Controlled by $\alpha$.
- **Type II (false negative):** you miss a real effect. Controlled by $\beta$.
- **Power** = $1 - \beta$: the probability of detecting a real effect of a given size. Power rises
  with sample size, effect size, and lower noise.
- **Effect size** is the *magnitude* of the difference — the thing you actually care about.
  Significance tells you "probably not zero"; effect size tells you "is it big enough to matter?"
  A statistically significant 0.2 ms latency improvement is engineering noise.

**Run a power analysis *before* collecting data** to size your experiment: given the smallest effect
worth caring about and your noise level, how many trials do you need? Skipping this leads to two
disasters — underpowered studies that miss real effects and waste effort, and the temptation to
keep collecting data until significance appears (a form of p-hacking, §6).

> **Senior tell.** "Is it significant?" is the junior question. "What's the effect size, the CI, and
> was the study powered to detect an effect worth caring about?" is the senior one.

---

## 6. The replication crisis and how to not be part of it

Large swaths of published science fail to replicate — not mostly from fraud, but from a collection
of honest-seeming practices that manufacture false positives. Know them so you don't commit them:

- **p-hacking / data dredging** — trying many analyses, subgroups, or outcomes and reporting the one
  that crossed 0.05. With twenty independent tests at $\alpha = 0.05$, you expect one "significant"
  result by pure chance ([the multiple-comparisons problem](https://xkcd.com/882/), the "green
  jelly beans cause acne" comic). Correct with pre-registration or multiplicity corrections
  (Bonferroni, FDR).
- **HARKing** (Hypothesizing After Results are Known) — finding a pattern in the data, then
  presenting it as if you'd predicted it. This converts exploratory noise-fitting into a fake
  confirmatory result. Exploration is fine; *labeling* it as confirmation is the sin.
- **Optional stopping** — peeking at the data and stopping as soon as $p < 0.05$. This inflates the
  false-positive rate dramatically because you're giving randomness many chances to cross the line.
- **Garden of forking paths** — even without conscious gaming, the many defensible analysis choices
  you'd have made *differently* given different data inflate false positives.

The defenses: **pre-register** your hypothesis and analysis before seeing data; **separate
exploratory from confirmatory** work honestly; **report everything you tried**, not just what
worked; **replicate** before believing; and weight a result by its **prior plausibility** — an
extraordinary claim from one underpowered study deserves skepticism, not a headline.

---

## 7. Bayesian inference: updating beliefs with data

The Bayesian frame is often more natural for engineering decisions than NHST, because it answers the
question you actually have: *given this data, what should I now believe?*

$$ P(H \mid D) = \frac{P(D \mid H)\, P(H)}{P(D)} $$

- **Prior** $P(H)$ — what you believed before the data.
- **Likelihood** $P(D \mid H)$ — how well the hypothesis predicts the data.
- **Posterior** $P(H \mid D)$ — your updated belief.

The power of this frame: it forces you to make your **prior explicit** and it combines evidence
across studies naturally (today's posterior is tomorrow's prior). It also dissolves the
prosecutor's fallacy — it keeps $P(H \mid D)$ and $P(D \mid H)$ distinct by construction. The
canonical lesson is the **base-rate / medical-test problem**: a test that is 99% accurate for a
disease with 0.1% prevalence still yields *mostly false positives*, because the rare true cases are
swamped by false positives from the huge healthy population. Ignore the base rate (the prior) and
you will be confidently wrong. This is the same machinery as the EKF in
[09-autonomy-gnc.md](../autonomy/09-gnc.md) — a Kalman filter *is* recursive Bayesian estimation.

Bayesian and frequentist methods are tools, not tribes; use the prior explicitly when you have real
prior information and a decision to make, and use frequentist tests when you need a convention-bound,
prior-free statement. Both demand the same honesty about uncertainty.

---

## 8. Regression and the dangers within it

Regression — fitting $Y$ as a function of predictors $X$ — is the workhorse of applied statistics
and a minefield:

- **Interpretation of coefficients.** In multiple regression, a coefficient is the association of
  that predictor with $Y$ *holding the others fixed* — which is only meaningful if "holding fixed"
  is coherent and you've included the right variables.
- **Confounding via omitted variables.** Leave out a common cause of both $X$ and $Y$ and your
  coefficient is biased — possibly even sign-flipped (§9).
- **Overfitting.** A model with enough parameters fits the noise, not the signal, and predicts new
  data terribly. This is the **bias–variance tradeoff**: too simple → biased/underfit; too complex →
  high-variance/overfit. Defend with held-out test data and cross-validation. (Deep treatment in
  [01-autonomy-ml-ai.md](../autonomy/01-ml-ai.md).)
- **Extrapolation.** A model is only trustworthy within the range of data it saw. Predicting outside
  it is a leap of faith that has killed real systems.
- **Simpson's paradox.** An association can *reverse* when you aggregate or disaggregate by a group.
  A treatment can look worse overall yet better in every subgroup, because group sizes and base
  rates differ. The "right" level of aggregation is a *causal* question, not a statistical one — you
  cannot resolve it from the numbers alone.

---

## 9. Causal inference: the ladder, confounders, and DAGs

Judea Pearl's **Ladder of Causation** is the cleanest framework for what "causal" even means:

1. **Association** ("seeing") — $P(Y \mid X)$. What ordinary statistics and most ML do. "Patients
   who took the drug recovered more."
2. **Intervention** ("doing") — $P(Y \mid do(X))$. What happens if I *set* X? This is different from
   merely observing X, because intervening cuts X off from its usual causes.
3. **Counterfactuals** ("imagining") — what *would have* happened to this specific unit had X been
   different? The deepest rung, and what "causation" ultimately means.

The central obstacle on rungs 2–3 is the **confounder**: a variable that causes both X and Y,
manufacturing an association with no causal link from X to Y.

```
        Z  (confounder: e.g. pilot skill)
       ╱ ╲
      ▼   ▼
      X    Y           Observing X–Y correlation tells you nothing causal
  (firmware) (crashes) until you account for Z.
```

The breakthrough tool is the **causal DAG** (directed acyclic graph): draw your assumed causal
structure, and the graph's rules tell you *which variables to control for* to isolate the causal
effect — and, crucially, that controlling for the *wrong* variable (a "collider" or a mediator) can
**create** bias rather than remove it. This is why "just control for everything" is wrong: adjusting
for a collider opens a spurious path. Causal inference is the discipline of getting from rung 1
(what you can passively measure) to rung 2 (what you actually want to know) using either a
randomized experiment or explicit, defensible causal assumptions.

> **Senior tell.** "Control for more variables" is the naïve instinct. The causal-literate engineer
> knows that *which* variables to adjust for is dictated by the causal structure, and that adjusting
> for the wrong one injects bias.

---

## 10. Experiments, A/B tests, and quasi-experiments

The cleanest route to rung 2 is the **randomized controlled experiment**: randomly assign units to
treatment or control. Randomization is magic because it makes the groups statistically identical *on
every variable, known and unknown*, so any outcome difference is attributable to the treatment. It
severs the confounding arrows by design — no causal model required.

- **A/B testing** is randomized experimentation applied to products: randomly serve variant A or B,
  compare a metric. Pitfalls: peeking/optional stopping (§6), testing too many metrics (§6),
  network effects that violate the independence of units, and novelty effects that fade.
- **When you can't randomize** (you can't randomly assign drones to crash, or countries to
  policies), **quasi-experimental** methods approximate it: difference-in-differences, regression
  discontinuity, instrumental variables, matching. Each substitutes a *defensible assumption* for
  randomization, and each is only as good as that assumption — which must be argued, not assumed.
- **Natural experiments** exploit a quasi-random real-world event (a policy that applied to one
  group by an arbitrary cutoff) to recover causal effects.

The hierarchy of evidence, roughly: randomized experiment > well-designed quasi-experiment >
adjusted observational study > raw correlation. Know where your evidence sits, and claim only what
that tier supports.

---

## 11. Failure modes and statistical fallacies

| Fallacy / failure | What it is | Defense |
|---|---|---|
| **Correlation ⇒ causation** | Treating association as a causal claim | DAGs; experiments; ask "what else could cause this?" |
| **Survivorship bias** | Analyzing only the survivors | Ask what's missing from the sample (Wald's bombers) |
| **p-hacking** | Fishing for significance | Pre-register; correct for multiplicity |
| **Base-rate neglect** | Ignoring the prior/prevalence | Bayes; always ask "out of how many?" |
| **Prosecutor's fallacy** | $P(D\mid H)$ confused with $P(H\mid D)$ | Keep the two directions distinct |
| **Simpson's paradox** | Aggregation flips the conclusion | Choose aggregation level by causal reasoning |
| **Overfitting** | Model fits noise | Held-out test data; cross-validation |
| **Texas sharpshooter** | Drawing the target after the shots | Pre-specify hypotheses |
| **Regression to the mean** | Extreme readings naturally moderate | Compare to baseline, not to the extreme point |
| **Confounding** | A hidden common cause | Randomize, or adjust per a causal model |

The unifying lesson: **statistics is mostly a discipline of doubt.** The math is the easy part; the
skill is relentlessly asking *how could this conclusion be wrong?* — biased sample, confounder,
chance, wrong aggregation — before you believe it.

---

## 12. Practice this month

- **Re-analyze one real result from your `drone/` testing** with a confidence interval, not just a
  point estimate. Ask: does the interval include "no difference"?
- **Run a power analysis** before your next test campaign: given the smallest effect worth caring
  about, how many trials do you need?
- **Find one "X causes Y" claim** in a paper or news story and draw its causal DAG. Identify the
  confounder that would invalidate it, and what experiment would settle it.
- **Hunt survivorship bias** in one belief you hold ("successful people do X"). Where is the
  invisible graveyard?
- **Do the medical-test Bayes calculation by hand** (99% accurate test, 0.1% prevalence) until the
  base-rate lesson is in your bones.

---

## Sources & Citations

**Canonical works**
- Judea Pearl & Dana Mackenzie — *The Book of Why* — the ladder of causation, DAGs, accessible.
- Judea Pearl — *Causality* — the rigorous treatment.
- David Freedman — *Statistical Models: Theory and Practice* — clear, skeptical, applied.
- Andrew Gelman & Jennifer Hill — *Data Analysis Using Regression and Multilevel Models*.
- Darrell Huff — *How to Lie with Statistics* — short, timeless, on the fallacies.
- Regina Nuzzo, "Scientific method: Statistical errors," *Nature* (2014) — the p-value problem.
- Ioannidis, "Why Most Published Research Findings Are False," *PLoS Medicine* (2005).
- Angrist & Pischke — *Mostly Harmless Econometrics* — quasi-experimental causal inference.

**Cross-links**
- Formal probability: [02-probability-and-stochastic.md](../mathematics/02-probability-and-stochastic.md).
- Recursive Bayesian estimation in practice (the EKF): [09-autonomy-gnc.md](../autonomy/09-gnc.md).
- Bias–variance and overfitting in ML: [01-autonomy-ml-ai.md](../autonomy/01-ml-ai.md).
- Using these tools for decisions: [15-decision-making-and-rationality.md](15-decision-making-and-rationality.md).
