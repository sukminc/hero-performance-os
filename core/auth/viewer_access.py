from __future__ import annotations

import os
from typing import Any
from uuid import uuid4

from core.storage.models import UserAccountRecord, UserGlobalRoleRecord, UserPlayerAccessRecord
from core.storage.repositories import V2Repository

HERO_PLAYER_ID = "4c9d1e29-1f6b-4e5f-92da-111111111111"


def _normalize_email(value: str | None) -> str | None:
    if not value:
        return None
    normalized = value.strip().lower()
    return normalized or None


def _parse_csv_env(value: str | None) -> set[str]:
    return {item.strip().lower() for item in (value or "").split(",") if item.strip()}


def bootstrap_identity_access_from_env(repo: V2Repository) -> dict[str, Any]:
    hero_user_id = (os.getenv("OPB_HERO_SUPABASE_USER_ID") or "").strip()
    hero_email = _normalize_email(os.getenv("OPB_HERO_SUPABASE_EMAIL"))
    operator_user_ids = _parse_csv_env(os.getenv("OPB_OPERATOR_SUPABASE_USER_IDS"))
    operator_emails = _parse_csv_env(os.getenv("OPB_OPERATOR_EMAILS"))

    seeded_accounts = 0
    seeded_access_rows = 0
    seeded_roles = 0

    def ensure_account(provider_user_id: str, email: str | None) -> dict[str, Any]:
        nonlocal seeded_accounts
        existing = repo.get_user_account_by_provider_identity("supabase", provider_user_id)
        record_id = existing["id"] if existing else str(uuid4())
        repo.upsert_user_account(
            UserAccountRecord(
                id=record_id,
                auth_provider="supabase",
                auth_provider_user_id=provider_user_id,
                email=email,
                account_metadata={"bootstrap_source": "env_mapping"},
            )
        )
        if not existing:
            seeded_accounts += 1
        return repo.get_user_account_by_provider_identity("supabase", provider_user_id) or {"id": record_id}

    hero_account: dict[str, Any] | None = None
    if hero_user_id:
        hero_account = ensure_account(hero_user_id, hero_email)
    elif hero_email:
        existing = repo.get_user_account_by_email(hero_email)
        hero_account = existing

    if hero_account:
        repo.upsert_user_player_access(
            UserPlayerAccessRecord(
                id=str(uuid4()),
                user_account_id=hero_account["id"],
                player_id=HERO_PLAYER_ID,
                access_role="owner",
                granted_by_user_account_id=hero_account["id"],
                granted_reason="bootstrap_hero_env_mapping",
                access_metadata={"bootstrap_source": "env_mapping"},
            )
        )
        seeded_access_rows += 1

    for operator_user_id in operator_user_ids:
        operator_account = ensure_account(operator_user_id, None)
        repo.upsert_user_global_role(
            UserGlobalRoleRecord(
                id=str(uuid4()),
                user_account_id=operator_account["id"],
                role="operator_admin",
                granted_by_user_account_id=hero_account["id"] if hero_account else None,
                role_metadata={"bootstrap_source": "env_mapping"},
            )
        )
        repo.upsert_user_player_access(
            UserPlayerAccessRecord(
                id=str(uuid4()),
                user_account_id=operator_account["id"],
                player_id=HERO_PLAYER_ID,
                access_role="operator",
                granted_by_user_account_id=hero_account["id"] if hero_account else None,
                granted_reason="bootstrap_operator_env_mapping",
                access_metadata={"bootstrap_source": "env_mapping"},
            )
        )
        seeded_roles += 1
        seeded_access_rows += 1

    for operator_email in operator_emails:
        existing = repo.get_user_account_by_email(operator_email)
        if not existing:
            continue
        repo.upsert_user_global_role(
            UserGlobalRoleRecord(
                id=str(uuid4()),
                user_account_id=existing["id"],
                role="operator_admin",
                granted_by_user_account_id=hero_account["id"] if hero_account else None,
                role_metadata={"bootstrap_source": "env_mapping"},
            )
        )
        repo.upsert_user_player_access(
            UserPlayerAccessRecord(
                id=str(uuid4()),
                user_account_id=existing["id"],
                player_id=HERO_PLAYER_ID,
                access_role="operator",
                granted_by_user_account_id=hero_account["id"] if hero_account else None,
                granted_reason="bootstrap_operator_env_mapping",
                access_metadata={"bootstrap_source": "env_mapping"},
            )
        )
        seeded_roles += 1
        seeded_access_rows += 1

    return {
        "seeded_accounts": seeded_accounts,
        "seeded_access_rows": seeded_access_rows,
        "seeded_roles": seeded_roles,
    }


