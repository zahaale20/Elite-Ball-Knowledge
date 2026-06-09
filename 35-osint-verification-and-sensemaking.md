# OSINT, Verification & Sensemaking — Turning Noisy Public Information into Disciplined Judgment

> **Why this exists.** Open-source intelligence (OSINT) is the practice of producing
> reliable understanding from publicly available information. In a world where the
> information environment is noisy (module 31), algorithmically filtered (module 32),
> cognitively distorting (module 33), and sometimes deliberately manipulated (module
> 34), the analyst's core skill is **disciplined verification and sensemaking**. This
> module covers source validation, corroboration, basic media forensics logic,
> confidence scoring, and — most importantly — how analysts avoid deceiving
> themselves. It is lawful, ethical, public-information tradecraft.

Part of the `31–36` band. It is the practical payoff of the prior four modules and
shares its reasoning backbone with
[29-autonomy-planning-decision.md](29-autonomy-planning-decision.md) (estimation under
uncertainty) and [33-cognitive-bias-attention-and-narratives.md](33-cognitive-bias-attention-and-narratives.md)
(bias defense).

---

## 1. What OSINT is — and what it isn't

- **Is:** systematically collecting, verifying, and analyzing *publicly available*
  information (news, public records, public social posts, maps, imagery, public
  filings) to answer a question with stated confidence.
- **Isn't:** hacking, accessing private accounts, social engineering, impersonation,
  or circumventing access controls. Those are out of scope and, in many cases,
  illegal. Keep strictly to lawful, public sources and respect platform terms and
  privacy.

The discipline is less about *finding* information (there is too much) and more about
**verifying** it and **honestly bounding your confidence**.

---

## 2. The intelligence cycle (a reusable workflow)

A classic, vendor-neutral loop that structures any analysis:

1. **Direction.** Define the precise question and why it matters. Vague questions
   produce vague, bias-prone answers.
2. **Collection.** Gather from multiple *independent* sources with different
   incentives.
3. **Processing.** Translate, deduplicate, timestamp, and organize raw material.
4. **Analysis.** Weigh evidence, test hypotheses, and form a calibrated judgment.
5. **Dissemination.** Communicate the judgment *with its confidence and assumptions*.
6. **Feedback.** Update as new evidence arrives; record what you got wrong.

The loop mirrors the autonomy `sense → estimate → decide` loop — analysis is just
estimation over human-sourced data.

---

## 3. Source validation

Before trusting a source, characterize it:

- **Primary vs secondary.** Did this source directly witness/produce the
  information, or are they relaying someone else? Trace to the primary whenever
  possible.
- **Provenance.** Where did this originate? Beware source laundering (module 34),
  where a claim's origin is deliberately obscured.
