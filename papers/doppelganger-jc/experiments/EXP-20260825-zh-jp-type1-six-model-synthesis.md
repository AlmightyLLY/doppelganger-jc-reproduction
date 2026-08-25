# EXP-20260825 — Chinese-to-Japanese Translation Type-1 and Bidirectional Synthesis

## Scope

This report covers 455 Chinese-to-Japanese Translation Type-1 questions for the six accessible Doppelganger-JC checkpoints, for a total of 2,730 four-option evaluations. Llama 3.1 was not run because access to the exact gated checkpoint was denied; no substitute model is reported as an exact reproduction.

## Summary

- The six official accuracies had a mean absolute difference of approximately 0.77 percentage points from the paper values. Five models differed by no more than 1.32 points.
- llm-jp exactly matched the paper aggregate at `298/455 = 65.49%`.
- Baichuan had the largest difference at −2.64 points; output structure, revision, finite scores, and argmin checks all passed.
- Across 1,141 official errors, 895 selected `wrong1` (`78.44%`).
- Candidate-only accuracy was 54.84% across model–item predictions, compared with 58.21% for official scoring. It nevertheless recovered 78 predictions that were wrong under official scoring.
- Of 298 official-versus-candidate-only disagreements, 287 (96.3%) favored the longer-token candidate under the official score.
- Aggregate strength again did not imply item-level containment.

## Checkpoints and environment

| Model | Fixed revision | Completed |
|---|---|---:|
| `llm-jp/llm-jp-3-7.2b-instruct3` | `cdd4c7f3296fdc7785423a864bd9a86ce4c15915` | 455/455 |
| `elyza/Llama-3-ELYZA-JP-8B` | `e6c316496ee7d9a11710c50229e8cb39b6b0a4a3` | 455/455 |
| `Qwen/Qwen2.5-7B-Instruct-1M` | `e28526f7bb80e2a9c8af03b831a9af3812f18fba` | 455/455 |
| `baichuan-inc/Baichuan2-7B-Base` | `f9d4d8dd2f7a3dbede3bda3b0cf0224e9272bbe5` | 455/455 |
| `google/gemma-7b` | `ff6768d9368919a1f025a54f9f5aa0ee591730bb` | 455/455 |
| `mistralai/Mistral-7B-Instruct-v0.2` | `63a8b081895390a26e140280378bc85ec8bce07a` | 455/455 |

Execution used a RunPod Secure Cloud NVIDIA A40 48 GB GPU, Python 3.11.10, PyTorch 2.5.1+cu121, Transformers 4.48.3, CUDA 12.1, and BF16 inference. Every output contained 455 rows with continuous indices, finite four-option losses and PPLs, the fixed revision, and a choice matching `argmin(PPL)`. Remote and local SHA-256 values matched.

Baichuan's first startup stopped before any formal row was written because its dynamic module required `bitsandbytes` to be importable. After installing the previously validated version `0.45.2`, the run restarted from 0/455. The failed startup was isolated from the formal output.

## Data audit

| Item | Count |
|---|---:|
| Cognate-list entries | 464 |
| Translation questions | 455 |
| Cognate entries without a question | 9 |
| Extra questions | 0 |
| Missing-field questions | 0 |
| Duplicate question keys | 0 |
| Questions with duplicate candidates | 1 |

The identities of the nine missing entries are available after joining to the
pinned upstream data. In item 439, `wrong1` and `wrong2` are identical.

The strict analysis retains all 455 official questions. The audited analysis excludes only item 439 and contains 454 questions. No candidate or gold label was silently rewritten.

## Scoring

The official Chinese-to-Japanese prompt is:

```text
“{original}”という中国語の文章の日本語訳は「{candidate}」です。
```

```text
official_loss = mean(NLL(all predictable prompt tokens))
candidate_loss = mean(NLL(candidate translation tokens only))
choice = argmin(exp(loss))
```

Candidate-only scoring uses the same forward pass and context but changes the averaging span. It is an evaluation diagnostic, not a human condition.

## Aggregate reproduction

| Model | Paper official | Reproduced official | Difference | Wilson 95% interval | Candidate-only | Candidate − official |
|---|---:|---:|---:|---:|---:|---:|
| llm-jp 7.2B | 65.49% | 298/455 = 65.49% | 0.00 pp | 61.01%–69.72% | 65.49% | 0.00 pp |
| Qwen2.5 7B-1M | 64.18% | 293/455 = 64.40% | +0.22 pp | 59.89%–68.66% | 62.64% | −1.76 pp |
| Gemma 7B | 60.00% | 279/455 = 61.32% | +1.32 pp | 56.77%–65.68% | 58.24% | −3.08 pp |
| ELYZA-JP 8B | 60.44% | 276/455 = 60.66% | +0.22 pp | 56.10%–65.04% | 57.58% | −3.08 pp |
| Baichuan2 7B Base | 58.90% | 256/455 = 56.26% | −2.64 pp | 51.67%–60.75% | 49.23% | −7.03 pp |
| Mistral 7B v0.2 | 41.32% | 187/455 = 41.10% | −0.22 pp | 36.67%–45.68% | 35.82% | −5.27 pp |

