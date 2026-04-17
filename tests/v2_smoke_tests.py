#!/usr/bin/env python3
"""Smoke tests for the V2 ingest -> evidence -> memory -> surfaces chain."""

from __future__ import annotations

import sys
from dataclasses import asdict
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.ingest.file_ingest import ingest_gg_file
from core.memory.memory_updater import update_memory_from_session_evidence
from core.parsing.gg_parser import parse_gg_text_file
from core.storage.models import IngestFileRecord, MemoryItemRecord, OperatorReviewRecord, SessionEvidenceRecord, SessionRecord
from core.surfaces.command_center import build_command_center_payload
from core.surfaces.memory_graph import build_memory_graph_payload
from core.surfaces.session_lab import build_session_lab_payload
from core.surfaces.today import build_today_surface


HERO_PLAYER_ID = "4c9d1e29-1f6b-4e5f-92da-111111111111"


class InMemoryV2Repository:
    def __init__(self) -> None:
        self.ingest_files: dict[str, dict[str, Any]] = {}
        self.sessions: dict[str, dict[str, Any]] = {}
        self.hands: list[dict[str, Any]] = []
        self.session_evidence: list[dict[str, Any]] = []
        self.memory_items: dict[tuple[str, str, str], dict[str, Any]] = {}
        self.operator_reviews: list[dict[str, Any]] = []
        self.surface_snapshots: list[dict[str, Any]] = []
        self.schema_ensured = False

    def ensure_schema(self) -> None:
        self.schema_ensured = True

    def get_ingest_file_by_hash(self, file_hash: str) -> dict[str, Any] | None:
        matches = [row for row in self.ingest_files.values() if row["file_hash"] == file_hash]
        return deepcopy(matches[-1]) if matches else None

    def create_ingest_file(self, record: IngestFileRecord) -> None:
        self.ingest_files[record.id] = deepcopy(asdict(record))

    def update_ingest_status(self, ingest_file_id: str, status: str, raw_metadata: dict[str, Any] | None = None) -> None:
        self.ingest_files[ingest_file_id]["status"] = status
        if raw_metadata is not None:
            self.ingest_files[ingest_file_id]["raw_metadata"] = deepcopy(raw_metadata)

    def create_session(self, record: SessionRecord) -> None:
        self.sessions[record.id] = deepcopy(asdict(record))

    def fetch_session(self, session_id: str) -> dict[str, Any] | None:
        session = self.sessions.get(session_id)
        return deepcopy(session) if session else None

    def fetch_latest_session_id(self, player_id: str) -> str | None:
        matches = [row for row in self.sessions.values() if row["player_id"] == player_id]
        return matches[-1]["id"] if matches else None

    def create_hands(self, hands: list) -> None:
        for hand in hands:
            self.hands.append(deepcopy(asdict(hand)))

    def fetch_hands_for_session(self, session_id: str, limit: int = 20) -> list[dict[str, Any]]:
        matches = [row for row in self.hands if row["session_id"] == session_id]
        return deepcopy(matches[:limit])

    def create_session_evidence(self, evidence_rows: list[SessionEvidenceRecord]) -> None:
        for row in evidence_rows:
            self.session_evidence.append(deepcopy(asdict(row)))

    def fetch_session_evidence(self, session_id: str) -> list[dict[str, Any]]:
        matches = [row for row in self.session_evidence if row["session_id"] == session_id]
        return deepcopy(matches)

    def get_memory_item(self, player_id: str, memory_type: str, memory_key: str) -> dict[str, Any] | None:
        item = self.memory_items.get((player_id, memory_type, memory_key))
        return deepcopy(item) if item else None

    def upsert_memory_item(self, record: MemoryItemRecord) -> None:
        self.memory_items[(record.player_id, record.memory_type, record.memory_key)] = deepcopy(asdict(record))

    def fetch_memory_items(self, player_id: str, statuses: list[str] | None = None) -> list[dict[str, Any]]:
        items = [row for row in self.memory_items.values() if row["player_id"] == player_id]
        if statuses is not None:
            items = [row for row in items if row["status"] in statuses]
        rank = {"active": 0, "baseline": 1, "watch": 2, "resolved": 3}
        items.sort(
            key=lambda row: (
                rank.get(str(row.get("status")), 4),
                -(int(row.get("evidence_count") or 0)),
                -(float(row.get("confidence") or 0.0)),
            )
        )
        return deepcopy(items)

    def fetch_memory_items_for_session(self, player_id: str, session_id: str) -> list[dict[str, Any]]:
        items = [
            row
            for row in self.memory_items.values()
            if row["player_id"] == player_id and row.get("last_seen_session_id") == session_id
        ]
        rank = {"active": 0, "baseline": 1, "watch": 2, "resolved": 3}
        items.sort(
            key=lambda row: (
                rank.get(str(row.get("status")), 4),
                -(int(row.get("evidence_count") or 0)),
                -(float(row.get("confidence") or 0.0)),
            )
        )
        return deepcopy(items)

    def create_operator_review(self, record: OperatorReviewRecord) -> None:
        self.operator_reviews.append(deepcopy(asdict(record)))

    def fetch_operator_reviews(self, target_type: str, target_id: str, review_type: str | None = None) -> list[dict[str, Any]]:
        reviews = [
            row
            for row in self.operator_reviews
            if row["target_type"] == target_type and row["target_id"] == target_id
        ]
        if review_type is not None:
            reviews = [row for row in reviews if row["review_type"] == review_type]
        reviews.sort(key=lambda row: (str(row.get("created_at") or ""), str(row.get("id") or "")), reverse=True)
        return deepcopy(reviews)

    def create_surface_snapshot(
        self,
        snapshot_id: str,
        player_id: str,
        session_id: str | None,
        surface_type: str,
        payload: dict[str, Any],
        confidence_summary: dict[str, Any],
    ) -> None:
        self.surface_snapshots.append(
            {
                "id": snapshot_id,
                "player_id": player_id,
                "session_id": session_id,
                "surface_type": surface_type,
                "payload": deepcopy(payload),
                "confidence_summary": deepcopy(confidence_summary),
            }
        )

    def fetch_latest_surface_snapshot(self, player_id: str, surface_type: str) -> dict[str, Any] | None:
        matches = [
            row
            for row in self.surface_snapshots
            if row["player_id"] == player_id and row["surface_type"] == surface_type
        ]
        return deepcopy(matches[-1]) if matches else None


