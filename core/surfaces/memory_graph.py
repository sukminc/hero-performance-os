from __future__ import annotations

from typing import Any

from core.storage.repositories import V2Repository
from core.surfaces.interpretation_groundwork import build_review_brain_readiness
from core.surfaces.interpretation_summary import build_interpretation_summary
from core.surfaces.pattern_progress import build_pattern_progress_summary
from core.surfaces.review_hooks import build_review_hook, build_reviewed_overlay


def _bucket_by_status(memory_items: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    buckets = {
        "active": [],
        "baseline": [],
        "watch": [],
        "resolved": [],
    }
    for item in memory_items:
        status = str(item.get("status") or "")
        buckets.setdefault(status, [])
        buckets[status].append(item)
    return buckets


def _bucket_by_type(memory_items: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    buckets: dict[str, list[dict[str, Any]]] = {}
    for item in memory_items:
        memory_type = str(item.get("memory_type") or "unknown")
        buckets.setdefault(memory_type, [])
        buckets[memory_type].append(item)
    return buckets


def _bucket_by_direction(memory_items: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    buckets: dict[str, list[dict[str, Any]]] = {}
    for item in memory_items:
        direction = str((item.get("memory_payload") or {}).get("direction") or "unknown")
        buckets.setdefault(direction, [])
        buckets[direction].append(item)
    return buckets


def _bucket_by_maturity(memory_items: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    buckets: dict[str, list[dict[str, Any]]] = {}
    for item in memory_items:
        maturity = str((item.get("memory_payload") or {}).get("maturity") or "unknown")
        buckets.setdefault(maturity, [])
        buckets[maturity].append(item)
    return buckets


def _compact_items(items: list[dict[str, Any]], limit: int = 10) -> list[dict[str, Any]]:
    return [
        {
            "id": item.get("id"),
            "memory_type": item.get("memory_type"),
            "memory_key": item.get("memory_key"),
            "status": item.get("status"),
            "confidence": item.get("confidence"),
            "summary": item.get("summary"),
            "suggested_adjustment": item.get("suggested_adjustment"),
            "evidence_count": item.get("evidence_count"),
            "first_seen_session_id": item.get("first_seen_session_id"),
            "last_seen_session_id": item.get("last_seen_session_id"),
            "maturity": (item.get("memory_payload") or {}).get("maturity"),
            "direction": (item.get("memory_payload") or {}).get("direction"),
        }
        for item in items[:limit]
    ]


def build_memory_graph_payload(repository: V2Repository, player_id: str) -> dict[str, Any]:
    memory_items = repository.fetch_memory_items(player_id)
    latest_session_id = repository.fetch_latest_session_id(player_id)
    latest_session_memory_items = (
        repository.fetch_memory_items_for_session(player_id, latest_session_id) if latest_session_id else []
    )
    by_status = _bucket_by_status(memory_items)
    by_type = _bucket_by_type(memory_items)
    by_direction = _bucket_by_direction(memory_items)
    by_maturity = _bucket_by_maturity(memory_items)

    confidence_values = [float(item.get("confidence") or 0.0) for item in memory_items]
    average_confidence = round(sum(confidence_values) / len(confidence_values), 3) if confidence_values else 0.0

    latest_touched = [
        {
            "id": item.get("id"),
            "memory_type": item.get("memory_type"),
            "memory_key": item.get("memory_key"),
            "status": item.get("status"),
            "confidence": item.get("confidence"),
            "last_seen_session_id": item.get("last_seen_session_id"),
            "summary": item.get("summary"),
            "maturity": (item.get("memory_payload") or {}).get("maturity"),
            "direction": (item.get("memory_payload") or {}).get("direction"),
        }
        for item in memory_items[:8]
    ]

    inspection_summary = {
        "negative_active_keys": [
            str((item.get("memory_payload") or {}).get("entity_key") or item.get("memory_key"))
            for item in by_status.get("active", [])
            if str((item.get("memory_payload") or {}).get("direction") or "") == "negative"
        ][:5],
        "positive_baseline_keys": [
            str((item.get("memory_payload") or {}).get("entity_key") or item.get("memory_key"))
            for item in by_status.get("baseline", [])
            if str((item.get("memory_payload") or {}).get("direction") or "") == "positive"
        ][:5],
        "emerging_watch_count": len(by_maturity.get("emerging", [])),
        "repeated_or_established_count": len(by_maturity.get("repeated", [])) + len(by_maturity.get("established", [])),
    }
    interpretation_groundwork = build_review_brain_readiness(
        parse_status="success",
        evidence_total=len(memory_items),
        evidence_by_direction={direction: len(items) for direction, items in by_direction.items()},
        promoted_memory_count=len(by_status.get("active", [])) + len(by_status.get("baseline", [])),
        watch_memory_count=len(by_status.get("watch", [])),
        active_negative_count=len(
            [
                item
                for item in by_status.get("active", [])
                if str((item.get("memory_payload") or {}).get("direction") or "") == "negative"
            ]
        ),
        positive_baseline_count=len(
            [
                item
                for item in by_status.get("baseline", [])
                if str((item.get("memory_payload") or {}).get("direction") or "") == "positive"
            ]
        ),
        repeated_or_established_count=inspection_summary["repeated_or_established_count"],
    )
    interpretation_summary = build_interpretation_summary(memory_items)
    pattern_progress = build_pattern_progress_summary(memory_items, latest_session_memory_items)
    interpretation_reviews = repository.fetch_operator_reviews(
        target_type="player",
        target_id=player_id,
        review_type="interpretation_emphasis_assessment",
    )

    return {
        "player_id": player_id,
        "summary": {
            "total_memory_items": len(memory_items),
            "active_count": len(by_status.get("active", [])),
            "baseline_count": len(by_status.get("baseline", [])),
            "watch_count": len(by_status.get("watch", [])),
            "resolved_count": len(by_status.get("resolved", [])),
            "average_confidence": average_confidence,
        },
        "inspection_summary": inspection_summary,
        "interpretation_groundwork": interpretation_groundwork,
        "interpretation_summary": interpretation_summary,
        "pattern_progress": pattern_progress,
        "reviewed_overlays": {
            "interpretation_emphasis": build_reviewed_overlay(
                target_type="player",
                target_id=player_id,
                review_type="interpretation_emphasis_assessment",
                reviews=interpretation_reviews,
            ),
        },
        "review_hooks": {
            "cumulative_memory": build_review_hook(
                target_type="player",
                target_id=player_id,
                review_type="memory_graph_assessment",
                overlay_slot="operator_memory_graph_overlay",
                review_count=len(
                    repository.fetch_operator_reviews(
                        target_type="player",
                        target_id=player_id,
                        review_type="memory_graph_assessment",
                    )
                ),
            ),
            "interpretation_emphasis": build_review_hook(
                target_type="player",
                target_id=player_id,
                review_type="interpretation_emphasis_assessment",
                overlay_slot="operator_interpretation_overlay",
                review_count=len(interpretation_reviews),
                latest_decision=interpretation_reviews[0].get("decision") if interpretation_reviews else None,
            ),
        },
        "status_buckets": {
            status: _compact_items(items)
            for status, items in by_status.items()
            if items
        },
        "type_buckets": {
            memory_type: _compact_items(items, limit=6)
            for memory_type, items in by_type.items()
        },
        "direction_buckets": {
            direction: _compact_items(items, limit=6)
            for direction, items in by_direction.items()
            if items
        },
        "maturity_buckets": {
            maturity: _compact_items(items, limit=6)
            for maturity, items in by_maturity.items()
            if items
        },
        "latest_touched": latest_touched,
    }
