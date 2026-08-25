#!/usr/bin/env python3
"""Create a blinded human-review packet for diagnostic kana transitions.

The packet is deliberately selected after model outcomes are known and is therefore
diagnostic, not a confirmatory sample.  Model choices, margins, and transition labels
are hidden from the review packet and stored in a separate key.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
from pathlib import Path


SEED = 20260825
CHOICE_FIELDS = ["correct", "wrong1", "wrong2", "wrong3"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-prefix", type=Path, required=True)
    return parser.parse_args()


def read_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def is_primary(item: dict) -> bool:
    return (
        not item["previously_exposed_causal_item"]
        and item["unrelated_control_quality_proxy"] in {"high", "medium"}
    )


def candidate_choice(item: dict, condition: str) -> int:
    return item["conditions"][condition]["candidate_only"]["choice"]


def stable_hash_rank(item: dict, category: str) -> str:
    payload = f"{SEED}:{category}:{item['item_index']}".encode()
    return hashlib.sha256(payload).hexdigest()


def balanced_hash_sample(items: list[dict], category: str, n: int = 10) -> list[dict]:
    """Prefer five exact and five variant items, then fill any shortfall."""
    exact = sorted(
        (x for x in items if x["surface_exact"]),
        key=lambda x: stable_hash_rank(x, category),
    )
    variant = sorted(
        (x for x in items if not x["surface_exact"]),
        key=lambda x: stable_hash_rank(x, category),
    )
    chosen = exact[: n // 2] + variant[: n // 2]
    chosen_ids = {x["item_index"] for x in chosen}
    if len(chosen) < n:
        remaining = sorted(
            (x for x in items if x["item_index"] not in chosen_ids),
            key=lambda x: stable_hash_rank(x, category),
        )
        chosen.extend(remaining[: n - len(chosen)])
    if len(chosen) != n:
        raise ValueError(f"category {category} has only {len(chosen)} selectable items")
    return chosen


def balanced_extreme_sample(items: list[dict], n: int = 10) -> list[dict]:
    """Select the largest absolute corrected effects, balanced by surface group."""
    rank = lambda x: (-abs(x["effects"]["orthography_effect_vs_unrelated"]), x["item_index"])
    exact = sorted((x for x in items if x["surface_exact"]), key=rank)
    variant = sorted((x for x in items if not x["surface_exact"]), key=rank)
    chosen = exact[: n // 2] + variant[: n // 2]
    chosen_ids = {x["item_index"] for x in chosen}
    if len(chosen) < n:
        remaining = sorted((x for x in items if x["item_index"] not in chosen_ids), key=rank)
        chosen.extend(remaining[: n - len(chosen)])
    if len(chosen) != n:
        raise ValueError(f"unchanged-choice category has only {len(chosen)} selectable items")
    return chosen


def select_items(items: list[dict]) -> list[dict]:
    primary = [x for x in items if is_primary(x)]
    wrong1_to_correct = [
        x for x in primary
        if candidate_choice(x, "original") == 1 and candidate_choice(x, "target_kana") == 0
    ]
    correct_to_other = [
        x for x in primary
        if candidate_choice(x, "original") == 0 and candidate_choice(x, "target_kana") in {2, 3}
    ]
    unchanged = [
        x for x in primary
        if candidate_choice(x, "original") == candidate_choice(x, "target_kana")
    ]

    selected: list[dict] = []
    for item in balanced_hash_sample(wrong1_to_correct, "wrong1_to_correct"):
        selected.append({"category": "wrong1_to_correct", "item": item})
    for item in balanced_hash_sample(correct_to_other, "correct_to_wrong2_or_wrong3"):
        selected.append({"category": "correct_to_wrong2_or_wrong3", "item": item})
    for item in balanced_extreme_sample(unchanged):
        selected.append({"category": "large_effect_choice_unchanged", "item": item})

    rng = random.Random(SEED)
    rng.shuffle(selected)
    for review_id, row in enumerate(selected, start=1):
        row["review_id"] = review_id
    return selected


def render_blind_packet(selected: list[dict], source_hash: str) -> str:
    lines = [
        "# 假名化转移案例盲态人工审核包（30题）",
        "",
        "## 用途与边界",
        "",
        "这 30 题是根据已经观察到的模型转移结果进行的诊断性抽样，不是确认性随机样本，不能用来估计数据集总体比例。每类 10 题；exact/variant 各优先抽取 5 题。为了减少锚定，本文隐藏模型选择、margin、效应方向和类别，结果见单独的 key 文件。",
        "",
        f"- 固定随机种子：`{SEED}`",
        f"- 来源结果 SHA-256：`{source_hash}`",
        "- 评分口径：candidate-only",
        "",
        "## 审核说明",
        "",
        "每题请先不看 key，填写以下判断：",
        "",
        "1. `target-kana` 的读音是否正确；",
        "2. 假名化后日语句子是否自然、是否保持原义、是否引入新的同音歧义；",
        "3. `unrelated-control` 是否自然且没有改变与目标词有关的语义证据；",
        "4. 中文候选中哪些可以接受（允许多选），candidate 0 是否确实优于其他候选；",
        "5. 如有问题，标注 `kana_invalid`、`homophone_ambiguity`、`multiple_valid`、`label_questionable`、`semantic_drift` 或自由备注。",
        "",
    ]
    for row in selected:
        item = row["item"]
        lines.extend([
            f"## R{row['review_id']:02d}｜item {item['item_index']}｜{item['word']}",
            "",
            f"- 原句：{item['source_sentences']['original']}",
            f"- 目标假名：{item['source_sentences']['target_kana']}",
            f"- 无关控制：{item['source_sentences']['unrelated_control_kana']}",
            f"- 目标替换：`{item['target_intervention_span']}`",
            f"- 控制替换：`{item['control_spans']['unrelated']}`",
            f"- candidate 0：{item['candidates'][0]}",
            f"- candidate 1：{item['candidates'][1]}",
            f"- candidate 2：{item['candidates'][2]}",
            f"- candidate 3：{item['candidates'][3]}",
            "",
            "填写：",
            "",
            "- target 读音正确：",
            "- target-kana 自然／原义保持／无新歧义：",
            "- unrelated-control 合格：",
            "- 可接受的中文候选（可多选）：",
            "- 首选候选：",
            "- 问题标签：",
            "- 备注：",
            "",
        ])
    return "\n".join(lines).rstrip() + "\n"


def render_key(selected: list[dict], source_hash: str) -> str:
    lines = [
        "# 假名化转移案例审核 key",
        "",
        "请在完成盲态语义审核后再看本文件。该文件中的类别和数值来自模型输出，不是人工金标准。",
        "",
        f"来源结果 SHA-256：`{source_hash}`",
        "",
        "| review | item | 词 | 类别 | original→target | original margin | target margin | control margin | corrected effect |",
        "| ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for row in selected:
        item = row["item"]
        original = candidate_choice(item, "original")
        target = candidate_choice(item, "target_kana")
        lines.append(
            f"| R{row['review_id']:02d} | {item['item_index']} | {item['word']} | "
            f"{row['category']} | {original} ({CHOICE_FIELDS[original]}) → "
            f"{target} ({CHOICE_FIELDS[target]}) | {item['margins']['original']:+.3f} | "
            f"{item['margins']['target_kana']:+.3f} | "
            f"{item['margins']['unrelated_control_kana']:+.3f} | "
            f"{item['effects']['orthography_effect_vs_unrelated']:+.3f} |"
        )
    lines.extend([
        "",
        "类别定义：",
        "",
        "- `wrong1_to_correct`：原句选择 wrong1，目标词假名化后选择数据标签 correct；",
        "- `correct_to_wrong2_or_wrong3`：原句选择 correct，目标词假名化后转向 wrong2/3；",
        "- `large_effect_choice_unchanged`：最终选择不变，但在各 surface 组中 corrected effect 的绝对值最大；",
        "- `corrected effect = margin(target-kana) - margin(unrelated-control-kana)`。",
    ])
    return "\n".join(lines).rstrip() + "\n"


def write_csv(path: Path, selected: list[dict]) -> None:
    fields = [
        "review_id", "item_index", "word", "surface_exact", "original",
        "target_kana", "unrelated_control", "candidate_0", "candidate_1",
        "candidate_2", "candidate_3", "target_reading_correct",
        "target_kana_valid", "unrelated_control_valid", "acceptable_candidates",
        "preferred_candidate", "issue_labels", "notes",
    ]
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in selected:
            item = row["item"]
            writer.writerow({
                "review_id": f"R{row['review_id']:02d}",
                "item_index": item["item_index"],
                "word": item["word"],
                "surface_exact": item["surface_exact"],
                "original": item["source_sentences"]["original"],
                "target_kana": item["source_sentences"]["target_kana"],
                "unrelated_control": item["source_sentences"]["unrelated_control_kana"],
                "candidate_0": item["candidates"][0],
                "candidate_1": item["candidates"][1],
                "candidate_2": item["candidates"][2],
                "candidate_3": item["candidates"][3],
            })


def main() -> None:
    args = parse_args()
    data = args.input.read_bytes()
    source_hash = hashlib.sha256(data).hexdigest()
    selected = select_items(read_jsonl(args.input))
    args.output_prefix.parent.mkdir(parents=True, exist_ok=True)
    args.output_prefix.with_suffix(".blind.md").write_text(
        render_blind_packet(selected, source_hash), encoding="utf-8"
    )
    args.output_prefix.with_suffix(".key.md").write_text(
        render_key(selected, source_hash), encoding="utf-8"
    )
    write_csv(args.output_prefix.with_suffix(".blind.csv"), selected)
    print(f"wrote {len(selected)} blinded review items")


if __name__ == "__main__":
    main()
