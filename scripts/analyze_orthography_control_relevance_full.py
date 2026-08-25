#!/usr/bin/env python3
"""Create post-run diagnostics for the frozen full orthography experiment."""

from __future__ import annotations

import argparse
import json
import math
import random
import statistics
from collections import Counter
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = (
    PROJECT_ROOT
    / "results"
    / "causal"
    / "Qwen--Qwen2.5-7B-Instruct-1M-orthography-control-relevance-full-v1.jsonl"
)
DEFAULT_OUTPUT = (
    PROJECT_ROOT
    / "results"
    / "analysis"
    / "orthography-control-relevance-full-v1-diagnostics.json"
)
FIELDS = ("correct", "wrong1", "wrong2", "wrong3")
SEED = 20260825
BOOTSTRAP_SAMPLES = 10000


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def percentile(sorted_values: list[float], probability: float) -> float:
    position = probability * (len(sorted_values) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return sorted_values[lower]
    weight = position - lower
    return sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight


def bootstrap_independent_mean_difference(
    left: list[float], right: list[float]
) -> dict[str, Any]:
    rng = random.Random(SEED + 9001)
    differences = []
    for _ in range(BOOTSTRAP_SAMPLES):
        left_mean = statistics.mean(left[rng.randrange(len(left))] for _ in left)
        right_mean = statistics.mean(right[rng.randrange(len(right))] for _ in right)
        differences.append(left_mean - right_mean)
    differences.sort()
    return {
        "mean_difference": statistics.mean(left) - statistics.mean(right),
        "bootstrap_95ci": [
            percentile(differences, 0.025),
            percentile(differences, 0.975),
        ],
        "definition": "mean(surface_exact)-mean(surface_variant)",
    }


def exact_paired_binary(left: list[bool], right: list[bool]) -> dict[str, Any]:
    left_to_right = sum(a and not b for a, b in zip(left, right))
    right_to_left = sum(not a and b for a, b in zip(left, right))
    discordant = left_to_right + right_to_left
    if not discordant:
        p_value = 1.0
    else:
        tail = sum(
            math.comb(discordant, k)
            for k in range(min(left_to_right, right_to_left) + 1)
        ) / (2**discordant)
        p_value = min(1.0, 2 * tail)
    return {
        "left_true_to_right_false": left_to_right,
        "left_false_to_right_true": right_to_left,
        "discordant": discordant,
        "exact_two_sided_p": p_value,
    }


def sign_and_trimmed_mean(values: list[float]) -> dict[str, Any]:
    nonzero = [value for value in values if value != 0]
    positive = sum(value > 0 for value in nonzero)
    n = len(nonzero)
    tail = sum(
        math.comb(n, k) for k in range(min(positive, n - positive) + 1)
    ) / (2**n)
    ordered = sorted(values)
    trim = int(0.10 * len(ordered))
    trimmed = ordered[trim:-trim] if trim else ordered
    return {
        "positive": positive,
        "negative": n - positive,
        "positive_proportion": positive / n,
        "exact_two_sided_sign_p": min(1.0, 2 * tail),
        "ten_percent_trimmed_mean": statistics.mean(trimmed),
        "minimum": ordered[0],
        "maximum": ordered[-1],
    }


def transition_matrix(records: list[dict[str, Any]], condition: str) -> dict[str, Any]:
    matrix = [[0 for _ in FIELDS] for _ in FIELDS]
    for record in records:
        original = record["conditions"]["original"]["candidate_only"]["choice"]
        changed = record["conditions"][condition]["candidate_only"]["choice"]
        matrix[original][changed] += 1
    return {
        "labels": list(FIELDS),
        "rows_original_columns_condition": matrix,
    }


def pearson(left: list[float], right: list[float]) -> float | None:
    if len(left) != len(right) or len(left) < 2:
        return None
    left_mean = statistics.mean(left)
    right_mean = statistics.mean(right)
    numerator = sum(
        (a - left_mean) * (b - right_mean) for a, b in zip(left, right)
    )
    denominator = math.sqrt(
        sum((a - left_mean) ** 2 for a in left)
        * sum((b - right_mean) ** 2 for b in right)
    )
    return numerator / denominator if denominator else None


def effect_by_category(
    records: list[dict[str, Any]], category_key: str, effect_key: str
) -> dict[str, Any]:
    groups: dict[str, list[float]] = {}
    for record in records:
        label = str(record[category_key])
        groups.setdefault(label, []).append(record["effects"][effect_key])
    return {
        label: {
            "n": len(values),
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "positive": sum(value > 0 for value in values),
        }
        for label, values in sorted(groups.items())
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    records = load_jsonl(args.input.resolve())
    primary = [
        record
        for record in records
        if not record["previously_exposed_causal_item"]
        and record["unrelated_control_quality_proxy"] in {"high", "medium"}
    ]
    exact = [
        record["effects"]["orthography_effect_vs_unrelated"]
        for record in primary
        if record["surface_exact"]
    ]
    variant = [
        record["effects"]["orthography_effect_vs_unrelated"]
        for record in primary
        if not record["surface_exact"]
    ]

    original_choices = [
        record["conditions"]["original"]["candidate_only"]["choice"]
        for record in primary
    ]
    target_choices = [
        record["conditions"]["target_kana"]["candidate_only"]["choice"]
        for record in primary
    ]
    unrelated_choices = [
        record["conditions"]["unrelated_control_kana"]["candidate_only"]["choice"]
        for record in primary
    ]

    target_token_delta = [
        record["source_token_counts"]["target_kana"]
        - record["source_token_counts"]["original"]
        for record in primary
    ]
    unrelated_token_delta = [
        record["source_token_counts"]["unrelated_control_kana"]
        - record["source_token_counts"]["original"]
        for record in primary
    ]
    orthography_effects = [
        record["effects"]["orthography_effect_vs_unrelated"] for record in primary
    ]

    token_delta_category_records: list[dict[str, Any]] = []
    for record, target_delta, unrelated_delta in zip(
        primary, target_token_delta, unrelated_token_delta
    ):
        copied = dict(record)
        difference = target_delta - unrelated_delta
        copied["token_delta_difference_category"] = (
            "target_more_tokens"
            if difference > 0
            else "target_fewer_tokens"
            if difference < 0
            else "matched"
        )
        token_delta_category_records.append(copied)

    original_wrong1 = [choice == 1 for choice in original_choices]
    target_wrong1 = [choice == 1 for choice in target_choices]
    unrelated_wrong1 = [choice == 1 for choice in unrelated_choices]
    original_correct = [choice == 0 for choice in original_choices]
    target_correct = [choice == 0 for choice in target_choices]
    unrelated_correct = [choice == 0 for choice in unrelated_choices]

    payload = {
        "analysis_set": "primary_holdout_nonweak_negative_control",
        "n_items": len(primary),
        "choice_transition_matrices": {
            "target_kana": transition_matrix(primary, "target_kana"),
            "unrelated_control_kana": transition_matrix(
                primary, "unrelated_control_kana"
            ),
        },
        "paired_binary_transitions": {
            "correct_original_vs_target": exact_paired_binary(
                original_correct, target_correct
            ),
            "correct_original_vs_unrelated": exact_paired_binary(
                original_correct, unrelated_correct
            ),
            "wrong1_original_vs_target": exact_paired_binary(
                original_wrong1, target_wrong1
            ),
            "wrong1_original_vs_unrelated": exact_paired_binary(
                original_wrong1, unrelated_wrong1
            ),
        },
        "surface_interaction": bootstrap_independent_mean_difference(exact, variant),
        "orthography_effect_robustness": sign_and_trimmed_mean(orthography_effects),
        "effect_by_quality_proxy": effect_by_category(
            primary,
            "unrelated_control_quality_proxy",
            "orthography_effect_vs_unrelated",
        ),
        "tokenization_diagnostics": {
            "target_token_delta_distribution": dict(Counter(target_token_delta)),
            "unrelated_token_delta_distribution": dict(Counter(unrelated_token_delta)),
            "mean_target_token_delta": statistics.mean(target_token_delta),
            "mean_unrelated_token_delta": statistics.mean(unrelated_token_delta),
            "pearson_target_delta_with_target_effect": pearson(
                target_token_delta,
                [record["effects"]["target_effect"] for record in primary],
            ),
            "pearson_unrelated_delta_with_unrelated_effect": pearson(
                unrelated_token_delta,
                [record["effects"]["unrelated_control_effect"] for record in primary],
            ),
            "pearson_delta_difference_with_orthography_effect": pearson(
                [
                    target_delta - unrelated_delta
                    for target_delta, unrelated_delta in zip(
                        target_token_delta, unrelated_token_delta
                    )
                ],
                orthography_effects,
            ),
            "orthography_effect_by_token_delta_difference": effect_by_category(
                token_delta_category_records,
                "token_delta_difference_category",
                "orthography_effect_vs_unrelated",
            ),
        },
        "interpretation_guards": [
            "The continuous margin isolates correct versus wrong1 preference; it is not four-way accuracy.",
            "A positive margin effect can coexist with correct-to-wrong2/wrong3 transitions.",
            "Surface and tokenization analyses are pre-specified or diagnostic interactions, not new treatment randomizations.",
        ],
    }
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(output.name + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    temporary.replace(output)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"diagnostics: {output}")


if __name__ == "__main__":
    main()
