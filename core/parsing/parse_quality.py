from __future__ import annotations

from typing import Any


def build_parse_status(parse_quality: dict[str, Any]) -> str:
    if parse_quality.get("zero_hand_parse"):
        return "failed_zero_hands"
    if parse_quality.get("parser_mode") == "simple_fixture_fallback":
        return "fixture_fallback"
    if int(parse_quality.get("skipped_blocks", 0)) > 0:
        return "partial_success"
    return "success"


def build_confidence_summary(parse_quality: dict[str, Any]) -> dict[str, Any]:
    parsed_hands = int(parse_quality.get("parsed_hands", 0) or 0)
    skipped_blocks = int(parse_quality.get("skipped_blocks", 0) or 0)
    total_blocks = int(parse_quality.get("total_blocks", 0) or 0)
    parser_mode = str(parse_quality.get("parser_mode") or "gg_real")
    coverage = round(parsed_hands / total_blocks, 3) if total_blocks else 0.0
    confidence_label = "low" if parsed_hands == 0 else "medium" if skipped_blocks else "high"
    if parser_mode == "simple_fixture_fallback" and parsed_hands > 0:
        confidence_label = "medium"
    return {
        "parse_status": build_parse_status(parse_quality),
        "coverage": coverage,
        "parsed_hands": parsed_hands,
        "skipped_blocks": skipped_blocks,
        "parser_mode": parser_mode,
        "real_style_block_count": int(parse_quality.get("real_style_block_count", 0) or 0),
        "simple_block_count": int(parse_quality.get("simple_block_count", 0) or 0),
        "confidence_label": confidence_label,
    }
