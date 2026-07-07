#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.ingest.hand_extraction import build_hand_extraction_ledger, write_hand_extraction_ledger


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the OPB hand extraction ledger from the raw file manifest.")
    parser.add_argument("--manifest", type=Path, default=ROOT / "data" / "manifests" / "raw_file_manifest.json")
    parser.add_argument("--out", type=Path, default=ROOT / "data" / "manifests" / "hand_extraction_ledger.json")
    parser.add_argument("--generated-at", default=None)
    parser.add_argument("--progress", action="store_true", help="Print scanned text file paths to stderr.")
    parser.add_argument("--progress-every", type=int, default=50, help="Print progress every N text files.")
    parser.add_argument("--summary", action="store_true", help="Print summary JSON after writing the ledger.")
    args = parser.parse_args()

    ledger = build_hand_extraction_ledger(
        args.manifest,
        generated_at=args.generated_at,
        progress=args.progress,
        progress_every=args.progress_every,
    )
    write_hand_extraction_ledger(ledger, args.out)

    if args.summary:
        print(json.dumps({"output": str(args.out), "totals": ledger["totals"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
