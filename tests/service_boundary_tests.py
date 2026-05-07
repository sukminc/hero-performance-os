#!/usr/bin/env python3
"""Smoke test the first production backend service boundary slice."""

from __future__ import annotations

import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.api.hand_matrix import HandObservation
from app.service.routes import (
    build_health_payload,
    build_matrix_quiz_service_payload,
    build_matrix_service_payload,
    build_today_service_payload,
)


PLAYER_ID = "service-boundary-player"


class StubRepository:
    def __init__(self) -> None:
        self.snapshots: list[dict] = []
        self.schema_ensured = False

    def ensure_schema(self) -> None:
        self.schema_ensured = True

    def fetch_latest_surface_snapshot(self, player_id: str, surface_type: str) -> dict | None:
        matches = [
            row
            for row in self.snapshots
            if row["player_id"] == player_id and row["surface_type"] == surface_type
        ]
        return deepcopy(matches[-1]) if matches else None

    def fetch_latest_session_id(self, player_id: str) -> str | None:
        return "session-service-boundary"

    def fetch_memory_items(self, player_id: str, statuses: list[str] | None = None) -> list[dict]:
        items = [
            {
                "id": "memory-1",
                "player_id": player_id,
                "memory_type": "style_drift_candidate",
                "memory_key": "passive_blind_compliance",
                "status": "active",
                "evidence_count": 4,
                "confidence": 0.82,
                "summary": "Hero is drifting passive from the blinds.",
                "suggested_adjustment": "Re-anchor blind discipline.",
                "memory_payload": {
                    "entity_key": "passive_blind_compliance",
                    "direction": "negative",
                    "maturity": "repeated",
                },
            }
        ]
        if statuses is not None:
            items = [item for item in items if item["status"] in statuses]
        return deepcopy(items)

    def create_surface_snapshot(
        self,
        snapshot_id: str,
        player_id: str,
        session_id: str | None,
        surface_type: str,
        payload: dict,
        confidence_summary: dict,
    ) -> None:
        self.snapshots.append(
            {
                "id": snapshot_id,
                "player_id": player_id,
                "session_id": session_id,
                "surface_type": surface_type,
                "payload": deepcopy(payload),
                "confidence_summary": deepcopy(confidence_summary),
            }
        )


def main() -> None:
    health = build_health_payload()
    if health.get("ok") is not True or health.get("boundary") != "python-service":
        raise AssertionError("Health payload did not identify the Python service boundary")

    repository = StubRepository()
    payload = build_today_service_payload(PLAYER_ID, repository=repository)
    if payload.get("ok") is not True:
        raise AssertionError("Service payload should be ok")
    if payload.get("surface") != "today":
        raise AssertionError("Service payload should identify the Today surface")
    if payload.get("player_id") != PLAYER_ID:
        raise AssertionError("Service payload should preserve player id provenance")
    if payload.get("data", {}).get("source") != "rebuilt_missing_snapshot":
        raise AssertionError("Today service should preserve the existing Today payload shape")
    if payload["data"]["payload"]["headline"] == "":
        raise AssertionError("Today service should return a usable Today headline")
    if not repository.schema_ensured:
        raise AssertionError("Today service should ensure repository schema through the existing API path")

    observations = [
        HandObservation(
            hand_id="hand-aa-1",
            session_id="session-service-boundary",
            tournament_id="tournament-service-boundary",
            started_at="2026/05/05 10:00:00",
            format_tag="standard_mtt",
            hand_class="AA",
            position="BTN",
            active_seats=6,
            stack_bb=20.0,
            bb_net=8.0,
            hero_summary="Hero opened AA and won.",
            first_preflop_action="raise",
            faced_action_preflop=False,
            preflop_entry_type="open_raise",
            prior_raise_count=0,
            prior_call_count=0,
            facing_state="unopened",
            faced_all_in_preflop=False,
            open_size_bb=None,
            hero_preflop_size_bb=2.0,
            hero_3bet_size_bb=None,
            hero_3bet_to_open_ratio=None,
            faced_4bet_after_3bet=False,
            folded_to_4bet_after_3bet=False,
        ),
        HandObservation(
            hand_id="hand-66-1",
            session_id="session-service-boundary",
            tournament_id="tournament-service-boundary",
            started_at="2026/05/05 10:05:00",
            format_tag="standard_mtt",
            hand_class="66",
            position="HJ",
            active_seats=6,
            stack_bb=14.0,
            bb_net=-14.0,
            hero_summary="Hero jammed 66 and lost.",
            first_preflop_action="jam",
            faced_action_preflop=False,
            preflop_entry_type="open_raise_jam",
            prior_raise_count=0,
            prior_call_count=0,
            facing_state="unopened",
            faced_all_in_preflop=False,
            open_size_bb=None,
            hero_preflop_size_bb=14.0,
            hero_3bet_size_bb=None,
            hero_3bet_to_open_ratio=None,
            faced_4bet_after_3bet=False,
            folded_to_4bet_after_3bet=False,
        ),
    ]
    matrix_payload = build_matrix_service_payload(PLAYER_ID, selected_hand="66", observations=observations)
    if matrix_payload.get("ok") is not True:
        raise AssertionError("Matrix service payload should be ok")
    if matrix_payload.get("surface") != "matrix":
        raise AssertionError("Matrix service payload should identify the Matrix surface")
    matrix_data = matrix_payload.get("data", {})
    if matrix_data.get("status") != "ok":
        raise AssertionError("Matrix service should preserve the existing Matrix payload shape")
    if matrix_data.get("selected_hand") != "66":
        raise AssertionError("Matrix service should preserve selected hand routing")
    if matrix_data.get("summary", {}).get("total_observations") != 2:
        raise AssertionError("Matrix service should build from provided observations")

    quiz_payload = build_matrix_quiz_service_payload(PLAYER_ID, quiz_date="2026-05-05", matrix_payload=matrix_data)
    if quiz_payload.get("ok") is not True:
        raise AssertionError("Matrix quiz service payload should be ok")
    if quiz_payload.get("surface") != "matrix_quiz":
        raise AssertionError("Matrix quiz service payload should identify the Matrix Quiz surface")
    if quiz_payload.get("date") != "2026-05-05":
        raise AssertionError("Matrix quiz service should preserve the requested date")
    quiz_data = quiz_payload.get("data", {})
    if quiz_data.get("status") != "ok":
        raise AssertionError("Matrix quiz service should build quiz cards from Matrix data")
    if not quiz_data.get("cards"):
        raise AssertionError("Matrix quiz service should expose quiz cards")


if __name__ == "__main__":
    main()
