from __future__ import annotations

from typing import Any

from core.storage.repositories import V2Repository
from core.surfaces.interpretation_groundwork import build_review_brain_readiness
from core.surfaces.review_hooks import build_review_hook


def _memory_update_brief(item: dict[str, Any]) -> str:
    payload = item.get("memory_payload") or {}
    entity_key = str(payload.get("entity_key") or item.get("memory_key") or "")
    maturity = str(payload.get("maturity") or "emerging")
    status = str(item.get("status") or "watch")
    return f"{entity_key} -> {status} ({maturity})"


def _evidence_direction_summary(evidence: list[dict[str, Any]]) -> dict[str, int]:
    summary = {"positive": 0, "negative": 0, "shift": 0, "unknown": 0}
    for row in evidence:
        direction = str(row.get("direction") or "unknown")
        summary[direction] = summary.get(direction, 0) + 1
    return summary


def build_session_lab_payload(
    repository: V2Repository,
    player_id: str,
    session_id: str,
) -> dict[str, Any]:
    session = repository.fetch_session(session_id)
    if not session:
        raise FileNotFoundError(f"Session {session_id} not found.")

    evidence = repository.fetch_session_evidence(session_id)
    hands = repository.fetch_hands_for_session(session_id, limit=25)
    memory_updates = repository.fetch_memory_items_for_session(player_id, session_id)

    parse_quality = dict(session.get("confidence_summary") or {})
    evidence_counts: dict[str, int] = {}
    for row in evidence:
        evidence_type = str(row.get("evidence_type"))
        evidence_counts[evidence_type] = evidence_counts.get(evidence_type, 0) + 1

    promoted_updates = [
        item for item in memory_updates if str(item.get("status") or "") in {"active", "baseline"}
    ]
    watch_updates = [item for item in memory_updates if str(item.get("status") or "") == "watch"]
    session_story = {
        "new_evidence_count": len(evidence),
        "promoted_memory_count": len(promoted_updates),
        "watch_memory_count": len(watch_updates),
        "top_promotions": [_memory_update_brief(item) for item in promoted_updates[:3]],
        "top_watchlist": [_memory_update_brief(item) for item in watch_updates[:3]],
    }
    evidence_direction_summary = _evidence_direction_summary(evidence)
    positive_baseline_count = sum(
        1
        for item in memory_updates
        if str(item.get("status") or "") == "baseline"
        and str((item.get("memory_payload") or {}).get("direction") or "") == "positive"
    )
    active_negative_count = sum(
        1
        for item in memory_updates
        if str(item.get("status") or "") == "active"
        and str((item.get("memory_payload") or {}).get("direction") or "") == "negative"
    )
    repeated_or_established_count = sum(
        1
        for item in memory_updates
        if str((item.get("memory_payload") or {}).get("maturity") or "") in {"repeated", "established"}
    )
    interpretation_groundwork = build_review_brain_readiness(
        parse_status=str(session.get("parse_status") or ""),
        evidence_total=len(evidence),
        evidence_by_direction=evidence_direction_summary,
        promoted_memory_count=len(promoted_updates),
        watch_memory_count=len(watch_updates),
        active_negative_count=active_negative_count,
        positive_baseline_count=positive_baseline_count,
        repeated_or_established_count=repeated_or_established_count,
    )

    return {
        "session": {
            "id": session.get("id"),
            "session_key": session.get("session_key"),
            "site": session.get("site"),
            "parse_status": session.get("parse_status"),
            "hand_count": session.get("hand_count"),
            "started_at": session.get("started_at"),
            "ended_at": session.get("ended_at"),
            "buyin_band": session.get("buyin_band"),
            "currency": session.get("currency"),
            "session_metadata": session.get("session_metadata") or {},
        },
        "parse_quality": parse_quality,
        "evidence_summary": {
            "total_evidence": len(evidence),
            "by_type": evidence_counts,
            "by_direction": evidence_direction_summary,
        },
        "session_story": session_story,
        "interpretation_groundwork": interpretation_groundwork,
        "review_hooks": {
            "session_evidence": build_review_hook(
                target_type="session",
                target_id=session_id,
                review_type="evidence_assessment",
                overlay_slot="operator_evidence_overlay",
            ),
            "memory_updates": build_review_hook(
                target_type="session",
                target_id=session_id,
                review_type="memory_update_assessment",
                overlay_slot="operator_memory_overlay",
            ),
            "surface_emphasis": build_review_hook(
                target_type="session",
                target_id=session_id,
                review_type="session_surface_emphasis",
                overlay_slot="operator_surface_emphasis_overlay",
            ),
        },
        "evidence": evidence,
        "memory_updates": [
            {
                "id": item.get("id"),
                "memory_type": item.get("memory_type"),
                "memory_key": item.get("memory_key"),
                "status": item.get("status"),
                "confidence": item.get("confidence"),
                "summary": item.get("summary"),
                "suggested_adjustment": item.get("suggested_adjustment"),
                "evidence_count": item.get("evidence_count"),
                "maturity": (item.get("memory_payload") or {}).get("maturity"),
                "direction": (item.get("memory_payload") or {}).get("direction"),
            }
            for item in memory_updates
        ],
        "sample_hands": hands,
    }
