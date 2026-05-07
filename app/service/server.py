#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

from app.service.routes import (
    build_health_payload,
    build_matrix_quiz_service_payload,
    build_matrix_service_payload,
    build_today_service_payload,
)


def _json_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, default=str).encode("utf-8")


def _truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


class OPBServiceHandler(BaseHTTPRequestHandler):
    server_version = "OPBBackend/0.1"

    def log_message(self, format: str, *args: Any) -> None:
        if _truthy(os.getenv("OPB_BACKEND_VERBOSE_LOGS")):
            super().log_message(format, *args)

    def _send_json(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
        body = _json_bytes(payload)
        self.send_response(status.value)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _is_authorized(self) -> bool:
        token = os.getenv("OPB_BACKEND_API_TOKEN", "").strip()
        if not token:
            return True
        return self.headers.get("Authorization", "") == f"Bearer {token}"

    def do_GET(self) -> None:
        parsed = urlparse(self.path)

        if parsed.path == "/health":
            self._send_json(HTTPStatus.OK, build_health_payload())
            return

        if not self._is_authorized():
            self._send_json(HTTPStatus.UNAUTHORIZED, {"ok": False, "error": "unauthorized"})
            return

        parts = [unquote(part) for part in parsed.path.split("/") if part]
        query = parse_qs(parsed.query)

        if len(parts) == 4 and parts[:2] == ["v1", "players"] and parts[3] == "today":
            player_id = parts[2].strip()
            if not player_id:
                self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": "missing_player_id"})
                return
            payload = build_today_service_payload(player_id=player_id, rebuild=_truthy(query.get("rebuild", ["0"])[0]))
            self._send_json(HTTPStatus.OK, payload)
            return

        if len(parts) == 4 and parts[:2] == ["v1", "players"] and parts[3] == "matrix":
            player_id = parts[2].strip()
            if not player_id:
                self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": "missing_player_id"})
                return
            payload = build_matrix_service_payload(
                player_id=player_id,
                selected_hand=query.get("selected_hand", [None])[0],
                window=query.get("window", ["all"])[0],
            )
            self._send_json(HTTPStatus.OK, payload)
            return

        if len(parts) == 5 and parts[:2] == ["v1", "players"] and parts[3:] == ["matrix", "quiz"]:
            player_id = parts[2].strip()
            if not player_id:
                self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": "missing_player_id"})
                return
            payload = build_matrix_quiz_service_payload(
                player_id=player_id,
                quiz_date=query.get("date", [None])[0],
            )
            self._send_json(HTTPStatus.OK, payload)
            return

        self._send_json(HTTPStatus.NOT_FOUND, {"ok": False, "error": "not_found"})


def main() -> None:
    host = os.getenv("OPB_BACKEND_HOST", "127.0.0.1")
    port = int(os.getenv("OPB_BACKEND_PORT", "8765"))
    server = ThreadingHTTPServer((host, port), OPBServiceHandler)
    print(f"OPB backend service listening on http://{host}:{port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
