# Research Trajectory and Revised Research Agenda

Date: 2026-08-26  
Status: reflective synthesis and forward plan, not a claim of a completed new method

## Executive synthesis

This project began as a first paper reproduction and developed into a more
precise research question about cross-lingual lexical transfer. The initial
intuition was that a multilingual model, like a Chinese reader encountering an
unfamiliar Japanese kanji word, might use visible form or pronunciation to
construct a useful translation hypothesis without first retrieving an explicit
dictionary entry. The risk is that the same mechanism produces false-friend
errors: a plausible-looking form can be accepted before its contextual meaning
is adequately checked.

The reproduction changed the proposed solution. The evidence does not support
universally suppressing orthographic information. Removing visible kanji
overlap shifted model preference away from the homograph distractor on average,
but it did not reliably improve four-option accuracy. Orthography is therefore
neither pure noise nor an unconditional shortcut. It is a potentially efficient
lexical cue whose value depends on the item, context, model, and decision rule.

The revised research theme is:

> **Reliability-aware cross-lingual lexical transfer: when should a
> multilingual system trust orthographic or phonological similarity, and when
> should it trigger semantic verification or retrieval?**

This refines the original proposal rather than replacing it. The central
contribution would not be “use cognates” or “remove cognates,” but a calibrated
policy that distinguishes helpful transfer from risky form-based guessing and
measures the trade-off among accuracy, calibration, retrieval cost, and latency.

## 1. From reading code to reproducing the benchmark

The first learning problems were concrete: what the tokenizer contributes, how
next-token NLL becomes PPL, why PPL can be numerically large, and how four scores
become one selected answer. Tracing a single item established the operational
pipeline: each candidate receives an average NLL, PPL is its exponential, and
the minimum is selected. This later made it possible to identify that official
and candidate-only scores average different token spans.

A 0.5B Qwen run was used as an engineering and conceptual check, not as a
substitute for the paper's 7–8B checkpoints. A 20-item pilot then exposed
official-versus-candidate-only disagreements, motivating a data audit before
interpreting model differences. The audit found 464 cognate rows but 462
Japanese-to-Chinese questions, two cognate entries without questions, and three
questions with duplicated options. Questionable items were retained in the
strict paper-compatible view and excluded only in a separately named audited
view. This established an important habit: document data problems rather than
silently repairing them after seeing results.

Six accessible paper checkpoints were evaluated in both Translation Type-1
directions: 462 Japanese-to-Chinese items and 455 Chinese-to-Japanese items per
model, for 5,502 model–item decisions. Revisions, row counts, score finiteness,
and argmin choices were validated. The exact Llama 3.1 checkpoint was not run
because gated access was denied; it was recorded as missing rather than replaced
with a model that might only appear equivalent.

The aggregate reproductions were close to the paper. In Chinese-to-Japanese,
the mean absolute difference across the six accessible checkpoints was about
0.77 percentage points. Japanese-to-Chinese results were likewise within a
reasonable reproduction range while preserving model-specific variation.

## 2. What the reproduction revealed

### Homograph error concentration

The strongest descriptive pattern was concentration on `wrong1`, the candidate
constructed from the cross-lingual homograph. In Japanese-to-Chinese, `wrong1`
accounted for approximately 69.5%–85.3% of official errors across the six
models. Both translation directions showed nearly identical aggregate `wrong1`
shares, although model-level cancellation means this should not be interpreted
as one proven direction-invariant mechanism.

### Scoring and candidate length

Candidate-only scoring is not a human baseline and does not remove the source
context. It uses the same forward pass but averages loss only over candidate
tokens. It was introduced as a diagnostic because the official score includes a
large shared prompt whose denominator changes with candidate length.

Official scoring generally had higher aggregate accuracy, but candidate-only
identified measurement-sensitive cases. In Chinese-to-Japanese, the official
score selected the longer-token candidate in 287 of 298 disagreements. This is
evidence about the scoring formula and candidate distribution, not evidence
that a model consciously follows a “choose the longer answer” rule. The paper
metric remains primary for reproduction; candidate-only remains useful for
controlled source interventions. The length effect is documented, not fully
resolved.

### Manual review and benchmark uncertainty

Sixty-seven items were found on which the first three models were all wrong.
Thirty-four unanimous-`wrong1` cases received a first-pass manual review. The
review separated at least three phenomena:

1. clear form-copy shortcuts that produce an unnatural or semantically
   indefensible target sentence;
2. fluent semantic alternatives that differ from the reference interpretation;
3. label or item ambiguity, including cases where candidate 0 may not be uniquely
   preferable.

