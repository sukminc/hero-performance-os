from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


GG_FILENAME_DATE_RE = re.compile(r"GG(?P<date>\d{8})")
IMAGE_FILENAME_DATE_RE = re.compile(r"(?P<date>\d{4}-\d{2}-\d{2})")
TOURNAMENT_SUMMARY_RE = re.compile(r"^Tournament #(?P<tournament_id>[^,]+),\s*(?P<title>.+)$")


@dataclass(frozen=True)
class DatasetAsset:
    file_id: str
    sha256_12: str
    source_relative_path: str
    canonical_relative_path: str
    original_filename: str
    safe_original_name: str
    extension: str
    input_kind: str
    source_bucket: str
    dataset_asset_kind: str
    processable_state: str
    dataset_date: str
    hand_occurrence_count: int | None = None
    tournament_id: str | None = None
    summary_title: str | None = None


def _slug_filename(filename: str) -> str:
    safe = filename.replace("/", "-").replace("\\", "-").strip()
    safe = re.sub(r"\s+", " ", safe)
    safe = re.sub(r"[^A-Za-z0-9._() \[\],#$&+-]+", "-", safe)
    return safe.strip(" .-") or "unnamed"


def _dataset_date_from_name(filename: str) -> str:
    gg_match = GG_FILENAME_DATE_RE.search(filename)
    if gg_match:
        value = gg_match.group("date")
        return f"{value[0:4]}-{value[4:6]}-{value[6:8]}"

    image_match = IMAGE_FILENAME_DATE_RE.search(filename)
    if image_match:
        return image_match.group("date")

    return "unknown-date"


def _date_parts(dataset_date: str) -> tuple[str, str, str]:
    if dataset_date == "unknown-date":
        return "unknown", "unknown", "unknown"
    year, month, day = dataset_date.split("-")
    return year, month, day


def _read_first_nonempty_line(data_root: Path, relative_path: str) -> str:
    try:
        with (data_root / relative_path).open("r", encoding="utf-8", errors="replace") as handle:
            for line in handle:
                stripped = line.strip()
                if stripped:
                    return stripped
    except OSError:
        return ""
    return ""


def _summary_metadata(data_root: Path, relative_path: str) -> tuple[str | None, str | None]:
    first_line = _read_first_nonempty_line(data_root, relative_path)
    match = TOURNAMENT_SUMMARY_RE.match(first_line)
    if not match:
        return None, None
    return match.group("tournament_id").strip(), match.group("title").strip()


def _canonical_path(
    *,
    player_id: str,
    dataset_date: str,
    dataset_asset_kind: str,
    sha256_12: str,
    safe_original_name: str,
) -> str:
    year, month, day = _date_parts(dataset_date)
    return "/".join(
        [
            "dataset_v0",
            player_id,
            year,
            month,
            day,
            dataset_asset_kind,
            f"{sha256_12}-{safe_original_name}",
        ]
    )


def _asset_kind_and_state(
    raw_file: dict[str, Any],
    hand_count_by_file_id: dict[str, int],
    data_root: Path,
) -> tuple[str, str, int | None, str | None, str | None]:
    input_kind = raw_file.get("input_kind")
    file_id = str(raw_file["file_id"])
    relative_path = str(raw_file["relative_path"])

    if input_kind == "text_hand_history_candidate":
        hand_count = hand_count_by_file_id.get(file_id, 0)
        if hand_count > 0:
            return "hand_history_text", "hand_blocks_extracted", hand_count, None, None

        tournament_id, title = _summary_metadata(data_root, relative_path)
        if tournament_id:
            return "tournament_summary_text", "summary_text_preserved", 0, tournament_id, title
        return "text_unclassified", "text_preserved_zero_hand", 0, None, None

    if input_kind == "zip_archive":
        return "zip_archive", "archive_preserved", None, None, None
    if input_kind == "image_evidence":
        return "image_evidence", "image_preserved_ocr_pending", None, None, None
    if input_kind == "processed_sqlite":
        return "processed_database", "processed_db_preserved", None, None, None
    return "unsupported_source", "unsupported_preserved", None, None, None