All paper values fall within the corresponding Wilson intervals. The intervals describe item-sampling uncertainty; they do not imply stochastic variation from rerunning a deterministic checkpoint.

## Error distribution and scoring sensitivity

| Model | `wrong1` / official errors | Paper `wrong1` rate | Official/candidate agreement | Official-only correct | Candidate-only-only correct | Official near-ties |
|---|---:|---:|---:|---:|---:|---:|
| Qwen-1M | 139/162 = 85.8% | 81.44% | 423/455 = 93.0% | 17 | 9 | 84 |
| llm-jp | 111/157 = 70.7% | 67.84% | 419/455 = 92.1% | 14 | 14 | 94 |
| ELYZA | 142/179 = 79.3% | 74.53% | 411/455 = 90.3% | 25 | 11 | 95 |
| Baichuan | 148/199 = 74.4% | 71.91% | 382/455 = 84.0% | 48 | 16 | 160 |
| Gemma | 143/176 = 81.3% | 78.25% | 409/455 = 89.9% | 27 | 13 | 98 |
| Mistral | 212/268 = 79.1% | 75.10% | 388/455 = 85.3% | 39 | 15 | 178 |

Across all 2,730 model–item predictions:

```text
official correct:             1,589 / 2,730 = 58.21%
candidate-only correct:       1,497 / 2,730 = 54.84%
choice agreement:             2,432 / 2,730 = 89.08%
official-only correct:          170
candidate-only-only correct:     78
```

Candidate-only is informative because it identifies scoring-sensitive cases, not because it improves the aggregate score.

## Candidate-length effect

Among the 298 disagreements:

```text
official selected the longer-token candidate: 287 (96.3%)
official selected an equal-length candidate:     9 (3.0%)
official selected the shorter-token candidate:   2 (0.7%)
```

The correct candidate was also longer than `wrong1` on average under all six tokenizers:

| Tokenizer | Correct mean tokens | `wrong1` mean tokens |
|---|---:|---:|
| Qwen-1M | 14.69 | 14.09 |
| llm-jp | 10.77 | 10.41 |
| ELYZA | 16.24 | 15.57 |
| Baichuan | 21.05 | 19.74 |
| Gemma | 11.72 | 11.32 |
| Mistral | 26.23 | 24.95 |

This reproduces the direction seen in Japanese-to-Chinese. It remains a property of the scoring formula and candidate distribution, not evidence that a model consciously chooses length when uncertain.

## Cross-model structure

| Correct models per item | Items |
|---:|---:|
| 0 | 55 |
| 1 | 41 |
| 2 | 61 |
| 3 | 54 |
| 4 | 65 |
| 5 | 70 |
| 6 | 109 |

Additional observations:

- 139 questions received the same option from all six models;
- 29 questions received unanimous `wrong1`;
- 55 questions were wrong for all six models;
- among the 41 questions solved by exactly one model, llm-jp solved 16 and Mistral solved 5 despite their different aggregate ranks.

These results again reject a strict item-level containment interpretation of model strength.

## Bidirectional comparison

| Model | Japanese→Chinese | Chinese→Japanese | Direction difference | Paper direction difference |
|---|---:|---:|---:|---:|
| Qwen-1M | 68.40% | 64.40% | −4.00 pp | −5.52 pp |
| llm-jp | 58.87% | 65.49% | +6.62 pp | +7.26 pp |
| ELYZA | 52.81% | 60.66% | +7.85 pp | +7.63 pp |
| Baichuan | 59.74% | 56.26% | −3.48 pp | −2.79 pp |
| Gemma | 60.82% | 61.32% | +0.50 pp | −1.04 pp |
| Mistral | 50.43% | 41.10% | −9.33 pp | −8.46 pp |

Five of six reproduced direction differences match the paper's sign. A simple claim that Japanese-heavy pretraining necessarily increases Chinese-to-Japanese homograph interference is not supported: llm-jp and ELYZA both score higher in that direction. Input comprehension, output-language modeling, prompt language, tokenizer, candidate construction, and checkpoint differences are all entangled.

At the aggregate level, the two directions show nearly identical `wrong1` shares:

| Direction | Official | Candidate-only | Official advantage | `wrong1` / official errors |
|---|---:|---:|---:|---:|
| Japanese→Chinese | 1622/2772 = 58.51% | 55.30% | +3.21 pp | 902/1150 = 78.435% |
| Chinese→Japanese | 1589/2730 = 58.21% | 54.84% | +3.37 pp | 895/1141 = 78.440% |

This aggregate similarity results from model-level cancellation and should not be interpreted as a direction-invariant mechanism.

## Conclusion

The Chinese-to-Japanese Translation Type-1 column is closely reproduced for six accessible checkpoints, and the main homograph-error concentration and scoring-length pattern replicate in both directions. The evidence is sufficient to freeze the bidirectional Translation Type-1 milestone and move to the contextualized phrase-retrieval baseline.

The broader paper remains only partially reproduced. Independent bilingual labels, alternative-task replication, and access to Llama 3.1 remain explicit limitations.
