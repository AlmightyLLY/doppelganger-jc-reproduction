# EXP-20260825 — Mistral-7B-Instruct-v0.2 Japanese-to-Chinese Translation Type-1

## Configuration

- Status: completed and validated
- Model: `mistralai/Mistral-7B-Instruct-v0.2`
- Revision: `63a8b081895390a26e140280378bc85ec8bce07a`
- Task: Japanese-to-Chinese Translation Type-1, 462 items
- Paper official accuracy: 49.78%
- Paper `wrong1` share of errors: 68.23%
- Primary score: official full-prompt PPL
- Environment: NVIDIA A40 48 GB, BF16, Python 3.11.10, PyTorch 2.5.1+cu121, Transformers 4.48.3

The strict set retains 462 questions. The audited set excludes the three known duplicate-option items.

## Results

| View | Paper | Reproduced | Difference |
|---|---:|---:|---:|
| Strict official | 49.78% | 233/462 = 50.43% | +0.65 pp |
| Audited official | — | 230/459 = 50.11% | — |
| Strict candidate-only | — | 205/462 = 44.37% | — |
| Audited candidate-only | — | 203/459 = 44.23% | — |
| `wrong1` / official errors | 68.23% | 160/229 = 69.87% | +1.64 pp |

The strict official result differs by three questions. Its Wilson 95% interval, 45.89%–54.97%, contains the paper value.

## Scoring diagnostics

- Official/candidate-only agreement: 394/462 = 85.28%
- Both correct: 195
- Official-only correct: 38
- Candidate-only-only correct: 10
- Both wrong: 219
- Official choice counts: `[233, 160, 41, 28]`
- Candidate-only choice counts: `[205, 194, 35, 28]`
- Among 68 disagreements, official chose the longer candidate 64 times, equal length 3 times, and shorter once
- Near-ties: 123 official versus 52 candidate-only

Candidate-only is retained as a scoring diagnostic. Its lower accuracy does not by itself validate the official score semantically.

## Comparison with Qwen-1M

- Qwen official: 316/462 = 68.40%
- Mistral official: 233/462 = 50.43%
- Mistral-only correct: 44
- Qwen-only correct: 127
- Exact paired McNemar p: `1.57e-10`
- Same option: 265/462 = 57.4%

Mistral is substantially lower in aggregate but still has 44 unique correct items, again showing that total accuracy does not imply strict capability containment.

## Validation and artifacts

The smoke and formal outputs were isolated. The formal JSONL contained 462 consecutive items, one revision, finite PPL values, and argmin-consistent choices. Remote and local hashes matched.

| Artifact | SHA-256 |
|---|---|
| JSONL | `a05542eaffbfaf01201244598a7a5eff9dd05b8368dcb1c3420cfce5bdf2dd41` |
| Summary | `a39456faa7dabbeea6d6206aade050c0be95206a33cd7335fe1fbaeecec5d670` |
| Diagnostics | `dc81e58526b0a01bf39e023113454c077c3cf8249c165e4774c39f8ca5e18f7d` |
| Log | `a7343a333776c226ff0d599799563cc1300d93aa41a6a73adac6c03192f3a195` |

Compact summary: [Mistral CSV](../../../results/EXP-20260825-jp-zh-type1-mistral.csv).

The approximate balance change was `$0.0663`. The A40 Pod was deleted after verification; the pre-existing network volume was retained.
