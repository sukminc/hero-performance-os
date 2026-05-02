from __future__ import annotations

import re
from collections import Counter, defaultdict
from typing import Any

from core.storage.repositories import V2Repository
from core.surfaces.aof_implementation_profile import (
    MEDIUM,
    PREMIUM,
    STRONG,
    _format_profile,
    _hand_class,
    _pct,
    _position_group,
    _result_bucket,
    _stack_band,
)

MONSTER = {"AA", "KK"}
PREMIUM_INDUCE = {"AA", "KK", "QQ", "AKs", "AKo"}
MARGINAL_PRESSURE = {"KJo", "KTo", "QJo", "QTo", "JTo", "J9s", "J8s", "T9o", "T8s", "98s", "89s", "87s", "76s"}

FAMILY_SEVERITY = {
    "multiway_overcommit": 5,
    "bad_calloff_candidate": 5,
    "satellite_survival_violation": 5,
    "premium_missed_induce": 4,
    "too_wide_open_jam_12_15bb": 4,
    "too_wide_reshove": 4,
    "too_tight_premium_fold": 4,
    "too_tight_monster_fold": 5,
}


def _preflop_lines(hand: dict[str, Any]) -> tuple[list[str], int, str | None]:
    block = list((hand.get("raw_payload") or {}).get("block") or [])
    lines: list[str] = []
    active_seats = 0
    cards = None
    for line in block:
        if line.startswith("Seat ") and " in chips" in line:
            active_seats += 1
        if line.startswith("*** FLOP ***"):
            break
        if line.startswith("Dealt to Hero"):
            cards = line
        lines.append(line)
    return lines, active_seats, cards


def _action_parts(line: str) -> tuple[str, str] | None:
    match = re.match(r"^(?P<player>[^:]+):\s+(?P<action>.+)$", line.strip())
    if not match:
        return None
    return match.group("player").strip(), match.group("action").strip()


def _is_voluntary(action: str) -> bool:
    lower = action.lower()
    return any(word in lower for word in ["raises", "calls", "bets", "all-in", "all in"]) and "posts" not in lower


def _hero_and_prior_actions(lines: list[str]) -> tuple[list[str], list[str], list[str]]:
    prior: list[str] = []
    hero: list[str] = []
    after_hero: list[str] = []
    hero_seen = False
    for line in lines:
        parts = _action_parts(line)
        if not parts:
            continue
        player, action = parts
        if player == "Hero" and "posts" not in action.lower():
            hero_seen = True
            hero.append(action)
        elif player != "Hero" and _is_voluntary(action):
            if hero_seen:
                after_hero.append(line)
            else:
                prior.append(line)
    return prior, hero, after_hero


def _action_family(action: str | None) -> str:
    if not action:
        return "missing"
    lower = action.lower()
    if "folds" in lower:
        return "fold"
    if "calls" in lower:
        return "call"
    if "all-in" in lower or "all in" in lower:
        return "jam"
    if "raises" in lower:
        return "raise"
    if "checks" in lower:
        return "check"
    return "other"


def _prior_shape(prior: list[str]) -> str:
    if not prior:
        return "unopened"
    all_in_count = sum(1 for line in prior if "all-in" in line.lower() or "all in" in line.lower())
    raise_count = sum(1 for line in prior if ": raises" in line.lower())
    call_count = sum(1 for line in prior if ": calls" in line.lower())
    if all_in_count >= 2 or (all_in_count and call_count):
        return "multiway_all_in"
    if all_in_count:
        return "facing_jam"
    if raise_count and call_count:
        return "facing_open_multiway"
    if raise_count:
        return "facing_open"
    return "limped_or_other"


def _situation(hand_class: str, stack_band: str, prior_shape: str, actual: str) -> str:
    if prior_shape == "unopened" and hand_class in PREMIUM_INDUCE and stack_band == "12-15bb":
        return "premium_induce_candidate"
    if prior_shape == "unopened":
        return "unopened_open_decision"
    if prior_shape == "facing_open" and actual in {"jam", "raise"}:
        return "facing_open_reshove"
    if prior_shape == "facing_open":
        return "facing_open_decision"
    if prior_shape == "facing_jam":
        return "facing_jam_calloff"
    if prior_shape == "multiway_all_in":
        return "multiway_all_in_decision"
    if prior_shape == "facing_open_multiway":
        return "multiway_after_open"
    return "other_short_stack_decision"


