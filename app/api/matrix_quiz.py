from __future__ import annotations

import hashlib
from datetime import UTC, date, datetime
from typing import Any
from uuid import uuid4
from zoneinfo import ZoneInfo

from app.api.hand_matrix import HERO_PLAYER_ID, get_hand_matrix_payload
from core.storage.models import OperatorReviewRecord

GRADE_CHOICES = ["Baseline", "Watch", "Leak", "Value"]
REACTION_CHOICES = {"expected", "surprising", "memory_mismatch", "needs_review"}
QUIZ_CARD_COUNT = 3


def _today_label() -> str:
    return datetime.now(ZoneInfo("America/Toronto")).date().isoformat()


def _resolve_date(raw: str | None) -> str:
    if not raw:
        return _today_label()
    try:
        return date.fromisoformat(raw).isoformat()
    except ValueError:
        return _today_label()


def _target_id(player_id: str, quiz_date: str, subject_key: str, source: str) -> str:
    clean_subject = subject_key.replace(" ", "_").replace("/", "_").replace(":", "_")
    return f"{player_id}:{quiz_date}:{source}:{clean_subject}"


def _safe_dict(raw: Any) -> dict[str, Any]:
    return raw if isinstance(raw, dict) else {}


def _positions_text(positions: Any) -> str:
    items = _safe_dict(positions)
    if not items:
        return "unknown positions"
    return ", ".join(f"{key} {value}x" for key, value in sorted(items.items()))


def _formats_text(formats: Any) -> str:
    items = _safe_dict(formats)
    if not items:
        return "format unknown"
    return ", ".join(f"{key} {value}x" for key, value in sorted(items.items()))


def _study_takeaway(grade: str, subject: str) -> str:
    if grade == "Leak":
        return f"Before approving {subject} again, separate the exact action node from the hand-class headline."
    if grade == "Value":
        return f"Preserve the working {subject} pattern, but keep the context gate tight before expanding it."
    if grade == "Watch":
        return f"Treat {subject} as a calibration question; the point is the boundary, not a verdict."
    return f"Use {subject} as baseline calibration and compare it against nearby hand classes."


def _card(
    *,
    player_id: str,
    quiz_date: str,
    source: str,
    subject: str,
    subject_key: str,
    grade: str,
    priority: float,
    prompt: dict[str, Any],
    reveal: dict[str, Any],
) -> dict[str, Any]:
    card_id = _target_id(player_id, quiz_date, subject_key, source)
    return {
        "id": card_id,
        "source": source,
        "subject": subject,
        "question": f"What is Hero's real baseline grade for {subject}?",
        "choices": GRADE_CHOICES,
        "prompt": {
            **prompt,
            "hidden_until_answer": ["avg_bb_per_hand", "avg_stack_realization_pct", "actual_grade", "interpretation"],
        },
        "answer": {
            "actual_grade": grade,
            **reveal,
        },
        "_priority": priority,
    }


def _cards_from_mandatory(player_id: str, quiz_date: str, matrix_payload: dict[str, Any]) -> list[dict[str, Any]]:
    cards = []
    for item in matrix_payload.get("mandatory_correction_cards") or []:
        subject = str(item.get("hand_class") or item.get("title") or "hand class")
        entry_type = str(item.get("entry_type") or "unknown_action")
        cards.append(
            _card(
                player_id=player_id,
                quiz_date=quiz_date,
                source="mandatory_correction",
                subject=subject,
                subject_key=f"{subject}:{entry_type}",
                grade="Leak",
                priority=3000 + float(item.get("severity_score") or 0),
                prompt={
                    "hand_class": subject,
                    "entry_type": entry_type,
                    "played_count": item.get("played_count"),
                    "dealt_count": None,
                    "context": {
                        "positions": _positions_text(item.get("positions")),
                        "formats": _formats_text(item.get("formats")),
                    },
                    "visible_stat_lines": [
                        f"{item.get('played_count') or 0} repeated {entry_type} spots",
                        f"Positions: {_positions_text(item.get('positions'))}",
                        f"Formats: {_formats_text(item.get('formats'))}",
                    ],
                },
                reveal={
                    "avg_bb_per_hand": item.get("avg_bb_per_hand"),
                    "avg_stack_realization_pct": item.get("avg_stack_realization_pct"),
                    "played_count": item.get("played_count"),
                    "dealt_count": None,
                    "why": item.get("read")
                    or "This hand/action pair is a correction candidate because repeated stack-normalized damage is visible.",
                    "study_takeaway": item.get("recommended_correction") or _study_takeaway("Leak", subject),
                    "truth_policy": "Learning log only; this does not mutate canonical Matrix truth.",
                },
            )
        )
    return cards


