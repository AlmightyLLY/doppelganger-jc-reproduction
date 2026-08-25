# Research Log — 2026-08-24

## Objective

Continue the Japanese-to-Chinese Translation Type-1 reproduction while separating successful execution from an understanding of what the evaluation measures.

## Progress

- Completed three exact paper checkpoints: Qwen-1M, llm-jp, and ELYZA.
- Completed Qwen2.5 0.5B and standard 7B diagnostic baselines without treating them as paper checkpoints.
- Used the same 462 questions, prompt, and scoring version for all formal runs.
- Recorded revisions, software, GPU, dtype, and artifact hashes; deleted paid Pods after verification.
- Audited 464 cognate entries, 462 questions, two missing question pairs, and three duplicate-option items.

## Initial paper-model results

| Model | Paper official | Reproduced official | Difference | Candidate-only |
|---|---:|---:|---:|---:|
| Qwen2.5-7B-Instruct-1M | 69.70% | 68.40% | −1.30 pp | 69.70% |
| llm-jp-3-7.2b-instruct3 | 58.23% | 58.87% | +0.64 pp | 51.95% |
| Llama-3-ELYZA-JP-8B | 52.81% | 52.81% | 0.00 pp | 48.27% |

ELYZA matches the aggregate paper count, but the absence of paper item-level outputs prevents an item-level identity claim.

## Measurement lessons

The lowest PPL is a preference under a particular prompt, tokenizer, and normalization rule, not a probability that the candidate is semantically true. The benchmark label then determines whether the selected candidate is counted as correct.

Candidate-only scoring uses the same source and prompt but averages only candidate-token NLL. It is not inherently more correct. Its immediate value is to expose how shared-prompt averaging and candidate length alter the ranking.

For ELYZA, official and candidate-only differed on 76 items; official selected the longer candidate on 72 and an equal-length candidate on four. Official also produced 94 near-ties versus 37 for candidate-only. The same direction had already appeared in the two earlier paper models.

## Model comparison lesson

Lower aggregate accuracy does not imply that a model's item-level correct set is contained by a higher-scoring model. ELYZA solved 20 items missed by both Qwen-1M and llm-jp. Tokenizer, pretraining, architecture, and post-training can redistribute errors even when aggregate ranking is stable.

## Homograph hypothesis

`wrong1` represented 82.9%, 69.5%, and 85.3% of official errors for Qwen, llm-jp, and ELYZA. This is consistent with homograph attraction but does not establish causality. Candidate construction, fluency, frequency, length, and label quality remain competing explanations.

A paired original/target-kana/control-kana experiment was therefore specified, with candidate-only margin as the primary outcome and human checks for reading, meaning preservation, syntax, naturalness, and ambiguity.

## Evidence boundary

Supported:

- close aggregate reproduction for the first three paper checkpoints;
- stable `wrong1` concentration and official-score length direction;
- substantial model-specific error redistribution.

Not supported:

- complete-paper reproduction;
- orthography as the unique or strongest cause;
- candidate-only as a superior metric;
- item-level equality with paper outputs.

## Next actions

1. Preregister each remaining checkpoint before viewing its result.
2. Validate the first kana-pilot items for reading and naturalness.
3. Audit the official PPL scripts before expanding to additional paper tasks.
4. Preserve a personal first-pass interpretation before formal report editing.
