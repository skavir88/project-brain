"""Local-only synthetic ingestion and structural-validation service for Stage 1."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from hashlib import sha256
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Lock

import psycopg


seen_fingerprints: set[str] = set()
fingerprint_lock = Lock()


def persistence_enabled() -> bool:
    return all(os.environ.get(name) for name in ("INGESTION_DB_HOST", "INGESTION_DB_NAME", "INGESTION_DB_USER", "INGESTION_DB_PASSWORD"))


def reserve_persisted_record(record: dict[str, object], fingerprint: str, disposition: str, reason_code: str | None, quality_gate: str) -> bool:
    """Persist one synthetic result; false means the unique fingerprint already exists."""
    if not persistence_enabled():
        with fingerprint_lock:
            if fingerprint in seen_fingerprints:
                return False
            seen_fingerprints.add(fingerprint)
            return True
    with psycopg.connect(
        host=os.environ["INGESTION_DB_HOST"], port=os.environ.get("INGESTION_DB_PORT", "5432"),
        dbname=os.environ["INGESTION_DB_NAME"], user=os.environ["INGESTION_DB_USER"], password=os.environ["INGESTION_DB_PASSWORD"],
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """INSERT INTO ingestion.credibility_records
                (record_fingerprint, canonical_record, provenance, source_id, record_id, observed_at, disposition, reason_code, quality_gate_outcome, lifecycle_state)
                VALUES (%s, %s::jsonb, %s::jsonb, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (record_fingerprint) DO NOTHING RETURNING record_fingerprint""",
                (fingerprint, json.dumps(record), json.dumps(record.get("provenance")), record["source_id"], record["record_id"], record.get("observed_at"), disposition, reason_code, quality_gate, disposition),
            )
            return cursor.fetchone() is not None


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
        if self.path.startswith("/v1/records/") and self.path.endswith("/certify"):
            fingerprint = self.path.removeprefix("/v1/records/").removesuffix("/certify").strip("/")
            try:
                actor = json.loads(self.rfile.read(int(self.headers.get("Content-Length", "")))).get("actor_id")
            except (ValueError, json.JSONDecodeError):
                actor = None
            if not isinstance(actor, str) or not actor.strip() or not persistence_enabled():
                self.send_json(HTTPStatus.BAD_REQUEST, {"error": "actor_id_required"}); return
            with psycopg.connect(host=os.environ["INGESTION_DB_HOST"], port=os.environ.get("INGESTION_DB_PORT", "5432"), dbname=os.environ["INGESTION_DB_NAME"], user=os.environ["INGESTION_DB_USER"], password=os.environ["INGESTION_DB_PASSWORD"]) as c:
                with c.cursor() as q:
                    q.execute("""WITH transitioned AS (UPDATE ingestion.credibility_records SET lifecycle_state='certified', certification_timestamp=now(), certification_actor=%s, certification_policy_version='st1-007-v1' WHERE record_fingerprint=%s AND lifecycle_state='certification_candidate' RETURNING record_fingerprint) INSERT INTO ingestion.certification_audit_events(record_fingerprint,previous_lifecycle_state,new_lifecycle_state,certification_timestamp,actor_identifier,policy_version) SELECT record_fingerprint,'certification_candidate','certified',now(),%s,'st1-007-v1' FROM transitioned RETURNING record_fingerprint""", (actor.strip(), fingerprint, actor.strip()))
                    if q.fetchone(): self.send_json(HTTPStatus.OK, {"disposition":"certified","actor_id":actor.strip(),"policy_version":"st1-007-v1"}); return
                    q.execute("SELECT lifecycle_state FROM ingestion.credibility_records WHERE record_fingerprint=%s", (fingerprint,)); row=q.fetchone()
                    self.send_json(HTTPStatus.CONFLICT if row else HTTPStatus.NOT_FOUND, {"error":"already_certified" if row and row[0]=='certified' else "not_eligible" if row else "not_found"}); return
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
                {
                    "accepted": False,
                    "error": "invalid_json",
                    "disposition": "rejected",
                    "reason_code": "structural_validation_failed",
                },
            )
            return

        errors = validate_record(record)
        if errors:
            self.send_json(
                HTTPStatus.UNPROCESSABLE_ENTITY,
                {
                    "accepted": False,
                    "validation_errors": errors,
                    "disposition": "rejected",
                    "reason_code": "structural_validation_failed",
                },
            )
            return

        canonical_record = canonicalize_record(record)
        fingerprint = fingerprint_record(canonical_record)
        disposition, reason_code = evaluate_quality_gate(canonical_record)
        quality_gate = "passed" if disposition == "certification_candidate" else "review_required" if disposition == "human_review_required" else "failed"
        if not reserve_persisted_record(canonical_record, fingerprint, disposition, reason_code, quality_gate):
            self.send_json(HTTPStatus.CONFLICT, {"accepted": False, "duplicate": True, "fingerprint": fingerprint, "disposition": "rejected", "reason_code": "duplicate_detected"})
            return
        if disposition == "rejected":
            self.send_json(
                HTTPStatus.UNPROCESSABLE_ENTITY,
                {
                    "accepted": False,
                    "duplicate": False,
                    "fingerprint": fingerprint,
                    "disposition": disposition,
                    "reason_code": reason_code,
                },
            )
            return

        if disposition == "human_review_required":
            self.send_json(
                HTTPStatus.ACCEPTED,
                {
                    "accepted": True,
                    "duplicate": False,
                    "quality_gate": "review_required",
                    "disposition": disposition,
                    "reason_code": reason_code,
                    "canonical_record": canonical_record,
                    "fingerprint": fingerprint,
                },
            )
            return

        self.send_json(
            HTTPStatus.ACCEPTED,
            {
                "accepted": True,
                "duplicate": False,
                "validation_errors": [],
                "quality_gate": "passed",
                "disposition": "certification_candidate",
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


def evaluate_quality_gate(record: dict[str, object]) -> tuple[str, str | None]:
    """Apply only the approved deterministic MVP credibility checks."""

    observed_at = record.get("observed_at")
    if observed_at is not None:
        if not is_valid_observed_at(observed_at):
            return "rejected", "temporal_validity_failed"

    payload = record["payload"]
    assert isinstance(payload, dict)
    payload_source_id = payload.get("source_id")
    if payload_source_id is not None and (
        not isinstance(payload_source_id, str)
        or payload_source_id.strip() != record["source_id"]
    ):
        return "rejected", "consistency_check_failed"

    provenance = record.get("provenance")
    if not isinstance(provenance, dict):
        return "human_review_required", "provenance_insufficient"
    source_reference = provenance.get("source_reference")
    if not isinstance(source_reference, str) or not source_reference.strip():
        return "human_review_required", "provenance_insufficient"

    return "certification_candidate", None


def is_valid_observed_at(value: object) -> bool:
    """Accept only timezone-aware, non-future ISO-8601 timestamps when supplied."""

    if not isinstance(value, str) or not value.strip():
        return False
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = f"{normalized[:-1]}+00:00"
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return False
    if parsed.tzinfo is None:
        return False
    return parsed.astimezone(timezone.utc) <= datetime.now(timezone.utc)


def main() -> None:
    host = os.environ.get("INGESTION_HOST", "127.0.0.1")
    port = int(os.environ.get("INGESTION_PORT", "8080"))
    ThreadingHTTPServer((host, port), IngestionHandler).serve_forever()


if __name__ == "__main__":
    main()
