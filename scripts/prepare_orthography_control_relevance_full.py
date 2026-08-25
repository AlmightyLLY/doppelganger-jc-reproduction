#!/usr/bin/env python3
"""Construct source-only controls for the full orthography intervention set.

The construction rule never reads model scores.  It first chooses a negative
control with a deterministic low-diagnosticity proxy, then chooses a distinct
local semantic cue.  Both are source-sentence spans containing kanji and are
converted to their contextual hiragana readings.

The automatic labels are an engineering approximation.  In particular,
``related_semantic_cue`` means locally coupled according to the frozen rule;
it is not a gold semantic-relation annotation.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any

import unidic_lite
from fugashi import Tagger

from prepare_orthography_causal_pilot import eligible_rows


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = (
    PROJECT_ROOT
    / "results"
    / "local"
    / "materials"
    / "orthography-control-relevance-full-v1.jsonl"
)
FROZEN_MATERIAL_CONFIG = PROJECT_ROOT / "configs" / "orthography_material_v1.json"

CONTENT_POS = {"名詞", "代名詞", "動詞", "形容詞", "形状詞", "副詞", "連体詞"}
CLAUSE_MARKS = {"、", "。", "！", "？", "!", "?", "；", ";"}

# These broad source-side classes are deliberately not tailored to any item.
# They only break ties toward conventional low-diagnosticity arguments.
GENERIC_PRONOUNS = {
    "彼", "彼女", "私", "僕", "我々", "われわれ", "自分", "誰", "何", "人", "者",
}
GENERIC_TIME_QUANTITY = {
    "今", "今日", "明日", "昨日", "今年", "去年", "前年", "来年", "朝", "昼", "夜",
    "晩", "今晩", "午前", "午後", "時間", "時", "日", "週", "月", "年", "一人", "二人",
}
GENERIC_PLACES_PARTICIPANTS = {
    "家", "学校", "会社", "店", "工場", "病院", "市場", "会議", "先生", "友人", "子供",
    "山", "駅", "空港", "公園", "部屋", "会場", "町", "都市", "国",
}
NUMERIC_COMPOUND_HEADS = {"年", "月", "日", "人", "回", "個", "本", "時", "分", "秒", "週間"}

RULE_VERSION = "source_only_rank_v1_20260825"
PURPOSE = "pre_outcome_control_relevance_full_v1"


def katakana_to_hiragana(text: str) -> str:
    chars: list[str] = []
    for char in text:
        codepoint = ord(char)
        chars.append(
            chr(codepoint - 0x60) if 0x30A1 <= codepoint <= 0x30F6 else char
        )
    return "".join(chars)


def contextual_reading(tagger: Tagger, sentence: str, span: str) -> str:
    """Return the contextual hiragana reading for one token-aligned span."""

    if sentence.count(span) != 1:
        raise ValueError("reading_span_not_unique")
    start = sentence.index(span)
    end = start + len(span)
    cursor = 0
    readings: list[str] = []
    covered_start: int | None = None
    covered_end: int | None = None
    for token in tagger(sentence):
        token_start = cursor
        token_end = cursor + len(token.surface)
        cursor = token_end
        if token_end <= start or token_start >= end:
            continue
        if token_start < start or token_end > end:
            raise ValueError("reading_span_not_token_aligned")
        if not token.feature.kana:
            raise ValueError("reading_missing")
        if covered_start is None:
            covered_start = token_start
        covered_end = token_end
        readings.append(token.feature.kana)
    if covered_start != start or covered_end != end or not readings:
        raise ValueError("reading_span_not_covered")
    return katakana_to_hiragana("".join(readings))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def contains_cjk(text: str) -> bool:
    return any("CJK UNIFIED IDEOGRAPH" in unicodedata.name(char, "") for char in text)


def all_cjk(text: str) -> bool:
    return bool(text) and all(
        "CJK UNIFIED IDEOGRAPH" in unicodedata.name(char, "") for char in text
    )


def load_previously_exposed_indices() -> set[int]:
    """Load the preregistered development-item union without outcome files.

    The former implementation reconstructed this set from two private scoring
    outputs.  Keeping the frozen index union in a text-free config makes the
    public material builder executable without redistributing those outcomes
    or benchmark sentences.
    """

    payload = json.loads(FROZEN_MATERIAL_CONFIG.read_text(encoding="utf-8"))
    indices = {int(index) for index in payload["previously_exposed_indices"]}
    if len(indices) != payload["previously_exposed_union_count"]:
        raise ValueError("Frozen exposed-index count does not match its config")
    return indices


def token_rows(tagger: Tagger, sentence: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    cursor = 0
    clause = 0
    for index, token in enumerate(tagger(sentence)):
        start = cursor
        end = start + len(token.surface)
        cursor = end
        rows.append(
            {
                "index": index,
                "surface": token.surface,
                "start": start,
                "end": end,
                "clause": clause,
                "pos1": token.feature.pos1,
                "pos2": token.feature.pos2,
                "pos3": token.feature.pos3,
                "lemma": token.feature.lemma or token.surface,
                "kana": token.feature.kana or "",
            }
        )
        if token.surface in CLAUSE_MARKS:
            clause += 1
    if cursor != len(sentence):
        raise ValueError(f"Tokenizer coverage mismatch: {sentence!r}")
    return rows


def generic_level(candidate: dict[str, Any]) -> int:
    surface = candidate["surface"]
    lemma = candidate["lemma"]
    if candidate["pos1"] == "代名詞" or surface in GENERIC_PRONOUNS or lemma in GENERIC_PRONOUNS:
        return 3
    if (
        candidate["pos2"] == "数詞"
        or surface in GENERIC_TIME_QUANTITY
        or lemma in GENERIC_TIME_QUANTITY
    ):
        return 2
    if surface in GENERIC_PLACES_PARTICIPANTS or lemma in GENERIC_PLACES_PARTICIPANTS:
        return 1
    return 0


def resolve_target_span(
    tokens: list[dict[str, Any]], sentence: str, target: str
) -> tuple[str, list[int], str]:
    target_start = sentence.index(target)
    target_end = target_start + len(target)
    target_indices = [
        token["index"]
        for token in tokens
        if token["end"] > target_start and token["start"] < target_end
    ]
    if not target_indices:
        raise ValueError("target_not_covered_by_tokenizer")
    first = tokens[target_indices[0]]
    last = tokens[target_indices[-1]]
    if first["start"] == target_start and last["end"] == target_end:
        return target, target_indices, "lexicon_span_exact"
    if len(target_indices) == 1 and first["start"] <= target_start and first["end"] >= target_end:
        intervention_span = first["surface"]
        if sentence.count(intervention_span) != 1:
            raise ValueError("expanded_target_token_not_unique")
        return intervention_span, target_indices, "expanded_to_contextual_token"
    raise ValueError("target_not_aligned_to_token_boundaries")


def extract_candidates(
    tagger: Tagger, sentence: str, target: str
) -> tuple[list[dict[str, Any]], list[int], str, str]:
    tokens = token_rows(tagger, sentence)
    intervention_span, target_indices, target_span_rule = resolve_target_span(
        tokens, sentence, target
    )
    target_clauses = {tokens[index]["clause"] for index in target_indices}
    target_mid = sum(target_indices) / len(target_indices)

    candidates: list[dict[str, Any]] = []
    for token in tokens:
        if token["index"] in target_indices:
            continue
        if token["pos1"] not in CONTENT_POS or not contains_cjk(token["surface"]):
            continue
        span_tokens = [token]
        next_index = token["index"] + 1
        while next_index < len(tokens):
            following = tokens[next_index]
            suffix_extension = following["pos1"] == "接尾辞"
            numeric_extension = (
                token["pos2"] == "数詞"
                and following["surface"] in NUMERIC_COMPOUND_HEADS
            )
            if (
                not (suffix_extension or numeric_extension)
                or following["clause"] != token["clause"]
            ):
                break
            if following["index"] in target_indices or not contains_cjk(following["surface"]):
                break
            span_tokens.append(following)
            next_index += 1
        surface = sentence[span_tokens[0]["start"] : span_tokens[-1]["end"]]
        if sentence.count(surface) != 1 or not token["kana"]:
            continue
        reading = contextual_reading(tagger, sentence, surface)
        if reading == surface:
            continue
        span_indices = [span_token["index"] for span_token in span_tokens]
        distance = min(
            abs(span_index - target_index)
            for span_index in span_indices
            for target_index in target_indices
        )
        same_clause = token["clause"] in target_clauses
        candidate = dict(token)
        candidate.update(
            {
                "surface": surface,
                "token_indices": span_indices,
                "reading": reading,
                "distance": distance,
                "same_clause": same_clause,
                "generic_level": generic_level(token),
                "all_cjk": all_cjk(surface),
                "surface_length_delta": abs(len(surface) - len(target)),
                "reading_length_delta": 0,
                "side": "left" if token["index"] < target_mid else "right",
            }
        )
        candidates.append(candidate)
    return candidates, target_indices, intervention_span, target_span_rule


def unrelated_key(candidate: dict[str, Any]) -> tuple[Any, ...]:
    """Higher tuple is preferred; semantic independence proxies come first."""

    predicate = candidate["pos1"] in {"動詞", "形容詞", "形状詞"} or candidate[
        "pos2"
    ] == "サ変可能" or candidate["pos3"] == "サ変可能"
    independence_score = (
        2 * candidate["generic_level"]
        + int(not predicate)
        - (4 if candidate["distance"] == 1 else 0)
    )
    return (
        independence_score,
        int(candidate["distance"] > 1),
        candidate["generic_level"],
        int(not predicate),
        int(not candidate["same_clause"]),
        candidate["distance"],
        int(candidate["all_cjk"]),
        -candidate["surface_length_delta"],
        -candidate["index"],
        candidate["surface"],
    )


def related_key(candidate: dict[str, Any]) -> tuple[Any, ...]:
    """Higher tuple is preferred; local contextual coupling proxies come first."""

    predicate = candidate["pos1"] in {"動詞", "形容詞", "形状詞"} or candidate[
        "pos2"
    ] == "サ変可能" or candidate["pos3"] == "サ変可能"
    return (
        int(predicate),
        int(candidate["same_clause"]),
        -candidate["distance"],
        -candidate["generic_level"],
        int(candidate["all_cjk"]),
        -candidate["surface_length_delta"],
        -candidate["index"],
        candidate["surface"],
    )


def candidate_audit(candidate: dict[str, Any]) -> dict[str, Any]:
    return {
        key: candidate[key]
        for key in (
            "surface",
            "reading",
            "index",
            "token_indices",
            "clause",
            "pos1",
            "pos2",
            "pos3",
            "lemma",
            "distance",
            "same_clause",
            "generic_level",
            "all_cjk",
            "surface_length_delta",
            "side",
        )
    }


def unrelated_quality_proxy(candidate: dict[str, Any]) -> str:
    predicate = candidate["pos1"] in {"動詞", "形容詞", "形状詞"} or candidate[
        "pos3"
    ] == "サ変可能"
    if (
        (candidate["generic_level"] >= 2 and candidate["distance"] >= 2)
        or (candidate["generic_level"] >= 1 and candidate["distance"] >= 3)
        or (not candidate["same_clause"] and candidate["distance"] >= 3)
    ):
        return "high"
    if candidate["distance"] >= 2 and not predicate:
        return "medium"
    return "weak"


def build_material() -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    tagger = Tagger()
    eligible, dataset_excluded = eligible_rows()
    exposed = load_previously_exposed_indices()
    rows: list[dict[str, Any]] = []
    control_excluded: list[dict[str, Any]] = []
    candidate_counts: Counter[int] = Counter()

    for source in eligible:
        index = int(source["item_index"])
        original = source["original"]
        target = source["japanese_word"]
        try:
            (
                candidates,
                target_token_indices,
                target_intervention_span,
                target_span_rule,
            ) = extract_candidates(tagger, original, target)
            target_reading = contextual_reading(
                tagger, original, target_intervention_span
            )
        except ValueError as error:
            control_excluded.append({**source, "exclusion_reason": str(error)})
            continue
        candidate_counts[len(candidates)] += 1
        if not candidates:
            control_excluded.append(
                {
                    **source,
                    "exclusion_reason": "no_non_target_kanji_control",
                    "candidate_count": len(candidates),
                    "candidate_spans": [candidate["surface"] for candidate in candidates],
                }
            )
            continue

        unrelated = max(candidates, key=unrelated_key)
        related_pool = [
            candidate for candidate in candidates if candidate["surface"] != unrelated["surface"]
        ]
        related = max(related_pool, key=related_key) if related_pool else None
        row = {
            "item_index": index,
            "word": source["word"],
            "japanese_word": target,
            "surface_exact": bool(source["surface_exact"]),
            "previously_exposed_causal_item": index in exposed,
            "original": original,
            "target_intervention_span": target_intervention_span,
            "target_span_rule": target_span_rule,
            "target_reading": target_reading,
            "target_kana_sentence": original.replace(
                target_intervention_span, target_reading, 1
            ),
            "unrelated_control_word": unrelated["surface"],
            "unrelated_control_reading": unrelated["reading"],
            "unrelated_control_kana_sentence": original.replace(
                unrelated["surface"], unrelated["reading"], 1
            ),
            "related_semantic_cue_word": related["surface"] if related else None,
            "related_semantic_cue_reading": related["reading"] if related else None,
            "related_semantic_cue_kana_sentence": (
                original.replace(related["surface"], related["reading"], 1)
                if related
                else None
            ),
            "candidate_control_count": len(candidates),
            "target_token_indices": target_token_indices,
            "unrelated_control_audit": candidate_audit(unrelated),
            "unrelated_control_quality_proxy": unrelated_quality_proxy(unrelated),
            "related_semantic_cue_audit": candidate_audit(related) if related else None,
            "selection_rule": RULE_VERSION,
            "purpose": PURPOSE,
            "review_status": (
                "deterministic_source_only_agent_rule; no independent bilingual review"
            ),
        }
        rows.append(row)

    rows.sort(key=lambda row: row["item_index"])
    excluded = [
        {**row, "exclusion_stage": "dataset_preselection"} for row in dataset_excluded
    ] + [
        {**row, "exclusion_stage": "control_construction"} for row in control_excluded
    ]
    excluded.sort(key=lambda row: row["item_index"])
    metadata = {
        "dataset_question_count": len(eligible) + len(dataset_excluded),
        "dataset_preeligible_count": len(eligible),
        "dataset_preexcluded_count": len(dataset_excluded),
        "negative_control_included_count": len(rows),
        "four_condition_subset_count": sum(
            row["related_semantic_cue_word"] is not None for row in rows
        ),
        "control_construction_excluded_count": len(control_excluded),
        "previously_exposed_union_count": len(exposed),
        "previously_exposed_indices": sorted(exposed),
        "negative_control_confirmatory_holdout_count": sum(
            not row["previously_exposed_causal_item"] for row in rows
        ),
        "four_condition_confirmatory_holdout_count": sum(
            not row["previously_exposed_causal_item"]
            and row["related_semantic_cue_word"] is not None
            for row in rows
        ),
        "surface_exact_included": sum(row["surface_exact"] for row in rows),
        "surface_variant_included": sum(not row["surface_exact"] for row in rows),
        "target_span_rule_distribution": dict(
            Counter(row["target_span_rule"] for row in rows)
        ),
        "unrelated_control_quality_proxy_distribution": dict(
            Counter(row["unrelated_control_quality_proxy"] for row in rows)
        ),
        "candidate_count_distribution": dict(sorted(candidate_counts.items())),
        "dataset_exclusion_reasons": dict(
            Counter(
                reason
                for row in dataset_excluded
                for reason in row["preselection_exclusion"].split(";")
            )
        ),
        "control_exclusion_reasons": dict(
            Counter(row["exclusion_reason"] for row in control_excluded)
        ),
    }
    return rows, excluded, metadata


def atomic_write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--audit-only", action="store_true")
    args = parser.parse_args()

    rows, excluded, metadata = build_material()
    print(json.dumps(metadata, ensure_ascii=False, indent=2))
    if args.audit_only:
        return

    output = args.output.resolve()
    exclusions = output.with_name(output.stem + ".excluded.jsonl")
    manifest = output.with_suffix(".manifest.json")
    if output.exists() or exclusions.exists() or manifest.exists():
        raise FileExistsError("Refusing to overwrite frozen full-set material outputs")
    output.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_jsonl(output, rows)
    atomic_write_jsonl(exclusions, excluded)
    manifest_payload = {
        "status": "frozen_before_full_control_relevance_treatment_scoring",
        "rule_version": RULE_VERSION,
        "purpose": PURPOSE,
        "selection_inputs": "source sentence, target span, fugashi morphology only",
        "model_outputs_used_for_control_selection": False,
        "independent_bilingual_second_review": False,
        "scoring_authorized_by_user": True,
        "fugashi_version": importlib.metadata.version("fugashi"),
        "unidic_lite_version": importlib.metadata.version("unidic-lite"),
        "unidic_directory": str(Path(unidic_lite.DICDIR).resolve()),
        **metadata,
        "material_path": str(output),
        "material_sha256": sha256(output),
        "exclusions_path": str(exclusions),
        "exclusions_sha256": sha256(exclusions),
    }
    frozen = json.loads(FROZEN_MATERIAL_CONFIG.read_text(encoding="utf-8"))
    expected_material_hash = frozen["expected_material_sha256"]
    expected_exclusions_hash = frozen["expected_exclusions_sha256"]
    if manifest_payload["material_sha256"] != expected_material_hash:
        raise RuntimeError(
            "Generated material does not match the frozen SHA-256. Check the "
            "pinned upstream commit and morphology package versions."
        )
    if manifest_payload["exclusions_sha256"] != expected_exclusions_hash:
        raise RuntimeError("Generated exclusions do not match the frozen SHA-256")
    temporary = manifest.with_name(manifest.name + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(manifest_payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, manifest)
    print(f"material: {output}")
    print(f"material sha256: {manifest_payload['material_sha256']}")
    print(f"exclusions: {exclusions}")
    print(f"manifest: {manifest}")


if __name__ == "__main__":
    main()
