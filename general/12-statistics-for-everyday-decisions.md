# Statistics & Probability for Everyday Decisions

> **Why this exists.** You are drowning in numbers — health studies, polls, risk
> warnings, financial returns, news charts — and almost all of them are designed,
> intentionally or not, to mislead an untrained reader. The good news is that you
> do not need a statistics degree to defend yourself. A handful of deep ideas —
> base rates, distributions, correlation vs. causation, sampling, and what a
> p-value actually means — let you cut through most of the noise and the
> manipulation. These ideas are not academic; they are the difference between
> being fooled by a scary headline and seeing the boring truth underneath it.
>
> **What understanding it gives you.** A built-in nonsense detector for numbers,
> the ability to ask the one question that deflates most bad statistics, and
> calibrated humility about what data can and cannot tell you.

This is the everyday companion to the formal treatment in
[../mathematics/02-probability-and-stochastic.md](../mathematics/02-probability-and-stochastic.md).
It supports critical reading of health claims in
[08-health-foundations-sleep-food-movement.md](08-health-foundations-sleep-food-movement.md),
energy claims in [09-how-the-electric-grid-and-energy-work.md](09-how-the-electric-grid-and-energy-work.md),
and the manipulation defense in
[../mindset-and-society/01-psychological-manipulation-defense.md](../mindset-and-society/01-psychological-manipulation-defense.md).

---

## 1. The Master Skill: Ask "Compared to What?"

Almost every misleading statistic survives only because the reader forgets to ask
for a baseline. "Eating X **doubles** your risk" is meaningless until you know the
*original* risk. Doubling a 1-in-a-million risk is nothing; doubling a 1-in-10
risk is enormous.

- **Relative risk:** "doubles," "50% more likely" — a *ratio*.
- **Absolute risk:** "from 2 in 1,000 to 4 in 1,000" — the actual *numbers*.

Headlines love relative risk because it sounds dramatic. Always convert to
absolute terms before you react.

> Worked example. A drug "cuts heart-attack risk by 50%." Sounds huge. The real
> numbers: from 2% down to 1% over ten years. That's a 1-percentage-point absolute
> change — real, but far less dramatic than "50%." Same fact, two emotional
> impacts.

---

## 2. Base Rates — The Most Ignored Number

The **base rate** is how common something is *before* you consider any specific
evidence. Humans systematically ignore it, leading to confident, wrong conclusions.

The classic trap is the **accurate test for a rare condition**:

> A disease affects 1 in 1,000 people. A test is 99% accurate. You test positive.
> What's the chance you actually have it?

Intuition says ~99%. The truth is about **9%.** Why? Out of 10,000 people:

```
   10 actually have it      → ~10 test positive   (true positives)
   9,990 are healthy        → ~100 test positive  (1% false-positive rate)
   ─────────────────────────────────────────────
   ~110 positives total, only 10 real → 10/110 ≈ 9%
```

Because the condition is *rare*, the false positives from the huge healthy
majority swamp the true positives. This is **Bayes' theorem** in action: new
evidence updates a prior, it doesn't replace it. Whenever you hear a scary test
result or a profiling claim, ask: *how common is this in the first place?*

---

## 3. Averages Lie — Look at the Distribution

An average compresses a whole population into one number, and that compression
often hides everything that matters.

- **A room of 9 people earning \$40k and 1 earning \$10M** has an *average* income
  over \$1M — describing no one in it.
- The **median** (the middle value) is far more honest for skewed data like income,
  house prices, and wealth.

```
   "Average income $1M"  ← dragged up by one outlier
   actual people:  • • • • • • • • •            ●
                   $40k earners            the $10M earner
   median: $40k  ← the truthful summary
```

Always ask three things about any average:

1. **Mean or median?** (Skewed data → trust the median.)
2. **How spread out is it?** (The variance/range matters as much as the center.)
3. **Is it bimodal?** (Two clusters averaged together describe neither — e.g.,
   "average" exam scores hiding a class that splits into pass/fail.)

---

## 4. Correlation Is Not Causation

When two things move together (**correlation**), it does *not* mean one causes the
other. There are four possibilities for any correlation between A and B:

| Possibility | Example |
|---|---|
| A causes B | Smoking → cancer |
| B causes A | "Sick people take medicine" looks like "medicine → sickness" |
| A third thing causes both (**confounder**) | Ice-cream sales & drownings (cause: summer heat) |
| Pure coincidence | Spurious correlations across random data |

The ice-cream/drowning case is the canonical **confounder**: hot weather drives
*both*. Mistaking the correlation for causation would have you banning ice cream
to save swimmers.

How causation actually gets established:

