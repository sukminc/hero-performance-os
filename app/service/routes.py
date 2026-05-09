from __future__ import annotations

from pathlib import Path
from typing import Any

from app.api.hand_matrix import get_hand_matrix_payload
from app.api.matrix_quiz import build_matrix_quiz_payload
from app.api.today import get_today_payload
from core.ingest.file_ingest import ingest_gg_file
from core.storage.repositories import V2Repository


def build_health_payload() -> dict[str, Any]:
    return {
        "ok": True,
        "service": "opb-backend",
        "boundary": "python-service",
    }


def build_today_service_payload(
    player_id: str,
    rebuild: bool = False,
    repository: Any | None = None,
) -> dict[str, Any]:
    payload = get_today_payload(player_id=player_id, rebuild=rebuild, repository=repository)
    return {
        "ok": True,
        "surface": "today",
        "player_id": player_id,
        "data": payload,
    }


def build_matrix_service_payload(
    player_id: str,
    selected_hand: str | None = None,
    window: str = "all",
    observations: list[Any] | None = None,
) -> dict[str, Any]:
    payload = get_hand_matrix_payload(
        player_id=player_id,
        window=window,
        selected_hand=selected_hand,
        observations=observations,
    )
    return {
        "ok": True,
        "surface": "matrix",
        "player_id": player_id,
        "data": payload,
    }


def build_matrix_quiz_service_payload(
    player_id: str,
    quiz_date: str | None = None,
    matrix_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = build_matrix_quiz_payload(
        player_id=player_id,
        quiz_date=quiz_date,
        matrix_payload=matrix_payload,
    )
    return {
        "ok": True,
        "surface": "matrix_quiz",
        "player_id": player_id,
        "date": payload.get("date"),
        "data": payload,
    }


def _serialize_ingest_result(result: Any, source_name: str, uploaded_name: str) -> dict[str, Any]:
    return {
        "sourceName": source_name,
        "uploadedName": uploaded_name,
        "status": result.status,
        "ingest_file_id": result.ingest_file_id,
        "session_id": result.session_id,
        "duplicate_of_file_id": result.duplicate_of_file_id,
        "duplicate_of_status": result.duplicate_of_status,
        "parsed_hand_count": result.parsed_hand_count,
        "evidence_count": result.evidence_count,
        "memory_count": result.memory_count,
    }


def build_upload_service_payload(
    player_id: str,
    packet_paths: list[dict[str, str]],
    source_file_count: int,
    repository: Any | None = None,
) -> dict[str, Any]:
    repository = repository or V2Repository()
    results: list[dict[str, Any]] = []

    for item in packet_paths:
        packet_path = Path(item["packet_path"])
        source_name = item["source_name"]
        try:
            result = ingest_gg_file(packet_path, repository, player_id)
            results.append(_serialize_ingest_result(result, source_name, packet_path.name))
        except Exception as exc:  # pragma: no cover - defensive service boundary
            results.append(
                {
                    "sourceName": source_name,
                    "uploadedName": packet_path.name,
                    "status": f"failed: {exc}",
                    "ingest_file_id": "",
                    "session_id": None,
                    "duplicate_of_file_id": None,
                    "duplicate_of_status": None,
                    "parsed_hand_count": 0,
                    "evidence_count": 0,
                    "memory_count": 0,
                }
            )

    ingested_count = sum(1 for item in results if item["status"] == "ingested")
    duplicate_count = sum(1 for item in results if item["status"] == "duplicate_skipped")
    duplicate_ingested_count = sum(
        1
        for item in results
        if item["status"] == "duplicate_skipped" and item.get("duplicate_of_status") == "ingested"
    )
    duplicate_summary_only_count = sum(
        1
        for item in results
        if item["status"] == "duplicate_skipped" and item.get("duplicate_of_status") == "skipped_summary_only"
    )
    summary_only_count = sum(1 for item in results if item["status"] == "skipped_summary_only")
    failed_count = sum(1 for item in results if str(item["status"]).startswith("failed"))

    return {
        "ok": failed_count == 0,
        "message": (
            "Some files failed during upload. Review the batch results below."
            if failed_count
            else (
                f"Batch processed successfully. {ingested_count} new packets ingested, "
                f"{duplicate_count} duplicates skipped ({duplicate_ingested_count} hand-packet duplicates, "
                f"{duplicate_summary_only_count} summary-only duplicates), "
                f"{summary_only_count} summary-only files skipped."
            )
        ),
        "summary": {
            "sourceFileCount": source_file_count,
            "extractedPacketCount": len(packet_paths),
            "ingestedCount": ingested_count,
            "duplicateCount": duplicate_count,
            "duplicateIngestedCount": duplicate_ingested_count,
            "duplicateSummaryOnlyCount": duplicate_summary_only_count,
            "summaryOnlyCount": summary_only_count,
            "failedCount": failed_count,
        },
        "results": results,
    }