def _cards_from_hidden_value(player_id: str, quiz_date: str, matrix_payload: dict[str, Any]) -> list[dict[str, Any]]:
    cards = []
    for item in matrix_payload.get("hidden_value_cards") or []:
        subject = str(item.get("hand_class") or item.get("title") or "hand class")
        entry_type = str(item.get("entry_type") or "unknown_action")
        cards.append(
            _card(
                player_id=player_id,
                quiz_date=quiz_date,
                source="hidden_value",
                subject=subject,
                subject_key=f"{subject}:{entry_type}",
                grade="Value",
                priority=2000 + float(item.get("value_score") or 0),
                prompt={
                    "hand_class": subject,
                    "entry_type": entry_type,
                    "played_count": item.get("played_count"),
                    "dealt_count": None,
                    "context": {
                        "positions": _positions_text(item.get("positions")),
                        "formats": _formats_text(item.get("formats")),
                    },
                    "visible_stat_lines": [
                        f"{item.get('played_count') or 0} repeated {entry_type} spots",
                        f"Positions: {_positions_text(item.get('positions'))}",
                        f"Formats: {_formats_text(item.get('formats'))}",
                    ],
                },
                reveal={
                    "avg_bb_per_hand": item.get("avg_bb_per_hand"),
                    "avg_stack_realization_pct": item.get("avg_stack_realization_pct"),
                    "played_count": item.get("played_count"),
                    "dealt_count": None,
                    "why": item.get("read")
                    or "This is a positive execution candidate rather than an automatic correction target.",
                    "study_takeaway": item.get("recommended_keep") or _study_takeaway("Value", subject),
                    "truth_policy": "Positive execution candidates remain reviewable; this is not solver approval.",
                },
            )
        )
    return cards


def _cards_from_study_panels(player_id: str, quiz_date: str, matrix_payload: dict[str, Any]) -> list[dict[str, Any]]:
    cards = []
    panels = _safe_dict(matrix_payload.get("study_panels"))
    source_priority = {
        "clear_repeated_mistakes": 1500,
        "belief_driven_patterns": 1400,
        "study_worthy_spots": 1300,
    }
    for panel_key, items in panels.items():
        for item in items or []:
            subject = str(item.get("family") or item.get("title") or "study family")
            repeated = int(item.get("repeated_count") or 0)
            cards.append(
                _card(
                    player_id=player_id,
                    quiz_date=quiz_date,
                    source=f"study_panel:{panel_key}",
                    subject=subject,
                    subject_key=subject,
                    grade="Watch",
                    priority=source_priority.get(panel_key, 1200) + repeated,
                    prompt={
                        "hand_class": subject,
                        "entry_type": item.get("classification") or "study_family",
                        "played_count": repeated,
                        "dealt_count": None,
                        "context": {
                            "positions": _positions_text(item.get("positions")),
                            "formats": _formats_text(item.get("formats")),
                            "actions": _positions_text(item.get("actions")),
                        },
                        "visible_stat_lines": [
                            f"{repeated} repeated family spots",
                            f"Positions: {_positions_text(item.get('positions'))}",
                            f"Actions: {_positions_text(item.get('actions'))}",
                        ],
                    },
                    reveal={
                        "avg_bb_per_hand": None,
                        "avg_stack_realization_pct": None,
                        "played_count": repeated,
                        "dealt_count": None,
                        "why": item.get("why_it_matters")
                        or "This is a study-worthy pattern, so the honest grade is Watch.",
                        "study_takeaway": _study_takeaway("Watch", subject),
                        "truth_policy": "Study panels are repeated-pattern prompts, not direct EV claims.",
                    },
                )
            )
    return cards


def _fallback_grade(cell: dict[str, Any]) -> str:
    played = int(cell.get("played_count") or cell.get("hands_played") or 0)
    avg_bb = cell.get("avg_bb_per_hand")
    stack_pct = cell.get("avg_stack_realization_pct")
    if played < 8 or avg_bb is None or stack_pct is None:
        return "Watch"
    avg_bb_value = float(avg_bb)
    stack_value = float(stack_pct)
    if avg_bb_value <= -0.4 and stack_value <= -5:
        return "Leak"
    if avg_bb_value >= 0.4 and stack_value >= 5:
        return "Value"
    if -0.4 < avg_bb_value < 0.4 and -5 < stack_value < 5:
        return "Baseline"
    return "Watch"


