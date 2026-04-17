from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from datetime import UTC, datetime, timedelta
from typing import Any

from core.storage.sqlite import get_sqlite_connection
from app.api.hand_matrix import HERO_PLAYER_ID, _extract_format_tag, _parse_json, _parse_started_at
from app.api.hud_trend import _extract_tournament_id, _street_actions, _street_reached


SUPPORTED_WINDOWS = {"90d", "all"}


def _hero_position(block: list[str]) -> str | None:
    for row in block:
        if "(button)" in row and "Hero" in row:
            return "button"
        if "Hero (small blind)" in row:
            return "small blind"
        if "Hero (big blind)" in row:
            return "big blind"
    for row in block:
        if row.startswith("Seat ") and "Hero" in row:
            if "(button)" in row:
                return "button"
    return None


def _preflop_rows(block: list[str]) -> list[str]:
    rows = []
    in_preflop = False
    for row in block:
        if row == "*** HOLE CARDS ***":
            in_preflop = True
            continue
        if not in_preflop:
            continue
        if row.startswith("*** FLOP ***") or row.startswith("*** SHOWDOWN ***") or row.startswith("*** SUMMARY ***"):
            break
        rows.append(row)
    return rows


def _count_limpers(preflop_rows: list[str]) -> int:
    limpers = 0
    prior_raise = False
    for row in preflop_rows:
        if ":" not in row:
            continue
        actor, remainder = row.split(":", 1)
        if actor == "Hero":
            continue
        remainder = remainder.strip()
        if remainder.startswith("calls ") and not prior_raise:
            limpers += 1
        elif remainder.startswith("raises "):
            prior_raise = True
    return limpers


def _has_limp_shove(preflop_rows: list[str]) -> bool:
    actor_state: dict[str, str] = {}
    for row in preflop_rows:
        if ":" not in row:
            continue
        actor, remainder = row.split(":", 1)
        remainder = remainder.strip()
        if remainder.startswith("calls "):
            actor_state[actor] = "limped"
        elif remainder.startswith("raises ") and "all-in" in remainder and actor_state.get(actor) == "limped":
            return True
        elif remainder.startswith("raises "):
            actor_state[actor] = "raised"
    return False


def _has_open_4x(preflop_rows: list[str], header: str) -> bool:
    blind_match = re.search(r"Level\d+\(([\d,]+)/([\d,]+)", header)
    if not blind_match:
        return False
    big_blind = int(blind_match.group(2).replace(",", ""))
    prior_raise = False
    for row in preflop_rows:
        if ":" not in row:
            continue
        actor, remainder = row.split(":", 1)
        remainder = remainder.strip()
        if actor == "Hero":
            continue
        if remainder.startswith("raises ") and not prior_raise:
            match = re.search(r"to ([\d,]+)", remainder)
            if not match:
                return False
            open_to = int(match.group(1).replace(",", ""))
            return open_to >= big_blind * 4
        if remainder.startswith("raises "):
            prior_raise = True
    return False


def _has_donk(actions: dict[str, list[dict[str, str]]], block: list[str]) -> bool:
    preflop_actions = actions["preflop"]
    aggressors = [action["actor"] for action in preflop_actions if action["action"] == "raise"]
    if not aggressors or not actions["flop"]:
        return False
    preflop_aggressor = aggressors[-1]
    first_flop_action = actions["flop"][0]
    return first_flop_action["actor"] != preflop_aggressor and first_flop_action["action"] in {"bet", "raise"}


def _hero_limp_multiway_reaction(preflop_rows: list[str], block: list[str]) -> str | None:
    limpers = _count_limpers(preflop_rows)
    if limpers < 1 or not _street_reached(block, "flop"):
        return None
    actions = _street_actions(block)
    if len(actions["flop"]) < 2:
        return None
    hero_flop_action = next((action for action in actions["flop"] if action["actor"] == "Hero"), None)
    if not hero_flop_action:
        return None
    if hero_flop_action["action"] in {"bet", "raise"}:
        return "aggressive"
    if hero_flop_action["action"] == "call":
        return "continue"
    if hero_flop_action["action"] in {"check", "fold"}:
        return "passive"
    return None


def _fetch_field_observations(player_id: str, window: str) -> list[dict[str, Any]]:
    cutoff = None
    if window == "90d":
        cutoff = datetime.now(UTC) - timedelta(days=90)
    observations = []
    with get_sqlite_connection() as conn:
        rows = conn.execute(
            """
            SELECT hands.id, hands.raw_payload, sessions.started_at, sessions.session_metadata
            FROM hands
            JOIN sessions ON sessions.id = hands.session_id
            WHERE sessions.player_id = ?
            ORDER BY sessions.started_at DESC
            """,
            (player_id,),
        ).fetchall()
    for row in rows:
        started_at = _parse_started_at(row["started_at"])
        if cutoff and started_at and started_at < cutoff:
            continue
        raw_payload = _parse_json(row["raw_payload"], {})
        session_metadata = _parse_json(row["session_metadata"], {})
        block = raw_payload.get("block") or []
        header = raw_payload.get("header") or ""
        preflop_rows = _preflop_rows(block)
        actions = _street_actions(block)
        observations.append(
            {
                "hand_id": row["id"],
                "tournament_id": _extract_tournament_id(header, session_metadata),
                "started_at": row["started_at"],
                "format_tag": _extract_format_tag(header, session_metadata),
                "limpers": _count_limpers(preflop_rows),
                "limp_shove": _has_limp_shove(preflop_rows),
                "open_4x": _has_open_4x(preflop_rows, header),
                "donk_flop": _has_donk(actions, block),
                "multiway_flop": _street_reached(block, "flop") and sum(1 for action in actions["flop"] if action["action"] in {"check", "call", "bet", "raise"}) >= 3,
                "hero_limp_multiway_reaction": _hero_limp_multiway_reaction(preflop_rows, block),
            }
        )
    return observations


