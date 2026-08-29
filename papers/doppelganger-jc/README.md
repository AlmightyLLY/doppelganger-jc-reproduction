# Doppelganger-JC Reproduction

This directory documents a partial reproduction and measurement audit of [Doppelganger-JC](https://aclanthology.org/2025.ijcnlp-long.96/), with an extension that tests whether visible Japanese target-word orthography causally affects Chinese candidate preference.

## Scope

Completed:

- Japanese-to-Chinese Translation Type-1, 462 items, six accessible paper checkpoints;
- Chinese-to-Japanese Translation Type-1, 455 items, the same six checkpoints;
- paper-versus-reproduction accuracy comparison;
- official full-prompt PPL and candidate-only NLL diagnostics;
- data-quality and duplicate-candidate audits;
- shared-error review;
- six-model target-kana intervention with a within-sentence unrelated negative control.

Not completed:

- the exact `meta-llama/Llama-3.1-8B-Instruct` checkpoint, because gated access was denied;
- word-meaning, word-meaning-in-context, other translation types, human baselines, open-ended generation, POS analyses, and appendix experiments;
- independent bilingual validation and external-dataset replication of the orthography intervention.

This work should therefore be described as a six-model bidirectional reproduction of Translation Type-1 plus a controlled orthography extension, not as a complete reproduction of the entire paper.

## Models

| Model | Japanese→Chinese | Chinese→Japanese |
|---|---:|---:|
| Qwen2.5-7B-Instruct-1M | 68.40% | 64.40% |
| llm-jp-3-7.2b-instruct3 | 58.87% | 65.49% |
| Llama-3-ELYZA-JP-8B | 52.81% | 60.66% |
| Baichuan2-7B-Base | 59.74% | 56.26% |
| Mistral-7B-Instruct-v0.2 | 50.43% | 41.10% |
| Gemma-7B | 60.82% | 61.32% |

All percentages above use the paper's official full-prompt PPL scoring rule and the unmodified task set. Exact model revisions and validation checks appear in the corresponding experiment records.

## Reproduction quality

For Japanese-to-Chinese, the absolute difference from the paper was at most 1.95 percentage points across the six models, with a mean absolute difference of approximately 0.79 points. For Chinese-to-Japanese, the mean absolute difference was approximately 0.77 points; Baichuan had the largest difference at −2.64 points. These aggregate results reproduce the target columns closely, while the absence of paper-released item-level predictions prevents a claim of item-level identity.

## Measurement audit

For candidate `i`, let `C,K` denote the total NLL and token count of the shared prompt context, and `S_i,L_i` the NLL and token count of the candidate span:

```text
official(i)       = (C + S_i) / (K + L_i)
candidate-only(i) = S_i / L_i
```

Candidate-only scoring uses the same source sentence and forward pass; only the final averaging mask changes. It is a diagnostic for scoring sensitivity, not a human baseline and not a replacement for the paper metric.

Across the six Japanese-to-Chinese models, 94.4% of official-versus-candidate-only disagreements favored the longer-token candidate under the official score. The corresponding proportion was 96.3% for Chinese-to-Japanese. This is consistent with a structural interaction between shared-prompt loss and candidate length, but it does not show that the underlying model blindly prefers longer translations.

## Orthography intervention

The primary intervention compared:

1. the original Japanese source sentence;
2. the same sentence with the target homograph converted from kanji to kana;
3. the same sentence with an unrelated kanji-bearing component converted to kana.

The primary candidate-only margin was:

```text
margin = NLL(wrong1) - NLL(correct)
effect = margin(target_kana) - margin(unrelated_control_kana)
```

A positive effect means that removing visible target-word kanji makes the correct candidate more favorable relative to `wrong1`, after subtracting the generic kana-rewrite control.

On the frozen 382-item analysis set, the fixed six-model mean effect was `+0.136`, with a paired bootstrap 95% confidence interval of `[+0.100, +0.173]`. Five models had intervals above zero; llm-jp was slightly negative with an interval crossing zero.

Final four-way accuracy was heterogeneous: Baichuan and Mistral improved, Qwen, llm-jp, and ELYZA declined, and Gemma was nearly unchanged. The intervention therefore supports a causal contribution of visible orthography to candidate preference under this design, but not a universal benefit from kana normalization.

## Evidence boundary

The current evidence supports the claim that visible target-word orthography is an input feature that can alter correct-versus-homograph candidate preference. It does not establish that orthography is the strongest factor, reveal an internal “semantic-check skipping” algorithm, or generalize automatically to new tasks and datasets.

The working research question is consequently reliability-aware: can a system estimate when a form-derived proposal is useful and selectively trigger semantic verification or retrieval when it is not?

## Documentation index

Primary reports:

- [Japanese-to-Chinese six-model synthesis](experiments/EXP-20260825-jp-zh-type1-six-model-synthesis.md)
- [Chinese-to-Japanese and bidirectional synthesis](experiments/EXP-20260825-zh-jp-type1-six-model-synthesis.md)
- [Six-model orthography replication](experiments/EXP-20260825-orthography-six-model-replication.md)
- [Stage synthesis and open questions](notes/2026-08-23-to-25-stage-synthesis.md)
- [Research trajectory and revised reliability-aware agenda](notes/2026-08-26-research-trajectory-and-revised-theme.md)
- [Post-meeting research log: current-model audit and layer-wise diagnostics](notes/2026-08-27-post-meeting-research-log.md)
- [Clean matched-probe research log](notes/2026-08-29-clean-matched-probe-research-log.md)
- [Five-item Qwen3-8B clean matched-probe pilot](experiments/EXP-20260829-clean-matched-probe-five-items.md)
- [Fifty-item factorial external-validation research log](notes/2026-08-30-factorial-external-validation-research-log.md)
- [Qwen3-8B orthography × semantic-information external validation](experiments/EXP-20260830-orthography-semantic-factorial-external-50.md)

Confirmatory plans and development records are listed in the [experiment index](experiments/README.md). Scores-only tables and analyses are listed in the [results archive](../../results/README.md).
