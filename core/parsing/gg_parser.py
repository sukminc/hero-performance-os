from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SUMMARY_HEADER_RE = re.compile(r"^Tournament #(?P<tournament_id>[^,]+), (?P<title>.+)$")
HAND_HEADER_RE = re.compile(
    r"^Poker Hand #(?P<hand_ref>[^:]+):\s+Tournament #(?P<tournament_id>[^,]+),\s+"
    r"(?P<label>.+?)\s+-\s+Level\s*(?P<level>\d+)\("
    r"(?P<small_blind>[\d,]+)\s*/\s*(?P<big_blind>[\d,]+)"
    r"(?:\s*/\s*(?P<button_ante>[\d,]+)|\((?P<ante>[\d,]+)\))?"
    r"\)\s+-\s+(?P<played_at>.+)$"
)
SEAT_STACK_RE = re.compile(
    r"^Seat\s+\d+:\s+(?P<player_name>.+?)\s+\((?P<stack>[\d,]+)\s+in chips(?:,\s*[^)]*)?\)$"
)


@dataclass(slots=True)
class ParsedHand:
    hand_id: str
    header_metadata: dict[str, Any]
    hero_position: str | None
    effective_stack_bb: float | None
    players_to_flop: int | None
    board_texture_summary: str | None
    result_summary: dict[str, Any]
    raw_payload: dict[str, Any]


@dataclass(slots=True)
class ParsedSessionPacket:
    session_key: str
    source_path: str
    metadata: dict[str, Any]
    hands: list[ParsedHand]
    parse_quality: dict[str, Any]


def parse_amount(value: str) -> int:
    digits = re.sub(r"[^\d-]", "", value)
    return int(digits) if digits else 0


def parse_hand_header(header: str) -> dict[str, Any]:
    normalized = " ".join(header.strip().split())
    match = HAND_HEADER_RE.match(normalized)
    if not match:
        return {}

    metadata = match.groupdict()
    metadata["level"] = int(metadata["level"])
    metadata["small_blind"] = parse_amount(metadata["small_blind"])
    metadata["big_blind"] = parse_amount(metadata["big_blind"])
    metadata["ante"] = parse_amount(str(metadata.get("ante") or "0"))
    metadata["button_ante"] = parse_amount(str(metadata.get("button_ante") or "0"))
    metadata["header_format"] = "gg_real"
    return metadata


def _session_key_from_path(path: Path) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", path.stem.lower()).strip("-")
    return slug or "gg-session"


def _parse_metadata(lines: list[str]) -> tuple[dict[str, Any], int]:
    metadata: dict[str, Any] = {}
    hand_start = len(lines)
    for idx, line in enumerate(lines):
        if line.startswith("Poker Hand") or line.startswith("Hand #"):
            hand_start = idx
            break
        if line and ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip().lower()] = value.strip()
    if hand_start < len(lines):
        header_meta = parse_hand_header(lines[hand_start])
        if header_meta:
            metadata.setdefault("date", header_meta.get("played_at"))
            metadata.setdefault("stakes", header_meta.get("label"))
            metadata.setdefault("tournament_id", header_meta.get("tournament_id"))
    return metadata, hand_start


def _parse_blocks(lines: list[str], start: int) -> list[list[str]]:
    blocks: list[list[str]] = []
    current: list[str] = []
    for line in lines[start:]:
        if not line.strip():
            if current:
                blocks.append(current)
                current = []
            continue
        if line.startswith("Poker Hand") or line.startswith("Hand #"):
            if current:
                blocks.append(current)
            current = [line]
        elif current:
            current.append(line)
    if current:
        blocks.append(current)
    return blocks


def _parse_simple_blocks(lines: list[str], start: int) -> list[list[str]]:
    blocks: list[list[str]] = []
    current: list[str] = []
    for line in lines[start:]:
        if not line.strip():
            if current:
                blocks.append(current)
                current = []
            continue
        if line.startswith("Hand #"):
            if current:
                blocks.append(current)
            current = [line]
        elif current:
            current.append(line)
    if current:
        blocks.append(current)
    return blocks


def _extract_stack_from_seat_row(row: str) -> tuple[str | None, int]:
    match = SEAT_STACK_RE.match(row.strip())
    if not match:
        return None, 0
    return match.group("player_name").strip(), parse_amount(match.group("stack"))


def _extract_hero_position(summary_line: str, hero_actions: list[str]) -> str | None:
    position_match = re.search(r"Hero \(([^)]+)\)", summary_line)
    if position_match:
        return position_match.group(1)
    if any("posts small blind" in row for row in hero_actions):
        return "small blind"
    if any("posts big blind" in row for row in hero_actions):
        return "big blind"
    return None


