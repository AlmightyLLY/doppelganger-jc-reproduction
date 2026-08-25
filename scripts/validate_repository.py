#!/usr/bin/env python3
"""Validate every committed raw result with the experiment invariants."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG = PROJECT_ROOT / "configs" / "reproduction_models.json"
TRANSLATION_VALIDATOR = PROJECT_ROOT / "scripts" / "validate_run_output.py"
ORTHOGRAPHY_VALIDATOR = (
    PROJECT_ROOT / "scripts" / "validate_orthography_control_relevance_full_output.py"
)


def run(*args: object) -> None:
    command = [str(arg) for arg in args]
    print("+", " ".join(command))
    subprocess.run(command, cwd=PROJECT_ROOT, check=True)


def validate_translation_summary(path: Path, model: dict, expected_items: int) -> None:
    records = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    summary_path = path.with_suffix(".summary.json")
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    strict = summary["strict"]
    expected = {
        "items": len(records),
        "official_correct": sum(record["official"]["correct"] for record in records),
        "candidate_correct": sum(
            record["candidate_only"]["correct"] for record in records
        ),
        "official_wrong1": sum(
            record["official"]["choice"] == 1 for record in records
        ),
        "candidate_wrong1": sum(
            record["candidate_only"]["choice"] == 1 for record in records
        ),
        "agreement": sum(
            record["official"]["choice"] == record["candidate_only"]["choice"]
            for record in records
        ),
    }
    observed = {
        "items": strict["items"],
        "official_correct": strict["official"]["correct"],
        "candidate_correct": strict["candidate_only"]["correct"],
        "official_wrong1": strict["official"]["wrong1_selections"],
        "candidate_wrong1": strict["candidate_only"]["wrong1_selections"],
        "agreement": strict["agreement"]["count"],
    }
    if observed != expected:
        raise ValueError(f"Summary does not match raw records: {summary_path}")
    if expected["items"] != expected_items:
        raise ValueError(f"Unexpected record count in {summary_path}")
    if summary["model"] != model["model"]:
        raise ValueError(f"Model mismatch in {summary_path}")
    if summary["model_revision"] != model["revision"]:
        raise ValueError(f"Revision mismatch in {summary_path}")


def main() -> None:
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    translation = config["translation"]
    orthography = config["orthography"]

    checked = 0
    for model in config["models"]:
        for direction, item_key in (("jp_zh", "jp_zh_items"), ("zh_jp", "zh_jp_items")):
            item_count = translation[item_key]
            path = (
                PROJECT_ROOT
                / "results"
                / "pilots"
                / (
                    f"{model['slug']}-{direction}-homographs-sv2-"
                    f"start0-limit{item_count}.jsonl"
                )
            )
            run(
                sys.executable,
                TRANSLATION_VALIDATOR,
                path,
                "--expected-items",
                item_count,
            )
            validate_translation_summary(path, model, item_count)
            checked += 1

        causal_path = (
            PROJECT_ROOT
            / "results"
            / "causal"
            / f"{model['slug']}-orthography-control-relevance-full-v1.jsonl"
        )
        run(
            sys.executable,
            ORTHOGRAPHY_VALIDATOR,
            causal_path,
            "--expected-items",
            orthography["material_items"],
            "--expected-related",
            orthography["related_control_items"],
            "--expected-revision",
            model["revision"],
        )
        checked += 1

    print(f"VALID: {checked} committed model runs passed all structural checks")


if __name__ == "__main__":
    main()
