# Research Log: V3.5 Diagnostic Evidence and Representation Audit

Date: 2026-09-05
Public baseline: commit `a54fe957baf763c759c467867add23498551c99b`

Public synchronization note (2026-09-06): the following correction was already
completed locally on September 5 and is published with the
[September 6 synthesis](2026-09-06-research-results-and-paper-assessment.zh-CN.md).
The [original public version](https://github.com/AlmightyLLY/doppelganger-jc-reproduction/blob/d6309b9eff661f54a036e283f2b01f84be3c2407/papers/doppelganger-jc/notes/2026-09-05-v3-5-diagnostic-and-representation-audit.md)
remains available in history. Independent audit here refers to the separate
review task; it is not independent bilingual human annotation.

Interpretation correction added on 2026-09-05 after an independent audit:
the numerical results below are retained, but V3.5B confounds note validity
with exact correct-candidate repetition, and V3.5C's manipulated sense suffix
is outside the measured focus positions' causal context. Application transfer
was not measured. The revised interpretation below supersedes stronger
semantic-specificity or form–sense-dissociation readings of this progress note.

## Summary

Since the previous public update, the project has moved from a small
theory-directed diagnostic prototype to a balanced 40-family exploratory
design with two complementary components:

1. a behavioral note comparison intended to test semantic specificity
   (`V3.5B`); and
2. a form-by-meaning representation measurement (`V3.5C`).

The strongest new result is behavioral. On the frozen Qwen3-8B run, an
item-specific applicable note changed the decision margin more than an
equally framed but item-inapplicable note. The four-cell equal-weight
`Delta_specific` estimate was 2.09375 with a stratified item-family bootstrap
95% interval of `[1.75233, 2.43945]`.

The same wrapper controls its formatting, but the content comparison is
confounded: all 40 applicable notes contain the exact correct candidate,
whereas none of the 40 shuffled notes do. All 320 actual runtime prompts
preserve this asymmetry. The observed effect can reflect candidate repetition,
lexical priming, applicability, semantic correctness, or a combination. It does
not identify semantic-specificity, and it does not prove that the model was
copying. Application transfer has no observations and is reported as N/A.

The representation run exposed a measurement and execution issue.
Target-span representations were recovered for every frozen prompt and
layer, but the registered decision-site comparison was not identifiable from
the exported states. In addition, apparent candidate-order differences were
traced to padded-batch numerical context rather than to the linguistic order
manipulation. Those analyses were stopped rather than interpreted.

The immediate next step was therefore a prospective decision-site rerun with
symmetric member-specific companion prompts and fixed execution context. That
corrected run has now completed. Its all-layer descriptive curve compares
focus-site and companion pre-choice geometry. The later construct audit
establishes that the manipulated sense information follows the focus sites;
the curve therefore does not identify a learned local-semantic versus
decision-state dissociation.

A subsequently frozen post-result robustness analysis used the 40 item
families as independent clusters, retained all 36 layers and both orders, and
applied a leave-one-family-out common-mean correction. The association survived
that correction. The zero sense contrasts at the focus sites are structural
zeros for a suffix-only manipulation in a causal decoder. The companion
pre-choice states can see the varying suffix and differ descriptively, but
the suffix also changes literal gloss content and candidate overlap. These
measurements retain descriptive value and motivate a better design; they do
not establish a form–sense dissociation or semantic transmission.

## V3.5A material expansion and review

The exploratory material pool was expanded through result-blind,
source-grounded construction, isolated AI adversarial review, and explicit PI
item review. Retired lexical components were not repeatedly rewritten merely
to satisfy a target count.

The resulting intake contains:

- 40 core item families, balanced at 10 per relation-by-direction cell;
- six retained exploratory backups;
- frozen `O+` and `O-` expressions, candidates, focus spans, source fields,
  and bilingual atomic propositions;
- explicit ledgers for naturalness, register, length, orthographic,
  tokenizer, semantic-granularity, and difficulty limitations.

The materials remain `AI+PI exploratory`. They are not bilingual human gold,
do not qualify a Main experiment, and cannot support a population-level
linguistic claim. The present role of the core 40 is to establish whether the
experimental contrasts are operationally and scientifically promising before
commissioning independent bilingual adjudication.

## V3.5B: semantic-specificity diagnostic

Each core family was paired with two neutrally framed supplemental notes:

- `G_TRUE_NEUTRAL`: an item-specific note that is applicable to the item;
- `G_SHUFFLED_NEUTRAL`: a note with the same framing but drawn from a frozen
  item exchange and therefore inapplicable to the current item.

Both arms used the same neutral wrapper, replacing an earlier explicit-unrelated
wrapper. However, the applicable note names the correct candidate directly.
Consequently the task does not require semantic applicability reasoning to
distinguish the two arms; a literal-match shortcut remains available.

The exact frozen Qwen3-8B execution covered 960 prompts across V3.5B and
V3.5C, with 120 forward calls. For V3.5B:

- accuracy was 298/320, or 93.125%;
- the frozen four-cell equal-weight `Delta_specific` was 2.09375;
- the 20,000-draw stratified item-family bootstrap interval was
  `[1.75233, 2.43945]`;
- every relation-by-direction cell retained 10 complete families;
- the frozen `SAME` safety check recorded no decision harms;
- the `DIFFERENT` residual `O` contrast was -0.51875;
- the mean frozen order-sensitivity difference was -0.040625.

The corrected interpretation is narrow: on this exploratory material and
model, a note that directly names the correct candidate changes the margin
relative to an equally framed note naming another item's meaning. The
historical endpoint name `Delta_specific` is retained, but semantic specificity
is not identified. This is a content-bundled exploratory contrast.

The upstream plan required application transfer, and every source family
contained an application record. The actual B schedule contained only 320
main-task prompts; the analysis adapter set `application_ids=[]` for every
family. Application transfer consequently has `n=0` and is **not measured
(N/A)**. No explicit prospective removal record was identified in the examined
lineage. The numerical main-task contrast remains valid for its scheduled
comparison, while complete upstream endpoint coverage and transfer claims are
unsupported. The omission is not remedied by retroactively adding new runs.

## V3.5C: what the first representation run established

V3.5C crossed shared versus nonshared form with same versus different meaning
in frozen tetrads. All 640 prompts and all 36 layers were retained. The run
produced 23,040 prompt-layer target-span rows, and the independent formula
recomputation matched exactly.

The decision-site analysis failed closed. A joint prompt supplied only one
final pre-choice state, while the frozen estimand required two independently
defined member-level states. No decision-site or global-minus-local result was
reported from that structure.

The order-invariance audit exposed a second issue:

- all 320 `XY`/`YX` pairs were text-identical through the second focus span;
- 319 pairs had nevertheless been evaluated in different shards;
- all 2,628 comparisons with the same paired-batch maximum length were
  exactly invariant;
- all 5,400 nonzero differences occurred when maximum padded length differed;
- the largest absolute discrepancy was 0.0184147141.

Candidate order therefore cannot be credited with those differences. They
are bound to execution context under padded batching. The target-span outputs
remain usable as qualified descriptive observations, but not as evidence of
order sensitivity, decision use, or mechanism.

This distinction strengthens the project's evidence hierarchy:

1. **Representation:** a site can only reflect manipulations visible in its
   causal context; content-specific encoding needs further controls.
2. **Behavioral sensitivity:** an input intervention changes a decision
   margin; semantic use additionally requires controls against simpler cues.
3. **Causal mediation:** manipulating an internal variable changes the
   decision beyond matched controls.

V3.5B contributes exploratory behavioral sensitivity to bundled note content.
V3.5C provides descriptive representation measurements and identifies
measurement limitations. Neither establishes semantic decision use or causal
mediation.

## Prospective repair and completed V3.5C-v2.2 run

The repair was designed before accessing any repaired-run result. It uses a
symmetric six-prompt forward group for each family and order:

- two joint prompts (`XY` and `YX`);
- four member-specific companion prompts, one per member and order.

The primary execution mode fixes every group to shape `[6,147]`, with global
right padding, explicit attention masks and position IDs, BF16, eager
attention, and a common execution context. The registered output comprises
all 36 layers and both orders; there is no result-driven layer selection.
The intended output remains a descriptive representation association.

The prospective schedule contains 1,920 prompts in 320 fixed groups. The
design preserves the same 40 families, estimands, directions, relations, and
model revision as the first run.

Two implementation attempts were stopped before scientific inference:

1. a registered seed exceeded the legacy NumPy seed range; and
2. a logical home path and its canonical mounted path were equivalent on the
   execution host but compared under inconsistent normalization rules.

Both failures occurred before any scheduled scientific forward and produced
no representation result. They do not alter the scientific design or prior
findings. They do reveal insufficient environment-faithful testing in the
custom fail-closed runner. The correction now requires a symlink-aware path
identity contract and a remote, no-model environment smoke check before a
full dispatch. Reusing a failed authorization or silently relaxing path
checks is prohibited.

After binding the exact validated Python environment, the unchanged V3.5C-v2.2
scientific run completed successfully:

- 1,920 frozen prompts in 320 fixed `[6,147]` forward groups;
- all 36 block-output layers and both candidate orders;
- 69,120 complete, unique, finite scalar records;
- approximately 1.13 GB of BF16 site tensors;
- complete formula, shape, hash, execution-mode, path, and source-binding
  validation;
- an independent recomputation of every reported association, grand mean,
  cell mean, and order diagnostic.

The descriptive equal-order association between the companion semantic-site
and decision-site quantities was 0.4427 at layer 1, rose to approximately
0.66 around layers 5--6, and declined to 0.1529 at layer 36. All 36 layers
remain visible; no layer was selected or promoted after observing the curve,
and no inferential test was applied.

The semantic-site quantities were exactly invariant to candidate order under
the fixed execution grouping. The companion decision-site quantity retained
a small order difference: mean absolute difference 0.00211 and maximum
absolute difference 0.04163 across 11,520 comparisons. This is reported as a
diagnostic property of the frozen companion prompts, not as proof of a
linguistic order effect.

The late-layer reduction in cross-site association is a descriptive curve.
It does not test preservation of the manipulated sense information: the focus
sites cannot see the varying sense suffix, while the final states can. It also
does not establish whether either site is used, necessary, sufficient, or a
mediator of the behavioral effect.

## Post-result robustness and factorial decomposition

After the original repaired-run curve had been observed, a separate analysis
charter was frozen for explicitly post-result exploratory robustness checks.
It treated the 40 item families, rather than the 320 repeated condition-by-form
units, as the independent bootstrap clusters. All 36 layers and both orders
were retained, with 10,000 fixed item-family bootstrap draws and no p-values,
binary gate, or result-selected layer.

The pooled `S_COMPANION`--`D_COMPANION` association remained positive across
all layers. Raw coefficients ranged from 0.1119 to 0.6491; coefficients after
leave-one-family-out common-mean centering ranged from 0.1081 to 0.6147. Every
layer's family-cluster percentile interval remained above zero in both
versions, and the mean absolute raw-versus-centered coefficient change was
0.0160. Subtracting this one shared direction therefore did not explain away
the curve, although it cannot remove every possible source of anisotropy or
template structure.

The factorial contrasts materially qualify the meaning of that association:

- `S_JOINT` and `S_COMPANION` showed positive shared-form contrasts at all 36
  layers, but their same- versus different-sense contrasts and interactions
  were exactly zero throughout the frozen schedule;
- `D_COMPANION` showed positive descriptive sense contrasts at all 36 layers
  before and after centering, including within each direction-by-`O`-form
  stratum;
- the raw decision-site cosine was strongly ceiling-compressed, with layer
  means between 0.9819 and 0.9999, whereas centering expanded the observable
  decision-site geometry;
- the decision-site form-by-sense interaction interval excluded zero at 31 of
  36 layers in the aggregate analysis, but its cross-stratum heterogeneity is
  retained as description rather than promoted into a new endpoint.

An additional material audit compared 1,280 focus-site pairs across the frozen
sense conditions. In all pairs, the full text prefix through the focus,
archived focus-token IDs/indices, prefix masks, and position IDs were identical.
The varying sense gloss follows the focus. Thus the zero sense contrast is an
expected structural zero, not empirical evidence that semantic encoding is
absent. Preceding source context can still carry semantic information; the
invisible quantity is this particular suffix manipulation.

The companion pre-choice state sees the varying gloss and can differ, but
literal gloss identity, template effects and candidate overlap remain plausible
explanations. The pooled association combines within-family and between-condition
structure. Common-mean centering does not control all these alternatives, and
36 layerwise intervals are not 36 independent replications or a simultaneous
confidence band. The complete results are retained as exploratory measurements
with these limitations.

## Auxiliary representation geometry

A separate 10-item `multilingual-e5-small` cosine pilot is retained only as a
measurement proof of concept. It showed that whole-input and target-span
similarities can diverge on its particular items. Bare shared-word cosine
near one is treated as an input-identity check, not as semantic evidence.

This auxiliary line will not be pooled with the generative-model result,
used to select layers or items, or described as proof of semantic confusion.
Any future geometry table must preserve the boundary
`encode != use != cause`.

## Implications for the paper

The emerging contribution is a diagnostic benchmark and strong analysis,
not a new model or training algorithm. The core question is becoming:

> Can a model selectively exploit a cross-lingual shared form when its meaning
> is preserved, suppress it when its meaning conflicts, and distinguish an
> applicable semantic cue from an equally framed inapplicable cue?

The audit clarifies what a future paper must establish. Candidate repetition
must be separated from semantic applicability; the manipulated information
must be visible at the measured representation site; and material, schedule
and analysis endpoint coverage must agree. The project has an exploratory
design and reusable infrastructure, but these B/C results do not yet supply
the proposed semantic-specificity or form–sense-dissociation contribution.

The numerical execution nuisance remains a reproducible measurement lesson.
A stronger analysis narrative depends on future controls and independent
language validation, not on promoting the number of layers or integrity checks
to scientific evidence.

The evidence is not yet ACL Main-ready. The principal missing components are
independent bilingual human adjudication, replication on additional frozen
model families, and a prospective confirmatory behavioral test with adequate
item-family coverage, together with correction of the content and visibility
confounds. A technical decision-site repair alone does not resolve them.

## Current status and next gates

At this cutoff:

- V3.5A core 40 and backup six are frozen as AI+PI exploratory materials;
- V3.5B has a positive, interval-separated but candidate-mention-confounded
  exploratory contrast on Qwen3-8B; application transfer is unmeasured;
- V3.5C-v1 is valid only for qualified target-span description;
- V3.5C-v2.2 completed with all-layer, both-order descriptive representation
  associations and independent recomputation;
- the V3.5C-v2.2 post-result robustness analysis is complete and independently
  recomputed: the association survives one common-direction correction,
  focus-site sense contrasts are structural zeros for the suffix manipulation,
  and descriptive condition differences occur at the companion pre-choice site;
- Main, reserve, held-out, CoT, probes, and activation patching remain closed;
- no paid compute is in use.

The next evidence-bearing gates are:

1. validate a small set of candidate-free note controls and causally visible
   sense manipulations, with explicit endpoint coverage;
2. obtain independent bilingual review of construct validity and freeze fresh
   confirmation materials before model outcome access;
3. run the resulting behavioral comparison on predeclared models and report
   its uncertainty, including null or heterogeneous results.

The correction package is recorded locally under
`research_notes/2026-09-05/v3_5bc_construct_validity_correction_v1/`.
It contains reproducible material/runtime checks, a revised interpretation
record, and a prospective design draft. The original sealed inputs and
numerical outputs are unchanged. No new model run was used for the correction.

## Public/private boundary

This note publishes aggregate results, methodological decisions, failure
boundaries, and epistemic limits. Source sentences, item texts, review
workbooks, prompt schedules, token IDs, raw outputs, representation vectors,
credentials, laboratory host details, protected reserves, and operational
logs remain outside the public repository.
