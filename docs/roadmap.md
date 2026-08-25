# Research Roadmap

## Stage 0 — Reproducibility infrastructure

- [x] Establish reading, experiment, and daily-log templates.
- [x] Define conventions for data, environment, results, and failed runs.
- [x] Create a traceable paper-to-code-to-result workflow.

## Stage 1 — Doppelganger-JC paper–code alignment

- [x] Identify the task, data, metrics, official implementation, and target tables.
- [x] Map Japanese-to-Chinese Translation Type-1 to the official pipeline.
- [x] Audit the dataset schema and duplicate candidates.
- [x] Estimate GPU memory, storage, and execution cost.

## Stage 2 — Core numerical reproduction

- [x] Reproduce Japanese-to-Chinese Translation Type-1 for six accessible paper checkpoints.
- [x] Reproduce Chinese-to-Japanese Translation Type-1 for the same six checkpoints.
- [x] Compare paper-reported and reproduced aggregate accuracies.
- [x] Preserve model revisions, row counts, hashes, blocked access, and resource cleanup records.
- [ ] Evaluate Llama 3.1 only if the exact gated checkpoint becomes accessible; do not replace it silently.

## Stage 3 — Measurement and data audit

- [x] Compare official full-prompt PPL with candidate-only NLL.
- [x] Document official-score sensitivity to candidate token length.
- [x] Audit missing questions and duplicate answer options.
- [x] Review a shared `wrong1` error subset manually.
- [ ] Obtain independent bilingual review for ambiguous and high-impact items.
- [ ] Compare alternative scoring rules against set-valued bilingual judgments.

## Stage 4 — Controlled orthography study

- [x] Define original, target-kana, and negative-control conditions.
- [x] Freeze a development set and a 382-item primary analysis set.
- [x] Preregister the five-model replication before viewing new results.
- [x] Complete the six-model target-versus-unrelated-control analysis.
- [x] Report paired bootstrap intervals and model-level heterogeneity.
- [ ] Replicate on an independent dataset or language setting.
- [ ] Add independent bilingual validation of the intervention materials.

## Stage 5 — Contextualized phrase retrieval

- [ ] Read the Cross-lingual Contextualized Phrase Retrieval paper and create a claim-to-table map.
- [ ] Locate the official data pipeline, model entry point, and evaluation command.
- [ ] Reproduce the smallest documented baseline.
- [ ] Audit the metric, splits, and implementation differences.
- [ ] Define a Japanese–Chinese homograph subset without using test outcomes.

## Stage 6 — Reliability-aware routing

- [ ] Define item-level reliability labels and oracle upper bounds.
- [ ] Compare static, calibrated, and learned routing baselines.
- [ ] Evaluate accuracy, risk–coverage, calibration, and computational cost.
- [ ] Test whether form-based proposals help low-resource retrieval without increasing false-friend risk.
