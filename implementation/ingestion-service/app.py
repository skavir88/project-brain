"""Local-only synthetic ingestion and structural-validation service for Stage 1."""

from __future__ import annotations

import json
import os
from hashlib import sha256
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Lock


seen_fingerprints: set[str] = set()
fingerprint_lock = Lock()


class IngestionHandler(BaseHTTPRequestHandler):
    """Expose a no-persistence synthetic-record validation slice."""

    server_version = "EnterpriseAIIngestion/0.1"

    def send_json(self, status: HTTPStatus, payload: dict[str, object]) -> None:
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        if self.path != "/health":
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        self.send_json(
            HTTPStatus.OK,
            {"service": "enterprise-ai-ingestion", "status": "ok"},
        )

    def do_POST(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        if self.path != "/v1/records":
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        try:
            length = int(self.headers.get("Content-Length", ""))
            raw_record = self.rfile.read(length)
            record = json.loads(raw_record)
        except (ValueError, json.JSONDecodeError):
            self.send_json(
                HTTPStatus.BAD_REQUEST,
                {"accepted": False, "error": "invalid_json"},
            )
            return

        errors = validate_record(record)
        if errors:
            self.send_json(
                HTTPStatus.UNPROCESSABLE_ENTITY,
                {"accepted": False, "validation_errors": errors},
            )
            return

        canonical_record = canonicalize_record(record)
        fingerprint = fingerprint_record(canonical_record)
        with fingerprint_lock:
            if fingerprint in seen_fingerprints:
                self.send_json(
                    HTTPStatus.CONFLICT,
                    {
                        "accepted": False,
                        "duplicate": True,
                        "fingerprint": fingerprint,
                    },
                )
                return
            seen_fingerprints.add(fingerprint)

        self.send_json(
            HTTPStatus.ACCEPTED,
            {
                "accepted": True,
                "duplicate": False,
                "validation_errors": [],
                "canonical_record": canonical_record,
                "fingerprint": fingerprint,
            },
        )

    def log_message(self, format: str, *args: object) -> None:
        """Avoid writing request paths or client information into default test output."""


def validate_record(record: object) -> list[dict[str, str]]:
    """Validate only the minimal synthetic contract; no record is retained."""

    if not isinstance(record, dict):
        return [{"field": "record", "code": "must_be_object"}]

    errors: list[dict[str, str]] = []
    for field in ("source_id", "record_id"):
        value = record.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append({"field": field, "code": "must_be_non_empty_string"})

    if not isinstance(record.get("payload"), dict):
        errors.append({"field": "payload", "code": "must_be_object"})

    return errors


def canonicalize_record(record: object) -> dict[str, object]:
    """Return a deterministic identifier-normalized copy without retaining it."""

    assert isinstance(record, dict)
    canonical_record = dict(record)
    canonical_record["source_id"] = record["source_id"].strip()
    canonical_record["record_id"] = record["record_id"].strip()
    return canonical_record


def fingerprint_record(record: dict[str, object]) -> str:
    """Hash stable JSON for later deduplication work without storing state."""

    canonical_json = json.dumps(record, sort_keys=True, separators=(",", ":"))
    return sha256(canonical_json.encode("utf-8")).hexdigest()


def main() -> None:
    host = os.environ.get("INGESTION_HOST", "127.0.0.1")
    port = int(os.environ.get("INGESTION_PORT", "8080"))
    ThreadingHTTPServer((host, port), IngestionHandler).serve_forever()


if __name__ == "__main__":
    main()
