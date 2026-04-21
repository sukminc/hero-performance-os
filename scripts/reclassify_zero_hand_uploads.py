from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from core.parsing.gg_parser import parse_gg_text_file


DB_PATH = Path("/Users/chrisyoon/GitHub/opb-poker/data/hero_v2.sqlite3")


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """
        select id, source_path
        from ingest_files
        where status = 'failed_zero_hands'
        order by uploaded_at desc
        """
    ).fetchall()

    reclassified = 0
    for row in rows:
        source_path = row["source_path"]
        if not source_path:
            continue
        path = Path(source_path)
        if not path.exists():
            continue
        parsed = parse_gg_text_file(path)
        if parsed.hands or parsed.parse_quality.get("parser_mode") != "tournament_summary_only":
            continue
        raw_metadata = json.dumps({"parse_quality": parsed.parse_quality, "source_path": str(path)})
        conn.execute(
            """
            update ingest_files
            set status = ?, raw_metadata = ?, updated_at = datetime('now')
            where id = ?
            """,
            ("skipped_summary_only", raw_metadata, row["id"]),
        )
        reclassified += 1

    conn.commit()
    conn.close()
    print(f"reclassified={reclassified}")


if __name__ == "__main__":
    main()
