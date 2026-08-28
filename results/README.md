# Results Archive

This directory contains scores-only artifacts and aggregate reports. Benchmark
source text, candidate translations, intervention sentences, complete model
checkpoints, credentials, and raw cloud logs are not distributed here.

## Public per-item outputs

- `pilots/`: 12 translation runs—six pinned checkpoints in each Type-1
  direction—plus summaries;
- `causal/`: six orthography-intervention score files, summaries, and a
  text-free material manifest;
- `analysis/`: cross-model aggregates, diagnostics, bootstrap results, and
  analysis manifests, including the text-free Qwen3-8B five-item clean
  matched-probe pilot.

Every public JSONL uses schema `scores_only_v1`. It retains the numeric evidence
needed to recompute accuracies, wrong-option distributions, score disagreements,
margins, and orthography effects. Benchmark text is rejoined by `item_index`
after retrieving the pinned upstream checkout. Private-source and public-file
hashes are mapped in `public-artifacts.manifest.json`.

Hashes labeled `private_source_*` in compact tables, or described as execution
JSONL/log hashes in historical experiment notes, refer to the complete local
artifacts verified at run time. They remain useful provenance records but do
not equal the redacted public files. Current public hashes are in the manifest.

Run:

```bash
make data-check
make check
```

The first command checks the public data boundary. The second also validates
all 18 model runs and their summaries.

## Human review

The repository retains aggregate judgments and item indices in the research
notes. Bulk review packets containing source and candidate text are kept only
in the local research workspace and are not public artifacts.
