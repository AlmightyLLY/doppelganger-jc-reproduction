#!/usr/bin/env python3
"""Summarize scoring-method diagnostics for one JSONL experiment run."""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path


METHODS = ("official", "candidate_only")


def load_records(path: Path) -> list[dict]:
    records: list[dict] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON at line {line_number}") from exc
    if not records:
        raise ValueError(f"No records in {path}")
    return records


def wilson_interval(correct: int, total: int, z: float = 1.96) -> tuple[float, float]:
    proportion = correct / total
    denominator = 1 + z**2 / total
    center = (proportion + z**2 / (2 * total)) / denominator
    half_width = (
        z
        * math.sqrt(
            proportion * (1 - proportion) / total + z**2 / (4 * total**2)
        )
        / denominator
    )
    return center - half_width, center + half_width


def method_summary(records: list[dict], method: str) -> dict:
    correct = sum(bool(record[method]["correct"]) for record in records)
    choices = Counter(int(record[method]["choice"]) for record in records)
    narrow_margins = 0
    for record in records:
        first, second, *_ = sorted(float(value) for value in record[method]["ppls"])
        if (second - first) / first < 0.05:
            narrow_margins += 1
    lower, upper = wilson_interval(correct, len(records))
    return {
        "correct": correct,
        "accuracy": correct / len(records),
        "wilson_95": [lower, upper],
        "choice_distribution": [choices[index] for index in range(4)],
        "wrong1_selections": choices[1],
        "wrong1_share_among_errors": choices[1] / (len(records) - correct),
        "ppl_margin_below_5_percent": narrow_margins,
    }


def build_report(path: Path, records: list[dict]) -> dict:
    both_correct = 0
    official_only = 0
    candidate_only_only = 0
    both_wrong = 0
    disagreements = 0
    official_longer = 0
    equal_length = 0
    official_shorter = 0

    for record in records:
        official = record["official"]
        candidate = record["candidate_only"]
        if official["correct"] and candidate["correct"]:
            both_correct += 1
        elif official["correct"]:
            official_only += 1
        elif candidate["correct"]:
            candidate_only_only += 1
        else:
            both_wrong += 1

        if official["choice"] == candidate["choice"]:
            continue
        disagreements += 1
        token_counts = record["candidate_token_counts"]
        official_count = token_counts[official["choice"]]
        candidate_count = token_counts[candidate["choice"]]
        if official_count > candidate_count:
            official_longer += 1
        elif official_count == candidate_count:
            equal_length += 1
        else:
            official_shorter += 1

    return {
        "input": str(path),
        "model": records[0]["model"],
        "model_revision": records[0].get("model_revision"),
        "items": len(records),
        "methods": {
            method: method_summary(records, method) for method in METHODS
        },
        "scoring_comparison": {
            "agreement": len(records) - disagreements,
            "agreement_rate": (len(records) - disagreements) / len(records),
            "disagreements": disagreements,
            "both_correct": both_correct,
            "official_only_correct": official_only,
            "candidate_only_only_correct": candidate_only_only,
            "both_wrong": both_wrong,
            "disagreement_token_direction": {
                "official_chose_longer": official_longer,
                "equal_length": equal_length,
                "official_chose_shorter": official_shorter,
            },
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    records = load_records(args.path)
    report = build_report(args.path, records)
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
