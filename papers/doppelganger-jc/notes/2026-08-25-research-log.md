# Research Log — 2026-08-25

## Objectives

1. Continue the exact-checkpoint reproduction and assess deviations from the paper.
2. Distinguish clear model errors from ambiguous benchmark labels through manual review.
3. Turn `wrong1` concentration into a testable orthographic-intervention question.
4. Define a more precise reliability-aware research direction.

## Work completed

- Reviewed 34 shared `wrong1` errors and recorded preferred candidates and issue categories.
- Distinguished clear form copying from fluent, ambiguous, or label-sensitive alternatives.
- Revised the control logic for the kana intervention so that the primary control is semantically unrelated to the target.
- Completed and validated Baichuan, Mistral, and Gemma Japanese-to-Chinese runs.
- Completed a five-item engineering smoke test, the full Qwen negative-control analysis, and preparation for the five-model replication.
- Preserved access failures, smoke-test failures, revisions, checksums, and resource-cleanup records.

## Additional model results

| Model | Paper official | Reproduced official | Candidate-only | `wrong1` / official errors |
|---|---:|---:|---:|---:|
| Baichuan2-7B-Base | 61.69% | 276/462 = 59.74% | 58.66% | 158/186 = 84.9% |
| Mistral-7B-Instruct-v0.2 | 49.78% | 233/462 = 50.43% | 44.37% | 160/229 = 69.9% |
| Gemma-7B | 61.04% | 281/462 = 60.82% | 58.87% | 145/181 = 80.1% |

Baichuan had the largest six-model paper difference at −1.95 percentage points in this direction. Mistral and Gemma closely matched the paper aggregates. Llama 3.1 remained unavailable because its gated-access request was denied.

## Manual review

The 34 reviewed items are a targeted unanimous-`wrong1` subset, not a random sample.

- 17/34 were marked shortcut-related;
- 19/34 involved ambiguity, multiple acceptable answers, or a label boundary;
- preferred candidate 0: 26;
- preferred `wrong1`: 6;
- both acceptable: 2;
- 27/34 remained unanimous `wrong1` under candidate-only scoring.

This supports the coexistence of genuine form-copy errors and benchmark-label limitations.

## Five-item development run

```text
margin = NLL(wrong1) - NLL(correct)
orthography_effect = target_effect - control_effect
```

| Target | Original margin | Target-kana | Control-kana | Effect |
|---|---:|---:|---:|---:|
| 大变 | 2.258 | 3.160 | 2.288 | +0.872 |
| 新闻 | 0.788 | 0.300 | 0.812 | −0.512 |
| 邪魔 | 2.372 | 2.785 | 2.233 | +0.553 |
| 改正 | 0.556 | 0.621 | 0.634 | −0.013 |
| 东洋 | −0.137 | −0.849 | −0.479 | −0.370 |

The mean effect was +0.106 and the median −0.013. No final option changed. The mixed directions showed that a control condition and continuous margin were necessary, and the five exposed items were retained only as development data.

## Full Qwen intervention

Of 462 original questions, 450 supported an unrelated control. The primary set contained 382 items after excluding 35 exposed development items and 33 weak controls.

- Target-versus-unrelated mean effect: `+0.121`
- Paired bootstrap 95% CI: `[+0.047, +0.198]`
- Unrelated-control mean change: `+0.017`, CI `[−0.012, +0.045]`
- Original correct: 265/382
- Target-kana correct: 250/382
- `wrong2/3` selections: 23 → 44

The intervention weakened `wrong1` relative to `correct` but did not improve final accuracy. Visible form therefore acts as both a potentially misleading shortcut and useful lexical evidence.

## Refined research hypothesis

A static instruction to always suppress form similarity is not supported. A more defensible system would:

1. generate a form-derived lexical proposal;
2. independently estimate context-based semantics;
3. compare the two paths;
4. accept the shortcut when estimated reliability is high;
5. trigger retrieval, semantic verification, or abstention when reliability is low.

Character-level decomposition may provide a prior, but context must update that prior when lexicalization or semantic drift makes literal interpretation unreliable.

## Evidence boundary

- The manual subset cannot estimate full-dataset shortcut or ambiguity rates.
- The linguistic judgments are primarily single-annotator development labels.
- Candidate-only margin is not a calibrated reliability probability.
- The Qwen intervention supports a target-specific preference effect, not the claim that orthography is the unique or strongest factor.
- The five-item material review occurred after outcomes were visible and remains development-only.

## Next action

Reuse the frozen material and analysis rules on the remaining five models without altering controls in response to results. Review blinded transition types separately: `wrong1→correct`, `correct→wrong2/3`, and large continuous effects without a final-choice change.
