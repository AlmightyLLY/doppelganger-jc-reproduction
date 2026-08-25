# EXP-20260825 — Preregistration: Chinese-to-Japanese Translation Type-1

## Objective

Reproduce the Chinese-to-Japanese Translation Type-1 column from Doppelganger-JC Table 3 using the complete official question set and full-prompt PPL rule. Candidate-only NLL is retained as a diagnostic and is not reported as the paper metric.

## Frozen data and scoring

- Dataset: `questions.zh_jp.homographs.dataset`, 455 questions
- Prompt: `“{original}”という中国語の文章の日本語訳は「{candidate}」です。`
- Official: mean NLL across all predictable prompt tokens; select minimum PPL
- Candidate-only: mean NLL over candidate Japanese translation tokens in the same forward pass
- Strict set: all 455 questions
- Audited set: 454 after excluding item 439, where `wrong1` and `wrong2` are identical
- The nine cognate-list entries without questions are not synthesized or added

## Paper values frozen before execution

| Model | Type-1 accuracy | `wrong1` share of errors |
|---|---:|---:|
| llm-jp-3-7.2b-instruct3 | 65.49% | 67.84% |
| Llama-3-ELYZA-JP-8B | 60.44% | 74.53% |
| Qwen2.5-7B-Instruct-1M | 64.18% | 81.44% |
| Baichuan2-7B-Base | 58.90% | 71.91% |
| Llama-3.1-8B-Instruct | 70.55% | 65.53% |
| Gemma-7B | 60.00% | 78.25% |
| Mistral-7B-Instruct-v0.2 | 41.32% | 75.10% |

Source: [Doppelganger-JC](https://aclanthology.org/2025.ijcnlp-long.96/).

## Frozen checkpoints

| Model | Revision | Preflight |
|---|---|---|
| `llm-jp/llm-jp-3-7.2b-instruct3` | `cdd4c7f3296fdc7785423a864bd9a86ce4c15915` | Passed |
| `elyza/Llama-3-ELYZA-JP-8B` | `e6c316496ee7d9a11710c50229e8cb39b6b0a4a3` | Passed |
| `Qwen/Qwen2.5-7B-Instruct-1M` | `e28526f7bb80e2a9c8af03b831a9af3812f18fba` | Passed |
| `baichuan-inc/Baichuan2-7B-Base` | `f9d4d8dd2f7a3dbede3bda3b0cf0224e9272bbe5` | Passed |
| `meta-llama/Llama-3.1-8B-Instruct` | unavailable | Access denied; no substitution allowed |
| `google/gemma-7b` | `ff6768d9368919a1f025a54f9f5aa0ee591730bb` | Passed |
| `mistralai/Mistral-7B-Instruct-v0.2` | `63a8b081895390a26e140280378bc85ec8bce07a` | Passed |

## Data audit frozen before execution

- Cognate-list entries: 464
- Translation questions: 455
- Missing questions: 9 (identities available after joining to the pinned upstream data)
- Extra questions: 0
- Missing fields: 0
- Duplicate question keys: 0
- Duplicate-option questions: 1

## Execution and acceptance

1. Run a two-item local CPU smoke test with Qwen2.5-0.5B.
2. Run accessible checkpoints sequentially on one RunPod A40 48 GB.
3. Cache one model at a time and clear it after verified download of outputs.
4. Require 455 rows with indices 0–454, one revision, finite losses/PPLs, and choices equal to `argmin(PPL)`.
5. Preserve JSONL, summary, full log, diagnostic JSON, and SHA-256 externally.
6. Delete the Pod after completion or the cost guard and verify zero GPU compute spend.

## Preregistered comparisons

- strict and audited official accuracy versus the paper;
- `wrong1` share of errors versus the paper;
- official versus candidate-only accuracy, agreement, and complementary correct sets;
- token-length direction when the scores disagree;
- cross-model overlap, common errors, and unique correct items;
- within-model direction differences versus the completed Japanese-to-Chinese results.

Post-result explanatory analyses must be labeled separately from these confirmatory comparisons.
