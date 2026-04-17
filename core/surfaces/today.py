from __future__ import annotations

from uuid import uuid4

from core.surfaces.surface_models import TodayAdjustment, TodaySurface
from core.storage.repositories import V2Repository


def _memory_priority(item: dict) -> tuple[int, float, int]:
    status_rank = {
        "active": 0,
        "baseline": 1,
        "watch": 2,
        "resolved": 3,
    }.get(str(item.get("status")), 4)
    maturity_rank = {
        "established": 0,
        "repeated": 1,
        "emerging": 2,
    }.get(str((item.get("memory_payload") or {}).get("maturity") or "emerging"), 3)
    confidence = float(item.get("confidence") or 0.0)
    evidence_count = int(item.get("evidence_count") or 0)
    return (status_rank, maturity_rank, -evidence_count, -confidence)


def _short_memory_label(item: dict) -> str:
    memory_type = str(item.get("memory_type") or "")
    entity_key = str((item.get("memory_payload") or {}).get("entity_key") or item.get("memory_key") or "")
    if memory_type == "style_drift_candidate" and entity_key == "passive_blind_compliance":
        return "blind-passivity drift"
    if memory_type == "contamination_risk_candidate":
        return "contamination risk"
    if memory_type == "hand_class_underperformance":
        return f"{entity_key} leak review"
    if memory_type == "stable_strength_candidate" and entity_key == "reset_and_preservation_discipline":
        return "reset discipline"
    return entity_key or memory_type


def _current_state(memory_items: list[dict]) -> tuple[str, str]:
    active_negative = [
        item
        for item in memory_items
        if item.get("status") == "active"
        and str((item.get("memory_payload") or {}).get("direction", "")) == "negative"
    ]
    contamination = [
        item
        for item in memory_items
        if item.get("status") == "active"
        and item.get("memory_type") == "contamination_risk_candidate"
    ]
    baselines = [item for item in memory_items if item.get("status") == "baseline"]
    repeated_negative = [
        item
        for item in active_negative
        if str((item.get("memory_payload") or {}).get("maturity") or "") in {"repeated", "established"}
    ]

    if contamination:
        headline = f"Protect baseline first. { _short_memory_label(contamination[0]) } is active enough to distort today's decisions."
        return ("contaminated", headline)
    if len(repeated_negative) >= 2:
        headline = "Strategic drift is repeating across sessions, so today's priority is to interrupt the pattern early."
        return ("drifting", headline)
    if len(active_negative) == 1 and baselines:
        headline = f"Baseline is still present, but { _short_memory_label(active_negative[0]) } is the one issue to control today."
        return ("volatile_but_acceptable", headline)
    if len(active_negative) == 1:
        headline = f"{ _short_memory_label(active_negative[0]) } is the clearest active risk, so keep today's focus narrow."
        return ("drifting", headline)
    if baselines and not active_negative:
        headline = f"Baseline is holding. Carry { _short_memory_label(baselines[0]) } forward without over-adjusting."
        return ("stable", headline)
    return ("unclear", "Memory is still emerging, so keep today's plan simple and avoid overreacting to thin evidence.")


def _adjustment_label(item: dict) -> str:
    memory_type = str(item.get("memory_type") or "")
    entity_key = str((item.get("memory_payload") or {}).get("entity_key") or "")
    if memory_type == "style_drift_candidate" and entity_key == "passive_blind_compliance":
        return "Re-anchor blind discipline"
    if memory_type == "contamination_risk_candidate":
        return "Avoid field contamination"
    if memory_type == "hand_class_underperformance":
        return f"Review {entity_key}"
    if memory_type == "stable_strength_candidate" and entity_key == "reset_and_preservation_discipline":
        return "Preserve reset discipline"
    return memory_type.replace("_", " ")


