#!/usr/bin/env python3
"""Compare the six completed paper checkpoints across both translation directions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


PAPER_RESULTS = {
    "Qwen/Qwen2.5-7B-Instruct-1M": {"jp_zh": 0.6970, "zh_jp": 0.6418},
    "llm-jp/llm-jp-3-7.2b-instruct3": {"jp_zh": 0.5823, "zh_jp": 0.6549},
    "elyza/Llama-3-ELYZA-JP-8B": {"jp_zh": 0.5281, "zh_jp": 0.6044},
    "baichuan-inc/Baichuan2-7B-Base": {"jp_zh": 0.6169, "zh_jp": 0.5890},
    "google/gemma-7b": {"jp_zh": 0.6104, "zh_jp": 0.6000},
    "mistralai/Mistral-7B-Instruct-v0.2": {"jp_zh": 0.4978, "zh_jp": 0.4132},
}


def load_summaries(results_root: Path) -> dict[tuple[str, str], dict]:
    selected: dict[tuple[str, str], dict] = {}
    for path in (results_root / "pilots").glob("*.summary.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        model = data.get("model")
        direction = data.get("direction")
        if direction is None:
            dataset = data.get("dataset", "")
            direction = "jp_zh" if "jp_zh" in dataset else None
        if model not in PAPER_RESULTS or direction not in ("jp_zh", "zh_jp"):
            continue
        expected_items = 462 if direction == "jp_zh" else 455
        if data.get("strict", {}).get("items") != expected_items:
            continue
        key = (model, direction)
        if key in selected:
            raise ValueError(f"Multiple complete summaries for {key}")
        selected[key] = data
    return selected


def direction_aggregate(summaries: dict, direction: str) -> dict:
    rows = [summaries[(model, direction)] for model in PAPER_RESULTS]
    items = sum(row["strict"]["items"] for row in rows)
    official_correct = sum(row["strict"]["official"]["correct"] for row in rows)
    candidate_correct = sum(
        row["strict"]["candidate_only"]["correct"] for row in rows
    )
    official_errors = items - official_correct
    wrong1 = sum(
        row["strict"]["official"]["wrong1_selections"] for row in rows
    )
    return {
        "predictions": items,
        "official_correct": official_correct,
        "official_accuracy": official_correct / items,
        "candidate_only_correct": candidate_correct,
        "candidate_only_accuracy": candidate_correct / items,
        "official_minus_candidate_only": (official_correct - candidate_correct) / items,
        "wrong1_selections": wrong1,
        "wrong1_share_among_errors": wrong1 / official_errors,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-root", type=Path, default=Path("results"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    summaries = load_summaries(args.results_root)
    missing = [
        (model, direction)
        for model in PAPER_RESULTS
        for direction in ("jp_zh", "zh_jp")
        if (model, direction) not in summaries
    ]
    if missing:
        raise ValueError(f"Missing complete runs: {missing}")

    models = []
    for model, paper in PAPER_RESULTS.items():
        row = {"model": model, "directions": {}}
        for direction in ("jp_zh", "zh_jp"):
            summary = summaries[(model, direction)]["strict"]
            reproduced = summary["official"]["accuracy"]
            row["directions"][direction] = {
                "items": summary["items"],
                "paper_accuracy": paper[direction],
                "reproduced_official_accuracy": reproduced,
                "paper_difference": reproduced - paper[direction],
                "candidate_only_accuracy": summary["candidate_only"]["accuracy"],
                "wrong1_share_among_official_errors": summary["official"][
                    "wrong1_share_among_errors"
                ],
            }
        row["reproduced_zh_jp_minus_jp_zh"] = (
            row["directions"]["zh_jp"]["reproduced_official_accuracy"]
            - row["directions"]["jp_zh"]["reproduced_official_accuracy"]
        )
        row["paper_zh_jp_minus_jp_zh"] = paper["zh_jp"] - paper["jp_zh"]
        models.append(row)

    output = {
        "models": models,
        "aggregate": {
            direction: direction_aggregate(summaries, direction)
            for direction in ("jp_zh", "zh_jp")
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
