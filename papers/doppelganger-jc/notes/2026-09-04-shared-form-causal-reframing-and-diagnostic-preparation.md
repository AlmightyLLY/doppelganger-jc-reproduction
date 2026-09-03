# Research Log: Shared-Form Causal Reframing and Diagnostic Preparation

Date: 2026-09-04
Public baseline: commit `12c0a14490336ffa91c3e25451357347288848c3`

## Summary

Since the previous public update, the lexical-conflict pilot has moved from a
frozen pre-model design through development execution, a sealed eligibility
check, and a principled stop. The resulting evidence did not justify the
planned activation-patching route. It did, however, motivate a sharper
behavioral question:

> When the same written form is helpful under a `SAME` relation and misleading
> under a `DIFFERENT` relation, can a model use context to selectively preserve
> beneficial transfer while suppressing harmful attraction?

This reframing is now the center of the project. A new exploratory design
produced a directionally consistent contextual-suppression component across
three model families, while also showing that the original three-way
interaction was underpowered and sensitive to candidate order. The intended
paper contribution is therefore becoming a **diagnostic benchmark and strong
analysis**, not a new architecture or training method.

No confirmatory human-grounded result is claimed. The strongest current
evidence is exploratory, and material construction plus independent bilingual
adjudication remain the main bottlenecks.

## Lexical-conflict V2 execution and stop point

The frozen V2 development split was executed on Qwen3-8B using shared
laboratory compute at zero cash cost:

- 96 development items and 576 frozen prompt presentations;
- 37 recorded representation points, including the embedding output and all
  transformer layers;
- exact final-layer equivalence on all 576 presentations;
- order-averaged `FULL` accuracy of 68/96 (70.83%);
- all 28 order-averaged `FULL` errors occurred on `DIFFERENT` items;
- content-decision stability across candidate orders of 211/288 (73.26%).

On `DIFFERENT` items, `CONTEXT_ONLY` rescued 17 `FULL` errors and harmed 2
correct `FULL` decisions. `FORM_ONLY` rescued 2 and harmed 19. These results
support the descriptive claim that context carries useful disambiguating
information and that form alone can be harmful. They do not identify an
internal causal mediator.

The synthetic hook and implementation gate passed all 22 checks. The sealed
held-out eligibility run then evaluated only the authorized `FULL` baseline in
both candidate orders. One required gate failed: the held-out split did not
contain at least three qualifying conflict errors, although baseline-correct
`SAME` controls did exist. Under the frozen protocol, development activation
patching, layer selection, and held-out patching were therefore not run.

This is a closed experimental branch, not a finding that the broader research
question is false. It specifically says that this split could not support the
registered patching test.

## V3 shared-form causal identification

The V3 design separates three questions that accuracy alone cannot answer:

1. **Occurrence:** how often does a model select the harmful shared-form
   candidate on `DIFFERENT` items?
2. **Form intervention:** does replacing a source expression with an
   orthographically nonshared counterpart change the shared-candidate margin?
3. **Context moderation:** does context reduce that form-driven preference,
   while preserving useful shared-form behavior on `SAME` items?

The first sealed exploratory run contained 40 active items and 400 frozen
presentations. On Qwen3-8B, the original
`orthography × context × relation` interaction was positive at 1.2063, but its
cluster-robust uncertainty was large: unadjusted `p = 0.1887` and stratified
bootstrap 95% interval `[-0.4125, 2.8375]`. It is not a supported confirmatory
effect.

The decomposition was more informative. The `DIFFERENT` contextual-
suppression component, denoted `S_D`, was -1.5875. Descriptively, beneficial
shared-form utilization was 97.5%, harmful shared-form attraction was 18.75%,
and their calibration gap was 78.75 percentage points. Mean absolute
candidate-order sensitivity was 3.3063 margin units, so order could not be
treated as a cosmetic nuisance.

## Cross-model bridge

The exact frozen presentations were then run once on two additional model
families, without rerunning Qwen3-8B:

| Model | Original interaction | `S_D` |
|---|---:|---:|
| Qwen3-8B | 1.2063 | -1.5875 |
| Mistral-Nemo-Instruct-2407 | 0.0516 | -0.0859 |
| Granite-3.3-8B-Instruct | 0.1438 | -0.3250 |

The original interaction was positive at the model-average level but failed
its prospectively frozen order-concordance rule in both new models. It was not
promoted. In contrast, `S_D` was negative in all three models, in both language
directions, and in both candidate orders for each new model. Neither new model
showed catastrophic `SAME` collapse. The two new-model intervals nevertheless
crossed zero, so this is a directional bridge result rather than a
confirmatory replication.

A 20,000-repetition sensitivity analysis found that, even at 80 active items
per direction-by-relation cell, the pilot-scale `S_D` test reached only 0.5324
power, although its two-direction sign stability was 0.8607. The original
interaction was weaker. No finite confirmatory sample-size recommendation was
available within that grid.

## Human-grounded Main design and construction status

The prospective Main design now makes human-adjudicated `DIFFERENT` `S_D` the
unique primary endpoint. It is order-symmetrized, standardized within model
and direction using blinded variance, and averaged with equal weights over a
fixed model panel and the two language directions. `SAME` preservation is a
guardrail rather than a source of apparent improvement through indiscriminate
rejection of shared forms.

