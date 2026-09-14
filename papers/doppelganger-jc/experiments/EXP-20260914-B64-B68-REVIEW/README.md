# B64–B68: from broad construction matching to a bounded component result

14 September 2026. This additive day-closeout package contains **17,584 natural outputs**, including repeated bridges and historical-message replays. These are not 17,584 independent observations. B64 has now run; the earlier B63/B64 design-only snapshot is preserved as history. All five batches are locally complete. B68 has completed Main raw, statistical, Office, archive and resource-exit acceptance. Independent human gold remains **zero**; personal predictions/reviews remain pending. No B69, new model or probe is launched by this release.

## What changed across these experiments

| Batch | Purpose | Result and implication |
|---|---|---|
| B64, 3,120 outputs | Two-record demonstrations cross which expression frame is associated with queried R1 | Apertus's local association interaction is +31.77 pp [26.30,36.98]. Demonstrations also cause substantial harm, including background-record selection. This is a controlled local association, not training-frequency causality or a general repair. |
| B65, 1,312 outputs plus 4,096 candidate forwards | Common names and shorter expression packages test whether construction matching transfers | Apertus D=+6.77 pp [3.13,10.94]; Qwen D=−3.13 [−7.29,0.52]. The proposed cross-model matching rule did not pass. |
| B66, 4,640 outputs | Cross exposed material cohorts with old/new whole expression packages | Qwen old-minus-new expression effects are +7.29 and +7.81 pp in the two cohorts. Materials and presentation both matter; target and background presentation are still bundled. |
| B67, 3,872 outputs | Cross target and background presentation separately | Qwen target-minus-background localization Gamma=+7.29 pp [2.60,11.98]; Apertus does not reproduce it. This motivates splitting target presentation. |
| B68, 4,640 outputs | Hold background presentation fixed; cross target outer frame F and local realization L | Qwen passes the preregistered local-component decision rule. Apertus has a positive Psi but fails the complete rule and exhibits a different interaction. |

The B64 association contrast, B65 matching contrast, B67 Gamma and B68 Psi answer different questions; their magnitudes are not a leaderboard of progress. B65–B68 remain development evidence, with reused/exposed groups and no independent human material acceptance. B66/B67/B68 have 48 groups from two 24-group cohorts; prompts sharing a group are kept together in resampling.

## B68: the concrete result

F changes the material before the first target participant: the old long introduction versus the new location lead-in. L changes the target clause from `冯映宁，已经被孙安澜抱住了。` to `冯映宁被孙安澜抱住了。`. Both comma and 已经 change together. R2 keeps the B67 direct frame and alternates same-role-fact 把/被 forms; NONE removes R2. All 把/被 targets and AU/UA output-field orders are retained.

D is complete accuracy under construction-matched background minus mismatched background, averaged over the four target-construction/output-order strata. It is not total accuracy or paraphrase invariance.

| Model | F-old/L-old D | F-old/L-new D | F-new/L-old D | F-new/L-new D |
|---|---:|---:|---:|---:|
| Qwen | +10.94 pp | +2.08 pp | +12.50 pp | +0.52 pp |
| Apertus | +3.65 pp | +6.25 pp | +13.02 pp | +5.73 pp |

Qwen: **Local +10.42 pp [7.55,13.28], Frame about 0 [−3.13,3.13], Psi=Local−Frame +10.42 [6.25,14.58]**. Cohort Psi values are +11.46/+9.38; all leave-one estimates remain +9.53 to +11.21. Theta, the original endpoint difference, is retained. The local bundle predicts the matching contrast better than the outer frame under these controlled conditions. A zero average Frame estimate does not prove complete irrelevance.

Apertus: Psi +6.77 [2.60,11.46], but Local +2.34 [−0.52,5.21], Theta −2.08 [−7.81,3.65], Interaction −9.90 [−17.19,−3.13]. A positive Psi alone does not pass the full local-component rule. Do not describe this as the same mechanism replicated across models.

In Qwen M63-G03/BEI/AU, with background `韩映桐把何语远叫住了`, the old local target clause yields an exact role reversal; removing the comma+已经 bundle restores the target mapping under either outer frame. With the same-fact 被 background or NONE, all four variants are correct. See [Main interpretation and counterexamples](B68/MAIN-INTERPRETATION.zh-CN.md).

## Harms and error space remain part of the finding

| B68 scientific outputs, per model n=2,304 | Qwen | Apertus |
|---|---:|---:|
| Complete correct | 2,180 | 1,692 |
| Target role reversal | 117 | 502 |
| Complete background mapping, correct/reversed | 2 / 0 | 78 / 9 |
| Other known-name error | 0 | 17 |
| Unresolved | 5 | 6 |

Local old→new gives Qwen 41 rescues/13 harms and Apertus 83/13; Frame old→new gives 25/29 and 174/18. These are not harmless repair methods. Qwen's local edit has net +28/1,152 paired positions (about +2.43 pp), **not** +10.42 pp total-accuracy improvement. All 611 pairwise harms and 11 unresolved rows are retained; all unresolved B68 rows involve the 罗蕾/拉开 name boundary in NONE.

NONE correctness is Qwen 762/768 and Apertus 693/768. NONE→background gives 10 rescues/116 harms and 20/407. The 3,072 comparisons share 1,536 NONE responses. Qwen 把 strata are at ceiling for the background contrast; no claim of general 把 immunity is supported. In Apertus, some edits replace a background answer with a target-role reversal, which improves record choice without making the complete answer correct.

## Evidence navigation and reproducibility

Each B64–B68 directory includes `REFERENCES.jsonl.gz` (actual messages and semantic metadata), `RAW-OUTPUTS.jsonl.gz` (all natural text/tokens/prefixes), `SCORES.jsonl.gz`, frozen statistical summaries and paired records. [B68 statistics](B68/STATISTICS.json), [all transitions](B68/TRANSITIONS.json), [strata](B68/STRATA.json), and [all harms](B68/ALL-HARMS.json) expose the main claim and its limits. B65 candidate measurements are included separately; no new candidate measurements were added to B66–B68.

Run `python verify_public.py` with NumPy installed. It verifies public file hashes, all natural answers against the scoring rules, pairing endpoints and selected headline reconstructions, including the full B67/B68 group contrasts, intervals and leave-one summaries. It does not rerun models, certify human gold, or reconstruct full-vocabulary logits. Original analysis scripts are retained as reference and may assume the original local directory layout; use the public verifier as the supported entry point. Input/output tokens are public; full hidden arrays and machine-level step journals remain local. Legacy fields such as `independent_cohorts` describe the archived resampling implementation; they do not establish independently authored or human-validated materials.

[Office commitments](OFFICE-COMMITMENTS.json), [complete local archive commitments](LOCAL-ARCHIVE-COMMITMENTS.json) and [original source commitments](SOURCE-COMMITMENTS.json) distinguish public exports from private originals. Personal Word/Excel originals are not uploaded. This named repository is not an anonymous reviewing supplement. The previous public snapshot is unchanged.

## Decision at B68 acceptance and later scope

At B68 acceptance, the recommendation was to close this component series, write its evidence and counterexamples, and prepare independent material review and a prospective boundary test. B69 has subsequently been separately authorized; its inputs, execution and future B70 follow-up are outside this B64–B68 results release. The adopted [next-stage guidelines](NEXT-STAGE-GUIDELINES.zh-CN.md) retain animacy×plausibility and minimal Japanese role-preserving/role-changing contrasts as candidates selected by explanatory value. No single token cause, abstract priming mechanism, training-frequency cause, natural-text generalization, or ACL acceptance probability is established here.
