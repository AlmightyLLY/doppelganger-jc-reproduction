# Orthography × Semantic-Information External Validation — Qwen3-8B

Internal experiment ID: `factorial-external-ai-curated-50-v1`
Run date: 2026-08-30 JST

## Research question

On new lexical groups selected without using evaluated-checkpoint outcomes, does removing a visible Japanese homograph improve correct-versus-form-derived Chinese candidate preference when a contextual Japanese semantic gloss is supplied?

The associated fixed-method question is whether one `target-kana + gloss` branch improves over the original source without unacceptable harm on form-reliable controls.

This experiment does not evaluate a router. Oracle is secondary.

## Epistemic status

The 50-item set is `AI_CURATED_RESULT_BLIND_EXTERNAL_VALIDATION`.

It is not human-confirmed gold, native-speaker adjudicated, or independent double-human annotation. Historical manual labels were used only to mine a broad pool, and the evaluated Qwen3 checkpoint was not used to generate, rank, filter, or repair the material before inference.

## Candidate construction and exclusions

- Historical manual source: 1,017 PIC-3Cue seeds
- Rows conservatively excluded through exposed-component expansion: 205
- Result-blind broad pool: 68 unsafe-prior and 43 reliable-prior rows
- Pass 1: 77 accepts, 34 cautions
- Adversarial result-blind AI Pass 2: 50 final accepts, 4 cautions, 57 rejects
- Final set: 30 strict unsafe, 20 form-reliable controls
- Final connected components: 50, with at most one item per component

Twenty-seven Pass-1 accepts were downgraded during Pass 2. Twelve retained materials were repaired, and 17 replacements were selected without inspecting Qwen3 results. No caution or reject entered the experiment.

Benchmark text, candidate sentences, semantic glosses, and intervention text remain in the private local research workspace.

## Model and scoring

- Model: `Qwen/Qwen3-8B`
- Revision: `b968826d9c46dd6066d109eabc6255188de91218`
- Precision: BF16
- Quantization: none
- Items: 50
- Conditions: 6
- Candidates per condition: 2
- Total complete-candidate scores: 600
- Primary score: teacher-forced complete-candidate mean NLL

For every item, candidate 0 was the frozen acceptable candidate and candidate 1 the frozen unacceptable candidate. The primary margin was

```text
M(condition) = mean_NLL(unacceptable) - mean_NLL(acceptable)
```

Positive `M` favors the acceptable candidate.

The six frozen conditions were:

| Code | Visible target form | Semantic gloss | Other intervention |
|---|---|---|---|
| `F0G0` | yes | no | none |
| `F0G1` | yes | yes | none |
| `F1G0` | target converted to kana | no | none |
| `F1G1` | target converted to kana | yes | none |
| `U1G0` | yes | no | unrelated component converted to kana |
| `U1G1` | yes | yes | unrelated component converted to kana |

The primary fixed comparison was `F1G1` versus `F0G0`. The primary unsafe continuous effect was

```text
E_form_with_gloss = M(F1G1) - M(F0G1)
```

and its unrelated-control adjustment was

```text
E_control_adjusted_with_gloss = M(F1G1) - M(U1G1)
```

Raw complete-sequence and lexical-span sequence scores were mandatory diagnostics.

## Preregistered forecasts

| Quantity | Forecast |
|---|---:|
| `F0G0` overall | 34/50 |
| `F1G1` overall | 39/50 |
| Unsafe `F0G0` | 15/30 |
| Unsafe `F1G1` | 22/30 |
| Reliable `F0G0` | 19/20 |
| Reliable `F1G1` | 17/20 |
| Positive unsafe `E_form_with_gloss` | 22/30 |
| Median unsafe `E_form_with_gloss` | +0.20 |
| Positive control-adjusted effect | 20/30 |
| Net rescues minus harms | +5 |
| Reliable harms | 2 |
| Oracle headroom over stronger fixed branch | 3/50 |

## Accuracy results

| Condition | All 50 | Strict unsafe | Form-reliable control |
|---|---:|---:|---:|
| `F0G0` | 46/50 (92%) | 26/30 (86.7%) | 20/20 (100%) |
| `F0G1` | 48/50 (96%) | 28/30 (93.3%) | 20/20 (100%) |
| `F1G0` | 47/50 (94%) | 27/30 (90.0%) | 20/20 (100%) |
| `F1G1` | 49/50 (98%) | 29/30 (96.7%) | 20/20 (100%) |
| `U1G0` | 46/50 (92%) | 26/30 (86.7%) | 20/20 (100%) |
| `U1G1` | 48/50 (96%) | 28/30 (93.3%) | 20/20 (100%) |

