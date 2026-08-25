#!/usr/bin/env python3
"""Run a resumable bidirectional Type-1 translation experiment.

Each completed item is appended to JSONL immediately. The summary compares the
official full-prompt score with the candidate-only diagnostic score.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("HF_HOME", str(PROJECT_ROOT / ".cache" / "huggingface"))
os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")
sys.path.insert(0, str(PROJECT_ROOT))

from transformers import AutoModelForCausalLM, AutoTokenizer

from questions.jp_zh.homographs import dataset as JP_ZH_DATASET
from questions.zh_jp.homographs import dataset as ZH_JP_DATASET
from scripts.compare_scoring_one_example import (
    DEFAULT_MODEL,
    score_candidate,
    select_device,
    select_dtype,
)


SCORING_VERSION = 2

DIRECTION_CONFIG = {
    "jp_zh": {
        "dataset": JP_ZH_DATASET,
        "dataset_name": "questions.jp_zh.homographs",
        "cognate_path": PROJECT_ROOT / "cognate_fixed" / "jp" / "homographs.txt",
        "to_lang": "zh",
    },
    "zh_jp": {
        "dataset": ZH_JP_DATASET,
        "dataset_name": "questions.zh_jp.homographs",
        "cognate_path": PROJECT_ROOT / "cognate_fixed" / "zh" / "homographs.txt",
        "to_lang": "jp",
    },
}


def safe_model_name(model_name: str) -> str:
    return model_name.replace("/", "--").replace(" ", "-")


def default_output(
    model_name: str,
    direction: str,
    start: int,
    limit: int,
) -> Path:
    filename = (
        f"{safe_model_name(model_name)}-{direction}-homographs-sv{SCORING_VERSION}-"
        f"start{start}-limit{limit}.jsonl"
    )
    return PROJECT_ROOT / "results" / "pilots" / filename


def load_cognate_pairs(direction: str) -> dict[str, tuple[str, str]]:
    """Map the question key to (Japanese word, Chinese word).

    In both direction-specific cognate files the question key is the second
    column.  The column language order differs: jp/ is Japanese|Chinese, while
    zh/ is Chinese|Japanese.
    """
    pairs: dict[str, tuple[str, str]] = {}
    cognate_path = DIRECTION_CONFIG[direction]["cognate_path"]
    with cognate_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            first, second, *_ = line.rstrip("\n").split("|")
            if direction == "jp_zh":
                japanese, chinese = first, second
                key = chinese
            else:
                chinese, japanese = first, second
                key = japanese
            if key in pairs:
                raise RuntimeError(f"Duplicate cognate question key: {key}")
            pairs[key] = (japanese, chinese)
    return pairs


def load_existing(path: Path) -> dict[int, dict]:
    records: dict[int, dict] = {}
    if not path.exists():
        return records
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise RuntimeError(
                    f"Cannot resume: invalid JSON at {path}:{line_number}"
                ) from exc
            records[int(record["item_index"])] = record
    return records


def choose(values: list[float]) -> int:
    return min(range(len(values)), key=values.__getitem__)


def summarize(records: list[dict]) -> dict:
    total = len(records)
    if total == 0:
        raise ValueError("No records to summarize.")

    official_correct = sum(record["official"]["correct"] for record in records)
    candidate_correct = sum(
        record["candidate_only"]["correct"] for record in records
    )
    agreements = sum(
        record["official"]["choice"] == record["candidate_only"]["choice"]
        for record in records
    )
    official_shortcuts = sum(
        record["official"]["choice"] == 1 for record in records
    )
    candidate_shortcuts = sum(
        record["candidate_only"]["choice"] == 1 for record in records
    )
    official_errors = total - official_correct
    candidate_errors = total - candidate_correct

    return {
        "items": total,
        "official": {
            "correct": official_correct,
            "accuracy": official_correct / total,
            "wrong1_selections": official_shortcuts,
            "wrong1_share_among_errors": (
                official_shortcuts / official_errors if official_errors else 0.0
            ),
        },
        "candidate_only": {
            "correct": candidate_correct,
            "accuracy": candidate_correct / total,
            "wrong1_selections": candidate_shortcuts,
            "wrong1_share_among_errors": (
                candidate_shortcuts / candidate_errors if candidate_errors else 0.0
            ),
        },
        "agreement": {
            "count": agreements,
            "rate": agreements / total,
        },
        "disagreement_items": [
            {
                "item_index": record["item_index"],
                "word": record["word"],
                "official_choice": record["official"]["choice"],
                "candidate_only_choice": record["candidate_only"]["choice"],
            }
            for record in records
            if record["official"]["choice"]
            != record["candidate_only"]["choice"]
        ],
    }


def summarize_optional(records: list[dict]) -> dict:
    return summarize(records) if records else {"items": 0}


def surface_summaries(records: list[dict]) -> dict:
    return {
        "exact": summarize_optional(
            [record for record in records if record["surface_exact"]]
        ),
        "variant": summarize_optional(
            [record for record in records if not record["surface_exact"]]
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument(
        "--direction",
        default="jp_zh",
        choices=tuple(DIRECTION_CONFIG),
        help="Translation direction: Japanese-to-Chinese or Chinese-to-Japanese.",
    )
    parser.add_argument(
        "--revision",
        help="Pin the exact Hugging Face model commit used for this run.",
    )
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--device",
        default="auto",
        choices=("auto", "cpu", "mps", "cuda"),
    )
    parser.add_argument("--local-files-only", action="store_true")
    args = parser.parse_args()

    config = DIRECTION_CONFIG[args.direction]
    dataset = config["dataset"]
    to_lang = config["to_lang"]

    all_items = list(dataset.items())
    if args.start < 0 or args.limit <= 0:
        raise ValueError("--start must be non-negative and --limit must be positive.")
    selected_items = all_items[args.start : args.start + args.limit]
    if not selected_items:
        raise ValueError("The requested range contains no dataset items.")

    expected_indices = list(range(args.start, args.start + len(selected_items)))
    output_path = args.output or default_output(
        args.model, args.direction, args.start, len(selected_items)
    )
    output_path = output_path.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path = output_path.with_suffix(".summary.json")
    cognate_pairs = load_cognate_pairs(args.direction)

    existing = load_existing(output_path)
    unexpected = set(existing) - set(expected_indices)
    if unexpected:
        raise RuntimeError(
            f"Output contains item indices outside this run: {sorted(unexpected)}"
        )
    for record in existing.values():
        if record.get("model") != args.model:
            raise RuntimeError("Existing output was produced by a different model.")
        if record.get("scoring_version") != SCORING_VERSION:
            raise RuntimeError("Existing output uses a different scoring version.")
        if record.get("direction", args.direction) != args.direction:
            raise RuntimeError("Existing output uses a different direction.")

    device = select_device(args.device)
    dtype = select_dtype(device)
    print(f"model:    {args.model}")
    print(f"direction:{args.direction:>10}")
    print(f"device:   {device}")
    print(f"dtype:    {dtype}")
    print(f"range:    [{args.start}, {args.start + len(selected_items)})")
    print(f"output:   {output_path}")
    print(f"resuming: {len(existing)} completed item(s)\n")

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

    with output_path.open("a", encoding="utf-8") as output_handle:
        for item_index, (word, item) in zip(expected_indices, selected_items):
            if item_index in existing:
                print(f"[{item_index + 1:>3}/{len(all_items)}] {word}: already complete")
                continue

            fields = ("correct", "wrong1", "wrong2", "wrong3")
            candidates = [item[field] for field in fields]
            if word not in cognate_pairs:
                raise RuntimeError(f"Question word is absent from cognate data: {word}")
            japanese_word, chinese_word = cognate_pairs[word]
            scores = [
                score_candidate(
                    model,
                    tokenizer,
                    item["target-sentence"],
                    item[field],
                    device,
                    to_lang=to_lang,
                )
                for field in fields
            ]
            official_choice = choose([score.full_ppl for score in scores])
            candidate_choice = choose([score.candidate_ppl for score in scores])
            record = {
                "scoring_version": SCORING_VERSION,
                "direction": args.direction,
                "model": args.model,
                "model_revision": getattr(model.config, "_commit_hash", None),
                "item_index": item_index,
                "word": word,
                "japanese_word": japanese_word,
                "chinese_word": chinese_word,
                "surface_exact": japanese_word == chinese_word,
                "duplicate_options": len(set(candidates)) != len(candidates),
                "original": item["target-sentence"],
                "candidates": candidates,
                "official": {
                    "losses": [score.full_loss for score in scores],
                    "ppls": [score.full_ppl for score in scores],
                    "choice": official_choice,
                    "choice_field": fields[official_choice],
                    "correct": official_choice == 0,
                },
                "candidate_only": {
                    "losses": [score.candidate_loss for score in scores],
                    "ppls": [score.candidate_ppl for score in scores],
                    "choice": candidate_choice,
                    "choice_field": fields[candidate_choice],
                    "correct": candidate_choice == 0,
                },
                "candidate_token_counts": [
                    len(score.candidate_tokens) for score in scores
                ],
            }
            output_handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            output_handle.flush()
            existing[item_index] = record
            print(
                f"[{item_index + 1:>3}/{len(all_items)}] {word}: "
                f"official={official_choice}  candidate-only={candidate_choice}"
            )

    ordered_records = [existing[index] for index in expected_indices]
    strict_summary = summarize(ordered_records)
    audited_records = [
        record for record in ordered_records if not record["duplicate_options"]
    ]
    audited_summary = summarize_optional(audited_records)
    missing_questions = [
        {"japanese": japanese, "chinese": chinese}
        for key, (japanese, chinese) in cognate_pairs.items()
        if key not in dataset
    ]
    summary = {
        "model": args.model,
        "model_revision": ordered_records[0].get("model_revision"),
        "direction": args.direction,
        "dataset": config["dataset_name"],
        "start": args.start,
        "limit": len(selected_items),
        "data_audit": {
            "cognate_rows": len(cognate_pairs),
            "translation_questions": len(dataset),
            "missing_translation_questions": missing_questions,
            "duplicate_option_items_in_run": [
                {
                    "item_index": record["item_index"],
                    "word": record["word"],
                }
                for record in ordered_records
                if record["duplicate_options"]
            ],
        },
        "strict": strict_summary,
        "audited": audited_summary,
        "surface_form": {
            "strict": surface_summaries(ordered_records),
            "audited": surface_summaries(audited_records),
        },
    }
    with summary_path.open("w", encoding="utf-8") as summary_handle:
        json.dump(summary, summary_handle, ensure_ascii=False, indent=2)
        summary_handle.write("\n")

    print(f"\n=== {strict_summary['items']}-item experiment summary ===")
    print(
        f"strict official accuracy:        "
        f"{strict_summary['official']['correct']}/{strict_summary['items']} "
        f"= {strict_summary['official']['accuracy'] * 100:.1f}%"
    )
    print(
        f"strict candidate-only accuracy:  "
        f"{strict_summary['candidate_only']['correct']}/{strict_summary['items']} "
        f"= {strict_summary['candidate_only']['accuracy'] * 100:.1f}%"
    )
    if audited_summary["items"]:
        print(
            f"audited official accuracy:       "
            f"{audited_summary['official']['correct']}/{audited_summary['items']} "
            f"= {audited_summary['official']['accuracy'] * 100:.1f}%"
        )
        print(
            f"audited candidate-only accuracy: "
            f"{audited_summary['candidate_only']['correct']}/{audited_summary['items']} "
            f"= {audited_summary['candidate_only']['accuracy'] * 100:.1f}%"
        )
    print(
        f"strict choice agreement:         "
        f"{strict_summary['agreement']['count']}/{strict_summary['items']} "
        f"= {strict_summary['agreement']['rate'] * 100:.1f}%"
    )
    print(
        f"strict official wrong1 choices:  "
        f"{strict_summary['official']['wrong1_selections']} "
        f"({strict_summary['official']['wrong1_share_among_errors'] * 100:.1f}% of errors)"
    )
    print(
        f"strict disagreements:            "
        f"{len(strict_summary['disagreement_items'])}"
    )
    for group_name in ("exact", "variant"):
        group = summary["surface_form"]["audited"][group_name]
        if group["items"]:
            print(
                f"audited {group_name:<7} official accuracy: "
                f"{group['official']['correct']}/{group['items']} "
                f"= {group['official']['accuracy'] * 100:.1f}%"
            )
    print(
        f"duplicate-option items excluded: "
        f"{len(summary['data_audit']['duplicate_option_items_in_run'])}"
    )
    print(f"summary saved to:        {summary_path}")


if __name__ == "__main__":
    main()
