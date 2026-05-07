#!/usr/bin/env python3
"""Deterministic tests for the Daily Hero Baseline Quiz payload."""

from __future__ import annotations

import sys
from dataclasses import asdict
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.api.hand_matrix import HandObservation, get_hand_matrix_payload
from app.api.matrix_quiz import build_matrix_quiz_payload, record_matrix_quiz_attempt

PLAYER_ID = "matrix-quiz-player"


class StubRepository:
    def __init__(self) -> None:
        self.reviews: list[dict] = []

    def create_operator_review(self, record) -> None:
        self.reviews.append(deepcopy(asdict(record)))


def obs(
    hand_id: str,
    hand_class: str,
    position: str,
    stack_bb: float,
    bb_net: float,
    action: str,
    entry_type: str,
) -> HandObservation:
    return HandObservation(
        hand_id=hand_id,
        session_id="session-matrix-quiz",
        tournament_id="tournament-matrix-quiz",
        started_at="2026/05/05 10:00:00",
        format_tag="standard_mtt",
        hand_class=hand_class,
        position=position,
        active_seats=6,
        stack_bb=stack_bb,
        bb_net=bb_net,
        hero_summary=f"Hero {entry_type} with {hand_class}.",
        first_preflop_action=action,
        faced_action_preflop=False,
        preflop_entry_type=entry_type,
        prior_raise_count=0,
        prior_call_count=0,
        facing_state="unopened",
        faced_all_in_preflop=False,
        open_size_bb=None,
        hero_preflop_size_bb=2.0,
        hero_3bet_size_bb=None,
        hero_3bet_to_open_ratio=None,
        faced_4bet_after_3bet=False,
        folded_to_4bet_after_3bet=False,
    )


def rich_matrix_payload() -> dict:
    observations = [
        obs("66-1", "66", "HJ", 14.0, -14.0, "jam", "open_raise_jam"),
        obs("66-2", "66", "HJ", 12.0, -12.0, "jam", "open_raise_jam"),
        obs("kjo-1", "KJo", "UTG", 14.0, 0.0, "jam", "open_raise_jam"),
        obs("kjo-2", "KJo", "HJ", 13.0, 0.0, "raise", "open_raise"),
        obs("kjo-3", "KJo", "HJ", 12.0, 0.0, "jam", "open_raise_jam"),
    ]
    observations.extend(
        obs(f"kqo-{index}", "KQo", "CO", 20.0, 3.0, "raise", "open_raise")
        for index in range(1, 6)
    )
    observations.extend(
        obs(f"a5s-{index}", "A5s", "BTN", 22.0, 3.0, "raise", "open_raise")
        for index in range(1, 6)
    )
    return get_hand_matrix_payload(player_id=PLAYER_ID, window="all", observations=observations)


def assert_no_hidden_metrics_in_prompt(card: dict) -> None:
    prompt = card.get("prompt") or {}
    forbidden = {"avg_bb_per_hand", "avg_stack_realization_pct", "actual_grade", "interpretation"}
    exposed = forbidden.intersection(prompt.keys())
    if exposed:
        raise AssertionError(f"Prompt leaked hidden answer metrics: {sorted(exposed)}")


def main() -> None:
    matrix = rich_matrix_payload()
    quiz = build_matrix_quiz_payload(player_id=PLAYER_ID, quiz_date="2026-05-05", matrix_payload=matrix)
    cards = quiz.get("cards") or []
    if len(cards) != 3:
        raise AssertionError("Quiz should return exactly 3 cards when enough candidates exist")
    for card in cards:
        assert_no_hidden_metrics_in_prompt(card)
        answer = card.get("answer") or {}
        if answer.get("actual_grade") not in {"Baseline", "Watch", "Leak", "Value"}:
            raise AssertionError("Reveal payload should include a supported actual grade")
        if "why" not in answer or "study_takeaway" not in answer:
            raise AssertionError("Reveal payload should include explanation and study takeaway")

    stable_again = build_matrix_quiz_payload(player_id=PLAYER_ID, quiz_date="2026-05-05", matrix_payload=matrix)
    if [card["id"] for card in cards] != [card["id"] for card in stable_again.get("cards") or []]:
        raise AssertionError("Same player/date should produce stable quiz cards")

    next_day = build_matrix_quiz_payload(player_id=PLAYER_ID, quiz_date="2026-05-06", matrix_payload=matrix)
    if quiz.get("summary", {}).get("candidate_count", 0) > 3 and [card["id"] for card in cards] == [
        card["id"] for card in next_day.get("cards") or []
    ]:
        raise AssertionError("Different dates should rotate candidate order when more than 3 candidates exist")

    zero_matrix = get_hand_matrix_payload(player_id=PLAYER_ID, window="all", observations=[])
    empty = build_matrix_quiz_payload(player_id=PLAYER_ID, quiz_date="2026-05-05", matrix_payload=zero_matrix)
    if empty.get("cards") != [] or empty.get("status") != "empty":
        raise AssertionError("Zero-hand Matrix payload should produce an honest empty quiz")

    repo = StubRepository()
    selected = cards[0]["answer"]["actual_grade"]
    attempt = record_matrix_quiz_attempt(
        repo,
        player_id=PLAYER_ID,
        quiz_date="2026-05-05",
        card_id=cards[0]["id"],
        selected_grade=selected,
        reaction="expected",
        matrix_payload=matrix,
    )
    if attempt.get("ok") is not True or not attempt.get("correct"):
        raise AssertionError("Quiz attempt logging should preserve correctness")
    if len(repo.reviews) != 1:
        raise AssertionError("Quiz attempt should write one operator review overlay")
    review_payload = repo.reviews[0]["review_payload"]
    if review_payload.get("truth_policy") != "Matrix quiz attempts are learning logs only and do not update canonical Hero memory.":
        raise AssertionError("Quiz attempt should preserve learning-log-only truth policy")


if __name__ == "__main__":
    main()