def bootstrap_authenticated_user_from_env_mapping(
    repo: V2Repository, auth_provider: str, auth_provider_user_id: str | None, email: str | None
) -> None:
    if not auth_provider_user_id and not email:
        return

    normalized_email = _normalize_email(email)
    hero_user_id = (os.getenv("OPB_HERO_SUPABASE_USER_ID") or "").strip().lower()
    hero_email = _normalize_email(os.getenv("OPB_HERO_SUPABASE_EMAIL"))
    operator_user_ids = _parse_csv_env(os.getenv("OPB_OPERATOR_SUPABASE_USER_IDS"))
    operator_emails = _parse_csv_env(os.getenv("OPB_OPERATOR_EMAILS"))
    normalized_user_id = (auth_provider_user_id or "").strip().lower()

    existing = None
    if auth_provider_user_id:
        existing = repo.get_user_account_by_provider_identity(auth_provider, auth_provider_user_id)
    if not existing and normalized_email:
        existing = repo.get_user_account_by_email(normalized_email)

    account_id = existing["id"] if existing else str(uuid4())
    repo.upsert_user_account(
        UserAccountRecord(
            id=account_id,
            auth_provider=auth_provider,
            auth_provider_user_id=auth_provider_user_id or f"email:{normalized_email}",
            email=normalized_email,
            account_metadata={"bootstrap_source": "authenticated_env_mapping"},
        )
    )

    user_account = repo.get_user_account_by_provider_identity(auth_provider, auth_provider_user_id or f"email:{normalized_email}")
    if not user_account:
        return

    is_hero = (normalized_user_id and normalized_user_id == hero_user_id) or (
        normalized_email and normalized_email == hero_email
    )
    is_operator = (normalized_user_id and normalized_user_id in operator_user_ids) or (
        normalized_email and normalized_email in operator_emails
    )

    if is_hero:
        repo.upsert_user_player_access(
            UserPlayerAccessRecord(
                id=str(uuid4()),
                user_account_id=user_account["id"],
                player_id=HERO_PLAYER_ID,
                access_role="owner",
                granted_by_user_account_id=user_account["id"],
                granted_reason="authenticated_env_mapping_hero",
                access_metadata={"bootstrap_source": "authenticated_env_mapping"},
            )
        )

    if is_operator:
        repo.upsert_user_global_role(
            UserGlobalRoleRecord(
                id=str(uuid4()),
                user_account_id=user_account["id"],
                role="operator_admin",
                granted_by_user_account_id=user_account["id"],
                role_metadata={"bootstrap_source": "authenticated_env_mapping"},
            )
        )
        repo.upsert_user_player_access(
            UserPlayerAccessRecord(
                id=str(uuid4()),
                user_account_id=user_account["id"],
                player_id=HERO_PLAYER_ID,
                access_role="operator",
                granted_by_user_account_id=user_account["id"],
                granted_reason="authenticated_env_mapping_operator",
                access_metadata={"bootstrap_source": "authenticated_env_mapping"},
            )
        )


def resolve_viewer_access(
    auth_provider: str, auth_provider_user_id: str | None, email: str | None
) -> dict[str, Any]:
    repo = V2Repository()
    repo.ensure_schema()
    bootstrap_identity_access_from_env(repo)
    bootstrap_authenticated_user_from_env_mapping(repo, auth_provider, auth_provider_user_id, email)

    normalized_email = _normalize_email(email)
    account = None
    source = "canonical_none"

    if auth_provider_user_id:
        account = repo.get_user_account_by_provider_identity(auth_provider, auth_provider_user_id)
        if account:
            source = "canonical_provider_identity"

    if not account and normalized_email:
        account = repo.get_user_account_by_email(normalized_email)
        if account:
            source = "canonical_email"

    if not account:
        return {
            "resolved": False,
            "source": source,
            "user_account_id": None,
            "player_id": None,
            "player_scope": "none",
            "role": "user",
            "can_see_operator_depth": False,
            "ownership_resolved": False,
            "ownership_source": "unmapped_user",
        }

    access_rows = repo.fetch_active_user_player_access(account["id"])
    global_roles = repo.fetch_active_user_global_roles(account["id"])
    has_operator_role = any(role.get("role") == "operator_admin" for role in global_roles)
    owner_access = next((row for row in access_rows if row.get("access_role") == "owner"), None)
    operator_access = next((row for row in access_rows if row.get("access_role") == "operator"), None)

    if has_operator_role and operator_access:
        return {
            "resolved": True,
            "source": source,
            "user_account_id": account["id"],
            "player_id": operator_access.get("player_id"),
            "player_scope": "all",
            "role": "operator",
            "can_see_operator_depth": True,
            "ownership_resolved": True,
            "ownership_source": "canonical_operator_access",
        }

    if owner_access:
        return {
            "resolved": True,
            "source": source,
            "user_account_id": account["id"],
            "player_id": owner_access.get("player_id"),
            "player_scope": "self",
            "role": "user",
            "can_see_operator_depth": False,
            "ownership_resolved": True,
            "ownership_source": "canonical_owner_access",
        }

    return {
        "resolved": True,
        "source": source,
        "user_account_id": account["id"],
        "player_id": None,
        "player_scope": "none",
        "role": "user",
        "can_see_operator_depth": has_operator_role,
        "ownership_resolved": False,
        "ownership_source": "canonical_account_unscoped",
    }
