#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.ingest.raw_manifest import build_raw_manifest, write_manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the OPB raw file manifest from preserved data files.")
    parser.add_argument("--data-root", type=Path, default=ROOT / "data")
    parser.add_argument("--out", type=Path, default=ROOT / "data" / "manifests" / "raw_file_manifest.json")
    parser.add_argument("--generated-at", default=None)
    parser.add_argument("--count-text-hands", action="store_true", help="Count Poker Hand blocks in text files.")
    parser.add_argument("--progress", action="store_true", help="Print scanned file paths to stderr.")
    parser.add_argument("--progress-every", type=int, default=50, help="Print progress every N files when --progress is set.")
    parser.add_argument("--summary", action="store_true", help="Print summary JSON after writing the manifest.")
    args = parser.parse_args()

    manifest = build_raw_manifest(
        args.data_root,
        generated_at=args.generated_at,
        count_text_hands=args.count_text_hands,
        progress=args.progress,
        progress_every=args.progress_every,
    )
    write_manifest(manifest, args.out)

    if args.summary:
        print(json.dumps({"output": str(args.out), "totals": manifest["totals"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
