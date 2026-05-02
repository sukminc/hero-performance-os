from __future__ import annotations

from typing import Any
import re

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


def _money_amount(value: str | None) -> float:
    if not value:
        return 0.0
    match = re.search(r"\$([0-9,]+(?:\.[0-9]+)?)", value)
    return float(match.group(1).replace(",", "")) if match else 0.0


def _place_rank(value: str | None) -> int | None:
    if not value:
        return None
    match = re.search(r"\d+", value)
    return int(match.group(0)) if match else None


def _build_result_context(repository: V2Repository, player_id: str, session: dict[str, Any]) -> dict[str, Any]:
    metadata = session.get("session_metadata") or {}
    tournament_id = str(metadata.get("tournament_id") or "").strip()
    official_result = repository.get_tournament_result(player_id, tournament_id) if tournament_id else None
    if not official_result:
        return {
            "tournament_id": tournament_id or None,
            "official_result": None,
            "result_signal": "missing_official_summary",
            "interpretation": "No official GG tournament summary is linked yet, so result-size interpretation stays unavailable.",
        }

    finish_rank = _place_rank(str(official_result.get("finish_place") or ""))
    received_amount = _money_amount(str(official_result.get("total_received") or ""))
    is_final_table = finish_rank is not None and finish_rank <= 9
    is_big_cash = received_amount >= 500
    signal = "deep_run_big_cash" if is_final_table and is_big_cash else "deep_run" if is_final_table else "cash_result"

    return {
        "tournament_id": tournament_id,
        "official_result": official_result,
        "result_signal": signal,
        "interpretation": (
            "Official GG summary confirms a final-table big cash. Treat this as a high-weight positive session, "
            "but separate execution review from run-good/result heat."
            if signal == "deep_run_big_cash"
            else "Official GG summary is linked; use it as result context while keeping strategic evidence separate."
        ),
        "review_prompts": [
            "Identify which decisions were repeatable positive execution, not just rewarded outcomes.",
            "Mark obvious run-good spots separately so the product preserves confidence without over-crediting variance.",
            "Promote only repeatable patterns into Hero memory; keep one-off heat as session context.",
        ],
    }


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
    result_context = _build_result_context(repository, player_id, session)

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
        "result_context": result_context,
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
