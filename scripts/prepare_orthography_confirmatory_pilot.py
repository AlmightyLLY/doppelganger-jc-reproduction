#!/usr/bin/env python3
"""Replace exposed engineering items and freeze a blind confirmatory pilot sheet."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
from collections import Counter
from pathlib import Path

from prepare_orthography_causal_pilot import eligible_rows


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ORIGINAL = (
    PROJECT_ROOT / "results" / "causal" / "orthography-pilot-seed20260823-n30.csv"
)
DEFAULT_DEVELOPMENT = (
    PROJECT_ROOT / "results" / "causal" / "orthography-engineering-smoke-n5.jsonl"
)
DEFAULT_OUTPUT = (
    PROJECT_ROOT
    / "results"
    / "causal"
    / "orthography-confirmatory-pilot-seed20260823-repl20260825-n30.csv"
)
DEFAULT_REPLACEMENT_SEED = 20260825


ANNOTATION_FIELDS = [
    "target_reading",
    "target_kana_sentence",
    "control_word",
    "control_reading",
    "control_kana_sentence",
    "target_naturalness_1_5",
    "control_naturalness_1_5",
    "meaning_preserved_yes_no",
    "target_homophone_risk_none_low_high",
    "target_context_disambiguates_yes_uncertain_no",
    "control_homophone_risk_none_low_high",
    "control_context_disambiguates_yes_uncertain_no",
    "target_control_ambiguity_match_yes_no",
    "include_yes_no",
    "exclusion_reason",
    "annotator",
    "reviewer",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_development_indices(path: Path) -> set[int]:
    indices: set[int] = set()
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                indices.add(int(json.loads(line)["item_index"]))
    return indices


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--original", type=Path, default=DEFAULT_ORIGINAL)
    parser.add_argument("--development", type=Path, default=DEFAULT_DEVELOPMENT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--replacement-seed", type=int, default=DEFAULT_REPLACEMENT_SEED
    )
    args = parser.parse_args()

    original_path = args.original.resolve()
    development_path = args.development.resolve()
    output_path = args.output.resolve()
    manifest_path = output_path.with_suffix(".manifest.json")
    if output_path.exists() or manifest_path.exists():
        raise FileExistsError(
            f"Refusing to overwrite frozen output: {output_path} or {manifest_path}"
        )

    original = read_csv(original_path)
    if len(original) != 30:
        raise ValueError(f"Expected 30 original rows, found {len(original)}")
    development_indices = read_development_indices(development_path)
    original_indices = {int(row["item_index"]) for row in original}
    if not development_indices <= original_indices:
        raise ValueError("Development indices are not a subset of the original pilot")

    retained = [
        row for row in original if int(row["item_index"]) not in development_indices
    ]
    retained_counts = Counter(row["surface_exact"] == "True" for row in retained)
    needed = {True: 15 - retained_counts[True], False: 15 - retained_counts[False]}
    if sum(needed.values()) != len(development_indices):
        raise ValueError(f"Replacement count mismatch: needed={needed}")

    eligible, _ = eligible_rows()
    pool = [row for row in eligible if row["item_index"] not in original_indices]
    rng = random.Random(args.replacement_seed)
    replacements: list[dict] = []
    for surface_exact in (True, False):
        stratum = [row for row in pool if row["surface_exact"] is surface_exact]
        replacements.extend(rng.sample(stratum, needed[surface_exact]))

    rows: list[dict[str, object]] = []
    for row in retained:
        base = {
            "item_index": int(row["item_index"]),
            "word": row["word"],
            "japanese_word": row["japanese_word"],
            "surface_exact": row["surface_exact"] == "True",
            "original": row["original"],
            "target_occurrences": int(row["target_occurrences"]),
            "selection_source": "retained_blind_from_seed20260823_n30",
        }
        rows.append(base)
    for row in replacements:
        base = dict(row)
        base["selection_source"] = "replacement_seed20260825"
        rows.append(base)
    rows.sort(key=lambda row: int(row["item_index"]))

    if len(rows) != 30:
        raise ValueError(f"Expected 30 final rows, found {len(rows)}")
    final_counts = Counter(bool(row["surface_exact"]) for row in rows)
    if final_counts != Counter({True: 15, False: 15}):
        raise ValueError(f"Unexpected final strata: {final_counts}")
    if {int(row["item_index"]) for row in rows} & development_indices:
        raise ValueError("Development items leaked into confirmatory sheet")

    fieldnames = [
        "item_index",
        "word",
        "japanese_word",
        "surface_exact",
        "original",
        "target_occurrences",
        "selection_source",
        *ANNOTATION_FIELDS,
    ]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    output_hash = sha256(output_path)
    manifest = {
        "status": "frozen_before_material_annotation_and_model_scoring",
        "original_pilot": str(original_path),
        "original_pilot_sha256": sha256(original_path),
        "development_items_file": str(development_path),
        "development_items_sha256": sha256(development_path),
        "excluded_development_item_indices": sorted(development_indices),
        "retained_item_count": len(retained),
        "replacement_seed": args.replacement_seed,
        "replacement_item_indices": sorted(
            int(row["item_index"]) for row in replacements
        ),
        "final_item_count": len(rows),
        "surface_exact_true": final_counts[True],
        "surface_exact_false": final_counts[False],
        "model_outputs_used_for_selection": False,
        "annotation_sheet": str(output_path),
        "annotation_sheet_sha256": output_hash,
    }
    with manifest_path.open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    print(f"retained blind rows: {len(retained)}")
    print(f"excluded dev rows:   {sorted(development_indices)}")
    print(f"replacement needs:   exact={needed[True]} variant={needed[False]}")
    print(f"replacement rows:    {manifest['replacement_item_indices']}")
    print(f"final strata:        exact={final_counts[True]} variant={final_counts[False]}")
    print(f"annotation sheet:    {output_path}")
    print(f"sheet sha256:        {output_hash}")
    print(f"manifest:            {manifest_path}")


if __name__ == "__main__":
    main()