def _safe_pct(numerator: int, denominator: int) -> float | None:
    if denominator <= 0:
        return None
    return round((numerator / denominator) * 100, 1)


def _latest_cut(observations: list[dict[str, Any]], days: int = 7) -> list[dict[str, Any]]:
    parsed = [_parse_started_at(item["started_at"]) for item in observations if item.get("started_at")]
    parsed = [item for item in parsed if item is not None]
    if not parsed:
        return []
    latest = max(parsed)
    cutoff = latest - timedelta(days=days - 1)
    result = []
    for item in observations:
        started_at = _parse_started_at(item.get("started_at"))
        if started_at and started_at >= cutoff:
            result.append(item)
    return result


def _build_format_split(observations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = _latest_cut(observations, days=7)
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in rows:
        grouped[item["format_tag"]].append(item)

    result = []
    for format_tag, items in sorted(grouped.items()):
        total = len(items)
        limp_multiway_spots = [item for item in items if item["limpers"] >= 1 and item["multiway_flop"]]
        passive_reacts = [item for item in limp_multiway_spots if item["hero_limp_multiway_reaction"] == "passive"]
        result.append(
            {
                "format_tag": format_tag,
                "hands": total,
                "limper_rate": _safe_pct(sum(1 for item in items if item["limpers"] >= 1), total),
                "donk_rate": _safe_pct(sum(1 for item in items if item["donk_flop"]), total),
                "limp_shove_rate": _safe_pct(sum(1 for item in items if item["limp_shove"]), total),
                "open_4x_rate": _safe_pct(sum(1 for item in items if item["open_4x"]), total),
                "multiway_flop_rate": _safe_pct(sum(1 for item in items if item["multiway_flop"]), total),
                "hero_passive_limp_multiway_rate": _safe_pct(len(passive_reacts), len(limp_multiway_spots)),
            }
        )
    return result


def get_field_ecology_payload(player_id: str = HERO_PLAYER_ID, window: str = "90d") -> dict[str, Any]:
    resolved_player_id = player_id or HERO_PLAYER_ID
    resolved_window = window if window in SUPPORTED_WINDOWS else "90d"
    observations = _fetch_field_observations(resolved_player_id, resolved_window)
    last7 = _latest_cut(observations, days=7)
    total = len(last7)
    limp_multiway_spots = [item for item in last7 if item["limpers"] >= 1 and item["multiway_flop"]]
    hero_reaction_counts = defaultdict(int)
    for item in limp_multiway_spots:
        if item["hero_limp_multiway_reaction"]:
            hero_reaction_counts[item["hero_limp_multiway_reaction"]] += 1

    headline = "Field ecology sample is still thin."
    if total:
        limper_rate = _safe_pct(sum(1 for item in last7 if item["limpers"] >= 1), total) or 0
        donk_rate = _safe_pct(sum(1 for item in last7 if item["donk_flop"]), total) or 0
        if limper_rate >= 25 or donk_rate >= 10:
            headline = "Recent field ecology is loose enough that blind aggression and limp-multiway response should be reviewed as context, not noise."
        else:
            headline = "Recent field ecology is present but not extreme enough to excuse baseline drift by itself."

    ecology_cards = [
        {
            "label": "Limpers",
            "value": _safe_pct(sum(1 for item in last7 if item["limpers"] >= 1), total),
            "meaning": "How often at least one open limp appears in the hand.",
        },
        {
            "label": "Donk Flop",
            "value": _safe_pct(sum(1 for item in last7 if item["donk_flop"]), total),
            "meaning": "How often a non-preflop-aggressor leads flop action.",
        },
        {
            "label": "Limp-Shove",
            "value": _safe_pct(sum(1 for item in last7 if item["limp_shove"]), total),
            "meaning": "How often a limper later back-jams preflop.",
        },
        {
            "label": "Open 4x",
            "value": _safe_pct(sum(1 for item in last7 if item["open_4x"]), total),
            "meaning": "How often the first open raise is 4x or bigger.",
        },
        {
            "label": "Multiway Flop",
            "value": _safe_pct(sum(1 for item in last7 if item["multiway_flop"]), total),
            "meaning": "How often the hand reaches a genuinely sticky multiway flop texture.",
        },
    ]

    hero_limp_multiway = {
        "spots": len(limp_multiway_spots),
        "reaction_mix": dict(sorted(hero_reaction_counts.items())),
        "passive_rate": _safe_pct(hero_reaction_counts.get("passive", 0), len(limp_multiway_spots)),
        "aggressive_rate": _safe_pct(hero_reaction_counts.get("aggressive", 0), len(limp_multiway_spots)),
        "continue_rate": _safe_pct(hero_reaction_counts.get("continue", 0), len(limp_multiway_spots)),
        "interpretation": "This block shows whether limp-multiway textures are pulling Hero toward passive compliance, controlled continuation, or active punishment.",
    }

    return {
        "status": "ok",
        "player_id": resolved_player_id,
        "summary": {
            "window": resolved_window,
            "hands": total,
            "headline": headline,
        },
        "ecology_cards": ecology_cards,
        "hero_limp_multiway": hero_limp_multiway,
        "format_splits": _build_format_split(observations),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Read the field ecology payload.")
    parser.add_argument("--player-id", default=HERO_PLAYER_ID, help="Player id to inspect.")
    parser.add_argument("--window", default="90d", choices=sorted(SUPPORTED_WINDOWS))
    args = parser.parse_args()
    payload = get_field_ecology_payload(player_id=args.player_id, window=args.window)
    print(json.dumps(payload, indent=2, default=str))


if __name__ == "__main__":
    main()
