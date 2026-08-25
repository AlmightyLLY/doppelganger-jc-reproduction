# Reproduction Guide

This guide reconstructs the Translation Type-1 and orthography-intervention
workflow reported in this repository. Committed scores-only outputs can be
validated without a GPU. Re-running inference requires benchmark data from its
authoritative source, Hugging Face model access, and sufficient accelerator
memory.

## 1. Clone and obtain the pinned benchmark data

```bash
git clone https://github.com/AlmightyLLY/doppelganger-jc-reproduction.git
cd doppelganger-jc-reproduction
python3 scripts/bootstrap_upstream.py
```

The bootstrap helper clones `0017-alt/Doppelganger-JC` at commit `eb1c4f3f17403af238046bf218dc49643bc2e2e2` and creates local links to `questions/`, `cognate_fixed/`, `calc_ppl_translation.py`, and `models.txt`. The upstream benchmark files are not copied into this repository and remain subject to their original data terms.

To reuse an existing checkout whose benchmark files match that commit:

```bash
python3 scripts/bootstrap_upstream.py --source /path/to/Doppelganger-JC
```

## 2. Create the environment

Python 3.11 was the preferred runtime. The full 7–8B runs were performed on an NVIDIA A40 with 48 GiB VRAM. A GPU with roughly 24 GiB can generally run one model in BF16/FP16, but 40–48 GiB provides safer headroom for remote-code models and avoids aggressive memory workarounds.

Linux/CUDA, current recommended rerun environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r environment/requirements-cuda.txt
python -m pip install -r environment/requirements.txt
python scripts/check_environment.py
```

The two historical GPU batches did not use the same PyTorch/CUDA wheel. The
translation runs recorded `2.5.1+cu121`; the orthography runs recorded
`2.4.1+cu124`. To follow either historical dependency lane more closely, create
separate virtual environments and install
`environment/requirements-translation-cuda121.txt` or
`environment/requirements-orthography-cuda124.txt`. These files capture the
reported direct dependencies, not a complete bit-for-bit operating-system and
driver image. See `environment/README.md`.

macOS development and small-model checks:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r environment/requirements-macos.txt
python -m pip install -r environment/requirements.txt
python scripts/check_environment.py
```

Do not commit Hugging Face or RunPod credentials. Gated models must be authorized in the account used for the run.

## 3. Validate the dataset and committed artifacts

The audit reports the two missing Japanese-to-Chinese questions and three duplicate-option items rather than silently correcting them:

```bash
python scripts/audit_jp_zh_homographs.py
```

All 12 translation runs and all six orthography runs are committed as
scores-only per-item JSONL. Their model revisions, record counts, PPL
identities, argmin choices, margins, effects, and aggregate means can be checked
without benchmark text:

```bash
make static-check
make data-check
make check
```

These checks use only the Python standard library and can also be added to any CI service.

## 4. Inspect the scoring procedure on one item

```bash
python scripts/compare_scoring_one_example.py \
  --model Qwen/Qwen2.5-0.5B-Instruct \
  --direction jp_zh \
  --device auto
```

This prints the paper-compatible full-prompt PPL and the candidate-only diagnostic NLL/PPL for the same four candidates. The candidate-only measure is not a human condition and is not substituted for the paper metric.

## 5. Re-run Translation Type-1

Preview the exact 12 pinned commands without starting GPU inference:

```bash
python scripts/run_reproduction_matrix.py --phase translation
```

Run them sequentially:

```bash
python scripts/run_reproduction_matrix.py \
  --phase translation \
  --device cuda \
  --execute
```

Use `--model-slug` and `--direction` to select a smaller subset. Outputs go to the ignored `results/local/` directory, so the frozen committed results cannot be overwritten accidentally. Each item is appended immediately and `run_translation_subset.py` resumes a matching partial run.

## 6. Re-run the orthography intervention

First reconstruct the frozen material locally from the pinned upstream data:

```bash
python scripts/prepare_orthography_control_relevance_full.py
```

The builder uses the text-free frozen config in
`configs/orthography_material_v1.json` and refuses output whose SHA-256 differs
from the preregistered material. The resulting material remains under the
ignored `results/local/` tree.

Then validate it without loading a model:

```bash
python scripts/run_orthography_control_relevance_full.py \
  --material results/local/materials/orthography-control-relevance-full-v1.jsonl \
  --validate-material-only
```

Preview or execute the six pinned model commands:

```bash
python scripts/run_reproduction_matrix.py --phase orthography
python scripts/run_reproduction_matrix.py \
  --phase orthography \
  --device cuda \
  --execute
```

The 450 constructed items include 411 with both unrelated and related controls. The preregistered primary estimate uses the frozen 382-item holdout/non-weak-negative-control set; it is an analysis subset, not the size of the material file.

## 7. Rebuild cross-model analyses

The aggregation scripts accept explicit paths and write JSON or Markdown reports:

```bash
python scripts/analyze_multimodel_translation.py \
  results/pilots/*-jp_zh-homographs-sv2-start0-limit462.jsonl \
  --output results/local/jp_zh-six-model-synthesis.json

python scripts/analyze_orthography_multimodel_replication.py \
  --output-json results/local/orthography-six-model-replication.json \
  --output-report results/local/orthography-six-model-replication.md
```

The published analyses remain under `results/analysis/`; local recomputations
should stay under `results/local/`. Published JSONL files omit benchmark text
and use `item_index` as the join key. See `data/README.md` and
`results/public-artifacts.manifest.json`.

## Scope boundary

This repository makes the six-model bidirectional Translation Type-1 reproduction and the six-model orthography extension executable and auditable. It does not claim to reproduce every task, translation type, human baseline, or appendix experiment in Doppelganger-JC. The inaccessible Llama 3.1 checkpoint is recorded as blocked rather than replaced.
