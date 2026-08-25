#!/usr/bin/env python3
"""Compare two scoring runs item by item.

The main accuracy difference is paired because both models answer the same
questions.  An exact McNemar test therefore uses only the questions where one
model is correct and the other is wrong.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


METHODS = ("official", "candidate_only")


def load_jsonl(path: Path) -> dict[int, dict]:
    records: dict[int, dict] = {}
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            record = json.loads(line)
            item_index = int(record["item_index"])
            if item_index in records:
                raise ValueError(f"Duplicate item_index {item_index} in {path}")
            records[item_index] = record
    if not records:
        raise ValueError(f"No records in {path}")
    return records


def exact_mcnemar_p(baseline_only: int, comparison_only: int) -> float:
    """Two-sided exact binomial McNemar p-value."""

    discordant = baseline_only + comparison_only
    if discordant == 0:
        return 1.0
    tail = sum(
        math.comb(discordant, k) for k in range(min(baseline_only, comparison_only) + 1)
    ) / (2**discordant)
    return min(1.0, 2 * tail)


def compare_subset(
    baseline: dict[int, dict],
    comparison: dict[int, dict],
    indices: list[int],
) -> dict:
    result: dict[str, object] = {"items": len(indices), "methods": {}}
    for method in METHODS:
        both_correct: list[int] = []
        baseline_only: list[int] = []
        comparison_only: list[int] = []
        both_wrong: list[int] = []
        same_choice = 0

        for index in indices:
            left = baseline[index][method]
            right = comparison[index][method]
            left_correct = bool(left["correct"])
            right_correct = bool(right["correct"])
            same_choice += left["choice"] == right["choice"]
            if left_correct and right_correct:
                both_correct.append(index)
            elif left_correct:
                baseline_only.append(index)
            elif right_correct:
                comparison_only.append(index)
            else:
                both_wrong.append(index)

        baseline_correct = len(both_correct) + len(baseline_only)
        comparison_correct = len(both_correct) + len(comparison_only)
        result["methods"][method] = {
            "baseline_correct": baseline_correct,
            "baseline_accuracy": baseline_correct / len(indices),
            "comparison_correct": comparison_correct,
            "comparison_accuracy": comparison_correct / len(indices),
            "accuracy_difference": (
                comparison_correct - baseline_correct
            ) / len(indices),
            "both_correct": len(both_correct),
            "baseline_only_correct": len(baseline_only),
            "comparison_only_correct": len(comparison_only),
            "both_wrong": len(both_wrong),
            "net_additional_correct": len(comparison_only) - len(baseline_only),
            "mcnemar_exact_p": exact_mcnemar_p(
                len(baseline_only), len(comparison_only)
            ),
            "same_choice": same_choice,
            "same_choice_rate": same_choice / len(indices),
            "baseline_only_items": [
                {"item_index": index, "word": baseline[index]["word"]}
                for index in baseline_only
            ],
            "comparison_only_items": [
                {"item_index": index, "word": comparison[index]["word"]}
                for index in comparison_only
            ],
        }
    return result


def print_subset(label: str, result: dict) -> None:
    print(f"\n=== {label}: {result['items']} paired items ===")
    for method in METHODS:
        metrics = result["methods"][method]
        print(f"\n{method}")
        print(
            "  baseline:   "
            f"{metrics['baseline_correct']}/{result['items']} = "
            f"{metrics['baseline_accuracy']:.1%}"
        )
        print(
            "  comparison: "
            f"{metrics['comparison_correct']}/{result['items']} = "
            f"{metrics['comparison_accuracy']:.1%}"
        )
        print(f"  difference: {metrics['accuracy_difference']:+.1%}")
        print(
            "  gained/lost: "
            f"{metrics['comparison_only_correct']}/"
            f"{metrics['baseline_only_correct']} "
            f"(net {metrics['net_additional_correct']:+d} correct)"
        )
        print(f"  exact McNemar p: {metrics['mcnemar_exact_p']:.3g}")
        print(
            "  identical option choices: "
            f"{metrics['same_choice']}/{result['items']} = "
            f"{metrics['same_choice_rate']:.1%}"
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("baseline", type=Path)
    parser.add_argument("comparison", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    baseline = load_jsonl(args.baseline)
    comparison = load_jsonl(args.comparison)
    if set(baseline) != set(comparison):
        raise ValueError("Runs do not contain the same item indices")
    for index in baseline:
        if baseline[index]["word"] != comparison[index]["word"]:
            raise ValueError(f"Word mismatch at item_index {index}")

    strict_indices = sorted(baseline)
    audited_indices = [
        index
        for index in strict_indices
        if not baseline[index]["duplicate_options"]
        and not comparison[index]["duplicate_options"]
    ]
    report = {
        "baseline": str(args.baseline),
        "comparison": str(args.comparison),
        "strict": compare_subset(baseline, comparison, strict_indices),
        "audited": compare_subset(baseline, comparison, audited_indices),
    }

    print_subset("strict", report["strict"])
    print_subset("audited", report["audited"])
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"\nreport saved to: {args.output.resolve()}")


if __name__ == "__main__":
    main()
