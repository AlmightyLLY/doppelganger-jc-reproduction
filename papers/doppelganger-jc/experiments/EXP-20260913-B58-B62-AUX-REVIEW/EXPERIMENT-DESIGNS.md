# Designs, competing explanations, and what changed

This is a retrospective public account of frozen experiments. It does not replace the actual pre-run Word/Excel records, whose hashes are committed in this package. `gold` means the synthetic author reference; independent human gold remains **zero**. All models are fixed snapshots; see each batch's `statistics.json` for model revisions and generation settings.

## Shared task and measures

The model reads fictional Chinese records and extracts **actor** and **undergoer** from target R1, while instructions exclude R2. AU requests actor first; UA requests undergoer first. BA denotes 把 constructions and BEI denotes 被 constructions. These are construction and output-schema factors, not two languages. `NONE` removes R2. BA_TOPIC and BEI_TOPIC express the same R2 event with different constructions in the topic-style background frame.

The author reference distinguishes complete correctness (C), target-person role reversal (R), other known wrong assignments (OTHER_W), and unresolved (U). A correct set of two names is weaker than correct assignment. Formatting, content, name selection, and role binding are separate outcomes. Unknown/truncated names remain U where the frozen scorer cannot resolve them. Paired reports retain rescues, new harms, and U transitions. Do not infer paired net effect by subtracting rescue/harm counts when U transitions also occur.

`P` in B60–B62 is a **joint correctness measure**: for a fixed target, both matched background variants must yield the author answer. Agreement between two wrong answers does not earn credit. The main analysis uses two selected construction/schema cells per group (BA/UA and BEI/AU), hence 24 pairs for 12 groups. NONE calibration pairs the original target fact with a genuine actor/undergoer swap. Cluster/bootstrap and leave-one summaries use the author group, not each prompt as an independent sample. Author-group clustering does not eliminate shared-template or linked-predicate dependence.

## B58

**Question:** Does the apparent benefit of a same-fact background construction edit survive reversing the answer-field order? Earlier AU-only results could not cleanly separate BEI selectivity from target/schema incongruence.

**Design:** Apertus and Qwen, 576 prompts each (1,152 formal outputs), matched AU/UA schema variants on the eight previously exposed predicate groups. Current-session old-AU bridges are retained separately. Inspect all cells, including BA targets under UA; predefine paired background effects, schema rescue/harm, and leave-one/bootstrap sensitivity.

**Decision-relevant outcome:** Apertus BEI/UA in the DIFFERENT subset barely improves (31→32 of 32), while BA/UA is harmed (26→19, seven harms and no rescues) by changing R2 from BA to BEI. Thus a universally protective 被 background, or a stable BEI-target-only effect, is not supported. Current AU bridge output drift (10/576) prohibits silently pooling current and historical answers. An early numerical failure and four diagnostic calls are separate from the 1,152 formal outputs.

## B59

**Question:** Can a third background order distinguish a simple linear-order account from construction-related effects, on new material? Can the models perform the component tasks without a distractor?

**Design:** Twelve new author groups, two models, 1,088 outputs including 32 old bridges; same-fact SVO/OSV and BA/BEI topic-frame background comparisons, both schemas, and no-background/component capability controls. New material and the topic frame changed together: this is not a single-factor replication of B58.

**Decision-relevant outcome:** The predesignated Apertus joint directional prediction is only partially supported. SVO→OSV raises BEI/AU correctness 4→8/24 as predicted, but also raises BA/UA 9→11/24 where the simple account predicted harm. The latter has three rescues and one harm. Apertus's standalone OSV capability is only 4/12 under AU and 10/12 under UA, so a background-order interpretation is limited by task/material calibration. Qwen's corresponding OSV scores are 10/12 and 12/12. Two unresolved truncated-name outputs are retained. BA↔BEI at fixed facts necessarily changes linear participant order; adding OSV does not by itself isolate corpus frequency.

## B60

**Question:** Are poor component-task results and background sensitivity responsive to a small, fixed demonstration package? Does the response depend on model or demonstration order?

**Design:** Same 12 B59 author groups; ZERO, fixed four-example DEMO_F, and the same examples reversed as DEMO_R. Both models receive 216 test prompts per condition, for 1,296 outputs. The examples include an OSV construction. Test NONE originals and role swaps, standalone OSV, and matched same-fact backgrounds. Do not tune examples or order after seeing outputs. The 336 ZERO bridge outputs match B59 exactly.

**Decision-relevant outcome:** Qwen improves from 205/216 to 216/216 in both orders (11 rescues, zero harms); primary P rises 19→24/24. Apertus declines from 166/216 to 159 and 158; rescue/harm is 18/26 and 21/31, with two U-involved pairs per order. Apertus also increasingly selects background people (34 and 45 OTHER_W outputs). Its P is 6→8 and 5/24 and component calibration is not established. The same example package has opposite overall consequences across the two snapshots.

