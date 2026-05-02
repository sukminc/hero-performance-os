from __future__ import annotations

import re
from typing import Any


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


def _signal_for(result: dict[str, Any]) -> str:
    rank = _place_rank(str(result.get("finish_place") or ""))
    amount = _money_amount(str(result.get("total_received") or ""))
    if rank is not None and rank <= 3 and amount >= 500:
        return "top_three_big_cash"
    if rank is not None and rank <= 9:
        return "final_table"
    if amount >= 100:
        return "meaningful_cash"
    if "Entry" in str(result.get("total_received") or ""):
        return "seat_or_ticket_win"
    return "ordinary_result_context"


def build_tournament_result_signals(results: list[dict[str, Any]], limit: int = 5) -> dict[str, Any]:
    ranked = sorted(
        results,
        key=lambda row: (
            _money_amount(str(row.get("total_received") or "")),
            -(_place_rank(str(row.get("finish_place") or "")) or 9999),
        ),
        reverse=True,
    )
    top = []
    for row in ranked[:limit]:
        top.append(
            {
                "tournament_id": row.get("tournament_id"),
                "title": row.get("title"),
                "started_at": row.get("started_at"),
                "finish_place": row.get("finish_place"),
                "total_received": row.get("total_received"),
                "signal": _signal_for(row),
                "interpretation": (
                    "High-weight deep run: preserve the official result and review repeatable execution separately from run-good."
                    if _signal_for(row) == "top_three_big_cash"
                    else "Official result context is available for review weighting."
                ),
            }
        )

    return {
        "total_official_results": len(results),
        "top_result_signals": top,
        "truth_policy": "official GG summaries provide result context; hand-level execution remains separate derived evidence",
    }
