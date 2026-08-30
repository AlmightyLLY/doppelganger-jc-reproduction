# Data Audit and Relation-Layer Construction — Windows A–Q

Date: 2026-08-30
Status: completed automated audit chain; AI-audited clean-pilot candidate pool ready; final human freeze pending

## 1. Purpose and stopping rule

The day's work moved the project from an encouraging but annotation-sensitive
factorial result toward a minimum credible feasibility set for
reliability-aware Japanese–Chinese lexical transfer.

The research question is now separated into two layers:

- **Layer A — contextual relation:** whether marked Japanese and Chinese
  expressions convey the same lexical sense in their respective contexts.
- **Layer B — downstream translation:** whether a Layer-A-approved relation can
  support a unique Chinese reference, a natural form-derived alternative, a
  matched carrier, and a leakage-resistant translation evaluation item.

This separation was necessary because a valid bilingual semantic relation does
not automatically supply a unique multiple-choice translation item.

The report adopts the following operational stopping rule:

1. M2 is the final full data-structure redesign.
2. After M2, only independent audit, one human freeze, and necessary local
   adjudication are allowed.
3. No M3/M4-style broad remine is allowed before the feasibility decision.
4. A pilot with roughly 8–12 strict different/unsafe relations and 8–12
   form-reliable relations is sufficient to return to experiments.
5. If only 5–7 strict different relations survive, run a smoke/pilot Oracle
   without population-level claims.
6. If fewer than five survive, stop cleaning and reconsider the task definition.
7. A final 80–120-item confirmatory set is authorized only if the clean pilot
   shows a surviving phenomenon and useful Oracle headroom.

## 2. Experimental context that triggered the audit

A result-blind 50-item Qwen3-8B factorial external validation had produced an
encouraging but explicitly non-gold result:

- original branch: 46/50;
- target-kana plus semantic gloss: 49/50;
- three rescues and no discrete harms;
- positive target-form-removal-with-gloss effect on 22/30 unsafe items;
- mean continuous effect +0.240, bootstrap 95% interval [+0.021, +0.460];
- form-reliable controls remained 20/20 correct, but their preference margins
  declined on 18/20 after form removal;
- the item-level Oracle was also 49/50, leaving no observed headroom over the
  stronger fixed branch.

A separate contextual-relation verifier feasibility result reached 92.5%
balanced accuracy, with 95% unsafe recall and 90% form-reliable recall under an
externally transferred threshold. It exceeded a calibrated word-only baseline
by ten percentage points. However, simple downstream Option-A/Option-B routing
and factorial routing experiments did not yield stable translation gains.

These results support the existence of readable contextual reliability signal,
but not a working downstream router. They also exposed a more basic problem:
the available constructed and legacy items were too easy, semantically noisy,
or insufficiently controlled to carry a confirmatory claim.

## 3. Windows A–F — audit of the legacy 34-item bank

### Windows A–E: five isolated audit streams

Five complementary local audit streams independently examined the same legacy
34-item development bank. The material-bearing files remain local under the
repository's public-data policy. Collectively, the audits covered:

- Chinese target-side naturalness and target-only leakage;
- bilingual contextual semantics and acceptable-set overlap;
- uniqueness of the intended answer and form-derived semantic-family overlap;
- matched-carrier and construction quality;
- tokenizer-boundary, provenance, license, exposure, and group-integrity risks.

The exact per-item mappings and blind decisions are not public artifacts.

### Window F: cross-audit synthesis

Window F combined the five audit streams. The synthesis found that only a small
fraction of the 34 items were strong without qualification. Common failure
modes included target-only leakage, semantic overlap or multiple acceptable
answers, non-independent wrong-option families, source-sense ambiguity,
provenance or license limitations, and carrier mismatch.

The old 34-item bank therefore could not serve as a clean confirmatory set.

## 4. Windows G–J — external mining, failure diagnosis, repair, and infrastructure

### Window G: Wave-2 external-corpus mining

Window G scanned 4,893,734 corpus lines and produced:

- 23,609 raw proposals;
- 160 deeply audited proposals;
- 4 strict candidates;
- 8 repairable candidates;
- 5 exploratory candidates;
- a sealed 13-item human-review package.

Terminal status: `BLOCKED_INSUFFICIENT_STRICT_UNSAFE_YIELD`.

