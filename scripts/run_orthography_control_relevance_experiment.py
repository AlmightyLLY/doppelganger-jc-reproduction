#!/usr/bin/env python3
"""Score a 30-item four-condition orthography control-relevance pilot."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import random
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
from scripts.run_orthography_causal_smoke import pack_scores


DEFAULT_MODEL = "Qwen/Qwen2.5-7B-Instruct-1M"
DEFAULT_REVISION = "e28526f7bb80e2a9c8af03b831a9af3812f18fba"
DEFAULT_MATERIAL = (
    PROJECT_ROOT / "results" / "causal" / "orthography-control-relevance-pilot-n30.jsonl"
)
FIELDS = ("correct", "wrong1", "wrong2", "wrong3")
CONDITIONS = (
    "original",
    "target_kana",
    "unrelated_control_kana",
    "related_semantic_cue_kana",
)
BOOTSTRAP_SEED = 20260825
BOOTSTRAP_SAMPLES = 10000


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
        raise ValueError(f"No rows found in {path}")
    return rows


def validate_material(rows: list[dict[str, Any]]) -> None:
    indexed_dataset = list(dataset.items())
    required = {
        "item_index",
        "word",
        "japanese_word",
        "surface_exact",
        "original",
        "target_reading",
        "target_kana_sentence",
        "unrelated_control_word",
        "unrelated_control_reading",
        "unrelated_control_kana_sentence",
        "related_semantic_cue_word",
        "related_semantic_cue_reading",
        "related_semantic_cue_kana_sentence",
        "selection_rule",
        "purpose",
        "review_status",
    }
    seen: set[int] = set()
    for row in rows:
        missing = required.difference(row)
        if missing:
            raise ValueError(f"Material row missing fields: {sorted(missing)}")
        index = row["item_index"]
        if not isinstance(index, int) or not 0 <= index < len(indexed_dataset):
            raise ValueError(f"Invalid item_index: {index!r}")
        if index in seen:
            raise ValueError(f"Duplicate item_index: {index}")
        seen.add(index)
        word, item = indexed_dataset[index]
        if row["word"] != word:
            raise ValueError(f"item {index}: word mismatch")
        if row["original"] != item["target-sentence"]:
            raise ValueError(f"item {index}: original differs from dataset")
        target = row["japanese_word"]
        unrelated = row["unrelated_control_word"]
        related = row["related_semantic_cue_word"]
        if len({target, unrelated, related}) != 3:
            raise ValueError(f"item {index}: target/control spans are not distinct")
        for span in (target, unrelated, related):
            if row["original"].count(span) != 1:
                raise ValueError(f"item {index}: span {span!r} must occur once")
        expected = {
            "target_kana_sentence": row["original"].replace(
                target, row["target_reading"], 1
            ),
            "unrelated_control_kana_sentence": row["original"].replace(
                unrelated, row["unrelated_control_reading"], 1
            ),
            "related_semantic_cue_kana_sentence": row["original"].replace(
                related, row["related_semantic_cue_reading"], 1
            ),
        }
        for field, sentence in expected.items():
            if row[field] != sentence:
                raise ValueError(f"item {index}: invalid one-span replacement for {field}")
        candidates = [item[field] for field in FIELDS]
        if len(set(candidates)) != 4:
            raise ValueError(f"item {index}: duplicate candidates")
        if row["purpose"] != "pre_outcome_control_relevance_pilot_n30":
            raise ValueError(f"item {index}: unexpected purpose")


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


def percentile(sorted_values: list[float], probability: float) -> float:
    if len(sorted_values) == 1:
        return sorted_values[0]
    position = probability * (len(sorted_values) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return sorted_values[lower]
    weight = position - lower
    return sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight


def bootstrap_mean_ci(values: list[float], seed_offset: int) -> list[float]:
    rng = random.Random(BOOTSTRAP_SEED + seed_offset)
    n = len(values)
    means = [
        statistics.mean(values[rng.randrange(n)] for _ in range(n))
        for _ in range(BOOTSTRAP_SAMPLES)
    ]
    means.sort()
    return [percentile(means, 0.025), percentile(means, 0.975)]


def describe(values: list[float], seed_offset: int) -> dict[str, Any]:
    return {
        "values": values,
        "mean": statistics.mean(values),
        "median": statistics.median(values),
        "bootstrap_mean_95ci": bootstrap_mean_ci(values, seed_offset),
        "positive_count": sum(value > 0 for value in values),
        "negative_count": sum(value < 0 for value in values),
        "zero_count": sum(value == 0 for value in values),
    }


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    condition_summary: dict[str, Any] = {}
    for condition in CONDITIONS:
        choices = [
            record["conditions"][condition]["candidate_only"]["choice"]
            for record in records
        ]
        margins = [record["margins"][condition] for record in records]
        original_choices = [
            record["conditions"]["original"]["candidate_only"]["choice"]
            for record in records
        ]
        condition_summary[condition] = {
            "candidate_only_correct": sum(choice == 0 for choice in choices),
            "candidate_only_wrong1": sum(choice == 1 for choice in choices),
            "choice_counts": {
                field: sum(choice == index for choice in choices)
                for index, field in enumerate(FIELDS)
            },
            "mean_margin": statistics.mean(margins),
            "median_margin": statistics.median(margins),
            "choice_changes_from_original": sum(
                choice != original
                for choice, original in zip(choices, original_choices)
            ),
        }

    effect_keys = (
        "target_effect",
        "unrelated_control_effect",
        "related_semantic_cue_effect",
        "orthography_effect_vs_unrelated",
        "orthography_effect_vs_related",
        "related_minus_unrelated_control_effect",
    )
    effect_summary = {
        key: describe([record["effects"][key] for record in records], offset)
        for offset, key in enumerate(effect_keys, start=1)
    }

    abs_unrelated = [
        abs(record["effects"]["unrelated_control_effect"]) for record in records
    ]
    abs_related = [
        abs(record["effects"]["related_semantic_cue_effect"]) for record in records
    ]
    abs_difference = [
        related - unrelated
        for unrelated, related in zip(abs_unrelated, abs_related)
    ]

    strata: dict[str, Any] = {}
    for label, expected in (("surface_exact", True), ("surface_variant", False)):
        subset = [record for record in records if record["surface_exact"] is expected]
        strata[label] = {
            "n_items": len(subset),
            "orthography_effect_vs_unrelated": describe(
                [record["effects"]["orthography_effect_vs_unrelated"] for record in subset],
                100 if expected else 101,
            ),
            "related_minus_unrelated_control_effect": describe(
                [record["effects"]["related_minus_unrelated_control_effect"] for record in subset],
                102 if expected else 103,
            ),
        }

    return {
        "n_items": len(records),
        "inference_status": (
            "pilot_n30_agent_constructed_controls_no_independent_bilingual_second_review"
        ),
        "primary_metric": "candidate_only_mean_nll",
        "margin_definition": "NLL(wrong1)-NLL(correct); larger favors correct",
        "condition_summary": condition_summary,
        "effects": effect_summary,
        "control_perturbation_comparison": {
            "absolute_unrelated_control_effect": describe(abs_unrelated, 200),
            "absolute_related_semantic_cue_effect": describe(abs_related, 201),
            "absolute_related_minus_unrelated": describe(abs_difference, 202),
            "unrelated_closer_to_original_count": sum(
                unrelated < related
                for unrelated, related in zip(abs_unrelated, abs_related)
            ),
            "related_closer_to_original_count": sum(
                related < unrelated
                for unrelated, related in zip(abs_unrelated, abs_related)
            ),
            "ties": sum(
                unrelated == related
                for unrelated, related in zip(abs_unrelated, abs_related)
            ),
            "interpretation_guard": (
                "Smaller absolute perturbation is a stability diagnostic, not by itself proof "
                "that a control satisfies the causal negative-control assumption."
            ),
        },
        "surface_strata": strata,
        "bootstrap": {
            "resamples": BOOTSTRAP_SAMPLES,
            "seed": BOOTSTRAP_SEED,
            "unit": "paired item",
        },
        "warnings": [
            "The unrelated/related assignments were constructed by the agent under explicit user authorization.",
            "No independent bilingual second reviewer validated all 30 interventions.",
            "The related semantic cue is an exploratory intervention, not a negative control.",
            "This n=30 pilot does not support population-wide causal claims or model comparisons.",
        ],
    }


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
    print(f"items: {len(rows)}")
    print(f"sha256: {material_hash}")
    print("material structure: VALID")
    if args.validate_material_only:
        return
    if args.output is None:
        parser.error("--output is required unless --validate-material-only is used")

    output_path = args.output.resolve()
    summary_path = output_path.with_suffix(".summary.json")
    if not args.force and (output_path.exists() or summary_path.exists()):
        raise FileExistsError("Output already exists; use a new path or --force")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    device = select_device(args.device)
    dtype = select_dtype(device)
    print(f"model: {args.model}")
    print(f"revision: {args.revision}")
    print(f"device: {device}")
    print(f"dtype: {dtype}")

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
            "unrelated_control_kana": row["unrelated_control_kana_sentence"],
            "related_semantic_cue_kana": row["related_semantic_cue_kana_sentence"],
        }
        source_token_counts = {
            condition: len(tokenizer(source, add_special_tokens=False)["input_ids"])
            for condition, source in source_sentences.items()
        }
        condition_results: dict[str, Any] = {}
        with torch.inference_mode():
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
        unrelated_effect = margins["unrelated_control_kana"] - margins["original"]
        related_effect = margins["related_semantic_cue_kana"] - margins["original"]
        effects = {
            "target_effect": target_effect,
            "unrelated_control_effect": unrelated_effect,
            "related_semantic_cue_effect": related_effect,
            "orthography_effect_vs_unrelated": target_effect - unrelated_effect,
            "orthography_effect_vs_related": target_effect - related_effect,
            "related_minus_unrelated_control_effect": related_effect - unrelated_effect,
        }
        if not all(math.isfinite(value) for value in (*margins.values(), *effects.values())):
            raise RuntimeError(f"item {row['item_index']}: non-finite effect")

        record = {
            "experiment": "orthography_control_relevance_pilot_n30",
            "model": args.model,
            "requested_revision": args.revision,
            "resolved_revision": resolved_revision,
            "material_sha256": material_hash,
            "item_index": row["item_index"],
            "word": row["word"],
            "japanese_word": row["japanese_word"],
            "surface_exact": row["surface_exact"],
            "review_status": row["review_status"],
            "control_spans": {
                "unrelated": row["unrelated_control_word"],
                "related_semantic_cue": row["related_semantic_cue_word"],
            },
            "source_sentences": source_sentences,
            "source_token_counts": source_token_counts,
            "candidates": candidates,
            "conditions": condition_results,
            "margins": margins,
            "effects": effects,
        }
        records.append(record)
        print(
            f"[{position:02d}/{len(rows)}] {row['word']}: choices="
            f"{condition_results['original']['candidate_only']['choice']}/"
            f"{condition_results['target_kana']['candidate_only']['choice']}/"
            f"{condition_results['unrelated_control_kana']['candidate_only']['choice']}/"
            f"{condition_results['related_semantic_cue_kana']['candidate_only']['choice']} "
            f"E_unrelated={effects['orthography_effect_vs_unrelated']:+.6f} "
            f"related-unrelated={effects['related_minus_unrelated_control_effect']:+.6f}"
        )

    summary = {
        "experiment": "orthography_control_relevance_pilot_n30",
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
    print("\n=== 30-item control-relevance pilot summary ===")
    print(
        "mean orthography effect vs unrelated: "
        f"{summary['effects']['orthography_effect_vs_unrelated']['mean']:+.6f}"
    )
    print(
        "mean related-minus-unrelated control effect: "
        f"{summary['effects']['related_minus_unrelated_control_effect']['mean']:+.6f}"
    )
    print(f"results: {output_path}")
    print(f"summary: {summary_path}")
    print("INFERENCE: pilot only; agent-constructed controls, no independent second review")


if __name__ == "__main__":
    main()
