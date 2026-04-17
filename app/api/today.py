from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from core.storage.repositories import V2Repository
from core.surfaces.today import build_today_surface


HERO_PLAYER_ID = "4c9d1e29-1f6b-4e5f-92da-111111111111"


def get_today_payload(
    player_id: str = HERO_PLAYER_ID,
    rebuild: bool = False,
) -> dict:
    repository = V2Repository()
    repository.ensure_schema()

    if rebuild:
        latest_session_id = repository.fetch_latest_session_id(player_id)
        surface = build_today_surface(repository, player_id=player_id, session_id=latest_session_id)
        return {
            "source": "rebuilt",
            "payload": {
                "player_id": surface.player_id,
                "current_state": surface.current_state,
                "headline": surface.headline,
                "adjustments": [asdict(adjustment) for adjustment in surface.adjustments],
                "supporting_memory": surface.supporting_memory,
                "confidence_summary": surface.confidence_summary,
            },
        }

    latest_snapshot = repository.fetch_latest_surface_snapshot(player_id, "today")
    if latest_snapshot:
        return {
            "source": "snapshot",
            "payload": latest_snapshot["payload"],
            "confidence_summary": latest_snapshot.get("confidence_summary") or {},
            "generated_at": latest_snapshot.get("generated_at"),
            "snapshot_id": latest_snapshot.get("id"),
            "session_id": latest_snapshot.get("session_id"),
        }

    latest_session_id = repository.fetch_latest_session_id(player_id)
    surface = build_today_surface(repository, player_id=player_id, session_id=latest_session_id)
    return {
        "source": "rebuilt_missing_snapshot",
        "payload": {
            "player_id": surface.player_id,
            "current_state": surface.current_state,
            "headline": surface.headline,
            "adjustments": [asdict(adjustment) for adjustment in surface.adjustments],
            "supporting_memory": surface.supporting_memory,
            "confidence_summary": surface.confidence_summary,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Read or rebuild the V2 Today surface payload.")
    parser.add_argument("--player-id", default=HERO_PLAYER_ID, help="Player id to read Today for.")
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Force a fresh Today rebuild from current memory instead of reading the latest snapshot.",
    )
    args = parser.parse_args()
    payload = get_today_payload(player_id=args.player_id, rebuild=args.rebuild)
    print(json.dumps(payload, indent=2, default=str))


if __name__ == "__main__":
    main()

