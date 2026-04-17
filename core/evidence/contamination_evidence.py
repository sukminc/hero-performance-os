from __future__ import annotations

from core.evidence.evidence_models import EvidenceCandidate
from core.storage.models import HandRecord


def build_contamination_evidence(hands: list[HandRecord]) -> list[EvidenceCandidate]:
    if len(hands) < 4:
        return []

    blind_hands = [hand for hand in hands if hand.hero_position in {"small blind", "big blind"}]
    limp_like_postflop = [hand for hand in blind_hands if hand.players_to_flop]
    if len(blind_hands) < 3 or len(limp_like_postflop) < 2:
        return []

    contamination_ratio = len(limp_like_postflop) / len(blind_hands)
    if contamination_ratio < 0.67:
        return []

    return [
        EvidenceCandidate(
            evidence_type="contamination_risk_candidate",
            entity_scope="contamination",
            entity_key="blind_structure_absorption",
            direction="negative",
            strength_score=round(contamination_ratio, 3),
            confidence=0.6,
            sample_size=len(blind_hands),
            explanation="Blind-position hands kept carrying through to postflop at a high rate, which raises a more credible contamination risk than a one-off messy sample.",
            source_hand_ids=[hand.id for hand in limp_like_postflop[:5]],
        )
    ]
