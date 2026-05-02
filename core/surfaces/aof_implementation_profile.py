from __future__ import annotations

import re
from collections import Counter, defaultdict
from typing import Any

from core.storage.repositories import V2Repository

RANK_ORDER = "23456789TJQKA"
PREMIUM = {"AA", "KK", "QQ", "JJ", "TT", "AKs", "AKo", "AQs"}
STRONG = PREMIUM | {"99", "88", "AJs", "ATs", "AQo", "KQs", "KJs", "QJs"}
MEDIUM = STRONG | {
    "77",
    "66",
    "55",
    "A9s",
    "A8s",
    "A7s",
    "A5s",
    "A4s",
    "AJo",
    "ATo",
    "KQo",
    "KJo",
    "KTs",
    "QJs",
    "QTs",
    "JTs",
    "T9s",
    "98s",
}


def _rank(card: str) -> str:
    return card[0].upper().replace("1", "T")


def _hand_class(cards: str | None) -> str | None:
    if not cards:
        return None
    parts = re.findall(r"([2-9TJQKA][cdhs])", cards)
    if len(parts) != 2:
        return None
    r1, r2 = _rank(parts[0]), _rank(parts[1])
    if r1 == r2:
        return r1 + r2
    high, low = sorted([r1, r2], key=lambda r: RANK_ORDER.index(r), reverse=True)
    suited = parts[0][1] == parts[1][1]
    return f"{high}{low}{'s' if suited else 'o'}"


def _stack_band(bb: float | None) -> str:
    if bb is None:
        return "unknown"
    if bb <= 8:
        return "0-8bb"
    if bb <= 12:
        return "8-12bb"
    if bb <= 15:
        return "12-15bb"
    return "15bb+"


def _format_profile(label: str) -> str:
    lower = label.lower()
    if "satellite" in lower or "step to" in lower or "seat" in lower:
        return "satellite"
    if "bounty" in lower or "ko" in lower:
        return "pko"
    return "standard_mtt"


def _extract_preflop_context(hand: dict[str, Any]) -> dict[str, Any] | None:
    block = list((hand.get("raw_payload") or {}).get("block") or [])
    if not block:
        return None
    preflop: list[str] = []
    cards = None
    active_seats = 0
    for line in block:
        if line.startswith("Seat ") and " in chips" in line:
            active_seats += 1
        if line.startswith("*** FLOP ***"):
            break
        if line.startswith("Dealt to Hero"):
            cards = line
        preflop.append(line)
    return {"preflop": preflop, "cards": cards, "active_seats": active_seats}


def _is_posting(action: str) -> bool:
    lower = action.lower()
    return "posts" in lower or "ante" in lower


def _classify_action(hand: dict[str, Any], preflop: list[str]) -> tuple[str | None, str | None, bool]:
    hero_action = None
    voluntary_before_hero = False
    for line in preflop:
        action_match = re.match(r"^(?P<player>[^:]+):\s+(?P<action>.+)$", line.strip())
        if not action_match:
            continue
        player = action_match.group("player").strip()
        action = action_match.group("action").strip()
        lower = action.lower()
        if player != "Hero" and any(word in lower for word in ["raises", "calls", "bets", "all-in", "all in"]):
            voluntary_before_hero = True
        if player == "Hero" and not _is_posting(action):
            hero_action = action
            break
    if hero_action is None:
        return None, None, voluntary_before_hero
    lower = hero_action.lower()
    if "folds" in lower:
        return "fold", hero_action, voluntary_before_hero
    if "all-in" in lower or "all in" in lower:
        return "open_jam", hero_action, voluntary_before_hero
    if "raises" in lower:
        bb = float((hand.get("header_metadata") or {}).get("big_blind") or 0)
        stack_bb = float(hand.get("effective_stack_bb") or 0)
        amounts = [int(x.replace(",", "")) for x in re.findall(r"\b\d[\d,]*\b", hero_action)]
        final_raise = max(amounts) if amounts else 0
        if bb and stack_bb and final_raise / bb >= stack_bb * 0.8:
            return "open_almost_all_in", hero_action, voluntary_before_hero
        return "open_raise_small", hero_action, voluntary_before_hero
    if "calls" in lower or "checks" in lower:
        return "call_or_check", hero_action, voluntary_before_hero
    return "other", hero_action, voluntary_before_hero