def build_processable_dataset_index(
    raw_manifest_path: Path,
    hand_ledger_path: Path,
    *,
    player_id: str = "hero",
    generated_at: str | None = None,
) -> dict[str, Any]:
    raw_manifest_path = raw_manifest_path.expanduser().resolve()
    hand_ledger_path = hand_ledger_path.expanduser().resolve()
    raw_manifest = json.loads(raw_manifest_path.read_text(encoding="utf-8"))
    hand_ledger = json.loads(hand_ledger_path.read_text(encoding="utf-8"))
    data_root = Path(raw_manifest["data_root"]).expanduser().resolve()

    hand_count_by_file_id = {
        str(item["file_id"]): int(item["hand_occurrence_count"])
        for item in hand_ledger.get("files", [])
    }

    assets: list[DatasetAsset] = []
    for raw_file in raw_manifest.get("files", []):
        safe_original_name = _slug_filename(str(raw_file.get("safe_original_name") or raw_file["filename"]))
        dataset_date = _dataset_date_from_name(str(raw_file["filename"]))
        dataset_asset_kind, processable_state, hand_count, tournament_id, summary_title = _asset_kind_and_state(
            raw_file,
            hand_count_by_file_id,
            data_root,
        )
        assets.append(
            DatasetAsset(
                file_id=str(raw_file["file_id"]),
                sha256_12=str(raw_file["sha256_12"]),
                source_relative_path=str(raw_file["relative_path"]),
                canonical_relative_path=_canonical_path(
                    player_id=player_id,
                    dataset_date=dataset_date,
                    dataset_asset_kind=dataset_asset_kind,
                    sha256_12=str(raw_file["sha256_12"]),
                    safe_original_name=safe_original_name,
                ),
                original_filename=str(raw_file["filename"]),
                safe_original_name=safe_original_name,
                extension=str(raw_file["extension"]),
                input_kind=str(raw_file["input_kind"]),
                source_bucket=str(raw_file["source_bucket"]),
                dataset_asset_kind=dataset_asset_kind,
                processable_state=processable_state,
                dataset_date=dataset_date,
                hand_occurrence_count=hand_count,
                tournament_id=tournament_id,
                summary_title=summary_title,
            )
        )

    if generated_at is None:
        generated_at = datetime.now(timezone.utc).isoformat()

    asset_kind_counts = Counter(asset.dataset_asset_kind for asset in assets)
    state_counts = Counter(asset.processable_state for asset in assets)
    date_counts = Counter(asset.dataset_date for asset in assets)
    hand_history_files = [asset for asset in assets if asset.dataset_asset_kind == "hand_history_text"]

    return {
        "schema_version": "processable_dataset_index_v0",
        "generated_at": generated_at,
        "player_id": player_id,
        "raw_manifest_path": str(raw_manifest_path),
        "hand_ledger_path": str(hand_ledger_path),
        "data_root": str(data_root),
        "canonical_root": f"dataset_v0/{player_id}",
        "totals": {
            "asset_count": len(assets),
            "dataset_asset_kind_counts": dict(sorted(asset_kind_counts.items())),
            "processable_state_counts": dict(sorted(state_counts.items())),
            "known_date_asset_count": sum(1 for asset in assets if asset.dataset_date != "unknown-date"),
            "unknown_date_asset_count": date_counts.get("unknown-date", 0),
            "hand_history_text_file_count": len(hand_history_files),
            "hand_history_occurrence_count": sum(asset.hand_occurrence_count or 0 for asset in hand_history_files),
        },
        "assets": [
            {key: value for key, value in asset.__dict__.items() if value is not None}
            for asset in assets
        ],
    }


def write_processable_dataset_index(index: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")
