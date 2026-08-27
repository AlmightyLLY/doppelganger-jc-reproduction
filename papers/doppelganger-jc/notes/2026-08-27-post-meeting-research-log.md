# Research Log — 2026-08-27

## 1. The problem I chose to pursue

After discussing my progress with Professor Chu, I changed the immediate priority of the project. I had planned to move directly to the Cross-lingual Contextualized Phrase Retrieval paper. Instead, I decided to stay with Doppelganger-JC and investigate the unresolved phenomenon more deeply.

The immediate question became:

> Does context-inappropriate homograph attraction remain a meaningful problem in more recent open-weight language models, and can layer-wise vocabulary readouts help characterize the effect observed in the kana intervention?

This reformulation matters because rapid improvements in multilingual models could have made the original behavior substantially less relevant. My initial informal forecast was that recent models might reach approximately 85%–90% accuracy and show a much smaller concentration of `wrong1` errors. If that had happened, a mechanism study centered on the old failure pattern would have had a weaker motivation.

This experiment did **not** test explicit chain-of-thought reasoning. It used the same teacher-forced likelihood scoring framework as the reproduction, rather than a reasoning prompt or free generation. My broader interest in reasoning-capable models therefore remains a separate future question.

My personal research objective is also methodological. I want to become able to inspect raw outputs, formulate a small falsifiable experiment, predict its result in advance, and update my view when the result disagrees with my expectation. AI assistance can accelerate execution and documentation, but I want the problem definition, linguistic judgments, evidence boundaries, and final interpretation to remain decisions that I can explain independently.

## 2. Forecast, experiment, and correction

I made two main predictions before examining the results:

1. recent models would obtain roughly 85%–90% accuracy and show a much smaller `wrong1` concentration;
2. because the controlled orthography contrast appeared strong near the upper layers, a fixed layer near 90% depth might score the full candidates more accurately than the final layer.

The first prediction was not supported. The full behavior audit evaluated four pinned checkpoints—Qwen3-8B, Qwen3-14B, llm-jp-4-8B-Instruct, and Apertus-8B-Instruct-2509—on all 462 Japanese-to-Chinese and 455 Chinese-to-Japanese Translation Type-1 items. Japanese-to-Chinese official accuracy ranged from 69.5% to 79.0%, and Chinese-to-Japanese accuracy ranged from 65.3% to 73.0%. Among the remaining official errors, `wrong1` accounted for 73.6%–85.2% in Japanese-to-Chinese and 78.0%–88.7% in Chinese-to-Japanese.

Qwen3-14B was more accurate than Qwen3-8B in both directions, but its remaining errors were more concentrated on `wrong1`. The two checkpoints also corrected and regressed on different individual items. The appropriate conclusion is not that the larger model lacks the smaller model's overall ability. Rather, aggregate improvement does not produce a nested set of item-level correct answers under this evaluation, and scaling changed the error distribution without eliminating the homograph-related pattern.

The second prediction was also not supported consistently. The previous 88%–90% observation concerned a peak in the **controlled orthography contrast**, not a peak in candidate accuracy. A separate diagnostic used each real hidden state under the original condition, selected the lowest teacher-forced candidate-only NLL, and compared a preregistered relative depth of 87.5% with the final layer. Some model–metric combinations improved, others were unchanged or declined, and all four models remained at 0% strict accuracy on the four strict-unsafe items at both the fixed upper layer and the final layer. There is therefore no stable evidence that approximately 90% depth is a better early-exit point.

## 3. What I learned by inspecting the outputs

I manually reviewed 50 selected failure or uncertainty cases instead of relying only on aggregate accuracy. The structured review retained 19 cases as `KEEP`, marked 10 as `CAUTION`, and excluded 21 from the clean mechanism-analysis pool. This was important because a fluent candidate can be semantically defensible even when the benchmark marks only option 0 as correct.

Three examples helped refine my interpretation:

- **教学** showed that the source expression, its field-specific or shortened Japanese meaning, and the Chinese lexicalization could not be assumed from surface form alone. I left the source semantics and acceptable set pending rather than forcing the item into the confirmatory set.
- **国体** illustrated that the same visible characters can activate a conventional target-language word even when the source lexicalization differs. It was retained as a safe/control-type case with more than one acceptable Chinese rendering.
- **脈々** illustrated why the distractors may form a semantic family rather than three unrelated errors: alternatives can be connected through target-language senses or associations evoked by the visible form.

My current working taxonomy is:

- `wrong1` is usually the most direct form copy or the direct adoption of the target-language homograph's conventional meaning;
- `wrong2` can be a paraphrase or semantic elaboration derived from that target-language interpretation;
- `wrong3` can be a more distant association continuing from the same form-triggered semantic path.

This led to the concept of a **form-derived semantic family**. On some items, comparing `correct` only with `wrong1` is too narrow because `wrong2` or `wrong3` inherits the same form-induced interpretation. The category is still a human-defined analytical hypothesis, not a proven internal model operation. Difficult and nonconforming cases must remain visible rather than being forced into the family.

## 4. Data and evaluation decisions

The audited 12-item Logit Lens material is divided into:

