#!/usr/bin/env python3
"""Thin local UI shell for V2 Hero Performance OS."""

from __future__ import annotations

import argparse
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from app.api.command_center import get_command_center_payload
from app.api.conviction_review import get_conviction_review_payload
from app.api.field_ecology import get_field_ecology_payload
from app.api.hand_matrix import get_hand_matrix_payload
from app.api.hud_trend import get_hud_trend_payload
from app.api.memory_graph import get_memory_graph_payload
from app.api.review_operator import get_review_operator_payload
from app.api.session_lab import get_session_lab_payload
from app.api.timing_stack_review import get_timing_stack_review_payload
from app.api.today import get_today_payload


APP_ROOT = Path(__file__).resolve().parent
UI_ROOT = APP_ROOT / "ui"


class V2UIShellHandler(BaseHTTPRequestHandler):
    def _send_json(self, payload: dict, status: int = HTTPStatus.OK) -> None:
        body = json.dumps(payload, indent=2, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path: Path, content_type: str) -> None:
        body = path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        route = parsed.path
        query = parse_qs(parsed.query)

        try:
            if route in {"/", "/index.html"}:
                return self._send_file(UI_ROOT / "index.html", "text/html; charset=utf-8")
            if route == "/styles.css":
                return self._send_file(UI_ROOT / "styles.css", "text/css; charset=utf-8")
            if route == "/main.js":
                return self._send_file(UI_ROOT / "main.js", "application/javascript; charset=utf-8")
            if route == "/api/today":
                payload = get_today_payload(
                    player_id=query.get("player_id", [None])[0] or None,
                    rebuild=_truthy(query.get("rebuild", ["false"])[0]),
                )
                return self._send_json(payload)
            if route == "/api/command-center":
                payload = get_command_center_payload(
                    player_id=query.get("player_id", [None])[0] or None,
                    rebuild_today=_truthy(query.get("rebuild_today", ["false"])[0]),
                )
                return self._send_json(payload)
            if route == "/api/session-lab":
                payload = get_session_lab_payload(
                    player_id=query.get("player_id", [None])[0] or None,
                    session_id=query.get("session_id", [None])[0],
                )
                return self._send_json(payload)
            if route == "/api/memory-graph":
                payload = get_memory_graph_payload(
                    player_id=query.get("player_id", [None])[0] or None,
                )
                return self._send_json(payload)
            if route == "/api/hand-matrix":
                payload = get_hand_matrix_payload(
                    player_id=query.get("player_id", [None])[0] or None,
                    window=query.get("window", ["90d"])[0],
                    format_filter=query.get("format_filter", ["all"])[0],
                    position_filter=query.get("position_filter", ["all"])[0],
                    stack_filter=query.get("stack_filter", ["all"])[0],
                    min_active_seats=int(query.get("min_active_seats", ["5"])[0]),
                    selected_hand=query.get("selected_hand", [None])[0],
                )
                return self._send_json(payload)
            if route == "/api/hud-trend":
                payload = get_hud_trend_payload(
                    player_id=query.get("player_id", [None])[0] or None,
                    window=query.get("window", ["90d"])[0],
                )
                return self._send_json(payload)
            if route == "/api/field-ecology":
                payload = get_field_ecology_payload(
                    player_id=query.get("player_id", [None])[0] or None,
                    window=query.get("window", ["90d"])[0],
                )
                return self._send_json(payload)
            if route == "/api/review-operator":
                payload = get_review_operator_payload(
                    player_id=query.get("player_id", [None])[0] or None,
                    window=query.get("window", ["90d"])[0],
                )
                return self._send_json(payload)
            if route == "/api/conviction-review":
                payload = get_conviction_review_payload(
                    player_id=query.get("player_id", [None])[0] or None,
                    window=query.get("window", ["all"])[0],
                )
                return self._send_json(payload)
            if route == "/api/timing-stack-review":
                payload = get_timing_stack_review_payload(
                    player_id=query.get("player_id", [None])[0] or None,
                    window=query.get("window", ["all"])[0],
                )
                return self._send_json(payload)
        except FileNotFoundError as exc:
            return self._send_json({"status": "error", "message": str(exc)}, status=HTTPStatus.NOT_FOUND)
        except Exception as exc:  # pragma: no cover - thin dev shell safety
            return self._send_json({"status": "error", "message": str(exc)}, status=HTTPStatus.INTERNAL_SERVER_ERROR)

        self._send_json({"status": "error", "message": f"Unknown route: {route}"}, status=HTTPStatus.NOT_FOUND)

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return


def _truthy(raw: str) -> bool:
    return raw.lower() in {"1", "true", "yes", "on"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the thin V2 local UI shell.")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind.")
    parser.add_argument("--port", type=int, default=8765, help="Port to bind.")
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), V2UIShellHandler)
    print(f"V2 UI shell running at http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
