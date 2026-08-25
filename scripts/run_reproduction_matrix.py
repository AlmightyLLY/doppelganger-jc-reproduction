#!/usr/bin/env python3
"""Print or execute the frozen six-model reproduction matrix."""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG = PROJECT_ROOT / "configs" / "reproduction_models.json"


def display(command: list[str]) -> None:
    print(" ".join(shlex.quote(part) for part in command), flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("translation", "orthography"), required=True)
    parser.add_argument(
        "--direction",
        choices=("jp_zh", "zh_jp", "both"),
        default="both",
        help="Used by the translation phase.",
    )
    parser.add_argument(
        "--model-slug",
        action="append",
        help="Run only the named config slug; repeat to select multiple models.",
    )
    parser.add_argument("--device", choices=("auto", "cpu", "mps", "cuda"), default="cuda")
    parser.add_argument("--output-dir", type=Path, default=PROJECT_ROOT / "results" / "local")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually run inference. Without this flag, only print the exact commands.",
    )
    args = parser.parse_args()

    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    models = config["models"]
    if args.model_slug:
        requested = set(args.model_slug)
        models = [model for model in models if model["slug"] in requested]
        missing = requested.difference(model["slug"] for model in models)
        if missing:
            parser.error(f"unknown model slug(s): {', '.join(sorted(missing))}")

    commands: list[list[str]] = []
    if args.phase == "translation":
        directions = ("jp_zh", "zh_jp") if args.direction == "both" else (args.direction,)
        for model in models:
            for direction in directions:
                item_count = config["translation"][f"{direction}_items"]
                output = (
                    args.output_dir
                    / "translation"
                    / (
                        f"{model['slug']}-{direction}-homographs-sv2-"
                        f"start0-limit{item_count}.jsonl"
                    )
                )
                commands.append(
                    [
                        sys.executable,
                        "scripts/run_translation_subset.py",
                        "--model",
                        model["model"],
                        "--revision",
                        model["revision"],
                        "--direction",
                        direction,
                        "--start",
                        "0",
                        "--limit",
                        str(item_count),
                        "--device",
                        args.device,
                        "--output",
                        str(output),
                    ]
                )
    else:
        material = (
            PROJECT_ROOT
            / "results"
            / "local"
            / "materials"
            / "orthography-control-relevance-full-v1.jsonl"
        )
        for model in models:
            output = (
                args.output_dir
                / "orthography"
                / f"{model['slug']}-orthography-control-relevance-full-v1.jsonl"
            )
            commands.append(
                [
                    sys.executable,
                    "scripts/run_orthography_control_relevance_full.py",
                    "--material",
                    str(material),
                    "--output",
                    str(output),
                    "--model",
                    model["model"],
                    "--revision",
                    model["revision"],
                    "--device",
                    args.device,
                ]
            )

    print(f"phase: {args.phase}; models: {len(models)}; commands: {len(commands)}")
    if not args.execute:
        print("DRY RUN: add --execute to start model inference.\n")
    for command in commands:
        display(command)
        if args.execute:
            subprocess.run(command, cwd=PROJECT_ROOT, check=True)


if __name__ == "__main__":
    main()
