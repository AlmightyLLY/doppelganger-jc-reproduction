# EXP-20260825 — Gated-Checkpoint Access Audit

## Purpose

This record distinguishes unavailable experimental material from a failed or low-scoring model run. A gated checkpoint that cannot be downloaded must not be counted as evaluated or silently replaced with a different checkpoint.

## Llama 3.1

- Paper checkpoint: `meta-llama/Llama-3.1-8B-Instruct`
- Intended revision: `0e9e39f249a16976918f6564b8830bc894c89659`
- Paper Japanese-to-Chinese official accuracy: 72.08%
- Final status: access request denied
- Model weights downloaded: no
- GPU Pod created: no
- Reportable accuracy: none

Llama 3.1 remains the missing seventh paper checkpoint.

## Gemma 7B

- Paper checkpoint: `google/gemma-7b`
- Fixed revision: `ff6768d9368919a1f025a54f9f5aa0ee591730bb`
- Initial preflight result: `403 GatedRepoError`
- Later status on the same day: access granted
- Final run: completed, 281/462 = 60.82%

No mirror, instruct variant, or Gemma 2 checkpoint was used in place of the paper model. The initial access failure is preserved even though the checkpoint later became available. See the [Gemma run record](EXP-20260825-gemma-7b.md).

## Final exact-model coverage

- Completed paper checkpoints: 6/7
- Not run because gated access was denied: 1/7

This does not constitute a 7/7 reproduction and is not reported as one.