Seventeen of 34 cases were shortcut-related, while 19 raised ambiguity or label
boundary concerns; two belonged to both. These are diagnostic counts from a
targeted, single-annotator subset, not prevalence estimates. They show why a
large `wrong1` count can arise from form bias, candidate naturalness, reference
ambiguity, or several factors simultaneously.

## 3. From correlation to a controlled intervention

The initial causal hypothesis was that target-word kana conversion would remove
the misleading visual shortcut and improve accuracy. An original-versus-kana
comparison alone was insufficient because rewriting can change naturalness,
tokenization, and generic source encoding. The design therefore used:

1. the original source sentence;
2. target-kana, rewriting only the target form;
3. unrelated-control-kana, rewriting a comparatively unrelated source component;
4. an exploratory related-semantic-cue condition when a second control existed.

The primary candidate-only margin was

```text
margin = NLL(wrong1) - NLL(correct)
```

and the difference-in-differences estimate was

```text
orthography_effect =
    [margin(target_kana) - margin(original)]
  - [margin(unrelated_control_kana) - margin(original)]
```

A positive effect means that removing target-word kanji overlap moves relative
preference toward the correct candidate more than an unrelated kana rewrite
does.

Control design changed during material review. A semantically important or
closely related word can itself remove translation evidence, so it is better
interpreted as a semantic-cue ablation than as a neutral control. The unrelated
component became the primary negative control; related controls were retained
as sensitivity analyses. This was a substantive research decision, not a
formatting change.

The full material contained 450 usable items, 411 of which supported both
control types. The preregistered primary set contained 382 holdout items with
non-weak negative-control proxies. Across six models, the fixed-model-set mean
orthography effect was +0.136 with an item-paired bootstrap 95% interval of
[+0.100, +0.173]. Five of six model means were positive.

Nevertheless, target-kana accuracy improved for two models, declined for three,
and changed little for one. Kana conversion redirected some errors away from
`wrong1` toward `wrong2` or `wrong3`. The continuous correct-versus-`wrong1`
margin and final four-way accuracy answer different questions, so these results
are not contradictory.

## 4. How the hypothesis changed

The original hypothesis treated orthographic overlap mainly as a harmful
shortcut. The combined evidence requires a different account:

- error concentration suggests a misleading form pathway;
- kana intervention supports a causal contribution of visible target
  orthography under this material;
- inconsistent accuracy effects show that removing form also removes useful
  information or changes competition among other wrong answers;
- item-level model differences reject a simple ability-containment story;
- manual review shows that not every benchmark disagreement is the same kind of
  semantic failure.

The revised hypothesis is that orthographic and phonological similarity act as
fast proposal-generating cues. Their expected utility varies. A system should
retain them when reliable, verify them when false-friend risk is high, and
measure the cost of verification rather than treating retrieval as free. The
problem is selective trust under uncertainty, not normalization versus no
normalization.

## 5. Revised research theme and system concept

### Working title

**Reliability-Aware Cross-Lingual Lexical Transfer: Selectively Trusting Form
and Sound in Multilingual Translation and Phrase Retrieval**

For a source phrase in context, the proposed system would produce two partially
independent hypotheses:

- a form/phonology proposal derived from cross-lingual character and sound
  similarity;
- a semantic proposal derived from contextual modeling or retrieval.

A reliability estimator would then choose whether to accept the fast proposal,
compare it with the semantic proposal, trigger dictionary/corpus/phrase
retrieval, or reject it when evidence conflicts. This preserves the original
human-inspired idea—make a provisional guess from form—but separates proposal
generation from final acceptance. The goal is not to claim an unobserved human
cognitive mechanism; it is to test an explicit decision policy.

Reliability can be operationalized as

```text
r(s) = P(form-derived proposal is semantically acceptable | evidence s)
```

Possible evidence includes orthographic and phonological similarity,
contextual compatibility, agreement with retrieval, NLL margin or entropy,
lexical frequency, domain, tokenizer fragmentation, candidate length, model
identity, and retrieval-source quality. Reliability is not synonymous with raw
model confidence: it must be calibrated against whether shortcut use is
actually acceptable.

A static threshold is a necessary baseline but is unlikely to be the final
method. A cost-sensitive policy should select the action minimizing

```text
expected translation risk(action | s) + lambda * verification_cost(action)
```

The threshold may therefore change with application risk, domain, lookup cost,
and available evidence. “Below threshold, flip the answer” is too crude. A low
score should trigger a specified verification action, after which competing
hypotheses are compared.

