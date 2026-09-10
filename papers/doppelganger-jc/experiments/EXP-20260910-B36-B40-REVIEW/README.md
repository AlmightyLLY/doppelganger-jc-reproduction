# B36–B40: Evidence package for an independent research diagnosis

Prepared 2026-09-10 after completion of B40. This is a retrospective synthesis, not a preregistration. Please inspect the raw prompts and counterexamples rather than taking our interpretation as established.

## Research question and scope

How do sentence construction, competing event descriptions, and response interfaces affect identifying who did what to whom? The immediate phenomenon is role reversal under Chinese negative passives, with large differences between joint answer-field orders. This branch emerged from a Japanese–Chinese shared-form translation project but these experiments do not test homographs or a shared internal mechanism with that project.

All five batches use Qwen3-8B at revision `b968826d9c46dd6066d109eabc6255188de91218`, deterministic decoding with thinking disabled. The materials are eight exposed author-constructed scenarios with four predicates and two name groups. Variants, models, and repeated calls are not independent scenarios. Independent human gold is zero. Author-AI labels and exact parsing are development references, not validated population error rates.

AU = joint JSON actor then undergoer. UA = joint JSON undergoer then actor. These specify participants in the relation expressed by R1, including when the action is denied; they do not assert that an event occurred. R2 is another numbered record. Names are fictional.

## Reading order and data

1. Read this synthesis and its claim limits.
2. Read the complete raw prompts and outputs in [B36](B36-evidence.json), [B37](B37-evidence.json), [B38](B38-evidence.json), [B39](B39-evidence.json), [B40](B40-evidence.json).
3. Each JSON contains `raw_outputs`, token IDs, the raw-source SHA256, and `frozen_analysis`. Call/source IDs link comparisons across batches. Native input/output text is preserved, including null and channel markers. Source paths, machine/account configuration, personal annotations and local Office originals are excluded.

There are 4,416 new output records in these five batches, NOT 4,416 independent examples. B37 includes repeated passive prompts, B38 comparisons reuse B36/B37 historical outputs, and 48 B40 prompts repeat B39 exactly. Raw tokens are provided for audit, not as evidence of hidden-state mechanisms. No activation experiment was run here.

## Experiment sequence

| Batch | Purpose | New calls | Main result | What it changed |
|---|---|---:|---|---|
| B36 | Hold target fixed, vary distractor identity/role/expression and record order; compare AU/UA | 784 | 667 correct; 117 errors all exact target-role reversals. AU→UA rescued 97 and harmed 2 | A strong local output-order effect; not a general repair or stable attraction mechanism |
| B37 | Cross target active/passive construction with answer order | 1,568 | Passive 667/784 correct; active 781/784. 117 rescues and 3 harms. Strict predicted order crossover failed | Construction matters, but voice, subject and mention order are bundled; active ceiling limits inference |
| B38 | Ask each role separately and choose complete mappings with answer position swapped | 1,568 | On 384 double-record sources: AU 278C, UA 373C, both single roles C 202, both choice positions C 305 | Easier-looking interfaces introduce their own errors and choice-position preference |
| B39 | Cross polarity, context presence/order and role/structural/factual question types | 384 | On 48 sources: legacy singles 35C, explicit relation singles 4C, structural extraction 42C, joint UA 46C; factual control 47C | The proposed explicit diagnostic itself failed; a positive interaction was not improvement |
| B40 | Factor the questionable instruction and undergoer wording on single sentences | 112 | Concrete wording repairs affirmative cases, but negatives mostly become null; joint UA 16/16 | Partial diagnosis of a measurement-design failure, not a reliable negative-role repair |

C/W/U mean correct/wrong/unresolved under the frozen rule. U is not a measured probability of correctness. Null is allowed output syntax; it is not a formatting violation. B38's original `format_ok` implementation excluded null; all 87 nulls were retained with the frozen flag and a separate posthoc allowed-format correction. Do not interpret those flags as 87 instruction-format violations. B39/B40 correctly accept null syntax. No historical semantic labels were overwritten.

## B36–B37 details

B36 has 384 unique double-record sources and 8 single-record controls, each in AU/UA. On double records, target-first AU=133/192 vs UA=186/192; target-last AU=145/192 vs UA=187/192. Single-record controls are all correct. The weak AU baseline should not hide the much stronger UA baseline.

B37 reran the 784 passive prompts and their active counterparts. The passive bridge matched B36 prompts, input tokens and outputs exactly; it is an engineering/repeatability bridge, not independent material confirmation. Active AU/UA advantages did not exhibit the predicted strict sign reversal. The passive and active comparison changes multiple linguistic properties. Earlier compatibility predictions were not robust enough to establish “Event-Role Attraction.”

## B38: diagnostic interfaces can create misleading success

Four fresh requests per unique source: actor-only, undergoer-only, correct mapping at A, correct mapping at B. Old AU/UA are explicitly historical comparators.

On 384 double-record sources, actor-only=210C/90W/84U and undergoer-only=364C/18W/2U. Combining independent responses gives 202C/99W/83U; this is an analytical join, not a real multi-stage model run. There are 87 same-person double assignments and 7 exact reversals.

Choice correctness is 382/384 when gold is A, 305/384 when gold is B; 77 sources yield A in both versions. Stable correctness requires both positions correct. Against AU, stable choice rescues 68 but harms 41; against UA, rescues 5 but harms 73.

