# Research Log — 2026-08-30

## 1. Objective

Today's objective was to test whether the interaction observed in the exposed 13-item development factorial would transfer to new lexical groups selected without using Qwen3 outcomes.

The two questions were:

1. On strict unsafe items, does removing the visible Japanese homograph improve the correct-versus-form-derived Chinese preference when a contextual semantic gloss is available?
2. Can one fixed branch—target-form kana replacement plus the gloss—improve candidate accuracy over the original source without materially harming form-reliable controls?

The experiment was explicitly not a router test. It also did not evaluate free generation, another model, another language pair, or an internal mechanism.

## 2. What was completed

I specified and authorized a result-blind external-validation protocol with fixed composition, exclusions, metrics, forecasts, stopping rules, and a USD 1.00 active-compute ceiling.

The engineering and material-construction workflow then:

- built a broad pool from 1,017 historical manual PIC-3Cue seeds;
- excluded components overlapping prior exposed development and calibration material;
- performed two separately recorded result-blind AI linguistic passes;
- froze 30 strict-unsafe and 20 form-reliable-control items in 50 distinct components;
- constructed six factorial conditions per item;
- checked gloss leakage, source interventions, candidate carriers, token boundaries, and length sensitivity;
- hash-froze the material, numerical forecasts, metrics, and decision gates before inference;
- ran exactly one Qwen3-8B inference attempt and independently reconstructed the results;
- stopped and rechecked the GPU Pod automatically.

The annotation status is deliberately limited to `AI_CURATED_RESULT_BLIND_EXTERNAL_VALIDATION`. These items are not human-confirmed gold, native-speaker adjudication, or independent double-human annotation.

## 3. Main results

The frozen primary score was complete-candidate teacher-forced mean NLL.

| Condition | All 50 | Unsafe 30 | Reliable 20 |
|---|---:|---:|---:|
| Original form, no gloss (`F0G0`) | 46/50 | 26/30 | 20/20 |
| Original form, gloss (`F0G1`) | 48/50 | 28/30 | 20/20 |
| Target kana, no gloss (`F1G0`) | 47/50 | 27/30 | 20/20 |
| Target kana, gloss (`F1G1`) | 49/50 | 29/30 | 20/20 |
| Unrelated kana, no gloss (`U1G0`) | 46/50 | 26/30 | 20/20 |
| Unrelated kana, gloss (`U1G1`) | 48/50 | 28/30 | 20/20 |

Relative to the original baseline, `F1G1` produced three unsafe rescues and no harms. The paired accuracy gain was `+3/50 = +6` percentage points, with a 10,000-resample item-bootstrap 95% interval of `[0, +14]` points and an exact two-sided McNemar `p = 0.25`. The discrete gain is favorable but is not statistically decisive on its own.

The stronger result was the preregistered continuous unsafe effect. Target-form removal with the gloss improved the correct-versus-form-derived margin on 22/30 items. Its mean was `+0.240`, median `+0.239`, and bootstrap 95% interval `[+0.021, +0.460]`. After subtracting the unrelated-kana effect, 22/30 items remained positive, with mean `+0.303`, median `+0.388`, and interval `[+0.060, +0.534]`.

The unrelated intervention did not reproduce the target-form effect. Raw-sequence and lexical-span diagnostics had positive medians, so the frozen scientific direction was not reversed by both secondary scoring definitions.

## 4. The most important interpretation update

The result does not support universal orthographic suppression.

On unsafe items, removing the potentially misleading form became useful when semantic information was supplied. On form-reliable controls, however, the same removal reduced the correct-candidate margin on 18/20 items even though no final choice became wrong. The control accuracy was already 100%, so the absence of discrete harm partly reflects a ceiling.

The most defensible interpretation is therefore:

> Orthographic overlap is useful but fallible evidence. Semantic clarification can compensate when the form is removed, while reliable form overlap still contributes measurable preference strength.

