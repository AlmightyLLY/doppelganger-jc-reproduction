# EXP-20260824 — Orthography Causal-Pilot Design

## Research question

Holding the Japanese sentence meaning and all Chinese candidates fixed, does removing visible kanji overlap between the Japanese target word and Chinese `wrong1` reduce the model's preference for the homographic distractor?

The treatment targets visible orthographic correspondence, not semantics, frequency, syntax, or candidate fluency.

## Hypotheses

- **H1:** Converting the target word to its contextually correct kana reading weakens `wrong1` relative to `correct` under candidate-only NLL.
- **H2:** The target-word change is larger than converting an unrelated kanji-bearing component in the same sentence.
- **H3:** If exact visual overlap is central, `surface_exact=true` items show a larger effect than variant-form items.

## Paired conditions

1. `original`: unmodified source sentence;
2. `target_kana`: only the target homograph is converted to kana;
3. `control_kana`: the target remains in kanji, while an unrelated component is converted to kana.

The public record does not reproduce benchmark sentences. The three aligned
conditions are regenerated locally from the pinned upstream item, and the
committed per-item outputs use `item_index` as their join key.

The control estimates generic effects of kana conversion, naturalness, and tokenization. A two-condition original-versus-target comparison is insufficient.

## Material validation

Before formal scoring, each item should be checked for:

- contextually correct reading;
- preserved meaning, part of speech, and syntax;
- acceptable kana rendering;
- absence of newly introduced homophone ambiguity;
- natural and semantically unrelated control choice;
- unique replacement boundaries.

Items with multiple readings, repeated targets, unclear boundaries, or severe new ambiguity should be excluded before model outcomes are observed, with reasons recorded. The frozen annotation table should include item identifiers, original and rewritten sentences, readings, control choice, inclusion status, exclusion reason, annotator, and SHA-256.

## Sampling

The initial pilot froze 30 items after excluding duplicate-option questions and source sentences in which the listed target form did not appear literally. Sampling used seed `20260823` and stratified `surface_exact` 15/15.

Items were not selected by whether an earlier model chose `wrong1`. The pilot was intended to test linguistic validity and engineering behavior, not to provide a definitive average treatment estimate.

## Primary metric

Candidate-only NLL is used because source rewriting changes source tokenization; the paper's official score would directly average that source change into the outcome.

```text
margin = NLL(wrong1) - NLL(correct)
target_effect = margin(target_kana) - margin(original)
control_effect = margin(control_kana) - margin(original)
orthography_effect = target_effect - control_effect
```

Positive `orthography_effect` is the predicted direction. The continuous margin is primary; final accuracy, `wrong1` rate, transitions, and official scoring are secondary diagnostics.

## Planned analysis

- report mean, median, and item-paired bootstrap 95% interval for the continuous effect;
- use paired transition analysis for discrete outcomes;
- report the preregistered exact/variant subgroup without selecting the main conclusion from it;
- report inclusion counts, exclusion reasons, and naturalness judgments;
- replicate across models only after the material and implementation pass the pilot.

## Evidence boundary

A target-versus-control difference supports a causal contribution of visible orthography under the validated materials. It does not establish that orthography is the strongest cue, that the effect generalizes to all homographs or tasks, or that universal normalization improves translation.

If target and control change similarly, generic rewriting or tokenization becomes a stronger explanation. If neither changes, the model may reconstruct the same lexical identity from kana; a null result would not by itself prove that orthography is irrelevant.

## Frozen pilot artifacts

- Sample seed: `20260823`
- Included items: 30, stratified 15 exact / 15 variant
- Machine-rule pre-exclusions: 7
- Annotation-table SHA-256: `5c9a5cc5f484a0ae27c8ae14d62c3a2e887327b554355ec7a5080acba5d77a9d`
- Pre-exclusion-table SHA-256: `9447ce42a4df0e05048e88f6168684863bd6a08d678715d72df5a1417d52e538`

No model choices, PPL values, or treatment outcomes were used to construct the frozen 30-item table.
