# Six-Model Replication of the Kana Orthography Effect

## Main results

| Model | Mean orthography effect [95% CI] | Positive/negative items | Original acc. | Target acc. | Δacc. |
|---|---:|---:|---:|---:|---:|
| `Qwen/Qwen2.5-7B-Instruct-1M` | +0.121 [+0.047, +0.198] | 217/165 | 69.4% | 65.4% | -3.9% |
| `llm-jp/llm-jp-3-7.2b-instruct3` | -0.037 [-0.076, +0.003] | 186/196 | 51.6% | 47.6% | -3.9% |
| `elyza/Llama-3-ELYZA-JP-8B` | +0.076 [+0.030, +0.122] | 234/148 | 47.6% | 46.1% | -1.6% |
| `baichuan-inc/Baichuan2-7B-Base` | +0.311 [+0.260, +0.363] | 291/91 | 59.4% | 70.7% | +11.3% |
| `mistralai/Mistral-7B-Instruct-v0.2` | +0.225 [+0.173, +0.279] | 253/129 | 43.7% | 53.1% | +9.4% |
| `google/gemma-7b` | +0.117 [+0.062, +0.172] | 227/155 | 58.4% | 58.1% | -0.3% |

## Fixed six-model-set summary

After averaging across models within each item and bootstrapping the 382 items:
**+0.136 [+0.100, +0.173]**. Five of six model means were positive, and five
intervals were entirely above zero.

This describes the fixed model set and is not a random-effects inference to all
language models.

## Directional consistency

| Models with positive effect | Items |
|---:|---:|
| 0 | 9 |
| 1 | 33 |
| 2 | 53 |
| 3 | 74 |
| 4 | 76 |
| 5 | 79 |
| 6 | 58 |

## Interpretation boundary

- The primary continuous effect compares candidate-only mean NLL for `correct`
  and `wrong1`; it is not a four-option accuracy gain.
- Reusing the same source-only controls across models weakens a single-model
  explanation but does not remove limitations in control naturalness or
  semantic independence.
- Model–item rows are not independent; the cross-model interval first averages
  models within item and then bootstraps items.
- Model heterogeneity, choice transitions, and tokenization are diagnostics and
  do not supersede the preregistered primary analysis.
