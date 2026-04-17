from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from core.storage.sqlite import get_sqlite_connection
from app.api.hand_matrix import (
    HERO_PLAYER_ID,
    _extract_format_tag,
    _extract_hero_position,
    _parse_json,
    _parse_started_at,
)


SUPPORTED_WINDOWS = {"90d", "all"}


@dataclass
class HudHandObservation:
    tournament_id: str
    started_at: str | None
    format_tag: str
    position: str | None
    saw_flop: bool
    vpip: bool
    pfr: bool
    ats_opportunity: bool
    ats_attempt: bool
    three_bet_opportunity: bool
    three_bet: bool
    flop_cbet_opportunity: bool
    flop_cbet: bool
    turn_cbet_opportunity: bool
    turn_cbet: bool
    river_opportunity: bool
    river_aggressive: bool
    showdown: bool
    showdown_win: bool


def _extract_tournament_id(header: str, session_metadata: dict[str, Any]) -> str:
    metadata_id = str(session_metadata.get("tournament_id") or "").strip()
    if metadata_id:
        return metadata_id
    match = re.search(r"Tournament #(\d+)", header)
    if match:
        return match.group(1)
    return "unknown_tournament"


def _street_actions(block: list[str]) -> dict[str, list[dict[str, str]]]:
    actions = {"preflop": [], "flop": [], "turn": [], "river": []}
    current_street = None
    for row in block:
        if row == "*** HOLE CARDS ***":
            current_street = "preflop"
            continue
        if row.startswith("*** FLOP ***"):
            current_street = "flop"
            continue
        if row.startswith("*** TURN ***"):
            current_street = "turn"
            continue
        if row.startswith("*** RIVER ***"):
            current_street = "river"
            continue
        if row.startswith("*** SHOWDOWN ***") or row.startswith("*** SUMMARY ***"):
            current_street = None
            continue
        if current_street is None or ":" not in row:
            continue
        actor, remainder = row.split(":", 1)
        remainder = remainder.strip()
        if remainder.startswith("folds"):
            action = "fold"
        elif remainder.startswith("checks"):
            action = "check"
        elif remainder.startswith("calls"):
            action = "call"
        elif remainder.startswith("bets"):
            action = "bet"
        elif remainder.startswith("raises"):
            action = "raise"
        else:
            continue
        actions[current_street].append({"actor": actor, "action": action, "row": row})
    return actions


def _hero_not_folded_preflop(preflop_actions: list[dict[str, str]]) -> bool:
    for action in preflop_actions:
        if action["actor"] == "Hero":
            return action["action"] != "fold"
    return True


def _hero_first_action(street_actions: list[dict[str, str]]) -> dict[str, str] | None:
    for action in street_actions:
        if action["actor"] == "Hero":
            return action
    return None


def _had_prior_raise(actions: list[dict[str, str]], index: int) -> int:
    return sum(1 for action in actions[:index] if action["action"] == "raise")


def _find_preflop_stats(position: str | None, preflop_actions: list[dict[str, str]]) -> dict[str, bool]:
    vpip = False
    pfr = False
    ats_opportunity = False
    ats_attempt = False
    three_bet_opportunity = False
    three_bet = False

    hero_index = None
    for index, action in enumerate(preflop_actions):
        if action["actor"] != "Hero":
            continue
        hero_index = index
        break

    if hero_index is None:
        return {
            "vpip": False,
            "pfr": False,
            "ats_opportunity": False,
            "ats_attempt": False,
            "three_bet_opportunity": False,
            "three_bet": False,
        }

    hero_action = preflop_actions[hero_index]["action"]
    prior_actions = preflop_actions[:hero_index]
    prior_raises = [action for action in prior_actions if action["action"] == "raise"]
    vpip = hero_action in {"call", "raise"}
    pfr = hero_action == "raise"
    ats_opportunity = position in {"CO", "BTN", "SB"} and len(prior_raises) == 0
    ats_attempt = ats_opportunity and hero_action == "raise"
    three_bet_opportunity = len(prior_raises) == 1
    three_bet = three_bet_opportunity and hero_action == "raise"

    return {
        "vpip": vpip,
        "pfr": pfr,
        "ats_opportunity": ats_opportunity,
        "ats_attempt": ats_attempt,
        "three_bet_opportunity": three_bet_opportunity,
        "three_bet": three_bet,
    }


