#!/usr/bin/env python3
"""Tests for position-first Matrix hand detail breakdown."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.api.hand_matrix import HandObservation, _extract_preflop_pattern, get_hand_matrix_payload

PLAYER_ID = "matrix-position-situation-player"


def obs(
    hand_id: str,
    position: str,
    bb_net: float,
    entry_type: str,
    prior_call_count: int,
    facing_state: str,
    open_size_bb: float | None = None,
    hand_class: str = "QJs",
    stack_bb: float = 20.0,
    started_at: str = "2026/05/05 10:00:00",
    hero_3bet_size_bb: float | None = None,
) -> HandObservation:
    resolved_3bet_size = hero_3bet_size_bb if hero_3bet_size_bb is not None else (6.0 if entry_type == "three_bet" else None)
    return HandObservation(
        hand_id=hand_id,
        session_id="session-position-situation",
        tournament_id="tournament-position-situation",
        started_at=started_at,
        format_tag="standard_mtt",
        hand_class=hand_class,
        position=position,
        active_seats=6,
        stack_bb=stack_bb,
        bb_net=bb_net,
        hero_summary=f"Hero {entry_type} from {position}.",
        first_preflop_action="raise" if "raise" in entry_type or "bet" in entry_type else "call",
        faced_action_preflop=facing_state != "unopened",
        preflop_entry_type=entry_type,
        prior_raise_count=1 if facing_state == "vs_open" else 0,
        prior_call_count=prior_call_count,
        facing_state=facing_state,
        faced_all_in_preflop=False,
        open_size_bb=open_size_bb,
        hero_preflop_size_bb=resolved_3bet_size if entry_type == "three_bet" else 2.0,
        hero_3bet_size_bb=resolved_3bet_size,
        hero_3bet_to_open_ratio=round(resolved_3bet_size / open_size_bb, 2) if resolved_3bet_size and open_size_bb else None,
        faced_4bet_after_3bet=False,
        folded_to_4bet_after_3bet=False,
    )


def main() -> None:
    two_limper_block = [
        "*** HOLE CARDS ***",
        "a1111111: calls 200",
        "b2222222: calls 200",
        "Hero: raises 800 to 1,000",
    ]
    parsed = _extract_preflop_pattern(two_limper_block)
    if parsed[4] != 2:
        raise AssertionError("Iso raise should preserve two prior limpers")
    if parsed[5] != "vs_multi_limp":
        raise AssertionError("Iso raise with two limpers should use vs_multi_limp facing state")

    call_vs_open_block = [
        "*** HOLE CARDS ***",
        "a1111111: raises 200 to 400",
        "Hero: calls 400",
    ]
    parsed_call = _extract_preflop_pattern(call_vs_open_block)
    if parsed_call[2] != "call_vs_open" or parsed_call[5] != "vs_open":
        raise AssertionError("Call versus one raise should be exposed as call_vs_open / vs_open")

    matrix = get_hand_matrix_payload(
        player_id=PLAYER_ID,
        window="all",
        selected_hand="QJs",
        observations=[
            obs("utg-open-1", "UTG", 4.0, "open_raise", 0, "unopened"),
            obs("utg-open-2", "UTG", 2.0, "open_raise", 0, "unopened"),
            obs("bb-call-1", "BB", -3.0, "call_vs_open", 0, "vs_open", open_size_bb=2.0),
            obs("bb-call-2", "BB", -5.0, "call_vs_open", 0, "vs_open", open_size_bb=2.5),
            obs("bb-call-3", "BB", -2.5, "call_vs_open", 0, "vs_open", open_size_bb=3.5),
            obs("bb-call-4", "BB", -1.5, "call_vs_open", 0, "vs_open", open_size_bb=3.5),
            obs("bb-call-5", "BB", -4.0, "call_vs_open", 0, "vs_open", open_size_bb=4.0),
            obs("btn-iso-1", "BTN", 6.0, "iso_raise", 2, "vs_multi_limp"),
            obs("co-3bet-1", "CO", 3.0, "three_bet", 0, "vs_open", open_size_bb=2.0),
            obs(
                "kk-near-all-in-3bet",
                "BB",
                -20.0,
                "three_bet",
                0,
                "vs_open",
                open_size_bb=2.0,
                hand_class="KK",
                stack_bb=40.0,
                hero_3bet_size_bb=32.0,
            ),
        ],
    )
    rows = matrix["detail"]["position_situation_breakdown"]
    labels = {(row["position"], row["situation_label"]): row for row in rows}
    if ("UTG", "Open") not in labels:
        raise AssertionError("QJs unopened opens should group under UTG / Open")
    if ("BB", "Call vs open") not in labels:
        raise AssertionError("QJs calls versus opens should group under BB / Call vs open")
    if ("BTN", "Iso vs limper(s)") not in labels:
        raise AssertionError("QJs iso raises should group under BTN / Iso vs limper(s)")
    if labels[("BB", "Call vs open")]["avg_open_size_bb"] != 3.1:
        raise AssertionError("Call vs open rows should expose average open size")
    if labels[("UTG", "Open")]["avg_hero_action_size_bb"] != 2.0:
        raise AssertionError("Open rows should expose Hero average action size")
    if labels[("BTN", "Iso vs limper(s)")]["prior_limper_count_max"] != 2:
        raise AssertionError("Iso rows should expose limper count")
    if labels[("BTN", "Iso vs limper(s)")]["sample_band"] != "tiny":
        raise AssertionError("Tiny samples should remain visible as tiny, not overinterpreted")
    read = matrix["detail"]["english_read"]
    if read["stance"] != "review_losing_subset":
        raise AssertionError("QJs read should preserve baseline while targeting the losing subset")
    actions = " ".join(read["next_actions"])
    if "Keep normal single-raised-pot BB defend baseline" not in actions:
        raise AssertionError("QJs BB loss should not become an automatic fold/range-cut instruction")
    if "3x+ opens" not in actions:
        raise AssertionError("QJs read should point large-open BB calls into review")
    sizing = matrix["preflop_sizing_summary"]
    if sizing["avg_standard_open_size_bb"] != 2.0:
        raise AssertionError("Preflop summary should expose Hero first-action open average")
    if sizing["avg_3bet_vs_2x_single_bb"] != 6.0:
        raise AssertionError("Preflop summary should expose clean Hero 3bet sizing versus single 2x opens")
    if sizing["near_all_in_3bet_count"] != 1 or sizing["all_3bet_count"] != 2:
        raise AssertionError("Preflop summary should separate near-all-in 3bets from sizing discipline")

    low_participation_rows = [
        HandObservation(
            hand_id=f"trash-fold-{index}",
            session_id="session-position-situation",
            tournament_id="tournament-position-situation",
            started_at="2026/05/05 10:00:00",
            format_tag="standard_mtt",
            hand_class="83o",
            position="BTN",
            active_seats=6,
            stack_bb=20.0,
            bb_net=0.0,
            hero_summary="Hero folded 83o.",
            first_preflop_action="fold",
            faced_action_preflop=False,
            preflop_entry_type="open_fold",
            prior_raise_count=0,
            prior_call_count=0,
            facing_state="unopened",
            faced_all_in_preflop=False,
            open_size_bb=None,
            hero_preflop_size_bb=None,
            hero_3bet_size_bb=None,
            hero_3bet_to_open_ratio=None,
            faced_4bet_after_3bet=False,
            folded_to_4bet_after_3bet=False,
        )
        for index in range(99)
    ]
    low_participation_rows.append(
        HandObservation(
            hand_id="trash-play-1",
            session_id="session-position-situation",
            tournament_id="tournament-position-situation",
            started_at="2026/05/05 10:00:00",
            format_tag="standard_mtt",
            hand_class="83o",
            position="BB",
            active_seats=6,
            stack_bb=20.0,
            bb_net=2.4,
            hero_summary="Hero completed 83o once.",
            first_preflop_action="call",
            faced_action_preflop=False,
            preflop_entry_type="open_limp_or_complete",
            prior_raise_count=0,
            prior_call_count=0,
            facing_state="unopened",
            faced_all_in_preflop=False,
            open_size_bb=None,
            hero_preflop_size_bb=1.0,
            hero_3bet_size_bb=None,
            hero_3bet_to_open_ratio=None,
            faced_4bet_after_3bet=False,
            folded_to_4bet_after_3bet=False,
        )
    )
    low_matrix = get_hand_matrix_payload(
        player_id=PLAYER_ID,
        window="all",
        selected_hand="83o",
        observations=low_participation_rows,
    )
    low_cell = low_matrix["matrix_cells"]["83o"]
    if not low_cell["low_participation"] or low_cell["style_tone"] != "low-participation":
        raise AssertionError("Sub-5% participation hands should be neutralized in the Matrix")
    if low_cell["english_read"]["stance"] != "low_participation":
        raise AssertionError("Low-participation hands should read as exposure, not performance targets")

    aof_rows = []
    for index, stack in enumerate([10.0, 14.0, 30.0]):
        aof_rows.append(
            HandObservation(
                hand_id=f"aof-{index}",
                session_id="session-position-situation",
                tournament_id="tournament-position-situation",
                started_at="2026/05/05 10:00:00",
                format_tag="standard_mtt",
                hand_class="A9o",
                position="BTN" if index < 2 else "SB",
                active_seats=6,
                stack_bb=stack,
                bb_net=-stack,
                hero_summary="Hero jammed preflop.",
                first_preflop_action="jam",
                faced_action_preflop=False,
                preflop_entry_type="open_raise_jam",
                prior_raise_count=0,
                prior_call_count=0,
                facing_state="unopened",
                faced_all_in_preflop=False,
                open_size_bb=None,
                hero_preflop_size_bb=stack,
                hero_3bet_size_bb=None,
                hero_3bet_to_open_ratio=None,
                faced_4bet_after_3bet=False,
                folded_to_4bet_after_3bet=False,
            )
        )
    aof_matrix = get_hand_matrix_payload(
        player_id=PLAYER_ID,
        window="all",
        selected_hand="A9o",
        observations=aof_rows,
    )
    aof_summary = aof_matrix["preflop_aof_summary"]
    if aof_summary["overall"]["avg_stack_bb"] != 18.0 or aof_summary["overall"]["median_stack_bb"] != 14.0:
        raise AssertionError("AOF summary should expose average and median stack depth")
    if aof_summary["overall"]["avg_bb_per_jam"] != -18.0 or aof_summary["overall"]["avg_stack_realization_pct"] != -100.0:
        raise AssertionError("AOF summary should expose actual result metrics")
    if aof_summary["short_stack_lte25"]["count"] != 2 or aof_summary["short_stack_lte25"]["avg_stack_bb"] != 12.0:
        raise AssertionError("AOF summary should expose <=25bb jam baseline")
    if not aof_summary["big_loss_clusters"]:
        raise AssertionError("AOF summary should expose repeated big-minus hover clusters")

    cooler_rows = [
        obs(
            f"kk-cooler-{index}",
            "CO",
            -20.0,
            "three_bet_jam",
            0,
            "vs_open",
            open_size_bb=2.0,
            hand_class="KK",
            stack_bb=20.0,
        )
        for index in range(5)
    ]
    cooler_rows.extend(
        [
            obs("a9o-leak-1", "HJ", -20.0, "three_bet_jam", 0, "vs_open", 2.0, "A9o", 20.0),
            obs("a9o-leak-2", "HJ", -20.0, "three_bet_jam", 0, "vs_open", 2.0, "A9o", 20.0),
            obs("a9o-leak-3", "HJ", -20.0, "three_bet_jam", 0, "vs_open", 2.0, "A9o", 20.0),
            obs("a9o-leak-4", "HJ", -20.0, "three_bet_jam", 0, "vs_open", 2.0, "A9o", 20.0),
        ]
    )
    cooler_matrix = get_hand_matrix_payload(
        player_id=PLAYER_ID,
        window="all",
        selected_hand="KK",
        observations=cooler_rows,
    )
    cooler_cards = cooler_matrix["runout_noise_cards"]
    if not any(card["hand_class"] == "KK" and card["classification"] == "premium_standard_pressure" for card in cooler_cards):
        raise AssertionError("Repeated KK premium losses should appear as runout-noise guardrails")
    if any(card["hand_class"] == "A9o" for card in cooler_cards):
        raise AssertionError("Non-premium loose pressure should not be protected as runout noise")
    kk_card = next(card for card in cooler_cards if card["hand_class"] == "KK")
    if kk_card["confidence"] != "repeated" or "prevent result-driven fear" not in kk_card["reminder"]:
        raise AssertionError("KK guardrail should remind Hero not to become scared from bad actual results")
    trend_cards = cooler_matrix["runout_noise_trends"]["last7"]["cards"]
    if not any(card["hand_class"] == "KK" for card in trend_cards):
        raise AssertionError("Recent runout-noise trend should include KK when KK losses are inside the last 7 observed days")
    old_cooler_rows = [
        obs(
            f"old-kk-cooler-{index}",
            "CO",
            -20.0,
            "three_bet_jam",
            0,
            "vs_open",
            open_size_bb=2.0,
            hand_class="KK",
            stack_bb=20.0,
            started_at="2026/04/01 10:00:00",
        )
        for index in range(5)
    ]
    old_cooler_rows.append(
        obs(
            "recent-aa-anchor",
            "CO",
            1.0,
            "open_raise",
            0,
            "unopened",
            hand_class="AA",
            stack_bb=50.0,
            started_at="2026/05/05 10:00:00",
        )
    )
    trend_matrix = get_hand_matrix_payload(
        player_id=PLAYER_ID,
        window="all",
        selected_hand="KK",
        observations=old_cooler_rows,
    )
    if any(card["hand_class"] == "KK" for card in trend_matrix["runout_noise_trends"]["last7"]["cards"]):
        raise AssertionError("Last 7 trend should not be diluted by old KK runout pain")
    if not any(card["hand_class"] == "KK" for card in trend_matrix["runout_noise_trends"]["all"]["cards"]):
        raise AssertionError("All-history runout-noise trend should preserve old repeated KK pain")


if __name__ == "__main__":
    main()