Of 106 AU reversals, 15 have both single roles correct and 9 have all four new answers correct (six scenarios). This proves limited cross-task behavioral dissociation. It does NOT show that the original wrong run internally encoded or used the correct mapping. New requests recompute; choices also supply complete mappings.

Example `B38-N02-B-ACTOR-FIRST-ORDINARY-TARGET_LAST`: R1 “苏禾没有被许安批评”, R2 “苏禾批评了沈言” with distinct backgrounds. AU reverses the pair; UA and all four new queries are correct. Counterexample: some previously correct sources become wrong under single queries. Even the eight single-record controls yield only six complete-correct single-query pairs.

## B39: the explicit question was a poor measuring instrument

All eight old scenarios, affirmative/negative target × no R2/target first/target last = 48 sources. Fresh legacy single-role questions L, explicit questions E, structural questions S, factual question F and joint UA total 384 calls. R2 has one fixed conflict configuration; this is not a broad distractor replication.

E retained “only identify the expressed relation” but added “temporarily remove negation” and used “who is the person this action points toward?” for undergoer. It bundled multiple changes. E produced 35/48 same-person assignments. Example `B39-N02-POS-NONE`: “苏禾被许安批评”; L/S/UA correct, E answers 许安 for both roles. Neither negation nor a second event is necessary for this failure.

The registered contrast was D=(E_NEG−L_NEG)−(E_POS−L_POS), with an additional requirement that E actually improve NEG. D=+12.5 percentage points overall, but E_NEG=1/24 vs L_NEG=15/24 and E_POS=3/24 vs L_POS=20/24. Positive D comes from greater affirmative damage. L→E produces no W→C rescue, 30 C→W harms and one C→U. Thus the improvement hypothesis failed even under unresolved-score bounds.

S=24/24 on affirmatives and 18/24 on negatives; S_undergoer=48/48, with negative actor errors/null. F=47/48, but supplies both names, so cannot establish unaided role recovery. UA's two errors are N05 negative double-record reversals. Structural/factual success cannot localize a hidden processing stage.

## B40: component repair results

Sixteen single-record sources (all eight scenarios × polarity), seven fresh arms each. N1 keeps the temporary-negation-removal clause; N0 deletes only that clause. W0 uses “行为所指向的人”; W1 replaces only the question with “谁是句中被{verb}的一方？” Two matched actor arms and joint UA complete the design.

| Undergoer arm | Affirmative C/W/U | Negative C/W/U |
|---|---|---|
| N1W0 | 1/7/0 | 1/7/0 |
| N1W1 | 8/0/0 | 1/1/6 |
| N0W0 | 5/3/0 | 0/1/7 |
| N0W1 | 8/0/0 | 0/0/8 |

W1 rescues seven affirmative errors under N1 and three under N0, with no new C→W/U in those affirmative cells. Under negative N1, one rescue is offset by one C→U; the sole rescue disappears if N07 or its predicate is excluded. Deleting N worsens negative actor correctness from 7/8 to 1/8, introducing six C→U. Joint UA remains 16/16 here. All 48 exact repeated prompts/tokens/outputs agree with B39.

Concrete wording may provide a structural position cue. Null may reflect uncertainty, task interpretation or refusal to assign a participant to a denied event; this study cannot distinguish these interpretations. Reduced wrong-name counts or reduced same-person assignments are not reliable repairs if they become null. A frozen `local_repair=true` flag only requires some W→C and no C→W: check the separate C→U counts; it is not a general success label.

## Current interpretation: provisional, challenge it

1. Original joint output-order sensitivity is a repeatable local behavioral observation on exposed material.
2. Proposed role-compatibility, pure serialization and universal split-query repair explanations were not established.
3. B39 is principally a diagnostic-design failure. B40 partially identifies a wording contribution in affirmatives; it does not rescue the negative diagnostic.
4. Do not infer “knows but does not use,” English mediation, internal parsing stages or human good-enough mechanisms from independent prompts.
5. Stop iterating E on this material. A candidate next decision is independently constructed, reviewed material testing frozen AU/UA prompts, with proper strong baselines. No B41 was designed or run in this package.

## Questions for Pro

Please provide a critical assessment, not reassurance. Separate verified facts, alternative explanations, missing controls and suggested next actions.

- Which observations remain scientifically interesting after accounting for prompt design, answer length/structure, polarity, names, repeated materials and choice bias?
- Does the strong joint UA baseline make the split-query branch unproductive, or suggest a falsifiable question about joint constraints? Avoid internal causal attribution without evidence.
- Is B39/B40 mostly measuring English role-label interpretation or Chinese instruction ambiguity? Which single minimal comparison would discriminate the leading alternatives without another prompt search?
- Should we freeze AU/UA and validate on new materials now, or first abandon/repair the construct? Specify stopping criteria and expected decision-changing outcomes.
- What contribution could survive as a strong NLP analysis paper, and which claims should be removed? If reviewing novelty, verify primary literature and separate this package's evidence from external evidence.
- What exactly should a human annotator review before confirmation: target naturalness, role definitions under negation, discourse independence, or response scoring? Prioritize the smallest useful audit.

## Provenance and publication boundary

This package includes full synthetic experimental prompt/output records, frozen analysis, and source-file hashes. It deliberately excludes credentials, laboratory/account configuration, private researcher comments and local Word/Excel originals. Those remain in local archives; this public release is not a complete private backup. Word/Excel were generated before and after each batch; human review remains pending. The package is additive to the existing public research branch, not a push of local private history.