`F0G0 → F1G1` produced three unsafe rescues, zero harms, and zero acceptable-to-acceptable changes. The paired gain was `+3/50 = +6` percentage points, with a 10,000-resample item-bootstrap 95% interval of `[0, +14]` points. Exact two-sided McNemar `p = 0.25`.

The discrete accuracy result is favorable but not statistically decisive on its own.

## Continuous unsafe effects

| Effect | Positive items | Mean | Median | 95% bootstrap interval for mean |
|---|---:|---:|---:|---:|
| Target-form removal with gloss | 22/30 | +0.240 | +0.239 | [+0.021, +0.460] |
| Target-form removal without gloss | 10/30 | −0.208 | −0.096 | [−0.608, +0.176] |
| Gloss with visible form | 13/30 | −0.053 | −0.116 | [−0.263, +0.161] |
| Gloss after target-form removal | 18/30 | +0.394 | +0.207 | [+0.121, +0.697] |
| Unrelated-kana effect with gloss | 9/30 | −0.063 | −0.032 | [−0.143, +0.011] |
| Control-adjusted target effect with gloss | 22/30 | +0.303 | +0.388 | [+0.060, +0.534] |
| Factorial interaction | 21/30 | +0.448 | +0.297 | [+0.140, +0.815] |

Raw-sequence and lexical-span versions both had positive median target effects. The unrelated control did not reproduce the target-form direction.

## Form-reliable controls

All 20 controls were correct under all six conditions. Nevertheless, target-form removal with the gloss reduced the correct-candidate mean-NLL margin on 18/20 controls: mean `−0.442`, median `−0.427`, 95% interval `[−0.605, −0.285]`.

The absence of discrete harm must therefore be interpreted together with the 100% control ceiling. The continuous result remains consistent with visible form providing useful evidence when the cross-lingual relation is reliable.

## Factorial decomposition

- Gloss alone rescued two baseline errors and harmed none.
- Target-kana alone rescued three errors but harmed two previously correct items.
- Target-kana plus gloss kept the three rescues and removed the two kana-only harms.
- Unrelated-kana plus gloss matched gloss alone at 48/50.

Thus, one discrete correction was added by target-form removal beyond the gloss branch. The broader form-specific conclusion depends on the preregistered continuous and control-adjusted effects rather than only on final accuracy.

## Sensitivity and Oracle

Four items were scoring-sensitive. Excluding them left a positive primary comparison: 43/46 to 45/46, with two rescues and no harms. The gain also appeared in both complete-candidate length strata:

- equal length: 20/21 to 21/21;
- unequal length: 26/29 to 28/29.

`Oracle(F0G0,F1G1)` scored 49/50, equal to the stronger fixed branch. The six-condition Oracle was also 49/50. This set provides no observed Oracle headroom for routing.

## Frozen gate outcome

The scientific-direction gate passed all five requirements:

- positive unsafe effect on at least 20/30: 22/30;
- positive median: +0.239;
- positive control-adjusted effect on at least 18/30: 22/30;
- unrelated control did not reproduce the effect;
- raw and lexical diagnostics were not both reversed.

The fixed-method gate also passed:

- `F1G1` improved by exactly 3/50;
- unsafe net rescues were +3;
- reliable harms were 0/20;
- no target-answer leakage was detected;
- the gain remained positive after removing scoring-sensitive items.

The primary unsafe mean-effect interval excluded zero. The frozen decision label is therefore `STRONG_EXTERNAL_SUPPORT_AI_CURATED_NOT_HUMAN_GOLD`.

## Technical validation and cost

- 600/600 scores were finite and independently reconstructible.
- Final-projection maximum absolute difference: `0.0`, below `1e-4`.
- A second local analysis produced byte-identical per-item, summary, and validation artifacts.
- No technical retry was used; the one-run authorization was consumed.
- Approximate active GPU cost: `$0.0406` at `$1.09/hour`.
- The Pod was stopped automatically and independently rechecked as `EXITED / stopped`.

## Evidence boundary and next step

The result supports a form-specific orthography × semantic-information interaction under frozen candidate scoring on this AI-curated set. It also supports testing the fixed branch on human-reviewed material.

It does not establish human-gold performance, free-generation improvement, deployment readiness, multilingual generalization, an internal causal mechanism, or a working router. The paired discrete accuracy comparison is not statistically decisive, and the reliable controls were at ceiling.

The required next stage is:

1. result-aware bilingual and preferably Japanese-native-speaker audit of the 50 exposed materials;
2. a fresh group-disjoint human-reviewed confirmation;
3. cross-model replication only after that confirmation.

The public aggregate result is stored in [`results/analysis/qwen3-8b-orthography-semantic-factorial-external-50-summary.json`](../../../results/analysis/qwen3-8b-orthography-semantic-factorial-external-50-summary.json). Material-bearing files and raw cloud logs remain local.
