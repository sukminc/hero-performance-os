#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.ingest.file_ingest import ingest_gg_file
from core.ingest.legacy_corpus import DEFAULT_OLD_REPO_ROOT, build_legacy_corpus_summary, collect_legacy_raw_gg_files
from core.storage.repositories import V2Repository


HERO_PLAYER_ID = "4c9d1e29-1f6b-4e5f-92da-111111111111"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Backfill Hero Performance OS V2 from raw GG hand-history files found in the legacy repo."
    )
    parser.add_argument(
        "--old-repo-root",
        default=str(DEFAULT_OLD_REPO_ROOT),
        help="Legacy repo root to scan for raw GG txt files.",
    )
    parser.add_argument("--player-id", default=HERO_PLAYER_ID, help="Player id to ingest into.")
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional file limit for controlled backfills.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually ingest into the configured V2 repository. Without this flag, the script only inventories the corpus.",
    )
    args = parser.parse_args()

    old_repo_root = Path(args.old_repo_root).expanduser().resolve()
    inventory = build_legacy_corpus_summary(old_repo_root=old_repo_root)
    files = collect_legacy_raw_gg_files(old_repo_root=old_repo_root)
    if args.limit is not None:
        files = files[: args.limit]

    if not args.apply:
        print(
            json.dumps(
                {
                    "mode": "inventory",
                    **inventory,
                    "selected_count": len(files),
                    "selected_files": [str(item.path) for item in files[:20]],
                },
                indent=2,
            )
        )
        return

    repository = V2Repository()
    repository.ensure_schema()

    results: list[dict[str, object]] = []
    status_counts: dict[str, int] = {}

    for item in files:
        result = ingest_gg_file(item.path, repository=repository, player_id=args.player_id)
        status_counts[result.status] = status_counts.get(result.status, 0) + 1
        results.append(
            {
                "path": str(item.path),
                "status": result.status,
                "session_id": result.session_id,
                "duplicate_of_file_id": result.duplicate_of_file_id,
                "parsed_hand_count": result.parsed_hand_count,
                "evidence_count": result.evidence_count,
                "memory_count": result.memory_count,
            }
        )

    print(
        json.dumps(
            {
                "mode": "apply",
                "old_repo_root": str(old_repo_root),
                "selected_count": len(files),
                "status_counts": status_counts,
                "results": results[:50],
            },
            indent=2,
            default=str,
        )
    )


if __name__ == "__main__":
    main()
