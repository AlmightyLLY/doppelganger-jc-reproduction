# B53–B57: Chinese role answers under irrelevant-record interference

**Status: B53 offline reanalysis and B54–B57 bounded experiments completed; Main numerical review and B57 delivery review passed.** Materials are authored development probes. Independent human gold: **0**; personal review: **PENDING**. This package is an additive public evidence subset, not the complete private research archive.

The question has narrowed from output-order sensitivity to a more specific problem: **when an instruction explicitly requests the roles in R1, how do the construction and lexical content of an irrelevant R2 change the correctness of the R1 answer?** The current evidence describes conditional behavioral interference. It does not establish an internal mechanism, actual training-frequency causation, or a reliable repair method.

Read [protocols and decision rules](PROTOCOLS.md), [the B57 Main analysis in Chinese](B57-main-analysis.zh-CN.md), and the complete input/output and paired-evidence files below. Previous context: [B48–B52 review](https://github.com/AlmightyLLY/doppelganger-jc-reproduction/tree/5d9a8efbbcfde3777d8c695b1976d9f8ae26d850/papers/doppelganger-jc/experiments/EXP-20260911-B48-B52-REVIEW).

## What changed across the batches

|Batch|Purpose and evidence|Finding and limit|
|---|---|---|
|B53|Reanalyse 3,600 saved B32/B36/B49–B52 records; no new model calls.|Apertus's active/passive output-schema directions motivated a new-material test. Qwen gains remained group-dependent; generic definitions and prompt repairs were not a reliable method. This was retrospective elimination work, not new confirmation.|
|B54|384 new inputs over 12 predicates × 2 contexts, plus 16 old bridges; 400 outputs.|Apertus's schema-direction pattern survived new authored materials and disjoint background names. This did not remove the background or isolate sentence order, lexical priors or internal roles. Some errors selected background people rather than simply reversing R1 roles.|
|B55|768 controlled inputs plus 16 bridges; 784 outputs. SVO/BA/BEI, R1 name order, output schema, disjoint background/NONE.|The simple universal first-mentioned-person copying account failed: BA and BEI behaved differently even in matched conflict conditions. Background removal changed the picture. Construction-dependent behavior was the warranted label.|
|B56|768 inputs: fixed R1 materials with NONE, SVO, BA/BEI backgrounds, CD/DC names and AU/UA schemas; 256 exact B55 baselines.|On the primary Apertus/AU/target-BEI comparison, background BA→BEI improved 14/32 to 27/32 (13 rescues, no harms). Target BA stayed perfect. The primary result was selective, not the predicted full bidirectional transfer. Apertus/UA still had two new target-BA harms.|
|B57|576 new inputs using 8 predicates absent from B54–B56 plus 32 old B56 bridges; 608 outputs.|The background BA→BEI correctness difference transferred to new materials both with and without exact target/background verb repetition. Absolute background damage remained large. Lexical modulation of the difference was uncertain.|

Do not compare overall accuracies across these different matrices as a learning curve. Repeated bridges and baselines are not new independent materials. All four GPU batches used the same pinned Qwen and Apertus model snapshots; B57 does not validate an unrestricted family of models.

## B57 primary result and its crucial negative control

AU means the requested JSON key order is actor then undergoer. The target is a BEI-marked passive. The two background name orders are pooled with equal weights, then contexts are averaged within the eight target-predicate clusters. All counts below refer to the 576 new inputs, excluding the 32 bridges.

|Model|Target/background verb relation|Background BA correct|Background BEI correct|Paired rescue / harm|Delta, percentage points|
|---|---|---:|---:|---:|---:|
|Apertus, primary|SAME|14/32|20/32|6 / 0|+18.75|
|Apertus, primary|DIFFERENT|5/32|13/32|8 / 0|+25.00|
|Qwen, scope control|SAME|23/32|27/32|4 / 0|+12.50|
|Qwen, scope control|DIFFERENT|24/32|28/32|4 / 0|+12.50|

For Apertus, both deltas remain positive under every leave-one-target-predicate analysis. The eight-cluster bootstrap intervals are +6.25 to +34.375 pp (SAME) and +6.25 to +50 pp (DIFFERENT). The prespecified development label is `TRANSFER_WITHOUT_EXACT_VERB_IDENTITY`.

**This label is not a repair claim.** Without any R2, target-BEI accuracy is 15/16 for Apertus and 16/16 for Qwen. Every pooled background condition performs worse. The NONE output is one reference per context, reused in comparisons; it is not an additional independent draw each time. Within-context averaging is required when comparing its denominator of 16 with a background denominator of 32.

For Apertus, changing SAME to DIFFERENT decreases absolute performance: background BA 14→5/32 (0 rescues, 9 harms); background BEI 20→13/32 (1 rescue, 8 harms). A larger difference between two damaged conditions does not mean a better method. The lexical-modulation contrast Gamma = Delta(SAME) − Delta(DIFFERENT) is −6.25 pp; its bootstrap interval spans −28.125 to +12.5 pp and leave-one signs differ. Neither a stable positive repetition boost nor lexical equivalence is established.

Other boundaries are retained. Both models' target-BA conditions are perfect, with zero background-marker delta. Apertus SAME/CD has only one rescue and loses a strictly positive effect when its contributing predicate is omitted; SAME/DC is stronger. Qwen's bootstrap intervals touch zero and each pooled gain comes from two predicate clusters. B57 fixes AU and does not erase the B56 UA harms.

## One actual B57 example

Prompt instructions explicitly say to answer R1 only and to return `{"actor":"person","undergoer":"person"}`. The full exact Chinese prompt is in the evidence file. The target R1 is fixed:

> R1：休息室里的恶作剧已经结束。姚承霁确实被叶知岳吓哭了。

The author reference is actor = 叶知岳, undergoer = 姚承霁. The target verb is 吓哭; the background verb is 劝退.

|Background R2|Actual Apertus output|Classification|
|---|---|---|
|R2：昨天另一处场地发生了一件事。石远澈把蒋沐衡劝退了。|`{"actor":"姚承霁","undergoer":"叶知岳"}`|R1 roles reversed|
|R2：昨天另一处场地发生了一件事。石远澈被蒋沐衡劝退了。|`{"actor":"叶知岳","undergoer":"姚承霁"}`|Correct|

IDs: `B57-apertus-N04-C01-BEI-AB-DIFFERENT_BA_CD-AU` and `B57-apertus-N04-C01-BEI-AB-DIFFERENT_BEI_CD-AU`. The fixed-name BA→BEI switch also changes the background role facts; the package therefore retains crossed CD/DC same-background-fact comparisons. This single example alone is not pure syntactic causal identification.

## Evidence files

- [B53 offline statistics](B53-offline-analysis.json): no new generation; complete private source records remain local.
- B54: [400 exact synthetic input/output extracts](B54-evidence.json), [statistics](B54-statistics.json), [all planned paired results](B54-paired-results.json).
- B55: [784 extracts](B55-evidence.json), [statistics](B55-statistics.json), [all pairs and four-answer groups](B55-paired-results.json).
- B56: [768 extracts](B56-evidence.json), [statistics](B56-statistics.json), [all pairs and four-answer groups](B56-paired-results.json).
- B57: [608 extracts](B57-evidence.json), [statistics](B57-statistics.json), [1,824 pairs and 128 target × background groups](B57-paired-results.json).
- [Local archive commitments](LOCAL-ARCHIVE-COMMITMENTS.json): pre/post Office, frozen inputs and full raw/ZIP hashes. These do not imply that private originals or personal reviews were published.

For B57, Main independently checked all raw responses, starts, exact native inputs, 32 bridges, 46 frozen files, 1,824 paired transitions, 128 groups, cluster estimates, leave-one results and the shared-draw bootstrap. The final Excel's 608 source/prompt/output/score rows were compared with the raw evidence, personal fields were preserved blank, both Word pages were inspected, and all 102 archive-member hashes were checked. Resource cleanup was verified; provider final billing remained unavailable. B53's Main review scope was narrower: independent B52 integer/schema/leave-one recomputation and source-hash checks, with other strata reviewed from the full reports. It was not an independent reimplementation of all 3,600-row parsing.

## Scientific boundary and next decision

Structural priming and lexical modulation in language models already have close predecessors: [Sinclair et al., 2022](https://aclanthology.org/2022.tacl-1.60/) and [Jumelet et al., 2024](https://aclanthology.org/2024.findings-acl.877/). The candidate contribution must concern predictive conditions for correct and incorrect role answers under explicitly irrelevant records, beyond rediscovering priming or role reversal.

These experiments balance observed test conditions, not actual conditional training-corpus frequencies. Replacing a background verb also changes event meaning and sometimes token length. The samples are small, author-generated and adaptively developed across batches. Independent material validation, discriminating predictions and a task-relevant comparison to adjacent work are still needed. B57 is the stopping point for this authorized sequence; no B58 has been launched.
