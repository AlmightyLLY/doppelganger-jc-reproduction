#!/usr/bin/env python3
"""Run a small three-condition orthography intervention smoke test.

This is an engineering smoke test, not an inferential causal analysis.  It
scores the same four Chinese candidates after changing only the Japanese
source sentence: original, target word in kana, and an unrelated control word
in kana.  The primary score is candidate-only mean NLL.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import statistics
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("HF_HOME", str(PROJECT_ROOT / ".cache" / "huggingface"))
sys.path.insert(0, str(PROJECT_ROOT))

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from questions.jp_zh.homographs import dataset
from scripts.compare_scoring_one_example import (
    score_candidate,
    select_device,
    select_dtype,
)


DEFAULT_MODEL = "Qwen/Qwen2.5-7B-Instruct-1M"
DEFAULT_REVISION = "e28526f7bb80e2a9c8af03b831a9af3812f18fba"
DEFAULT_MATERIAL = (
    PROJECT_ROOT / "results/causal/orthography-engineering-smoke-n5.jsonl"
)
FIELDS = ("correct", "wrong1", "wrong2", "wrong3")
CONDITIONS = ("original", "target_kana", "control_kana")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as error:
                raise ValueError(f"{path}:{line_number}: invalid JSON: {error}") from error
    if not rows:
        raise ValueError(f"No material rows found in {path}")
    return rows


def validate_material(rows: list[dict[str, Any]]) -> None:
    indexed_dataset = list(dataset.items())
    seen: set[int] = set()
    required = {
        "item_index",
        "word",
        "japanese_word",
        "surface_exact",
        "original",
        "target_reading",
        "target_kana_sentence",
        "control_word",
        "control_reading",
        "control_kana_sentence",
        "selection_rule",
        "purpose",
        "review_status",
    }

    for row in rows:
        missing = required.difference(row)
        if missing:
            raise ValueError(f"Material row is missing fields: {sorted(missing)}")

        index = row["item_index"]
        if not isinstance(index, int) or not 0 <= index < len(indexed_dataset):
            raise ValueError(f"Invalid item_index: {index!r}")
        if index in seen:
            raise ValueError(f"Duplicate item_index: {index}")
        seen.add(index)

        dataset_word, item = indexed_dataset[index]
        if row["word"] != dataset_word:
            raise ValueError(
                f"item {index}: word mismatch ({row['word']!r} != {dataset_word!r})"
            )
        if row["original"] != item["target-sentence"]:
            raise ValueError(f"item {index}: original sentence differs from dataset")

        target_word = row["japanese_word"]
        target_reading = row["target_reading"]
        control_word = row["control_word"]
        control_reading = row["control_reading"]
        original = row["original"]
        if target_word == control_word:
            raise ValueError(f"item {index}: target and control word are identical")
        if original.count(target_word) != 1:
            raise ValueError(f"item {index}: target word must occur exactly once")
        if original.count(control_word) != 1:
            raise ValueError(f"item {index}: control word must occur exactly once")

        expected_target = original.replace(target_word, target_reading, 1)
        expected_control = original.replace(control_word, control_reading, 1)
        if row["target_kana_sentence"] != expected_target:
            raise ValueError(f"item {index}: target_kana is not a one-span replacement")
        if row["control_kana_sentence"] != expected_control:
            raise ValueError(f"item {index}: control_kana is not a one-span replacement")

        candidates = [item[field] for field in FIELDS]
        if len(set(candidates)) != len(candidates):
            raise ValueError(f"item {index}: duplicate Chinese candidates")
        if row["purpose"] != "engineering_smoke_only":
            raise ValueError(f"item {index}: unexpected purpose label")


def pack_scores(scores) -> dict[str, Any]:
    full_losses = [score.full_loss for score in scores]
    candidate_losses = [score.candidate_loss for score in scores]
    official_choice = min(range(len(scores)), key=full_losses.__getitem__)
    candidate_choice = min(range(len(scores)), key=candidate_losses.__getitem__)
    return {
        "official": {
            "losses": full_losses,
            "ppls": [score.full_ppl for score in scores],
            "choice": official_choice,
            "choice_field": FIELDS[official_choice],
            "correct": official_choice == 0,
        },
        "candidate_only": {
            "losses": candidate_losses,
            "ppls": [score.candidate_ppl for score in scores],
            "choice": candidate_choice,
            "choice_field": FIELDS[candidate_choice],
            "correct": candidate_choice == 0,
            "shortcut_margin_wrong1_minus_correct": (
                candidate_losses[1] - candidate_losses[0]
            ),
        },
        "candidate_token_counts": [len(score.candidate_tokens) for score in scores],
        "candidate_tokens": [list(score.candidate_tokens) for score in scores],
    }


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    effects = [record["effects"] for record in records]
    condition_summary: dict[str, Any] = {}
    for condition in CONDITIONS:
        choices = [
            record["conditions"][condition]["candidate_only"]["choice"]
            for record in records
        ]
        margins = [
            record["conditions"][condition]["candidate_only"][
                "shortcut_margin_wrong1_minus_correct"
            ]
            for record in records
        ]
        condition_summary[condition] = {
            "candidate_only_correct": sum(choice == 0 for choice in choices),
            "candidate_only_wrong1": sum(choice == 1 for choice in choices),
            "choice_counts": {
                field: sum(choice == index for choice in choices)
                for index, field in enumerate(FIELDS)
            },
            "mean_shortcut_margin_wrong1_minus_correct": statistics.mean(margins),
            "median_shortcut_margin_wrong1_minus_correct": statistics.median(margins),
        }

    def describe(key: str) -> dict[str, Any]:
        values = [effect[key] for effect in effects]
        return {
            "values": values,
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "positive_count": sum(value > 0 for value in values),
            "negative_count": sum(value < 0 for value in values),
            "zero_count": sum(value == 0 for value in values),
        }

    original_target_flips: dict[str, int] = {}
    for record in records:
        original_choice = record["conditions"]["original"]["candidate_only"][
            "choice_field"
        ]
        target_choice = record["conditions"]["target_kana"]["candidate_only"][
            "choice_field"
        ]
        label = f"{original_choice}->{target_choice}"
        original_target_flips[label] = original_target_flips.get(label, 0) + 1

    return {
        "n_items": len(records),
        "inference_status": "none_engineering_smoke_n5",
        "primary_metric": "candidate_only_mean_nll",
        "margin_definition": "NLL(wrong1)-NLL(correct); larger favors correct",
        "condition_summary": condition_summary,
        "target_effect": describe("target_effect"),
        "control_effect": describe("control_effect"),
        "orthography_effect_difference_in_differences": describe(
            "orthography_effect"
        ),
        "original_to_target_choice_flips": original_target_flips,
        "warning": (
            "Five preselected items are for implementation and direction checks only; "
            "do not report bootstrap intervals, p-values, or causal population claims."
        ),
    }


def atomic_write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--material", type=Path, default=DEFAULT_MATERIAL)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--revision", default=DEFAULT_REVISION)
    parser.add_argument(
        "--device", default="auto", choices=("auto", "cpu", "mps", "cuda")
    )
    parser.add_argument("--local-files-only", action="store_true")
    parser.add_argument("--validate-material-only", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    material_path = args.material.resolve()
    rows = load_jsonl(material_path)
    validate_material(rows)
    material_hash = sha256(material_path)
    print(f"material: {material_path}")
    print(f"items:    {len(rows)}")
    print(f"sha256:   {material_hash}")
    print("material structure: VALID")
    if args.validate_material_only:
        return
    if args.output is None:
        parser.error("--output is required unless --validate-material-only is used")

    output_path = args.output.resolve()
    summary_path = output_path.with_suffix(".summary.json")
    if not args.force and (output_path.exists() or summary_path.exists()):
        raise FileExistsError("Output already exists; use a new path or pass --force")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    device = select_device(args.device)
    dtype = select_dtype(device)
    print(f"model:    {args.model}")
    print(f"revision: {args.revision}")
    print(f"device:   {device}")
    print(f"dtype:    {dtype}")

    tokenizer = AutoTokenizer.from_pretrained(
        args.model,
        revision=args.revision,
        local_files_only=args.local_files_only,
        trust_remote_code=True,
    )
    model = AutoModelForCausalLM.from_pretrained(
        args.model,
        revision=args.revision,
        torch_dtype=dtype,
        low_cpu_mem_usage=True,
        local_files_only=args.local_files_only,
        trust_remote_code=True,
    ).to(device).eval()
    resolved_revision = getattr(model.config, "_commit_hash", None)
    parameter_count = sum(parameter.numel() for parameter in model.parameters())
    print(f"parameters: {parameter_count / 1e9:.3f}B")
    print(f"resolved revision: {resolved_revision}\n")

    indexed_dataset = list(dataset.items())
    records: list[dict[str, Any]] = []
    for position, row in enumerate(rows, start=1):
        _, item = indexed_dataset[row["item_index"]]
        candidates = [item[field] for field in FIELDS]
        source_sentences = {
            "original": row["original"],
            "target_kana": row["target_kana_sentence"],
            "control_kana": row["control_kana_sentence"],
        }
        condition_results: dict[str, Any] = {}
        for condition, source_sentence in source_sentences.items():
            scores = [
                score_candidate(model, tokenizer, source_sentence, candidate, device)
                for candidate in candidates
            ]
            condition_results[condition] = pack_scores(scores)

        margins = {
            condition: condition_results[condition]["candidate_only"][
                "shortcut_margin_wrong1_minus_correct"
            ]
            for condition in CONDITIONS
        }
        target_effect = margins["target_kana"] - margins["original"]
        control_effect = margins["control_kana"] - margins["original"]
        orthography_effect = target_effect - control_effect
        if not all(
            math.isfinite(value)
            for value in (*margins.values(), target_effect, control_effect, orthography_effect)
        ):
            raise RuntimeError(f"item {row['item_index']}: non-finite effect")

        record = {
            "experiment": "orthography_engineering_smoke_n5",
            "model": args.model,
            "requested_revision": args.revision,
            "resolved_revision": resolved_revision,
            "material_sha256": material_hash,
            "item_index": row["item_index"],
            "word": row["word"],
            "japanese_word": row["japanese_word"],
            "surface_exact": row["surface_exact"],
            "review_status": row["review_status"],
            "source_sentences": source_sentences,
            "candidates": candidates,
            "conditions": condition_results,
            "effects": {
                "target_effect": target_effect,
                "control_effect": control_effect,
                "orthography_effect": orthography_effect,
            },
        }
        records.append(record)
        print(
            f"[{position}/{len(rows)}] {row['word']}: "
            f"choices="
            f"{condition_results['original']['candidate_only']['choice']}/"
            f"{condition_results['target_kana']['candidate_only']['choice']}/"
            f"{condition_results['control_kana']['candidate_only']['choice']} "
            f"orthography_effect={orthography_effect:+.6f}"
        )

    summary = {
        "experiment": "orthography_engineering_smoke_n5",
        "model": args.model,
        "requested_revision": args.revision,
        "resolved_revision": resolved_revision,
        "parameter_count": parameter_count,
        "material_path": str(material_path),
        "material_sha256": material_hash,
        "selection_rule": rows[0]["selection_rule"],
        **summarize(records),
    }
    atomic_write_jsonl(output_path, records)
    atomic_write_json(summary_path, summary)
    print("\n=== engineering smoke summary ===")
    print(
        "mean orthography effect: "
        f"{summary['orthography_effect_difference_in_differences']['mean']:+.6f}"
    )
    print(f"results: {output_path}")
    print(f"summary: {summary_path}")
    print("INFERENCE: none (n=5 engineering smoke)")


if __name__ == "__main__":
    main()
