from __future__ import annotations

from typing import Any

from app.api.hand_matrix import get_hand_matrix_payload
from app.api.matrix_quiz import build_matrix_quiz_payload
from app.api.today import get_today_payload


def build_health_payload() -> dict[str, Any]:
    return {
        "ok": True,
        "service": "opb-backend",
        "boundary": "python-service",
    }


def build_today_service_payload(
    player_id: str,
    rebuild: bool = False,
    repository: Any | None = None,
) -> dict[str, Any]:
    payload = get_today_payload(player_id=player_id, rebuild=rebuild, repository=repository)
    return {
        "ok": True,
        "surface": "today",
        "player_id": player_id,
        "data": payload,
    }


def build_matrix_service_payload(
    player_id: str,
    selected_hand: str | None = None,
    window: str = "all",
    observations: list[Any] | None = None,
) -> dict[str, Any]:
    payload = get_hand_matrix_payload(
        player_id=player_id,
        window=window,
        selected_hand=selected_hand,
        observations=observations,
    )
    return {
        "ok": True,
        "surface": "matrix",
        "player_id": player_id,
        "data": payload,
    }


def build_matrix_quiz_service_payload(
    player_id: str,
    quiz_date: str | None = None,
    matrix_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = build_matrix_quiz_payload(
        player_id=player_id,
        quiz_date=quiz_date,
        matrix_payload=matrix_payload,
    )
    return {
        "ok": True,
        "surface": "matrix_quiz",
        "player_id": player_id,
        "date": payload.get("date"),
        "data": payload,
    }