def _find_flop_cbet(preflop_actions: list[dict[str, str]], flop_actions: list[dict[str, str]]) -> tuple[bool, bool]:
    if not flop_actions:
        return (False, False)
    aggressors = [action["actor"] for action in preflop_actions if action["action"] == "raise"]
    if not aggressors or aggressors[-1] != "Hero":
        return (False, False)
    hero_flop_index = next((index for index, action in enumerate(flop_actions) if action["actor"] == "Hero"), None)
    if hero_flop_index is None:
        return (False, False)
    prior_aggression = any(action["action"] in {"bet", "raise"} for action in flop_actions[:hero_flop_index] if action["actor"] != "Hero")
    if prior_aggression:
        return (False, False)
    return (True, flop_actions[hero_flop_index]["action"] in {"bet", "raise"})


def _find_turn_cbet(flop_cbet: bool, turn_actions: list[dict[str, str]]) -> tuple[bool, bool]:
    if not flop_cbet or not turn_actions:
        return (False, False)
    hero_turn_index = next((index for index, action in enumerate(turn_actions) if action["actor"] == "Hero"), None)
    if hero_turn_index is None:
        return (False, False)
    prior_aggression = any(action["action"] in {"bet", "raise"} for action in turn_actions[:hero_turn_index] if action["actor"] != "Hero")
    if prior_aggression:
        return (False, False)
    return (True, turn_actions[hero_turn_index]["action"] in {"bet", "raise"})


def _find_river_aggression(river_actions: list[dict[str, str]]) -> tuple[bool, bool]:
    if not river_actions:
        return (False, False)
    hero_action = _hero_first_action(river_actions)
    if not hero_action:
        return (False, False)
    if hero_action["action"] == "fold":
        return (False, False)
    return (True, hero_action["action"] in {"bet", "raise"})


def _find_showdown(block: list[str], hero_not_folded_preflop: bool) -> tuple[bool, bool]:
    showdown = any(row.startswith("*** SHOWDOWN ***") for row in block)
    hero_showed = any(row.startswith("Hero: shows") for row in block)
    hero_collected = any(row.startswith("Hero collected ") for row in block)
    if not showdown or not hero_not_folded_preflop:
        return (False, False)
    return (hero_showed or hero_collected, hero_collected)


def _street_reached(block: list[str], street: str) -> bool:
    marker = {
        "flop": "*** FLOP ***",
        "turn": "*** TURN ***",
        "river": "*** RIVER ***",
    }[street]
    return any(row.startswith(marker) for row in block)


def _safe_pct(numerator: int, denominator: int) -> float | None:
    if denominator <= 0:
        return None
    return round((numerator / denominator) * 100, 1)