def _adjustment_reason(item: dict) -> str:
    memory_type = str(item.get("memory_type") or "")
    entity_key = str((item.get("memory_payload") or {}).get("entity_key") or "")
    maturity = str((item.get("memory_payload") or {}).get("maturity") or "emerging")
    evidence_count = int(item.get("evidence_count") or 0)
    if memory_type == "style_drift_candidate" and entity_key == "passive_blind_compliance":
        return f"This drift is {maturity} across {evidence_count} sessions of evidence, so avoid slipping into automatic blind defense/calls."
    if memory_type == "contamination_risk_candidate":
        return f"The contamination signal is {maturity}, so use pool chaos as context only and do not inherit it as your baseline."
    if memory_type == "hand_class_underperformance":
        return f"{entity_key} has become a {maturity} leak candidate, so revisit its pre-session threshold before you sit."
    if memory_type == "stable_strength_candidate" and entity_key == "reset_and_preservation_discipline":
        return f"This strength is {maturity}, so deliberately keep the breathing/reset routine that preserved chips in prior sessions."
    summary = str(item.get("summary") or "").strip()
    return summary or "Carry the strongest mature memory forward into today's play."


def build_today_surface(repository: V2Repository, player_id: str, session_id: str | None = None) -> TodaySurface:
    memory_items = repository.fetch_memory_items(player_id, statuses=["active", "baseline", "watch"])
    ordered_items = sorted(memory_items, key=_memory_priority)
    current_state, headline = _current_state(ordered_items)

    adjustments: list[TodayAdjustment] = []
    for item in ordered_items:
        suggestion = item.get("suggested_adjustment")
        if item.get("status") == "watch":
            continue
        direction = str((item.get("memory_payload") or {}).get("direction") or "")
        if item.get("status") == "baseline" and direction != "positive":
            continue
        if item.get("status") == "active" and direction != "negative":
            continue
        confidence = float(item.get("confidence") or 0.0)
        adjustments.append(
            TodayAdjustment(
                label=_adjustment_label(item),
                reason=_adjustment_reason(item),
                confidence=confidence,
                memory_id=str(item.get("id")),
            )
        )
        if len(adjustments) == 2:
            break

    supporting_memory = [
        {
            "id": item.get("id"),
            "memory_type": item.get("memory_type"),
            "memory_key": item.get("memory_key"),
            "status": item.get("status"),
            "confidence": item.get("confidence"),
            "summary": item.get("summary"),
            "evidence_count": item.get("evidence_count"),
            "maturity": (item.get("memory_payload") or {}).get("maturity"),
            "direction": (item.get("memory_payload") or {}).get("direction"),
        }
        for item in ordered_items[:6]
    ]

    confidence_values = [float(item.get("confidence") or 0.0) for item in ordered_items]
    average_confidence = round(sum(confidence_values) / len(confidence_values), 3) if confidence_values else 0.0
    primary_focus = adjustments[0].label if adjustments else "Keep the plan simple"
    confidence_summary = {
        "memory_items_considered": len(ordered_items),
        "average_confidence": average_confidence,
        "adjustment_count": len(adjustments),
        "state": current_state,
        "primary_focus": primary_focus,
    }

    surface = TodaySurface(
        player_id=player_id,
        current_state=current_state,
        headline=headline,
        adjustments=adjustments,
        supporting_memory=supporting_memory,
        confidence_summary=confidence_summary,
    )

    repository.create_surface_snapshot(
        snapshot_id=f"surface-{uuid4()}",
        player_id=player_id,
        session_id=session_id,
        surface_type="today",
        payload={
            "player_id": surface.player_id,
            "current_state": surface.current_state,
            "headline": surface.headline,
            "adjustments": [
                {
                    "label": adjustment.label,
                    "reason": adjustment.reason,
                    "confidence": adjustment.confidence,
                    "memory_id": adjustment.memory_id,
                }
                for adjustment in surface.adjustments
            ],
            "supporting_memory": surface.supporting_memory,
        },
        confidence_summary=surface.confidence_summary,
    )
    return surface
