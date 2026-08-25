#!/usr/bin/env python3
"""Validate full-set orthography control-relevance output invariants."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
from pathlib import Path
from typing import Any


FIELDS = ("correct", "wrong1", "wrong2", "wrong3")
BASE_CONDITIONS = ("original", "target_kana", "unrelated_control_kana")
RELATED_CONDITION = "related_semantic_cue_kana"
BASE_EFFECTS = (
    "target_effect",
    "unrelated_control_effect",
    "orthography_effect_vs_unrelated",
)
RELATED_EFFECTS = (
    "related_semantic_cue_effect",
    "orthography_effect_vs_related",
    "related_minus_unrelated_control_effect",
)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def close(left: float, right: float) -> bool:
    return math.isclose(left, right, rel_tol=1e-9, abs_tol=1e-9)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_scores(record: dict[str, Any]) -> None:
    item_index = record["item_index"]
    expected_conditions = set(BASE_CONDITIONS)
    if record["related_available"]:
        expected_conditions.add(RELATED_CONDITION)
    if set(record["conditions"]) != expected_conditions:
        raise ValueError(f"item {item_index}: condition mismatch")
    if set(record["margins"]) != expected_conditions:
        raise ValueError(f"item {item_index}: margin mismatch")
    margins: dict[str, float] = {}
    for condition in expected_conditions:
        packed = record["conditions"][condition]
        for score_type in ("official", "candidate_only"):
            scores = packed[score_type]
            losses = scores["losses"]
            ppls = scores["ppls"]
            if len(losses) != 4 or len(ppls) != 4:
                raise ValueError(f"item {item_index}: score length mismatch")
            if not all(math.isfinite(value) for value in losses + ppls):
                raise ValueError(f"item {item_index}: non-finite score")
            choice = min(range(4), key=losses.__getitem__)
            if scores["choice"] != choice or scores["choice_field"] != FIELDS[choice]:
                raise ValueError(f"item {item_index}: argmin mismatch")
            if scores["correct"] != (choice == 0):
                raise ValueError(f"item {item_index}: correct flag mismatch")
            for loss, ppl in zip(losses, ppls):
                if not close(math.exp(loss), ppl):
                    raise ValueError(f"item {item_index}: PPL mismatch")
        losses = packed["candidate_only"]["losses"]
        margin = losses[1] - losses[0]
        stored = packed["candidate_only"]["shortcut_margin_wrong1_minus_correct"]
        if not close(margin, stored) or not close(margin, record["margins"][condition]):
            raise ValueError(f"item {item_index}: candidate-only margin mismatch")
        margins[condition] = margin

    target = margins["target_kana"] - margins["original"]
    unrelated = margins["unrelated_control_kana"] - margins["original"]
    expected_effects: dict[str, float | None] = {
        "target_effect": target,
        "unrelated_control_effect": unrelated,
        "orthography_effect_vs_unrelated": target - unrelated,
        "related_semantic_cue_effect": None,
        "orthography_effect_vs_related": None,
        "related_minus_unrelated_control_effect": None,
    }
    if record["related_available"]:
        related = margins[RELATED_CONDITION] - margins["original"]
        expected_effects.update(
            {
                "related_semantic_cue_effect": related,
                "orthography_effect_vs_related": target - related,
                "related_minus_unrelated_control_effect": related - unrelated,
            }
        )
    if set(record["effects"]) != set(expected_effects):
        raise ValueError(f"item {item_index}: effect keys mismatch")
    for key, expected in expected_effects.items():
        observed = record["effects"][key]
        if expected is None:
            if observed is not None:
                raise ValueError(f"item {item_index}: {key} should be null")
        elif observed is None or not close(expected, observed):
            raise ValueError(f"item {item_index}: {key} mismatch")


def verify_analysis_mean(
    summary: dict[str, Any], records: list[dict[str, Any]], set_name: str
) -> None:
    if set_name == "primary_holdout_nonweak_negative_control":
        subset = [
            record
            for record in records
            if not record["previously_exposed_causal_item"]
            and record["unrelated_control_quality_proxy"] in {"high", "medium"}
        ]
    elif set_name == "holdout_all_negative_controls":
        subset = [
            record for record in records if not record["previously_exposed_causal_item"]
        ]
    elif set_name == "holdout_high_proxy_only":
        subset = [
            record
            for record in records
            if not record["previously_exposed_causal_item"]
            and record["unrelated_control_quality_proxy"] == "high"
        ]
    elif set_name == "all_included_negative_controls":
        subset = records
    elif set_name == "four_condition_primary_common_subset":
        subset = [
            record
            for record in records
            if not record["previously_exposed_causal_item"]
            and record["unrelated_control_quality_proxy"] in {"high", "medium"}
            and record["related_available"]
        ]
    elif set_name == "four_condition_holdout_all_controls":
        subset = [
            record
            for record in records
            if not record["previously_exposed_causal_item"] and record["related_available"]
        ]
    elif set_name == "four_condition_all_included":
        subset = [record for record in records if record["related_available"]]
    else:
        raise ValueError(f"Unknown analysis set: {set_name}")
    block = summary["analysis_sets"][set_name]
    if block["n_items"] != len(subset):
        raise ValueError(f"{set_name}: item count mismatch")
    for effect in BASE_EFFECTS:
        expected = statistics.mean(record["effects"][effect] for record in subset)
        if not close(expected, block["effects"][effect]["mean"]):
            raise ValueError(f"{set_name}: {effect} summary mean mismatch")
    if set_name.startswith("four_condition"):
        for effect in RELATED_EFFECTS:
            expected = statistics.mean(record["effects"][effect] for record in subset)
            if not close(expected, block["effects"][effect]["mean"]):
                raise ValueError(f"{set_name}: {effect} summary mean mismatch")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--expected-items", type=int, required=True)
    parser.add_argument("--expected-related", type=int, required=True)
    parser.add_argument("--expected-revision", required=True)
    args = parser.parse_args()

    output = args.output.resolve()
    records = load_jsonl(output)
    if len(records) != args.expected_items:
        raise ValueError(f"Expected {args.expected_items} records, found {len(records)}")
    if sum(record["related_available"] for record in records) != args.expected_related:
        raise ValueError("Related-available count mismatch")
    if len({record["item_index"] for record in records}) != len(records):
        raise ValueError("Duplicate item_index")
    material_hashes = {record["material_sha256"] for record in records}
    if len(material_hashes) != 1:
        raise ValueError("Multiple material hashes")
    for record in records:
        if record["requested_revision"] != args.expected_revision:
            raise ValueError(f"item {record['item_index']}: requested revision mismatch")
        resolved = record["resolved_revision"]
        if resolved is not None and resolved != args.expected_revision:
            raise ValueError(f"item {record['item_index']}: resolved revision mismatch")
        if "candidates" in record and (
            len(record["candidates"]) != 4 or len(set(record["candidates"])) != 4
        ):
            raise ValueError(f"item {record['item_index']}: invalid candidates")
        validate_scores(record)

    summary_path = output.with_suffix(".summary.json")
    with summary_path.open(encoding="utf-8") as handle:
        summary = json.load(handle)
    if summary["n_records"] != len(records):
        raise ValueError("Summary record count mismatch")
    if summary["n_related_available"] != args.expected_related:
        raise ValueError("Summary related count mismatch")
    if summary["material_sha256"] not in material_hashes:
        raise ValueError("Summary material hash mismatch")
    if summary["requested_revision"] != args.expected_revision:
        raise ValueError("Summary requested revision mismatch")
    if "no_independent_bilingual_second_review" not in summary["inference_status"]:
        raise ValueError("Missing inference guard")
    expected_sets = {
        "primary_holdout_nonweak_negative_control",
        "holdout_all_negative_controls",
        "holdout_high_proxy_only",
        "all_included_negative_controls",
        "four_condition_primary_common_subset",
        "four_condition_holdout_all_controls",
        "four_condition_all_included",
    }
    if set(summary["analysis_sets"]) != expected_sets:
        raise ValueError("Analysis set mismatch")
    for set_name in expected_sets:
        verify_analysis_mean(summary, records, set_name)

    print(
        f"VALID: {len(records)} records ({args.expected_related} with related cue); "
        "revision, PPL, argmin, margins, effects, and analysis means verified"
    )
    print(f"material_sha256: {next(iter(material_hashes))}")
    print(f"results_sha256: {sha256(output)}")
    print(f"summary_sha256: {sha256(summary_path)}")


if __name__ == "__main__":
    main()
