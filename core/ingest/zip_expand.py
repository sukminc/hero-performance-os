from __future__ import annotations

import argparse
import json
from pathlib import Path
from zipfile import ZipFile


def main() -> None:
    parser = argparse.ArgumentParser(description="Expand uploaded zip archives into raw GG text files.")
    parser.add_argument("--zip", dest="zip_path", type=Path, required=True, help="Zip archive path.")
    parser.add_argument("--out", dest="out_dir", type=Path, required=True, help="Extraction destination directory.")
    args = parser.parse_args()

    zip_path = args.zip_path.expanduser().resolve()
    out_dir = args.out_dir.expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    extracted_files: list[str] = []
    skipped_entries: list[str] = []

    with ZipFile(zip_path) as archive:
        for member in archive.infolist():
            if member.is_dir():
                continue
            member_name = Path(member.filename)
            if member_name.name.startswith(".") or member_name.suffix.lower() != ".txt":
                skipped_entries.append(member.filename)
                continue
            safe_name = member_name.name
            destination = out_dir / safe_name
            counter = 1
            while destination.exists():
                destination = out_dir / f"{member_name.stem}-{counter}{member_name.suffix}"
                counter += 1
            destination.write_bytes(archive.read(member))
            extracted_files.append(str(destination))

    print(
        json.dumps(
            {
                "zip_path": str(zip_path),
                "out_dir": str(out_dir),
                "extracted_files": extracted_files,
                "skipped_entries": skipped_entries,
            }
        )
    )


if __name__ == "__main__":
    main()
