#!/usr/bin/env python3
"""Analyze the preregistered six-model orthography replication."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import statistics
from collections import Counter
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULT_DIR = PROJECT_ROOT / "results" / "causal"
DEFAULT_INPUTS = (
    RESULT_DIR
    / "Qwen--Qwen2.5-7B-Instruct-1M-orthography-control-relevance-full-v1.jsonl",
    RESULT_DIR
    / "llm-jp--llm-jp-3-7.2b-instruct3-orthography-control-relevance-full-v1.jsonl",
    RESULT_DIR
    / "elyza--Llama-3-ELYZA-JP-8B-orthography-control-relevance-full-v1.jsonl",
    RESULT_DIR
    / "baichuan-inc--Baichuan2-7B-Base-orthography-control-relevance-full-v1.jsonl",
    RESULT_DIR
    / "mistralai--Mistral-7B-Instruct-v0.2-orthography-control-relevance-full-v1.jsonl",
    RESULT_DIR / "google--gemma-7b-orthography-control-relevance-full-v1.jsonl",
)
EXPECTED_REVISIONS = {
    "Qwen/Qwen2.5-7B-Instruct-1M": "e28526f7bb80e2a9c8af03b831a9af3812f18fba",
    "llm-jp/llm-jp-3-7.2b-instruct3": "cdd4c7f3296fdc7785423a864bd9a86ce4c15915",
    "elyza/Llama-3-ELYZA-JP-8B": "e6c316496ee7d9a11710c50229e8cb39b6b0a4a3",
    "baichuan-inc/Baichuan2-7B-Base": "f9d4d8dd2f7a3dbede3bda3b0cf0224e9272bbe5",
    "mistralai/Mistral-7B-Instruct-v0.2": "63a8b081895390a26e140280378bc85ec8bce07a",
    "google/gemma-7b": "ff6768d9368919a1f025a54f9f5aa0ee591730bb",
}
EXPECTED_MATERIAL_SHA256 = (
    "fa19564838ab4d86f8ecda1a08daf9e792e3d576734138927f2b569ef933b4c9"
)
CONDITIONS = ("original", "target_kana", "unrelated_control_kana")
FIELDS = ("correct", "wrong1", "wrong2", "wrong3")
BOOTSTRAP_SEED = 20260825
BOOTSTRAP_SAMPLES = 10000


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def percentile(sorted_values: list[float], probability: float) -> float:
    position = probability * (len(sorted_values) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return sorted_values[lower]
    weight = position - lower
    return sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight


def bootstrap_mean(values: list[float], seed_offset: int) -> dict[str, Any]:
    rng = random.Random(BOOTSTRAP_SEED + seed_offset)
    n = len(values)
    means = [
        statistics.mean(values[rng.randrange(n)] for _ in range(n))
        for _ in range(BOOTSTRAP_SAMPLES)
    ]
    means.sort()
    return {
        "mean": statistics.mean(values),
        "median": statistics.median(values),
        "bootstrap_mean_95ci": [percentile(means, 0.025), percentile(means, 0.975)],
        "positive": sum(value > 0 for value in values),
        "negative": sum(value < 0 for value in values),
        "zero": sum(value == 0 for value in values),
    }


def pearson(left: list[float], right: list[float]) -> float | None:
    if len(left) != len(right) or len(left) < 2:
        return None
    left_mean = statistics.mean(left)
    right_mean = statistics.mean(right)
    numerator = sum((a - left_mean) * (b - right_mean) for a, b in zip(left, right))
    denominator = math.sqrt(
        sum((value - left_mean) ** 2 for value in left)
        * sum((value - right_mean) ** 2 for value in right)
    )
    return numerator / denominator if denominator else None


def is_primary(record: dict[str, Any]) -> bool:
    return (
        not record["previously_exposed_causal_item"]
        and record["unrelated_control_quality_proxy"] in {"high", "medium"}
    )


def validate_run(path: Path, records: list[dict[str, Any]]) -> tuple[str, str]:
    if len(records) != 450:
        raise ValueError(f"{path}: expected 450 rows, found {len(records)}")
    models = {record["model"] for record in records}
    revisions = {record["requested_revision"] for record in records}
    material_hashes = {record["material_sha256"] for record in records}
    if len(models) != 1 or len(revisions) != 1 or len(material_hashes) != 1:
        raise ValueError(f"{path}: mixed model, revision, or material hash")
    model = next(iter(models))
    revision = next(iter(revisions))
    if model not in EXPECTED_REVISIONS:
        raise ValueError(f"{path}: unexpected model {model}")
    if revision != EXPECTED_REVISIONS[model]:
        raise ValueError(f"{path}: unexpected revision {revision}")
    if next(iter(material_hashes)) != EXPECTED_MATERIAL_SHA256:
        raise ValueError(f"{path}: unexpected material hash")
    if len({record["item_index"] for record in records}) != 450:
        raise ValueError(f"{path}: duplicate item index")
    primary = [record for record in records if is_primary(record)]
    if len(primary) != 382:
        raise ValueError(f"{path}: expected 382 primary rows, found {len(primary)}")
    return model, revision


def model_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    primary = [record for record in records if is_primary(record)]
    effects = [
        record["effects"]["orthography_effect_vs_unrelated"] for record in primary
    ]
    condition_summary: dict[str, Any] = {}
    for condition in CONDITIONS:
        choices = [
            record["conditions"][condition]["candidate_only"]["choice"]
            for record in primary
        ]
        condition_summary[condition] = {
            "choice_counts": {
                field: sum(choice == index for choice in choices)
                for index, field in enumerate(FIELDS)
            },
            "accuracy": sum(choice == 0 for choice in choices) / len(choices),
            "wrong1_rate": sum(choice == 1 for choice in choices) / len(choices),
        }
    original = condition_summary["original"]
    target = condition_summary["target_kana"]
    control = condition_summary["unrelated_control_kana"]
    return {
        "n_items": len(primary),
        # Match the full runner's primary-set orthography-effect stream exactly:
        # subset seed_base=1000 and this effect is the third described effect.
        "orthography_effect": bootstrap_mean(effects, 1003),
        "conditions": condition_summary,
        "accuracy_delta_target_minus_original": target["accuracy"]
        - original["accuracy"],
        "accuracy_delta_control_minus_original": control["accuracy"]
        - original["accuracy"],
        "wrong1_rate_delta_target_minus_original": target["wrong1_rate"]
        - original["wrong1_rate"],
        "wrong1_rate_delta_control_minus_original": control["wrong1_rate"]
        - original["wrong1_rate"],
    }


def format_ci(block: dict[str, Any]) -> str:
    lower, upper = block["bootstrap_mean_95ci"]
    return f"{block['mean']:+.3f} [{lower:+.3f}, {upper:+.3f}]"


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Six-Model Replication of the Kana Orthography Effect",
        "",
        "## Main results",
        "",
        "| Model | Mean orthography effect [95% CI] | Positive/negative items | Original acc. | Target acc. | Δacc. |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for model, block in payload["models"].items():
        effect = block["orthography_effect"]
        original = block["conditions"]["original"]["accuracy"]
        target = block["conditions"]["target_kana"]["accuracy"]
        lines.append(
            f"| `{model}` | {format_ci(effect)} | {effect['positive']}/{effect['negative']} "
            f"| {original:.1%} | {target:.1%} | {target-original:+.1%} |"
        )
    fixed = payload["fixed_model_set_average"]
    lines.extend(
        [
            "",
            "## Fixed six-model-set summary",
            "",
            "After averaging across models within each item and bootstrapping "
            f"the 382 items: **{format_ci(fixed)}**.",
            f"Positive model means: {payload['model_mean_signs']['positive']}/{payload['n_models']}; "
            f"interval entirely above zero: {payload['model_mean_signs']['ci_above_zero']}/{payload['n_models']}.",
            "",
            "This describes the fixed model set and is not a random-effects inference to all language models.",
            "",
            "## Directional consistency",
            "",
            "Distribution of the number of models with a positive item effect:",
            "",
            "| Models with positive effect | Items |",
            "|---:|---:|",
        ]
    )
    for count, frequency in sorted(
        payload["item_positive_model_count_distribution"].items(), key=lambda pair: int(pair[0])
    ):
        lines.append(f"| {count} | {frequency} |")
    lines.extend(
        [
            "",
            "## Interpretation boundary",
            "",
            "- The primary continuous effect compares candidate-only mean NLL for `correct` and `wrong1`; it is not a four-option accuracy gain.",
            "- Reusing the same source-only controls across models weakens a single-model explanation but does not remove limitations in control naturalness or semantic independence.",
            "- Model–item rows are not independent; the cross-model interval first averages models within item and then bootstraps items.",
            "- Model heterogeneity, choice transitions, and tokenization are diagnostics and do not supersede the preregistered primary analysis.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", nargs="+", type=Path, default=list(DEFAULT_INPUTS))
    parser.add_argument(
        "--output-json",
        type=Path,
        default=PROJECT_ROOT
        / "results"
        / "analysis"
        / "orthography-six-model-replication.json",
    )
    parser.add_argument(
        "--output-report",
        type=Path,
        default=PROJECT_ROOT
        / "results"
        / "analysis"
        / "orthography-six-model-replication.report.md",
    )
    parser.add_argument(
        "--allow-partial",
        action="store_true",
        help="Development only: analyze fewer than all six expected runs.",
    )
    args = parser.parse_args()

    runs: dict[str, list[dict[str, Any]]] = {}
    input_metadata: dict[str, Any] = {}
    for raw_path in args.inputs:
        path = raw_path.resolve()
        records = load_jsonl(path)
        model, revision = validate_run(path, records)
        if model in runs:
            raise ValueError(f"Duplicate model input: {model}")
        runs[model] = records
        input_metadata[model] = {
            "path": str(path),
            "revision": revision,
            "sha256": sha256(path),
        }
    if not args.allow_partial and set(runs) != set(EXPECTED_REVISIONS):
        missing = sorted(set(EXPECTED_REVISIONS).difference(runs))
        extra = sorted(set(runs).difference(EXPECTED_REVISIONS))
        raise ValueError(f"Expected all six models; missing={missing}, extra={extra}")

    ordered_models = [model for model in EXPECTED_REVISIONS if model in runs]
    primary_by_model = {
        model: {
            record["item_index"]: record
            for record in runs[model]
            if is_primary(record)
        }
        for model in ordered_models
    }
    item_sets = [set(records) for records in primary_by_model.values()]
    if any(item_set != item_sets[0] for item_set in item_sets[1:]):
        raise ValueError("Primary item sets differ across models")
    item_indices = sorted(item_sets[0])

    summaries = {model: model_summary(runs[model]) for model in ordered_models}
    per_model_effects = {
        model: [
            primary_by_model[model][item_index]["effects"][
                "orthography_effect_vs_unrelated"
            ]
            for item_index in item_indices
        ]
        for model in ordered_models
    }
    item_means = [
        statistics.mean(per_model_effects[model][position] for model in ordered_models)
        for position in range(len(item_indices))
    ]
    positive_counts = [
        sum(per_model_effects[model][position] > 0 for model in ordered_models)
        for position in range(len(item_indices))
    ]
    correlations = {
        left: {
            right: pearson(per_model_effects[left], per_model_effects[right])
            for right in ordered_models
        }
        for left in ordered_models
    }
    payload = {
        "analysis": "preregistered_fixed_model_set_orthography_replication_v1",
        "material_sha256": EXPECTED_MATERIAL_SHA256,
        "n_models": len(ordered_models),
        "n_primary_items": len(item_indices),
        "models": summaries,
        "fixed_model_set_average": bootstrap_mean(item_means, 7000),
        "model_mean_signs": {
            "positive": sum(
                block["orthography_effect"]["mean"] > 0
                for block in summaries.values()
            ),
            "negative": sum(
                block["orthography_effect"]["mean"] < 0
                for block in summaries.values()
            ),
            "ci_above_zero": sum(
                block["orthography_effect"]["bootstrap_mean_95ci"][0] > 0
                for block in summaries.values()
            ),
            "ci_below_zero": sum(
                block["orthography_effect"]["bootstrap_mean_95ci"][1] < 0
                for block in summaries.values()
            ),
        },
        "item_positive_model_count_distribution": {
            str(key): value for key, value in sorted(Counter(positive_counts).items())
        },
        "pairwise_item_effect_pearson": correlations,
        "inputs": input_metadata,
        "inference_guards": [
            "The cross-model interval averages within item before bootstrapping items.",
            "The six models are a fixed set, not a random sample from all language models.",
            "The continuous correct-vs-wrong1 margin is not four-choice accuracy.",
            "All models reuse the same source-only automatic controls without independent bilingual second review.",
        ],
    }
    output_json = args.output_json.resolve()
    output_report = args.output_report.resolve()
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_report.parent.mkdir(parents=True, exist_ok=True)
    with output_json.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    output_report.write_text(render_markdown(payload), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"json: {output_json}")
    print(f"report: {output_report}")


if __name__ == "__main__":
    main()
