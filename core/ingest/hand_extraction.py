from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


HAND_START_PREFIXES = ("Poker Hand #", "Hand #")
HAND_REF_RE = re.compile(r"^(?:Poker Hand #|Hand #)(?P<hand_ref>[^:\s]+)")
GG_HEADER_RE = re.compile(
    r"^Poker Hand #(?P<hand_ref>[^:]+):\s+Tournament #(?P<tournament_id>[^,]+),\s+"
    r"(?P<label>.+?)\s+-\s+Level\s*(?P<level>\d+)\(.+?\)\s+-\s+(?P<played_at>.+)$"
)


@dataclass(frozen=True)
class ExtractedHandBlock:
    source_file_id: str
    source_relative_path: str
    source_sequence: int
    line_start: int
    line_end: int
    hand_fingerprint: str
    hand_fingerprint_12: str
    header: str
    hand_ref: str | None
    tournament_id: str | None
    played_at: str | None
    header_parse_status: str
    line_count: int
    byte_count: int


def normalize_hand_block(lines: list[str]) -> str:
    trimmed = [line.rstrip() for line in lines]
    while trimmed and not trimmed[0].strip():
        trimmed.pop(0)
    while trimmed and not trimmed[-1].strip():
        trimmed.pop()
    return "\n".join(trimmed) + "\n" if trimmed else ""


def _is_hand_start(line: str) -> bool:
    return line.startswith(HAND_START_PREFIXES)


def split_hand_blocks(text: str) -> list[tuple[int, int, list[str]]]:
    blocks: list[tuple[int, int, list[str]]] = []
    current_start: int | None = None
    current_lines: list[str] = []

    for line_number, line in enumerate(text.splitlines(), start=1):
        if _is_hand_start(line):
            if current_start is not None and current_lines:
                blocks.append((current_start, line_number - 1, current_lines))
            current_start = line_number
            current_lines = [line]
            continue
        if current_start is not None:
            current_lines.append(line)

    if current_start is not None and current_lines:
        blocks.append((current_start, current_start + len(current_lines) - 1, current_lines))
    return blocks


def _extract_hand_ref(header: str) -> str | None:
    match = HAND_REF_RE.match(header.strip())
    return match.group("hand_ref") if match else None


def parse_minimal_gg_header(header: str) -> dict[str, str]:
    match = GG_HEADER_RE.match(" ".join(header.strip().split()))
    return match.groupdict() if match else {}


def extract_hands_from_text_file(path: Path, *, source_file_id: str, source_relative_path: str) -> list[ExtractedHandBlock]:
    text = path.read_text(encoding="utf-8", errors="replace")
    extracted: list[ExtractedHandBlock] = []

    for sequence, (line_start, line_end, lines) in enumerate(split_hand_blocks(text), start=1):
        normalized = normalize_hand_block(lines)
        if not normalized:
            continue
        digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
        header = lines[0].strip()
        header_metadata = parse_minimal_gg_header(header)
        extracted.append(
            ExtractedHandBlock(
                source_file_id=source_file_id,
                source_relative_path=source_relative_path,
                source_sequence=sequence,
                line_start=line_start,
                line_end=line_end,
                hand_fingerprint=digest,
                hand_fingerprint_12=digest[:12],
                header=header,
                hand_ref=_extract_hand_ref(header),
                tournament_id=str(header_metadata.get("tournament_id")) if header_metadata.get("tournament_id") else None,
                played_at=str(header_metadata.get("played_at")) if header_metadata.get("played_at") else None,
                header_parse_status="parsed" if header_metadata else "unparsed",
                line_count=len(lines),
                byte_count=len(normalized.encode("utf-8")),
            )
        )
    return extracted


def _text_candidate_files(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        item
        for item in manifest.get("files", [])
        if item.get("input_kind") == "text_hand_history_candidate"
    ]


def _duplicate_groups(hands: list[ExtractedHandBlock]) -> dict[str, str]:
    by_fingerprint: dict[str, list[ExtractedHandBlock]] = defaultdict(list)
    for hand in hands:
        by_fingerprint[hand.hand_fingerprint].append(hand)
    duplicate_group_by_fingerprint: dict[str, str] = {}
    for fingerprint, items in sorted(by_fingerprint.items()):
        if len(items) > 1:
            duplicate_group_by_fingerprint[fingerprint] = f"hand-dup-{fingerprint[:12]}"
    return duplicate_group_by_fingerprint


