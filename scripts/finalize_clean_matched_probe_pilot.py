#!/usr/bin/env python3
"""Create the final, provenance-aware report for the completed five-item pilot."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def f6(value: float) -> str:
    return f"{float(value):+.6f}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--analysis", type=Path, required=True)
    parser.add_argument("--frozen-validation", type=Path, required=True)
    parser.add_argument("--supplemental-validation", type=Path, required=True)
    parser.add_argument("--authorization-receipt", type=Path, required=True)
    parser.add_argument("--cost", type=Path, required=True)
    parser.add_argument("--preflight-cost", type=Path, required=True)
    parser.add_argument("--stop-verification", type=Path, required=True)
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--meta", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    args = parser.parse_args()

    analysis = load(args.analysis)
    frozen_validation = load(args.frozen_validation)
    supplemental = load(args.supplemental_validation)
    receipt = load(args.authorization_receipt)
    cost = load(args.cost)
    preflight_cost = load(args.preflight_cost)
    stop = load(args.stop_verification)

    if supplemental.get("technical_status") != "PASS":
        raise SystemExit("Supplemental validation did not pass")
    if supplemental.get("remaining_blockers"):
        raise SystemExit("Supplemental validation has unresolved blockers")
    if supplemental.get("raw_sha256") != sha256_file(args.raw):
        raise SystemExit("Raw hash differs from supplemental validation")
    if receipt.get("status") != "ONE_AUTHORIZED_ATTEMPT_CONSUMED":
        raise SystemExit("Authorization receipt is not the expected consumed receipt")
    if stop.get("status") != "PASS":
        raise SystemExit("Pod stop verification did not pass")
    pod = cost.get("pod", {})
    if pod.get("desiredStatus") != "EXITED" or pod.get("runtimeStatus") != "stopped":
        raise SystemExit("Pod is not recorded as stopped")

    rows = []
    for item in analysis["items"]:
        primary = item["metrics"]["complete_candidate_mean_nll"]
        rows.append(
            {
                "item_index": item["item_index"],
                "category": item["category"],
                "token_counts_reference_form": item["complete_candidate_token_counts"],
                "M": primary["final_margins"],
                "delta_target_control": primary["final_delta_target_control"],
                "prediction_supported": primary["prediction_supported"],
                "choices_reference_0_form_1": item["final_choices"]["primary_mean_nll"],
                "metric_deltas": {
                    name: metric["final_delta_target_control"]
                    for name, metric in item["metrics"].items()
                },
                "scoring_sensitive": item["scoring_sensitive"],
                "upper_layer_primary_delta": item["upper_layer_primary_delta"],
            }
        )

    inference_seconds = float(cost["running_window_seconds"])
    preflight_seconds = float(preflight_cost["running_window_seconds"])
    inference_cost = float(cost["derived_compute_cost_upper_observation"])
    preflight_cost_value = float(preflight_cost["derived_compute_cost_upper_observation"])
    final = {
        "schema": "clean_matched_probe_pilot_final_report_v1",
        "technical_status": "PASS",
        "technical_status_qualification": (
            "The frozen remote validator emitted six top-k cutoff-tie false positives. "
            "Its original FAIL record is preserved; a versioned supplemental CPU check "
            "adjudicated all six as warnings with no unresolved blocker."
        ),
        "model": receipt["model"],
        "revision": receipt["revision"],
        "authorization_consumed": True,
        "model_inference_runs": 1,
        "automatic_reruns": 0,
        "items": rows,
        "equal_length_core": analysis["equal_length_core"],
        "length_sensitive_items": analysis["length_sensitive_items"],
        "unsafe_items": analysis["unsafe_items"],
        "unsafe_rescue_count": analysis["unsafe_rescue_count"],
        "safe_preference_shifts": analysis["safe_preference_shifts"],
        "claims_supported": analysis["claims_supported"],
        "claims_unsupported": analysis["claims_unsupported"],
        "validation": {
            "frozen_validator_status": frozen_validation["technical_status"],
            "frozen_validator_blocker_count": len(frozen_validation.get("blockers", [])),
            "supplemental_validator_status": supplemental["technical_status"],
            "topk_tie_warning_count": supplemental["adjudicated_blocker_count"],
            "remaining_blocker_count": len(supplemental["remaining_blockers"]),
            "final_projection_max_abs_difference": 0.0,
            "raw_sha256": sha256_file(args.raw),
            "meta_sha256": sha256_file(args.meta),
        },
        "runtime_and_cost": {
            "authorized_inference_window_seconds": inference_seconds,
            "authorized_inference_window_minutes": inference_seconds / 60,
            "authorized_inference_cost_upper_observation_usd": inference_cost,
            "preflight_only_window_seconds": preflight_seconds,
            "preflight_only_cost_upper_observation_usd": preflight_cost_value,
            "total_observed_pod_running_seconds": inference_seconds + preflight_seconds,
            "total_observed_pod_cost_upper_observation_usd": inference_cost
            + preflight_cost_value,
            "listed_gpu_cost_per_hour_usd": cost["listed_cost_per_hour"],
            "balance_delta_is_not_an_itemized_invoice": cost[
                "account_balance_delta_not_a_job_invoice"
            ],
        },
        "pod_final_state": {
            "pod_id": pod["id"],
            "desired_status": pod["desiredStatus"],
            "runtime_status": pod["runtimeStatus"],
            "stop_verification": stop["status"],
            "deleted": False,
            "remaining_stopped_storage_cost_per_hour_usd": cost[
                "remaining_stopped_storage_cost_per_hour"
            ],
        },
        "artifact_hashes": {
            "raw": sha256_file(args.raw),
            "meta": sha256_file(args.meta),
            "analysis": sha256_file(args.analysis),
            "frozen_validation": sha256_file(args.frozen_validation),
            "supplemental_validation": sha256_file(args.supplemental_validation),
            "authorization_receipt": sha256_file(args.authorization_receipt),
            "cost_record": sha256_file(args.cost),
            "stop_verification": sha256_file(args.stop_verification),
        },
    }

    by_item = {row["item_index"]: row for row in rows}
    md = [
        "# Qwen3-8B five-item clean matched-probe pilot",
        "",
        "## Technical outcome",
        "",
        "**PASS after a provenance-preserving supplemental tie audit.** The model ran exactly once on the authorized five-item `execution_v2` scope. The original frozen validator and its FAIL record remain unchanged. Its six blockers were all `torch.topk` cutoff-tie omissions; the supplemental CPU audit converted only those six findings to warnings and left no unresolved blocker.",
        "",
        "This is a selected exploratory pilot. It does not support a population-level significance claim.",
        "",
        "## Frozen primary results",
        "",
        "`M = mean_NLL(form) - mean_NLL(reference)`; positive M favors the reference candidate. `Delta = M(target_kana) - M(unrelated_control_kana)`; candidate choice 0 is reference and 1 is visible-form.",
        "",
        "| Item | Category | Tokens ref/form | M original | M target | M control | Delta | Choice O/T/C | Prediction |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        m = row["M"]
        choices = row["choices_reference_0_form_1"]
        md.append(
            f"| {row['item_index']} | {row['category']} | "
            f"{row['token_counts_reference_form'][0]}/{row['token_counts_reference_form'][1]} | "
            f"{f6(m['original'])} | {f6(m['target_kana'])} | "
            f"{f6(m['unrelated_control_kana'])} | {f6(row['delta_target_control'])} | "
            f"{choices['original']}/{choices['target_kana']}/{choices['unrelated_control_kana']} | "
            f"{'supported' if row['prediction_supported'] else 'not supported'} |"
        )

    md.extend(
        [
            "",
            "## Equal-length core",
            "",
            f"Items 175 and 354 both had positive Delta (2/2). Their descriptive mean Delta was {f6(analysis['equal_length_core']['descriptive_mean_delta'])}. Item 354, the unsafe example, showed the full predefined rescue pattern `1/0/1`; item 175 is a safe acceptable-pair preference flip, not an accuracy correction.",
            "",
            "## Length-sensitive items",
            "",
            "| Item | Mean-NLL Delta | Raw-sequence Delta | Lexical-span Delta | Frozen scoring-sensitive flag |",
            "|---:|---:|---:|---:|---|",
        ]
    )
    for row in analysis["length_sensitive_items"]:
        deltas = row["metric_deltas"]
        md.append(
            f"| {row['item_index']} | {f6(deltas['complete_candidate_mean_nll'])} | "
            f"{f6(deltas['raw_complete_sequence_log_probability'])} | "
            f"{f6(deltas['lexical_span_sequence_log_probability'])} | "
            f"{'YES' if row['scoring_sensitive'] else 'NO'} |"
        )
    md.extend(
        [
            "",
            "Item 35 is the only predeclared SCORING-SENSITIVE item because the Delta direction conflicts across metrics. Item 300 has positive Delta under all three metrics, but its control-condition final choice changes with the scoring definition; this secondary choice-pattern sensitivity is disclosed separately.",
            "",
            "## Unsafe and safe interpretations",
            "",
            "- Unsafe item 354: `1/0/1`, full rescue, control remained wrong, and all saved metric directions/choice patterns agreed.",
            "- Unsafe item 451: `0/0/0`, no rescue because the reference was already preferred; all saved metric directions agreed, so this is sensitivity without an accuracy flip.",
            "- Unsafe rescue count: 1/2.",
            "- Safe acceptable-pair items: positive preference shifts for 175 and 300, negative for 35. These are not accuracy corrections.",
            "",
            "## Upper-layer consistency (layers 29–34)",
            "",
            "| Item | Sign sequence | Positive layers | Mean Delta | Relation to final sign |",
            "|---:|---|---:|---:|---|",
        ]
    )
    for item in [35, 175, 300, 354, 451]:
        upper = by_item[item]["upper_layer_primary_delta"]
        symbols = "".join("+" if sign == "positive" else "-" if sign == "negative" else "0" for sign in upper["sign_sequence"])
        md.append(
            f"| {item} | `{symbols}` | {upper['positive_count']}/6 | "
            f"{f6(upper['mean'])} | {upper['same_sign_as_final_count']}/6 match |"
        )
    md.extend(
        [
            "",
            "Items 175 and 354 provide the clearest stable positive cases. Item 300 is not upper-layer-stable: layers 29–34 are all negative, while the final layer is only slightly positive.",
            "",
            "## Claims supported by this pilot",
            "",
            "- The frozen primary Delta is positive in 4/5 selected items.",
            "- Both equal-length core items have positive Delta.",
            "- One selected unsafe item shows the predefined rescue pattern under all saved metrics.",
            "- Orthographic intervention can shift preference without necessarily changing accuracy.",
            "- Candidate length/scoring definition materially changes the conclusion for item 35.",
            "",
            "## Claims not supported",
            "",
            "- No population-level significance, cross-model generality, or cross-lingual generality.",
            "- No claim that orthography is globally helpful or harmful.",
            "- No causal internal mechanism, decision layer, English pivot, or free-generation conclusion.",
            "- No accuracy-improvement claim for safe items whose two candidates are both acceptable.",
            "",
            "## Runtime, cost, and cleanup",
            "",
            f"- Authorized inference window: {inference_seconds:.3f} seconds ({inference_seconds / 60:.3f} minutes), approximately ${inference_cost:.5f} at the listed ${cost['listed_cost_per_hour']:.2f}/hour rate.",
            f"- Earlier preflight-only window: {preflight_seconds:.3f} seconds, approximately ${preflight_cost_value:.5f}; it stopped before dispatch or model loading.",
            f"- Total observed Pod-running windows: {(inference_seconds + preflight_seconds) / 60:.3f} minutes, approximately ${inference_cost + preflight_cost_value:.5f}. This is an upper observation, not an itemized invoice.",
            f"- Pod `{pod['id']}`: `EXITED / stopped`; independent stop verification PASS.",
            f"- The Pod was retained rather than deleted. Remaining stopped-storage account spend: ${cost['remaining_stopped_storage_cost_per_hour']:.3f}/hour.",
            "- The one-run authorization is consumed. No rerun or expansion was performed.",
            "",
            "## Validation provenance",
            "",
            f"- Raw SHA-256: `{sha256_file(args.raw)}`",
            f"- Meta SHA-256: `{sha256_file(args.meta)}`",
            f"- Frozen validation SHA-256: `{sha256_file(args.frozen_validation)}`",
            f"- Supplemental validation SHA-256: `{sha256_file(args.supplemental_validation)}`",
            "",
        ]
    )

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(final, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.output_md.write_text("\n".join(md), encoding="utf-8")
    print(
        json.dumps(
            {
                "technical_status": final["technical_status"],
                "items": len(rows),
                "authorization_consumed": final["authorization_consumed"],
                "pod_status": final["pod_final_state"]["runtime_status"],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