- **Incentive.** What does the source gain if you believe them? (Module 31's "follow
  the incentives.")
- **Track record.** Has this source been reliable and self-correcting in the past?
- **Access and expertise.** Was the source actually positioned to know what they
  claim?
- **Recency and context.** Is the information current, and is it being presented in
  its original context (vs malinformation — true-but-decontextualized, module 34)?

---

## 4. Corroboration — the core defense

A single source is a hypothesis, not a fact. Confidence comes from **independent**
corroboration.

- **Independence is the key word.** Ten outlets repeating one wire report is one
  source, not ten (illusory truth, module 33). Ask whether corroborating sources
  share an origin or incentive.
- **Triangulate across types.** Combine textual, visual, geospatial, and
  documentary evidence — different evidence types fail in different ways.
- **Seek disconfirmation.** Actively look for evidence that the claim is false. If
  you only find confirming evidence, suspect confirmation bias, not truth.
- **Weight by independence and access**, not by volume or emotional intensity.

---

## 5. Media forensics logic (concepts, not a toolkit)

The point is the *reasoning*, which survives changes in specific tools:

- **Reverse image/video search.** Has this media appeared before? Recycled media
  from old or unrelated events is the most common form of visual misinformation.
- **Geolocation.** Cross-reference visible features (terrain, signage, architecture,
  sun position/shadows, road layouts) against maps and satellite imagery to confirm
  *where* something was recorded.
- **Chronolocation.** Use shadows, weather records, foliage, and other time-linked
  cues to confirm *when*.
- **Internal consistency.** Check for physical implausibilities, mismatched
  lighting/reflections, and inconsistent metadata.
- **Synthetic-media awareness.** Treat audio/video as potentially generated; rising
  generative capability means **absence of obvious artifacts is not proof of
  authenticity**. Lean on provenance and corroboration rather than artifact-spotting
  alone, and be aware of the *liar's dividend* (module 31) cutting the other way.

This is detective reasoning: build a chain of physical, cross-referenced evidence for
*where, when, and what*.

---

## 6. Analysis of Competing Hypotheses (ACH)

A structured technique (Heuer) that directly counters confirmation bias:

1. Enumerate *all* plausible hypotheses up front, including uncomfortable ones.
2. List the evidence and arguments.
3. For each piece of evidence, ask which hypotheses it is **inconsistent** with —
   focus on *disconfirmation*, not confirmation.
4. The strongest hypothesis is the one with the least *disconfirming* evidence, not
   the most confirming.
5. Identify which few pieces of evidence are doing the most work, and how sensitive
   your conclusion is to them.
6. Report conclusions with the evidence that would change them.

ACH externalizes reasoning so it can be checked — the antidote to System 1
shortcuts (module 33).

---

## 7. Confidence scoring and calibrated language

Vague language hides sloppy thinking. Discipline your output:

- **Probabilities or bands.** Prefer "~70% likely" or a defined confidence band over
  "probably." State the number and what would move it.
- **Standardized terms.** If using words, map them to ranges consistently (e.g.,
  "likely" = a defined probability band) so readers interpret them the same way.
- **Separate confidence in the *source* from confidence in the *judgment*.** You can
  have a reliable source about an uncertain situation, or a shaky source about a
  well-corroborated fact.
- **Distinguish evidence from inference.** "The imagery shows X" (observation) vs "X
  implies Y" (inference). Label which is which.
- **Track calibration over time.** Record predictions and outcomes; good
  forecasters measure and improve their calibration (Tetlock, *Superforecasting*).

This is identical in spirit to reporting an estimator's covariance, not just its mean
— see [29-autonomy-planning-decision.md](29-autonomy-planning-decision.md).

---

## 8. How analysts avoid self-deception

The hardest adversary is your own cognition (module 33). Concrete guards:

- **State your prior and your question before collecting**, so you can see if you
  drifted toward a convenient answer.
- **Keep a disconfirmation log** — evidence against your leading hypothesis.
- **Use a devil's advocate or red team** for important judgments.
- **Beware desire and fear.** Note when you *want* a conclusion to be true (or dread
  it); that is exactly when to add scrutiny.
- **Time-box and avoid premature closure.** The pull to resolve uncertainty quickly
  is strong; resist it on high-stakes questions.
- **Separate collection from judgment.** Gather broadly before you start scoring, so
  early hypotheses don't filter your collection.
- **Document assumptions explicitly**, so they can be challenged and revisited.

---

## 9. Ethics and legality (non-negotiable)

- Use only **lawful, publicly available** sources. No intrusion, no impersonation, no
  circumventing access controls.
- Respect **privacy** and platform terms; avoid doxxing and harassment. Minimize
  collection of personal data not relevant to the question.
- Be transparent about **uncertainty**; never launder a guess as a fact.
- Consider **harm**: how could your published analysis be misused, and does that
  change what or how you publish?
- Maintain a clear **audit trail** so your work can be reviewed and reproduced.

Ethical discipline is not a constraint on good OSINT — it *is* good OSINT. Sloppy or
intrusive methods produce both legal risk and worse analysis.

---

## 10. Relevance to defense-tech and autonomy

- **Public information as a sensor.** OSINT feeds situational awareness, but like any
  sensor it has noise, bias, and adversarial spoofing (module 34) — fuse it with the
  same skepticism you'd apply to a degraded GPS signal
  ([26-autonomy-gnss-jamming-spoofing.md](26-autonomy-gnss-jamming-spoofing.md)).
- **Verification at machine scale.** The same logic informs automated
  content-verification and trust-scoring systems.
- **Operator sensemaking.** Interfaces should present *calibrated confidence*, not
  just raw feeds, so operators trust appropriately (module 33).
- **Estimation parallel.** Sensemaking under uncertainty is the human analog of state
  estimation; the rigor transfers both directions
  ([28-autonomy-gnc.md](28-autonomy-gnc.md)).

---

## Sources & further study

- Richards Heuer — *Psychology of Intelligence Analysis* (free) and the ACH method.
- Bellingcat — *Online Investigations Toolkit* and published, ethical OSINT
  casework (geolocation, chronolocation, verification).
- Michael Bazzell — *Open Source Intelligence Techniques* (methods reference).
- Philip Tetlock & Dan Gardner — *Superforecasting* (calibration).
- First Draft / verification handbooks — practical media verification workflows.

> Framing note: this module teaches lawful, ethical, public-source verification and
> disciplined judgment. The objective is accurate understanding with honest
> confidence — and explicit respect for legality and privacy.
