from __future__ import annotations


def next_memory_status(
    evidence_count: int,
    confidence: float,
    direction: str,
    existing_status: str | None = None,
) -> str:
    if existing_status == "resolved" and confidence < 0.85:
        return "resolved"

    if direction == "positive":
        if evidence_count >= 3 and confidence >= 0.65:
            return "baseline"
        if evidence_count >= 2 and confidence >= 0.58:
            return "baseline"
        return "watch"

    if direction == "negative":
        if evidence_count >= 3 and confidence >= 0.62:
            return "active"
        if evidence_count >= 2 and confidence >= 0.7:
            return "active"
        if confidence >= 0.82:
            return "active"
        return "watch"

    if evidence_count >= 3 and confidence >= 0.62:
        return "active"
    if evidence_count >= 2 and confidence >= 0.72:
        return "active"
    return "watch"
