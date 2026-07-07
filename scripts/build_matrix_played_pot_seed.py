#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.ingest.matrix_played_pot_seed import build_matrix_played_pot_seed, write_matrix_played_pot_seed


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the OPB 13x13 matrix played-pot seed.")
    parser.add_argument("--matrix-result-seed", type=Path, default=ROOT / "data" / "manifests" / "matrix_result_seed.json")
    parser.add_argument("--out", type=Path, default=ROOT / "data" / "manifests" / "matrix_played_pot_seed.json")
    parser.add_argument("--generated-at", default=None)
    parser.add_argument("--summary", action="store_true", help="Print summary JSON after writing the seed.")
    args = parser.parse_args()

    seed = build_matrix_played_pot_seed(
        args.matrix_result_seed,
        generated_at=args.generated_at,
    )
    write_matrix_played_pot_seed(seed, args.out)

    if args.summary:
        print(json.dumps({"output": str(args.out), "totals": seed["totals"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
