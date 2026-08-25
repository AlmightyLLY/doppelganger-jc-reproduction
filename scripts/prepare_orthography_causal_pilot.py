#!/usr/bin/env python3
"""Create a blinded, stratified annotation sheet for the kana intervention pilot."""

from __future__ import annotations

import argparse
import csv
import random
import sys
from collections import Counter
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from questions.jp_zh.homographs import dataset


FIELDS = ("correct", "wrong1", "wrong2", "wrong3")
COGNATE_PATH = PROJECT_ROOT / "cognate_fixed" / "jp" / "homographs.txt"
DEFAULT_SEED = 20260823
DEFAULT_SIZE = 30


def load_cognate_pairs() -> dict[str, str]:
    pairs: dict[str, str] = {}
    with COGNATE_PATH.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            japanese, chinese, *_ = line.rstrip("\n").split("|")
            if chinese in pairs:
                raise ValueError(f"Duplicate Chinese key: {chinese}")
            pairs[chinese] = japanese
    return pairs


def eligible_rows() -> tuple[list[dict], list[dict]]:
    pairs = load_cognate_pairs()
    eligible: list[dict] = []
    excluded: list[dict] = []

    for item_index, (word, item) in enumerate(dataset.items()):
        japanese_word = pairs[word]
        candidates = [item[field] for field in FIELDS]
        target_occurrences = item["target-sentence"].count(japanese_word)
        row = {
            "item_index": item_index,
            "word": word,
            "japanese_word": japanese_word,
            "surface_exact": japanese_word == word,
            "original": item["target-sentence"],
            "target_occurrences": target_occurrences,
        }
        reasons: list[str] = []
        if len(set(candidates)) != len(candidates):
            reasons.append("duplicate_options")
        if target_occurrences != 1:
            reasons.append(f"target_occurrences={target_occurrences}")
        if reasons:
            row["preselection_exclusion"] = ";".join(reasons)
            excluded.append(row)
        else:
            eligible.append(row)
    return eligible, excluded


def select_stratified(rows: list[dict], size: int, seed: int) -> list[dict]:
    if size <= 0 or size % 2:
        raise ValueError("--size must be a positive even number")
    per_stratum = size // 2
    rng = random.Random(seed)
    selected: list[dict] = []
    for surface_exact in (True, False):
        stratum = [row for row in rows if row["surface_exact"] is surface_exact]
        if len(stratum) < per_stratum:
            raise ValueError(
                f"Only {len(stratum)} eligible rows for surface_exact={surface_exact}"
            )
        selected.extend(rng.sample(stratum, per_stratum))
    return sorted(selected, key=lambda row: row["item_index"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--size", type=int, default=DEFAULT_SIZE)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing sheet. Never use after model outcomes are inspected.",
    )
    args = parser.parse_args()

    output = args.output or (
        PROJECT_ROOT
        / "results"
        / "causal"
        / f"orthography-pilot-seed{args.seed}-n{args.size}.csv"
    )
    output = output.resolve()
    exclusions_output = output.with_name(output.stem + ".preexcluded.csv")
    if output.exists() and not args.force:
        raise FileExistsError(f"Refusing to overwrite frozen sheet: {output}")

    eligible, excluded = eligible_rows()
    selected = select_stratified(eligible, args.size, args.seed)
    fieldnames = [
        "item_index",
        "word",
        "japanese_word",
        "surface_exact",
        "original",
        "target_occurrences",
        "target_reading",
        "target_kana_sentence",
        "control_word",
        "control_reading",
        "control_kana_sentence",
        "target_naturalness_1_5",
        "control_naturalness_1_5",
        "meaning_preserved_yes_no",
        "include_yes_no",
        "exclusion_reason",
        "annotator",
        "reviewer",
    ]
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in selected:
            writer.writerow(row)

    exclusion_fields = [
        "item_index",
        "word",
        "japanese_word",
        "surface_exact",
        "original",
        "target_occurrences",
        "preselection_exclusion",
    ]
    with exclusions_output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=exclusion_fields,
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(excluded)

    exact = sum(bool(row["surface_exact"]) for row in selected)
    print(f"eligible rows:       {len(eligible)}")
    print(f"pre-excluded rows:   {len(excluded)}")
    print(f"selected rows:       {len(selected)}")
    print(f"surface strata:      exact={exact}, variant={len(selected) - exact}")
    print(f"seed:                 {args.seed}")
    print(f"annotation sheet:     {output}")
    print(f"pre-exclusion sheet:  {exclusions_output}")
    reason_counts = Counter(
        reason
        for row in excluded
        for reason in row["preselection_exclusion"].split(";")
    )
    print(f"pre-exclusion reasons:{dict(reason_counts)}")
    print("Model outputs were not used for selection and are absent from the sheet.")


if __name__ == "__main__":
    main()
