# Methodological Reflection — 2026-08-25

## 1. What I personally completed today

I read the experiment reports that remained from yesterday, as well as the reports produced from today's runs. I inspected whether the control words in the kana intervention were appropriate. I decided that the primary negative control should be a semantically unrelated kanji-bearing component in the same source sentence, rather than a component closely related to the target meaning. This decision led to a target-kana versus unrelated-control-kana comparison, while the more strongly related controls were retained for sensitivity analysis.

## 2. The three most important facts I learned today

1. Orthographic overlap is strongly associated with model choices. In the Japanese-to-Chinese Translation Type-1 experiment, `wrong1` accounted for 69.5%–85.3% of each model's official errors. The controlled kana intervention provided stronger evidence that visible target-word orthography can causally affect the correct-versus-`wrong1` preference margin.
2. The unrelated control worked empirically as a negative control: kana-converting an unrelated component changed the six-model mean margin by only about `+0.005`, whereas converting the target word produced a much larger and model-dependent change.
3. Target-word kana conversion reduced `wrong1` choices in five of the six models, but it did not uniformly improve four-way accuracy. Some decisions moved from `wrong1` to `wrong2` or `wrong3`; Baichuan and Mistral improved, Qwen, llm-jp, and ELYZA declined, and Gemma was almost unchanged. Orthographic information can therefore be useful evidence as well as a harmful shortcut.

## 3. The result that surprised me most

I was most surprised that removing visible target-word orthography often reduced the attraction of `wrong1`, yet did not consistently improve overall accuracy. I had expected that weakening the suspected shortcut would directly improve performance. Instead, the intervention changed the whole candidate competition: a model could become less attracted to `wrong1` but then select `wrong2` or `wrong3`.

This result strengthens the motivation of my research proposal, although it does not by itself validate the proposed method. It suggests that the useful question is not whether orthographic information should always be removed, but when it should be trusted.

## 4. How my original hypothesis changed

### What I originally thought

I thought that bypassing or normalizing the orthographic cue would generally improve model accuracy.

### What I now think

Orthographic similarity should be treated as a conditionally reliable prior. It can provide an efficient lexical clue in some items and models, while producing false-friend or copy-based errors in others. My research objective should therefore be to identify this boundary and help a model retain useful form-based evidence while triggering semantic verification when that evidence is unreliable.

### Evidence that changed my view

The six-model intervention produced a positive fixed-set correct-versus-`wrong1` margin effect of `+0.136`, with a paired bootstrap 95% interval of `[+0.100, +0.173]`. Five models had positive intervals, but the corresponding accuracy changes were heterogeneous. This combination of a shared preference effect and divergent final decisions is what changed my hypothesis.

## 5. My current understanding of the causality of the orthographic shortcut

### What the observational evidence supports

Across the six Japanese-to-Chinese runs, 69.5%–85.3% of official errors were concentrated on `wrong1`, the candidate constructed around the overlapping form. This is strong descriptive evidence that the homographic distractor has special attraction. It is not, by itself, causal evidence, because candidate naturalness, frequency, semantic distance, length, and label ambiguity may also differ.

### What the intervention supports

Relative to kana-converting an unrelated source component, kana-converting the target word systematically changed the correct-versus-`wrong1` NLL margin in five of the six models. This supports a causal contribution of visible target-word orthography to candidate preference under the frozen intervention design. The redistribution toward `wrong2` and `wrong3` further shows that orthography shapes the candidate competition rather than operating as a simple isolated error switch.

### What remains unproven

The current evidence does not prove that orthography is the strongest causal factor among all alternatives, that the model internally “skips” semantic processing, that orthographic effects are beneficial more often than harmful, or that kana conversion fully removes form-based lexical knowledge. It also does not yet establish generalization to new datasets, language pairs, generation tasks, or retrieval tasks.

## 6. My current understanding of reliability

The reliability to be estimated is not merely the model's overall confidence. It is the item-level probability that accepting a form-derived translation proposal will improve the final decision relative to a more expensive semantic-verification path.

The model should retain the orthographic clue when the estimated reliability is high—for example, when form-based and context-based predictions agree and the semantic context supports the proposed meaning. It should trigger semantic verification, external retrieval, or abstention when the estimated reliability is low, when the two reasoning paths disagree, or when the word has false-friend and ambiguity risks.

