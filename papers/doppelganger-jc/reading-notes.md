# Doppelganger-JC Reading and Scope Notes

## Paper

- Title: *Doppelgänger/JCI: Imitating Lexical Misunderstanding in Cross-Lingual Interpretation*
- Venue: IJCNLP-AACL 2025
- Paper: <https://aclanthology.org/2025.ijcnlp-long.96/>
- Languages: Japanese and Chinese

## Task overview

The benchmark studies how language models handle Japanese–Chinese lexical items whose forms overlap but whose meanings or contextual uses may diverge. It includes word-meaning, word-meaning-in-context, and sentence-translation evaluations with several relation or error types.

For the reproduced Translation Type-1 setting, each item supplies a source sentence and four candidate translations:

- `correct`: the benchmark-designated translation;
- `wrong1`: a candidate that preserves or directly transfers the cross-lingual homographic form;
- `wrong2` and `wrong3`: other distractors.

The paper selects the candidate with the lowest perplexity under a fixed prompt. Correctness is defined by whether the selected candidate is `correct`.

## Why the task matters

Shared form can provide an efficient cross-lingual lexical clue, especially in related scripts and low-resource settings. The same clue can also produce false-friend or copy-based errors. The benchmark therefore provides a controlled setting for studying the boundary between useful transfer and misleading form similarity.

## Reproduction target

The initial target was the Japanese-to-Chinese Translation Type-1 column. The study later expanded to the corresponding Chinese-to-Japanese column. Six of seven listed checkpoints were accessible.

## Paper-to-code questions retained for audit

- Which tokens are included in the reported average loss?
- How do candidate length and the shared prompt affect PPL ranking?
- Are model revisions and data versions fully specified?
- How should duplicate or semantically acceptable alternatives be scored?
- Which observed error concentrations persist under a candidate-only diagnostic?

## Connection to the broader research program

The benchmark provides a diagnostic environment for a form–semantics reliability hypothesis. It does not by itself evaluate contextualized phrase retrieval. The next stage is to reproduce a retrieval baseline and test whether item-level signals can predict when orthographic evidence should be accepted, verified, or rejected.

## Open questions

1. Can reliability be predicted on a held-out lexical split rather than fitted to the current test set?
2. Do calibrated or PMI-style scores align better with bilingual set-valued judgments than either current score?
3. Does the orthographic effect transfer to open-ended translation and contextualized phrase retrieval?
4. How much of the effect remains after controlling candidate naturalness, frequency, token length, and semantic distance?
