from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from core.memory.memory_queries import build_memory_key
from core.storage.models import MemoryItemRecord, OperatorReviewRecord
from core.storage.repositories import V2Repository

ALLOWED_TAGS = {"repeatable_execution", "run_good", "cooler", "unclear"}


def _amounts_from_text(text: str) -> list[int]:
    return [int(value.replace(",", "")) for value in re.findall(r"\b\d[\d,]{2,}\b", text)]


def _hand_block(hand: dict[str, Any]) -> list[str]:
    return list(((hand.get("raw_payload") or {}).get("block") or []))


def _spot_score(hand: dict[str, Any]) -> tuple[float, list[str]]:
    block = _hand_block(hand)
    text = "\n".join(block)
    lower = text.lower()
    hero_actions = " ".join((hand.get("result_summary") or {}).get("hero_actions") or []).lower()
    amounts = _amounts_from_text(text)
    max_amount = max(amounts) if amounts else 0
    score = 0.0
    reasons: list[str] = []

    if "collected" in lower or " won " in lower:
        score += 4.0
        reasons.append("Hero won or collected chips")
    if "all-in" in lower or "all in" in lower:
        score += 3.0
        reasons.append("All-in pressure appeared")
    if any(action in hero_actions for action in ["raises", "bets", "calls"]):
        score += 2.0
        reasons.append("Hero took a meaningful betting/calling action")
    if hand.get("effective_stack_bb") is not None:
        stack_bb = float(hand.get("effective_stack_bb") or 0.0)
        if stack_bb <= 25:
            score += 1.5
            reasons.append("Short/medium-stack decision node")
        elif stack_bb >= 50:
            score += 1.0
            reasons.append("Deep-stack decision node")
    if max_amount >= 100_000:
        score += 2.0
        reasons.append("Large chip movement")
    elif max_amount >= 25_000:
        score += 1.0
        reasons.append("Medium chip movement")

    return score, reasons


def _compact_hand(hand: dict[str, Any], score: float, reasons: list[str]) -> dict[str, Any]:
    block = _hand_block(hand)
    hero_lines = [line for line in block if line.startswith("Hero:")]
    summary_lines = [line for line in block if line.startswith("Seat ") and "Hero" in line]
    return {
        "spot_id": hand.get("id"),
        "hand_external_id": hand.get("hand_external_id"),
        "score": round(score, 2),
        "reasons": reasons,
        "hero_position": hand.get("hero_position"),
        "effective_stack_bb": hand.get("effective_stack_bb"),
        "players_to_flop": hand.get("players_to_flop"),
        "board": hand.get("board_texture_summary"),
        "hero_actions": hero_lines[:8],
        "hero_summary": summary_lines[:2],
        "operator_question": "Tag this spot as repeatable execution, run-good, cooler, or unclear.",
    }


def _latest_tag(repository: V2Repository, spot_id: str) -> dict[str, Any] | None:
    reviews = repository.fetch_operator_reviews(
        target_type="deep_run_spot",
        target_id=spot_id,
        review_type="deep_run_spot_tag",
    )
    return reviews[0] if reviews else None


def build_big_win_review_payload(
    repository: V2Repository,
    player_id: str,
    tournament_id: str = "6408385",
    limit: int = 12,
) -> dict[str, Any]:
    tournament_result = repository.get_tournament_result(player_id, tournament_id)
    session = repository.fetch_session_by_tournament_id(player_id, tournament_id)
    if not tournament_result or not session:
        return {
            "tournament_id": tournament_id,
            "ready": False,
            "reason": "Official result and linked hand-history session are both required.",
            "tournament_result": tournament_result,
            "session": session,
            "candidate_spots": [],
            "tag_summary": {},
        }

    hands = repository.fetch_hands_for_session(str(session["id"]), limit=1000)
    scored = []
    for hand in hands:
        score, reasons = _spot_score(hand)
        if score > 0:
            scored.append((score, reasons, hand))
    scored.sort(key=lambda item: item[0], reverse=True)

    candidate_spots = []
    tag_summary: dict[str, int] = {}
    for score, reasons, hand in scored[:limit]:
        spot = _compact_hand(hand, score, reasons)
        tag = _latest_tag(repository, str(spot["spot_id"]))
        if tag:
            decision = str(tag.get("decision") or "unclear")
            tag_summary[decision] = tag_summary.get(decision, 0) + 1
            spot["operator_tag"] = {
                "decision": decision,
                "notes": tag.get("notes"),
                "review_payload": tag.get("review_payload") or {},
                "created_at": tag.get("created_at"),
            }
        candidate_spots.append(spot)

    return {
        "tournament_id": tournament_id,
        "ready": True,
        "truth_policy": "Big-win context prioritizes review; operator tags decide what becomes repeatable execution memory.",
        "tournament_result": tournament_result,
        "session": {
            "id": session.get("id"),
            "session_key": session.get("session_key"),
            "started_at": session.get("started_at"),
            "buyin_band": session.get("buyin_band"),
            "hand_count": session.get("hand_count"),
            "parse_status": session.get("parse_status"),
        },
        "review_summary": {
            "candidate_count": len(candidate_spots),
            "tag_summary": tag_summary,
            "next_operator_action": "Tag the highest-weight spots before promoting anything from this run into durable Hero memory.",
        },
        "candidate_spots": candidate_spots,
    }


