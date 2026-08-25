# EXP-20260824 — Initial Three-Model Japanese-to-Chinese Reproduction

## Status and scope

- Status: completed and validated
- Dates: 2026-08-23 to 2026-08-24 (Asia/Tokyo)
- Task: Doppelganger-JC Japanese-to-Chinese Translation Type-1
- Items: 462
- Primary metric: official full-prompt PPL
- Diagnostic metric: candidate-only mean NLL
- Hardware: RunPod Secure Cloud, NVIDIA A40 48 GB, BF16
- Environment: Python 3.11.10, PyTorch 2.5.1+cu121, Transformers 4.48.3, Accelerate 1.3.0

This record captures the first three exact paper checkpoints. The later six-model synthesis supersedes it for final comparisons.

## Questions

1. Are the reproduced official accuracies close to the paper values?
2. Do official and candidate-only scoring produce systematic choice differences?
3. Are errors concentrated on the homograph-based `wrong1` candidate?
4. Does aggregate model ranking imply item-level capability containment?

## Data audit

- Cognate-list entries: 464
- Translation questions: 462
- Missing pairs: `低下/低下` and `論調/论调`
- Duplicate-option items: `果子`, `前年`, and `顾客`
- Strict set: 462; audited set: 459

The official data were not silently modified.

## Results

| Model | Paper official | Reproduced official | Difference | Candidate-only |
|---|---:|---:|---:|---:|
| Qwen2.5-7B-Instruct-1M | 69.70% | 316/462 = 68.40% | −1.30 pp | 322/462 = 69.70% |
| llm-jp-3-7.2b-instruct3 | 58.23% | 272/462 = 58.87% | +0.64 pp | 240/462 = 51.95% |
| Llama-3-ELYZA-JP-8B | 52.81% | 244/462 = 52.81% | 0.00 pp | 223/462 = 48.27% |

The official ranking matches the paper. ELYZA matches the aggregate paper count, but item-level identity cannot be claimed because the paper does not release corresponding predictions.

Machine-readable summary: [three-model CSV](../../../results/EXP-20260824-jp-zh-type1-three-models.csv).

## Scoring diagnostics

| Model | Choice agreement | Disagreements | Official chose longer | Official near-ties | Candidate-only near-ties |
|---|---:|---:|---:|---:|---:|
| Qwen-1M | 425/462 = 92.0% | 37 | 34 | 52 | 24 |
| llm-jp | 393/462 = 85.1% | 69 | 68 | 92 | 36 |
| ELYZA | 386/462 = 83.5% | 76 | 72 | 94 | 37 |

The official score almost always selected the longer-token candidate when the two rules disagreed. Candidate-only is an evaluation ablation, not a human or no-context condition.

## `wrong1` concentration

| Model | Official errors | `wrong1` selections | Share of errors |
|---|---:|---:|---:|
| Qwen-1M | 146 | 121 | 82.9% |
| llm-jp | 190 | 132 | 69.5% |
| ELYZA | 218 | 186 | 85.3% |

The concentration is consistent with homograph attraction, but candidate naturalness, frequency, length, and label quality remain alternative explanations.

## Item-level overlap

- All three correct: 155 items
- All three wrong: 67 items
- Identical option across all three: 202/462
- Shared `wrong1` among jointly wrong items: 43
- At least one candidate-only recovery among the 67: 9

ELYZA solved 20 items that both higher-scoring models missed. Aggregate accuracy therefore does not define a strict item-level capability superset.

The 67-item review packet contains benchmark text and remains in the local
research workspace. Public aggregate judgments and item indices are recorded in
the corresponding research note.

## Validation

Every formal output had 462 consecutive indices, one fixed model revision, finite PPL values, and choices equal to the four-option PPL argmin. Remote and local SHA-256 values matched.

| Model | Revision | JSONL SHA-256 | Summary SHA-256 |
|---|---|---|---|
| Qwen-1M | `e28526f7bb80e2a9c8af03b831a9af3812f18fba` | `47b5cb306bfee2fa4ad793255d8d4d599b6fdb2bbada610f09120c65e4d9f130` | `abf60520281686a933da3daa984d3efda29310dea921d9999073206d23532f26` |
| llm-jp | `cdd4c7f3296fdc7785423a864bd9a86ce4c15915` | `fac083e092155d7879a1671c334917453f5a2969d747c892b2d96f9106f46254` | `92c61ef14e1a25152124fe7a021a9e838341df126cabb1d304796f94eec10d6b` |
| ELYZA | `e6c316496ee7d9a11710c50229e8cb39b6b0a4a3` | `caed63e1d41506010dd2647386f2ad769b4dbe9be8551ed3f6b97d1615c8c6ac` | `868e96463f1f1d0f701c5270ece6c4c8625767db1736ce811d3cfd3f6fd23a3d` |

## Evidence boundary

The three aggregate results are closely reproduced, and both `wrong1` concentration and scoring-length sensitivity appear across models. This record does not establish a complete-paper reproduction, a causal orthographic mechanism, or the superiority of candidate-only scoring.
