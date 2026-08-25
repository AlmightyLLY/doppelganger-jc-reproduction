#!/usr/bin/env python3
"""Score the frozen full-set orthography control-relevance material."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import random
import statistics
import sys
from collections import Counter
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("HF_HOME", str(PROJECT_ROOT / ".cache" / "huggingface"))
sys.path.insert(0, str(PROJECT_ROOT))

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from questions.jp_zh.homographs import dataset
from scripts.compare_scoring_one_example import score_candidate, select_device, select_dtype
from scripts.run_orthography_causal_smoke import pack_scores


DEFAULT_MODEL = "Qwen/Qwen2.5-7B-Instruct-1M"
DEFAULT_REVISION = "e28526f7bb80e2a9c8af03b831a9af3812f18fba"
DEFAULT_MATERIAL = (
    PROJECT_ROOT
    / "results"
    / "local"
    / "materials"
    / "orthography-control-relevance-full-v1.jsonl"
)
FIELDS = ("correct", "wrong1", "wrong2", "wrong3")
BASE_CONDITIONS = ("original", "target_kana", "unrelated_control_kana")
RELATED_CONDITION = "related_semantic_cue_kana"
BOOTSTRAP_SEED = 20260825
BOOTSTRAP_SAMPLES = 10000
PURPOSE = "pre_outcome_control_relevance_full_v1"
EXPERIMENT = "orthography_control_relevance_full_v1"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as error:
                raise ValueError(f"{path}:{line_number}: invalid JSON: {error}") from error
    if not rows:
        raise ValueError(f"No rows found in {path}")
    return rows


def validate_material(rows: list[dict[str, Any]]) -> None:
    indexed_dataset = list(dataset.items())
    required = {
        "item_index",
        "word",
        "japanese_word",
        "surface_exact",
        "previously_exposed_causal_item",
        "original",
        "target_intervention_span",
        "target_span_rule",
        "target_reading",
        "target_kana_sentence",
        "unrelated_control_word",
        "unrelated_control_reading",
        "unrelated_control_kana_sentence",
        "related_semantic_cue_word",
        "related_semantic_cue_reading",
        "related_semantic_cue_kana_sentence",
        "candidate_control_count",
        "unrelated_control_quality_proxy",
        "selection_rule",
        "purpose",
        "review_status",
    }
    seen: set[int] = set()
    for row in rows:
        missing = required.difference(row)
        if missing:
            raise ValueError(f"Material row missing fields: {sorted(missing)}")
        index = row["item_index"]
        if not isinstance(index, int) or not 0 <= index < len(indexed_dataset):
            raise ValueError(f"Invalid item_index: {index!r}")
        if index in seen:
            raise ValueError(f"Duplicate item_index: {index}")
        seen.add(index)
        word, item = indexed_dataset[index]
        if row["word"] != word or row["original"] != item["target-sentence"]:
            raise ValueError(f"item {index}: dataset identity mismatch")
        if row["purpose"] != PURPOSE:
            raise ValueError(f"item {index}: unexpected purpose")
        if row["unrelated_control_quality_proxy"] not in {"high", "medium", "weak"}:
            raise ValueError(f"item {index}: invalid quality proxy")
        candidates = [item[field] for field in FIELDS]
        if len(set(candidates)) != len(candidates):
            raise ValueError(f"item {index}: duplicate candidate options")

        target = row["target_intervention_span"]
        unrelated = row["unrelated_control_word"]
        if row["original"].count(target) != 1 or row["original"].count(unrelated) != 1:
            raise ValueError(f"item {index}: non-unique target/unrelated span")
        if target == unrelated:
            raise ValueError(f"item {index}: target equals unrelated control")
        if row["target_kana_sentence"] != row["original"].replace(
            target, row["target_reading"], 1
        ):
            raise ValueError(f"item {index}: invalid target replacement")
        if row["unrelated_control_kana_sentence"] != row["original"].replace(
            unrelated, row["unrelated_control_reading"], 1
        ):
            raise ValueError(f"item {index}: invalid unrelated replacement")

        related_fields = (
            row["related_semantic_cue_word"],
            row["related_semantic_cue_reading"],
            row["related_semantic_cue_kana_sentence"],
        )
        if all(value is None for value in related_fields):
            if row["candidate_control_count"] != 1:
                raise ValueError(f"item {index}: missing related cue despite multiple controls")
        elif any(value is None for value in related_fields):
            raise ValueError(f"item {index}: partially missing related cue")
        else:
            related = row["related_semantic_cue_word"]
            if related in {target, unrelated} or row["original"].count(related) != 1:
                raise ValueError(f"item {index}: invalid related cue span")
            if row["related_semantic_cue_kana_sentence"] != row["original"].replace(
                related, row["related_semantic_cue_reading"], 1
            ):
                raise ValueError(f"item {index}: invalid related replacement")


def atomic_write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def percentile(sorted_values: list[float], probability: float) -> float:
    position = probability * (len(sorted_values) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return sorted_values[lower]
    weight = position - lower
    return sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight


def describe(values: list[float], seed_offset: int) -> dict[str, Any]:
    if not values:
        raise ValueError("Cannot describe an empty value list")
    rng = random.Random(BOOTSTRAP_SEED + seed_offset)
    n = len(values)
    bootstrap_means = [
        statistics.mean(values[rng.randrange(n)] for _ in range(n))
        for _ in range(BOOTSTRAP_SAMPLES)
    ]
    bootstrap_means.sort()
    return {
        "mean": statistics.mean(values),
        "median": statistics.median(values),
        "bootstrap_mean_95ci": [
            percentile(bootstrap_means, 0.025),
            percentile(bootstrap_means, 0.975),
        ],
        "positive_count": sum(value > 0 for value in values),
        "negative_count": sum(value < 0 for value in values),
        "zero_count": sum(value == 0 for value in values),
    }


def exact_mcnemar(original: list[int], condition: list[int]) -> dict[str, Any]:
    gains = sum(left != 0 and right == 0 for left, right in zip(original, condition))
    losses = sum(left == 0 and right != 0 for left, right in zip(original, condition))
    discordant = gains + losses
    if discordant == 0:
        p_value = 1.0
    else:
        tail = sum(
            math.comb(discordant, k) for k in range(min(gains, losses) + 1)
        ) / (2**discordant)
        p_value = min(1.0, 2 * tail)
    return {
        "wrong_to_correct": gains,
        "correct_to_wrong": losses,
        "discordant": discordant,
        "exact_two_sided_p": p_value,
    }


def subset_summary(
    records: list[dict[str, Any]], *, include_related: bool, seed_base: int
) -> dict[str, Any]:
    conditions = [*BASE_CONDITIONS]
    if include_related:
        if not all(record["related_available"] for record in records):
            raise ValueError("Related subset contains records without a related cue")
        conditions.append(RELATED_CONDITION)
    original_choices = [
        record["conditions"]["original"]["candidate_only"]["choice"]
        for record in records
    ]
    condition_summary: dict[str, Any] = {}
    for condition in conditions:
        choices = [
            record["conditions"][condition]["candidate_only"]["choice"]
            for record in records
        ]
        margins = [record["margins"][condition] for record in records]
        condition_summary[condition] = {
            "correct": sum(choice == 0 for choice in choices),
            "wrong1": sum(choice == 1 for choice in choices),
            "choice_counts": {
                field: sum(choice == position for choice in choices)
                for position, field in enumerate(FIELDS)
            },
            "mean_margin": statistics.mean(margins),
            "median_margin": statistics.median(margins),
            "choice_changes_from_original": sum(
                choice != original
                for choice, original in zip(choices, original_choices)
            ),
            "correctness_transition_from_original": exact_mcnemar(
                original_choices, choices
            ),
        }

    effect_keys = [
        "target_effect",
        "unrelated_control_effect",
        "orthography_effect_vs_unrelated",
    ]
    if include_related:
        effect_keys.extend(
            [
                "related_semantic_cue_effect",
                "orthography_effect_vs_related",
                "related_minus_unrelated_control_effect",
            ]
        )
    effects = {
        key: describe([record["effects"][key] for record in records], seed_base + offset)
        for offset, key in enumerate(effect_keys, start=1)
    }
    result: dict[str, Any] = {
        "n_items": len(records),
        "surface_exact": sum(record["surface_exact"] for record in records),
        "surface_variant": sum(not record["surface_exact"] for record in records),
        "unrelated_control_quality_proxy": dict(
            Counter(record["unrelated_control_quality_proxy"] for record in records)
        ),
        "condition_summary": condition_summary,
        "effects": effects,
    }
    if include_related:
        abs_unrelated = [
            abs(record["effects"]["unrelated_control_effect"]) for record in records
        ]
        abs_related = [
            abs(record["effects"]["related_semantic_cue_effect"]) for record in records
        ]
        differences = [
            related - unrelated
            for unrelated, related in zip(abs_unrelated, abs_related)
        ]
        result["control_perturbation_comparison"] = {
            "absolute_unrelated_control_effect": describe(
                abs_unrelated, seed_base + 101
            ),
            "absolute_related_semantic_cue_effect": describe(
                abs_related, seed_base + 102
            ),
            "absolute_related_minus_unrelated": describe(
                differences, seed_base + 103
            ),
            "unrelated_closer_to_original_count": sum(
                unrelated < related
                for unrelated, related in zip(abs_unrelated, abs_related)
            ),
            "related_closer_to_original_count": sum(
                related < unrelated
                for unrelated, related in zip(abs_unrelated, abs_related)
            ),
            "ties": sum(
                unrelated == related
                for unrelated, related in zip(abs_unrelated, abs_related)
            ),
        }
    return result


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    holdout = [record for record in records if not record["previously_exposed_causal_item"]]
    primary = [
        record
        for record in holdout
        if record["unrelated_control_quality_proxy"] in {"high", "medium"}
    ]
    high_only = [
        record
        for record in holdout
        if record["unrelated_control_quality_proxy"] == "high"
    ]
    four_all = [record for record in records if record["related_available"]]
    four_holdout = [record for record in holdout if record["related_available"]]
    four_primary = [record for record in primary if record["related_available"]]

    analysis_sets = {
        "primary_holdout_nonweak_negative_control": subset_summary(
            primary, include_related=False, seed_base=1000
        ),
        "holdout_all_negative_controls": subset_summary(
            holdout, include_related=False, seed_base=2000
        ),
        "holdout_high_proxy_only": subset_summary(
            high_only, include_related=False, seed_base=3000
        ),
        "all_included_negative_controls": subset_summary(
            records, include_related=False, seed_base=4000
        ),
        "four_condition_primary_common_subset": subset_summary(
            four_primary, include_related=True, seed_base=5000
        ),
        "four_condition_holdout_all_controls": subset_summary(
            four_holdout, include_related=True, seed_base=6000
        ),
        "four_condition_all_included": subset_summary(
            four_all, include_related=True, seed_base=7000
        ),
    }
    surface_strata: dict[str, Any] = {}
    for offset, (label, expected) in enumerate(
        (("surface_exact", True), ("surface_variant", False)), start=1
    ):
        subset = [record for record in primary if record["surface_exact"] is expected]
        surface_strata[label] = {
            "n_items": len(subset),
            "orthography_effect_vs_unrelated": describe(
                [record["effects"]["orthography_effect_vs_unrelated"] for record in subset],
                8000 + offset,
            ),
        }
    return {
        "primary_analysis_set": "primary_holdout_nonweak_negative_control",
        "primary_analysis_rationale": (
            "exclude 35 previously exposed causal items and source-only weak-control proxies; "
            "the inclusive holdout and high-only proxy sets are frozen sensitivity analyses"
        ),
        "analysis_sets": analysis_sets,
        "primary_surface_strata": surface_strata,
        "bootstrap": {
            "resamples": BOOTSTRAP_SAMPLES,
            "seed": BOOTSTRAP_SEED,
            "unit": "paired item",
        },
        "warnings": [
            "Controls were assigned by a deterministic source-only heuristic under user authorization.",
            "No independent bilingual reviewer validated all interventions.",
            "Control quality labels are pre-outcome heuristic proxies, not gold semantic judgments.",
            "The related semantic cue is an exploratory intervention, not a negative control.",
            "Rows without two distinct non-target kanji controls do not enter related-vs-unrelated comparisons.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--material", type=Path, default=DEFAULT_MATERIAL)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--revision", default=DEFAULT_REVISION)
    parser.add_argument("--device", default="auto", choices=("auto", "cpu", "mps", "cuda"))
    parser.add_argument("--local-files-only", action="store_true")
    parser.add_argument("--validate-material-only", action="store_true")
    parser.add_argument(
        "--limit",
        type=int,
        help="Development-only prefix limit; omit for the frozen full run.",
    )
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    material_path = args.material.resolve()
    if not material_path.exists():
        raise FileNotFoundError(
            f"Orthography material is missing: {material_path}. Run "
            "`python scripts/prepare_orthography_control_relevance_full.py` "
            "after bootstrapping the pinned upstream benchmark."
        )
    rows = load_jsonl(material_path)
    validate_material(rows)
    material_hash = sha256(material_path)
    if args.limit is not None:
        if args.limit <= 0:
            parser.error("--limit must be positive")
        rows = rows[: args.limit]
        print("WARNING: development prefix limit is active; this is not a full result")
    print(f"material: {material_path}")
    print(f"items with negative control: {len(rows)}")
    print(f"items with distinct related cue: {sum(row['related_semantic_cue_word'] is not None for row in rows)}")
    print(f"sha256: {material_hash}")
    print("material structure: VALID")
    if args.validate_material_only:
        return
    if args.output is None:
        parser.error("--output is required unless --validate-material-only is used")

    output_path = args.output.resolve()
    summary_path = output_path.with_suffix(".summary.json")
    if not args.force and (output_path.exists() or summary_path.exists()):
        raise FileExistsError("Output already exists; use a new path or --force")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    device = select_device(args.device)
    dtype = select_dtype(device)
    print(f"model: {args.model}")
    print(f"revision: {args.revision}")
    print(f"device: {device}")
    print(f"dtype: {dtype}")
    tokenizer = AutoTokenizer.from_pretrained(
        args.model,
        revision=args.revision,
        local_files_only=args.local_files_only,
        trust_remote_code=True,
    )
    model = AutoModelForCausalLM.from_pretrained(
        args.model,
        revision=args.revision,
        torch_dtype=dtype,
        low_cpu_mem_usage=True,
        local_files_only=args.local_files_only,
        trust_remote_code=True,
    ).to(device).eval()
    resolved_revision = getattr(model.config, "_commit_hash", None)
    parameter_count = sum(parameter.numel() for parameter in model.parameters())
    print(f"parameters: {parameter_count / 1e9:.3f}B")
    print(f"resolved revision: {resolved_revision}\n")

    indexed_dataset = list(dataset.items())
    records: list[dict[str, Any]] = []
    for position, row in enumerate(rows, start=1):
        _, item = indexed_dataset[row["item_index"]]
        candidates = [item[field] for field in FIELDS]
        source_sentences = {
            "original": row["original"],
            "target_kana": row["target_kana_sentence"],
            "unrelated_control_kana": row["unrelated_control_kana_sentence"],
        }
        if row["related_semantic_cue_kana_sentence"] is not None:
            source_sentences[RELATED_CONDITION] = row[
                "related_semantic_cue_kana_sentence"
            ]
        source_token_counts = {
            condition: len(tokenizer(source, add_special_tokens=False)["input_ids"])
            for condition, source in source_sentences.items()
        }
        condition_results: dict[str, Any] = {}
        with torch.inference_mode():
            for condition, source_sentence in source_sentences.items():
                scores = [
                    score_candidate(model, tokenizer, source_sentence, candidate, device)
                    for candidate in candidates
                ]
                condition_results[condition] = pack_scores(scores)

        margins = {
            condition: condition_results[condition]["candidate_only"]
            ["shortcut_margin_wrong1_minus_correct"]
            for condition in source_sentences
        }
        target_effect = margins["target_kana"] - margins["original"]
        unrelated_effect = margins["unrelated_control_kana"] - margins["original"]
        effects: dict[str, float | None] = {
            "target_effect": target_effect,
            "unrelated_control_effect": unrelated_effect,
            "orthography_effect_vs_unrelated": target_effect - unrelated_effect,
            "related_semantic_cue_effect": None,
            "orthography_effect_vs_related": None,
            "related_minus_unrelated_control_effect": None,
        }
        if RELATED_CONDITION in margins:
            related_effect = margins[RELATED_CONDITION] - margins["original"]
            effects.update(
                {
                    "related_semantic_cue_effect": related_effect,
                    "orthography_effect_vs_related": target_effect - related_effect,
                    "related_minus_unrelated_control_effect": related_effect
                    - unrelated_effect,
                }
            )
        finite_values = [*margins.values()] + [
            value for value in effects.values() if value is not None
        ]
        if not all(math.isfinite(value) for value in finite_values):
            raise RuntimeError(f"item {row['item_index']}: non-finite effect")

        record = {
            "experiment": EXPERIMENT,
            "model": args.model,
            "requested_revision": args.revision,
            "resolved_revision": resolved_revision,
            "material_sha256": material_hash,
            "item_index": row["item_index"],
            "word": row["word"],
            "japanese_word": row["japanese_word"],
            "target_intervention_span": row["target_intervention_span"],
            "target_span_rule": row["target_span_rule"],
            "surface_exact": row["surface_exact"],
            "previously_exposed_causal_item": row[
                "previously_exposed_causal_item"
            ],
            "unrelated_control_quality_proxy": row[
                "unrelated_control_quality_proxy"
            ],
            "review_status": row["review_status"],
            "related_available": RELATED_CONDITION in source_sentences,
            "control_spans": {
                "unrelated": row["unrelated_control_word"],
                "related_semantic_cue": row["related_semantic_cue_word"],
            },
            "source_sentences": source_sentences,
            "source_token_counts": source_token_counts,
            "candidates": candidates,
            "conditions": condition_results,
            "margins": margins,
            "effects": effects,
        }
        records.append(record)
        choices = "/".join(
            str(condition_results[condition]["candidate_only"]["choice"])
            for condition in source_sentences
        )
        print(
            f"[{position:03d}/{len(rows)}] {row['word']}: choices={choices} "
            f"E_unrelated={effects['orthography_effect_vs_unrelated']:+.6f}"
        )

    summary = {
        "experiment": EXPERIMENT,
        "model": args.model,
        "requested_revision": args.revision,
        "resolved_revision": resolved_revision,
        "parameter_count": parameter_count,
        "material_path": str(material_path),
        "material_sha256": material_hash,
        "selection_rule": rows[0]["selection_rule"],
        "n_records": len(records),
        "n_related_available": sum(record["related_available"] for record in records),
        "inference_status": (
            "full_source_only_controls_no_independent_bilingual_second_review"
        ),
        "primary_metric": "candidate_only_mean_nll",
        "margin_definition": "NLL(wrong1)-NLL(correct); larger favors correct",
        **summarize(records),
    }
    atomic_write_jsonl(output_path, records)
    atomic_write_json(summary_path, summary)
    primary = summary["analysis_sets"][summary["primary_analysis_set"]]
    common = summary["analysis_sets"]["four_condition_primary_common_subset"]
    print("\n=== full control-relevance summary ===")
    print(f"records: {len(records)}; related common subset: {summary['n_related_available']}")
    print(
        "primary holdout nonweak effect vs unrelated: "
        f"{primary['effects']['orthography_effect_vs_unrelated']['mean']:+.6f}"
    )
    print(
        "four-condition primary related-minus-unrelated: "
        f"{common['effects']['related_minus_unrelated_control_effect']['mean']:+.6f}"
    )
    print(f"results: {output_path}")
    print(f"summary: {summary_path}")
    print("INFERENCE: source-only automatic controls; no independent bilingual review")


if __name__ == "__main__":
    main()
