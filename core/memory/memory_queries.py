from __future__ import annotations


def build_memory_key(evidence_type: str, entity_scope: str, entity_key: str) -> str:
    return f"{evidence_type}:{entity_scope}:{entity_key}"

