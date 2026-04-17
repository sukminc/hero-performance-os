from __future__ import annotations

from core.evidence.evidence_models import EvidenceCandidate
from core.storage.models import HandRecord


def build_style_drift_evidence(hands: list[HandRecord]) -> list[EvidenceCandidate]:
    if len(hands) < 3:
        return []

    passive_positions = {"small blind", "big blind"}
    blind_hands = [hand for hand in hands if hand.hero_position in passive_positions]
    flops_seen = [hand for hand in hands if hand.players_to_flop]
    deep_stack_hands = [hand for hand in hands if (hand.effective_stack_bb or 0) >= 30]

    candidates: list[EvidenceCandidate] = []
    if len(blind_hands) >= 2 and len(flops_seen) <= max(1, len(hands) // 4):
        candidates.append(
            EvidenceCandidate(
                evidence_type="style_drift_candidate",
                entity_scope="style",
                entity_key="passive_blind_compliance",
                direction="negative",
                strength_score=round(len(blind_hands) / len(hands), 3),
                confidence=0.62,
                sample_size=len(hands),
                explanation="Blind-heavy volume with very limited flop continuation is starting to look more like passive compliance drift than normal variance.",
                source_hand_ids=[hand.id for hand in blind_hands[:5]],
            )
        )
    if len(deep_stack_hands) >= 2 and len(flops_seen) >= max(3, len(hands) // 2):
        candidates.append(
            EvidenceCandidate(
                evidence_type="style_drift_candidate",
                entity_scope="style",
                entity_key="high_engagement_profile",
                direction="shift",
                strength_score=round(len(flops_seen) / len(hands), 3),
                confidence=0.55,
                sample_size=len(hands),
                explanation="Deep-stack hands kept carrying into flops at a high rate, which is worth tracking as a possible engagement shift rather than a one-off table pattern.",
                source_hand_ids=[hand.id for hand in flops_seen[:5]],
            )
        )
    return candidates
