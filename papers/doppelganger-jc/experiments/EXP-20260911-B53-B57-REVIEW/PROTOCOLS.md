# Protocol excerpts and measurement boundaries

This is a post-run public summary of plans frozen locally before the respective GPU batches. It is not a third-party preregistration record. Actual pre-run Word documents, full input workbooks and immutable freeze files are local and hash-committed. Human fields were not filled by AI. The B-series exploratory policy permits execution while personal review remains pending; it does not turn author references into independent gold.

## Shared measurement

Two fixed models: `Qwen/Qwen3-8B` revision `b968826d9c46dd6066d109eabc6255188de91218` and `swiss-ai/Apertus-8B-Instruct-2509` revision `b946d40447b2b597999b9c86d44bee0b452c919f`. Native chat templates; Qwen thinking disabled. BF16 eager computation, no KV cache, TF32 off, full-vocabulary raw-logit argmax, no logits processors. Maximum 128 new tokens; no retry of any started scientific call. Detailed policy and versions appear in each statistics file. Greedy decoding is a selected observation regime, not a universal model behavior guarantee.

Inputs contain numbered fictional-person records, a definition of actor/undergoer, an instruction to answer R1 only, and a requested JSON schema. AU requests actor before undergoer; UA requests the reverse. R1 correctness uses explicit author references. C/W/U is the frozen field-aware scoring system. R is a derived diagnostic subclass: the R1 people are correct but their two roles are reversed. Other wrong people and unresolved outputs are retained separately; JSON/key-order compliance is not equated with semantic correctness. Full generated strings are preserved, including null/unresolved failures.

Inference counts refer to unique started positions, not independent semantic samples. Separate baselines and bridges replay the old exact input under the same decoding configuration; they are excluded from new-material primary estimates. Estimates and resampling operate at the specified semantic/predicate level, not the individual prompt row. No condition was selected after generation to become a replacement primary model.

## B53: offline diagnosis

Use 3,600 saved records from B32/B36/B49–B52. Reconstruct 1,800 output-schema pairs and 1,536 background-related pairs, preserve source-specific strata and leave-one semantic-group behavior. Ask whether surface/role-order congruence and shared-identity explanations warrant controlled follow-up. This is retrospective analysis, with zero new GPU or model calls. Previously unclear external claims are not treated as facts. B52-to-B54 continuation was authorized separately after review.

## B54: new-material development transfer

12 new predicates × 2 contexts × 2 target voices × 2 background identity conditions × 2 answer schemas × 2 models = 384 new calls, plus 16 old bridges = 400. Shared-person and disjoint-person backgrounds are compared. Test whether the previously observed schema-direction pattern survives these authored materials and whether shared identity is necessary. Retain one unresolved old bridge instead of relabeling it for an attractive result. Predicate-cluster and leave-one analyses accompany all paired rescues and harms. Material validity has AI author review only.

## B55: construction-dependent role/copy diagnosis

16 authored contexts over 8 predicates × 3 R1 constructions (SVO, BA, BEI) × 2 R1 name orders × 2 backgrounds (DISJOINT, NONE) × 2 output schemas × 2 models = 768 controlled calls, plus 16 B54 bridges = 784. These target predicates are not claimed to be unseen relative to earlier author development. Predefine H_ROLE and H_COPY for every input; H_COPY puts first and second R1 people into the first and second requested fields. Evaluate conflict cells with role-minus-copy theta, preserve person errors and U, examine full four-answer target/schema groups and eight-predicate leave-one behavior. The decision is whether one simple position-copy rule suffices or effects depend on construction and background.

## B56: irrelevant background construction

Reuse B55's 16 contexts and 8 predicates; fix one R1 name order per context (C01 AB, C02 BA). 16 contexts × 2 target constructions × 2 answer schemas × 6 backgrounds × 2 models = 768. Backgrounds: NONE, SVO_CD, BA_CD, BEI_CD, BA_DC, BEI_DC. R2 is first, R1 last. Include 256 exact B55 baseline inputs within the cap. Foreground and background verbs are identical in this batch.

