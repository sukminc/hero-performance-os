#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.ingest.dataset_index import build_processable_dataset_index, write_processable_dataset_index


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the OPB processable dataset index.")
    parser.add_argument("--raw-manifest", type=Path, default=ROOT / "data" / "manifests" / "raw_file_manifest.json")
    parser.add_argument("--hand-ledger", type=Path, default=ROOT / "data" / "manifests" / "hand_extraction_ledger.json")
    parser.add_argument("--out", type=Path, default=ROOT / "data" / "manifests" / "processable_dataset_index.json")
    parser.add_argument("--player-id", default="hero")
    parser.add_argument("--generated-at", default=None)
    parser.add_argument("--summary", action="store_true", help="Print summary JSON after writing the index.")
    args = parser.parse_args()

    index = build_processable_dataset_index(
        args.raw_manifest,
        args.hand_ledger,
        player_id=args.player_id,
        generated_at=args.generated_at,
    )
    write_processable_dataset_index(index, args.out)

    if args.summary:
        print(json.dumps({"output": str(args.out), "totals": index["totals"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
