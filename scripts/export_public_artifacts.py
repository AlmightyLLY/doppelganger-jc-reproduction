#!/usr/bin/env python3
"""Create scores-only public artifacts without benchmark or intervention text.

Local inference outputs retain text because the scorers need it.  Public
artifacts retain item indices, model metadata, scores, choices, token counts,
and derived statistics so every reported aggregate remains recomputable after
the reader obtains the pinned benchmark from its authoritative source.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
UPSTREAM_COMMIT = "eb1c4f3f17403af238046bf218dc49643bc2e2e2"
SCHEMA = "scores_only_v1"

TRANSLATION_FIELDS = (
    "scoring_version",
    "direction",
    "model",
    "model_revision",
    "item_index",
    "surface_exact",
    "duplicate_options",
    "official",
    "candidate_only",
    "candidate_token_counts",
)
ORTHOGRAPHY_FIELDS = (
    "experiment",
    "model",
    "requested_revision",
    "resolved_revision",
    "material_sha256",
    "item_index",
    "target_span_rule",
    "surface_exact",
    "previously_exposed_causal_item",
    "unrelated_control_quality_proxy",
    "review_status",
    "related_available",
    "source_token_counts",
    "conditions",
    "margins",
    "effects",
)
SENSITIVE_KEYS = {
    "word",
    "japanese_word",
    "chinese_word",
    "japanese",
    "chinese",
    "candidates",
    "candidate_tokens",
    "source_sentences",
    "target_intervention_span",
    "control_spans",
    "target_reading",
    "target_kana_sentence",
    "unrelated_control_word",
    "unrelated_control_reading",
    "unrelated_control_kana_sentence",
    "related_semantic_cue_word",
    "related_semantic_cue_reading",
    "related_semantic_cue_kana_sentence",
    "candidate_spans",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def infer_direction(path: Path) -> str:
    if "-jp_zh-" in path.name:
        return "jp_zh"
    if "-zh_jp-" in path.name:
        return "zh_jp"
    raise ValueError(f"Cannot infer translation direction from {path}")


def sanitize_translation_record(path: Path, record: dict[str, Any]) -> dict[str, Any]:
    packed = {key: record[key] for key in TRANSLATION_FIELDS if key in record}
    packed.setdefault("direction", infer_direction(path))
    packed["public_artifact_schema"] = SCHEMA
    return packed


def sanitize_orthography_record(record: dict[str, Any]) -> dict[str, Any]:
    packed = {key: record[key] for key in ORTHOGRAPHY_FIELDS if key in record}
    if "conditions" in packed:
        packed["conditions"] = scrub_tree(packed["conditions"])
    packed["public_artifact_schema"] = SCHEMA
    return packed


def scrub_tree(value: Any) -> Any:
    if isinstance(value, list):
        return [scrub_tree(item) for item in value]
    if not isinstance(value, dict):
        return value
    output: dict[str, Any] = {}
    for key, item in value.items():
        if key in SENSITIVE_KEYS:
            continue
        # In orthography summaries, ``original`` names a condition and is a
        # dictionary.  In benchmark-bearing analyses it is a sentence string.
        if key == "original" and isinstance(item, str):
            continue
        if key == "material_path":
            output["material_source"] = "generated locally from pinned upstream data"
            continue
        output[key] = scrub_tree(item)
    return output


def sanitize_summary(payload: dict[str, Any]) -> dict[str, Any]:
    result = scrub_tree(payload)
    audit = result.get("data_audit")
    source_audit = payload.get("data_audit")
    if isinstance(audit, dict) and isinstance(source_audit, dict):
        missing = source_audit.get("missing_translation_questions")
        if isinstance(missing, list):
            audit.pop("missing_translation_questions", None)
            audit["missing_translation_question_count"] = len(missing)
    result["public_artifact_schema"] = SCHEMA
    result["benchmark_text_removed"] = True
    result["join_key"] = "item_index"
    result["upstream_commit"] = UPSTREAM_COMMIT
    return result


def rewrite_jsonl(path: Path, kind: str) -> tuple[int, str, str]:
    before = sha256(path)
    records = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if kind == "translation":
        public = [sanitize_translation_record(path, record) for record in records]
    else:
        public = [sanitize_orthography_record(record) for record in records]
    path.write_text(
        "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in public),
        encoding="utf-8",
    )
    return len(public), before, sha256(path)


def rewrite_json(path: Path) -> tuple[str, str]:
    before = sha256(path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    public = sanitize_summary(payload)
    path.write_text(
        json.dumps(public, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return before, sha256(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Rewrite the repository's published model artifacts in place.",
    )
    args = parser.parse_args()
    if not args.apply:
        parser.error("This command changes published artifacts; pass --apply explicitly")

    manifest_path = PROJECT_ROOT / "results" / "public-artifacts.manifest.json"
    previous_source_hashes: dict[str, str] = {}
    if manifest_path.exists():
        previous = json.loads(manifest_path.read_text(encoding="utf-8"))
        previous_source_hashes = {
            entry["path"]: entry["private_source_sha256"]
            for entry in previous.get("artifacts", [])
        }

    entries: list[dict[str, Any]] = []
    for path in sorted((PROJECT_ROOT / "results" / "pilots").glob("*.jsonl")):
        count, source_hash, public_hash = rewrite_jsonl(path, "translation")
        entries.append(
            {
                "path": str(path.relative_to(PROJECT_ROOT)),
                "kind": "translation_scores",
                "records": count,
                "private_source_sha256": previous_source_hashes.get(
                    str(path.relative_to(PROJECT_ROOT)), source_hash
                ),
                "public_sha256": public_hash,
            }
        )
    for path in sorted((PROJECT_ROOT / "results" / "pilots").glob("*.summary.json")):
        source_hash, public_hash = rewrite_json(path)
        entries.append(
            {
                "path": str(path.relative_to(PROJECT_ROOT)),
                "kind": "translation_summary",
                "private_source_sha256": previous_source_hashes.get(
                    str(path.relative_to(PROJECT_ROOT)), source_hash
                ),
                "public_sha256": public_hash,
            }
        )
    for path in sorted((PROJECT_ROOT / "results" / "causal").glob("*.jsonl")):
        if path.name.startswith("orthography-control-relevance-full-v1"):
            continue
        count, source_hash, public_hash = rewrite_jsonl(path, "orthography")
        entries.append(
            {
                "path": str(path.relative_to(PROJECT_ROOT)),
                "kind": "orthography_scores",
                "records": count,
                "private_source_sha256": previous_source_hashes.get(
                    str(path.relative_to(PROJECT_ROOT)), source_hash
                ),
                "public_sha256": public_hash,
            }
        )
    for path in sorted((PROJECT_ROOT / "results" / "causal").glob("*.summary.json")):
        source_hash, public_hash = rewrite_json(path)
        entries.append(
            {
                "path": str(path.relative_to(PROJECT_ROOT)),
                "kind": "orthography_summary",
                "private_source_sha256": previous_source_hashes.get(
                    str(path.relative_to(PROJECT_ROOT)), source_hash
                ),
                "public_sha256": public_hash,
            }
        )
    for path in sorted((PROJECT_ROOT / "results" / "analysis").glob("*.json")):
        source_hash, public_hash = rewrite_json(path)
        entries.append(
            {
                "path": str(path.relative_to(PROJECT_ROOT)),
                "kind": "derived_analysis",
                "private_source_sha256": previous_source_hashes.get(
                    str(path.relative_to(PROJECT_ROOT)), source_hash
                ),
                "public_sha256": public_hash,
            }
        )

    manifest = {
        "schema": "public_artifact_manifest_v1",
        "export_date": date.today().isoformat(),
        "public_artifact_schema": SCHEMA,
        "upstream_commit": UPSTREAM_COMMIT,
        "join_key": "item_index",
        "benchmark_text_included": False,
        "private_source_sha256_definition": (
            "SHA-256 of the local complete run artifact before public redaction"
        ),
        "artifacts": entries,
    }
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"exported {len(entries)} scores-only artifacts")
    print(f"manifest: {manifest_path}")


if __name__ == "__main__":
    main()
