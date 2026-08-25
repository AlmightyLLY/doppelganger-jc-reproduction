# EXP-20260825 — Preregistration: Five-Model Orthographic-Effect Replication

## Research question

The completed Qwen experiment showed that target-word kana conversion, relative to an unrelated control conversion, shifted the candidate-only correct–`wrong1` margin toward `correct` without improving four-option accuracy. This preregistration tests whether the continuous effect replicates in the five remaining completed paper models.

## Frozen material

- File family: `orthography-control-relevance-full-v1`
- Items: 450
- SHA-256: `fa19564838ab4d86f8ecda1a08daf9e792e3d576734138927f2b569ef933b4c9`
- Primary set: 382 items after excluding 35 exposed development items and weak unrelated-control proxies
- Four-condition common subset: 365 items
- Conditions: original, target-kana, unrelated-control-kana, and related semantic control where available

No replacement, quality label, analysis-set definition, or candidate answer may be changed in response to a new model output. The source-only controls do not have independent bilingual item-level validation; cross-model replication does not remove that limitation.

## Frozen checkpoints

| Model | Revision |
|---|---|
| `llm-jp/llm-jp-3-7.2b-instruct3` | `cdd4c7f3296fdc7785423a864bd9a86ce4c15915` |
| `elyza/Llama-3-ELYZA-JP-8B` | `e6c316496ee7d9a11710c50229e8cb39b6b0a4a3` |
| `baichuan-inc/Baichuan2-7B-Base` | `f9d4d8dd2f7a3dbede3bda3b0cf0224e9272bbe5` |
| `mistralai/Mistral-7B-Instruct-v0.2` | `63a8b081895390a26e140280378bc85ec8bce07a` |
| `google/gemma-7b` | `ff6768d9368919a1f025a54f9f5aa0ee591730bb` |

The completed Qwen result is added only at the final six-model synthesis stage and is not rerun or used to alter the rules above.

## Frozen metric

```text
margin = NLL(wrong1) - NLL(correct)
target_effect = margin(target_kana) - margin(original)
control_effect = margin(unrelated_control_kana) - margin(original)
orthography_effect = target_effect - control_effect
```

NLL is averaged only over candidate-translation tokens. Positive effect means that target-kanji removal favors `correct` relative to `wrong1`; it is not an accuracy difference.

## Confirmatory analyses

1. For each model, report mean, median, positive/negative counts, and an item-paired bootstrap 95% interval on the 382-item set.
2. Report the number of new models with a positive mean alongside the frozen Qwen direction.
3. For the fixed six-model summary, average effects across models within each item, then bootstrap the 382 item means.
4. Do not treat `6 × 382` observations as independent or use a pooled row-level interval as primary evidence.

## Secondary diagnostics

- four-option choice counts and original-to-target transitions;
- target and control accuracy changes;
- high-only, weak-inclusive, and all-450 sensitivity views;
- related-control comparison on the 365-item common subset;
- exact/variant, tokenization, outliers, inter-model effect correlation, and opposing transitions.

These diagnostics cannot convert a positive margin effect into a claim of universal accuracy improvement or a direct cognitive-process claim.

## Execution and failure rules

- Run sequentially on a RunPod A40 48 GB in BF16.
- Produce an isolated three-item smoke output before each 450-item formal output.
- Validate row count, revision, finite scores, argmin, margins, effects, and summary means.
- Preserve failures; do not substitute checkpoints or alter other model rules.
- Verify downloaded SHA-256 values locally.
- Apply a four-hour automatic termination guard and delete the Pod after completion or confirmed failure.

An initial two-item smoke run completed forward passes for llm-jp but failed during summary generation because the prefix contained no `high-only` item. Before any formal 450-item output existed, the smoke prefix was mechanically expanded to the first three items, the smallest prefix covering all preregistered analysis subsets. The failed two-item log was retained.

## Decision rule

If most model means are positive and the fixed six-model interval excludes zero, report cross-model replication on the frozen materials. If directions differ, report heterogeneity without selecting only supportive models. General causal claims still require stronger bilingual validation and independent materials.
