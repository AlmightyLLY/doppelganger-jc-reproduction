# B63–B70: conditional predictions, rescues, harms, and the limits of a repair account

15 September 2026. **B70 is complete and Main-audited.** This is the unified entry point for an independent Pro/Claude review. It adds all **9,280 B69/B70 natural outputs** and links the unchanged B63–B68 evidence. The eight batches contain 31,520 natural outputs in total, including repeated bridges and historical inputs; they are not 31,520 independent observations. B65 additionally used 4,096 candidate forwards. B69/B70 used none. Independent human gold remains **zero**. Personal predictions/reviews remain pending; mechanical and AI acceptance do not fill those fields.

## Start here

1. Read the trajectory below, then the [B69 interpretation](B69/MAIN-INTERPRETATION.zh-CN.md) and [B70 interpretation](B70/MAIN-INTERPRETATION.zh-CN.md), including counterexamples.
2. Inspect actual messages, raw answers and paired transitions in each batch. For B69/B70, run `python verify_public.py` with NumPy installed.
3. Read the [questions and decision boundaries](REVIEW-QUESTIONS.md). Ready-to-use prompts are provided for [Claude in English](CLAUDE-PROMPT.en.md) and [Pro in Chinese](PRO-PROMPT.zh-CN.md).

| Evidence | Immutable source |
|---|---|
| B63 results, plus the historical B64 design-only state | [B63/B64 snapshot at 8afafa6](https://github.com/AlmightyLLY/doppelganger-jc-reproduction/tree/8afafa6887285d4b15061b9f828dedbfc7b4b339/papers/doppelganger-jc/experiments/EXP-20260914-B63-B64-REVIEW) |
| Actual B64–B68 results | [B64–B68 snapshot at de1e916](https://github.com/AlmightyLLY/doppelganger-jc-reproduction/tree/de1e916c0fda3de125fc1a053787e0c5a6c42bcb/papers/doppelganger-jc/experiments/EXP-20260914-B64-B68-REVIEW) |
| B69 new events within the template family | [B69 files](B69), [design](B69/MAIN-DESIGN.zh-CN.md), [statistics](B69/STATISTICS.json), [transitions](B69/TRANSITIONS.json) |
| B70 comma × 已经 component crossing | [B70 files](B70), [design](B70/MAIN-DESIGN.zh-CN.md), [statistics](B70/STATISTICS.json), [transitions](B70/TRANSITIONS.json) |

The older B63 README correctly says B64 had not run **at that snapshot**. Its future-state wording is superseded by the actual B64 results linked above. Do not use the repository default branch as a substitute for these evidence snapshots.

## How the question narrowed

| Batch | Question | Result and what it permits |
|---|---|---|
| B63 | Does a fixed example package transfer across two authored expression frames, and does frame matching affect record selection? | Qwen rescues the same 29 items under both example packages. Apertus's frame-match interaction is +11.46 pp [5.73,17.71], alongside harm. Correctness, invariance and joint correctness remain separate. |
| B64 | With both frames present, does their association with queried R1 in demonstrations matter? | Apertus's preregistered local association contrast is +31.77 pp [26.30,36.98]. Background-record errors also rise. This is local example association, not proof of a hidden selection module or training-frequency cause. |
| B65 | Does construction matching survive common names and shorter expression packages? | Apertus D=+6.77 pp [3.13,10.94], Qwen D=−3.13 [−7.29,0.52]. A common positive matching rule does not transfer. |
| B66 | Is that change attributable to materials or the whole expression package? | Crossing both exposed cohorts with both packages yields Qwen old-minus-new effects of +7.29/+7.81 pp. Target and background presentation remain bundled. |
| B67 | Which record's presentation contributes more? | Qwen target-minus-background localization Gamma=+7.29 pp [2.60,11.98]. Apertus does not reproduce that localization. |
| B68 | Does target outer framing or the local clause bundle matter more? | Qwen's local-component rule passes; Psi=+10.42 pp [6.25,14.58]. Apertus's positive Psi alone does not pass the complete rule. Comma and 已经 are still bundled. |
| B69 | Can the fixed local-bundle prediction survive new event bindings and both role directions? | Qwen Lambda=+6.25 pp [3.13,9.77] passes the complete prospective decision rule. Apertus +4.69 [1.17,8.20] falls below the 5 pp investment threshold. Both use shared templates and mostly reused predicates; this is limited transfer, not independent human-confirmed generalization. |
| B70 | Without the subject-following comma, does adding 已经 still change the background-matching contrast? | Qwen T=+0.39 pp [−1.17,1.95], wholly inside the prespecified ±2.5 pp practical-small band. Apertus's scope check T=+5.47 [1.95,8.99] passes its development rule. The simple cross-model single-component explanation is not supported. |

These contrasts answer different questions. Their magnitudes must not be ranked as a progress score.

## B69: prediction transfer is not harmless repair

Each model has 1,536 scientific outputs and 16 bridges. The sample structure is **16 predicate clusters × two new scenarios**, preserving AB/BA roles, 把/被 targets, AU/UA fields, two local renderings and BA/BEI/NONE backgrounds. Resampling retains every condition and both scenarios of a predicate together: 10,000 draws, seed 690914, with all leave-one results.

Qwen's Lambda is the difference between old- and new-clause **background matching contrasts**, not total-accuracy improvement. Old→new yields **14 rescues and 9 harms**, 723/768→728/768 correct: only +0.65 pp overall. In BEI/AU, BA-background correctness rises 31/64→41/64 while BEI-background correctness falls 53/64→48/64. This is an informative directional tradeoff, not an invariant repair. Apertus has 45 rescues/12 harms.

All Qwen scientific errors in B69 are target-role reversals, but Apertus also has eight other errors. Earlier batches include background selection errors. Do not claim that entities are always correct or both congruence-conflict strata always collapse. In particular, Qwen 把 targets are at ceiling in this series.

## B70: the component result

B70 reuses all 32 B69 scenarios and adds the two missing intermediate renderings. Per model: 3,072 scientific outputs plus 16 bridges. C means subject-following comma; A means 已经. The location-introducing comma is held fixed. D is accuracy with construction-matched background minus mismatched background, averaged over the four construction/field-order strata. Primary T=D01−D00 tests adding 已经 without the subject-following comma.

| Quantity, percentage points | Qwen | Apertus |
|---|---:|---:|
| D00 | 2.73 | 5.47 |
| D01 | 3.13 | 10.94 |
| D10 | 4.30 | 10.16 |
| D11 | 8.98 | 10.16 |
| Primary T, no-comma 已经 increment | **0.39 [−1.17,1.95]** | **5.47 [1.95,8.99]** |
| Secondary T1, increment with comma | 4.69 [1.56,7.81] | 0.00 [−3.91,3.91] |
| Secondary interaction J=T1−T | 4.30 [1.56,7.42] | −5.47 [−10.94,−0.39] |
| Secondary whole-bundle contrast D11−D00 | 6.25 [3.13,9.38] | 4.69 [1.17,8.20] |

All 17 prespecified quantities, 16-cluster bootstrap intervals (10,000 draws, seed 700915), direction/scenario strata and leave-one estimates are included. The secondary interaction does not replace Qwen's unsuccessful primary support test. Qwen's small-effect interval is more informative than merely calling its result nonsignificant, but does not prove exact zero. A significant result in one model and a nonsignificant result in another is not itself a formal model-difference test.

**Concrete Qwen case:** R2 is `在接待区，许明把吕宁扶起了。`; the correct R1 event is 蒋宁 pushing 李诚. The first three targets below yield the correct mapping. The fourth yields its exact reversal.

- `在排练厅，李诚被蒋宁推开了。`
- `在排练厅，李诚已经被蒋宁推开了。`
- `在排练厅，李诚，被蒋宁推开了。`
- `在排练厅，李诚，已经被蒋宁推开了。`

See V01-S1/DAB/BEI/AU/BA in the raw files. This illustrates why the original two-endpoint comparison could not identify comma or 已经 alone. It does not validate the naturalness of the marked comma construction.

**A larger D can accompany worse accuracy.** Apertus C0A0→C0A1 falls 643/768→618/768 correct while D rises. Its background-burden change relative to NONE is −4.30 pp [−7.62,−0.78]. Qwen goes 728/768→730/768. Positive T is not a method gain.

| B70 fixed pair direction | Qwen rescue / harm | Apertus rescue / harm |
|---|---:|---:|
| Mismatched→matched background, 1,024 pairs/model | 50 / 1 | 100 / 6 |
| Comma 0→1, 1,536 pairs/model | 25 / 13 | 25 / 44 |
| 已经 0→1, 1,536 pairs/model | 8 / 30 | 26 / 73 |
| Whole bundle 00→11, 768 pairs/model | 9 / 14 | 12 / 45 |
| NONE→background, 2,048 pairs/model | 0 / 141 | 9 / 377 |

Pair sets reuse outputs; counts cannot be summed as independent cases. B70 whole-bundle direction reverses B69 old→new. NONE comparisons share 1,024 NONE responses/model. Same-fact target changes and fixed-mention-order changes of actual role facts are also retained; the latter are not paraphrase repairs.

B70 scientific classifications: Qwen **2,928 correct, 144 reversals**; Apertus **2,503 correct, 552 reversals, 16 other errors and one correct background mapping**. Four-member complete correctness is 659/768 and 316/768. Aggregate U=0 hides three Apertus field-U/string-`null` cases: the other field is known-wrong, and the frozen scorer gives W precedence over U. All such cases are exposed separately.

## Verification, archival differences and limits

Main independently checked B70's 6,176 outputs and all 89,804 saved generation steps, decoded tokens, and reproduced the statistical analyses. All 32 bridges and 3,072 historical endpoints exactly reproduce B69 messages, prefixes, input/output tokens and text. This is evidence against an observed execution-drift explanation, not a new model run or a full-vocabulary-logit reconstruction.

The local B70 archive contains 172 files plus its manifest; all hashes passed. Its CURRENT-STATUS is a pre-send snapshot, with subsequent delivery receipts outside the sealed archive. At launch, the Main release and executor JSON copy differed only by a terminal newline; identical JSON content and the copy's correct runtime hash were documented. Neither difference altered scientific inputs or outputs.

`verify_public.py` verifies this new package's full hash manifest, all 9,280 exported answers, complete B69/B70 pair sets and G4 controls, group contrasts, intervals, leave-one results, strata and B70 historical matches. Existing B63–B68 snapshots have their own public verifiers. Full local step journals, host details and personal Office originals are not uploaded. [Office commitments](OFFICE-COMMITMENTS.json), [archive commitments](LOCAL-ARCHIVE-COMMITMENTS.json) and [source commitments](SOURCE-COMMITMENTS.json) distinguish public exports from private evidence. Original analysis scripts may assume local paths; public auditors are the supported entry points.

The remaining scientific limits are material naturalness, human validation, shared templates/predicates, model scope, output-interface dependence, and position/length/lexical effects. 已经 changes temporal/aspectual expression; preserving task-relevant participant relations does not hold all semantics or pragmatics fixed. No universal repair, hidden mechanism, human cue-hierarchy reversal, or January acceptance probability is established. This named public repository is not an anonymous ARR supplement.

**Decision now:** stop this component series, write the supported conditional claims and failures, and obtain independent material review before a bounded prospective boundary test. Animacy/plausibility and Japanese scrambling remain candidate follow-ups, not executed contributions or automatic next batches. B71 and further probes are not launched by this release.
