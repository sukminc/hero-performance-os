from __future__ import annotations

import argparse
import json

from core.storage.repositories import V2Repository
from core.surfaces.session_lab import build_session_lab_payload


HERO_PLAYER_ID = "4c9d1e29-1f6b-4e5f-92da-111111111111"


def get_session_lab_payload(
    player_id: str = HERO_PLAYER_ID,
    session_id: str | None = None,
) -> dict:
    repository = V2Repository()
    repository.ensure_schema()
    resolved_session_id = session_id or repository.fetch_latest_session_id(player_id)
    if not resolved_session_id:
        return {
            "player_id": player_id,
            "session": None,
            "message": "No session is available yet for Session Lab.",
        }
    payload = build_session_lab_payload(repository, player_id=player_id, session_id=resolved_session_id)
    payload["player_id"] = player_id
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Read the V2 Session Lab payload.")
    parser.add_argument("--player-id", default=HERO_PLAYER_ID, help="Player id to inspect.")
    parser.add_argument("--session-id", help="Specific session id to inspect. Defaults to latest session.")
    args = parser.parse_args()
    payload = get_session_lab_payload(player_id=args.player_id, session_id=args.session_id)
    print(json.dumps(payload, indent=2, default=str))


if __name__ == "__main__":
    main()

