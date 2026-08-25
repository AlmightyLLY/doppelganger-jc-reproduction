# EXP-20260825 — Japanese-to-Chinese Translation Type-1 Six-Model Synthesis

## Scope

This report covers the 462-item Japanese-to-Chinese Translation Type-1 slice of Doppelganger-JC. Complete outputs were obtained for six of the seven checkpoints listed in the paper:

1. `Qwen/Qwen2.5-7B-Instruct-1M`
2. `llm-jp/llm-jp-3-7.2b-instruct3`
3. `elyza/Llama-3-ELYZA-JP-8B`
4. `baichuan-inc/Baichuan2-7B-Base`
5. `mistralai/Mistral-7B-Instruct-v0.2`
6. `google/gemma-7b`

`meta-llama/Llama-3.1-8B-Instruct` was not run because gated access was denied. Additional Qwen2.5 0.5B and standard 7B runs were used only as diagnostics and are not included in the six-model paper comparison.

## Summary

- All six official accuracies were within approximately two percentage points of the paper values. The maximum absolute difference was 1.95 points for Baichuan; the mean absolute difference was approximately 0.79 points.
- The homograph-based `wrong1` option accounted for 69.5%–85.3% of each model's official errors.
- Official and candidate-only scoring disagreed 373 times. In 352 of these cases (94.4%), the official score selected the candidate with more tokens.
- Candidate-only accuracy exceeded official accuracy only for Qwen-1M, but every model had items that were correct only under candidate-only scoring. It is therefore retained as a diagnostic rather than promoted as a replacement metric.
- Higher aggregate accuracy did not imply item-level containment: every model pair had nonzero correct-only items in both directions.
- A subsequent target-kana intervention showed that visible target orthography affects correct-versus-`wrong1` preference, while final accuracy effects remain model-dependent.

## Data audit

The official cognate list contains 464 entries, while the translation file contains 462 questions. The missing word pairs are:

- `低下 → 低下`
- `論調 → 论调`

Three questions contain duplicate options:

- `果子`: `wrong2` and `wrong3` are identical;
- `前年`: `correct` and `wrong1` are identical;
- `顾客`: `correct` and `wrong1` are identical.

Two evaluation views are retained:

- **strict**: all 462 official questions, used for paper comparison;
- **audited**: 459 questions after excluding the three duplicate-option items.

Excluding the three items changes no substantive six-model conclusion. Their presence nevertheless shows why later human evaluation should allow multiple acceptable answers when warranted.

## Scoring definitions

For candidate `i`, let `C,K` be the accumulated NLL and token count of the shared prompt portion, and `S_i,L_i` those of the candidate translation span:

```text
official(i)       = (C + S_i) / (K + L_i)
candidate-only(i) = S_i / L_i
```

Both scores use the complete source sentence and prompt. Candidate-only is not a no-context or human condition; it changes only which token losses are averaged for the final ranking.

The paper's official score is the primary reproduction metric. Candidate-only is used to diagnose sensitivity to the shared prompt and length normalization.

## Aggregate reproduction

| Model | Paper official | Reproduced official | Difference | Wilson 95% interval | Candidate-only |
|---|---:|---:|---:|---:|---:|
| Qwen2.5-7B-Instruct-1M | 69.70% | 316/462 = 68.40% | −1.30 pp | 64.02%–72.47% | 322/462 = 69.70% |
| llm-jp-3-7.2b-instruct3 | 58.23% | 272/462 = 58.87% | +0.64 pp | 54.33%–63.27% | 240/462 = 51.95% |
| Llama-3-ELYZA-JP-8B | 52.81% | 244/462 = 52.81% | 0.00 pp | 48.26%–57.32% | 223/462 = 48.27% |
| Baichuan2-7B-Base | 61.69% | 276/462 = 59.74% | −1.95 pp | 55.21%–64.11% | 271/462 = 58.66% |
| Mistral-7B-Instruct-v0.2 | 49.78% | 233/462 = 50.43% | +0.65 pp | 45.89%–54.97% | 205/462 = 44.37% |
| Gemma-7B | 61.04% | 281/462 = 60.82% | −0.22 pp | 56.30%–65.17% | 272/462 = 58.87% |

ELYZA exactly matches the paper's aggregate count, but paper-released item-level outputs are unavailable, so item-level identity cannot be claimed. Small deterministic differences are more plausibly related to model revisions, software versions, tokenizer behavior, precision, data versions, or undocumented implementation details than to random seeds.

## Error distribution and scoring sensitivity