def _decision_quality(
    *,
    hand_class: str,
    stack_band: str,
    fmt: str,
    prior_shape: str,
    actual: str,
    situation: str,
) -> tuple[str, str, str]:
    if situation == "premium_induce_candidate":
        if actual == "jam" and hand_class in MONSTER:
            return "mistake_candidate", "premium_missed_induce", "15bb AA/KK can often prefer small open/induce over killing action with an open jam."
        if actual == "raise":
            return "standard", "premium_induce_line", "Premium used a smaller open size in an induce-capable stack band."
    if situation == "unopened_open_decision":
        if stack_band == "12-15bb" and actual == "jam" and hand_class in MARGINAL_PRESSURE and fmt == "standard_mtt":
            return "mistake_candidate", "too_wide_open_jam_12_15bb", "Marginal pressure hand open-jammed in the 12-15bb band."
        if stack_band == "12-15bb" and actual == "jam" and hand_class in MARGINAL_PRESSURE and fmt in {"pko", "satellite"}:
            return "operator_defer", "format_exception_candidate", "Format context may change the baseline; review before grading."
        if actual == "fold" and hand_class in PREMIUM:
            return "mistake_candidate", "too_tight_premium_fold", "Premium hand folded in an unopened short-stack spot."
        return "standard", "standard_or_low_signal_unopened", "No high-confidence AOF mistake family triggered."
    if situation == "facing_open_reshove":
        if hand_class in STRONG or (stack_band in {"0-8bb", "8-12bb"} and hand_class in MEDIUM):
            return "standard", "standard_reshove_pressure", "Reshove candidate uses a strong enough hand family for this v1 baseline."
        if hand_class in MARGINAL_PRESSURE and fmt == "standard_mtt":
            return "mistake_candidate", "too_wide_reshove", "Marginal hand reshoved over an open in a standard MTT context."
        return "operator_defer", "reshove_context_review", "Reshove needs position, opener, and stack-geometry review."
    if situation in {"facing_jam_calloff", "multiway_all_in_decision"}:
        if actual == "call" and hand_class not in STRONG:
            if fmt == "satellite":
                return "mistake_candidate", "satellite_survival_violation", "Non-premium calloff in satellite-like context should be treated skeptically."
            return "mistake_candidate", "bad_calloff_candidate", "Calloff with a non-strong hand family needs review."
        if actual == "fold" and hand_class in MONSTER:
            return "mistake_candidate", "too_tight_monster_fold", "Monster hand folded facing all-in pressure."
        if actual == "call" and hand_class in PREMIUM:
            return "non_mistake", "standard_calloff_or_cooler", "Premium calloff outcome should not be corrected just because it lost."
        return "non_mistake", "standard_fold_or_cooler_zone", "No clean decision leak triggered; outcome may be variance/cooler."
    if situation == "multiway_after_open":
        if actual == "call" and hand_class not in PREMIUM:
            return "mistake_candidate", "multiway_overcommit", "Calling into multiway preflop pressure with non-premium hand class is a review target."
        return "operator_defer", "multiway_context_review", "Multiway short-stack context needs operator review."
    return "operator_defer", "unclassified_short_stack_context", "Short-stack spot detected but not enough v2 context to grade."