def promote_repeatable_execution_memory(
    repository: V2Repository,
    *,
    player_id: str,
    tournament_id: str = "6408385",
) -> dict[str, Any]:
    payload = build_big_win_review_payload(repository, player_id, tournament_id=tournament_id, limit=1000)
    if not payload.get("ready"):
        return {
            "ok": False,
            "promoted": False,
            "reason": "Big Win Review is not ready; official result and linked hand-history session are required.",
            "tournament_id": tournament_id,
        }

    repeatable_spots = [
        spot
        for spot in payload.get("candidate_spots", [])
        if (spot.get("operator_tag") or {}).get("decision") == "repeatable_execution"
    ]
    if not repeatable_spots:
        return {
            "ok": True,
            "promoted": False,
            "reason": "No repeatable_execution operator tags found.",
            "tournament_id": tournament_id,
            "reviewed_repeatable_count": 0,
        }

    session = payload.get("session") or {}
    tournament = payload.get("tournament_result") or {}
    title = tournament.get("title") or f"tournament {tournament_id}"
    memory_type = "positive_execution_memory"
    entity_scope = "deep_run"
    entity_key = f"repeatable_execution:{tournament_id}"
    memory_key = build_memory_key(memory_type, entity_scope, entity_key)
    source_hand_ids = [str(spot.get("spot_id")) for spot in repeatable_spots if spot.get("spot_id")]
    review_ids = [
        str((spot.get("operator_tag") or {}).get("review_payload", {}).get("source_review_id") or "")
        for spot in repeatable_spots
    ]
    review_ids = [review_id for review_id in review_ids if review_id]
    confidence = round(min(0.92, 0.74 + 0.04 * len(repeatable_spots)), 2)
    summary = (
        f"Operator approved {len(repeatable_spots)} repeatable execution spot"
        f"{'' if len(repeatable_spots) == 1 else 's'} from {title}. "
        "Preserve this as positive execution memory while keeping result heat separate from strategic truth."
    )
    record = MemoryItemRecord(
        id=str((repository.get_memory_item(player_id, memory_type, memory_key) or {}).get("id") or f"memory-{uuid4()}"),
        player_id=player_id,
        memory_type=memory_type,
        memory_key=memory_key,
        status="baseline",
        first_seen_session_id=str(session.get("id") or "") or None,
        last_seen_session_id=str(session.get("id") or "") or None,
        evidence_count=len(repeatable_spots),
        confidence=confidence,
        summary=summary,
        suggested_adjustment="Keep the approved deep-run execution pattern available without over-learning the tournament result.",
        memory_payload={
            "entity_scope": entity_scope,
            "entity_key": entity_key,
            "direction": "positive",
            "maturity": "operator_reviewed",
            "source": "big_win_review_operator_tags",
            "tournament_id": tournament_id,
            "tournament_title": title,
            "official_result": {
                "finish_place": tournament.get("finish_place"),
                "total_received": tournament.get("total_received"),
                "player_count": tournament.get("player_count"),
            },
            "reviewed_repeatable_count": len(repeatable_spots),
            "source_hand_ids": source_hand_ids,
            "source_review_ids": review_ids,
            "spot_summaries": [
                {
                    "spot_id": spot.get("spot_id"),
                    "hand_external_id": spot.get("hand_external_id"),
                    "score": spot.get("score"),
                    "reasons": spot.get("reasons") or [],
                    "effective_stack_bb": spot.get("effective_stack_bb"),
                    "hero_actions": spot.get("hero_actions") or [],
                    "operator_notes": (spot.get("operator_tag") or {}).get("notes"),
                }
                for spot in repeatable_spots[:12]
            ],
            "truth_policy": "operator_approved_positive_execution_memory_separate_from_result_heat",
        },
    )
    repository.upsert_memory_item(record)
    return {
        "ok": True,
        "promoted": True,
        "memory_id": record.id,
        "memory_key": record.memory_key,
        "reviewed_repeatable_count": len(repeatable_spots),
        "status": record.status,
        "confidence": record.confidence,
    }


def tag_big_win_spot(
    repository: V2Repository,
    *,
    spot_id: str,
    decision: str,
    notes: str | None = None,
) -> dict[str, Any]:
    normalized = decision.strip().lower()
    if normalized not in ALLOWED_TAGS:
        raise ValueError(f"Unsupported deep-run tag: {decision}")
    review_id = f"review-{uuid4()}"
    record = OperatorReviewRecord(
        id=review_id,
        target_type="deep_run_spot",
        target_id=spot_id,
        review_type="deep_run_spot_tag",
        decision=normalized,
        notes=notes.strip() if notes else None,
        review_payload={
            "truth_policy": "operator_tag_overlay_separate_from_source_hand_truth",
            "allowed_tags": sorted(ALLOWED_TAGS),
            "source_review_id": review_id,
        },
        created_at=datetime.now(timezone.utc),
    )
    repository.create_operator_review(record)
    return {"ok": True, "spot_id": spot_id, "decision": normalized}