- strict unsafe primary: items 39, 354, 416, and 451;
- safe controls: items 35 and 291;
- boundary cases: items 175 and 300;
- pending or sensitivity cases: items 76, 259, 322, and 404.

The strict set is deliberately small. It cannot estimate the prevalence of the phenomenon or support formal significance claims. `裏面` still requires native-speaker or reliable lexical evidence about whether kana-only `りめん` activates the same sense. `明後日` requires a common-reading `あさって` sensitivity condition. `教学` still lacks a frozen source-sense analysis and acceptable set. These uncertainties are part of the result rather than inconveniences to hide.

My own judgments may also be affected by my Japanese proficiency, contemporary Chinese usage, register, and regional variation. Without this audit, I could easily misclassify preference shifts as error corrections, interpret an ambiguous benchmark label as a model failure, or select mechanism cases that merely reflect unnatural material.

## 5. What the evidence currently supports

The recent-model audit supports a descriptive claim: the benchmark's homograph-based distractor remains prominent among errors in all four evaluated checkpoints. It does not by itself prove an internal orthographic shortcut because `wrong1` was deliberately designed to be competitive, and candidate naturalness and label quality remain confounds.

The controlled kana intervention provides stronger behavioral evidence that visible target-word orthography changes candidate preference. In the audited Logit Lens subset, Qwen3-8B and Qwen3-14B showed consistently positive strict-primary contrasts; llm-jp was close to zero, and Apertus was mixed but positive on three of four items. This pattern is heterogeneous and exploratory.

The first-divergence contrast and full-family contrast were positively associated in the selected cases, but a local token-level comparison cannot replace complete candidate-family scoring. More importantly, standard Logit Lens measures what can be linearly decoded by the final norm and language-model head. It does not establish causal mediation, prove that the model skipped semantic processing, or identify a discrete layer at which the model “made its decision.”

The strongest defensible wording is therefore:

> Under the vocabulary projection, upper-layer residual states on selected items become more compatible with particular candidate lexicalizations, and this compatibility changes under the controlled orthographic intervention.

I cannot yet claim an English pivot, a latent translation cascade, a universal 90%-depth decision layer, or a causal internal path from visible form to the final error.

## 6. How the research question changed

I originally treated the phenomenon primarily as a shortcut that should be suppressed. The kana intervention had already shown that removing visible form can reduce `wrong1` attraction while also moving errors toward `wrong2` and `wrong3`. Today's manual review and form-family analysis made this more precise: visible form may activate a useful or misleading family of lexical proposals, and the final outcome depends on whether context and semantics support that family.

My current question is consequently:

> When is a form-derived lexical proposal reliable, and when should a model trigger semantic verification rather than accept it?

The long-term method would need to estimate the reliability of the proposal, compare form-based and context-based evidence, and route uncertain cases to verification or retrieval. Today's experiments do not yet implement such a router; they clarify the target behavior and the evidence required before training one.

## 7. Tightening the next feedback loop

The most informative work today was not another large run. It was reading the selected outputs, separating acceptable alternatives from true errors, and testing whether the upper-layer contrast peak was also an accuracy peak. The negative early-exit result prevented an attractive but unsupported mechanism claim.

Before using a GPU again, I need to freeze one multilingual lexicalization probe for item 416 (`供出`). It should distinguish the source-language correct-sense form, an English correct-sense expression, the target-language correct form, the target-language form-derived wrong form, the English expression of the wrong sense, and any shared or ambiguous form. These entries must be judged manually rather than treated as machine-generated gold labels.

Only after that freeze should I run a one-item Qwen3-8B full-top-k smoke test. The smoke test must validate every-layer token ranks, log probabilities, sequence scores, and the final projection before any four-model expansion. Activation patching should come later, after the material and readout pattern are stable.

## 8. Research practice and responsibility

I made a useful decision to stop launching experiments and reconstruct what had happened during the day. This exposed several points I had not yet understood clearly, especially the distinction between the full recent-model audit and the 12-item layer-wise pilot.

Automation supported model execution, validation, statistical aggregation, plotting, and report formatting. My responsibility was to inspect the language, decide which candidates were acceptable, define the form-derived family, preserve unresolved cases, and judge what the evidence did and did not support.

The main skill I practiced today was not simply using Logit Lens. It was research calibration: making an advance prediction, discovering that both central predictions were too strong, and replacing them with narrower claims that better match the evidence.

## 9. Points I need to revisit personally

1. I should be able to explain, without referring to a generated report, why the current-model behavior audit and the Logit Lens pilot answer different questions.
2. I need to verify the source semantics and naturalness of `教学` and the kana-only reading of `裏面` with stronger linguistic evidence.
3. I should test whether the form-derived-family taxonomy remains useful outside the cases that motivated it.
4. I need to distinguish vocabulary compatibility from semantic correctness, language identity, orthographic similarity, and causal mediation in my own words.
5. Before the next experiment, I should record a numerical forecast and the result that would make me abandon or revise the hypothesis.

## 10. One-sentence update

I began the day expecting recent models and a fixed upper-layer exit to have largely reduced the Doppelganger-JC problem; the evidence instead showed that homograph-related errors remain concentrated, while upper-layer orthographic decodability does not translate into a stable accuracy advantage, motivating a narrower study of form-derived lexical families and selective semantic verification.
