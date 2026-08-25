#!/usr/bin/env python3
"""Audit either direction of the Type-1 translation dataset."""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from questions.jp_zh.homographs import dataset as JP_ZH_DATASET
from questions.zh_jp.homographs import dataset as ZH_JP_DATASET


FIELDS = ("correct", "wrong1", "wrong2", "wrong3")

CONFIG = {
    "jp_zh": (
        "Japanese-to-Chinese",
        JP_ZH_DATASET,
        PROJECT_ROOT / "cognate_fixed" / "jp" / "homographs.txt",
    ),
    "zh_jp": (
        "Chinese-to-Japanese",
        ZH_JP_DATASET,
        PROJECT_ROOT / "cognate_fixed" / "zh" / "homographs.txt",
    ),
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--direction", choices=tuple(CONFIG), default="jp_zh")
    args = parser.parse_args()
    label, dataset, cognate_path = CONFIG[args.direction]

    cognate_rows: list[tuple[str, str]] = []
    with cognate_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            parts = line.rstrip("\n").split("|")
            if args.direction == "jp_zh":
                japanese, chinese = parts[0], parts[1]
            else:
                chinese, japanese = parts[0], parts[1]
            cognate_rows.append((japanese, chinese))

    question_words = [
        chinese if args.direction == "jp_zh" else japanese
        for japanese, chinese in cognate_rows
    ]
    word_counts = Counter(question_words)
    duplicate_words = [
        (word, count) for word, count in word_counts.items() if count > 1
    ]
    missing_questions = [
        (japanese, chinese)
        for japanese, chinese in cognate_rows
        if (chinese if args.direction == "jp_zh" else japanese) not in dataset
    ]
    extra_questions = [word for word in dataset if word not in word_counts]

    missing_fields = []
    duplicate_options = []
    for item_index, (word, item) in enumerate(dataset.items()):
        absent = [field for field in FIELDS if field not in item]
        if absent:
            missing_fields.append((item_index, word, absent))
            continue
        values = [item[field] for field in FIELDS]
        if len(set(values)) != len(values):
            duplicate_options.append(
                (
                    item_index,
                    word,
                    [(field, item[field]) for field in FIELDS],
                )
            )

    print(f"=== {label} Type-1 dataset audit ===")
    print(f"cognate rows:                  {len(cognate_rows)}")
    print(f"translation questions:         {len(dataset)}")
    print(f"duplicate cognate word keys:   {len(duplicate_words)}")
    print(f"missing translation questions: {len(missing_questions)}")
    print(f"extra translation questions:   {len(extra_questions)}")
    print(f"questions missing fields:      {len(missing_fields)}")
    print(f"questions with duplicate options: {len(duplicate_options)}")

    if missing_questions:
        print("\nMissing questions (Japanese, Chinese):")
        for row in missing_questions:
            print(f"  {row}")

    if duplicate_options:
        print("\nDuplicate candidate options:")
        for item_index, word, options in duplicate_options:
            print(f"  item_index={item_index}, word={word}")
            for field, value in options:
                print(f"    {field:<7} {value}")

    has_integrity_issues = bool(
        duplicate_words
        or missing_questions
        or extra_questions
        or missing_fields
        or duplicate_options
    )
    print(
        "\nAudit status: "
        + ("ISSUES FOUND (do not silently modify them)" if has_integrity_issues else "OK")
    )
    return int(has_integrity_issues)


if __name__ == "__main__":
    raise SystemExit(main())
