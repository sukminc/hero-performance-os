from __future__ import annotations

import argparse
import json

from core.storage.repositories import V2Repository
from core.surfaces.command_center import build_command_center_payload


HERO_PLAYER_ID = "4c9d1e29-1f6b-4e5f-92da-111111111111"


def get_command_center_payload(
    player_id: str = HERO_PLAYER_ID,
    rebuild_today: bool = False,
) -> dict:
    repository = V2Repository()
    repository.ensure_schema()
    return build_command_center_payload(repository, player_id=player_id, rebuild_today=rebuild_today)


def main() -> None:
    parser = argparse.ArgumentParser(description="Read the V2 Command Center payload.")
    parser.add_argument("--player-id", default=HERO_PLAYER_ID, help="Player id to read Command Center for.")
    parser.add_argument(
        "--rebuild-today",
        action="store_true",
        help="Force Today to rebuild before assembling the Command Center payload.",
    )
    args = parser.parse_args()
    payload = get_command_center_payload(player_id=args.player_id, rebuild_today=args.rebuild_today)
    print(json.dumps(payload, indent=2, default=str))


if __name__ == "__main__":
    main()

