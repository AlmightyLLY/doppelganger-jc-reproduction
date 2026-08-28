#!/usr/bin/env python3
"""Adjudicate only top-k cutoff-tie blockers from the frozen pilot validator.

This is a post-run supplemental check. It does not replace or modify the
frozen validator, raw model output, or preregistered analysis. A missing gold
token is downgraded to a warning only when its score is exactly tied with the
top-k cutoff and its stored competition rank is otherwise reproducible.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any


TOPK = 50
TIE_TOLERANCE = 1e-7
FIELD_PATTERN = re.compile(
    r"item\[(?P<item>\d+)\]\."
    r"(?P<condition>[^.]+)\.candidate\[(?P<candidate>\d+)\]\."
    r"readout\[(?P<layer>\d+)\]\[(?P<token>\d+)\]"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def locate_token_row(
    raw_by_item: dict[int, dict[str, Any]], field: str
) -> tuple[dict[str, Any], dict[str, Any], dict[str, int | str]]:
    match = FIELD_PATTERN.fullmatch(field)
    if match is None:
        raise ValueError(f"Unrecognized blocker field: {field}")
    location: dict[str, int | str] = {
        "item": int(match.group("item")),
        "condition": match.group("condition"),
        "candidate": int(match.group("candidate")),
        "layer": int(match.group("layer")),
        "token": int(match.group("token")),
    }
    item_row = raw_by_item[int(location["item"])]
    candidate = item_row["conditions"][str(location["condition"])]["candidates"][
        int(location["candidate"])
    ]
    token_row = candidate["full_vocabulary_readout"]["layers"][
        int(location["layer"])
    ]["tokens"][int(location["token"])]
    return candidate, token_row, location


def adjudicate_tie(
    raw_by_item: dict[int, dict[str, Any]], blocker: dict[str, Any]
) -> dict[str, Any]:
    field = blocker.get("field")
    if blocker.get("code") != "gold_token_missing_or_duplicated_in_topk":
        return {
            "field": field,
            "adjudication": "UNRESOLVED_NON_TIE_BLOCKER",
            "passed": False,
        }
    try:
        candidate, token_row, location = locate_token_row(raw_by_item, str(field))
    except (KeyError, IndexError, TypeError, ValueError) as error:
        return {
            "field": field,
            "adjudication": "UNRESOLVED_LOCATION_ERROR",
            "error": str(error),
            "passed": False,
        }

    topk = token_row.get("topk", [])
    gold_id = token_row.get("gold_token_id")
    gold_rank = token_row.get("gold_vocabulary_rank")
    gold_logp = token_row.get("gold_log_probability")
    if (
        len(topk) != TOPK
        or not isinstance(gold_id, int)
        or not isinstance(gold_rank, int)
        or not isinstance(gold_logp, (int, float))
        or not math.isfinite(float(gold_logp))
    ):
        return {
            "field": field,
            "adjudication": "UNRESOLVED_MALFORMED_ROW",
            "passed": False,
        }

    topk_ids = [row.get("token_id") for row in topk]
    topk_logps = [float(row.get("log_probability")) for row in topk]
    unique_ids = len(set(topk_ids)) == TOPK
    descending = all(
        left >= right for left, right in zip(topk_logps, topk_logps[1:])
    )
    gold_occurrences = sum(token_id == gold_id for token_id in topk_ids)
    strictly_higher = sum(value > float(gold_logp) for value in topk_logps)
    cutoff_logp = topk_logps[-1]
    cutoff_tied = math.isclose(
        cutoff_logp,
        float(gold_logp),
        rel_tol=TIE_TOLERANCE,
        abs_tol=TIE_TOLERANCE,
    )
    rank_reproduced = strictly_higher + 1 == gold_rank
    passed = (
        unique_ids
        and descending
        and gold_occurrences == 0
        and gold_rank <= TOPK
        and rank_reproduced
        and cutoff_tied
    )
    return {
        "field": field,
        "item_index": location["item"],
        "condition": location["condition"],
        "candidate_index": location["candidate"],
        "layer_index": location["layer"],
        "token_index": location["token"],
        "gold_token_id": gold_id,
        "gold_token_piece": candidate["tokens"][int(location["token"])],
        "gold_competition_rank": gold_rank,
        "gold_log_probability": float(gold_logp),
        "topk_cutoff_log_probability": cutoff_logp,
        "strictly_higher_topk_count": strictly_higher,
        "gold_occurrences_in_topk": gold_occurrences,
        "topk_ids_unique": unique_ids,
        "topk_log_probabilities_descending": descending,
        "cutoff_exactly_tied_with_gold": cutoff_tied,
        "competition_rank_reproduced": rank_reproduced,
        "adjudication": (
            "TOPK_BOUNDARY_TIE_OMISSION_WARNING"
            if passed
            else "UNRESOLVED_TOPK_INCONSISTENCY"
        ),
        "passed": passed,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--frozen-validation", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    raw = load_jsonl(args.raw)
    frozen = json.loads(args.frozen_validation.read_text(encoding="utf-8"))
    raw_by_item = {int(row["item_index"]): row for row in raw}
    adjudications = [
        adjudicate_tie(raw_by_item, blocker)
        for blocker in frozen.get("blockers", [])
    ]
    unresolved = [row for row in adjudications if not row.get("passed")]
    output = {
        "schema": "clean_matched_probe_topk_tie_adjudication_v1",
        "technical_status": "PASS" if not unresolved else "FAIL",
        "scope": "supplemental_postrun_validation_only",
        "frozen_validator_status_preserved": frozen.get("technical_status"),
        "frozen_validator_sha256": sha256_file(args.frozen_validation),
        "raw_sha256": sha256_file(args.raw),
        "raw_model_output_modified": False,
        "model_rerun_performed": False,
        "adjudicated_blocker_count": len(adjudications),
        "topk_boundary_tie_warnings": adjudications,
        "remaining_blockers": unresolved,
        "inherited_nonblocking_warnings": frozen.get("warnings", []),
        "interpretation": (
            "All frozen-validator blockers were top-k cutoff-tie omissions; "
            "all other frozen checks passed."
            if not unresolved
            else "At least one frozen-validator blocker was not explained by a cutoff tie."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "technical_status": output["technical_status"],
                "adjudicated": len(adjudications),
                "remaining_blockers": len(unresolved),
            },
            ensure_ascii=False,
        )
    )
    raise SystemExit(0 if not unresolved else 1)


if __name__ == "__main__":
    main()
