from __future__ import annotations

from core.parsing.gg_parser import ParsedSessionPacket
from core.parsing.parse_quality import build_confidence_summary, build_parse_status
from core.storage.models import SessionRecord


def build_session_record(player_id: str, ingest_file_id: str, session_id: str, parsed_packet: ParsedSessionPacket) -> SessionRecord:
    metadata = parsed_packet.metadata
    confidence_summary = build_confidence_summary(parsed_packet.parse_quality)
    return SessionRecord(
        id=session_id,
        player_id=player_id,
        ingest_file_id=ingest_file_id,
        session_key=parsed_packet.session_key,
        site="gg",
        parse_status=build_parse_status(parsed_packet.parse_quality),
        hand_count=len(parsed_packet.hands),
        started_at=metadata.get("date"),
        ended_at=metadata.get("date"),
        buyin_band=metadata.get("stakes"),
        currency="USD",
        confidence_summary=confidence_summary,
        session_metadata=metadata,
    )

