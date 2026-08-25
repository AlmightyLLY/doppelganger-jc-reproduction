#!/usr/bin/env python3
"""Create a human-review packet for official errors shared by three models."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUNS = {
    "Qwen-1M": PROJECT_ROOT
    / "results/pilots/Qwen--Qwen2.5-7B-Instruct-1M-jp_zh-homographs-sv2-start0-limit462.jsonl",
    "llm-jp": PROJECT_ROOT
    / "results/pilots/llm-jp--llm-jp-3-7.2b-instruct3-jp_zh-homographs-sv2-start0-limit462.jsonl",
    "ELYZA": PROJECT_ROOT
    / "results/pilots/elyza--Llama-3-ELYZA-JP-8B-jp_zh-homographs-sv2-start0-limit462.jsonl",
}
FIELDS = ("correct", "wrong1", "wrong2", "wrong3")
GROUP_LABELS = {
    "unanimous_wrong1": "A. 三模型共同选择 wrong1",
    "unanimous_other": "B. 三模型共同选择同一个 wrong2/wrong3",
    "split_wrong": "C. 三模型都错，但错误选项不同",
}


def load_jsonl(path: Path) -> dict[int, dict]:
    records: dict[int, dict] = {}
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            record = json.loads(line)
            item_index = int(record["item_index"])
            if item_index in records:
                raise ValueError(f"Duplicate item {item_index} at {path}:{line_number}")
            records[item_index] = record
    return records


def relative_top2_gap(ppls: list[float]) -> float:
    first, second, *_ = sorted(float(value) for value in ppls)
    return (second - first) / first


def escape_cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", "<br>")


def classify(choices: tuple[int, ...]) -> str:
    if len(set(choices)) == 1 and choices[0] == 1:
        return "unanimous_wrong1"
    if len(set(choices)) == 1:
        return "unanimous_other"
    return "split_wrong"


def build_rows(runs: dict[str, dict[int, dict]]) -> list[dict]:
    expected = set(range(462))
    for model_name, records in runs.items():
        if set(records) != expected:
            raise ValueError(f"{model_name} does not contain exactly item 0..461")

    rows: list[dict] = []
    for item_index in sorted(expected):
        model_records = {name: records[item_index] for name, records in runs.items()}
        reference = next(iter(model_records.values()))
        if not all(
            record["original"] == reference["original"]
            and record["candidates"] == reference["candidates"]
            for record in model_records.values()
        ):
            raise ValueError(f"Models disagree on the input for item {item_index}")
        if not all(not record["official"]["correct"] for record in model_records.values()):
            continue

        official_choices = tuple(
            record["official"]["choice"] for record in model_records.values()
        )
        candidate_rescues = [
            name
            for name, record in model_records.items()
            if record["candidate_only"]["correct"]
        ]
        rows.append(
            {
                "item_index": item_index,
                "word": reference["word"],
                "japanese_word": reference["japanese_word"],
                "surface_exact": reference["surface_exact"],
                "duplicate_options": reference["duplicate_options"],
                "group": classify(official_choices),
                "original": reference["original"],
                "candidates": reference["candidates"],
                "official_choices": {
                    name: record["official"]["choice"]
                    for name, record in model_records.items()
                },
                "candidate_choices": {
                    name: record["candidate_only"]["choice"]
                    for name, record in model_records.items()
                },
                "official_top2_gaps": {
                    name: relative_top2_gap(record["official"]["ppls"])
                    for name, record in model_records.items()
                },
                "candidate_rescues": candidate_rescues,
            }
        )
    return sorted(rows, key=lambda row: (tuple(GROUP_LABELS).index(row["group"]), row["item_index"]))


def render_markdown(rows: list[dict]) -> str:
    group_counts = Counter(row["group"] for row in rows)
    exact = sum(bool(row["surface_exact"]) for row in rows)
    duplicate = sum(bool(row["duplicate_options"]) for row in rows)
    rescued = sum(bool(row["candidate_rescues"]) for row in rows)
    all_same = group_counts["unanimous_wrong1"] + group_counts["unanimous_other"]

    lines = [
        "# 三个论文精确模型共同错误的 67 题人工审阅包",
        "",
        "筛选条件：Qwen2.5-7B-Instruct-1M、llm-jp-3-7.2b-instruct3 和 "
        "Llama-3-ELYZA-JP-8B 在同一 462 题日译中 Type-1 实验中，official "
        "评分均未选择 candidate 0。这里的‘共同错误’只依据数据集标签，不预先假定标签和候选一定没有问题。",
        "",
        "## 汇总",
        "",
        f"- 共同错误：{len(rows)}/462；",
        f"- 三模型选择同一个错误选项：{all_same}/{len(rows)}；",
        f"- 共同选择 wrong1：{group_counts['unanimous_wrong1']}；",
        f"- 共同选择同一个 wrong2/wrong3：{group_counts['unanimous_other']}；",
        f"- 三者都错但错误选项不同：{group_counts['split_wrong']}；",
        f"- 日中目标词表面完全同形：{exact}；字形变体：{len(rows) - exact}；",
        f"- 含重复候选的数据异常题：{duplicate}；",
        f"- 至少一个模型在 candidate-only 下改为正确：{rescued}。",
        "",
        "## 建议标注标签",
        "",
        "人工阅读时可填写：`clear_model_failure`、`wrong1_shortcut`、"
        "`multiple_valid`、`correct_unnatural`、`label_questionable`、"
        "`source_ambiguous`、`needs_second_annotator`。不要仅凭模型一致就修改数据标签。",
        "",
    ]

    display_number = 0
    for group_key, group_label in GROUP_LABELS.items():
        lines.extend([f"## {group_label}", ""])
        for row in (candidate for candidate in rows if candidate["group"] == group_key):
            display_number += 1
            form = "exact" if row["surface_exact"] else "variant"
            lines.extend(
                [
                    f"### {display_number}. item {row['item_index']} — {row['word']} "
                    f"（日文词形：{row['japanese_word']}；{form}）",
                    "",
                    f"**日文原句：** {row['original']}",
                    "",
                    "| 选项 | 数据标签 | 候选译文 |",
                    "| ---: | --- | --- |",
                ]
            )
            for option_index, (field, candidate) in enumerate(
                zip(FIELDS, row["candidates"])
            ):
                lines.append(
                    f"| {option_index} | {field} | {escape_cell(candidate)} |"
                )
            lines.extend(
                [
                    "",
                    "| 模型 | official 选择 | candidate-only 选择 | official 前两名相对差 |",
                    "| --- | ---: | ---: | ---: |",
                ]
            )
            for model_name in RUNS:
                official = row["official_choices"][model_name]
                candidate = row["candidate_choices"][model_name]
                gap = row["official_top2_gaps"][model_name]
                lines.append(
                    f"| {model_name} | {official} ({FIELDS[official]}) | "
                    f"{candidate} ({FIELDS[candidate]}) | {gap * 100:.2f}% |"
                )
            rescue_text = ", ".join(row["candidate_rescues"]) or "无"
            lines.extend(
                [
                    "",
                    f"candidate-only 改为正确的模型：{rescue_text}",
                    "",
                    "人工首选选项：`____`",
                    "",
                    "问题标签：`____`",
                    "",
                    "判断理由：",
                    "",
                    "---",
                    "",
                ]
            )
    return "\n".join(lines).rstrip() + "\n"


def write_csv(rows: list[dict], path: Path) -> None:
    fieldnames = [
        "item_index",
        "word",
        "japanese_word",
        "surface_exact",
        "duplicate_options",
        "group",
        "original",
        "correct",
        "wrong1",
        "wrong2",
        "wrong3",
        "qwen_official",
        "llm_jp_official",
        "elyza_official",
        "qwen_candidate_only",
        "llm_jp_candidate_only",
        "elyza_candidate_only",
        "candidate_only_rescues",
        "human_best_option",
        "issue_tags",
        "review_notes",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "item_index": row["item_index"],
                    "word": row["word"],
                    "japanese_word": row["japanese_word"],
                    "surface_exact": row["surface_exact"],
                    "duplicate_options": row["duplicate_options"],
                    "group": row["group"],
                    "original": row["original"],
                    **dict(zip(FIELDS, row["candidates"])),
                    "qwen_official": row["official_choices"]["Qwen-1M"],
                    "llm_jp_official": row["official_choices"]["llm-jp"],
                    "elyza_official": row["official_choices"]["ELYZA"],
                    "qwen_candidate_only": row["candidate_choices"]["Qwen-1M"],
                    "llm_jp_candidate_only": row["candidate_choices"]["llm-jp"],
                    "elyza_candidate_only": row["candidate_choices"]["ELYZA"],
                    "candidate_only_rescues": ";".join(row["candidate_rescues"]),
                    "human_best_option": "",
                    "issue_tags": "",
                    "review_notes": "",
                }
            )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=PROJECT_ROOT
        / "results/reviews/three-model-common-official-errors-n67.md",
    )
    parser.add_argument(
        "--csv-output",
        type=Path,
        default=PROJECT_ROOT
        / "results/reviews/three-model-common-official-errors-n67.csv",
    )
    args = parser.parse_args()

    runs = {name: load_jsonl(path) for name, path in RUNS.items()}
    rows = build_rows(runs)
    if len(rows) != 67:
        raise ValueError(f"Expected 67 shared official errors, found {len(rows)}")

    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.csv_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(render_markdown(rows), encoding="utf-8")
    write_csv(rows, args.csv_output)
    print(f"shared official errors: {len(rows)}")
    print(f"markdown: {args.markdown_output}")
    print(f"csv:      {args.csv_output}")


if __name__ == "__main__":
    main()