def _position_group(position: str | None) -> str:
    value = (position or "unknown").lower()
    if "button" in value:
        return "BTN"
    if "small blind" in value:
        return "SB"
    if "big blind" in value:
        return "BB"
    return value.upper() if value != "unknown" else "unknown"


def _baseline_action(hand_class: str, stack_band: str, position: str, fmt: str) -> str:
    if fmt == "satellite":
        if hand_class in PREMIUM:
            return "jam"
        if stack_band == "0-8bb" and hand_class in STRONG:
            return "mixed"
        return "fold"
    if stack_band == "0-8bb":
        return "jam" if hand_class in MEDIUM or hand_class.startswith("A") or hand_class.endswith("s") else "fold"
    if stack_band == "8-12bb":
        if hand_class in STRONG or hand_class.startswith("A"):
            return "jam"
        if position in {"BTN", "SB", "CO"} and hand_class in MEDIUM:
            return "mixed"
        return "fold"
    if stack_band == "12-15bb":
        if hand_class in PREMIUM:
            return "jam"
        if hand_class in STRONG:
            return "mixed"
        return "fold"
    return "excluded"


def _verdict(actual: str, baseline: str, fmt: str) -> str:
    if baseline == "excluded":
        return "excluded"
    if fmt in {"pko", "satellite"} and baseline != "jam" and actual in {"open_jam", "open_almost_all_in"}:
        return "special_context_defer"
    if baseline == "mixed":
        return "mixed"
    if baseline == "jam" and actual in {"open_jam", "open_almost_all_in"}:
        return "match"
    if baseline == "fold" and actual == "fold":
        return "match"
    if baseline == "jam" and actual == "fold":
        return "too_tight"
    if baseline == "fold" and actual in {"open_jam", "open_almost_all_in", "open_raise_small"}:
        return "too_loose"
    if baseline == "jam" and actual == "open_raise_small":
        return "awkward_raise"
    return "mixed"


def _result_bucket(hand: dict[str, Any]) -> str:
    text = " ".join(str(x) for x in (hand.get("result_summary") or {}).values()).lower()
    if "won" in text or "collected" in text:
        return "won"
    if "lost" in text:
        return "lost"
    if "fold" in text:
        return "folded"
    return "unknown"


def _pct(count: int, total: int) -> float:
    return round((count / total) * 100, 1) if total else 0.0


