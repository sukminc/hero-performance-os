from __future__ import annotations

from core.storage.models import HandRecord


POSITIVE_EXECUTION_KEYWORDS = (
    "breathe",
    "breathing",
    "reset",
    "saved chips",
    "save chips",
    "locked",
    "preserve",
    "disciplined fold",
    "discipline held",
    "practice reset",
)


def hand_outcome(hand: HandRecord) -> str:
    result_summary = hand.result_summary or {}
    result_value = result_summary.get("result_value")
    if isinstance(result_value, int | float):
        if result_value > 0:
            return "win"
        if result_value < 0:
            return "loss"

    hero_summary = str(result_summary.get("hero_summary") or "").lower()
    if "lost" in hero_summary:
        return "loss"
    if "won" in hero_summary or "collected" in hero_summary:
        return "win"
    if "folded" in hero_summary:
        return "neutral"
    return "unknown"


def has_positive_execution_cue(hand: HandRecord) -> bool:
    result_summary = hand.result_summary or {}
    text = " ".join(
        [
            str(result_summary.get("hero_summary") or ""),
            " ".join(str(action) for action in result_summary.get("hero_actions") or []),
            str(result_summary.get("pattern") or ""),
        ]
    ).lower()
    return any(keyword in text for keyword in POSITIVE_EXECUTION_KEYWORDS)
