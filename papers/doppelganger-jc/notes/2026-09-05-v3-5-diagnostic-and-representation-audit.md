# Research Log: V3.5 Diagnostic Evidence and Representation Audit

Date: 2026-09-05
Public baseline: commit `a54fe957baf763c759c467867add23498551c99b`

## Summary

Since the previous public update, the project has moved from a small
theory-directed diagnostic prototype to a balanced 40-family exploratory
design with two complementary components:

1. a behavioral semantic-specificity control (`V3.5B`); and
2. a form-by-meaning representation analysis (`V3.5C`).

The strongest new result is behavioral. On the frozen Qwen3-8B run, an
item-specific applicable note changed the decision margin more than an
equally framed but item-inapplicable note. The four-cell equal-weight
`Delta_specific` estimate was 2.09375 with a stratified item-family bootstrap
95% interval of `[1.75233, 2.43945]`.

This is useful exploratory evidence that the model does more than respond to
the generic authority or format of a supplemental instruction. It does not,
however, eliminate a simpler applicability-gating explanation, establish a
human-grounded population effect, or identify an internal causal mechanism.

The representation run also produced a substantive methodological finding.
Target-span representations were recovered for every frozen prompt and
layer, but the registered decision-site comparison was not identifiable from
the exported states. In addition, apparent candidate-order differences were
traced to padded-batch numerical context rather than to the linguistic order
manipulation. Those analyses were stopped rather than interpreted.

The immediate next step was therefore a prospective decision-site rerun with
symmetric member-specific companion prompts and fixed execution context. That
corrected run has now completed. Its all-layer descriptive curve is consistent
with a late-layer separation between local semantic geometry and the final
companion decision-state geometry, but it remains association evidence rather
than evidence of behavioral use or causal mediation.

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

Both arms used the same neutral wrapper. The model, rather than the prompt,
had to determine whether the content applied. This replaced an earlier
explicit-unrelated wrapper that risked revealing the intended control.

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

The permitted interpretation is narrow: on this exploratory material and
model, the decision responds differently to applicable item-specific content
than to an equally framed inapplicable note. This is stronger than a generic
prompt-effect observation, but still compatible with applicability gating.
It is auxiliary evidence, not a confirmatory endpoint.

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

1. **Encoding:** information covaries with a frozen representation site.
2. **Decision use:** a controlled input intervention changes a decision
   margin.
3. **Causal mediation:** manipulating an internal variable changes the
   decision beyond matched controls.

V3.5B currently contributes exploratory decision-use evidence. V3.5C-v1
provides partial descriptive encoding evidence. Neither supports causal
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

The late-layer reduction in semantic-site/decision-site association is
consistent with a representation--decision-location dissociation: semantic
structure visible locally need not be preserved in the same geometry at the
pre-choice state. It does not show whether the model used the information,
whether either site is necessary or sufficient, or whether one mediates the
behavioral effect.

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

The new evidence improves the paper in three ways:

- it separates generic instruction effects from item-specific semantic
  responsiveness;
- it makes representation-versus-decision dissociation an empirical question
  rather than a rhetorical caveat;
- it documents a concrete numerical-execution nuisance that could otherwise
  be mistaken for linguistic order sensitivity.

The completed V3.5C-v2.2 curve adds a fourth contribution: it supplies a
prospectively repaired, execution-context-controlled comparison of semantic and
decision locations across every layer. This makes the distinction between
encoded information and decision-aligned geometry measurable, while leaving
the causal boundary intact.

The evidence is not yet ACL Main-ready. The principal missing components are
independent bilingual human adjudication, replication on additional frozen
model families, and a prospective confirmatory behavioral test with adequate
item-family coverage. A successful corrected decision-site run would improve
the analysis story but would still be association evidence rather than a
causal mechanism result.

## Current status and next gates

At this cutoff:

- V3.5A core 40 and backup six are frozen as AI+PI exploratory materials;
- V3.5B has a positive, interval-separated exploratory result on Qwen3-8B;
- V3.5C-v1 is valid only for qualified target-span description;
- V3.5C-v2.2 completed with all-layer, both-order descriptive representation
  associations and independent recomputation;
- Main, reserve, held-out, CoT, probes, and activation patching remain closed;
- no paid compute is in use.

The next evidence-bearing gates are:

1. decide whether the combined behavioral and representation evidence is
   strong enough to justify independent bilingual human annotation;
2. if justified, reproduce the behavioral effect with human-grounded
   materials and additional predeclared models.

## Public/private boundary

This note publishes aggregate results, methodological decisions, failure
boundaries, and epistemic limits. Source sentences, item texts, review
workbooks, prompt schedules, token IDs, raw outputs, representation vectors,
credentials, laboratory host details, protected reserves, and operational
logs remain outside the public repository.