def _fetch_hud_observations(player_id: str, window: str) -> list[HudHandObservation]:
    cutoff = None
    if window == "90d":
        cutoff = datetime.now(UTC) - timedelta(days=90)

    observations: list[HudHandObservation] = []
    with get_sqlite_connection() as conn:
        rows = conn.execute(
            """
            SELECT hands.raw_payload, hands.result_summary, sessions.started_at, sessions.session_metadata
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
        tournament_id = _extract_tournament_id(header, session_metadata)
        format_tag = _extract_format_tag(header, session_metadata)
        position = _extract_hero_position(block)
        actions = _street_actions(block)
        preflop_stats = _find_preflop_stats(position, actions["preflop"])
        saw_flop = _street_reached(block, "flop") and _hero_not_folded_preflop(actions["preflop"])
        flop_cbet_opportunity, flop_cbet = _find_flop_cbet(actions["preflop"], actions["flop"])
        turn_cbet_opportunity, turn_cbet = _find_turn_cbet(flop_cbet, actions["turn"])
        river_opportunity, river_aggressive = _find_river_aggression(actions["river"])
        showdown, showdown_win = _find_showdown(block, _hero_not_folded_preflop(actions["preflop"]))

        observations.append(
            HudHandObservation(
                tournament_id=tournament_id,
                started_at=row["started_at"],
                format_tag=format_tag,
                position=position,
                saw_flop=saw_flop,
                vpip=preflop_stats["vpip"],
                pfr=preflop_stats["pfr"],
                ats_opportunity=preflop_stats["ats_opportunity"],
                ats_attempt=preflop_stats["ats_attempt"],
                three_bet_opportunity=preflop_stats["three_bet_opportunity"],
                three_bet=preflop_stats["three_bet"],
                flop_cbet_opportunity=flop_cbet_opportunity,
                flop_cbet=flop_cbet,
                turn_cbet_opportunity=turn_cbet_opportunity,
                turn_cbet=turn_cbet,
                river_opportunity=river_opportunity,
                river_aggressive=river_aggressive,
                showdown=showdown,
                showdown_win=showdown_win,
            )
        )
    return observations


def _aggregate_tournaments(observations: list[HudHandObservation]) -> list[dict[str, Any]]:
    grouped: dict[str, list[HudHandObservation]] = defaultdict(list)
    for item in observations:
        grouped[item.tournament_id].append(item)

    tournaments: list[dict[str, Any]] = []
    for tournament_id, rows in grouped.items():
        ordered_rows = sorted(rows, key=lambda item: item.started_at or "", reverse=True)
        hands = len(rows)
        vpip_count = sum(1 for item in rows if item.vpip)
        pfr_count = sum(1 for item in rows if item.pfr)
        ats_attempts = sum(1 for item in rows if item.ats_attempt)
        ats_opportunities = sum(1 for item in rows if item.ats_opportunity)
        three_bet_count = sum(1 for item in rows if item.three_bet)
        three_bet_opportunities = sum(1 for item in rows if item.three_bet_opportunity)
        flop_cbet_count = sum(1 for item in rows if item.flop_cbet)
        flop_cbet_opportunities = sum(1 for item in rows if item.flop_cbet_opportunity)
        turn_cbet_count = sum(1 for item in rows if item.turn_cbet)
        turn_cbet_opportunities = sum(1 for item in rows if item.turn_cbet_opportunity)
        river_aggressive_count = sum(1 for item in rows if item.river_aggressive)
        river_opportunities = sum(1 for item in rows if item.river_opportunity)
        flop_seen_count = sum(1 for item in rows if item.saw_flop)
        showdown_count = sum(1 for item in rows if item.showdown)
        showdown_win_count = sum(1 for item in rows if item.showdown_win)
        format_mix = defaultdict(int)
        for item in rows:
            format_mix[item.format_tag] += 1

        tournaments.append(
            {
                "tournament_id": tournament_id,
                "started_at": ordered_rows[0].started_at,
                "hands": hands,
                "format_mix": dict(sorted(format_mix.items())),
                "metrics": {
                    "vpip": _safe_pct(vpip_count, hands),
                    "pfr": _safe_pct(pfr_count, hands),
                    "ats": _safe_pct(ats_attempts, ats_opportunities),
                    "three_bet": _safe_pct(three_bet_count, three_bet_opportunities),
                    "flop_cbet": _safe_pct(flop_cbet_count, flop_cbet_opportunities),
                    "turn_cbet": _safe_pct(turn_cbet_count, turn_cbet_opportunities),
                    "river_aggression": _safe_pct(river_aggressive_count, river_opportunities),
                    "wtsd": _safe_pct(showdown_count, flop_seen_count),
                    "wsd": _safe_pct(showdown_win_count, showdown_count),
                },
                "counts": {
                    "ats_opportunities": ats_opportunities,
                    "three_bet_opportunities": three_bet_opportunities,
                    "flop_cbet_opportunities": flop_cbet_opportunities,
                    "turn_cbet_opportunities": turn_cbet_opportunities,
                    "river_opportunities": river_opportunities,
                    "flop_seen": flop_seen_count,
                    "showdowns": showdown_count,
                },
            }
        )
    return sorted(tournaments, key=lambda item: item["started_at"] or "", reverse=True)


def _window_average(tournaments: list[dict[str, Any]], metric: str, start: int, size: int) -> float | None:
    values = [
        item["metrics"].get(metric)
        for item in tournaments[start : start + size]
        if item["metrics"].get(metric) is not None
    ]
    if not values:
        return None
    return round(sum(values) / len(values), 1)


def _latest_observed_at(tournaments: list[dict[str, Any]]) -> datetime | None:
    parsed = [_parse_started_at(item.get("started_at")) for item in tournaments]
    valid = [item for item in parsed if item is not None]
    if not valid:
        return None
    return max(valid)


def _bucket_tournaments_by_day(tournaments: list[dict[str, Any]], days: int = 7) -> list[dict[str, Any]]:
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    latest = _latest_observed_at(tournaments)
    if latest is None:
        return []
    cutoff = latest - timedelta(days=days - 1)
    for item in tournaments:
        started_at = _parse_started_at(item.get("started_at"))
        if not started_at or started_at < cutoff:
            continue
        day_key = started_at.strftime("%Y-%m-%d")
        buckets[day_key].append(item)

    ordered_days = sorted(buckets.keys(), reverse=True)[:days]
    results: list[dict[str, Any]] = []
    for day_key in ordered_days:
        rows = buckets[day_key]
        hands = sum(int(row.get("hands") or 0) for row in rows)
        metrics = {}
        for metric in ("vpip", "pfr", "ats", "three_bet", "flop_cbet", "turn_cbet", "river_aggression", "wtsd", "wsd"):
            values = [row["metrics"].get(metric) for row in rows if row["metrics"].get(metric) is not None]
            metrics[metric] = round(sum(values) / len(values), 1) if values else None
        results.append(
            {
                "day": day_key,
                "tournaments": len(rows),
                "hands": hands,
                "metrics": metrics,
            }
        )
    return results


def _tournaments_by_format(tournaments: list[dict[str, Any]], days: int = 7) -> list[dict[str, Any]]:
    latest = _latest_observed_at(tournaments)
    if latest is None:
        return []
    cutoff = latest - timedelta(days=days - 1)
    by_format: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in tournaments:
        started_at = _parse_started_at(item.get("started_at"))
        if not started_at or started_at < cutoff:
            continue
        for format_tag, count in (item.get("format_mix") or {}).items():
            if count > 0:
                by_format[format_tag].append(item)

    results: list[dict[str, Any]] = []
    for format_tag, rows in sorted(by_format.items()):
        hands = sum(int(row.get("hands") or 0) for row in rows)
        metrics = {}
        for metric in ("vpip", "pfr", "ats", "three_bet", "flop_cbet", "turn_cbet", "river_aggression", "wtsd", "wsd"):
            values = [row["metrics"].get(metric) for row in rows if row["metrics"].get(metric) is not None]
            metrics[metric] = round(sum(values) / len(values), 1) if values else None
        results.append(
            {
                "format_tag": format_tag,
                "tournaments": len(rows),
                "hands": hands,
                "metrics": metrics,
                "headline": _format_split_headline(format_tag, metrics),
            }
        )
    return results


def _format_split_headline(format_tag: str, metrics: dict[str, float | None]) -> str:
    river = metrics.get("river_aggression")
    vpip = metrics.get("vpip")
    pfr = metrics.get("pfr")
    if format_tag == "satellite":
        if river is not None and river < 30:
            return "Satellite sample still shows conservative river follow-through."
        return "Satellite sample looks structurally tighter and more survival-aware."
    if format_tag == "pko":
        if vpip is not None and pfr is not None and vpip > pfr + 10:
            return "PKO sample is widening, but some of that width is not converting into initiative."
        return "PKO sample is carrying the most active entry profile."
    if format_tag == "standard_mtt":
        if river is not None and river < 35:
            return "Standard MTT sample still looks the most river-cautious."
        return "Standard MTT sample is comparatively balanced right now."
    return "Format split interpretation pending."


def _interpret_stat_shift(metric: str, delta: float | None) -> str:
    if delta is None:
        return "Not enough history to compare yet."
    abs_delta = abs(delta)
    direction = "up" if delta > 0 else "down"
    if metric == "vpip":
        if delta > 0:
            return f"VPIP is {direction}, which usually means you are entering more pots overall rather than waiting for stronger starting thresholds."
        return f"VPIP is {direction}, which usually means your overall entry threshold has tightened and fewer marginal hands are being approved."
    if metric == "pfr":
        if delta > 0:
            return f"PFR is {direction}, which means more of your entries are proactive raises rather than passive calls or folds."
        return f"PFR is {direction}, which means your preflop game is becoming less initiative-heavy and more selective or passive."
    if metric == "ats":
        if delta > 0:
            return f"ATS is {direction}, so late-position steal approval is becoming more active when folds reach you."
        return f"ATS is {direction}, so you may still be passing on some late-position pressure spots."
    if metric == "three_bet":
        if delta > 0:
            return f"3BET is {direction}, which means you are re-raising more often instead of flatting or folding after an open."
        return f"3BET is {direction}, which means your preflop resistance to opens is softening."
    if metric == "flop_cbet":
        if delta > 0:
            return f"Flop c-bet is {direction}, which means preflop initiative is converting into flop pressure more often."
        return f"Flop c-bet is {direction}, which means you are checking back more often after taking initiative preflop."
    if metric == "turn_cbet":
        if delta > 0:
            return f"Turn c-bet is {direction}, which means second barrels are appearing more often after the flop bet lands."
        return f"Turn c-bet is {direction}, which means your flop pressure is not carrying forward as often on the turn."
    if metric == "river_aggression":
        if delta > 0:
            return f"River aggression is {direction}, which is the clearest sign that your previous river passivity may actually be changing in live volume."
        return f"River aggression is {direction}, which suggests the old passive river baseline may still be pulling you back."
    if metric == "wtsd":
        if delta > 0:
            return f"WTSD is {direction}, which means more flop-seen hands are continuing all the way to showdown."
        return f"WTSD is {direction}, which means more hands are getting resolved before showdown."
    if metric == "wsd":
        if delta > 0:
            return f"W$SD is {direction}, which means your showdown quality is improving when you do arrive there."
        return f"W$SD is {direction}, which means recent showdown results are being won less often despite getting there."
    return f"{metric} is {direction} by {abs_delta:.1f} points."


def _build_change_notes(featured_metrics: list[dict[str, Any]]) -> list[dict[str, Any]]:
    notes = []
    for item in featured_metrics:
        notes.append(
            {
                "metric": item["metric"],
                "label": item["label"],
                "delta": item["delta"],
                "meaning": _interpret_stat_shift(item["metric"], item["delta"]),
            }
        )
    return notes


def _metric_interpretation(metric: str, current: float | None, recent_delta: float | None) -> str:
    if current is None:
        return "Not enough opportunity volume yet."
    delta_phrase = ""
    if recent_delta is not None:
        delta_phrase = f" Recent change: {recent_delta:+.1f} pts."
    if metric == "river_aggression":
        if current < 28:
            return f"River aggression still reads passive for a pressure-oriented tournament baseline.{delta_phrase}"
        if current < 40:
            return f"River aggression is present but still conservative; trend matters more than one tournament snapshot.{delta_phrase}"
        return f"River aggression is showing up with intent instead of default passivity.{delta_phrase}"
    if metric == "vpip":
        return f"VPIP shows how wide you are entering pots overall.{delta_phrase}"
    if metric == "pfr":
        return f"PFR shows how often your entry is proactive rather than passive.{delta_phrase}"
    if metric == "ats":
        return f"ATS tracks steal approval when folded to in late positions.{delta_phrase}"
    if metric == "three_bet":
        return f"3BET tracks re-raise aggression when openers appear before you.{delta_phrase}"
    if metric == "flop_cbet":
        return f"Flop CBet tracks whether preflop initiative converts into flop pressure.{delta_phrase}"
    if metric == "turn_cbet":
        return f"Turn CBet tracks second-barrel follow-through after flop initiative.{delta_phrase}"
    if metric == "wtsd":
        return f"WTSD shows how often flop-seen hands continue all the way to showdown.{delta_phrase}"
    if metric == "wsd":
        return f"W$SD shows how often showdown hands are actually getting won.{delta_phrase}"
    return delta_phrase.strip() or "Trend interpretation pending."


def get_hud_trend_payload(player_id: str = HERO_PLAYER_ID, window: str = "90d") -> dict[str, Any]:
    resolved_player_id = player_id or HERO_PLAYER_ID
    resolved_window = window if window in SUPPORTED_WINDOWS else "90d"
    observations = _fetch_hud_observations(resolved_player_id, resolved_window)
    tournaments = _aggregate_tournaments(observations)
    recent = tournaments[:20]

    legend = [
        {"metric": "vpip", "label": "VPIP", "definition": "Voluntarily put money in preflop."},
        {"metric": "pfr", "label": "PFR", "definition": "Preflop raise frequency."},
        {"metric": "ats", "label": "ATS", "definition": "Attempt to steal when folded to in CO / BTN / SB."},
        {"metric": "three_bet", "label": "3BET", "definition": "Re-raise frequency when facing one open."},
        {"metric": "flop_cbet", "label": "Flop CB", "definition": "Flop continuation bet after being the preflop aggressor."},
        {"metric": "turn_cbet", "label": "Turn CB", "definition": "Turn barrel after making the flop c-bet."},
        {"metric": "river_aggression", "label": "River Agg", "definition": "Aggressive river decision rate when Hero acts on the river."},
        {"metric": "wtsd", "label": "WTSD", "definition": "Went to showdown after seeing a flop."},
        {"metric": "wsd", "label": "W$SD", "definition": "Won at showdown."},
    ]

    featured_metrics = []
    for metric, label in [
        ("vpip", "VPIP"),
        ("pfr", "PFR"),
        ("ats", "ATS"),
        ("three_bet", "3BET"),
        ("flop_cbet", "Flop CB"),
        ("turn_cbet", "Turn CB"),
        ("river_aggression", "River Agg"),
        ("wtsd", "WTSD"),
        ("wsd", "W$SD"),
    ]:
        current = _window_average(tournaments, metric, 0, min(10, len(tournaments)))
        previous = _window_average(tournaments, metric, 10, min(10, max(len(tournaments) - 10, 0)))
        delta = round(current - previous, 1) if current is not None and previous is not None else None
        series = [item["metrics"].get(metric) for item in recent]
        featured_metrics.append(
            {
                "metric": metric,
                "label": label,
                "current": current,
                "previous": previous,
                "delta": delta,
                "series": series,
                "interpretation": _metric_interpretation(metric, current, delta),
            }
        )

    headline = "HUD trend is still forming."
    river_metric = next((item for item in featured_metrics if item["metric"] == "river_aggression"), None)
    if river_metric and river_metric["current"] is not None:
        if river_metric["current"] < 28:
            headline = "River remains your clearest passive holdout in the current tournament sample."
        elif river_metric["delta"] is not None and river_metric["delta"] > 3:
            headline = "River aggression is finally moving enough to be visible in tournament-level HUD trend."
        else:
            headline = "Tournament-level HUD trend is readable now, but river change still needs more separation from baseline noise."

    last_7_days = _bucket_tournaments_by_day(tournaments, days=7)
    format_splits = _tournaments_by_format(tournaments, days=7)
    change_notes = _build_change_notes(featured_metrics)

    return {
        "status": "ok",
        "player_id": resolved_player_id,
        "summary": {
            "window": resolved_window,
            "tournaments": len(tournaments),
            "hands": len(observations),
            "headline": headline,
        },
        "legend": legend,
        "featured_metrics": featured_metrics,
        "change_notes": change_notes,
        "last_7_days": last_7_days,
        "format_splits": format_splits,
        "recent_tournaments": recent[:12],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Read the HUD trend payload.")
    parser.add_argument("--player-id", default=HERO_PLAYER_ID, help="Player id to inspect.")
    parser.add_argument("--window", default="90d", choices=sorted(SUPPORTED_WINDOWS))
    args = parser.parse_args()
    payload = get_hud_trend_payload(player_id=args.player_id, window=args.window)
    print(json.dumps(payload, indent=2, default=str))


if __name__ == "__main__":
    main()
