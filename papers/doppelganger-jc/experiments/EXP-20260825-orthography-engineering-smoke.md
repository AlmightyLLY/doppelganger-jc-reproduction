# EXP-20260825 — Five-Item Kana Intervention Engineering Smoke Test

## Purpose

This development-only run verified three-condition scoring and effect computation. With five items, it is not used for significance testing or population-level causal claims.

## Configuration

- Model: `Qwen/Qwen2.5-7B-Instruct-1M`
- Revision: `e28526f7bb80e2a9c8af03b831a9af3812f18fba`
- Hardware: NVIDIA A40 48 GB, BF16
- Items: first five rows of the frozen 30-item table, not selected by outcome
- Conditions: original, target-kana, and control-kana
- Primary score: candidate-only mean NLL
- Material SHA-256: `fb6a669bb050f6ff3adc13b1184d4d5dbc7bbeb61d4177e06eb76df196d3d4c6`

## Materials

The development items were indices 4, 9, 33, 82, and 87 of the pinned
Japanese-to-Chinese question set. Benchmark sentences and rewritten variants
are not redistributed in this public repository; the material builder
reconstructs them locally.

A single post-result material review judged the readings and sentence meanings acceptable for these five items. Because Japanese kana can introduce homophone ambiguity, this review does not validate the broader material. These items remained a development set and were not reintroduced as blind confirmatory data.

## Metric

```text
margin = NLL(wrong1) - NLL(correct)
orthography_effect = [margin(target_kana) - margin(original)]
                    - [margin(control_kana) - margin(original)]
```

## Results

| Item | Original | Target-kana | Control-kana | Target effect | Control effect | Orthography effect |
|---|---:|---:|---:|---:|---:|---:|
| 4 | 2.258 | 3.160 | 2.288 | +0.902 | +0.030 | +0.872 |
| 9 | 0.788 | 0.300 | 0.812 | −0.488 | +0.025 | −0.512 |
| 33 | 2.372 | 2.785 | 2.233 | +0.413 | −0.140 | +0.553 |
| 82 | 0.556 | 0.621 | 0.634 | +0.065 | +0.078 | −0.013 |
| 87 | −0.137 | −0.849 | −0.479 | −0.712 | −0.343 | −0.370 |

- Mean effect: +0.106
- Median effect: −0.013
- Positive / negative items: 2 / 3
- Final choices: four correct and one `wrong1` in every condition; no discrete transition
- Official and candidate-only choices agreed in all 15 item–condition observations

The run established that the implementation worked and that continuous margins were more sensitive than final choices. It did not support a universal kana benefit.

## Validation and cost

- Result JSONL SHA-256: `2e24a2a6097ade8be6babac8a25fbb6bb88d013e43dbb8489931081d1e505db9`
- Summary SHA-256: `cc197a5950f4da445c83d4d486f185689bc5768e90c765ba69ccfdcb393a98f5`
- Approximate A40 cost: `$0.0314`
- Pod deleted after remote and local validation
