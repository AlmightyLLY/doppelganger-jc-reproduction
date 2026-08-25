# EXP-20260825 — Full Qwen Target-Kana and Negative-Control Experiment

## Question and configuration

Does removing visible kanji overlap from the Japanese target homograph reduce the Chinese `wrong1` preference more than kana-converting an unrelated source component?

- Model: `Qwen/Qwen2.5-7B-Instruct-1M`
- Revision: `e28526f7bb80e2a9c8af03b831a9af3812f18fba`
- Score: candidate-only mean NLL
- Frozen material SHA-256: `fa19564838ab4d86f8ecda1a08daf9e792e3d576734138927f2b569ef933b4c9`
- Runnable unrelated controls: 450/462
- Items with an additional related control: 411/462
- Primary set: 382 items after excluding 35 development items and 33 weak controls

## Conditions and metric

1. `original`
2. `target_kana`
3. `unrelated_control_kana`
4. exploratory `related_semantic_cue_kana`, where available

```text
margin = NLL(wrong1) - NLL(correct)
orthography_effect = margin(target_kana) - margin(unrelated_control_kana)
```

A positive effect favors `correct` over `wrong1` after subtracting generic kana rewriting. It is not equivalent to a four-option accuracy difference.

## Primary results

| Condition | Correct | `wrong1` | `wrong2` | `wrong3` | Mean margin |
|---|---:|---:|---:|---:|---:|
| Original | 265 | 94 | 12 | 11 | 0.612 |
| Target-kana | 250 | 88 | 26 | 18 | 0.750 |
| Unrelated control | 260 | 97 | 14 | 11 | 0.629 |

| Continuous effect | Mean | Median | Paired bootstrap 95% CI |
|---|---:|---:|---:|
| Target − original | +0.138 | +0.135 | [+0.061, +0.215] |
| Unrelated − original | +0.017 | +0.009 | [−0.012, +0.045] |
| Target − unrelated | **+0.121** | **+0.080** | **[+0.047, +0.198]** |

The direction was stable in high-only, weak-control-inclusive, all-runnable, and trimmed-mean sensitivity analyses. The correlation between the target–control token-count difference and the primary effect was −0.030, so simple token-count change does not explain the average effect.

## Accuracy redistribution

Target-kana accuracy fell from `265/382 = 69.4%` to `250/382 = 65.4%`: 37 wrong predictions became correct, while 52 correct predictions became wrong. `wrong2` and `wrong3` selections increased from 23 to 44.

The positive margin and lower accuracy are compatible. The intervention weakens some homograph attraction while also removing lexical-identification and orthographic-disambiguation evidence, allowing other distractors to win.

## Control interpretation

On the 365-item four-condition subset, the mean absolute margin perturbation was 0.189 for the unrelated control and 0.224 for the related semantic control. Their paired difference was +0.035, with 95% CI `[+0.004, +0.068]`. The unrelated control is therefore retained as the primary negative control; the related condition is better interpreted as semantic-cue ablation.

## Evidence boundary

Supported under this model and frozen design:

- visible target-word orthography contributes to correct-versus-`wrong1` preference;
- the mean effect is not explained by unrelated kana rewriting or token-count increase alone.

Not supported:

- universal accuracy improvement from kana conversion;
- complete bilingual validation of all automatic controls;
- an internal process in which the model literally skips semantics;
- cross-model generalization, which was tested only in the subsequent replication.

## Review and artifacts

The local 30-item blinded diagnostic package contains 10 `wrong1→correct`, 10
`correct→wrong2/3`, and 10 large continuous-effect items without a final-choice
change. Because selection uses observed outcomes, it is for mechanism review
rather than population-rate estimation. The packet contains benchmark text and
is therefore not redistributed in the public repository.

| Artifact | SHA-256 |
|---|---|
| Complete local result JSONL | `263cf38022ccda82755776e2084faed7426916f21b119675bc294b43f08be6ca` |
| Complete local summary | `f5c2c1939f18bf63fe5d70a28a73096ca7952d92d9c4b055ba1b9ccb2d5235aa` |
| Complete local diagnostics | `3e4477eb4266b775cc78fcfdf8b8b9f3fefa99a3a6fc9e07708b204bcd2dedb9` |

Execution used an A40 48 GB GPU, BF16, PyTorch `2.4.1+cu124`, Transformers `4.48.3`, and Accelerate `1.3.0`. Results were independently recomputed and verified locally before Pod deletion.