def _cards_from_fallback_cells(player_id: str, quiz_date: str, matrix_payload: dict[str, Any]) -> list[dict[str, Any]]:
    cards = []
    cells = _safe_dict(matrix_payload.get("matrix_cells"))
    for hand_class, cell in cells.items():
        cell = _safe_dict(cell)
        played = int(cell.get("played_count") or cell.get("hands_played") or 0)
        dealt = int(cell.get("dealt_count") or 0)
        if played <= 0 and dealt <= 0:
            continue
        grade = _fallback_grade(cell)
        avg_bb = cell.get("avg_bb_per_hand")
        stack_pct = cell.get("avg_stack_realization_pct")
        signal = abs(float(avg_bb or 0)) * 10 + abs(float(stack_pct or 0)) + min(played, 30)
        action_lines = [
            f"{row.get('entry_type')}: {row.get('played_count') or 0}x"
            for row in (cell.get("hover_action_breakdown") or [])[:3]
        ]
        cards.append(
            _card(
                player_id=player_id,
                quiz_date=quiz_date,
                source="matrix_cell_fallback",
                subject=str(hand_class),
                subject_key=str(hand_class),
                grade=grade,
                priority=1000 + signal,
                prompt={
                    "hand_class": hand_class,
                    "entry_type": "mixed_actions",
                    "played_count": played,
                    "dealt_count": dealt,
                    "context": {
                        "action_mix": ", ".join(action_lines) if action_lines else "no action breakdown yet",
                    },
                    "visible_stat_lines": [
                        f"{played} played / {dealt} dealt",
                        f"Action mix: {', '.join(action_lines) if action_lines else 'no action breakdown yet'}",
                        f"Sample band: {cell.get('sample_band') or 'unknown'}",
                    ],
                },
                reveal={
                    "avg_bb_per_hand": avg_bb,
                    "avg_stack_realization_pct": stack_pct,
                    "played_count": played,
                    "dealt_count": dealt,
                    "why": _fallback_why(str(hand_class), grade, played),
                    "study_takeaway": _study_takeaway(grade, str(hand_class)),
                    "truth_policy": "Fallback Matrix cells are quiz material only when higher-signal queues are short.",
                },
            )
        )
    return cards


def _fallback_why(hand_class: str, grade: str, played: int) -> str:
    if grade == "Watch":
        return f"{hand_class} has {played} played samples, but the signal is thin or mixed enough to avoid fake precision."
    if grade == "Baseline":
        return f"{hand_class} has enough played samples without a strong correction or value signal."
    if grade == "Leak":
        return f"{hand_class} is negative in both raw and stack-normalized fallback Matrix views."
    return f"{hand_class} is positive in both raw and stack-normalized fallback Matrix views."


def _dedupe(cards: list[dict[str, Any]]) -> list[dict[str, Any]]:
    best: dict[str, dict[str, Any]] = {}
    for card in cards:
        subject = str(card.get("subject") or card.get("id"))
        current = best.get(subject)
        if not current or float(card.get("_priority") or 0) > float(current.get("_priority") or 0):
            best[subject] = card
    return list(best.values())


def _daily_pick(cards: list[dict[str, Any]], player_id: str, quiz_date: str, count: int) -> list[dict[str, Any]]:
    ordered = sorted(cards, key=lambda item: (-float(item.get("_priority") or 0), str(item.get("id") or "")))
    if not ordered:
        return []
    seed = hashlib.sha256(f"{player_id}:{quiz_date}:matrix_quiz".encode("utf-8")).hexdigest()
    offset = int(seed[:8], 16) % len(ordered)
    rotated = ordered[offset:] + ordered[:offset]
    return rotated[:count]


def _public_card(card: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in card.items() if key != "_priority"}


