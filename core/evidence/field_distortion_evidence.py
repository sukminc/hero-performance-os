from __future__ import annotations

from core.evidence.evidence_models import EvidenceCandidate
from core.storage.models import HandRecord


def build_field_distortion_evidence(hands: list[HandRecord]) -> list[EvidenceCandidate]:
    if len(hands) < 3:
        return []

    multiway_like = [hand for hand in hands if (hand.players_to_flop or 0) >= 3]
    boards_seen = [hand for hand in hands if hand.board_texture_summary]

    candidates: list[EvidenceCandidate] = []
    if len(multiway_like) >= 2:
        candidates.append(
            EvidenceCandidate(
                evidence_type="field_distortion_candidate",
                entity_scope="field",
                entity_key="multiway_pressure",
                direction="shift",
                strength_score=round(len(multiway_like) / len(hands), 3),
                confidence=0.58,
                sample_size=len(hands),
                explanation="Multiple hands reached genuinely multiway-like pressure, which is a stronger sign of loose field texture than a single noisy spot.",
                source_hand_ids=[hand.id for hand in multiway_like[:5]],
            )
        )
    if len(boards_seen) >= max(3, (len(hands) * 2) // 3):
        candidates.append(
            EvidenceCandidate(
                evidence_type="field_distortion_candidate",
                entity_scope="field",
                entity_key="board_contact_density",
                direction="shift",
                strength_score=round(len(boards_seen) / len(hands), 3),
                confidence=0.53,
                sample_size=len(hands),
                explanation="A large share of hands reached boards, suggesting a stickier field texture rather than clean preflop resolution.",
                source_hand_ids=[hand.id for hand in boards_seen[:5]],
            )
        )
    return candidates
