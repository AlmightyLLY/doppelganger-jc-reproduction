# Doppelganger-JC Reproduction and Orthography Study

This repository documents a reproducibility study of Doppelganger-JC, with a focus on Japanese–Chinese lexical transfer, cross-lingual homographs, scoring behavior, and controlled orthographic interventions. A subsequent contextualized phrase-retrieval stage is included in the research roadmap.

The project follows a staged workflow: reproduce a published result, audit the measurement procedure, identify robust error patterns, and test a narrowly defined extension with frozen controls.

## Run and verify the study

This repository contains the actual experiment code and scores-only per-item
outputs—not only narrative reports. A third party can validate all 18 committed
model runs without downloading model weights or receiving benchmark text:

```bash
git clone https://github.com/AlmightyLLY/doppelganger-jc-reproduction.git
cd doppelganger-jc-reproduction
make static-check
make check
```

Re-running inference additionally requires the pinned upstream benchmark data,
local reconstruction of the intervention material, and a suitable GPU:

```bash
python3 scripts/bootstrap_upstream.py
python3 scripts/prepare_orthography_control_relevance_full.py
python3 scripts/run_reproduction_matrix.py --phase translation   # dry run
python3 scripts/run_reproduction_matrix.py --phase orthography   # dry run
```

See [REPRODUCE.md](REPRODUCE.md) for environment installation, exact commands, data provenance, artifact validation, and scope boundaries.

## Current study

The first study examines [Doppelganger-JC](https://aclanthology.org/2025.ijcnlp-long.96/), a benchmark for Japanese–Chinese homographs.

Completed work:

- bidirectional Translation Type-1 evaluation for six accessible paper checkpoints;
- comparison with the paper-reported aggregate accuracies;
- audit of the official full-prompt PPL score and a candidate-only NLL diagnostic;
- dataset and duplicate-option checks;
- manual review of a shared homograph-error subset;
- a preregistered six-model kana intervention with an unrelated within-sentence negative control.

The seventh checkpoint, `meta-llama/Llama-3.1-8B-Instruct`, was not evaluated because access to the gated model was denied. No substitute checkpoint is reported as an exact reproduction.

### Main findings

| Finding | Evidence | Interpretation boundary |
|---|---|---|
| The homograph-based `wrong1` option attracts a large share of errors. | 69.5%–85.3% of official Japanese-to-Chinese errors across six models. | Descriptive concentration alone does not establish causality. |
| Visible target-word orthography affects candidate preference. | Frozen 382-item intervention; six-model mean effect `+0.136`, paired bootstrap 95% CI `[+0.100, +0.173]`. | The result concerns the correct-versus-`wrong1` NLL margin under this design. |
| Removing kanji is not a universal correction. | Accuracy improved for two models, declined for three, and was nearly unchanged for one. | Orthographic information can be useful evidence or a misleading shortcut. |
| Evaluation is scoring-sensitive. | Official and candidate-only rankings differ systematically, with a documented candidate-length effect in the official score. | Candidate-only scoring is a diagnostic, not a replacement paper metric. |

These results motivate a reliability-aware question: when should a model retain a form-derived lexical proposal, and when should it trigger semantic verification or retrieval?

This is a high-quality partial reproduction of the paper's bidirectional Translation Type-1 setting, not a reproduction of every task, type, human baseline, or appendix analysis in the paper.

## Repository map

```text
.
├── papers/
│   ├── doppelganger-jc/   # reproduction, audits, and orthography study
│   └── ccpr/              # next-stage phrase-retrieval reproduction
├── configs/               # exact model IDs, revisions, and frozen set sizes
├── results/               # scores-only outputs, summaries, and analyses
├── data/                  # benchmark provenance and redistribution policy
├── environment/           # pinned macOS and CUDA dependencies
├── scripts/               # scoring, inference, intervention, and validation code
├── templates/             # experiment, reading, and research-log templates
├── REPRODUCE.md            # end-to-end commands
├── Makefile                # bootstrap, audit, static-check, and validation targets
└── docs/roadmap.md         # project milestones and next steps
```

Start with the [Doppelganger-JC study overview](papers/doppelganger-jc/README.md). Detailed experiment records are indexed in [papers/doppelganger-jc/experiments](papers/doppelganger-jc/experiments/README.md).
The evolution from reproduction to the revised reliability-aware research theme
is summarized in [Research Trajectory and Revised Research Agenda](papers/doppelganger-jc/notes/2026-08-26-research-trajectory-and-revised-theme.md).

## Reproducibility policy

Each formal experiment records, where applicable:

- the exact model identifier and revision;
- the analysis set and exclusion rules;
- paper and diagnostic scoring definitions;
- environment and accelerator information;
- failed or blocked runs;
- output row counts and SHA-256 checks;
- confirmatory versus exploratory analyses;
- claims supported by the evidence and claims that remain unsupported.

Large model weights, benchmark text, intervention text, credentials, and raw
cloud logs are not committed. The benchmark is obtained from its authoritative
repository at a pinned commit. Public per-item outputs retain only indices,
scores, choices, token counts, and derived statistics; bulk review packets stay
local. Reported aggregates remain independently recomputable from the numeric
artifacts, and text can be rejoined locally by `item_index`.

## Status and next step

The Doppelganger-JC Translation Type-1 reproduction is frozen. Following a
research-planning discussion, the immediate priority is now a small, audited
mechanism study of the remaining homograph behavior in recent open-weight
checkpoints. CCPR remains part of the longer-term roadmap but is not the next
execution milestone. The current transition is documented in the
[2026-08-27 research log](papers/doppelganger-jc/notes/2026-08-27-post-meeting-research-log.md).

## Citation and license

Code in this reproduction is released under Apache License 2.0; see [LICENSE](LICENSE) and [NOTICE](NOTICE). Benchmark data retain the upstream terms described in [data/README.md](data/README.md). Citation metadata for this repository and the original paper are provided in [CITATION.cff](CITATION.cff).
