from __future__ import annotations

from typing import Any


def build_review_brain_readiness(
    *,
    parse_status: str | None,
    evidence_total: int,
    evidence_by_direction: dict[str, int] | None,
    promoted_memory_count: int,
    watch_memory_count: int,
    active_negative_count: int,
    positive_baseline_count: int,
    repeated_or_established_count: int,
) -> dict[str, Any]:
    direction_counts = evidence_by_direction or {}
    blockers: list[str] = []
    strengths: list[str] = []
    missing_structure: list[str] = []

    if parse_status in {None, "failed_zero_hands"}:
        blockers.append("parse_truth_missing")
    if evidence_total <= 0:
        blockers.append("session_evidence_missing")

    if evidence_total > 0:
        strengths.append("session_evidence_present")
    if direction_counts:
        strengths.append("evidence_direction_mix_present")
    if promoted_memory_count > 0:
        strengths.append("promoted_memory_present")
    if repeated_or_established_count > 0:
        strengths.append("cumulative_memory_present")
    if positive_baseline_count > 0:
        strengths.append("positive_baseline_present")
    if active_negative_count > 0:
        strengths.append("active_risk_present")

    if active_negative_count <= 0 and positive_baseline_count <= 0:
        missing_structure.append("state_contrast_for_standard_vs_unusual")
    if repeated_or_established_count <= 0:
        missing_structure.append("longitudinal_memory_maturity")
    if watch_memory_count > 0 and promoted_memory_count <= 0:
        missing_structure.append("promotion_ready_memory")

    readiness_score = 0.0
    readiness_score += 0.2 if evidence_total > 0 else 0.0
    readiness_score += 0.15 if direction_counts else 0.0
    readiness_score += 0.2 if promoted_memory_count > 0 else 0.0
    readiness_score += 0.2 if repeated_or_established_count > 0 else 0.0
    readiness_score += 0.125 if positive_baseline_count > 0 else 0.0
    readiness_score += 0.125 if active_negative_count > 0 else 0.0
    readiness_score = round(min(1.0, readiness_score), 3)

    if blockers:
        label = "blocked"
    elif readiness_score >= 0.75:
        label = "strong"
    elif readiness_score >= 0.45:
        label = "developing"
    else:
        label = "thin"

    return {
        "label": label,
        "score": readiness_score,
        "blockers": blockers,
        "strengths": strengths,
        "missing_structure": missing_structure,
    }
