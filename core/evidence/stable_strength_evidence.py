from __future__ import annotations

from collections import Counter

from core.evidence.evidence_models import EvidenceCandidate
from core.evidence.evidence_utils import has_positive_execution_cue
from core.storage.models import HandRecord


def build_stable_strength_evidence(hands: list[HandRecord]) -> list[EvidenceCandidate]:
    pattern_counter = Counter()
    pattern_refs: dict[str, list[str]] = {}
    for hand in hands:
        pattern = str((hand.result_summary or {}).get("pattern") or "").strip()
        if not pattern:
            continue
        pattern_counter[pattern] += 1
        pattern_refs.setdefault(pattern, []).append(hand.id)

    if pattern_counter:
        pattern, count = pattern_counter.most_common(1)[0]
        if count >= 2:
            return [
                EvidenceCandidate(
                    evidence_type="stable_strength_candidate",
                    entity_scope="execution",
                    entity_key=pattern,
                    direction="positive",
                    strength_score=round(min(1.0, 0.5 + count * 0.08), 3),
                    confidence=round(min(0.82, 0.52 + count * 0.07), 3),
                    sample_size=count,
                    explanation=f"Session repeated the execution pattern '{pattern}' often enough to preserve as real baseline evidence rather than one-off wording.",
                    source_hand_ids=pattern_refs.get(pattern, [])[:5],
                )
            ]

    positive_execution_hands = [hand for hand in hands if has_positive_execution_cue(hand)]
    if len(positive_execution_hands) >= max(2, len(hands) // 2):
        return [
            EvidenceCandidate(
                evidence_type="stable_strength_candidate",
                entity_scope="execution",
                entity_key="reset_and_preservation_discipline",
                direction="positive",
                strength_score=round(len(positive_execution_hands) / len(hands), 3),
                confidence=0.64,
                sample_size=len(hands),
                explanation="Multiple hands carried explicit reset, breathing, or chip-preservation cues, which is stronger positive execution evidence than a single named pattern.",
                source_hand_ids=[hand.id for hand in positive_execution_hands[:5]],
            )
        ]

    if len(hands) < 4:
        return []

    surviving_hands = [
        hand for hand in hands if "folded" not in (hand.result_summary or {}).get("hero_summary", "").lower()
    ]
    if len(surviving_hands) < max(2, len(hands) // 3):
        return []

    return [
        EvidenceCandidate(
            evidence_type="stable_strength_candidate",
            entity_scope="execution",
            entity_key="session_survival_discipline",
            direction="positive",
            strength_score=round(len(surviving_hands) / len(hands), 3),
            confidence=0.58,
            sample_size=len(hands),
            explanation="Enough hands avoided collapse outcomes to keep baseline tournament discipline on the board for this session.",
            source_hand_ids=[hand.id for hand in surviving_hands[:5]],
        )
    ]