This is aligned with a reliability-aware research question, but it does not yet validate a reliability estimator or router.

## 5. Why the factorial design mattered

The six conditions separated effects that the fixed branch alone would have mixed together:

- gloss alone rescued two baseline errors;
- kana removal alone rescued three errors but harmed two previously correct items;
- kana plus gloss kept all three rescues and removed the two kana-only harms;
- unrelated kana plus gloss matched gloss alone at 48/50.

Therefore only one of the three discrete `F0G0 → F1G1` rescues was an additional target-form correction beyond the gloss branch. The broader form-specific evidence comes from the continuous target-versus-control contrasts, not merely the final accuracy difference.

## 6. Robustness checks

Four items were scoring-sensitive. After excluding all four, accuracy still moved from 43/46 to 45/46, with two rescues and no harms. The unsafe continuous effect remained positive on 20/28 scoring-stable items.

The fixed-method gain also appeared in both length strata:

- equal candidate length: 20/21 to 21/21;
- unequal candidate length: 26/29 to 28/29.

The result therefore did not depend exclusively on unequal token length or a single scoring-sensitive rescue.

The Oracle over the original and fixed branch was 49/50, equal to `F1G1`. There was no observed Oracle headroom over the stronger fixed branch in this selected set, so these results do not yet motivate adding router complexity.

## 7. What the evidence supports

The frozen scientific-direction gate and fixed-method gate both passed, and the primary unsafe continuous-effect interval excluded zero. Under the preregistered terminology, the result is `STRONG_EXTERNAL_SUPPORT_AI_CURATED_NOT_HUMAN_GOLD`.

This supports:

- a result-aware human and preferably Japanese-native-speaker audit of the 50 materials;
- a fresh group-disjoint, human-reviewed confirmation after that audit;
- later cross-model replication only if the human-reviewed result survives.

It does not support:

- human-gold or population-level performance claims;
- a statistically decisive discrete accuracy improvement;
- free-generation improvement;
- deployment readiness;
- multilingual generalization;
- an internal causal-mechanism claim;
- a working reliability router.

## 8. Research-practice reflection

The most valuable part of today's work was keeping the inference decision downstream of the scientific-integrity gate. Material construction, two linguistic passes, leakage checks, tokenization checks, forecasts, and stopping rules were all frozen before any evaluated-model output was visible.

The result also forced a useful distinction between three statements that would otherwise be easy to conflate:

1. the continuous form-specific effect transferred to new AI-curated groups;
2. the fixed branch improved three final choices;
3. the fixed branch did not create Oracle complementarity on this set.

All three are true, but they imply different next steps. The correct next action is better annotation and fresh confirmation, not immediate scale-up.

## 9. Compute and preservation

The run produced 600/600 finite, reconstructible candidate scores. Model scoring took 27.64 seconds; the guarded active-compute window was 134.08 seconds. Approximate active GPU cost was `$0.0406`, below the `$1.00` cap.

The Pod was stopped automatically and independently rechecked as `EXITED / stopped`. No retry or expansion occurred. Complete local results, material-bearing audits, cloud logs, and candidate text remain outside the public repository under the existing data policy.

## 10. Minimum next actions

1. Audit all 50 source senses, Japanese glosses, kana readings, controls, and Chinese candidate contrasts with human bilingual review.
2. Separate retained items from revised items; every revised item must be treated as a new material rather than inheriting the exposed result.
3. Freeze a fresh group-disjoint confirmation before new inference.
4. Defer another model, multilingual expansion, and router development until that confirmation is complete.

## One-sentence update

A result-blind 50-item Qwen3-8B factorial replicated the positive form-removal-with-gloss effect on 22/30 unsafe items and improved the fixed branch from 46/50 to 49/50 without observed control harms, while the 100% control ceiling, zero Oracle headroom, and AI-only annotation status make human-reviewed confirmation—not immediate scale-up—the required next step.
