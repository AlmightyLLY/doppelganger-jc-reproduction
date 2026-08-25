#!/usr/bin/env python3
"""Validate structural and numerical invariants of a scoring JSONL run."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


METHODS = ("official", "candidate_only")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("--expected-items", type=int, required=True)
    args = parser.parse_args()

    records: list[dict] = []
    with args.path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON at line {line_number}") from exc

    if len(records) != args.expected_items:
        raise ValueError(
            f"Expected {args.expected_items} records, found {len(records)}"
        )
    indices = [int(record["item_index"]) for record in records]
    expected_indices = list(range(args.expected_items))
    if indices != expected_indices:
        raise ValueError("item_index values are not continuous and ordered")

    models = {record["model"] for record in records}
    revisions = {record.get("model_revision") for record in records}
    scoring_versions = {record.get("scoring_version") for record in records}
    if len(models) != 1 or len(revisions) != 1 or len(scoring_versions) != 1:
        raise ValueError("Model, revision, or scoring version changed within the run")
    if None in revisions:
        raise ValueError("Model revision is missing")

    for record in records:
        # Public artifacts intentionally omit benchmark text.  A private/local
        # run may still contain the four candidate strings, while a public
        # scores-only export proves arity through token counts and score arrays.
        if "candidates" in record and len(record["candidates"]) != 4:
            raise ValueError(f"Item {record['item_index']} does not have four candidates")
        if len(record.get("candidate_token_counts", [])) != 4:
            raise ValueError(
                f"Item {record['item_index']} does not have four candidate token counts"
            )
        for method in METHODS:
            result = record[method]
            losses = result["losses"]
            ppls = result["ppls"]
            if len(losses) != 4 or len(ppls) != 4:
                raise ValueError(
                    f"Item {record['item_index']} {method} does not have four scores"
                )
            if not all(math.isfinite(value) for value in losses + ppls):
                raise ValueError(
                    f"Item {record['item_index']} {method} contains NaN or Inf"
                )
            if not all(value > 0 for value in ppls):
                raise ValueError(
                    f"Item {record['item_index']} {method} has non-positive PPL"
                )
            expected_choice = min(range(4), key=ppls.__getitem__)
            if result["choice"] != expected_choice:
                raise ValueError(
                    f"Item {record['item_index']} {method} choice is not argmin(PPL)"
                )
            if bool(result["correct"]) != (expected_choice == 0):
                raise ValueError(
                    f"Item {record['item_index']} {method} correct flag is inconsistent"
                )

    print("VALID")
    print(f"items:            {len(records)}")
    print(f"model:            {next(iter(models))}")
    print(f"model revision:   {next(iter(revisions))}")
    print(f"scoring version:  {next(iter(scoring_versions))}")
    print(f"indices:          continuous 0..{args.expected_items - 1}")
    print("scores:           finite; four losses and PPLs per method")
    print("choices:          all equal argmin(PPL)")


if __name__ == "__main__":
    main()
