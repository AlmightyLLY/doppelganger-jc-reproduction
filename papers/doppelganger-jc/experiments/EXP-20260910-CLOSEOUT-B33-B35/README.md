# 2026-09-10 research closeout: B35 review and B33–B35 archival

This closes the current Main-window work session. Experiment IDs retain their
original 2026-09-09 dates; final review and this publication are recorded on
2026-09-10 in the local research-day convention. This is an archival summary,
not a retrospective preregistration. B33 and B34 are prior completed batches
included to resolve the publication backlog since the B26–B32 release.

## Scientific progression

| Batch | New generated answers | Question | Main finding |
|---|---:|---|---|
| B33 | 3,264 | Does the B32 layout contrast persist in 24 new author contexts? | Primary reversal differences 37/96 and 1/4 retain the predicted direction. |
| B34 | 3,264 | Does shared identity amplify the R2 layout contrast? | Shared-minus-disjoint contrasts H=1/6 and 7/16; the second includes an opposite layout contrast in disjoint records. |
| B35 | 3,456 | Does exchanging the target pivot's role modulate that interaction? | K=17/48 and 61/96 supports the preregistered directional rule; aggregate H changes sign in both mention strata. |

The 9,984 generated answers are not 9,984 independent linguistic observations.
B34 reruns 864 exact earlier prompts; B35 reruns 1,728. Both bridges reproduce
prior text and output tokens, but are not independent confirmation. B34 and B35
use the exposed B33 contexts. All use a single Qwen3-8B snapshot and six previously
used predicates. References and scores are author/AI judgments, not independent
human gold. Human review remains pending.

## B35: what was established

The target remains passive; only its two names are exchanged. The distractor and
other paired task conditions remain fixed. This changes the target roles and
correct answer, so it is not a meaning-preserving repair intervention.

For each R2 pivot mention position, D is the reversal-rate difference between
R2 pivot actor and pivot undergoer, using that fixed axis for both target roles.
H=D_shared-D_disjoint. K=H_target-undergoer-H_target-actor.

| R2 pivot mention | H: target undergoer | H: target actor | K |
|---|---:|---:|---:|
| FIRST | 1/6 | -3/16 | 17/48 |
| SECOND | 7/16 | -19/96 | 61/96 |

Both K values are positive and meet the frozen rule. In this batch H also
actually changes sign; K positivity alone would not establish a sign reversal.
The change is mainly in the shared-condition layout contrast, rather than a large
shift of the disjoint baseline. These are finite-material contrasts and
classification identification bounds, not confidence intervals or significance tests.

All 3,456 responses were independently re-parsed in Main and checked against
roles mechanically rederived from R1: 2,980 correct, 463 reversed, 13 other wrong.
Coordination & Operation additionally reports actual reading of all 1,562
selected complete responses (781 sources), without changing frozen scores.
Mechanical agreement and AI reading do not establish independent human validity.

## Counterexamples and scope boundaries

- Target-first K=(-1/24,19/48), whereas target-last K=(3/4,7/8). The first
  target-first contrast does not follow the prediction. Do not claim invariance
  to record order.
- Across 24 contexts, FIRST K is positive in 16, zero in seven, negative in one;
  SECOND is positive in 21 and zero in three. Only 15 contexts have both K>0.
- Each of six predicates and each leave-one-predicate-out aggregate retains two
  positive K values. This is internal sensitivity analysis, not independent replication.
- Single-record performance is 383/384 correct, with one UA role reversal.
  All 40 capability references pass their thresholds; threshold passage does
  not imply perfect ability or correct role assignment in dual records.
- Switching AU to UA yields 331 wrong-to-correct and nine correct-to-wrong pairs;
  eleven reversals become other errors, not rescues. AU has 1,329/1,728 correct
  and UA 1,651/1,728. This is promising local sensitivity, not reliable general repair.
- R2 layout changes yield 134 rescues and 133 new harms. Target-role changes
  yield 83 rescues and 145 harms, but change the gold answer. Different pair
  families overlap and must not be added as independent benefits.
- Two new-arm errors copy the entire R2 participant pair; eleven old-arm other
  errors assign one person to both roles. Reversal alone does not cover all failures.

## Interpretation and next decision

The current evidence supports conditional behavioral interaction between target
and distractor role arrangements. The important advance is a sharper prediction
and a clearer failure boundary, not a universal method or an internal mechanism.

Target roles co-vary with target name positions. R2 role-by-mention manipulations
also determine voice. Sharing changes repeated identity and entity count. A
surface-position or output-order account remains a serious alternative to a
pure semantic-role account. Some raw examples keep the same answer after R1 roles
swap, changing correctness without showing sensitivity to the target update.

The proposed next priority is a minimal contrast that separates competing
semantic-role and name-position/output-order predictions, explicitly retaining
record-order counterexamples. Only after freezing a discriminating prediction
should new materials and another model test its scope. No B36 is authorized or
run by this closeout. The existing professor-report deck remains through B32;
B33 onward belongs to the following reporting cycle.

## Deliverables and publication boundaries

B33–B35 each have actual pre-run Word/input Excel and post-run Word/result Excel,
frozen configurations, complete local archives and recorded pending human review.
The B35 final native file hashes and 181-file archive were checked by Main.
This release rechecks 589 archived files across the three batches.

Each ZIP includes exact synthetic model messages and complete answers, token
records, per-answer scores and condition metadata, selected frozen statistics,
a protocol excerpt and hash commitments for four native Word/Excel artifacts.
The protocol excerpts are derivatives of the original frozen records, not newly
registered predictions. Full originals remain locally archived.

Personal review containers, private judgments, account/environment logs, secrets,
sealed material and unrelated presentation/A-line files are excluded. This is a
public scientific subset, not a complete cloud backup of the private workspace.
Publication does not mean human review or independent confirmation is complete.
The release is additive to the existing research branch and preserves its prior
public history. Current workflow is Main → Coordination & Operation, with the
latter executing directly at Astra medium; no worktree or third-tier task is used.