def parse_gg_text_file(path: Path) -> ParsedSessionPacket:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    metadata, hand_start = _parse_metadata(lines)
    blocks = _parse_blocks(lines, hand_start)
    hands: list[ParsedHand] = []
    skipped_blocks = 0
    real_blocks = 0
    simple_block_count = 0

    for index, block in enumerate(blocks, start=1):
        header = block[0]
        header_meta = parse_hand_header(header)
        if not header_meta:
            skipped_blocks += 1
            continue
        real_blocks += 1

        hero_actions: list[str] = []
        hero_summary = ""
        hero_start_stack = 0
        board = ""
        current_street = "blind"
        saw_flop = False
        hero_name = "Hero"
        players_seen_flop: set[str] = set()

        for row in block[1:]:
            stripped = row.strip()
            if stripped.startswith("*** FLOP ***"):
                current_street = "flop"
                saw_flop = True
            elif stripped.startswith("*** TURN ***"):
                current_street = "turn"
            elif stripped.startswith("*** RIVER ***"):
                current_street = "river"
            elif stripped.startswith("*** SUMMARY ***"):
                current_street = "summary"

            if row.startswith("Seat "):
                player_name, stack_amount = _extract_stack_from_seat_row(row)
                if player_name == hero_name and stack_amount:
                    hero_start_stack = stack_amount

            action_match = re.match(r"^(?P<player>[^:]+):\s+(?P<action>.+)$", stripped)
            if action_match:
                player_name = action_match.group("player").strip()
                action_text = action_match.group("action").strip()
                if player_name == hero_name:
                    hero_actions.append(stripped)
                if current_street == "flop":
                    normalized_action = action_text.lower()
                    if not normalized_action.startswith("doesn't show") and not normalized_action.startswith("has"):
                        players_seen_flop.add(player_name)

            if current_street == "summary":
                if stripped.startswith("Seat ") and "Hero" in stripped:
                    hero_summary = stripped
                if stripped.startswith("Board ["):
                    board = stripped

        big_blind = int(header_meta.get("big_blind", 0) or 0)
        effective_stack_bb = round(hero_start_stack / big_blind, 2) if hero_start_stack and big_blind else None
        players_to_flop = len(players_seen_flop) if players_seen_flop else (2 if saw_flop else None)
        hand_external_id = str(header_meta.get("hand_ref") or index)

        hands.append(
            ParsedHand(
                hand_id=f"{_session_key_from_path(path)}:{hand_external_id}",
                header_metadata=header_meta,
                hero_position=_extract_hero_position(hero_summary, hero_actions),
                effective_stack_bb=effective_stack_bb,
                players_to_flop=players_to_flop,
                board_texture_summary=board or None,
                result_summary={
                    "hero_summary": hero_summary,
                    "hero_actions": hero_actions,
                },
                raw_payload={
                    "header": header,
                    "block": block,
                },
            )
        )

    if not hands:
        simple_blocks = _parse_simple_blocks(lines, hand_start)
        simple_block_count = len(simple_blocks)
        for index, block in enumerate(simple_blocks, start=1):
            if not block or not block[0].startswith("Hand #"):
                continue

            hand_ref = block[0].replace("Hand #", "").strip() or str(index)
            result_value = 0
            result_line = ""
            hero_action = ""
            summary = ""
            pattern = ""
            table_name = ""

            for row in block[1:]:
                if row.startswith("Result:"):
                    result_line = row.split(":", 1)[1].strip()
                    result_value = parse_amount(result_line)
                elif row.startswith("Hero action:"):
                    hero_action = row.split(":", 1)[1].strip()
                elif row.startswith("Summary:"):
                    summary = row.split(":", 1)[1].strip()
                elif row.startswith("Pattern:"):
                    pattern = row.split(":", 1)[1].strip()
                elif row.startswith("Table:"):
                    table_name = row.split(":", 1)[1].strip()

            hands.append(
                ParsedHand(
                    hand_id=f"{_session_key_from_path(path)}:{hand_ref}",
                header_metadata={
                        "hand_ref": hand_ref,
                        "tournament_id": metadata.get("session") or metadata.get("tournament_id"),
                        "label": metadata.get("stakes"),
                        "played_at": metadata.get("date"),
                        "table_name": table_name,
                        "header_format": "simple_fixture",
                    },
                    hero_position=None,
                    effective_stack_bb=None,
                    players_to_flop=2 if hero_action else None,
                    board_texture_summary=None,
                    result_summary={
                        "hero_summary": summary,
                        "hero_actions": [hero_action] if hero_action else [],
                        "result_value": result_value,
                        "pattern": pattern,
                    },
                    raw_payload={
                        "header": block[0],
                        "block": block,
                        "simple_format": True,
                    },
                )
            )

    parse_quality = {
        "total_blocks": real_blocks or simple_block_count or len(blocks),
        "raw_block_count": len(blocks),
        "parsed_hands": len(hands),
        "skipped_blocks": skipped_blocks,
        "zero_hand_parse": len(hands) == 0,
        "parser_mode": "simple_fixture_fallback" if hands and real_blocks == 0 else "gg_real",
        "real_style_block_count": real_blocks,
        "simple_block_count": simple_block_count,
    }

    return ParsedSessionPacket(
        session_key=_session_key_from_path(path),
        source_path=str(path),
        metadata=metadata,
        hands=hands,
        parse_quality=parse_quality,
    )
