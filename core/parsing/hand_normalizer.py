from __future__ import annotations

from core.parsing.gg_parser import ParsedSessionPacket
from core.storage.models import HandRecord


def normalize_hands(session_id: str, parsed_packet: ParsedSessionPacket) -> list[HandRecord]:
    normalized: list[HandRecord] = []
    for hand in parsed_packet.hands:
        header_meta = hand.header_metadata
        normalized.append(
            HandRecord(
                id=hand.hand_id,
                session_id=session_id,
                hand_external_id=str(header_meta.get("hand_ref") or hand.hand_id),
                tournament_id=str(header_meta.get("tournament_id")) if header_meta.get("tournament_id") else None,
                hero_position=hand.hero_position,
                effective_stack_bb=hand.effective_stack_bb,
                phase_proxy=f"level_{header_meta.get('level')}" if header_meta.get("level") else None,
                bounty_proxy=None,
                players_to_flop=hand.players_to_flop,
                board_texture_summary=hand.board_texture_summary,
                result_summary=hand.result_summary,
                header_metadata=header_meta,
                raw_payload=hand.raw_payload,
            )
        )
    return normalized

