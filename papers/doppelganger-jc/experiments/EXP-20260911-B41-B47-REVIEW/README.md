# B41–B47: role extraction, output order, and limits of transfer

Research closeout covering experiments dated 2026-09-10 and completed locally after midnight on September 11. All results are AI-authored, outcome-exposed developmental evidence; independent human reviewers and independent gold remain **zero**. C/W/U are the frozen complete-correct/contradictory/unresolved labels, not interchangeable with JSON compliance. AU outputs actor first; UA outputs undergoer first. D_AU/D_UA independently vary definition order.

## Research trajectory

| Batch | Question | Finding and boundary |
|---|---|---|
| B41 | Is the original joint task usable? | AI review of 48 items found no mandatory reference change. Not human construct validation; no new model calls. |
| B42 | Transfer to new verbs/scenarios on Qwen? | Passive-negative double-record AU30/48→UA43/48; 13 rescues, no new losses locally, predominantly target-last. Whole-batch harms remain. |
| B43 | Transfer to Apertus? | Same local endpoint 13/48→27/48. Across all conditions 47 rescues versus 50 new losses; active and passive show opposing preferences. |
| B44 | Does definition order matter? | Qwen passive-double UA advantage 27.08→8.33 percentage points. Apertus mean change small but position effects cancel. No universal definition repair. |
| B45 | Does shared identity amplify the schema gap? | No uniform cross-system interaction. Removing overlap yields Apertus 42 rescues/0 new losses under the original definition, but changes background facts and is not a deployable repair. |
| B46 | Prospective predictions on new narrative contexts? | Four-cell joint prediction **failed**: Qwen D_UA target-last G=0, with three rescues and three harms. Three other cells positive; cannot override the failed cell. |
| B47 | Do narrower findings survive cyclic name-role reassignment? | Qwen definition contrast H=38.89pp; two new mappings H=33.33pp. Apertus mean active-AU/passive-UA preferences persist. B46 failure remains unchanged. |

## Read the evidence

- **B41**: [summary](B41-summary.md), [machine-readable full evidence](B41-evidence.json)
- **B42**: [summary](B42-summary.md), [machine-readable full evidence](B42-evidence.json), [Main design](B42-design.md)
- **B43**: [summary](B43-summary.md), [machine-readable full evidence](B43-evidence.json), [Main design](B43-design.md)
- **B44**: [summary](B44-summary.md), [machine-readable full evidence](B44-evidence.json), [Main design](B44-design.md)
- **B45**: [summary](B45-summary.md), [machine-readable full evidence](B45-evidence.json), [Main design](B45-design.md)
- **B46**: [summary](B46-summary.md), [machine-readable full evidence](B46-evidence.json), [Main design](B46-design.md)
- **B47**: [summary](B47-summary.md), [machine-readable full evidence](B47-evidence.json), [Main design](B47-design.md)

B42–B47 evidence includes actual messages, full scored outputs, raw generated outputs/token records as available in the archived run results, paired transitions, analyses and QA. Download the JSON files if GitHub cannot preview their size. B41 contains the AI item audit, not a new model experiment. B42–B47 contain 576+576+1152+1920+1152+1152 = **6528 fresh calls**; these are not 6528 independent scenes. The analyses use scene pairing and 12 predicate blocks where specified.

## Claims that must not be made

No universal harmless repair, proven internal role-binding mechanism, independent human validation, or natural-text generalization has been established. Native templates differ between systems. A small average interaction does not establish absence; improvements can coexist with new harms. B45 replacement names were concentrated in two identities. B46 name assignment aliased names with roles; B47 uses three cyclic permutations, not all six, and retains the same scenes/name pool. Original frozen scores and failed predictions are preserved.

B46 encountered an Apertus native date mismatch before any AP call started; a process-local UTC setting restored all frozen texts/tokens, and failure/recovery time was counted within budget. B47 ROT0 historical inputs/outputs/scores matched B46 in all 384 pairs. Resource and QA claims are documented in the evidence; no further batches are authorized by this publication.

Original personal-review Word/Excel files and blind-review packages remain local. [Hash commitments and omissions](LOCAL-ARCHIVE-COMMITMENTS.json) document this boundary. This public release is a research evidence subset, not a complete private backup. Earlier history: [B36–B40 review](../EXP-20260910-B36-B40-REVIEW/README.md).
