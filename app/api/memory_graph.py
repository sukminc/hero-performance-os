from __future__ import annotations

import argparse
import json

from core.storage.repositories import V2Repository
from core.surfaces.memory_graph import build_memory_graph_payload


HERO_PLAYER_ID = "4c9d1e29-1f6b-4e5f-92da-111111111111"


def get_memory_graph_payload(player_id: str = HERO_PLAYER_ID) -> dict:
    repository = V2Repository()
    repository.ensure_schema()
    return build_memory_graph_payload(repository, player_id=player_id)


def main() -> None:
    parser = argparse.ArgumentParser(description="Read the V2 Memory Graph payload.")
    parser.add_argument("--player-id", default=HERO_PLAYER_ID, help="Player id to inspect.")
    args = parser.parse_args()
    payload = get_memory_graph_payload(player_id=args.player_id)
    print(json.dumps(payload, indent=2, default=str))


if __name__ == "__main__":
    main()

