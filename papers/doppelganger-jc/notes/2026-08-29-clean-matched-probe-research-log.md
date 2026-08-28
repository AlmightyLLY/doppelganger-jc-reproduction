# Research Log — 2026-08-29

## 1. Objective

Today I aimed to turn the previous exploratory Logit Lens work into a smaller and more defensible experiment. The first item-416 probe had passed its technical checks but produced unstable and score-dependent trajectories. Instead of expanding that result, I froze a five-item clean matched-probe pilot designed to test one narrow question:

> Does target-word kana replacement change preference between a human-frozen reference lexicalization and a visible-form lexicalization more than an unrelated kana control does?

The purpose was not to prove a mechanism from five examples. It was to determine whether the repaired design could produce interpretable, auditable case-level evidence before any larger confirmatory study.

## 2. What I completed

The five retained items had already passed blind linguistic review and human freezing. Each item used exactly two complete Chinese candidates, three source conditions, and a fixed primary score. Two items were unsafe cases in which the visible-form alternative was judged semantically wrong. Three were safe cases in which both Chinese alternatives were judged acceptable, so their results could only be interpreted as preference shifts.

The pilot ran on the exact `Qwen/Qwen3-8B` revision `b968826d9c46dd6066d109eabc6255188de91218`. It saved all 37 real hidden states, full-vocabulary readouts, complete-candidate scores, lexical-span scores, token ranks, and final-projection checks. The model completed the authorized scope exactly once.

I also preserved two operational failures rather than hiding them. The first Pod window stopped before model loading because a lock-referenced script was absent from the upload bundle. After the upload manifest was corrected, the authorized inference completed. The frozen output validator then produced six apparent top-50 errors. Direct inspection showed that all six were cutoff ties: the target token had the same log probability as the final retained token, and `torch.topk` selected a different member of the tie. A supplemental CPU-only audit resolved the false positives without changing the raw output or rerunning the model.

## 3. Main observations

The frozen primary prediction was supported on four of five selected items. The two equal-token-count cases were both positive, and their descriptive mean controlled contrast was `+1.478535`.

The most important individual result was unsafe item 354. The original and unrelated-control conditions preferred the visible-form error, while target-kana preferred the reference; every saved metric agreed with this rescue pattern. Unsafe item 451 also had a positive contrast, but it already preferred the reference in every condition, so it demonstrated sensitivity without an accuracy correction.

The safe cases were deliberately interpreted differently. Items 175 and 300 shifted toward the reference after target-kana relative to the control, while item 35 shifted in the opposite direction. Because both candidates were acceptable, these outcomes cannot be counted as accuracy gains or losses.

Item 35 also showed why the scoring audit remains necessary. Complete-candidate mean NLL and raw sequence score gave a negative contrast, but the lexical-span score gave a positive contrast. Item 300's final primary contrast was slightly positive, yet every layer in the predefined 29–34 upper band was negative. I therefore cannot treat a final-layer sign alone as evidence of a stable trajectory.

## 4. How my interpretation changed

Earlier work established that visible orthography changes model preference, but the broad intervention mixed clean failures, acceptable alternatives, token-length differences, and several possible form-derived senses. Today's matched design sharpened the question.

The strongest current interpretation is not that kana replacement generally fixes homograph errors. Instead:

- in at least one clean unsafe case, removing the visible target form produced the predefined rescue while an unrelated kana rewrite did not;
- in safe cases, the same intervention can redirect preference without changing semantic acceptability;
- the direction can depend on score definition and can be unstable across adjacent upper layers.

This strengthens the motivation for reliability-aware selective verification, but it does not yet validate a reliability estimator. The relevant prediction target is not merely whether the model copied a form. It is whether a form-derived proposal is contextually acceptable and stable under a defensible evaluation.

## 5. Methodological lessons

### Freeze language before inspecting model behavior

The distinction between unsafe and safe items prevented me from calling every positive shift a correction. Human semantic freezing is part of the experimental design, not an optional interpretation step after the run.

### Structural matching does not remove scoring sensitivity

Using the same carrier and changing only the lexical span greatly improves interpretability, but unequal token counts can still make mean NLL, raw sequence probability, and lexical-span scores disagree. Equal-length items should therefore remain a primary core rather than a post-hoc convenience.

### Adjacent-layer stability matters

A final-layer contrast can reverse the direction seen throughout the upper band. Layerwise analysis should report actual layers, sign runs, and metric agreement rather than selecting a visually favorable peak.

### Validators are part of the evidence chain

The top-50 incident was not merely an engineering nuisance. Competition rank and `topk` membership are different under tied logits. Preserving the original failure and adding a narrowly scoped tie audit was more defensible than silently changing the frozen validator or rerunning the model.

### A failed preflight should remain visible

The incomplete upload did not consume the authorization or load model weights, but it still cost time and money. Recording it makes the operational history and cost estimate honest.

## 6. What the evidence supports

For these five selected Qwen3-8B items, I can report that:

- the primary controlled contrast was positive for four items;
- both equal-length core items were positive;
- one of two unsafe items showed the predefined rescue pattern;
- scoring and upper-layer stability changed the interpretation of individual cases.

I still cannot claim population-level significance, a general causal mechanism inside the model, an English pivot, a universal decision layer, cross-model generality, or improved free generation. The pilot is evidence that the repaired measurement is worth studying, not evidence that the broader method is already established.

## 7. Research practice reflection

The useful work today was not increasing the number of models or items. It was narrowing the contrast, freezing the linguistic decisions, preserving inconvenient failures, and distinguishing stable evidence from a favorable final value.

This represents a healthier research loop than the earlier large-scale execution phase:

```text
unstable probe
→ identify confounds
→ repair one contrast
→ freeze predictions and interpretation rules
→ run once
→ audit failures
→ update the claim boundary
```

I am becoming more able to explain why an experiment was run, what would count as support, and why some apparently positive results should still be treated cautiously. The remaining weakness is that I still need more practice reading the layerwise evidence directly rather than relying on a finished summary.

## 8. Next steps

The next step should not be an automatic scale-up. I should first personally inspect:

1. the full trajectories for the stable positive items 175 and 354;
2. the metric disagreement for item 35;
3. the upper-band/final-layer reversal for item 300;
4. whether the semantic freezing for the retained cases should receive a second bilingual judgment.

Only after this review should I freeze a small confirmatory set or a cross-model replication. Its selection rule, equal-length core, exclusion criteria, and stopping rule must be written before new results are visible.

## 9. One-sentence update

I converted an unstable one-item Logit Lens probe into a human-frozen five-item matched pilot, found a clean rescue in one unsafe case and positive controlled shifts in four of five selected items, and learned that scoring choice, adjacent-layer stability, and validator semantics are essential parts of any defensible claim about orthographic influence.
