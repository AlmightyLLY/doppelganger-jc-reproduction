# September 8 exploratory branch evidence: B09–B15

[中文日终报告](../../notes/2026-09-08-branch-research-day-closeout.zh-CN.md)

This is a scientific export of seven completed exploratory batches, not the full private execution or review archive. The [ledger](LEDGER.json) records 1,824 new scientific generations and 34,640 forwards, with USD 0 paid. A one-generation/two-forward deployment check is separate. Cached outputs, inverse mappings and deterministic selections do not increase generation counts or independent sample size.

Each batch directory includes actual new raw responses, available call plans and author references, frozen AI scores and paired transitions, a scientific report extract, and relevant predeclared method sections. `NEW-RAW-RESPONSES.json` is byte-identical to the local source. Other JSON exports omit local account locations or private collaboration metadata, with the original source hash and every omitted field recorded in `PUBLIC-MANIFEST.json`. Historical status and stop statements in protocol/report extracts describe their original time, not later batch authorizations.

Materials are controlled author constructions or previously exposed development materials. Author/AI references and full AI review are **not independent human gold or independent confirmation**. C/W/U means correct, explicitly wrong/unsupported, and unresolved under the recorded task contract. Content, occurrence, roles, name representation and output format remain separate. A correct negative proposition can still specify both role participants; it does not assert the event occurred.

## Reading the main evidence

- **B09/B10:** clean single-event controls and two-event context comparisons. B10's conditional model-extraction stage did not trigger; it was not run. Its separate simple selector uses exact cached single-call responses.
- **B11:** controlled inventory-display, voice and sentence-order comparisons. Single calls are all correct; double-call role errors and opposite-direction examples limit a universal ordering rule.
- **B12/B13:** Japanese original-material bridge, two-model comparison and identity-inventory calibration. Preserve B12 strict frozen scores; the separately identified posthoc ID-content audit is not a replacement score. B13's visible-ID content rule was declared before its outputs.
- **B14/B15:** reversible first-mention name substitutions and two-map agreement with exact-baseline fallback. B14 reuses 192 B13 baselines and adds 48 unique normalized calls. B15 adds 192 baselines and 96 normalized calls. Their 384 mapped and 192 method positions are deterministic derivatives of actual generations.

B14 improves Llama from 91/96 to 96/96, but both fixed single mappings already achieve the same score. B15 has baseline/method ceiling scores for both models; one Llama normalized role error maps to four related positions, and disagreement triggers baseline fallback. This is a local operational boundary, not evidence that agreement guarantees truth or that the procedure outperforms the best simpler baseline.

## Recompute the normalization analysis without models

From the selected B14 or B15 directory, use standard Python:

```sh
python3 analyze_normalization.py --raw NEW-RAW-RESPONSES.json --output-dir recomputed
```

The script refuses to overwrite existing result files. Only add `--all-raw-reviewed` after actually reading all raw responses; that flag records review status and does not change scores. Both exported packages were recomputed locally and matched all nine formal JSON outputs after JSON serialization, excluding the summary's run timestamp and raw-file hash metadata. Recalculation adds zero model forwards. `INFERENCE-SPEC.PUBLIC.json`, where available, retains model revisions, tokenizer/weight hashes and generation settings while omitting private machine paths; weights and tokens granting model access are not distributed.

## Archive boundary

The complete pre/post Word and Excel files, editable personal-review fields, execution logs and local provenance receipts remain in the local batch archives. They are not represented as publicly uploaded or human-approved. This export contains no private natural-source corpus, conversation transcript, account credential, model weights or unrelated unpublished main-line changes.

`PUBLIC-MANIFEST.json` hashes each payload file, excluding itself to avoid a circular digest. The separate local publication allowlist also hashes that manifest and the day report. Remote synchronization is verified against the exact commit; preparing a local export is not by itself a successful upload.
