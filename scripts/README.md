# Experiment Code

These are the scripts used to construct, run, validate, and analyze the reported experiments. Formal commands are in [REPRODUCE.md](../REPRODUCE.md); exact model revisions and set sizes are in [`configs/reproduction_models.json`](../configs/reproduction_models.json).

## Entry points

| Script | Purpose |
|---|---|
| `bootstrap_upstream.py` | Retrieve the benchmark at the pinned upstream commit and install local data links. |
| `check_environment.py` | Check package versions, hardware backend, and benchmark layout. |
| `audit_jp_zh_homographs.py` | Reproduce the missing-question and duplicate-option data audit. |
| `compare_scoring_one_example.py` | Trace official full-prompt and candidate-only scores for one item. |
| `run_translation_subset.py` | Run a resumable Translation Type-1 subset in either direction. |
| `run_reproduction_matrix.py` | Print or execute the frozen six-model translation/orthography matrix. |
| `run_orthography_control_relevance_full.py` | Score original, target-kana, unrelated-control, and related-control conditions. |
| `export_public_artifacts.py` | Export scores-only artifacts while stripping benchmark and intervention text. |
| `audit_public_artifacts.py` | Enforce the public data boundary. |
| `validate_repository.py` | Validate all 18 committed raw runs. |
| `analyze_multimodel_translation.py` | Aggregate aligned per-item translation outputs across models. |
| `analyze_orthography_multimodel_replication.py` | Recompute cross-model orthography effects and paired bootstrap intervals. |

## Material construction and review

The retained `prepare_*`, `render_*`, and `create_*review*` scripts cover the
current source-only construction and local review workflow. Earlier one-off
builders with embedded intervention fragments are not distributed. The frozen
full material is generated under ignored `results/local/` storage from the
pinned upstream benchmark. Bulk review packets likewise remain local because
they contain benchmark text.

## Validation utilities

- `validate_run_output.py` checks per-item translation scores, revisions, record ordering, and argmin choices.
- `validate_orthography_control_relevance_full_output.py` additionally verifies `PPL = exp(NLL)`, margins, difference-in-differences effects, and reported analysis-set means.
- `validate_repository.py` applies these checks to every published model artifact.

The code writes local reruns under `results/local/` by default. Published
artifacts under `results/pilots/` and `results/causal/` are scores-only exports
and should not be overwritten by complete local runs.
