from __future__ import annotations

import argparse
import json
from pathlib import Path

from core.ingest.file_ingest import ingest_gg_file
from core.storage.repositories import V2Repository


HERO_PLAYER_ID = "4c9d1e29-1f6b-4e5f-92da-111111111111"


def main() -> None:
    parser = argparse.ArgumentParser(description="V2 GG session-packet ingest entrypoint.")
    parser.add_argument("--file", type=Path, required=True, help="Path to GG Poker hand-history text file.")
    parser.add_argument(
        "--player-id",
        default=HERO_PLAYER_ID,
        help="Player id to associate with the ingest. Defaults to Hero canonical id.",
    )
    args = parser.parse_args()

    repository = V2Repository()
    result = ingest_gg_file(args.file.expanduser(), repository, args.player_id)
    print(
        json.dumps(
            {
            "status": result.status,
            "ingest_file_id": result.ingest_file_id,
            "session_id": result.session_id,
            "duplicate_of_file_id": result.duplicate_of_file_id,
            "duplicate_of_status": result.duplicate_of_status,
            "parsed_hand_count": result.parsed_hand_count,
            "evidence_count": result.evidence_count,
            "memory_count": result.memory_count,
            }
        )
    )


if __name__ == "__main__":
    main()
