#!/usr/bin/env python3
"""Validate the public scores-only five-item matched-probe artifact."""

from __future__ import annotations

import json
import math
from pathlib import Path
from statistics import mean
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "results"
    / "analysis"
    / "qwen3-8b-clean-matched-probe-five-item-pilot.json"
)
EXPECTED_ITEMS = [35, 175, 300, 354, 451]
EXPECTED_EQUAL_LENGTH = [175, 354]
EXPECTED_UNSAFE = [354, 451]
CONDITIONS = ["original", "target_kana", "unrelated_control_kana"]
FORBIDDEN_KEYS = {
    "word",
    "japanese_word",
    "chinese_word",
    "candidates",
    "candidate_tokens",
    "source_sentences",
}
TOLERANCE = 1e-12


def close(left: float, right: float) -> bool:
    return math.isclose(float(left), float(right), rel_tol=TOLERANCE, abs_tol=TOLERANCE)


def walk(value: Any, path: tuple[str, ...] = ()) -> list[str]:
    problems: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            if key in FORBIDDEN_KEYS:
                problems.append(".".join((*path, key)))
            problems.extend(walk(item, (*path, key)))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            problems.extend(walk(item, (*path, str(index))))
    return problems


def sign(value: float) -> str:
    if value > 0:
        return "+"
    if value < 0:
        return "-"
    return "0"


def main() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    errors: list[str] = []

    if payload.get("public_artifact_schema") != "scores_only_v1":
        errors.append("missing scores_only_v1 schema")
    if payload.get("experiment_id") != "EXP-20260828-clean-matched-probe-pilot-v1":
        errors.append("experiment ID mismatch")
    if payload.get("benchmark_text_removed") is not True:
        errors.append("benchmark_text_removed is not true")
    forbidden = walk(payload)
    if forbidden:
        errors.append(f"forbidden fields: {forbidden}")
    if payload.get("model") != "Qwen/Qwen3-8B":
        errors.append("model mismatch")
    if payload.get("requested_revision") != payload.get("resolved_revision"):
        errors.append("requested/resolved revision mismatch")
    if payload.get("condition_order") != CONDITIONS:
        errors.append("condition order mismatch")
    if payload.get("hidden_state_indices") != list(range(37)):
        errors.append("hidden-state index mismatch")

    items = payload.get("item_results", [])
    if [row.get("item_index") for row in items] != EXPECTED_ITEMS:
        errors.append("item order mismatch")

    positive_items: list[int] = []
    unsafe_rescues = 0
    scoring_sensitive: list[int] = []
    by_item: dict[int, dict[str, Any]] = {}
    for row in items:
        item = int(row["item_index"])
        by_item[item] = row
        margins = row["primary_final_margins"]
        if list(margins) != CONDITIONS:
            errors.append(f"item {item}: margin condition order mismatch")
            continue
        delta = float(margins["target_kana"]) - float(
            margins["unrelated_control_kana"]
        )
        if not close(delta, row["primary_final_delta_target_control"]):
            errors.append(f"item {item}: primary Delta mismatch")
        if (delta > 0) != bool(row["prediction_supported"]):
            errors.append(f"item {item}: prediction flag mismatch")
        if delta > 0:
            positive_items.append(item)

        choices = row["primary_final_choices_reference_0_form_1"]
        expected_choices = {
            condition: 0 if float(margins[condition]) >= 0 else 1
            for condition in CONDITIONS
        }
        if choices != expected_choices:
            errors.append(f"item {item}: primary choices mismatch")

        metric_deltas = row["metric_final_deltas"]
        score_signs = {
            sign(metric_deltas["complete_candidate_mean_nll"]),
            sign(metric_deltas["raw_complete_sequence_log_probability"]),
            sign(metric_deltas["lexical_span_sequence_log_probability"]),
        }
        expected_sensitive = len(score_signs) > 1
        if bool(row["scoring_sensitive"]) != expected_sensitive:
            errors.append(f"item {item}: scoring-sensitive flag mismatch")
        if expected_sensitive:
            scoring_sensitive.append(item)

        upper = row["upper_band"]
        if upper["layers"] != list(range(29, 35)):
            errors.append(f"item {item}: upper-band layers mismatch")
        values = [float(value) for value in upper["delta_values"]]
        if len(values) != 6 or not all(math.isfinite(value) for value in values):
            errors.append(f"item {item}: invalid upper-band values")
        if not close(mean(values), upper["mean_delta"]):
            errors.append(f"item {item}: upper-band mean mismatch")
        if "".join(sign(value) for value in values) != upper["sign_sequence"]:
            errors.append(f"item {item}: upper-band sign sequence mismatch")
        final_sign = sign(delta)
        matches = sum(sign(value) == final_sign for value in values)
        if matches != upper["same_sign_as_final_count"]:
            errors.append(f"item {item}: upper/final sign count mismatch")

        if item in EXPECTED_UNSAFE:
            rescue = (
                choices["original"] == 1
                and choices["target_kana"] == 0
                and choices["unrelated_control_kana"] == 1
            )
            if rescue:
                unsafe_rescues += 1
            if bool(row["unsafe_rescue"]) != rescue:
                errors.append(f"item {item}: unsafe rescue flag mismatch")

    aggregates = payload["descriptive_aggregates"]
    if aggregates["primary_positive_items"] != positive_items:
        errors.append("positive item list mismatch")
    if aggregates["primary_positive_count"] != len(positive_items):
        errors.append("positive item count mismatch")
    if aggregates["scoring_sensitive_items"] != scoring_sensitive:
        errors.append("scoring-sensitive item list mismatch")
    if aggregates["unsafe_rescue_count"] != unsafe_rescues:
        errors.append("unsafe rescue count mismatch")

    equal_deltas = [
        by_item[item]["primary_final_delta_target_control"]
        for item in EXPECTED_EQUAL_LENGTH
    ]
    if aggregates["equal_length_core_items"] != EXPECTED_EQUAL_LENGTH:
        errors.append("equal-length core mismatch")
    if aggregates["equal_length_core_support_count"] != sum(
        value > 0 for value in equal_deltas
    ):
        errors.append("equal-length support count mismatch")
    if not close(mean(equal_deltas), aggregates["equal_length_core_mean_delta"]):
        errors.append("equal-length mean mismatch")

    validation = payload["validation"]
    if validation["supplemental_topk_tie_audit_status"] != "PASS":
        errors.append("supplemental validation did not pass")
    if validation["remaining_blocker_count"] != 0:
        errors.append("supplemental validation has blockers")
    if validation["final_projection_max_abs_difference"] > 1e-4:
        errors.append("final projection exceeded tolerance")
    execution = payload["execution"]
    if execution["model_inference_runs"] != 1 or execution["automatic_reruns"] != 0:
        errors.append("model-run count mismatch")
    if execution["authorization_consumed"] is not True:
        errors.append("authorization receipt mismatch")
    if execution["pod_final_status"] != "EXITED / stopped":
        errors.append("Pod final status mismatch")

    if errors:
        raise SystemExit("PUBLIC PILOT VALIDATION FAILED\n" + "\n".join(errors))
    print("VALID: five-item public matched-probe artifact")
    print("VALID: primary margins, Delta values, choices, and aggregates recompute")
    print("VALID: no benchmark or intervention text fields are present")


if __name__ == "__main__":
    main()