Human annotation can supervise reliability, but the label should not simply be
“benchmark candidate 0.” A stronger scheme records set-valued acceptability,
whether the form proposal preserves contextual meaning, whether lookup is
needed, annotator confidence, and disagreement. At least two bilingual
annotators and predefined adjudication are needed for a formal evaluation.

## 6. Research questions and evaluation

The revised agenda yields five falsifiable questions:

1. Do form and sound reduce retrieval cost or improve low-resource lexical
   transfer on true cognates?
2. Can false-friend risk be predicted better than with raw NLL or a single
   similarity threshold?
3. At matched accuracy, can selective verification use fewer lookups than
   always-retrieve; at matched cost, can it outperform always-trust-form?
4. Does the policy generalize from multiple-choice translation to contextualized
   phrase retrieval and open generation?
5. Does phonology add information beyond orthography, and what distinct failure
   modes does it introduce?

Evaluation should include strict and set-valued bilingual accuracy, Brier score
or log loss, calibration error, reliability diagrams, risk–coverage curves,
false-accept and false-reject rates, retrieval-call rate, latency, token cost,
and utility at fixed budgets. Results should be stratified by true cognate versus
false friend, surface form, frequency, direction, and domain. An oracle router
is needed to measure available headroom.

A logistic or mixed-effects model is a valuable first analysis for estimating
associations among orthographic overlap, length, frequency, naturalness labels,
and error type. It can audit confounds and establish an interpretable routing
baseline. It does not replace controlled intervention when making a causal
claim.

## 7. Proposed experimental sequence

### Phase A: reproduce a minimal CCPR baseline

Reproduce the smallest official Cross-lingual Contextualized Phrase Retrieval
baseline before adaptation. This supplies a natural verification mechanism and
reduces the risk of overfitting the idea to one multiple-choice benchmark.

### Phase B: build a small reliability dataset

Freeze a stratified sample of true cognates, false friends, surface variants,
and low-frequency items. Obtain bilingual set-valued judgments and lookup-need
labels, with adjudication defined before model comparison.

### Phase C: establish transparent routing baselines

Compare always trust form, never use form, always retrieve, a static similarity
threshold, a raw-confidence threshold, logistic regression or gradient boosting,
and an oracle router. A lightweight model should precede language-model
fine-tuning because it tests whether the signal is learnable and whether enough
oracle headroom exists.

### Phase D: strengthen causal evidence

Replicate the kana intervention on an independent benchmark or language pair,
validate interventions bilingually, and compare effect sizes for orthography,
phonology, context, tokenization, length, and naturalness under one preregistered
analysis.

### Phase E: learn and freeze a routing policy

Calibrate the estimator on development data, freeze the action rule, and
evaluate accuracy–cost trade-offs on held-out domains and models. Fine-tuning
should be tested only after labels, baselines, and measurement are stable.

## 8. Evidence boundary

Current evidence supports close reproduction of the six accessible bidirectional
Translation Type-1 results, strong homograph-error concentration, scoring-span
and length sensitivity, and a causal effect of visible target orthography on the
correct-versus-`wrong1` preference margin under the controlled kana design. It
also shows that kana normalization is not a universal accuracy-improving fix.

It does not yet establish that orthography is the strongest factor after
controlling for frequency, naturalness, length, and ambiguity; that the effect
generalizes to CCPR or open translation; that heuristic controls are bilingual
gold annotations; that a reliability router improves accuracy and efficiency;
that the proposed mechanism matches human cognition; or that phonology adds an
independent benefit.

## 9. Development as a researcher

The most important progress was not the number of GPU runs, but the change in
how evidence was handled. Code-level questions were pursued until the scoring
pipeline was explicit. A surprising result was allowed to revise the hypothesis
rather than being forced into the original narrative. Dataset flaws, failed
access, model differences, and ambiguous judgments were recorded. Control
design was reconsidered when a related control was recognized as a treatment.
Human review challenged benchmark labels while retaining its own limitations.
The repository was converted from a narrative snapshot into an executable,
validated pipeline with a conservative public-data boundary.

Remaining growth areas include independent bilingual annotation, deeper direct
ownership of commands and data transformations, statistical modeling beyond
summary comparisons, and shorter cycles between reading, preregistration,
execution, and personally written synthesis. Automation can continue to handle
environment setup, repetitive execution, hashing, and validation. The
researcher must own hypotheses, inclusion rules, annotation decisions,
interpretation, uncertainty, and final prose.

The Doppelganger-JC Translation Type-1 stage is now suitable to freeze with
explicit limits. The highest-value next move is a minimal CCPR reproduction,
followed by a small annotated reliability-routing pilot—not another undirected
model run.
