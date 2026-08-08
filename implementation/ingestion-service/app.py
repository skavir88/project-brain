"""Minimal local-only ingestion service skeleton for Enterprise AI Stage 1."""

from __future__ import annotations

import json
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class HealthHandler(BaseHTTPRequestHandler):
    """Expose only a non-sensitive liveness response for the initial vertical slice."""

    server_version = "EnterpriseAIIngestion/0.1"

    def do_GET(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        if self.path != "/health":
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        payload = json.dumps(
            {"service": "enterprise-ai-ingestion", "status": "ok"}, separators=(",", ":")
        ).encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format: str, *args: object) -> None:
        """Avoid writing request paths or client information into default test output."""


def main() -> None:
    host = os.environ.get("INGESTION_HOST", "127.0.0.1")
    port = int(os.environ.get("INGESTION_PORT", "8080"))
    ThreadingHTTPServer((host, port), HealthHandler).serve_forever()


if __name__ == "__main__":
    main()