def build_matrix_quiz_payload(
    player_id: str = HERO_PLAYER_ID,
    quiz_date: str | None = None,
    matrix_payload: dict[str, Any] | None = None,
    card_count: int = QUIZ_CARD_COUNT,
) -> dict[str, Any]:
    resolved_player_id = player_id or HERO_PLAYER_ID
    resolved_date = _resolve_date(quiz_date)
    matrix_payload = matrix_payload or get_hand_matrix_payload(player_id=resolved_player_id, window="all")
    total_observations = int((_safe_dict(matrix_payload.get("summary")).get("total_observations") or 0))
    if total_observations <= 0:
        return {
            "status": "empty",
            "player_id": resolved_player_id,
            "date": resolved_date,
            "cards": [],
            "blank_state": "No parsed Hero hand observations are available for a Matrix quiz yet.",
            "truth_policy": "Zero-hand Matrix results must not emit fake quiz cards.",
        }

    cards = _dedupe(
        _cards_from_mandatory(resolved_player_id, resolved_date, matrix_payload)
        + _cards_from_hidden_value(resolved_player_id, resolved_date, matrix_payload)
        + _cards_from_study_panels(resolved_player_id, resolved_date, matrix_payload)
    )
    if len(cards) < card_count:
        existing_ids = {card["id"] for card in cards}
        fallback_cards = sorted(
            _cards_from_fallback_cells(resolved_player_id, resolved_date, matrix_payload),
            key=lambda item: (-float(item.get("_priority") or 0), str(item.get("id") or "")),
        )
        for card in fallback_cards:
            if card["id"] not in existing_ids:
                cards.append(card)
                existing_ids.add(card["id"])
            if len(cards) >= card_count:
                break

    selected = [_public_card(card) for card in _daily_pick(cards, resolved_player_id, resolved_date, card_count)]
    return {
        "status": "ok" if selected else "empty",
        "player_id": resolved_player_id,
        "date": resolved_date,
        "choices": GRADE_CHOICES,
        "cards": selected,
        "summary": {
            "card_count": len(selected),
            "candidate_count": len(cards),
            "source_policy": "High-signal Matrix candidates first; fallback Matrix cells only fill gaps.",
        },
        "truth_policy": "Daily Matrix Quiz is a post-hoc Hero baseline recall surface, not solver truth and not RTA.",
    }


def record_matrix_quiz_attempt(
    repository: Any,
    *,
    player_id: str,
    quiz_date: str | None,
    card_id: str,
    selected_grade: str,
    reaction: str | None = None,
    matrix_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    resolved_date = _resolve_date(quiz_date)
    quiz = build_matrix_quiz_payload(player_id=player_id, quiz_date=resolved_date, matrix_payload=matrix_payload)
    cards = {str(card.get("id")): card for card in quiz.get("cards") or []}
    card = cards.get(card_id)
    if not card:
        return {"ok": False, "reason": "quiz_card_not_found", "card_id": card_id}

    normalized_grade = selected_grade.strip().title()
    if normalized_grade not in GRADE_CHOICES:
        return {"ok": False, "reason": "unsupported_grade", "selected_grade": selected_grade}
    normalized_reaction = reaction.strip().lower() if reaction else None
    if normalized_reaction and normalized_reaction not in REACTION_CHOICES:
        return {"ok": False, "reason": "unsupported_reaction", "reaction": reaction}

    actual_grade = str((card.get("answer") or {}).get("actual_grade") or "")
    correct = normalized_grade == actual_grade
    review_id = f"review-{uuid4()}"
    record = OperatorReviewRecord(
        id=review_id,
        target_type="matrix_quiz_card",
        target_id=card_id,
        review_type="matrix_quiz_attempt",
        decision=normalized_grade.lower(),
        notes=normalized_reaction,
        review_payload={
            "source_review_id": review_id,
            "player_id": player_id,
            "date": resolved_date,
            "card_id": card_id,
            "subject": card.get("subject"),
            "source": card.get("source"),
            "selected_grade": normalized_grade,
            "actual_grade": actual_grade,
            "correct": correct,
            "reaction": normalized_reaction,
            "revealed_metrics": {
                "avg_bb_per_hand": (card.get("answer") or {}).get("avg_bb_per_hand"),
                "avg_stack_realization_pct": (card.get("answer") or {}).get("avg_stack_realization_pct"),
                "played_count": (card.get("answer") or {}).get("played_count"),
                "dealt_count": (card.get("answer") or {}).get("dealt_count"),
            },
            "truth_policy": "Matrix quiz attempts are learning logs only and do not update canonical Hero memory.",
        },
        created_at=datetime.now(UTC),
    )
    repository.create_operator_review(record)
    return {
        "ok": True,
        "card_id": card_id,
        "selected_grade": normalized_grade,
        "actual_grade": actual_grade,
        "correct": correct,
        "reaction": normalized_reaction,
    }