## B61

**Question:** Are Apertus's errors specific to mandatory JSON punctuation, or do they persist with another labelled extraction interface?

**Design:** 192 existing ZERO task inputs in JSON and 192 matched labelled key/value responses (384 outputs), same Apertus snapshot. Includes 96 background cases and 96 NONE original/role-swap cases per format. KV retains explicit role labels and output order; this is not unconstrained natural language generation. The 192 JSON bridges exactly reproduce B60.

**Decision-relevant outcome:** JSON yields 152 C / 38 R / 2 U; KV yields 144 C / 42 R / 2 OTHER_W / 4 U. Background correctness stays 66/96. P rises 6→8/24, but the group-bootstrap interval for that gain includes zero; NONE original/swap joint performance deteriorates. There are nine rescues, fourteen harms and five U-involved pairs. Errors persisting in KV rule out a JSON-punctuation-only account, not every possible interface account or a specific internal failure stage.

## B62

**Question:** Does the exact successful B60 four-example package transfer to fresh author materials, without tuning, in both example orders?

**Design:** Qwen only; 12 new groups with new names, predicates and contexts in the same synthetic template family. There are 192 distinct new base tests × ZERO/F/R = 576 new-material outputs, plus 24 old B60 bridges, totaling 600. Examples are unchanged. The core P still uses 24 pairs; NONE role-swap calibration uses 48 pairs. Predefined headroom, unresolved-score bounds, cross-order rescue/harm and leave-one criteria are retained. No expansion of examples, model families or test templates is authorized by this result.

**Decision-relevant outcome:** ZERO 182/192 C (8 R, 2 background-person errors); F/R both 192/192. Each order rescues the same ten outputs with zero new harms. P 19→24/24; gain 20.83 percentage points, leave-one range 18.18–22.73 points, 10,000 group-bootstrap 95% interval 8.33–33.33 points (seed 620913). NONE joint correctness 47→48/48; all 24 bridges are exact in input/output tokens and text. This meets the frozen `REPLICATED_PACKAGE_GAIN` criterion. It establishes a development-material replication of this package's response in Qwen, not abstract grammar learning or a universal repair.

## AUX: observation and calibration are separate

**Question:** Can existing Apertus failures be diagnosed with layer readouts, a held-out name-conditioned role probe, and calibrated intervention tooling?

**Design:** All 192 B61 JSON inputs, 12 groups, 33 residual layers (embedding output plus 32 blocks), four fixed positions where available: shared instruction end, R2 end, R1 end, native prompt end. R2 comes before R1. Generate 48 predetermined natural baseline answers plus four no-hook repeats. Score four complete candidate answers for each input, and inspect the first divergent token under each pair's shared answer prefix. Different opponent comparisons may have different teacher-forced prefixes; they are not a single four-answer distribution.

The fixed name-conditioned probe uses a 64-dimensional bilinear feature from normalized hidden state, the query-name embedding and a fixed random projection, followed by standardized L2 logistic regression. Train on NONE inputs from 11 groups; test on the twelfth. R1-end duplicate training prefixes are merged. Include 20 training-label permutations, name-only and first-position baselines, an explicit BA/BEI rule, and construction-transfer tests. Do not select a winning layer from the observed curves. No R2-end classifier is trained because NONE training examples have no R2 anchor.

**Observation outcome:** 48 native outputs contain 30 correct answers and 18 complete target-role reversals; all have the correct target name set and valid formatting. There are 768 baseline candidate scores and 20,592 single-position layer readouts. Held-out NONE probe performance stays near chance. Background labels are balanced across all groups but constant within each group, so background-only accuracy lacks a within-group fact-swap test. Late conditional lens preferences do not demonstrate natural-output knowledge or causal use.

**Calibration boundary:** The first auxiliary run stopped on a cross-length prefix comparison. Same-length comparisons were exact, and CPU causal-mask inspection found no future-token mask leak; the numerical/kernel root cause is not proven. A limited continuation completed observations, but its first disk-archived SELF candidate changed token scores (sum delta −0.12781748; maximum token delta 0.16109395). Thus original donor/sham interventions and SELF free-generation interventions were **not run**. These are missing causal evidence, not zero causal effects.

**AUX-CAL-02:** A separately authorized repair freezes eight prior inputs from four predetermined groups and every model call to shape [1,512], using masked right padding and the original valid tokens. Precision and snapshot stay fixed. Eight saved/reloaded prefills precede 16 candidate baselines, 64 SELF candidates, then at most 20 generations. Require all 33-layer prefix states, SELF scored logits/log probabilities, and generated-token identities to meet the original exact criteria. Any failure stops dependent steps; no retries or adjusted tolerance. Passing would calibrate this tool configuration only, and does not authorize donor intervention. See the final [AUX report](AUX/README.md) for the actual repair coverage and outcome.