The acceptance threshold should eventually be calibrated on held-out development data according to the desired risk–coverage or accuracy–cost trade-off, rather than chosen directly on the test set as an arbitrary fixed number.

## 7. The scope of my reproduction

### Completed

I completed the bidirectional Translation Type-1 experiments—Japanese-to-Chinese and Chinese-to-Japanese—on six accessible paper checkpoints. I also audited the official and candidate-only scoring schemes, examined the error distribution, reviewed a subset of shared `wrong1` cases, and conducted a six-model target-kana intervention with an unrelated negative control.

### Not completed

I have not reproduced the paper's word-meaning, word-meaning-in-context, other translation-type, human-baseline, open-ended generation, POS, and appendix experiments. The current causal evidence also lacks independent bilingual annotation and external-dataset replication. The source of the official scoring scheme's token-length sensitivity and the design of a better calibrated scoring mechanism remain unresolved.

### Why I am stopping at this stage

The core Translation Type-1 phenomenon has been reproduced in both directions, and the intervention has already established a useful boundary for the next research question. Merely increasing the number of runs on the same task is now likely to have lower marginal value. The next cited paper provides the downstream contextualized phrase-retrieval setting in which the reliability hypothesis should ultimately be tested.

## 8. Issues I still do not fully trust or understand

1. I do not yet know how to isolate and correct the token-length sensitivity of the official scoring procedure without replacing the paper's reproduction metric with an unvalidated alternative.
2. I need a clearer framework for comparing official PPL, candidate-only NLL, calibrated or PMI-style scoring, and bilingual human judgments.
3. I have not fully mastered all relevant evaluation concepts and statistical terminology, especially calibration, selective prediction, risk–coverage analysis, and the distinction between behavioral causal evidence and claims about internal mechanisms.

## 9. How I would report the current stage

### One-sentence progress summary

I have completed a six-model partial reproduction of the paper's bidirectional Translation Type-1 setting and obtained initial controlled evidence that visible orthography changes correct-versus-homograph candidate preference.

### The result most worth reporting

Target-word kana conversion produced a positive six-model mean correct-versus-`wrong1` margin effect, but its effect on final accuracy differed substantially across models. This motivates a reliability-aware selective strategy rather than always preserving or always removing orthographic cues.

### A focused next-stage question

The next decision is whether to reproduce the Cross-lingual Contextualized Phrase Retrieval baseline and operationalize reliability as an item-level routing decision there, while treating stronger causal identification and the remaining Doppelganger-JC tasks as selective follow-up work.

## 10. The minimum first step for the next paper

Tomorrow I will first read the abstract, introduction, method, experimental setup, and main result tables of the Cross-lingual Contextualized Phrase Retrieval paper. I will write a claim-to-table map before running any code. I will then read the official repository README myself and locate the data-preparation pipeline, model entry point, evaluation script, and smallest documented baseline command. I will choose the first table cell or metric to reproduce only after completing this map.

## 11. Workflow and research responsibility

### Work suitable for automation and engineering support

Environment inspection, reproducible scripting, mechanical checks, cloud-job monitoring, hash and row-count verification, statistical aggregation, and report formatting can be automated or delegated when their outputs are independently checked.

### Research judgments that I must make personally

I must personally understand the paper and repository, formulate the hypothesis and competing explanations, decide whether controls are conceptually valid, review ambiguous examples, interpret evidence, define stopping conditions, and write the first version of my scientific conclusions.

## 12. My work state today

### What was effective

I repeatedly reconsidered the choice of the control condition rather than accepting the first convenient design. This led to a more defensible unrelated negative control and an experiment that could distinguish target-specific orthographic effects from generic sentence rewriting.

### What I need to adjust

Before launching another substantial experiment, I should write a short preregistration containing the research question, primary hypothesis, competing explanations, primary metric, analysis set, and the result that would cause me to revise my belief.

### My stopping conditions for tomorrow

I will stop if I feel physically unwell, if my reasoning becomes confused, or if experiment production begins to outpace my understanding and skill development. I will also avoid starting a new major run before I can explain what evidence it is intended to produce and how each possible result would change my conclusion.
