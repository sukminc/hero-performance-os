from __future__ import annotations

from typing import Any


def build_review_hook(
    *,
    target_type: str,
    target_id: str,
    review_type: str,
    overlay_slot: str,
    review_count: int = 0,
    latest_decision: str | None = None,
) -> dict[str, Any]:
    return {
        "target_type": target_type,
        "target_id": target_id,
        "review_type": review_type,
        "overlay_slot": overlay_slot,
        "review_count": review_count,
        "latest_decision": latest_decision,
        "canonical_truth_policy": "immutable_source_truth_separate_review_overlay",
    }


def build_reviewed_overlay(
    *,
    target_type: str,
    target_id: str,
    review_type: str,
    reviews: list[dict[str, Any]],
) -> dict[str, Any] | None:
    if not reviews:
        return None
    latest = reviews[0]
    return {
        "target_type": target_type,
        "target_id": target_id,
        "review_type": review_type,
        "decision": latest.get("decision"),
        "notes": latest.get("notes"),
        "review_payload": latest.get("review_payload") or {},
        "created_at": latest.get("created_at"),
        "canonical_truth_policy": "immutable_source_truth_separate_review_overlay",
    }
