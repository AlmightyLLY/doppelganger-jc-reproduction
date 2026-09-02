# Research Progress Since the Wave 2 Human Audit

Date: 2026-09-03
Public baseline: commit `91bae0a560eb948303b2ba753044dd3e3a093a25`

## Summary

Since the Wave 2 human-audit confirmation, the project has moved from
phenomenon validation into mechanism and decision-utility pilots. The new
development evidence strengthens two conclusions: contextual information can
improve lexical-relation judgments, and alternative reasoning branches can be
correct on different items. It does not yet support a reliable selector,
automatic correction policy, or internal-mechanism claim.

The main research route is now **Counterfactual Utility-Guided Minimal
Translation Repair and Escalation (CURE-JC)**: decide among `KEEP`,
`MINIMAL_EDIT`, and `ABSTAIN` according to expected downstream utility. A
separate lexical-conflict mechanism pilot has reached a fully frozen
pre-model stage. The fresh-math study remains a secondary transfer test and
has not produced a formal utility result.

## New completed development results

### Contextual lexical-relation signal

On the 22-item frozen development set, word-only classification was correct on
11/22 items (50.0%), while full-context classification was correct on 18/22
items (81.8%). This is evidence that context contains useful relation
information. It does not show that a relation label alone can select the best
translation action.

### Open-output branch complementarity

A 22-item open-output audit compared Original and Verification branches using
single-reviewer, assisted-draft annotations:

- Original strict acceptability: 10/22;
- Verification strict acceptability: 8/22;
- itemwise human-outcome Oracle: 15/22;
- Verification-only rescues: 5;
- Original-only correct cases: 7.

Thus, Verification had a net loss of two items as a fixed policy even though
the branches had substantial complementarity. The frozen selector used in
that experiment scored 6/22. The result is
`DOWNSTREAM_BRANCH_HEADROOM_PRESENT_SELECTOR_NOT_IMPROVED`. These annotations
are not independent double-human or native-speaker gold.

### Utility-proxy selector feasibility

In the follow-up 22-item selector feasibility test, both candidate orderings
were classified as `NEITHER` on every item. The required fallback therefore
selected Original throughout, scoring 10/22 and recovering 0/5
Verification-only rescues. The registered result is
`EXP_R3_SELECTOR_FEASIBILITY_GATE_FAIL`.

### Larger development-set branch test

On 1,522 development items, the closed-choice results were:

| Policy | Accuracy |
|---|---:|
| Baseline | 52.760% |
| Verification | 53.417% |
| Selector | 53.285% |
| Itemwise Oracle | 55.519% |

There were 42 Verification-only successes and 32 Baseline-only successes. The
Oracle headroom over the best fixed branch was only 2.102 percentage points,
below the registered decision threshold. The result is
`EXP_R5A_NO_GO_NO_CLOSED_CHOICE_BRANCH_HEADROOM`. This was a development-only
analysis on a previously used benchmark; the sealed diagnostic test remained
unopened and unscored.

### Fresh relation holdout limit

The fresh relation holdout contained 17 admissible items: 14 `SAME` and 3
`DIFFERENT`. It therefore failed the minimum 5/5 balance requirement and was
closed as
`EXP_R4_FRESH_RELATION_HOLDOUT_NO_GO_INSUFFICIENT_HUMAN_CONFIRMED_DIFFERENT`.
No confirmatory relation-generalization claim is made.

## CURE-JC status

The negative selector results changed the target from relation-routed
full-sentence verification to direct decision utility over `KEEP`,
`MINIMAL_EDIT`, and `ABSTAIN`.

An internal 60-item Qwen3-8B generation kill test was run at a pinned model
revision. Candidate generations frequently failed the intended action space:
some were unchanged, fragmentary, contained analysis traces, or rewrote more
than the local target span. The review was AI-only and two-pass, not human
gold. Consequently:

- no positive CURE-JC feasibility claim is registered;
- no selector was trained from those outputs;
- a fresh Phase 0 must enforce genuinely local edits and use at least two
  independent bilingual reviewers;
- progression requires at least five percentage points of Oracle headroom.

## Lexical-conflict mechanism pilot

The revised pilot has passed its data and human-review gates and is frozen at
`LEXICAL_CONFLICT_PILOT_V2_PRE_MODEL_READY`:

| Property | Frozen value |
|---|---:|
| Items | 120 |
| `SAME` / `DIFFERENT` | 25 / 95 |
| Japanese→Chinese / Chinese→Japanese | 60 / 60 |
| Development / held-out | 96 / 24 |
| Frozen prompts | 720 |
| Human-reviewed replacements | 19 |
| Formal model forward passes at cutoff | 0 |

All 120 items have distinct item IDs, lexical components, and contexts. The
public provenance hashes are:

- final sample: `7329bfb236e0d2cb0f7d51564e7222b6de35790e6ec037059020780037a38915`;
- split: `dc6d416c89e39f8001ecf2df9ec7efb1e440e7ff388c2476f95527e54c88fd2e`;
- prompt manifest: `4c1189c2b4aad18face7625e768bc5312ab1f7449ef6c2477dcfa590fc8998b2`;
- version manifest: `2db1c40982f8ad09bdc8ad2204f7493691af8a6898e93a48a9f015e43b7f394f`.

At this cutoff, no formal Qwen3-8B forward pass, Logit Lens analysis,
activation patching, or held-out evaluation had been run. The pilot therefore
does not yet support claims about late-layer suppression or causal recovery.

## Fresh-math side study

The cleaned source contains 1,333 admissible records from 1,527 published
rows, with an 80-item screening set and a 300-item primary set. The first
laboratory run stopped after 70 checkpoints under the earlier exclusive-GPU
rule. It did not reach the formal screening gate. A non-formal diagnostic found
4 valid responses, 63 without a valid final answer, and 3 truncated responses.
Even if all 10 unobserved items had passed, the maximum possible screening
score would have been 14/80, below the 76/80 gate.

The status remains `UTILITY_PILOT_BLOCKED`; this is a pipeline-format failure,
not evidence about correction utility. A revised run is in preparation. The
study uses shared laboratory compute when memory permits, with no paid RunPod
fallback authorized.

## Current research position

Completed evidence now covers reproduction, measurement audit, causal input
intervention, contextual relation characterization, branch-complementarity
tests, and rejection of two weak selector formulations. The project is now
between **mechanism validation** and **candidate-generation feasibility**.

The next evidence-bearing steps are:

1. run the frozen lexical-conflict development split;
2. proceed to patching only if the registered observational gates pass;
3. rebuild CURE-JC Phase 0 around constrained local edits and independent
   bilingual review;
4. retain fresh math as a secondary transfer check rather than the main claim.

The present package can support a rigorous pilot or negative-results account.
It cannot yet support a deployable correction system, a confirmatory selector
claim, or a causal internal-mechanism conclusion.

## Public/private boundary

This note publishes only aggregate results, registered statuses, and hashes.
Source sentences, candidate translations, human-review workbooks, raw model
generations, credentials, laboratory host details, and operational logs remain
outside the public repository.