Primary: Apertus/AU. Compute d_BEI and d_BA for background BA→BEI at fixed background mention order, average CD/DC within context and contexts within predicate; also compute I=d_BEI−d_BA. A full directional-transfer-compatible result requires positive leave-one-stable d_BEI and negative leave-one-stable d_BA, rather than a positive interaction alone. Preserve selective, common-direction, opposite and mixed outcomes. Check CD/DC, crossed same-background-fact pairs, NONE, all harms and 192 target × schema groups. B56 supported BEI-selective behavior in the primary stratum; secondary UA harm cannot be substituted as the primary result.

## B57: new predicates and exact repetition

Primary question: does B56's background construction effect transfer to new authored materials without exact R1/R2 verb identity?

Eight complete predicates absent from the B54–B56 reference verb vocabulary: 拉开、踢伤、击败、吓哭、撞倒、扶稳、劝退、抱紧. Two contexts each, totaling 16 semantic groups. This is new relative to those specified batches, not proof of absence from all prior work or pretraining. Reuse the name inventory with one fixed R1 name order per context. AU only; background and target people are disjoint.

- 16 contexts × 2 target constructions × 2 lexical-overlap conditions × 2 background constructions × 2 background name orders × 2 models = 512 new background calls.
- 16 contexts × 2 target constructions × 2 models = 64 new NONE calls.
- 32 exact B56 bridges: all eight old predicates, C01, target BEI/AB/AU, background BA_CD and BEI_CD, both models.
- Total hard cap 608 started calls, 304 per model. No extra smoke generations, third model, response retries or automatic next batch.

SAME repeats the target verb in R2. DIFFERENT uses a predetermined cyclic permutation: offset +3 for C01 and +5 for C02 over the eight-verb list. Each target verb occurs equally often as an R2 predicate in the SAME and DIFFERENT marginal distributions. This does not match conditional training frequencies or equalize the semantics of the different events. Fixed BA/BEI marker pairs have equal native token lengths; lexical replacement is not uniformly token-length matched.

For the primary Apertus/target-BEI/AU comparison, define Delta_L=C(background BEI,L)−C(background BA,L), L in SAME/DIFFERENT, and Gamma=Delta_SAME−Delta_DIFFERENT. Pool the two background name orders within context, then the two contexts within target predicate; eight target predicates receive equal weight. Each lexical layer contains 32 fixed-mention pairs. Joint 10,000-draw cluster bootstrap uses seed 570911 and identical target-cluster draws for both deltas and Gamma. Report every predicate and leave-one result. Because cyclic R2 verbs are shared across target clusters, these intervals describe development stability rather than fully independent lexical-population uncertainty.

A layer is “clear positive” under the frozen development rule only if Delta>0 and every leave-one point estimate remains >0. Both clear → `TRANSFER_WITHOUT_EXACT_VERB_IDENTITY`; only SAME → `ONLY_SAME_CLEAR`; only DIFFERENT → `DIFFERENT_ONLY_PATTERN`; neither → `NO_CLEAR_NEW_MATERIAL_TRANSFER`. If unresolved bounds change the classification, use `INDETERMINATE`. Only-SAME would not prove exact repetition is necessary. A positive Gamma is a separate lexical-modulation claim; failure to establish Gamma is not evidence of equivalence.

Qwen, target BA, separate CD/DC, same-background-fact crossing, SAME→DIFFERENT changes, and NONE are compulsory scope controls. The 128 four-answer groups cross **target BA/BEI × background BA/BEI with AU fixed**, unlike B56's target × schema groups. All 1,824 pairs, including reused NONE references, remain visible. No global reliability or causal-frequency conclusion follows from a successful primary label.

## Resource and stop rules

Each GPU batch used a bounded authorization with a USD 10 total ceiling across attempts and storage, at most two models, and no scientific retry of started calls. B57's own instance was removed and verified absent after retrieval; no new persistent volume was created. Cost estimates are not final provider invoices. Technical metadata corrections are recorded separately from scientific input/output changes. Material/scoring ambiguity, native bridge mismatch, input drift, resource safety limits or scope violations require a stop or explicit diagnostic treatment, not silent model substitution or discarded failures.
