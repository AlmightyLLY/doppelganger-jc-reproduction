#!/usr/bin/env python3
"""Create a reproducible, blinded worksheet for translation error review."""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RESULTS = (
    PROJECT_ROOT
    / "results"
    / "pilots"
    / "Qwen--Qwen2.5-0.5B-Instruct-jp_zh-homographs-sv2-start0-limit462.jsonl"
)
DEFAULT_WORKSHEET = (
    PROJECT_ROOT / "results" / "reviews" / "qwen2.5-0.5b-blind-review.md"
)
DEFAULT_KEY = (
    PROJECT_ROOT / "results" / "reviews" / "qwen2.5-0.5b-blind-review-key.json"
)
SEED = 20260823

# Four official-only wins, four candidate-only wins, and four cases where both
# methods are wrong but disagree. Each group contains exact and variant forms.
SELECTED_INDICES = (23, 100, 105, 193, 31, 41, 132, 180, 22, 25, 147, 171)
LETTERS = "ABCD"


def load_records(path: Path) -> dict[int, dict]:
    records: dict[int, dict] = {}
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                record = json.loads(line)
                records[int(record["item_index"])] = record
    return records


def category(record: dict) -> str:
    official_correct = bool(record["official"]["correct"])
    candidate_correct = bool(record["candidate_only"]["correct"])
    if official_correct and not candidate_correct:
        return "official_only_correct"
    if candidate_correct and not official_correct:
        return "candidate_only_correct"
    if not official_correct and not candidate_correct:
        return "both_wrong"
    return "both_correct"


def build_review(records: dict[int, dict]) -> tuple[list[str], list[dict]]:
    rng = random.Random(SEED)
    selected = [records[index] for index in SELECTED_INDICES]
    rng.shuffle(selected)

    worksheet = [
        "# Doppelganger-JC 盲测人工复核",
        "",
        "只根据日语原句，选择语义最准确、中文最自然的一个译文。",
        "不要查看 PPL、模型选择或答案文件。如果两个选项都能接受，仍请选择更准确自然的一个，并在答案后加 `?` 说明你不确定。",
        "",
        "请按 `1B, 2D, 3A ...` 的格式提交答案；有疑问时可补一句理由。",
        "",
    ]
    answer_key: list[dict] = []

    for review_id, record in enumerate(selected, start=1):
        option_order = list(range(4))
        rng.shuffle(option_order)
        original_to_letter = {
            original_index: LETTERS[display_index]
            for display_index, original_index in enumerate(option_order)
        }

        worksheet.extend(
            [
                f"## {review_id}",
                "",
                f"日语：{record['original']}",
                "",
            ]
        )
        for display_index, original_index in enumerate(option_order):
            worksheet.append(
                f"- {LETTERS[display_index]}. {record['candidates'][original_index]}"
            )
        worksheet.extend(["", "你的选择：____", ""])

        answer_key.append(
            {
                "review_id": review_id,
                "item_index": record["item_index"],
                "japanese_word": record["japanese_word"],
                "chinese_word": record["word"],
                "surface_exact": record["surface_exact"],
                "category": category(record),
                "correct_letter": original_to_letter[0],
                "official_letter": original_to_letter[record["official"]["choice"]],
                "candidate_only_letter": original_to_letter[
                    record["candidate_only"]["choice"]
                ],
                "option_order": option_order,
                "official_ppls": record["official"]["ppls"],
                "candidate_only_ppls": record["candidate_only"]["ppls"],
                "candidate_token_counts": record["candidate_token_counts"],
            }
        )

    return worksheet, answer_key


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", type=Path, default=DEFAULT_RESULTS)
    parser.add_argument("--worksheet", type=Path, default=DEFAULT_WORKSHEET)
    parser.add_argument("--key", type=Path, default=DEFAULT_KEY)
    args = parser.parse_args()

    records = load_records(args.results)
    missing = [index for index in SELECTED_INDICES if index not in records]
    if missing:
        raise RuntimeError(f"Selected result indices are missing: {missing}")

    worksheet, answer_key = build_review(records)
    args.worksheet.parent.mkdir(parents=True, exist_ok=True)
    args.key.parent.mkdir(parents=True, exist_ok=True)
    args.worksheet.write_text("\n".join(worksheet) + "\n", encoding="utf-8")
    args.key.write_text(
        json.dumps(
            {
                "seed": SEED,
                "source": str(args.results),
                "items": answer_key,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    counts: dict[str, int] = {}
    for item in answer_key:
        counts[item["category"]] = counts.get(item["category"], 0) + 1
    print(f"worksheet: {args.worksheet}")
    print(f"answer key: {args.key}")
    print(f"items:      {len(answer_key)}")
    print(f"categories: {counts}")


if __name__ == "__main__":
    main()