### Window H: Wave-3 preparation and failure analysis

Window H analyzed 147 non-sealed failures. Non-exclusive failure-mode counts
were semantic overlap 61, grammatical leakage 53, non-unique correct answer 19,
construction-repairable 55, and inherently unsuitable 91.

A new construction attempt produced 26 WikiMatrix-derived proposals and zero
strict unsafe or reliable items. The bottleneck was source coverage and the
one-step construction strategy, not proof that the phenomenon had disappeared.

### Window I: repair of 55 legacy failures

- eligible: 55;
- successfully reconstructed: 11;
- rejected: 44;
- ready for audit: 5;
- native/domain review: 4;
- exploratory: 2;
- provenance complete for 11/11;
- sealed overlap: zero.

Only nine items proceeded to K/L. The I repair route is now closed.

### Window J: source and lexicon infrastructure

Window J established deterministic, exposure-aware infrastructure:

- 7 active resource families;
- 93,081 lexical links;
- 29,310 components;
- 59,473 Japanese and 43,810 Chinese entries;
- 69,332 Japanese and 113,367 Chinese attestations;
- 14,020 parallel attestations;
- 1,606 non-exposed components with bilateral monolingual evidence;
- 18,265 eligible components before semantic review;
- 13 sealed and 11,032 exposed components excluded;
- 19/19 validation checks and deterministic rebuild passed.

Terminal status: `SOURCE_INFRASTRUCTURE_PASS_READY_FOR_PROSPECTIVE_MINING`.

## 5. Windows K–N and M-v1

### Window K: Chinese target-only blind audit

Nine repaired items yielded PASS 5, REVISE 2, REJECT 1, and second judgment 1.
Leakage labels were NONE 3, LOW 2, MODERATE 1, and HIGH 3.

### Window L: bilingual semantic audit

The same nine stable IDs yielded PASS 1, REVISE 4, REJECT 1, and native/domain
review 3. One multiple-answer item and one semantic-overlap item were confirmed.

### Window M-v1: one-step translation-item construction

Starting from 1,606 eligible components, M-v1 reserved 330 unread components,
used 1,276 for discovery, identified 103 potential unsafe-divergence and 22
potential reliable components, but produced zero final unsafe and zero final
reliable translation items.

Terminal status: `BLOCKED_INSUFFICIENT_UNSAFE_YIELD`.

Relation discovery had been incorrectly coupled to reference, distractor,
matched-carrier, and final balance construction. The 103/22 cohorts remained
useful Layer-A entry points.

### Window N: K/L cross-audit synthesis

The nine repaired items yielded one joint pass pending human review, two
bilingual semantic repairs, three native/domain cases, two rejects, and one
unresolved conflict. Legacy repair could not carry the scaling plan.

## 6. M2 — relation-layer reconstruction

M2 was the final authorized full data-structure adjustment. It reconstructed
the 103 potential-unsafe and 22 potential-reliable cohorts as Layer-A relation
materials without requiring a complete translation reference.

Terminal status: `RELATION_LAYER_PACKETS_READY_FOR_INDEPENDENT_AUDIT`.

Key results:

- unsafe cohort 103; reliable cohort 22; overlap 7;
- 118 unique primary components;
- 330 reserved components untouched; protected/reserved overlap zero;
- proposed DIFFERENT 21; SAME 68; uncertain/overlapping 16; rejected 13;
- Layer-B potential 18; reference missing 21; not appropriate 79;
- two blind packets of 105 rows each;
- 27/27 validations passed;
- 18 canonical outputs rebuilt byte-identically.

The source mix—FLORES 31, MASSIVE 5, Universal Dependencies 82—is adequate for
a feasibility pilot but not a broad cross-domain claim. M2 generated no final
translation-choice items and ran no model inference.

## 7. Windows O–Q — independent audit and synthesis

### Window O: Chinese context-sense blind audit

- rows 105;
- PASS 78; REVISE 21; REJECT 3; native/domain review 3;
- expert queue 3;
- additional model and network calls zero;
- source hashes and Git state unchanged.

All results are `AI-SUGGESTION-NOT-GOLD`.

### Window P: bilingual relation blind audit

