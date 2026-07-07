from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.ingest.hand_extraction import build_hand_extraction_ledger, split_hand_blocks
from core.ingest.raw_manifest import build_raw_manifest, write_manifest


GG_HAND_1 = """Poker Hand #TM1: Tournament #111, Test Event Hold'em No Limit - Level1(50/100(12)) - 2026/04/01 01:00:00
Table '1' 9-max Seat #1 is the button
Seat 1: Hero (10000 in chips)
Hero: posts small blind 50
*** SUMMARY ***
"""

GG_HAND_2 = """Poker Hand #TM2: Tournament #111, Test Event Hold'em No Limit - Level1(50/100(12)) - 2026/04/01 01:00:10
Table '1' 9-max Seat #2 is the button
Seat 1: Hero (9950 in chips)
Hero: posts big blind 100
*** SUMMARY ***
"""

SIMPLE_HAND = """Hand #S1
Hero wins simple test hand.
"""


def test_split_hand_blocks() -> None:
    blocks = split_hand_blocks(f"ignored preface\n{GG_HAND_1}\n{GG_HAND_2}")
    assert len(blocks) == 2
    assert blocks[0][0] == 2
    assert blocks[0][2][0].startswith("Poker Hand #TM1")


def test_build_hand_extraction_ledger() -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir) / "data"
        root.mkdir()
        (root / "a.txt").write_text(GG_HAND_1 + "\n" + GG_HAND_2, encoding="utf-8")
        (root / "b.txt").write_text(GG_HAND_1 + "\n" + GG_HAND_2, encoding="utf-8")
        (root / "c.txt").write_text(GG_HAND_1 + "\n" + SIMPLE_HAND, encoding="utf-8")

        raw_manifest = build_raw_manifest(root, generated_at="2026-07-07T00:00:00+00:00")
        manifest_path = root / "manifests" / "raw_file_manifest.json"
        write_manifest(raw_manifest, manifest_path)

        ledger = build_hand_extraction_ledger(
            manifest_path,
            generated_at="2026-07-07T00:00:00+00:00",
        )

        assert ledger["schema_version"] == "hand_extraction_ledger_v0"
        assert ledger["totals"]["text_file_count"] == 3
        assert ledger["totals"]["hand_occurrence_count"] == 6
        assert ledger["totals"]["unique_hand_fingerprint_count"] == 3
        assert ledger["totals"]["duplicate_hand_group_count"] == 2
        assert ledger["totals"]["duplicate_hand_occurrence_count"] == 5
        assert ledger["totals"]["header_parse_status_counts"] == {"parsed": 5, "unparsed": 1}

        duplicate_records = [item for item in ledger["hands"] if item.get("duplicate_group_id")]
        assert len(duplicate_records) == 5
        assert any(item["hand_ref"] == "TM1" for item in ledger["hands"])
        assert any(item["hand_ref"] == "S1" for item in ledger["hands"])


if __name__ == "__main__":
    test_split_hand_blocks()
    test_build_hand_extraction_ledger()
    print("Hand extraction tests passed.")
