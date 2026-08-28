# Clean Matched-Probe Five-Item Pilot — Qwen3-8B

Internal experiment ID: `EXP-20260828-clean-matched-probe-pilot-v1`. This public report was finalized on 2026-08-29.

## Question

Does removing the visible Japanese target-word form, rather than converting an unrelated source component to kana, shift a recent model away from a human-frozen visible-form Chinese lexicalization and toward a human-frozen reference lexicalization?

This is a selected exploratory mechanism pilot. It was designed after the first item-416 probe was technically valid but pattern-unstable. It is not a prevalence study and does not support population-level significance claims.

## Frozen scope

- Model: `Qwen/Qwen3-8B`
- Revision: `b968826d9c46dd6066d109eabc6255188de91218`
- Items: 35, 175, 300, 354, and 451
- Conditions, in order: original, target-kana, and unrelated-control-kana
- Two human-frozen complete Chinese candidates per item
- Hidden states: all 37 real states, indices 0–36
- Primary outcome: complete-candidate mean NLL

Items 354 and 451 were frozen as unsafe. Items 35, 175, and 300 were frozen as safe visible-form alternatives: both candidates were considered acceptable, so their outcomes measure preference shifts rather than accuracy corrections.

Items 175 and 354 formed the equal-token-count core. Items 35, 300, and 451 were reported separately as length-sensitive.

## Metrics and prediction

The primary margin was

```text
M(condition) = mean_NLL(visible-form candidate)
             - mean_NLL(reference candidate)
```

Positive `M` favors the reference. The controlled contrast was

```text
Delta_target_control = M(target_kana)
                     - M(unrelated_control_kana)
```

The frozen item-level prediction was `Delta_target_control > 0`. A full rescue additionally required the original and control conditions to prefer the unsafe visible-form candidate while target-kana preferred the reference.

Raw complete-sequence log probability, lexical-span score, lexical first-token score, all 37 layer values, token ranks, top-50 readouts, and final-projection checks were saved as secondary diagnostics.

## Final-layer results

Candidate choice `0` is the reference and `1` is the visible-form candidate.

| Item | Category | Tokens ref/form | M original | M target | M control | Delta | Choice O/T/C |
|---:|---|---:|---:|---:|---:|---:|---:|
| 35 | safe | 9/8 | +1.518884 | +1.514736 | +1.755609 | −0.240873 | 0/0/0 |
| 175 | safe | 11/11 | −0.279993 | +0.438421 | −0.241566 | +0.679987 | 1/0/1 |
| 300 | safe | 14/15 | +0.068401 | +0.002333 | −0.029125 | +0.031458 | 0/0/1 |
| 354 | unsafe | 9/9 | −0.086845 | +1.977208 | −0.299874 | +2.277082 | 1/0/1 |
| 451 | unsafe | 5/6 | +0.251285 | +0.588059 | +0.245445 | +0.342615 | 0/0/0 |

The primary prediction was supported on four of five selected items. The equal-length core was positive for both items, with a descriptive mean Delta of `+1.478535`.

## Unsafe and safe outcomes

Item 354 showed the full predefined unsafe rescue: original and unrelated control preferred the unsafe visible-form candidate, target-kana preferred the reference, and all saved score directions agreed.

Item 451 had a positive Delta but no rescue because the reference was already preferred in every condition. It is evidence of preference sensitivity, not an accuracy correction. The unsafe rescue count was therefore one of two.

Among the safe acceptable-pair items, 175 and 300 had positive primary shifts and 35 had a negative shift. These observations cannot establish that form information improved or reduced accuracy because both candidates were frozen as acceptable.

## Length and scoring sensitivity

Item 35 met the preregistered `SCORING-SENSITIVE` definition:

| Metric | Delta |
|---|---:|
| Complete-candidate mean NLL | −0.240873 |
| Raw complete-sequence log probability | −1.609460 |
| Lexical-span sequence score | +4.386718 |

Items 300 and 451 had positive Delta under all three metrics. Item 300 nevertheless changed its control-condition final choice under alternative scoring definitions; this secondary choice-pattern sensitivity is disclosed but is not the frozen scoring-sensitive flag.

## Upper-layer stability

Layers 29–34 produced the following primary-Delta signs:

| Item | Sign sequence | Upper-band mean | Match final sign |
|---:|---|---:|---:|
| 35 | `------` | −0.499727 | 6/6 |
| 175 | `++++++` | +1.137869 | 6/6 |
| 300 | `------` | −0.958301 | 0/6 |
| 354 | `++++++` | +2.711643 | 6/6 |
| 451 | `++--++` | +0.343860 | 4/6 |

Items 175 and 354 were the clearest stable positive cases. Item 300's final positive contrast was small and contradicted by every layer in the predefined upper band.

## Validation incident and resolution

The frozen remote validator initially returned `FAIL` because six target tokens with competition ranks 49 or 50 were absent from the stored top-50 list. Each target token's log probability exactly equaled the top-50 cutoff. `torch.topk` had retained another tied token, while the independently stored gold rank correctly counted only strictly higher logits.

The original validator output and raw model artifact were preserved. A versioned CPU-only supplemental audit checked the six rows and converted them to cutoff-tie warnings only when all of the following held:

- top-50 IDs were unique and log probabilities were descending;
- the stored competition rank equaled one plus the number of strictly higher top-50 scores;
- the target token was absent rather than duplicated;
- the target log probability exactly matched the cutoff.

All six rows passed these conditions, no other blocker remained, and the final-projection maximum absolute difference was `0.0`. No model rerun was needed.

## Execution and cleanup

The first Pod window stopped during preflight before dispatch or model loading because a lock-referenced script had not been included in the upload bundle. The failed attempt was preserved and did not consume the authorization.

After the upload manifest was repaired and the same exact run was explicitly reauthorized, one inference completed all five items. The inference window was 237.840 seconds, with an upper cost observation of approximately `$0.07201` at the listed `$1.09/hour` rate. Including the preflight-only window, total observed Pod time was 5.949 minutes and the derived upper cost observation was approximately `$0.10808`.

The Pod was verified as `EXITED / stopped`. It was retained rather than deleted, leaving a recorded stopped-storage cost of `$0.024/hour`. The one-run authorization was consumed; no rerun or expansion occurred.

## Evidence boundary

This pilot supports four narrow descriptive statements:

1. the frozen controlled contrast was positive on four of five selected items;
2. both equal-length core items were positive;
3. one selected unsafe item showed the predefined rescue pattern;
4. score definition and layerwise stability materially affect case interpretation.

It does not establish population-level significance, cross-model or cross-lingual generality, a universal benefit or harm from visible form, a causal internal mechanism, an English pivot, a discrete decision layer, or free-generation improvement.

The public scores-only artifact is [available here](../../../results/analysis/qwen3-8b-clean-matched-probe-five-item-pilot.json). Benchmark and intervention text remain local under the repository's data policy.