def _copy_fixture(name: str, tmpdir: Path) -> Path:
    source = ROOT / "fixtures" / name
    target = tmpdir / name
    target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    return target


def main() -> None:
    repository = InMemoryV2Repository()

    with TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        sample_file = _copy_fixture("gg_session_sample.txt", tmpdir)
        real_style_file = _copy_fixture("gg_session_sample_real.txt", tmpdir)

        real_packet = parse_gg_text_file(real_style_file)
        if real_packet.parse_quality.get("parser_mode") != "gg_real":
            raise AssertionError(f"Expected gg_real parser mode, got {real_packet.parse_quality.get('parser_mode')}")
        if real_packet.parse_quality.get("parsed_hands") != 2:
            raise AssertionError("Expected both real-style GG hands to parse")
        if real_packet.hands[0].hero_position != "button":
            raise AssertionError(f"Expected first real-style hand hero position to parse, got {real_packet.hands[0].hero_position}")
        if real_packet.hands[0].effective_stack_bb != 31.25:
            raise AssertionError(
                f"Expected first real-style hand stack in bb to parse, got {real_packet.hands[0].effective_stack_bb}"
            )
        if real_packet.hands[0].players_to_flop != 2:
            raise AssertionError(
                f"Expected first real-style hand players_to_flop to be counted, got {real_packet.hands[0].players_to_flop}"
            )

        result = ingest_gg_file(sample_file, repository, HERO_PLAYER_ID)

        if result.status != "ingested":
            raise AssertionError(f"Expected ingested status, got {result.status}")
        if result.parsed_hand_count <= 0:
            raise AssertionError("Expected parsed hands from sample fixture")
        if result.evidence_count <= 0:
            raise AssertionError("Expected session evidence to be generated")
        if result.memory_count <= 0:
            raise AssertionError("Expected memory items to be generated")

        session_id = result.session_id
        if not session_id:
            raise AssertionError("Expected a session id after ingest")

        today = build_today_surface(repository, HERO_PLAYER_ID, session_id=session_id)
        if today.current_state not in {"stable", "drifting", "contaminated", "volatile_but_acceptable", "unclear"}:
            raise AssertionError(f"Unexpected Today state {today.current_state}")
        if not repository.fetch_latest_surface_snapshot(HERO_PLAYER_ID, "today"):
            raise AssertionError("Today snapshot was not persisted")
        if today.confidence_summary.get("primary_focus") != "Keep the plan simple":
            raise AssertionError("Early Today surface should default to a simple primary focus when no mature action exists")

        command_center = build_command_center_payload(repository, HERO_PLAYER_ID)
        if "today" not in command_center or "top_memory" not in command_center:
            raise AssertionError("Command Center payload missing expected sections")
        if "interpretation_groundwork" not in command_center:
            raise AssertionError("Command Center should expose interpretation groundwork readiness")
        if "interpretation_summary" not in command_center:
            raise AssertionError("Command Center should expose structured interpretation summary")
        if "pattern_progress" not in command_center:
            raise AssertionError("Command Center should expose repeated pattern progress")
        if "review_hooks" not in command_center:
            raise AssertionError("Command Center should expose operator review hooks")
        if command_center["interpretation_groundwork"]["label"] not in {"blocked", "thin", "developing", "strong"}:
            raise AssertionError("Command Center interpretation groundwork should expose a valid readiness label")

        session_lab = build_session_lab_payload(repository, HERO_PLAYER_ID, session_id)
        if session_lab["session"]["id"] != session_id:
            raise AssertionError("Session Lab session id mismatch")
        if session_lab["evidence_summary"]["total_evidence"] <= 0:
            raise AssertionError("Session Lab should expose generated evidence")
        if not session_lab["memory_updates"]:
            raise AssertionError("Session Lab should expose memory updates for the session")
        if "by_direction" not in session_lab["evidence_summary"]:
            raise AssertionError("Session Lab evidence summary should expose evidence directions")
        if "session_story" not in session_lab:
            raise AssertionError("Session Lab should expose a compact session story summary")
        if "interpretation_groundwork" not in session_lab:
            raise AssertionError("Session Lab should expose interpretation groundwork")
        if "review_hooks" not in session_lab:
            raise AssertionError("Session Lab should expose operator review hooks")
        if session_lab["session_story"]["watch_memory_count"] <= 0:
            raise AssertionError("Session Lab should show watch-stage memory counts for early sessions")
        if session_lab["interpretation_groundwork"]["label"] not in {"thin", "developing", "strong"}:
            raise AssertionError("Session Lab groundwork should be readable without being blocked on this sample")

        evidence_rows = repository.fetch_session_evidence(session_id)
        evidence_keys = {(row["evidence_type"], row["entity_key"]) for row in evidence_rows}
        if ("stable_strength_candidate", "reset_and_preservation_discipline") not in evidence_keys:
            raise AssertionError("Expected positive execution discipline evidence from the sample fixture")
        if any(row["evidence_type"] == "contamination_risk_candidate" for row in evidence_rows):
            raise AssertionError("Tiny sample fixture should not emit contamination risk evidence")
        if any(row["evidence_type"] == "field_distortion_candidate" for row in evidence_rows):
            raise AssertionError("Tiny sample fixture should not emit field distortion evidence")

        positive_memory = next(
            item
            for item in session_lab["memory_updates"]
            if item["memory_type"] == "stable_strength_candidate"
            and "reset_and_preservation_discipline" in item["memory_key"]
        )
        if positive_memory["status"] != "watch":
            raise AssertionError(f"Expected one-off positive execution memory to stay watch, got {positive_memory['status']}")
        if positive_memory["suggested_adjustment"] is not None:
            raise AssertionError("Watch-stage memory should not surface a Today adjustment yet")

        repository.create_session_evidence(
            [
                SessionEvidenceRecord(
                    id="evidence-repeat-positive",
                    session_id="session-repeat-positive",
                    evidence_type="stable_strength_candidate",
                    entity_scope="execution",
                    entity_key="reset_and_preservation_discipline",
                    direction="positive",
                    strength_score=0.72,
                    confidence=0.64,
                    sample_size=2,
                    explanation="Repeated reset-and-preservation discipline showed up again in a later session.",
                    source_hand_ids=["session-repeat-positive:1"],
                ),
                SessionEvidenceRecord(
                    id="evidence-repeat-negative",
                    session_id="session-repeat-negative",
                    evidence_type="style_drift_candidate",
                    entity_scope="style",
                    entity_key="passive_blind_compliance",
                    direction="negative",
                    strength_score=0.74,
                    confidence=0.73,
                    sample_size=4,
                    explanation="Passive blind compliance drift repeated in a later session.",
                    source_hand_ids=["session-repeat-negative:1"],
                ),
                SessionEvidenceRecord(
                    id="evidence-repeat-negative-2",
                    session_id="session-repeat-negative-2",
                    evidence_type="style_drift_candidate",
                    entity_scope="style",
                    entity_key="passive_blind_compliance",
                    direction="negative",
                    strength_score=0.78,
                    confidence=0.74,
                    sample_size=4,
                    explanation="Passive blind compliance drift repeated again.",
                    source_hand_ids=["session-repeat-negative-2:1"],
                ),
            ]
        )
        update_memory_from_session_evidence(repository, HERO_PLAYER_ID, "session-repeat-positive")
        update_memory_from_session_evidence(repository, HERO_PLAYER_ID, "session-repeat-negative")
        update_memory_from_session_evidence(repository, HERO_PLAYER_ID, "session-repeat-negative-2")

        repeated_positive = repository.fetch_memory_items(player_id=HERO_PLAYER_ID)
        repeated_positive_lookup = {
            (item["memory_type"], item["memory_key"]): item for item in repeated_positive
        }
        positive_key = positive_memory["memory_key"]
        if repeated_positive_lookup[("stable_strength_candidate", positive_key)]["status"] != "baseline":
            raise AssertionError("Expected repeated positive execution memory to promote to baseline")
        if repeated_positive_lookup[("stable_strength_candidate", positive_key)]["memory_payload"].get("maturity") != "repeated":
            raise AssertionError("Expected repeated positive execution memory to be marked repeated")

        negative_key = "style_drift_candidate:style:passive_blind_compliance"
        if repeated_positive_lookup[("style_drift_candidate", negative_key)]["status"] != "active":
            raise AssertionError("Expected repeated negative drift memory to promote to active")

        repository.create_operator_review(
            OperatorReviewRecord(
                id="review-1",
                target_type="player",
                target_id=HERO_PLAYER_ID,
                review_type="command_center_interpretation_assessment",
                decision="refine",
                notes="Treat contamination as a secondary pressure, not the lead headline.",
                review_payload={
                    "reviewed_headline": "Baseline is holding, but multiway pressure deserves more emphasis than contamination.",
                    "reviewed_priority_labels": ["multiway pressure", "high-engagement profile"],
                },
            )
        )

        memory_graph = build_memory_graph_payload(repository, HERO_PLAYER_ID)
        if memory_graph["summary"]["total_memory_items"] <= 0:
            raise AssertionError("Memory Graph should expose cumulative memory")
        if not memory_graph["status_buckets"]:
            raise AssertionError("Memory Graph status buckets should not be empty")
        if "inspection_summary" not in memory_graph:
            raise AssertionError("Memory Graph should expose inspection summary")
        if "direction_buckets" not in memory_graph or "maturity_buckets" not in memory_graph:
            raise AssertionError("Memory Graph should expose direction and maturity buckets")
        if "interpretation_groundwork" not in memory_graph:
            raise AssertionError("Memory Graph should expose interpretation groundwork readiness")
        if "interpretation_summary" not in memory_graph:
            raise AssertionError("Memory Graph should expose structured interpretation summary")
        if "pattern_progress" not in memory_graph:
            raise AssertionError("Memory Graph should expose repeated pattern progress")
        if "review_hooks" not in memory_graph:
            raise AssertionError("Memory Graph should expose operator review hooks")
        if memory_graph["inspection_summary"]["repeated_or_established_count"] <= 0:
            raise AssertionError("Memory Graph should show repeated or established memory after repeat injections")
        if "negative" not in memory_graph["direction_buckets"]:
            raise AssertionError("Memory Graph should bucket negative memory items separately")
        pattern_cards = memory_graph["pattern_progress"]["pattern_cards"]
        if not pattern_cards:
            raise AssertionError("Pattern progress should surface repeated pattern cards once memory matures")
        passive_blind_card = next(
            (card for card in pattern_cards if card["label"] == "passive blind compliance"),
            None,
        )
        if not passive_blind_card:
            raise AssertionError("Pattern progress should include passive blind compliance once it repeats")
        if passive_blind_card["progress_verdict"] not in {"still_repeating", "improving_window"}:
            raise AssertionError("Repeated leak should surface a concrete progress verdict once it matures")
        if memory_graph["interpretation_groundwork"]["label"] not in {"developing", "strong"}:
            raise AssertionError("Memory Graph groundwork should show cumulative interpretation readiness after repeats")
        if memory_graph["interpretation_summary"]["hero_standard"] is None:
            raise AssertionError("Memory Graph should expose at least one hero standard in the cumulative interpretation summary")
        if session_lab["review_hooks"]["session_evidence"]["canonical_truth_policy"] != "immutable_source_truth_separate_review_overlay":
            raise AssertionError("Review hooks should make canonical truth separation explicit")

        if session_lab["parse_quality"].get("parse_status") != "fixture_fallback":
            raise AssertionError(
                f"Expected simple fixture parse status to stay explicit, got {session_lab['parse_quality'].get('parse_status')}"
            )
        if session_lab["parse_quality"].get("parser_mode") != "simple_fixture_fallback":
            raise AssertionError(
                f"Expected simple fixture parser mode in session lab, got {session_lab['parse_quality'].get('parser_mode')}"
            )

        today_after_repeats = build_today_surface(repository, HERO_PLAYER_ID, session_id=session_id)
        if not today_after_repeats.adjustments:
            raise AssertionError("Expected mature active memory to surface Today adjustments after repeats")
        if today_after_repeats.adjustments[0].label != "Re-anchor blind discipline":
            raise AssertionError("Expected Today to translate repeated active drift into a clearer action label")
        if "automatic blind defense/calls" not in today_after_repeats.adjustments[0].reason:
            raise AssertionError("Expected Today reason to become more specific and action-oriented")
        if today_after_repeats.current_state != "volatile_but_acceptable":
            raise AssertionError(f"Expected mixed baseline + one active risk state, got {today_after_repeats.current_state}")
        if "blind-passivity drift" not in today_after_repeats.headline:
            raise AssertionError("Expected Today headline to identify the main active issue clearly")
        if today_after_repeats.confidence_summary.get("primary_focus") != "Re-anchor blind discipline":
            raise AssertionError("Expected Today primary focus to mirror the top adjustment label")
        if len(today_after_repeats.adjustments) > 2:
            raise AssertionError("Expected Today to stay narrowly focused instead of surfacing too many adjustments")

        command_center_after_review = build_command_center_payload(repository, HERO_PLAYER_ID)
        reviewed_overlay = command_center_after_review["reviewed_overlays"]["command_center_interpretation"]
        if reviewed_overlay is None:
            raise AssertionError("Expected command center to surface the first reviewed overlay")
        if reviewed_overlay["decision"] != "refine":
            raise AssertionError("Expected reviewed overlay to preserve the operator decision")
        if command_center_after_review["review_hooks"]["command_center_interpretation"]["review_count"] != 1:
            raise AssertionError("Expected review hook review_count to reflect stored overlays")

        duplicate_result = ingest_gg_file(sample_file, repository, HERO_PLAYER_ID)
        if duplicate_result.status != "duplicate_skipped":
            raise AssertionError("Expected duplicate fixture ingest to be skipped")

        empty_file = _copy_fixture("gg_session_empty.txt", tmpdir)
        empty_result = ingest_gg_file(empty_file, repository, HERO_PLAYER_ID)
        if empty_result.status != "failed_zero_hands":
            raise AssertionError("Expected zero-hand fixture to fail safely")

    print("V2 smoke tests passed.")


if __name__ == "__main__":
    main()
