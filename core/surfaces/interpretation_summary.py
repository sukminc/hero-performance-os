from __future__ import annotations

from typing import Any


def _entity_key(item: dict[str, Any]) -> str:
    return str((item.get("memory_payload") or {}).get("entity_key") or item.get("memory_key") or "")


def _maturity(item: dict[str, Any]) -> str:
    return str((item.get("memory_payload") or {}).get("maturity") or "emerging")


def _direction(item: dict[str, Any]) -> str:
    return str((item.get("memory_payload") or {}).get("direction") or "unknown")


def _short_label(item: dict[str, Any]) -> str:
    memory_type = str(item.get("memory_type") or "")
    entity_key = _entity_key(item)
    if memory_type == "stable_strength_candidate" and entity_key == "session_survival_discipline":
        return "session survival discipline"
    if memory_type == "style_drift_candidate" and entity_key == "high_engagement_profile":
        return "high-engagement profile"
    if memory_type == "field_distortion_candidate" and entity_key == "multiway_pressure":
        return "multiway pressure"
    if memory_type == "field_distortion_candidate" and entity_key == "board_contact_density":
        return "board contact density"
    if memory_type == "contamination_risk_candidate" and entity_key == "blind_structure_absorption":
        return "blind-structure absorption"
    return entity_key or memory_type


def _compact(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "memory_type": item.get("memory_type"),
        "entity_key": _entity_key(item),
        "label": _short_label(item),
        "status": item.get("status"),
        "direction": _direction(item),
        "maturity": _maturity(item),
        "evidence_count": item.get("evidence_count"),
        "confidence": item.get("confidence"),
        "summary": item.get("summary"),
    }


def build_interpretation_summary(memory_items: list[dict[str, Any]]) -> dict[str, Any]:
    positives = [item for item in memory_items if _direction(item) == "positive"]
    negatives = [item for item in memory_items if _direction(item) == "negative"]
    shifts = [item for item in memory_items if _direction(item) == "shift"]

    standards = [item for item in positives if str(item.get("status") or "") == "baseline"]
    persistent_pressures = [
        item
        for item in negatives + shifts
        if int(item.get("evidence_count") or 0) >= 20 or _maturity(item) in {"repeated", "established"}
    ]
    field_context = [
        item
        for item in shifts
        if str(item.get("memory_type") or "") == "field_distortion_candidate"
        and int(item.get("evidence_count") or 0) >= 20
    ]

    hero_standard = _compact(standards[0]) if standards else None
    top_pressures = [_compact(item) for item in persistent_pressures[:3]]
    field_signals = [_compact(item) for item in field_context[:2]]

    if hero_standard and top_pressures:
        longitudinal_headline = (
            f"Baseline {hero_standard['label']} is holding, while {top_pressures[0]['label']} remains the main pressure to interpret."
        )
    elif hero_standard:
        longitudinal_headline = f"Baseline {hero_standard['label']} is the clearest cumulative standard in the corpus so far."
    elif top_pressures:
        longitudinal_headline = f"{top_pressures[0]['label']} is the clearest repeated pressure in the current corpus read."
    else:
        longitudinal_headline = "Interpretation is still thin and should stay close to inspectable evidence."

    return {
        "hero_standard": hero_standard,
        "persistent_pressures": top_pressures,
        "field_context": field_signals,
        "longitudinal_update": {
            "headline": longitudinal_headline,
            "baseline_count": len(standards),
            "persistent_pressure_count": len(persistent_pressures),
            "field_signal_count": len(field_context),
        },
    }
