# Doppelganger-JC Stage Synthesis — 2026-08-23 to 2026-08-25

## Stage definition

The completed milestone is a high-quality partial reproduction, not a complete reproduction of the entire paper. It includes:

- bidirectional Translation Type-1;
- six of seven paper checkpoints;
- official PPL, candidate-only diagnostics, error distributions, and bidirectional comparison;
- dataset audit and a 34-item manual review;
- a six-model target-kana intervention with an unrelated negative control.

Unreproduced components include word meaning, word meaning in context, other relation types, context robustness, open-ended translation, POS analysis, human baselines, Type-6, and appendix scale analyses.

## Development of the research question

### From score execution to score interpretation

The first stage established how tokenization, token-level NLL, PPL, and candidate selection interact. The model does not output a benchmark “correct answer” directly; it assigns sequence losses under a fixed prompt, and the evaluation rule selects the lowest-PPL candidate.

The full runs then showed that official and candidate-only scoring can rank candidates differently. Candidate-only is not a human or no-context condition: it averages loss only over candidate tokens. The paper metric remains primary for reproduction, while candidate-only reveals sensitivity to the shared prompt and length normalization.

### From `wrong1` concentration to a causal hypothesis

Most errors in several models selected the homograph-preserving `wrong1` option. This motivated the hypothesis that cross-lingual form similarity can act as a shortcut. At that point, however, the evidence was descriptive and confounded by candidate naturalness, frequency, length, and label ambiguity.

Manual review separated at least two phenomena:

- clear form copying that produces an unnatural or semantically wrong Chinese sentence;
- fluent or defensible alternatives for which the benchmark label is narrow or ambiguous.

This distinction prevented all `wrong1` outcomes from being treated as identical model failures.

### From universal normalization to controlled intervention

The initial idea was to convert the Japanese target to kana and remove visible overlap. The control design evolved from convenient sentence-internal kanji words to a primary negative control that was semantically unrelated to the target. This reduces the risk that the control itself removes target-relevant semantic evidence.

```text
margin = NLL(wrong1) - NLL(correct)
orthography_effect = margin(target_kana) - margin(unrelated_control_kana)
```

The fixed six-model mean effect was `+0.136`, 95% CI `[+0.100, +0.173]`. Five models had positive intervals, while the unrelated-control change averaged approximately `+0.005`.

Final four-option accuracy was heterogeneous: Baichuan and Mistral improved, Gemma was nearly unchanged, and Qwen, ELYZA, and llm-jp declined. Two early claims therefore had to be rejected:

- orthographic similarity is not exclusively harmful;
- universal kana conversion is not a general correction method.

## Refined research direction

Shared cross-lingual form should be modeled as a conditionally reliable prior rather than a feature that is always preserved or always removed.

The resulting question is:

> Can a model estimate the contextual reliability of a form-derived lexical proposal before final prediction and decide whether to accept it, trigger semantic verification, retrieve external evidence, or abstain?

This framing connects naturally to selective prediction, risk–coverage, calibration, multi-view agreement, retrieval-triggered verification, and a form–semantics gate for cross-lingual phrase retrieval.

The current evidence motivates the problem but does not yet constitute a method paper. Missing components include independent reliability labels, a learned router, strong baselines, held-out evaluation, and downstream retrieval validation.

## Methodological lessons

- Preserve the paper metric for reproduction while labeling alternative scores as diagnostics.
- Record data defects, blocked checkpoints, failures, exact revisions, and hashes rather than silently repairing or substituting them.
- Separate continuous preference changes, discrete accuracy changes, and claims about internal mechanisms.
- Modify hypotheses in response to heterogeneous results rather than selecting only supportive models.
- Require a second bilingual annotator before upgrading personal semantic judgments to gold labels.
- Slow experiment production when it begins to outpace direct understanding of the methods and failure cases.

## Frozen conclusions

1. The core bidirectional Translation Type-1 phenomenon is closely reproduced for six accessible checkpoints.
2. `wrong1` concentration is not explained solely by the official shared-prompt score.
3. Visible target orthography has a cross-model but heterogeneous causal contribution to correct-versus-`wrong1` preference under the frozen intervention.
4. Universal kana normalization is not supported as a correction method.
5. Reliability-aware selective routing is a more defensible research formulation than a static form rule.

## Open questions

1. How large is the orthographic effect relative to naturalness, frequency, candidate length, POS, and semantic distance?
2. Which observable features predict shortcut reliability on unseen lexical items?
3. Do calibrated, PMI-style, or span-based scores align better with set-valued bilingual judgments?
4. Does the behavior transfer from multiple choice to contextualized phrase retrieval and open-ended generation?
5. Can a router improve accuracy, risk–coverage, and computational efficiency over strong static baselines?

## Next stage

1. Freeze and document the current milestone.
2. Report the initial results to Professor Chu without claiming a complete-paper reproduction.
3. Reproduce the minimal official Cross-lingual Contextualized Phrase Retrieval baseline.
4. Define the homograph subset and reliability intervention only after the retrieval baseline is validated.
5. Return to remaining Doppelganger-JC tasks only when they answer a specific retrieval question.
