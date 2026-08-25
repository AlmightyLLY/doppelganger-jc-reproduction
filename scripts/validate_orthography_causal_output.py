#!/usr/bin/env python3
"""Validate numerical and provenance invariants of orthography smoke output."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


FIELDS = ("correct", "wrong1", "wrong2", "wrong3")
CONDITIONS = ("original", "target_kana", "control_kana")


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def close(left: float, right: float) -> bool:
    return math.isclose(left, right, rel_tol=1e-9, abs_tol=1e-9)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--expected-items", type=int, default=5)
    parser.add_argument("--expected-revision", required=True)
    args = parser.parse_args()

    records = load_jsonl(args.output)
    if len(records) != args.expected_items:
        raise ValueError(f"Expected {args.expected_items} records, found {len(records)}")
    if len({record["item_index"] for record in records}) != len(records):
        raise ValueError("Duplicate item_index in result")

    material_hashes = {record["material_sha256"] for record in records}
    if len(material_hashes) != 1:
        raise ValueError("Multiple material hashes in result")

    for record in records:
        if record["requested_revision"] != args.expected_revision:
            raise ValueError(f"item {record['item_index']}: requested revision mismatch")
        resolved = record["resolved_revision"]
        if resolved is not None and resolved != args.expected_revision:
            raise ValueError(f"item {record['item_index']}: resolved revision mismatch")
        if len(record["candidates"]) != 4 or len(set(record["candidates"])) != 4:
            raise ValueError(f"item {record['item_index']}: invalid candidates")

        margins: dict[str, float] = {}
        for condition in CONDITIONS:
            packed = record["conditions"][condition]
            for score_type in ("official", "candidate_only"):
                scores = packed[score_type]
                losses = scores["losses"]
                ppls = scores["ppls"]
                if len(losses) != 4 or len(ppls) != 4:
                    raise ValueError(f"item {record['item_index']}: score length mismatch")
                if not all(math.isfinite(value) for value in losses + ppls):
                    raise ValueError(f"item {record['item_index']}: non-finite score")
                expected_choice = min(range(4), key=losses.__getitem__)
                if scores["choice"] != expected_choice:
                    raise ValueError(f"item {record['item_index']}: argmin mismatch")
                if scores["choice_field"] != FIELDS[expected_choice]:
                    raise ValueError(f"item {record['item_index']}: choice field mismatch")
                if scores["correct"] != (expected_choice == 0):
                    raise ValueError(f"item {record['item_index']}: correct flag mismatch")
                for loss, ppl in zip(losses, ppls):
                    if not close(math.exp(loss), ppl):
                        raise ValueError(f"item {record['item_index']}: PPL mismatch")

            losses = packed["candidate_only"]["losses"]
            expected_margin = losses[1] - losses[0]
            margin = packed["candidate_only"][
                "shortcut_margin_wrong1_minus_correct"
            ]
            if not close(expected_margin, margin):
                raise ValueError(f"item {record['item_index']}: margin mismatch")
            margins[condition] = margin

        expected_target = margins["target_kana"] - margins["original"]
        expected_control = margins["control_kana"] - margins["original"]
        expected_orthography = expected_target - expected_control
        effects = record["effects"]
        for key, expected in (
            ("target_effect", expected_target),
            ("control_effect", expected_control),
            ("orthography_effect", expected_orthography),
        ):
            if not close(effects[key], expected):
                raise ValueError(f"item {record['item_index']}: {key} mismatch")

    summary_path = args.output.with_suffix(".summary.json")
    with summary_path.open(encoding="utf-8") as handle:
        summary = json.load(handle)
    if summary["n_items"] != len(records):
        raise ValueError("Summary item count mismatch")
    if summary["material_sha256"] not in material_hashes:
        raise ValueError("Summary material hash mismatch")
    if summary["inference_status"] != "none_engineering_smoke_n5":
        raise ValueError("Missing engineering-smoke inference guard")
    print(f"VALID: {len(records)} items, revision and numerical invariants verified")
    print(f"material_sha256: {next(iter(material_hashes))}")


if __name__ == "__main__":
    main()
