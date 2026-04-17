from __future__ import annotations

from typing import Any


def _entity_key(item: dict[str, Any]) -> str:
    return str((item.get("memory_payload") or {}).get("entity_key") or item.get("memory_key") or "")


def _direction(item: dict[str, Any]) -> str:
    return str((item.get("memory_payload") or {}).get("direction") or "unknown")


def _maturity(item: dict[str, Any]) -> str:
    return str((item.get("memory_payload") or {}).get("maturity") or "emerging")


def _label(item: dict[str, Any]) -> str:
    memory_type = str(item.get("memory_type") or "")
    entity_key = _entity_key(item)

    if memory_type == "style_drift_candidate" and entity_key == "passive_blind_compliance":
        return "passive blind compliance"
    if memory_type == "style_drift_candidate" and entity_key == "high_engagement_profile":
        return "high-engagement profile"
    if memory_type == "field_distortion_candidate" and entity_key == "multiway_pressure":
        return "multiway pressure"
    if memory_type == "field_distortion_candidate" and entity_key == "board_contact_density":
        return "board contact density"
    if memory_type == "contamination_risk_candidate" and entity_key == "blind_structure_absorption":
        return "blind-structure absorption"
    if memory_type == "stable_strength_candidate" and entity_key == "session_survival_discipline":
        return "session survival discipline"
    if memory_type == "stable_strength_candidate" and entity_key == "reset_and_preservation_discipline":
        return "reset and preservation discipline"
    return entity_key or memory_type


def _pattern_family(item: dict[str, Any]) -> str:
    memory_type = str(item.get("memory_type") or "")
    direction = _direction(item)
    if direction == "positive":
        return "strength"
    if memory_type == "field_distortion_candidate" or direction == "shift":
        return "field_or_context"
    return "leak_or_risk"


def _progress_verdict(item: dict[str, Any], latest_session_memory_ids: set[str]) -> tuple[str, str]:
    direction = _direction(item)
    status = str(item.get("status") or "")
    maturity = _maturity(item)
    item_id = str(item.get("id") or "")
    seen_in_latest = item_id in latest_session_memory_ids

    if direction == "positive":
        if seen_in_latest:
            return (
                "holding",
                "This positive pattern showed up again in the latest session, so it looks like a baseline you are keeping.",
            )
        if status == "baseline":
            return (
                "baseline_without_recent_ping",
                "This still reads as part of your baseline, but the latest session did not reinforce it directly.",
            )
        return (
            "too_early",
            "This looks useful, but the sample is still too thin to call it a stable strength.",
        )

    if direction == "negative":
        if seen_in_latest:
            return (
                "still_repeating",
                "This pattern appeared again in the latest session, so the correction is not holding yet.",
            )
        if maturity in {"repeated", "established"} and status == "active":
            return (
                "improving_window",
                "This has repeated enough to matter, but it did not fire in the latest session, which is the first sign of possible correction.",
            )
        return (
            "watching",
            "This risk exists in the memory, but the evidence is not yet strong enough to claim a real correction trend.",
        )

    if seen_in_latest:
        return (
            "context_live",
            "This context pattern was present in the latest session and should stay in the interpretation frame.",
        )
    return (
        "context_background",
        "This context pattern belongs in the longer read, but it was not refreshed by the latest session.",
    )


def _priority(item: dict[str, Any]) -> tuple[int, int, int, float]:
    family = _pattern_family(item)
    maturity = _maturity(item)
    confidence = float(item.get("confidence") or 0.0)
    evidence_count = int(item.get("evidence_count") or 0)
    family_rank = {
        "leak_or_risk": 0,
        "strength": 1,
        "field_or_context": 2,
    }.get(family, 3)
    maturity_rank = {
        "established": 0,
        "repeated": 1,
        "emerging": 2,
    }.get(maturity, 3)
    return (family_rank, maturity_rank, -evidence_count, -confidence)


def build_pattern_progress_summary(
    memory_items: list[dict[str, Any]],
    latest_session_memory_items: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    latest_session_memory_items = latest_session_memory_items or []
    latest_session_memory_ids = {
        str(item.get("id"))
        for item in latest_session_memory_items
        if item.get("id") is not None
    }

    candidates = [
        item
        for item in memory_items
        if _maturity(item) in {"repeated", "established"}
        or int(item.get("evidence_count") or 0) >= 3
    ]
    ordered = sorted(candidates, key=_priority)

    pattern_cards: list[dict[str, Any]] = []
    for item in ordered[:6]:
        verdict, verdict_reason = _progress_verdict(item, latest_session_memory_ids)
        pattern_cards.append(
            {
                "memory_id": item.get("id"),
                "memory_type": item.get("memory_type"),
                "memory_key": item.get("memory_key"),
                "label": _label(item),
                "pattern_family": _pattern_family(item),
                "status": item.get("status"),
                "direction": _direction(item),
                "maturity": _maturity(item),
                "evidence_count": item.get("evidence_count"),
                "confidence": item.get("confidence"),
                "appeared_in_latest_session": str(item.get("id") or "") in latest_session_memory_ids,
                "progress_verdict": verdict,
                "progress_reason": verdict_reason,
                "summary": item.get("summary"),
                "suggested_adjustment": item.get("suggested_adjustment"),
            }
        )

    repeated_leaks = [card for card in pattern_cards if card["pattern_family"] == "leak_or_risk"]
    repeated_strengths = [card for card in pattern_cards if card["pattern_family"] == "strength"]
    live_context = [
        card
        for card in pattern_cards
        if card["pattern_family"] == "field_or_context" and card["appeared_in_latest_session"]
    ]

    if repeated_leaks:
        headline = (
            f"The clearest repeat pattern is {repeated_leaks[0]['label']}, "
            f"and it currently reads as {repeated_leaks[0]['progress_verdict']}."
        )
    elif repeated_strengths:
        headline = (
            f"The clearest stable pattern is {repeated_strengths[0]['label']}, "
            f"and it currently reads as {repeated_strengths[0]['progress_verdict']}."
        )
    elif live_context:
        headline = f"The latest session mostly refreshed context patterns such as {live_context[0]['label']}."
    else:
        headline = "Pattern tracking is still thin, so keep interpretation close to inspectable session evidence."

    return {
        "headline": headline,
        "counts": {
            "tracked_patterns": len(pattern_cards),
            "repeated_leak_count": len(repeated_leaks),
            "repeated_strength_count": len(repeated_strengths),
            "live_context_count": len(live_context),
        },
        "pattern_cards": pattern_cards,
    }