| Model | `wrong1` / official errors | Official/candidate agreement | Disagreements | Official-only correct | Candidate-only-only correct | Official near-ties |
|---|---:|---:|---:|---:|---:|---:|
| Qwen-1M | 121/146 = 82.9% | 425/462 = 92.0% | 37 | 15 | 21 | 52 |
| llm-jp | 132/190 = 69.5% | 393/462 = 85.1% | 69 | 44 | 12 | 92 |
| ELYZA | 186/218 = 85.3% | 386/462 = 83.5% | 76 | 46 | 25 | 94 |
| Baichuan | 158/186 = 84.9% | 425/462 = 92.0% | 37 | 18 | 13 | 115 |
| Mistral | 160/229 = 69.9% | 394/462 = 85.3% | 68 | 38 | 10 | 123 |
| Gemma | 145/181 = 80.1% | 376/462 = 81.4% | 86 | 39 | 30 | 80 |

A near-tie is defined as a relative PPL difference below 5% between the first- and second-ranked options. Candidate-only produced fewer near-ties for every model, consistent with the shared prompt compressing relative differences. Near-ties are potential reliability features, not calibrated probabilities of semantic uncertainty.

## Cross-model structure

Across official predictions:

- 94 items were correct for all six models;
- 40 items were wrong for all six models;
- 114/462 items received exactly the same option from all six models;
- 20 items were assigned `wrong1` by all six models.

The number of correct models per item was:

| Correct models | Items |
|---:|---:|
| 0 | 40 |
| 1 | 51 |
| 2 | 55 |
| 3 | 71 |
| 4 | 71 |
| 5 | 80 |
| 6 | 94 |

Selected pairwise comparisons illustrate non-containment:

| Model pair | Same option | First-only correct | Second-only correct |
|---|---:|---:|---:|
| Qwen / Mistral | 57.4% | 127 | 44 |
| Qwen / Gemma | 68.8% | 82 | 47 |
| llm-jp / ELYZA | 60.8% | 92 | 64 |
| Baichuan / Gemma | 68.4% | 60 | 65 |
| Mistral / Gemma | 53.7% | 68 | 116 |

Aggregate model strength therefore reflects lower average error, not a strict superset of item-level capabilities.

## Candidate-length effect

Among the 373 official-versus-candidate-only disagreements:

```text
official selected the longer-token candidate: 352 (94.4%)
official selected an equal-length candidate:    17 (4.6%)
official selected the shorter-token candidate:   4 (1.1%)
```

This is not direct evidence that the model blindly chooses longer translations. The official formula averages shared-prompt and candidate loss together, so candidate length changes how the common loss is diluted.

The correct option was also longer on average than `wrong1` under all six tokenizers:

| Tokenizer | Correct mean tokens | `wrong1` mean tokens |
|---|---:|---:|
| Qwen-1M | 8.48 | 8.18 |
| llm-jp | 12.23 | 11.21 |
| ELYZA | 11.26 | 10.44 |
| Baichuan | 7.65 | 7.37 |
| Mistral | 14.92 | 13.62 |
| Gemma | 9.02 | 8.51 |

The official score's higher accuracy may therefore partly reflect alignment between its length tendency and dataset construction. A length-matched semantic control is required before preferring one scoring rule on semantic grounds.

## Human-review evidence

The first 34 items from a 67-item three-model shared-error subset were reviewed. This was a deliberately difficult `unanimous_wrong1` subset, not a random sample of all 462 questions.

- human preferred `correct`: 26 items;
- human preferred `wrong1`: 6 items;
- both considered acceptable: 2 items;
- 27/34 remained unanimous `wrong1` under candidate-only scoring.

The review separated clear form-copy errors from fluent or semantically defensible alternatives. It supports the reality of homograph attraction while also documenting label ambiguity. Independent bilingual annotation is still required before treating these judgments as a gold standard.

## Orthography extension

The initial Qwen target-kana experiment produced a target-versus-unrelated-control margin effect of `+0.121`, paired bootstrap 95% CI `[+0.047, +0.198]`. The later six-model replication is reported separately in [EXP-20260825-orthography-six-model-replication.md](EXP-20260825-orthography-six-model-replication.md).

The intervention supports a causal contribution of visible orthography to correct-versus-`wrong1` preference under the frozen design. It does not show that kana normalization improves accuracy generally or that the model internally skips semantic processing.

## Conclusion

The Japanese-to-Chinese Translation Type-1 aggregate results are successfully reproduced for the six accessible paper checkpoints. The reproduction also reveals two issues that matter beyond aggregate accuracy: homographic distractors attract a large and stable share of errors, and the paper score has a strong structural association with candidate token length.

The evidence motivates selective, reliability-aware use of orthographic information rather than universal normalization. External replication, independent bilingual labels, and a downstream retrieval evaluation remain necessary.
