#!/usr/bin/env python3
"""Render a model-outcome-free Markdown review packet from a material draft."""

from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = (
    PROJECT_ROOT
    / "results"
    / "causal"
    / "orthography-confirmatory-pilot-seed20260823-repl20260825-n30.materials-draft-v2.csv"
)
DEFAULT_OUTPUT = (
    PROJECT_ROOT
    / "results"
    / "causal"
    / "orthography-confirmatory-pilot-seed20260823-repl20260825-n30.human-review-packet-v2.md"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    input_path = args.input.resolve()
    output_path = args.output.resolve()
    if output_path.exists():
        raise FileExistsError(f"Refusing to overwrite review packet: {output_path}")

    with input_path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 30:
        raise ValueError(f"Expected 30 rows, found {len(rows)}")

    lines = [
        "# 30题确认性假名实验：盲态人工复核包（v2）",
        "",
        "> 本文件不包含任何模型输出。请只根据日语材料判断，不要预测实验方向。",
        "",
        f"- 材料草稿：`{input_path.name}`",
        f"- 材料草稿 SHA-256：`{sha256(input_path)}`",
        "- 组成：原冻结表中未曝光的 25 题，加固定种子补抽的 5 题；exact/variant 各 15。",
        "- 当前状态：机器读音与控制词建议稿，未获人工通过，禁止模型评分。",
        "",
        "## 复核规则",
        "",
        "每题检查目标与控制读音、两种假名句自然度、语义保持、潜在同音歧义、上下文能否消歧，以及 target/control 的歧义程度是否大致匹配。若控制词不合适，可以标记 `REVISE_CONTROL`，但不要根据任何预期模型结果修改。",
        "",
        "建议分三批完成：1-10、11-20、21-30。每批完成后再统一修改材料并生成新的冻结版本。",
        "",
    ]
    for position, row in enumerate(rows, start=1):
        lines.extend(
            [
                f"## {position:02d}. item {row['item_index']} — {row['word']} / {row['japanese_word']}",
                "",
                f"- 分层：`surface_exact={row['surface_exact']}`；来源：`{row['selection_source']}`",
                f"- original：{row['original']}",
                f"- target：`{row['japanese_word']}→{row['target_reading']}`",
                f"- target-kana：{row['target_kana_sentence']}",
                f"- control：`{row['control_word']}→{row['control_reading']}`",
                f"- control-kana：{row['control_kana_sentence']}",
                f"- 长度差（control-target）：surface `{row['surface_char_delta_control_minus_target']}`；reading `{row['reading_char_delta_control_minus_target']}`",
                "",
                "填写：",
                "",
                "- 目标/控制读音：",
                "- target 自然度（1-5）：",
                "- control 自然度（1-5）：",
                "- 语义保持：",
                "- target 同音风险：",
                "- target 上下文可消歧：",
                "- control 同音风险：",
                "- control 上下文可消歧：",
                "- target/control 歧义匹配：",
                "- 决定：",
                "- 备注：",
                "",
            ]
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"rows rendered: {len(rows)}")
    print(f"packet:        {output_path}")
    print(f"sha256:        {sha256(output_path)}")


if __name__ == "__main__":
    main()
