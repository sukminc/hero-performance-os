#!/usr/bin/env python3
from __future__ import annotations

from email import policy
from email.parser import BytesParser
import json
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import re
from uuid import uuid4
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse
from zipfile import ZipFile

from app.service.routes import (
    build_health_payload,
    build_matrix_quiz_service_payload,
    build_matrix_service_payload,
    build_today_service_payload,
    build_upload_service_payload,
)


def _json_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, default=str).encode("utf-8")


def _truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def _safe_upload_name(filename: str) -> str:
    name = Path(filename or "upload.txt").name
    return re.sub(r"[^a-zA-Z0-9._-]", "_", name) or "upload.txt"


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

    def _read_multipart_files(self) -> list[dict[str, Any]]:
        content_type = self.headers.get("Content-Type", "")
        if "multipart/form-data" not in content_type:
            raise ValueError("expected multipart/form-data")

        content_length = int(self.headers.get("Content-Length", "0") or "0")
        max_bytes = int(os.getenv("OPB_UPLOAD_MAX_BYTES", str(50 * 1024 * 1024)))
        if content_length <= 0:
            raise ValueError("empty upload body")
        if content_length > max_bytes:
            raise ValueError("upload body is too large")

        body = self.rfile.read(content_length)
        message_bytes = (
            f"Content-Type: {content_type}\r\nMIME-Version: 1.0\r\n\r\n".encode("utf-8") + body
        )
        message = BytesParser(policy=policy.default).parsebytes(message_bytes)

        files: list[dict[str, Any]] = []
        for part in message.iter_parts():
            if part.get_content_disposition() != "form-data":
                continue
            if part.get_param("name", header="content-disposition") != "packet":
                continue
            filename = part.get_filename()
            payload = part.get_payload(decode=True) or b""
            if not filename or not payload:
                continue
            files.append({"filename": _safe_upload_name(filename), "bytes": payload})
        return files

    def _save_upload_packets(self, files: list[dict[str, Any]]) -> list[dict[str, str]]:
        upload_root = Path(os.getenv("OPB_UPLOAD_TMP_DIR", "/tmp/opb_uploads")).expanduser()
        upload_root.mkdir(parents=True, exist_ok=True)

        packet_paths: list[dict[str, str]] = []
        for uploaded in files:
            filename = uploaded["filename"]
            destination = upload_root / f"{uuid4()}-{filename}"
            destination.write_bytes(uploaded["bytes"])

            if filename.lower().endswith(".zip"):
                expand_dir = upload_root / "expanded" / str(uuid4())
                expand_dir.mkdir(parents=True, exist_ok=True)
                with ZipFile(destination) as archive:
                    for member in archive.infolist():
                        if member.is_dir():
                            continue
                        member_name = _safe_upload_name(member.filename)
                        if not member_name.lower().endswith(".txt"):
                            continue
                        extracted = expand_dir / member_name
                        counter = 1
                        while extracted.exists():
                            stem = extracted.stem
                            extracted = expand_dir / f"{stem}-{counter}{extracted.suffix}"
                            counter += 1
                        extracted.write_bytes(archive.read(member))
                        packet_paths.append({"packet_path": str(extracted), "source_name": filename})
            elif filename.lower().endswith(".txt"):
                packet_paths.append({"packet_path": str(destination), "source_name": filename})

        return packet_paths

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

    def do_POST(self) -> None:
        parsed = urlparse(self.path)

        if not self._is_authorized():
            self._send_json(HTTPStatus.UNAUTHORIZED, {"ok": False, "error": "unauthorized"})
            return

        parts = [unquote(part) for part in parsed.path.split("/") if part]
        if len(parts) == 4 and parts[:2] == ["v1", "players"] and parts[3] == "uploads":
            player_id = parts[2].strip()
            if not player_id:
                self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": "missing_player_id"})
                return
            try:
                uploaded_files = self._read_multipart_files()
                if not uploaded_files:
                    self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "message": "No GG packet files were attached."})
                    return
                packet_paths = self._save_upload_packets(uploaded_files)
                if not packet_paths:
                    self._send_json(
                        HTTPStatus.BAD_REQUEST,
                        {"ok": False, "message": "No .txt GG packets were found in the upload."},
                    )
                    return
                payload = build_upload_service_payload(
                    player_id=player_id,
                    packet_paths=packet_paths,
                    source_file_count=len(uploaded_files),
                )
                self._send_json(HTTPStatus.OK, payload)
                return
            except Exception as exc:
                self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "message": str(exc)})
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
