# Manual Review of 34 Shared `wrong1` Errors

## Sample boundary

The original review package contained 67 items that Qwen-1M, llm-jp, and ELYZA all answered incorrectly under official scoring. The first 34 reviewed items all belong to the `unanimous_wrong1` subset. This targeted sample is useful for identifying shared failure modes but cannot estimate their prevalence in the full 462-item dataset.

The judgments below are development annotations from one reviewer and have not been validated by a second bilingual annotator.

## Descriptive summary

- Preferred candidate 0: 26 items
- Preferred `wrong1`: 6 items
- Candidates 0 and 1 both acceptable: 2 items
- Shortcut-related: 17/34
- Ambiguity or label-boundary concern: 19/34
- Both shortcut-related and ambiguous: 2 items
- Still unanimous `wrong1` under candidate-only scoring: 27/34
- Exact / variant items: 20 / 14
- Shortcut-related within exact / variant: 10 / 7

## Reviewed items

The public record retains item indices and judgments but not benchmark lexical
content. The 34 reviewed indices were 11, 53, 76, 111, 113, 142, 171, 175,
179, 180, 189, 243, 277, 283, 288, 291, 294, 298, 300, 318, 319, 321, 331,
345, 349, 352, 354, 369, 370, 373, 374, 376, 382, and 384. The aggregate
category counts above are the stable public review result; item text can be
rejoined locally from the pinned upstream checkout.

## Interpretation

Dataset quality and shortcut behavior are not mutually exclusive explanations. Some `wrong1` options are clear form copies or unnatural Chinese collocations; others are fluent, understandable, or arguably preferable to candidate 0.

Future annotation should distinguish at least `clear_shortcut`, `multiple_valid`, `label_questionable`, `semantic_drift`, and `needs_second_annotator`. A single strict label should not convert all benchmark disagreements into the same model-error category.