- rows 105;
- SAME 69; DIFFERENT 24; UNCERTAIN 12;
- PASS 91; REVISE 4; REJECT 5; native/domain review 5;
- expert queue 5;
- 44/44 mechanical validations passed;
- no M2 proposed labels were read or compared;
- additional model and network calls zero;
- source hashes and Git state unchanged.

All results are `AI-SUGGESTION-NOT-GOLD`.

### Window Q: O/P cross-audit synthesis

Window Q established an exact one-to-one crosswalk between the 105 O rows and
the 105 P rows using a seven-field Chinese-side signature: marked expression,
context, marked context, start span, end span, source identifier, and evidence
URL. O and P use distinct audit IDs, so the join did not rely on ID equality,
row order, or fuzzy matching.

| Category | Count |
|---|---:|
| CLEAR_SAME | 43 |
| CLEAR_DIFFERENT | 14 |
| TARGET_SIDE_REPAIR | 21 |
| BILINGUAL_RELATION_REPAIR | 10 |
| UNCERTAIN_HOLD | 4 |
| NATIVE_OR_DOMAIN_REVIEW | 7 |
| CROSS_AUDIT_CONFLICT | 0 |
| REJECT | 6 |
| **Total** | **105** |

The human queue contains 64 rows and the learning/exclusion queue 41. All 74
validation checks passed; inputs and Git state remained unchanged; no model,
network, constructor-label, gold-label, or Layer-B operation occurred.

Terminal status:
`WINDOW_Q_CROSS_AUDIT_SYNTHESIS_COMPLETE_AI_SUGGESTIONS_NOT_GOLD`.

At the suggestion level, 14 clear DIFFERENT and 43 clear SAME candidates pass
the yield requirement for an 8+8 clean feasibility pilot, subject to human
freeze.

## 8. Human-confirmed local audit artifacts

Lingyun completed item-wise review of:

- `G-11-HUMAN-REVIEW-PACKET-HUMAN-CONFIRMED.xlsx`;
- `N-09-TARGET-ONLY-BLIND-AUDIT-PACKET-HUMAN-CONFIRMED.xlsx`;
- `N-10-BILINGUAL-BLIND-AUDIT-PACKET-HUMAN-CONFIRMED.xlsx`.

The records preserve `HUMAN_CONFIRMED_BY_LINGYUN`, 253 frozen judgment cells,
no blanks or formula errors, original blank packets, provisional AI-prefilled
versions, and final human decision authority.

These are AI-assisted, human-confirmed researcher annotations—not independent
double-human annotation, independent blind human gold, or Japanese-native
adjudication. The two N workbooks are different audit views of the same stable
items and must not be double-counted. Material-bearing workbooks remain local.

## 9. What the day establishes—and does not establish

The work establishes that legacy and early constructed sets contain substantial
semantic/evaluation noise; Layer A and Layer B must remain separate; source
infrastructure can yield sufficient relation candidates; and O/P/Q produced 14
clear DIFFERENT and 43 clear SAME candidates with zero cross-audit conflicts.

It does not yet establish a final human-gold dataset, clean-data downstream
Oracle, working router, broad source/domain or multilingual generalization,
causal internal mechanism, or ACL Main-level final contribution.

## 10. Frozen next action

Do not review all 64 Q rows. Conduct one capped human freeze:

1. review all or nearly all 14 `CLEAR_DIFFERENT` candidates;
2. select 10–12 group-disjoint, source/domain-diverse `CLEAR_SAME` candidates;
3. keep seven native/domain cases outside the strict pilot unless needed;
4. merge retained Q candidates with non-overlapping human-confirmed G/N items;
5. exclude repair, uncertain, reject, high-leakage, unresolved expert, and
   group-overlapping rows;
6. freeze approximately 8–12 strict different/unsafe and 8–12 form-reliable
   relations.

After the freeze, return immediately to:

1. clean-set behavior audit;
2. Layer-A verifier replication;
3. Layer-B downstream Oracle on the smaller eligible subset.

Only clear Oracle headroom authorizes router development or expansion toward a
larger confirmatory set.

## One-sentence update

A full A–Q audit and reconstruction chain converted a noisy legacy and
translation-coupled pipeline into 14 clear DIFFERENT and 43 clear SAME
contextual-relation candidates, with human-confirmed G/N evidence preserved
separately; one capped human freeze now stands between the project and a clean
8+8 feasibility pilot.
