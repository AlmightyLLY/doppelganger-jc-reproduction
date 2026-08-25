#!/usr/bin/env python3
"""Fail when published result artifacts contain benchmark/intervention text."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS = PROJECT_ROOT / "results"
FORBIDDEN_TOP_LEVEL = {
    "word",
    "japanese_word",
    "chinese_word",
    "original",
    "candidates",
    "source_sentences",
    "target_intervention_span",
    "control_spans",
}
FORBIDDEN_FILES = (
    RESULTS / "causal" / "orthography-control-relevance-full-v1.jsonl",
    RESULTS / "causal" / "orthography-control-relevance-full-v1.excluded.jsonl",
    RESULTS / "EXP-20260824-three-model-common-errors-n67.csv",
    RESULTS / "EXP-20260825-orthography-transition-review-n30.blind.csv",
    RESULTS / "EXP-20260825-orthography-transition-review-n30.blind.md",
    RESULTS / "EXP-20260825-orthography-transition-review-n30.key.md",
    PROJECT_ROOT / "scripts" / "draft_orthography_confirmatory_materials.py",
    PROJECT_ROOT / "scripts" / "prepare_orthography_control_relevance_materials.py",
    PROJECT_ROOT / "scripts" / "prepare_orthography_dual_control_v3.py",
    PROJECT_ROOT / "scripts" / "prepare_orthography_negative_control_v4.py",
)


def walk(value: Any, path: tuple[str, ...] = ()) -> list[str]:
    problems: list[str] = []
    if isinstance(value, list):
        for index, item in enumerate(value):
            problems.extend(walk(item, (*path, str(index))))
    elif isinstance(value, dict):
        for key, item in value.items():
            if key in {
                "word",
                "japanese_word",
                "chinese_word",
                "candidates",
                "candidate_tokens",
            }:
                problems.append(".".join((*path, key)))
            elif key == "original" and isinstance(item, str):
                problems.append(".".join((*path, key)))
            else:
                problems.extend(walk(item, (*path, key)))
    return problems


def main() -> None:
    problems: list[str] = []
    for path in FORBIDDEN_FILES:
        if path.exists():
            problems.append(f"forbidden benchmark-bearing file: {path.relative_to(PROJECT_ROOT)}")

    jsonl_paths = [
        *sorted((RESULTS / "pilots").glob("*.jsonl")),
        *[
            path
            for path in sorted((RESULTS / "causal").glob("*.jsonl"))
            if not path.name.startswith("orthography-control-relevance-full-v1")
        ],
    ]
    for path in jsonl_paths:
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            record = json.loads(line)
            forbidden = FORBIDDEN_TOP_LEVEL.intersection(record)
            if forbidden:
                problems.append(
                    f"{path.relative_to(PROJECT_ROOT)}:{line_number}: {sorted(forbidden)}"
                )
            for location in walk(record):
                problems.append(
                    f"{path.relative_to(PROJECT_ROOT)}:{line_number}: {location}"
                )
            if record.get("public_artifact_schema") != "scores_only_v1":
                problems.append(
                    f"{path.relative_to(PROJECT_ROOT)}:{line_number}: missing scores-only schema"
                )

    for path in [
        *sorted((RESULTS / "pilots").glob("*.summary.json")),
        *sorted((RESULTS / "causal").glob("*.summary.json")),
        *sorted((RESULTS / "analysis").glob("*.json")),
    ]:
        payload = json.loads(path.read_text(encoding="utf-8"))
        for location in walk(payload):
            problems.append(f"{path.relative_to(PROJECT_ROOT)}: {location}")

    if problems:
        raise SystemExit("PUBLIC DATA AUDIT FAILED\n" + "\n".join(problems[:100]))
    print(f"VALID: {len(jsonl_paths)} scores-only JSONL artifacts contain no benchmark text")
    print("VALID: public summaries and analyses contain no benchmark text fields")
    print("VALID: frozen intervention material and bulk review packets are not distributed")


if __name__ == "__main__":
    main()