The current design target is 440 active human-adjudicated items: 120
`DIFFERENT` and 100 `SAME` items per direction. A separate conservative
simulation with variance inflation estimated 0.9368 power at the standardized
smallest effect of interest, but this remains a design calculation rather than
empirical evidence.

Human gold does not yet exist. AI-assisted, source-grounded construction is
being used only to establish feasibility and to prepare review material. At
this cutoff, five exploratory items were source-complete and independently
reproducible. Two repaired items had both an independent AI pass and explicit
PI acceptance and were frozen as `AI_PI_SCREENED_EXPLORATORY_CONSTRUCTION`,
not as human gold. Three unresolved materials remain excluded or under
revision. Definitions for the context-reduced and orthography-reduced controls
have been separated into a protocol clarification and remain subject to PI
approval before further construction.

## Theory-directed diagnostic preparation

The project has also begun a local, no-model diagnostic preparation inspired
by recent work on theoretically directed errors. The proposed prompt families
separate:

- a neutral baseline instruction;
- a length- and style-matched but non-diagnostic rule;
- an item-specific, source-grounded sense gloss.

These prompts are crossed with the orthography manipulation and both candidate
orders. The planned primary diagnostic contrast asks whether the item-specific
gloss suppresses harmful shared-form attraction on `DIFFERENT` items beyond a
matched generic rule. Generic reasoning instructions and ordinary chain-of-
thought prompts remain separate future interventions rather than being folded
into this contrast.

A four-item prototype audit exposed material defects before any model run. Two
core prototypes were retained unchanged and two entered targeted repair. The
repair audit was still in progress at this cutoff. No diagnostic model output
has been generated.

## Metric interpretation

The project will use linguistically interpretable labels without presenting
algebraic renaming as metric novelty. Under the current two-choice task and
identical masks, weights, and tie rules:

- harmful shared-form attraction on `DIFFERENT` items equals
  `1 - accuracy_DIFFERENT`;
- the relation-calibration gap is a linear transformation of balanced
  relation accuracy.

Their value is explanatory: they distinguish beneficial shared-form use from
harmful shared-form attraction. The causal evidence must come from the frozen
orthography and context contrasts, order controls, cross-model replication,
and human-grounded materials.

The evidence hierarchy is now explicit:

1. **Encoding:** relevant information is present in internal representations.
2. **Decision use:** manipulating form, context, or a diagnostic rule changes
   the candidate margin.
3. **Causal mediation:** a content-specific internal intervention changes the
   decision beyond matched controls.

The V2 stop point prevents a causal-mediation claim. The V3 behavioral results
currently address decision use only at an exploratory level.

## Reading integrated into the design

Two papers were studied in parallel with the experimental work.

The completed reading of Anthropic's
[Reasoning Models Don't Always Say What They Think](https://www.anthropic.com/research/reasoning-models-dont-say-think)
reinforced an important boundary: generated reasoning text is a behavioral
output and cannot, by itself, be treated as a faithful report of the internal
mechanism. Native model thinking, an ordinary chain-of-thought instruction,
and a targeted diagnostic rule will therefore be analyzed as distinct
interventions.

Reading is ongoing for Ma and Miyao's
[The Imperfective Paradox in Large Language Models](https://aclanthology.org/2026.acl-long.689/).
The most relevant lesson so far is to define a theoretically predicted error
direction, then test whether a controlled intervention changes that specific
error while preserving the complementary behavior. This supports the
project's shift from generic accuracy gains to relation-calibrated use of
shared form. It does not justify copying the paper's task or treating the
current descriptive rates as a new statistical method.

## Fresh-math side study

The revised MMLU-Pro utility screen completed all 80 authorized screening
items on shared laboratory compute. Sixty-five outputs were valid, seven were
truncated, and valid-output accuracy was 95.38%, leaving only three valid
errors. The frozen screening gate did not pass, and the primary correction-
utility stage did not start.

This resolves the immediate engineering question but still does not estimate
correction utility: the screened task-model-prompt combination produced too
few valid errors and insufficient output yield for the registered rescue/harm
analysis. The math route remains secondary to the shared-form research.

## Current research position

The project has advanced from asking whether Japanese-Chinese shared forms
cause errors to asking whether models are **selectively calibrated** to use
the same cue when it is semantically helpful and suppress it when it is
misleading. The most defensible present claim is:

> Across three exploratory model families, context shifts the `DIFFERENT`
> shared-form preference in the predicted direction, but the effect is not yet
> statistically confirmed, the original interaction is order-sensitive, and
> the materials are not yet independent bilingual human gold.

The next evidence-bearing steps are:

1. finalize the control definitions before scaling construction;
2. complete and audit the four-item theory-directed diagnostic prototype;
3. prepare a bilingual calibration and adjudication packet before recruiting
   independent reviewers;
4. expand source-grounded materials without opening protected reserves;
5. run larger or multilingual experiments only after material and human-gold
   gates are met.

This is a plausible foundation for a strong analysis paper. It is not yet an
ACL Main-level empirical package, a new-method contribution, or a causal
mechanism result.

## Public/private boundary

This note publishes only aggregate results, methodological decisions, and
epistemic limits. Source sentences, candidate materials, review workbooks,
raw model outputs, credentials, laboratory host details, protected reserves,
and operational logs remain outside the public repository.
