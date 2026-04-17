from __future__ import annotations

from typing import Any

from core.storage.repositories import V2Repository
from core.surfaces.interpretation_groundwork import build_review_brain_readiness
from core.surfaces.interpretation_summary import build_interpretation_summary
from core.surfaces.pattern_progress import build_pattern_progress_summary
from core.surfaces.review_hooks import build_review_hook, build_reviewed_overlay
from core.surfaces.today import build_today_surface


def _top_memory_items(memory_items: list[dict[str, Any]], limit: int = 5) -> list[dict[str, Any]]:
    return [
        {
            "id": item.get("id"),
            "memory_type": item.get("memory_type"),
            "memory_key": item.get("memory_key"),
            "status": item.get("status"),
            "confidence": item.get("confidence"),
            "summary": item.get("summary"),
            "suggested_adjustment": item.get("suggested_adjustment"),
            "evidence_count": item.get("evidence_count"),
        }
        for item in memory_items[:limit]
    ]


def build_command_center_payload(
    repository: V2Repository,
    player_id: str,
    rebuild_today: bool = False,
) -> dict[str, Any]:
    latest_session_id = repository.fetch_latest_session_id(player_id)
    latest_today_snapshot = repository.fetch_latest_surface_snapshot(player_id, "today")

    if rebuild_today or not latest_today_snapshot:
        today_surface = build_today_surface(repository, player_id=player_id, session_id=latest_session_id)
        today_payload = {
            "player_id": today_surface.player_id,
            "current_state": today_surface.current_state,
            "headline": today_surface.headline,
            "adjustments": [
                {
                    "label": adjustment.label,
                    "reason": adjustment.reason,
                    "confidence": adjustment.confidence,
                    "memory_id": adjustment.memory_id,
                }
                for adjustment in today_surface.adjustments
            ],
            "supporting_memory": today_surface.supporting_memory,
            "confidence_summary": today_surface.confidence_summary,
        }
        today_meta = {
            "source": "rebuilt" if rebuild_today else "rebuilt_missing_snapshot",
            "session_id": latest_session_id,
        }
    else:
        today_payload = dict(latest_today_snapshot["payload"])
        today_payload["confidence_summary"] = latest_today_snapshot.get("confidence_summary") or {}
        today_meta = {
            "source": "snapshot",
            "snapshot_id": latest_today_snapshot.get("id"),
            "generated_at": latest_today_snapshot.get("generated_at"),
            "session_id": latest_today_snapshot.get("session_id"),
        }

    memory_items = repository.fetch_memory_items(player_id, statuses=["active", "baseline", "watch"])
    latest_session_memory_items = (
        repository.fetch_memory_items_for_session(player_id, latest_session_id) if latest_session_id else []
    )
    top_memory = _top_memory_items(memory_items)
    confidence_values = [float(item.get("confidence") or 0.0) for item in memory_items]
    average_confidence = round(sum(confidence_values) / len(confidence_values), 3) if confidence_values else 0.0
    active_negative_count = sum(
        1
        for item in memory_items
        if item.get("status") == "active"
        and str((item.get("memory_payload") or {}).get("direction") or "") == "negative"
    )
    positive_baseline_count = sum(
        1
        for item in memory_items
        if item.get("status") == "baseline"
        and str((item.get("memory_payload") or {}).get("direction") or "") == "positive"
    )
    repeated_or_established_count = sum(
        1
        for item in memory_items
        if str((item.get("memory_payload") or {}).get("maturity") or "") in {"repeated", "established"}
    )
    interpretation_groundwork = build_review_brain_readiness(
        parse_status="success" if latest_session_id else "failed_zero_hands",
        evidence_total=len(memory_items),
        evidence_by_direction={
            "positive": sum(1 for item in memory_items if str((item.get("memory_payload") or {}).get("direction") or "") == "positive"),
            "negative": sum(1 for item in memory_items if str((item.get("memory_payload") or {}).get("direction") or "") == "negative"),
            "shift": sum(1 for item in memory_items if str((item.get("memory_payload") or {}).get("direction") or "") == "shift"),
        },
        promoted_memory_count=sum(1 for item in memory_items if item.get("status") in {"active", "baseline"}),
        watch_memory_count=sum(1 for item in memory_items if item.get("status") == "watch"),
        active_negative_count=active_negative_count,
        positive_baseline_count=positive_baseline_count,
        repeated_or_established_count=repeated_or_established_count,
    )
    interpretation_summary = build_interpretation_summary(memory_items)
    pattern_progress = build_pattern_progress_summary(memory_items, latest_session_memory_items)
    interpretation_reviews = repository.fetch_operator_reviews(
        target_type="player",
        target_id=player_id,
        review_type="command_center_interpretation_assessment",
    )
    reviewed_interpretation_overlay = build_reviewed_overlay(
        target_type="player",
        target_id=player_id,
        review_type="command_center_interpretation_assessment",
        reviews=interpretation_reviews,
    )

    return {
        "player_id": player_id,
        "current_state": today_payload.get("current_state", "unclear"),
        "headline": today_payload.get("headline", "Today is not yet available."),
        "today": today_payload,
        "top_memory": top_memory,
        "interpretation_summary": interpretation_summary,
        "pattern_progress": pattern_progress,
        "reviewed_overlays": {
            "command_center_interpretation": reviewed_interpretation_overlay,
        },
        "review_hooks": {
            "today_emphasis": build_review_hook(
                target_type="player",
                target_id=player_id,
                review_type="today_emphasis_assessment",
                overlay_slot="operator_today_emphasis_overlay",
                review_count=len(
                    repository.fetch_operator_reviews(
                        target_type="player",
                        target_id=player_id,
                        review_type="today_emphasis_assessment",
                    )
                ),
            ),
            "command_center_interpretation": build_review_hook(
                target_type="player",
                target_id=player_id,
                review_type="command_center_interpretation_assessment",
                overlay_slot="operator_command_center_overlay",
                review_count=len(interpretation_reviews),
                latest_decision=interpretation_reviews[0].get("decision") if interpretation_reviews else None,
            ),
        },
        "confidence_block": {
            "memory_items_considered": len(memory_items),
            "average_confidence": average_confidence,
            "active_count": sum(1 for item in memory_items if item.get("status") == "active"),
            "baseline_count": sum(1 for item in memory_items if item.get("status") == "baseline"),
            "watch_count": sum(1 for item in memory_items if item.get("status") == "watch"),
        },
        "interpretation_groundwork": interpretation_groundwork,
        "meta": today_meta,
    }