def build_aof_decision_system(repository: V2Repository, player_id: str) -> dict[str, Any]:
    hands = repository.fetch_hands_for_player(player_id, limit=50000)
    spots: list[dict[str, Any]] = []
    excluded = Counter()
    for hand in hands:
        bb = hand.get("effective_stack_bb")
        if bb is None or float(bb) > 15:
            continue
        lines, active_seats, cards = _preflop_lines(hand)
        if active_seats < 5:
            excluded["short_handed"] += 1
            continue
        hand_class = _hand_class(cards)
        if not hand_class:
            excluded["missing_cards"] += 1
            continue
        prior, hero_actions, after_hero = _hero_and_prior_actions(lines)
        if not hero_actions:
            excluded["missing_hero_decision"] += 1
            continue
        actual = _action_family(hero_actions[0])
        stack_band = _stack_band(float(bb))
        fmt = _format_profile(str(hand.get("buyin_band") or ""))
        prior_shape = _prior_shape(prior)
        situation = _situation(hand_class, stack_band, prior_shape, actual)
        quality, family, explanation = _decision_quality(
            hand_class=hand_class,
            stack_band=stack_band,
            fmt=fmt,
            prior_shape=prior_shape,
            actual=actual,
            situation=situation,
        )
        spots.append(
            {
                "spot_id": hand.get("id"),
                "hand_external_id": hand.get("hand_external_id"),
                "tournament_id": hand.get("tournament_id"),
                "tournament": hand.get("buyin_band"),
                "format_profile": fmt,
                "stack_bb": round(float(bb), 2),
                "stack_band": stack_band,
                "position": _position_group(hand.get("hero_position")),
                "hand_class": hand_class,
                "situation": situation,
                "prior_shape": prior_shape,
                "hero_action": hero_actions[0],
                "actual_action": actual,
                "decision_quality": quality,
                "mistake_family": family,
                "explanation": explanation,
                "result": _result_bucket(hand),
                "prior_actions": prior[:4],
                "after_hero_actions": after_hero[:4],
            }
        )

    total = len(spots)
    quality_counts = Counter(s["decision_quality"] for s in spots)
    situation_counts = Counter(s["situation"] for s in spots)
    mistake_rows = [s for s in spots if s["decision_quality"] == "mistake_candidate"]
    non_mistake_rows = [s for s in spots if s["decision_quality"] == "non_mistake"]

    families: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for s in mistake_rows:
        families[(s["mistake_family"], s["hand_class"])].append(s)
    mistake_cards = []
    for (family, hand_class), rows in sorted(families.items(), key=lambda item: len(item[1]), reverse=True)[:14]:
        mistake_cards.append(
            {
                "mistake_family": family,
                "hand_class": hand_class,
                "count": len(rows),
                "situations": dict(Counter(r["situation"] for r in rows)),
                "formats": dict(Counter(r["format_profile"] for r in rows)),
                "stack_bands": dict(Counter(r["stack_band"] for r in rows)),
                "results": dict(Counter(r["result"] for r in rows)),
                "examples": rows[:5],
                "next_adjustment": _adjustment_for_family(family, hand_class),
                "product_read": _product_read_for_family(family, hand_class, rows),
                "priority_score": _priority_score(family, len(rows)),
            }
        )
    priority_cards = sorted(mistake_cards, key=lambda card: card["priority_score"], reverse=True)[:6]

    cooler_like = [
        s
        for s in spots
        if s["decision_quality"] in {"non_mistake", "standard"} and s["result"] == "lost" and s["hand_class"] in PREMIUM
    ][:20]

    return {
        "summary": {
            "short_stack_decision_count": total,
            "excluded_counts": dict(excluded),
            "mistake_candidate_count": len(mistake_rows),
            "mistake_candidate_rate": _pct(len(mistake_rows), total),
            "non_mistake_count": len(non_mistake_rows),
            "operator_defer_count": quality_counts["operator_defer"],
            "standard_count": quality_counts["standard"],
            "cooler_protection_count": len(cooler_like),
            "truth_policy": "AOF v2 separates decision leaks from cooler/runout outcomes; it is not solver-grade EV truth.",
        },
        "situation_counts": dict(situation_counts),
        "decision_quality_counts": dict(quality_counts),
        "product_summary": _product_summary(
            total=total,
            mistake_rows=mistake_rows,
            non_mistake_rows=non_mistake_rows,
            operator_defer_count=quality_counts["operator_defer"],
            priority_cards=priority_cards,
            cooler_like=cooler_like,
        ),
        "priority_leak_cards": priority_cards,
        "mistake_cards": mistake_cards,
        "cooler_or_non_mistake_examples": cooler_like,
        "premium_induce_examples": [s for s in spots if s["situation"] == "premium_induce_candidate"][:20],
    }


def _adjustment_for_family(family: str, hand_class: str) -> str:
    if family == "too_wide_open_jam_12_15bb":
        return f"Stop treating {hand_class} as an automatic 12-15bb pressure jam before position and format justify it."
    if family == "premium_missed_induce":
        return f"With {hand_class} around 12-15bb, consider small-open/induce lines before open-jamming."
    if family == "bad_calloff_candidate":
        return f"Review {hand_class} calloffs; lost outcomes are not the issue, weak calloff selection is."
    if family == "satellite_survival_violation":
        return f"Satellite calloffs with {hand_class} need survival-pressure review before approval."
    if family == "too_wide_reshove":
        return f"Do not convert {hand_class} into a reshove hand without opener/position evidence."
    if family == "multiway_overcommit":
        return f"Reduce non-premium multiway preflop commitments with {hand_class}."
    return f"Review repeated {family} spots for {hand_class}."


def _priority_score(family: str, count: int) -> int:
    return count * FAMILY_SEVERITY.get(family, 3)


def _severity_label(family: str, count: int) -> str:
    score = _priority_score(family, count)
    if score >= 15:
        return "High priority"
    if score >= 8:
        return "Review queue"
    return "Watchlist"


