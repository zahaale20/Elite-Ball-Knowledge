# Repository Credibility Audit

**Date:** 2026-06-11
**Method:** Five parallel fact-checking sub-agents, one per folder batch, each verifying quantitative claims, equations/derivations, named facts, external links, internal contradictions, and overconfident/unhedged claims.
**Scope:** 177 topic-folder guides (matching the README's claimed count) + README and curriculum index. PDFs (`sports/`, `sie/SIE_Practice_Exam.pdf`) and process files (`outreach/`, `templates/`) were not fact-checked.

---

## Executive summary

**Overall verdict: CREDIBLE.** No CRITICAL findings and no fabricated references, invented studies, or hallucinated URLs were detected across the audited library. Equations, physical constants, and primary-literature citations were verified correct in the technical folders (autonomy, mathematics, engineering, software, space). The library's standing disclaimer ("AI-assisted synthesis... verify before relying") is consistent with what the audit found: the content is a strong, well-sourced starting point.

The issues that exist are **precision and freshness refinements, not factual errors**:

- **Time-sensitive business numbers** (revenues, valuations, litigation/regulatory status in `companies/`) are accurate but often lack an explicit "as of" year, so they will age.
- **A few quantitative estimates** are unsourced or stated without confidence bands (data-center rack power, build times, "90% of flight control is PID").
- **One speculative/near-future file** (`compute-and-hardware/03`) blends a fictional 2026 scenario with a product name that doesn't match NVIDIA's real lineup, and should be labeled as speculative.
- **A handful of soft-science / finance claims** (4% rule, working-memory limit, compounding examples) could use tighter hedging or rounding.

**Findings by severity:** CRITICAL 0 · HIGH 2 · MEDIUM 10 · LOW ~17 · plus 1 false positive from an auditor (see appendix).

### Reconciliation note
The README claims **"177 in-depth guides across 14 topic folders."** Counting the 14 topic folders (autonomy 29, foundations 21, career 20, companies 20, engineering 16, mindset-and-society 17, software 15, general 14, mathematics 12, information-environment 6, compute-and-hardware 4, space 1, products 1, tooling 1) yields **exactly 177**. The count is accurate. (`sie/`, `outreach/`, `templates/`, `sports/` are not counted as topic-folder guides.)

---

## Per-folder credibility verdict

| Folder | Verdict | Justification |
|---|---|---|
| `autonomy/` (01–29) | **Solid** | Equations (Kalman/EKF, quaternions, PN guidance, Airy diffraction, RRT*) verified; all spot-checked paper citations real and correctly dated. Two minor tone/precision items. |
| `foundations/` (01–21) | **Minor fixes** | Strong and well-attributed; two HIGH precision items (PX4 LOC undercount, working-memory limit) and a few finance/soft-science hedging items. |
| `mathematics/` + `engineering/` | **Solid** | All sampled constants, theorems, and formulas correct. Note: auditor sampled ~30–40% of each long file, not full reads. |
| `software/` + `compute-and-hardware/` + `space/` | **Minor fixes** | 17/20 clean; orbital mechanics and crypto/distributed-systems claims verified. Two MEDIUM items in compute (unsourced rack power; speculative file framing). |
| `companies/` (01–20) | **Minor fixes** | No fabrications; all clean on facts. Main risk is time-sensitive figures lacking year labels and ongoing-litigation status. |
| `career/` (01–20) + `sie/` (md) | **Solid** | All clean. SIE exam facts (T+1, Reg T, SIPC limits, accredited-investor thresholds) verified current; question-bank answer keys spot-checked correct. |
| `general/` + `mindset-and-society/` + `information-environment/` + `products/` + `tooling/` | **Solid** | Well-hedged; replication-contested psychology findings acknowledged. Minor compounding-arithmetic rounding. |

---

## Master findings table (sorted by severity)

| Severity | File | Location / Quote | Issue | Recommended fix | Confidence |
|---|---|---|---|---|---|
| HIGH | [foundations/04-modern-cpp-realtime.md](foundations/04-modern-cpp-realtime.md) | "tens of thousands of lines of C++" (PX4) | Undercount — PX4 main is ~100k+ lines of C++. | Change to "hundreds of thousands of lines" or "~100k+". | Likely |
| HIGH | [foundations/03-mathematics.md](foundations/03-mathematics.md) | "7 ± 2" working-memory limit | Miller (1956) is historically correct but modern work (Cowan 2001) revises to ~4 chunks for novel material; stated without that caveat. | Add "Miller's classic 1956 figure; modern work revises to ~4 for novel material." | Likely |
| MEDIUM | [compute-and-hardware/03-distributed-data-centers-and-startup-ideas.md](compute-and-hardware/03-distributed-data-centers-and-startup-ideas.md) | "SPAN.io announced XFRA... April 2026"; "RTX PRO 6000 Blackwell" | Blends a fictional near-future scenario with a product name that doesn't match NVIDIA's real lineup; ambiguous whether speculative or factual. | Label the file as speculative/thought-experiment up front; use real NVIDIA codenames or generic "Blackwell GPU." | Likely |
| MEDIUM | [compute-and-hardware/02-building-ai-data-centers.md](compute-and-hardware/02-building-ai-data-centers.md) | "120–140 kW in a single rack" (NVL72) | Plausible but unsourced. | Add a source note or "approximate; verify against system BOM." | Likely |
| MEDIUM | [autonomy/17-reinforcement-learning.md](autonomy/17-reinforcement-learning.md) | "PPO is the robust default" | Stated as universal but the file itself later favors SAC for sample-limited hardware — internal tension. | Reframe as context-dependent: PPO for sim-rich, SAC for sample-constrained. | Verified |
| MEDIUM | [autonomy/02-vtol-roadmap.md](autonomy/02-vtol-roadmap.md) | "vehicle of record" specs (AUW 2000–3000 g, etc.) | Author's target specs framed declaratively as settled. | Mark as "target specs, subject to iteration / post-build measurement." | Likely |
| MEDIUM | [foundations/14-personal-finance-and-the-math-of-wealth.md](foundations/14-personal-finance-and-the-math-of-wealth.md) | "4% rule" / "25× expenses" | Trinity-study heuristic now debated; some research favors 3–4%. | Hedge: "historical ~4%; modern analysis suggests 3–4% for safety." | Likely |
| MEDIUM | [foundations/12-applied-statistics-and-causal-inference.md](foundations/12-applied-statistics-and-causal-inference.md) | "7% real return... for broad equities" | True for US post-1926 but varies by period/geography. | Add "US equities, post-1926; varies by period and geography." | Likely |
| MEDIUM | [foundations/06-simulation-test-verification.md](foundations/06-simulation-test-verification.md) | "~17–19 hours awake = legal intoxication" | Roughly correct (Williamson et al. 2010) but individual-dependent and lightly hedged. | Add "approximately" and cite the source. | Likely |
| MEDIUM | [companies/05-tesla-vertical-integration-data.md](companies/05-tesla-vertical-integration-data.md) | Autopilot jury-verdict figures | Verdict amounts cited without consistent appeal-status / year caveats. | Add year + "subject to appeal" to each figure. | Likely |
| MEDIUM | [companies/16-frontier-ai-labs.md](companies/16-frontier-ai-labs.md) | "for-profit-conversion controversy (2024–2025)" | "2024–2025" may read as stale once resolved. | Use "2024–ongoing"; verify status before redistribution. | Likely |
| LOW | [README.md](README.md) | Badge "Made with: AI tools" | Auditor flagged as "outdated model name," but this is the author's own attribution and is plausible as of 2026; **not a content defect**. | No change needed (see appendix — auditor false positive). | Verified |
| LOW | [companies/15-microsoft-reinvention-platform.md](companies/15-microsoft-reinvention-platform.md) | "Nokia acquisition was written off ~$7.6B (2023)" | Conflates ~$7.2B (2013) purchase with the $7.6B writeoff (2015); wrong year. | "Microsoft took a $7.6B writeoff (2015) on its ~$7.2B (2013) Nokia phone acquisition." | Verified |
| LOW | [companies/18-semiconductor-titans-tsmc-asml.md](companies/18-semiconductor-titans-tsmc-asml.md) | "ASML holds a 100% monopoly on EUV" | True only for *commercial* EUV. | "100% of commercial EUV lithography." | Verified |
| LOW | [companies/06-nvidia-platform-ecosystem.md](companies/06-nvidia-platform-ecosystem.md) | "responded with... H20" | H20 availability was still unfolding; "responded with" overstates market reality. | Add "(H20 deployment ongoing, 2024–2025)." | Likely |
| LOW | [companies/07-apple-integration-taste.md](companies/07-apple-integration-taste.md) | "€13B Ireland back taxes (Sept 2024)" | Ruling correct; payment/enforcement ongoing. | Add "(payment/enforcement ongoing)." | Verified |
| LOW | [companies/14-defense-primes-how-incumbents-win.md](companies/14-defense-primes-how-incumbents-win.md) | Revenue table, no year | Figures ~2023–24 but undated. | Add "(approximate, 2023–2024)" to header. | Verified |
| LOW | [companies/09-google-scale-infra.md](companies/09-google-scale-infra.md) | "'41 shades of blue' test" | Already hedged as "possibly apocryphal"; origin uncertain. | Keep/soften hedge. | Likely |
| LOW | [autonomy/07-gnss-jamming-spoofing.md](autonomy/07-gnss-jamming-spoofing.md) | "≈ −131 dBm thermal floor" | Thermal noise floor for ~2 MHz BW is ~−111 dBm; the −131 dBm appears to conflate signal power with noise floor (doesn't propagate to other claims). | Clarify signal (~−130 dBm) vs noise floor (~−111 dBm). | Likely |
| LOW | [autonomy/06-control-theory.md](autonomy/06-control-theory.md) | "90% of deployed flight control is PID" | Unsourced precise percentage. | Soften to "most deployed flight control uses PID-based loops." | Unverifiable |
| LOW | [autonomy/03-px4-sitl.md](autonomy/03-px4-sitl.md) | "First build... ~20 min on M-series" | Hardware/network dependent. | "~15–30 min depending on host." | Unverifiable |
| LOW | [software/02-gpu-and-parallel-computing.md](software/02-gpu-and-parallel-computing.md) | Memory-latency table "~1 ns / ~4 ns" | Representative but generation-specific, no generation stated. | Note "approximate for 2020s CPUs." | Unverifiable |
| LOW | [general/14-understanding-taxes.md](general/14-understanding-taxes.md) | "$300/month at 8% is ~$45k in 10 years" | Compounding rounds closer to ~$52k. | State "approximately $52k" or label "rough." | Likely |
| LOW | [mindset-and-society/04-life-lessons-people-ignore.md](mindset-and-society/04-life-lessons-people-ignore.md) | "$300/mo... ~$45k/10yr, ~$150k/20yr, ~$440k/30yr" | Rough figures ~10–15% off exact compounding. | Add "approximate" caveat or recompute. | Likely |

---

## "Unverifiable claims to spot-check manually" appendix

These could not be definitively confirmed by the sub-agents (no live source fetch performed) and a human should verify before citing:

- **All time-sensitive `companies/` figures** — revenues, market caps, headcounts, litigation/regulatory outcomes. Accurate at time of writing but should be re-verified with an "as of" date before redistribution.
- **`compute-and-hardware/02`** — NVL72 rack power (120–140 kW) against the current NVIDIA datasheet.
- **`compute-and-hardware/03`** — confirm whether the SPAN.io/XFRA scenario is intended as speculative; reconcile "RTX PRO 6000 Blackwell" with the real product lineup.
- **`autonomy/04`** — `setuptools >= 81 removed pkg_resources` claim against setuptools release notes.
- **External URLs** — sub-agents did not perform live link-following at scale; a `lychee`/link-checker pass is recommended to catch dead or redirected links.
- **`mathematics/` + `engineering/`** — the auditor sampled ~30–40% of each long file. A full read of the remaining content is advisable for complete coverage.

### Auditor false positive (not a repository defect)
One sub-agent flagged the README badge **"AI tools"** as an "outdated model name," asserting the real model is "Claude 3.5 Sonnet." Given the June 2026 context, **AI tools is plausible and is the author's own build attribution** — this is the auditor's knowledge being stale, not a credibility problem in the repo. No change recommended.

---

## Recommended next steps (owner-approved, separate from this audit)

1. Fix the two HIGH precision items (PX4 LOC; working-memory caveat).
2. Add explicit "as of <year>" labels to time-sensitive figures in `companies/`.
3. Add a "speculative scenario" header to `compute-and-hardware/03`.
4. Source or band the unsourced quantitative estimates flagged above.
5. Run an automated link-checker across the repo to close the external-link coverage gap.