def build_aof_implementation_profile(repository: V2Repository, player_id: str) -> dict[str, Any]:
    hands = repository.fetch_hands_for_player(player_id, limit=50000)
    spots: list[dict[str, Any]] = []
    excluded = Counter()
    for hand in hands:
        bb = hand.get("effective_stack_bb")
        if bb is None or float(bb) > 15:
            continue
        ctx = _extract_preflop_context(hand)
        if not ctx:
            excluded["missing_raw"] += 1
            continue
        if ctx["active_seats"] < 5:
            excluded["short_handed"] += 1
            continue
        hand_class = _hand_class(ctx["cards"])
        if not hand_class:
            excluded["missing_cards"] += 1
            continue
        actual, hero_action, voluntary_before_hero = _classify_action(hand, ctx["preflop"])
        if voluntary_before_hero:
            excluded["facing_action"] += 1
            continue
        if not actual:
            excluded["missing_decision"] += 1
            continue
        stack_band = _stack_band(float(bb))
        fmt = _format_profile(str(hand.get("buyin_band") or ""))
        position = _position_group(hand.get("hero_position"))
        baseline = _baseline_action(hand_class, stack_band, position, fmt)
        verdict = _verdict(actual, baseline, fmt)
        spots.append(
            {
                "spot_id": hand.get("id"),
                "hand_external_id": hand.get("hand_external_id"),
                "tournament_id": hand.get("tournament_id"),
                "tournament": hand.get("buyin_band"),
                "format_profile": fmt,
                "stack_bb": round(float(bb), 2),
                "stack_band": stack_band,
                "position": position,
                "hand_class": hand_class,
                "actual_action": actual,
                "hero_action": hero_action,
                "baseline_action": baseline,
                "verdict": verdict,
                "result": _result_bucket(hand),
            }
        )
    total = len(spots)
    verdicts = Counter(s["verdict"] for s in spots)
    actions = Counter(s["actual_action"] for s in spots)
    avg_stack = round(sum(s["stack_bb"] for s in spots) / total, 2) if total else None
    median_stack = sorted(s["stack_bb"] for s in spots)[total // 2] if total else None
    jam_spots = [s for s in spots if s["actual_action"] in {"open_jam", "open_almost_all_in"}]
    jam_avg = round(sum(s["stack_bb"] for s in jam_spots) / len(jam_spots), 2) if jam_spots else None
    jam_median = sorted(s["stack_bb"] for s in jam_spots)[len(jam_spots) // 2] if jam_spots else None

    repeated: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for s in spots:
        if s["verdict"] in {"too_loose", "too_tight", "awkward_raise", "special_context_defer"}:
            repeated[(s["hand_class"], s["position"], s["verdict"])].append(s)
    pattern_cards = []
    for (hand_class, position, verdict), rows in sorted(repeated.items(), key=lambda item: len(item[1]), reverse=True)[:12]:
        pattern_cards.append(
            {
                "hand_class": hand_class,
                "position": position,
                "verdict": verdict,
                "count": len(rows),
                "formats": dict(Counter(r["format_profile"] for r in rows)),
                "stack_bands": dict(Counter(r["stack_band"] for r in rows)),
                "results": dict(Counter(r["result"] for r in rows)),
                "examples": rows[:5],
            }
        )

    stack_breakdown = {}
    for band in ["0-8bb", "8-12bb", "12-15bb"]:
        rows = [s for s in spots if s["stack_band"] == band]
        stack_breakdown[band] = {
            "count": len(rows),
            "jam_rate": _pct(sum(1 for r in rows if r["actual_action"] in {"open_jam", "open_almost_all_in"}), len(rows)),
            "match_rate": _pct(sum(1 for r in rows if r["verdict"] == "match"), len(rows)),
            "too_loose_rate": _pct(sum(1 for r in rows if r["verdict"] == "too_loose"), len(rows)),
        }

    suspicious_15bb = [
        s
        for s in spots
        if s["stack_band"] == "12-15bb"
        and s["actual_action"] in {"open_jam", "open_almost_all_in"}
        and s["baseline_action"] == "fold"
    ][:20]

    return {
        "summary": {
            "aof_opportunity_count": total,
            "excluded_counts": dict(excluded),
            "average_stack_bb": avg_stack,
            "median_stack_bb": median_stack,
            "jam_average_stack_bb": jam_avg,
            "jam_median_stack_bb": jam_median,
            "hero_12bb_hypothesis": "supported" if jam_median is not None and 10 <= jam_median <= 13 else "not_yet_supported",
            "match_rate": _pct(verdicts["match"], total),
            "too_tight_rate": _pct(verdicts["too_tight"], total),
            "too_loose_rate": _pct(verdicts["too_loose"], total),
            "awkward_raise_rate": _pct(verdicts["awkward_raise"], total),
            "special_context_defer_rate": _pct(verdicts["special_context_defer"], total),
            "mixed_rate": _pct(verdicts["mixed"], total),
        },
        "action_shape": dict(actions),
        "stack_breakdown": stack_breakdown,
        "format_breakdown": {
            fmt: {
                "count": len(rows),
                "jam_rate": _pct(sum(1 for r in rows if r["actual_action"] in {"open_jam", "open_almost_all_in"}), len(rows)),
                "too_loose_rate": _pct(sum(1 for r in rows if r["verdict"] == "too_loose"), len(rows)),
                "special_context_defer_rate": _pct(sum(1 for r in rows if r["verdict"] == "special_context_defer"), len(rows)),
            }
            for fmt, rows in ((fmt, [s for s in spots if s["format_profile"] == fmt]) for fmt in ["standard_mtt", "pko", "satellite"])
        },
        "pattern_cards": pattern_cards,
        "suspicious_12_15bb_jams": suspicious_15bb,
        "truth_policy": "AOF v1 is deterministic baseline comparison, not solver-grade EV truth.",
    }
