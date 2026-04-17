from __future__ import annotations

from collections import defaultdict

from core.evidence.evidence_models import EvidenceCandidate
from core.evidence.evidence_utils import hand_outcome
from core.storage.models import HandRecord


def _classify_hand(hand: HandRecord) -> str | None:
    raw_payload = hand.raw_payload or {}
    block = raw_payload.get("block") or []
    for row in block:
        if row.startswith("Dealt to Hero"):
            start = row.find("[")
            end = row.find("]")
            if start >= 0 and end > start:
                cards = row[start + 1:end].split()
                if len(cards) == 2:
                    ranks = "".join(card[0] for card in cards)
                    suited = "s" if cards[0][-1] == cards[1][-1] else "o"
                    if ranks[0] == ranks[1]:
                        return ranks
                    return f"{ranks}{suited}"
    return None


def build_hand_class_evidence(hands: list[HandRecord]) -> list[EvidenceCandidate]:
    grouped: dict[str, list[HandRecord]] = defaultdict(list)
    for hand in hands:
        hand_class = _classify_hand(hand)
        if hand_class:
            grouped[hand_class].append(hand)

    evidence: list[EvidenceCandidate] = []
    for hand_class, grouped_hands in grouped.items():
        if len(grouped_hands) < 2:
            continue

        losing_hands = sum(1 for hand in grouped_hands if hand_outcome(hand) == "loss")
        winning_hands = sum(1 for hand in grouped_hands if hand_outcome(hand) == "win")

        loss_rate = losing_hands / len(grouped_hands)
        win_rate = winning_hands / len(grouped_hands)
        if loss_rate >= 0.67:
            evidence.append(
                EvidenceCandidate(
                    evidence_type="hand_class_underperformance",
                    entity_scope="hand_class",
                    entity_key=hand_class,
                    direction="negative",
                    strength_score=round(loss_rate, 3),
                    confidence=min(0.82, 0.46 + len(grouped_hands) * 0.07),
                    sample_size=len(grouped_hands),
                    explanation=f"{hand_class} produced a clearly loss-heavy sample in this session and is a more believable leak-review candidate than a mixed one-off result.",
                    source_hand_ids=[hand.id for hand in grouped_hands[:5]],
                )
            )
        elif win_rate >= 0.75 and len(grouped_hands) >= 3:
            evidence.append(
                EvidenceCandidate(
                    evidence_type="stable_strength_candidate",
                    entity_scope="hand_class",
                    entity_key=hand_class,
                    direction="positive",
                    strength_score=round(win_rate, 3),
                    confidence=min(0.8, 0.42 + len(grouped_hands) * 0.06),
                    sample_size=len(grouped_hands),
                    explanation=f"{hand_class} held up consistently enough in this session to count as a provisional execution strength.",
                    source_hand_ids=[hand.id for hand in grouped_hands[:5]],
                )
            )
    return evidence
