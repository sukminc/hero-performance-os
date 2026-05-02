from __future__ import annotations

import re
from typing import Any
from uuid import uuid4

from core.storage.models import DemoApplicationRecord, UserAccountRecord, UserPlayerAccessRecord
from core.storage.repositories import V2Repository

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
ALLOWED_STATUSES = {"new", "screening", "approved", "rejected", "provisioned"}


def _clean(value: str | None, limit: int) -> str:
    return (value or "").strip()[:limit]


def submit_demo_application(name: str, email: str, games: str, help_goal: str, source: str = "public_demo_apply") -> dict[str, Any]:
    cleaned_name = _clean(name, 120)
    cleaned_email = _clean(email, 180).lower()
    cleaned_games = _clean(games, 240)
    cleaned_help_goal = _clean(help_goal, 1000)

    if not cleaned_name or not cleaned_email or not cleaned_games or not cleaned_help_goal:
        return {"ok": False, "message": "Please complete every field before requesting demo access."}
    if not EMAIL_RE.match(cleaned_email):
        return {"ok": False, "message": "Please use a valid email address."}

    repo = V2Repository()
    repo.ensure_schema()
    application_id = f"demo-{uuid4()}"
    repo.create_demo_application(
        DemoApplicationRecord(
            id=application_id,
            name=cleaned_name,
            email=cleaned_email,
            games=cleaned_games,
            help_goal=cleaned_help_goal,
            source=source,
            application_metadata={
                "recruiting_boundary": "gg_poker_ontario_online_mtt",
                "provisioning_handoff": "operator_approve_then_create_user_player_access",
            },
        )
    )

    return {
        "ok": True,
        "message": "Application received. Approved users will be provisioned into a player ownership record before any private data is shown.",
        "application_id": application_id,
        "status": "new",
    }


def list_demo_applications(status: str | None = None, limit: int = 25) -> dict[str, Any]:
    repo = V2Repository()
    repo.ensure_schema()
    rows = repo.fetch_demo_applications(status=status if status in ALLOWED_STATUSES else None, limit=limit)
    return {"ok": True, "applications": rows}


def update_demo_application_status(application_id: str, status: str) -> dict[str, Any]:
    if status not in ALLOWED_STATUSES:
        return {"ok": False, "message": f"Unsupported application status: {status}"}

    repo = V2Repository()
    repo.ensure_schema()
    application = repo.get_demo_application(application_id)
    if not application:
        return {"ok": False, "message": "Demo application not found."}

    metadata = application.get("application_metadata") or {}
    history = list(metadata.get("status_history") or [])
    history.append({"from": application.get("status"), "to": status})
    metadata["status_history"] = history
    repo.update_demo_application_status(application_id, status, metadata)
    return {"ok": True, "message": f"Application moved to {status}.", "application_id": application_id, "status": status}


def provision_demo_application_owner(application_id: str, player_id: str, auth_provider: str = "supabase") -> dict[str, Any]:
    cleaned_player_id = _clean(player_id, 180)
    if not cleaned_player_id:
        return {"ok": False, "message": "A target player id is required before provisioning access."}

    repo = V2Repository()
    repo.ensure_schema()
    application = repo.get_demo_application(application_id)
    if not application:
        return {"ok": False, "message": "Demo application not found."}
    if application.get("status") != "approved":
        return {"ok": False, "message": "Only approved applications can be provisioned."}

    email = _clean(str(application.get("email") or ""), 180).lower()
    account = repo.get_user_account_by_email(email)
    account_id = account["id"] if account else str(uuid4())
    provider_user_id = account.get("auth_provider_user_id") if account else f"email:{email}"

    repo.upsert_user_account(
        UserAccountRecord(
            id=account_id,
            auth_provider=auth_provider,
            auth_provider_user_id=provider_user_id,
            email=email,
            account_metadata={"source": "demo_application", "demo_application_id": application_id},
        )
    )
    account = repo.get_user_account_by_email(email) or {"id": account_id}
    repo.upsert_user_player_access(
        UserPlayerAccessRecord(
            id=str(uuid4()),
            user_account_id=account["id"],
            player_id=cleaned_player_id,
            access_role="owner",
            granted_by_user_account_id=None,
            granted_reason="approved_demo_application",
            access_metadata={"demo_application_id": application_id},
        )
    )

    metadata = application.get("application_metadata") or {}
    metadata["provisioned_player_id"] = cleaned_player_id
    metadata["provisioned_user_account_id"] = account["id"]
    repo.update_demo_application_status(application_id, "provisioned", metadata)
    return {
        "ok": True,
        "message": "Application provisioned into owner access.",
        "application_id": application_id,
        "player_id": cleaned_player_id,
        "user_account_id": account["id"],
    }