def _product_read_for_family(family: str, hand_class: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    count = len(rows)
    formats = Counter(r["format_profile"] for r in rows)
    stack_bands = Counter(r["stack_band"] for r in rows)
    results = Counter(r["result"] for r in rows)
    common_stack = stack_bands.most_common(1)[0][0] if stack_bands else "unknown"
    common_format = formats.most_common(1)[0][0] if formats else "unknown"
    lost_count = results.get("lost", 0)

    family_copy = {
        "multiway_overcommit": {
            "title": f"{hand_class} is showing up in multiway pressure spots",
            "why_it_matters": "Multiway short-stack mistakes are expensive because fold equity is lower and dominated hands realize poorly.",
            "what_to_change": f"Make {hand_class} a default no in multiway short-stack pressure unless position, bounty, and pot odds clearly justify continuing.",
            "what_not_to_overreact_to": "Do not call every lost multiway all-in a leak; only the non-premium hand selection is being flagged here.",
        },
        "bad_calloff_candidate": {
            "title": f"{hand_class} calloffs need a tighter approval gate",
            "why_it_matters": "Calloff errors are harder to recover from than open-jam errors because Hero has less fold equity and often realizes full tournament risk.",
            "what_to_change": f"Before approving {hand_class} calloffs, require stack band, opener/jammer range, position, and bounty economics to all line up.",
            "what_not_to_overreact_to": "Premium calloffs that lost are protected elsewhere; this card is about marginal hand selection, not bad runouts.",
        },
        "satellite_survival_violation": {
            "title": f"{hand_class} is risky in satellite survival spots",
            "why_it_matters": "Satellite-like formats punish unnecessary all-in risk more than normal chip-EV spots.",
            "what_to_change": f"Treat {hand_class} as a survival-review hand before calling off or forcing all-in pressure.",
            "what_not_to_overreact_to": "This is proxy-based format detection, so operator review should confirm the actual payout/satellite pressure.",
        },
        "too_wide_open_jam_12_15bb": {
            "title": f"{hand_class} may be too loose as a 12-15bb open jam",
            "why_it_matters": "At 12-15bb, the product should protect Hero from turning every playable hand into a shove by habit.",
            "what_to_change": f"Move {hand_class} from automatic AOF into position-and-format review at 12-15bb.",
            "what_not_to_overreact_to": "This does not mean never jam it; it means do not treat it as baseline without context.",
        },
        "too_wide_reshove": {
            "title": f"{hand_class} reshoves need opener/position proof",
            "why_it_matters": "Reshoving over an open is not the same decision as unopened AOF; opener strength and position matter more.",
            "what_to_change": f"Require opener profile, position, and stack geometry before approving {hand_class} as a reshove.",
            "what_not_to_overreact_to": "A reshove can still be good in the right pool/position; this card only blocks autopilot reshoves.",
        },
        "premium_missed_induce": {
            "title": f"{hand_class} may be killing action instead of inducing",
            "why_it_matters": "With monsters at 12-15bb, open-jamming can make worse hands fold when a small open could induce a reshove.",
            "what_to_change": f"Review whether {hand_class} should prefer small-open/call over open-jam in this stack band.",
            "what_not_to_overreact_to": "This is not a command to slowplay every premium; table aggression and stack geometry still decide.",
        },
    }
    copy = family_copy.get(
        family,
        {
            "title": f"{hand_class} repeated {family}",
            "why_it_matters": "Repeated short-stack deviations deserve review before they become baseline habits.",
            "what_to_change": _adjustment_for_family(family, hand_class),
            "what_not_to_overreact_to": "One-off outcomes are not enough; this card is only here because the pattern repeated.",
        },
    )
    return {
        **copy,
        "severity": _severity_label(family, count),
        "evidence_line": f"{count} repeats · common stack {common_stack} · common format {common_format} · {lost_count} lost outcomes",
        "review_status": "operator_review_needed",
    }


def _product_summary(
    *,
    total: int,
    mistake_rows: list[dict[str, Any]],
    non_mistake_rows: list[dict[str, Any]],
    operator_defer_count: int,
    priority_cards: list[dict[str, Any]],
    cooler_like: list[dict[str, Any]],
) -> dict[str, Any]:
    top = priority_cards[0] if priority_cards else None
    if top:
        top_read = top["product_read"]
        headline = top_read["title"]
        primary_fix = top_read["what_to_change"]
    else:
        headline = "No repeated high-priority AOF leak is currently leading the queue"
        primary_fix = "Keep collecting short-stack decisions and preserve the cooler guardrail."

    return {
        "headline": headline,
        "read": (
            f"Out of {total} short-stack decisions, {len(mistake_rows)} are leak candidates. "
            "The product should lead with the repeated hand-selection/situation mistakes, not raw all-in results."
        ),
        "primary_fix": primary_fix,
        "cooler_guardrail": (
            f"{len(non_mistake_rows)} non-mistake decisions and {len(cooler_like)} premium lost-outcome examples are protected "
            "from fake correction. Bad beats stay variance unless the decision node is off."
        ),
        "operator_note": (
            f"{operator_defer_count} spots still require operator/context review because AOF quality depends on position, opener, "
            "multiway geometry, bounty economics, and tournament format."
        ),
        "confidence": "directional_v2_not_solver_ev",
    }
