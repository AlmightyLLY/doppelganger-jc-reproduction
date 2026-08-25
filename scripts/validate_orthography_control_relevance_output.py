#!/usr/bin/env python3
"""Validate four-condition orthography control-relevance output invariants."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any


FIELDS = ("correct", "wrong1", "wrong2", "wrong3")
CONDITIONS = (
    "original",
    "target_kana",
    "unrelated_control_kana",
    "related_semantic_cue_kana",
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--expected-items", type=int, default=30)
    parser.add_argument("--expected-revision", required=True)
    args = parser.parse_args()

    output_path = args.output.resolve()
    records = load_jsonl(output_path)
    if len(records) != args.expected_items:
        raise ValueError(f"Expected {args.expected_items} records, found {len(records)}")
    if len({record["item_index"] for record in records}) != len(records):
        raise ValueError("Duplicate item_index")
    material_hashes = {record["material_sha256"] for record in records}
    if len(material_hashes) != 1:
        raise ValueError("Multiple material hashes")

    for record in records:
        item_index = record["item_index"]
        if record["requested_revision"] != args.expected_revision:
            raise ValueError(f"item {item_index}: requested revision mismatch")
        resolved = record["resolved_revision"]
        if resolved is not None and resolved != args.expected_revision:
            raise ValueError(f"item {item_index}: resolved revision mismatch")
        if len(record["candidates"]) != 4 or len(set(record["candidates"])) != 4:
            raise ValueError(f"item {item_index}: invalid candidates")
        if set(record["conditions"]) != set(CONDITIONS):
            raise ValueError(f"item {item_index}: condition mismatch")
        if set(record["margins"]) != set(CONDITIONS):
            raise ValueError(f"item {item_index}: margin condition mismatch")

        margins: dict[str, float] = {}
        for condition in CONDITIONS:
            packed = record["conditions"][condition]
            for score_type in ("official", "candidate_only"):
                scores = packed[score_type]
                losses = scores["losses"]
                ppls = scores["ppls"]
                if len(losses) != 4 or len(ppls) != 4:
                    raise ValueError(f"item {item_index}: score length mismatch")
                if not all(math.isfinite(value) for value in losses + ppls):
                    raise ValueError(f"item {item_index}: non-finite score")
                expected_choice = min(range(4), key=losses.__getitem__)
                if scores["choice"] != expected_choice:
                    raise ValueError(f"item {item_index}: argmin mismatch")
                if scores["choice_field"] != FIELDS[expected_choice]:
                    raise ValueError(f"item {item_index}: choice field mismatch")
                if scores["correct"] != (expected_choice == 0):
                    raise ValueError(f"item {item_index}: correct flag mismatch")
                for loss, ppl in zip(losses, ppls):
                    if not close(math.exp(loss), ppl):
                        raise ValueError(f"item {item_index}: PPL mismatch")

            losses = packed["candidate_only"]["losses"]
            expected_margin = losses[1] - losses[0]
            margin = packed["candidate_only"][
                "shortcut_margin_wrong1_minus_correct"
            ]
            if not close(expected_margin, margin):
                raise ValueError(f"item {item_index}: margin mismatch")
            if not close(record["margins"][condition], margin):
                raise ValueError(f"item {item_index}: stored margin mismatch")
            margins[condition] = margin

        target = margins["target_kana"] - margins["original"]
        unrelated = margins["unrelated_control_kana"] - margins["original"]
        related = margins["related_semantic_cue_kana"] - margins["original"]
        expected_effects = {
            "target_effect": target,
            "unrelated_control_effect": unrelated,
            "related_semantic_cue_effect": related,
            "orthography_effect_vs_unrelated": target - unrelated,
            "orthography_effect_vs_related": target - related,
            "related_minus_unrelated_control_effect": related - unrelated,
        }
        if set(record["effects"]) != set(expected_effects):
            raise ValueError(f"item {item_index}: effect keys mismatch")
        for key, expected in expected_effects.items():
            if not close(record["effects"][key], expected):
                raise ValueError(f"item {item_index}: {key} mismatch")

    summary_path = output_path.with_suffix(".summary.json")
    with summary_path.open(encoding="utf-8") as handle:
        summary = json.load(handle)
    if summary["n_items"] != len(records):
        raise ValueError("Summary item count mismatch")
    if summary["material_sha256"] not in material_hashes:
        raise ValueError("Summary material hash mismatch")
    if summary["requested_revision"] != args.expected_revision:
        raise ValueError("Summary requested revision mismatch")
    if "no_independent_bilingual_second_review" not in summary["inference_status"]:
        raise ValueError("Missing inference guard")

    print(
        f"VALID: {len(records)} items, four conditions, revision, PPL, argmin, "
        "margins, effects, and summary invariants verified"
    )
    print(f"material_sha256: {next(iter(material_hashes))}")
    print(f"results_sha256: {sha256(output_path)}")
    print(f"summary_sha256: {sha256(summary_path)}")


if __name__ == "__main__":
    main()