def _record_for(hand: ExtractedHandBlock, duplicate_group_by_fingerprint: dict[str, str]) -> dict[str, Any]:
    record = {
        "hand_occurrence_id": f"{hand.source_file_id}:{hand.source_sequence}",
        "hand_fingerprint": hand.hand_fingerprint,
        "hand_fingerprint_12": hand.hand_fingerprint_12,
        "duplicate_group_id": duplicate_group_by_fingerprint.get(hand.hand_fingerprint),
        "source_file_id": hand.source_file_id,
        "source_relative_path": hand.source_relative_path,
        "source_sequence": hand.source_sequence,
        "line_start": hand.line_start,
        "line_end": hand.line_end,
        "header": hand.header,
        "hand_ref": hand.hand_ref,
        "tournament_id": hand.tournament_id,
        "played_at": hand.played_at,
        "header_parse_status": hand.header_parse_status,
        "line_count": hand.line_count,
        "byte_count": hand.byte_count,
    }
    return {key: value for key, value in record.items() if value is not None}


def build_hand_extraction_ledger(
    manifest_path: Path,
    *,
    generated_at: str | None = None,
    progress: bool = False,
    progress_every: int = 50,
) -> dict[str, Any]:
    manifest_path = manifest_path.expanduser().resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    data_root = Path(manifest["data_root"]).expanduser().resolve()
    text_files = _text_candidate_files(manifest)

    all_hands: list[ExtractedHandBlock] = []
    per_file: list[dict[str, Any]] = []
    for index, item in enumerate(text_files, start=1):
        relative_path = str(item["relative_path"])
        source_file_id = str(item["file_id"])
        should_print_progress = (
            progress
            and (index == 1 or index == len(text_files) or index % max(progress_every, 1) == 0)
        )
        if should_print_progress:
            print(f"[{index}/{len(text_files)}] {relative_path}", file=sys.stderr, flush=True)

        path = data_root / relative_path
        try:
            hands = extract_hands_from_text_file(
                path,
                source_file_id=source_file_id,
                source_relative_path=relative_path,
            )
            status = "extracted"
            error = None
        except OSError as exc:
            hands = []
            status = "read_error"
            error = exc.__class__.__name__

        all_hands.extend(hands)
        per_file_record = {
            "file_id": source_file_id,
            "relative_path": relative_path,
            "hand_occurrence_count": len(hands),
            "status": status,
        }
        if error:
            per_file_record["error"] = error
        per_file.append(per_file_record)

    duplicate_group_by_fingerprint = _duplicate_groups(all_hands)
    header_status_counts = Counter(hand.header_parse_status for hand in all_hands)
    hands_by_fingerprint = Counter(hand.hand_fingerprint for hand in all_hands)
    duplicate_occurrence_count = sum(count for count in hands_by_fingerprint.values() if count > 1)

    if generated_at is None:
        generated_at = datetime.now(timezone.utc).isoformat()

    return {
        "schema_version": "hand_extraction_ledger_v0",
        "generated_at": generated_at,
        "raw_manifest_path": str(manifest_path),
        "data_root": str(data_root),
        "totals": {
            "text_file_count": len(text_files),
            "files_with_hands": sum(1 for item in per_file if item["hand_occurrence_count"] > 0),
            "files_with_zero_hands": sum(1 for item in per_file if item["hand_occurrence_count"] == 0),
            "hand_occurrence_count": len(all_hands),
            "unique_hand_fingerprint_count": len(hands_by_fingerprint),
            "duplicate_hand_group_count": len(duplicate_group_by_fingerprint),
            "duplicate_hand_occurrence_count": duplicate_occurrence_count,
            "header_parse_status_counts": dict(sorted(header_status_counts.items())),
        },
        "files": per_file,
        "hands": [_record_for(hand, duplicate_group_by_fingerprint) for hand in all_hands],
    }


def write_hand_extraction_ledger(ledger: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(ledger, indent=2, sort_keys=True) + "\n", encoding="utf-8")
