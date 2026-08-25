#!/usr/bin/env python3
"""Aggregate aligned translation-scoring runs across several models."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from itertools import combinations
from pathlib import Path


def load(path: Path) -> list[dict]:
    records = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if not records:
        raise ValueError(f"No records in {path}")
    return records


def normalize_legacy_schema(path: Path, records: list[dict]) -> list[dict]:
    """Fill fields absent from the earliest scoring-version-2 JP→ZH runs.

    Those frozen files predate the explicit ``direction`` and ``chinese_word``
    fields. Their filename and dataset key make both values unambiguous: in a
    JP→ZH run, ``word`` is the Chinese question key.
    """
    filename = path.name
    if "-jp_zh-" in filename:
        inferred_direction = "jp_zh"
    elif "-zh_jp-" in filename:
        inferred_direction = "zh_jp"
    else:
        inferred_direction = records[0].get("direction")
    if inferred_direction not in {"jp_zh", "zh_jp"}:
        raise ValueError(f"Cannot infer translation direction from {path}")

    for record in records:
        observed = record.get("direction")
        if observed is not None and observed != inferred_direction:
            raise ValueError(f"Direction conflicts with filename in {path}")
        record.setdefault("direction", inferred_direction)
        if inferred_direction == "jp_zh" and "word" in record:
            record.setdefault("chinese_word", record["word"])
    return records


def model_summary(records: list[dict]) -> dict:
    total = len(records)
    official_correct = sum(r["official"]["correct"] for r in records)
    candidate_correct = sum(r["candidate_only"]["correct"] for r in records)
    agreements = sum(
        r["official"]["choice"] == r["candidate_only"]["choice"]
        for r in records
    )
    official_only = sum(
        r["official"]["correct"] and not r["candidate_only"]["correct"]
        for r in records
    )
    candidate_only_only = sum(
        r["candidate_only"]["correct"] and not r["official"]["correct"]
        for r in records
    )
    length_direction = Counter()
    for record in records:
        official_choice = record["official"]["choice"]
        candidate_choice = record["candidate_only"]["choice"]
        if official_choice == candidate_choice:
            continue
        counts = record["candidate_token_counts"]
        delta = counts[official_choice] - counts[candidate_choice]
        length_direction[
            "official_longer" if delta > 0 else "official_shorter" if delta < 0 else "equal"
        ] += 1

    official_errors = total - official_correct
    candidate_errors = total - candidate_correct
    exact = [r for r in records if r["surface_exact"] and not r["duplicate_options"]]
    variant = [r for r in records if not r["surface_exact"] and not r["duplicate_options"]]
    return {
        "model": records[0]["model"],
        "model_revision": records[0].get("model_revision"),
        "items": total,
        "official": {
            "correct": official_correct,
            "accuracy": official_correct / total,
            "wrong1_selections": sum(r["official"]["choice"] == 1 for r in records),
            "wrong1_share_among_errors": (
                sum(r["official"]["choice"] == 1 for r in records) / official_errors
            ),
        },
        "candidate_only": {
            "correct": candidate_correct,
            "accuracy": candidate_correct / total,
            "wrong1_selections": sum(
                r["candidate_only"]["choice"] == 1 for r in records
            ),
            "wrong1_share_among_errors": (
                sum(r["candidate_only"]["choice"] == 1 for r in records)
                / candidate_errors
            ),
        },
        "scoring_comparison": {
            "agreement": agreements,
            "agreement_rate": agreements / total,
            "official_only_correct": official_only,
            "candidate_only_only_correct": candidate_only_only,
            "length_direction": dict(length_direction),
        },
        "surface_form_audited": {
            "exact": {
                "items": len(exact),
                "correct": sum(r["official"]["correct"] for r in exact),
                "accuracy": sum(r["official"]["correct"] for r in exact) / len(exact),
            },
            "variant": {
                "items": len(variant),
                "correct": sum(r["official"]["correct"] for r in variant),
                "accuracy": sum(r["official"]["correct"] for r in variant) / len(variant),
            },
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    runs = [
        (path, normalize_legacy_schema(path, load(path)))
        for path in args.paths
    ]
    reference = runs[0][1]
    expected_indices = list(range(len(reference)))
    for path, records in runs:
        if [r["item_index"] for r in records] != expected_indices:
            raise ValueError(f"Unaligned item indices in {path}")
        for left, right in zip(reference, records):
            signature = ("direction", "surface_exact", "duplicate_options")
            if all(key in left and key in right for key in ("word", "original", "candidates")):
                signature += ("word", "original", "candidates")
            if any(left.get(key) != right.get(key) for key in signature):
                raise ValueError(f"Dataset content differs in {path} at item {left['item_index']}")

    model_names = [records[0]["model"] for _, records in runs]
    if len(model_names) != len(set(model_names)):
        raise ValueError("The same model appears more than once")

    correct_count_distribution = Counter()
    choice_unanimous = 0
    unanimous_wrong1 = 0
    common_errors = []
    single_model_correct = Counter()

    for item_index in expected_indices:
        item_records = [records[item_index] for _, records in runs]
        correct_models = [
            record["model"] for record in item_records if record["official"]["correct"]
        ]
        correct_count_distribution[len(correct_models)] += 1
        choices = [record["official"]["choice"] for record in item_records]
        if len(set(choices)) == 1:
            choice_unanimous += 1
            if choices[0] == 1:
                unanimous_wrong1 += 1
        if len(correct_models) == 1:
            single_model_correct[correct_models[0]] += 1
        if not correct_models:
            base = item_records[0]
            common_error = {
                "item_index": item_index,
                "surface_exact": base["surface_exact"],
                "duplicate_options": base["duplicate_options"],
                "official_choices": {
                    record["model"]: record["official"]["choice"]
                    for record in item_records
                },
                "candidate_only_choices": {
                    record["model"]: record["candidate_only"]["choice"]
                    for record in item_records
                },
            }
            # Local artifacts may include benchmark text; public scores-only
            # exports do not.  Never make text a requirement for aggregation.
            for key in (
                "word",
                "japanese_word",
                "chinese_word",
                "original",
                "candidates",
            ):
                if key in base:
                    common_error[key] = base[key]
            common_errors.append(common_error)

    pairwise = []
    for (left_name, left_records), (right_name, right_records) in combinations(
        [(records[0]["model"], records) for _, records in runs], 2
    ):
        same_choice = sum(
            left["official"]["choice"] == right["official"]["choice"]
            for left, right in zip(left_records, right_records)
        )
        left_only = sum(
            left["official"]["correct"] and not right["official"]["correct"]
            for left, right in zip(left_records, right_records)
        )
        right_only = sum(
            right["official"]["correct"] and not left["official"]["correct"]
            for left, right in zip(left_records, right_records)
        )
        pairwise.append(
            {
                "left": left_name,
                "right": right_name,
                "same_choice": same_choice,
                "same_choice_rate": same_choice / len(reference),
                "left_only_correct": left_only,
                "right_only_correct": right_only,
            }
        )

    summaries = [model_summary(records) for _, records in runs]
    total_predictions = len(reference) * len(runs)
    official_correct = sum(s["official"]["correct"] for s in summaries)
    candidate_correct = sum(s["candidate_only"]["correct"] for s in summaries)
    official_errors = total_predictions - official_correct
    output = {
        "direction": reference[0].get("direction"),
        "items": len(reference),
        "models": model_names,
        "model_summaries": summaries,
        "aggregate": {
            "predictions": total_predictions,
            "official_correct": official_correct,
            "official_accuracy": official_correct / total_predictions,
            "candidate_only_correct": candidate_correct,
            "candidate_only_accuracy": candidate_correct / total_predictions,
            "official_wrong1_selections": sum(
                s["official"]["wrong1_selections"] for s in summaries
            ),
            "official_wrong1_share_among_errors": sum(
                s["official"]["wrong1_selections"] for s in summaries
            )
            / official_errors,
            "choice_agreement": sum(
                s["scoring_comparison"]["agreement"] for s in summaries
            ),
            "official_only_correct": sum(
                s["scoring_comparison"]["official_only_correct"] for s in summaries
            ),
            "candidate_only_only_correct": sum(
                s["scoring_comparison"]["candidate_only_only_correct"] for s in summaries
            ),
            "length_direction": dict(
                sum(
                    (
                        Counter(s["scoring_comparison"]["length_direction"])
                        for s in summaries
                    ),
                    Counter(),
                )
            ),
        },
        "cross_model": {
            "correct_model_count_distribution": dict(
                sorted(correct_count_distribution.items())
            ),
            "all_models_correct": correct_count_distribution[len(runs)],
            "all_models_wrong": correct_count_distribution[0],
            "choice_unanimous": choice_unanimous,
            "unanimous_wrong1": unanimous_wrong1,
            "single_model_correct": dict(single_model_correct),
            "pairwise": pairwise,
            "common_error_items": common_errors,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(output["aggregate"], ensure_ascii=False, indent=2))
    print(json.dumps(output["cross_model"], ensure_ascii=False, indent=2)[:4000])
    print(f"saved: {args.output}")


if __name__ == "__main__":
    main()