- **Randomized controlled trials (RCTs):** randomly assign people to treatment vs.
  control. Randomization balances out confounders, isolating the real effect.
  This is why RCTs are the gold standard.
- **Observational studies** can only *suggest* causation; they're vulnerable to
  confounders no matter how large the dataset.

> Rule of thumb: when you read "linked to," "associated with," or "correlated,"
> mentally append: *"…which may or may not mean it causes anything."*

---

## 5. Sampling and Bias — Who's Actually Being Measured?

A statistic is only as good as the sample it came from. The most common failures:

- **Selection bias:** the sample isn't representative. An online poll captures
  people who visit that site and choose to answer — not the population.
- **Survivorship bias:** you only see the survivors. "Successful founders dropped
  out of college" ignores the vastly larger number of dropouts who failed. WWII
  engineers nearly armored the wrong parts of planes by studying only the bombers
  that *returned* — the bullet holes were on the *survivable* spots.
- **Response bias:** how you ask changes the answer. "Do you support *job-killing*
  regulation?" and "Do you support *life-saving* regulation?" poll the same policy
  differently.
- **Small samples:** tiny samples swing wildly by chance. "3 of 4 dentists
  recommend" is noise, not evidence.

```
   Survivorship bias:
   planes that came back  →  bullet holes here  →  "armor here!"  ✗
   planes that didn't     →  (invisible)        →  hit elsewhere, fatal  ✓
```

The question to always ask: **"Who is missing from this data?"**

---

## 6. p-values and "Statistical Significance" — Demystified

A **p-value** answers a narrow question: *if there were truly no effect, how likely
is a result at least this extreme, just by chance?* A small p-value (commonly
< 0.05) means "this would be surprising under pure chance."

What it does **not** mean — and these errors are everywhere:

| Misreading | Truth |
|---|---|
| "p = 0.05 → 95% chance the effect is real" | No. It's about data *given* no effect, not effect given data. |
| "Significant → important/large" | No. With huge samples, trivial effects become "significant." |
| "Not significant → no effect" | No. Could just be too little data to detect it. |

Two deeper traps:

- **p-hacking:** test 20 things, one comes back "significant" by chance alone, and
  *only that one* gets published. Always ask how many things were tested.
- **Significance ≠ size.** A statistically significant weight-loss pill that drops
  half a pound is real and useless. Look for the **effect size**, not just the
  p-value.

---

## 7. Reading Charts Critically

Charts are where honest data goes to be quietly distorted. Watch for:

1. **Truncated y-axis.** Starting the axis at 90 instead of 0 turns a tiny change
   into a cliff.

   ```
   axis from 0:        axis from 90:
   │ ▁▁▂▂              │      ╱▔  "explosive growth!"
   │ ▁▁▂▂              │   ╱▔
   └──────             └──────
   (same data, very different feeling)
   ```

2. **Cherry-picked range.** Showing 2021–2023 to imply a trend that reverses if
   you zoom out to 2010.
3. **Misleading area/3-D.** Doubling both width and height of an icon *quadruples*
   the visual area for a 2× value.
4. **Unlabeled or dual axes** rigged to make two lines appear to track.
5. **Correlation dressed as causation** with a suggestive overlay.

Defense: read the **axes and units first**, ask what range was chosen and why, and
distrust any chart with no zero baseline or no labels.

---

## 8. A Practical Checklist for Any Statistic

When a number tries to move you, run it through these:

1. **Compared to what?** (Absolute vs. relative; is there a baseline?)
2. **What's the base rate?** (Rare things make accurate tests misleading.)
3. **Mean or median — and how spread out?**
4. **Correlation or causation?** (Was it an RCT or just observed?)
5. **Who's in the sample — and who's missing?**
6. **How big is the effect, not just is it 'significant'?**
7. **What does the chart's axis and range hide?**
8. **Who benefits from me believing this?**

Internalizing even half of these puts you ahead of most journalists, marketers,
and pundits who deploy statistics at you daily.

---

## Sources & further study

- Darrell Huff, *How to Lie with Statistics* — the timeless short classic.
- Tim Harford, *The Data Detective* (a.k.a. *How to Make the World Add Up*).
- Charles Wheelan, *Naked Statistics* — friendly, intuition-first.
- Daniel Kahneman, *Thinking, Fast and Slow* — base-rate neglect and intuition.
- Nate Silver, *The Signal and the Noise* — prediction, probability, humility.
- Gerd Gigerenzer, *Calculated Risks* — risk literacy and natural frequencies.

> Framing note: Statistics is not about computing the right number; it's about
> refusing to be fooled by the wrong one. The goal is not certainty — data rarely
> offers it — but calibrated doubt: knowing *how much* a number is worth, and
> exactly which question it has not answered.
