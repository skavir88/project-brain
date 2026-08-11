"""Local-only synthetic ingestion and structural-validation service for Stage 1."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from hashlib import sha256
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Lock
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlparse
from urllib.request import Request, urlopen

import psycopg


seen_fingerprints: set[str] = set()
fingerprint_lock = Lock()
SDAS_POLICY = "sdas-v0.1-pilot-assessment-v1"
HEX64 = set("0123456789abcdef")
PASSPORT_RESULTS = {
    "VERIFIED",
    "VERIFIED_WITH_LIMITATIONS",
    "HUMAN_REQUIRED",
    "NOT_RELIANCE_ELIGIBLE",
    "REVOKED_OR_SUPERSEDED",
    "QUARANTINED",
    "INTEGRITY_FAILURE",
}
PORTFOLIO_RESULTS = {
    "VERIFIED",
    "VERIFIED_WITH_LIMITATIONS",
    "HUMAN_REQUIRED",
    "NOT_RELIANCE_ELIGIBLE",
    "REVOKED_OR_SUPERSEDED",
    "QUARANTINED",
    "INTEGRITY_FAILURE",
}
ROUTING_RESULTS = {
    "policy_automatic",
    "human_required",
    "reject_or_quarantine",
}
CERTIFIED_KNOWLEDGE_QDRANT_COLLECTION = os.environ.get("CERTIFIED_KNOWLEDGE_QDRANT_COLLECTION", "enterprise_ai_certified_knowledge_v1")
QDRANT_URL = os.environ.get("QDRANT_URL", "http://rdvector:6333").rstrip("/")
CERTIFIED_KNOWLEDGE_REQUIRED_FIELDS = {
    "knowledge_id",
    "source_fingerprint",
    "source_record_id",
    "certification_event_id",
    "knowledge_text",
    "provenance",
    "certifying_actor",
    "certification_timestamp",
    "certification_policy_version",
}


def persistence_enabled() -> bool:
    return all(os.environ.get(name) for name in ("INGESTION_DB_HOST", "INGESTION_DB_NAME", "INGESTION_DB_USER", "INGESTION_DB_PASSWORD"))


def database_connection() -> psycopg.Connection:
    return psycopg.connect(
        host=os.environ["INGESTION_DB_HOST"], port=os.environ.get("INGESTION_DB_PORT", "5432"),
        dbname=os.environ["INGESTION_DB_NAME"], user=os.environ["INGESTION_DB_USER"], password=os.environ["INGESTION_DB_PASSWORD"],
    )

def is_hex64(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and set(value) <= HEX64


def chained_event_hash(previous_hash: str | None, knowledge_id: str, event_type: str, policy: str, payload: dict[str, object]) -> str:
    return sha256(json.dumps({"previous_event_hash": previous_hash, "knowledge_id": knowledge_id, "event_type": event_type, "policy": policy, "payload": payload}, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def parse_boolean_flag(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def point_id_from_knowledge_id(knowledge_id: str) -> str:
    return (
        f"{knowledge_id[:8]}-{knowledge_id[8:12]}-{knowledge_id[12:16]}-"
        f"{knowledge_id[16:20]}-{knowledge_id[20:32]}"
    )


def qdrant_request(path: str, method: str = "GET", payload: dict[str, object] | None = None) -> tuple[int | None, dict[str, object]]:
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = Request(f"{QDRANT_URL}{path}", data=body, method=method, headers={"Content-Type": "application/json"})
    try:
        with urlopen(request, timeout=20) as response:
            return response.status, json.load(response)
    except HTTPError as error:
        try:
            return error.code, json.load(error)
        except json.JSONDecodeError:
            return error.code, {"error": "qdrant_http_error"}
    except (URLError, TimeoutError, ValueError, json.JSONDecodeError):
        return None, {"error": "qdrant_unavailable"}


def finalize_passport_verification_result(base_result: str, reliance_state: str | None, require_reliance_eligible: bool) -> str:
    if base_result not in PASSPORT_RESULTS:
        raise ValueError("unexpected_passport_result")
    if require_reliance_eligible and base_result in {"VERIFIED", "VERIFIED_WITH_LIMITATIONS"} and reliance_state != "eligible":
        return "NOT_RELIANCE_ELIGIBLE"
    return base_result


def uniq(items: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            output.append(item)
    return output


def build_dimension(*, status: str, evidence_refs: list[str], limitations: list[str], policy_version: str | None = None,
                    verified_at: str | None = None, evaluated_at: str | None = None) -> dict[str, object]:
    payload: dict[str, object] = {
        "status": status,
        "evidence_refs": uniq(evidence_refs),
        "limitations": uniq(limitations),
    }
    if policy_version:
        payload["policy_version"] = policy_version
    if verified_at:
        payload["verified_at"] = verified_at
    if evaluated_at:
        payload["evaluated_at"] = evaluated_at
    return payload


def build_passport_dimensions(row: tuple[object, ...], limitation_codes: list[str]) -> dict[str, object]:
    knowledge_id = str(row[0])
    source_fingerprint = str(row[1])
    source_id = str(row[3]) if isinstance(row[3], str) else None
    quality_gate_outcome = str(row[5]) if isinstance(row[5], str) else None
    certification_timestamp = row[11].isoformat() if row[11] else None
    certification_policy_version = row[12] if isinstance(row[12], str) else None
    assurance_policy_version = row[15] if isinstance(row[15], str) else None
    currentness_state = str(row[19]) if isinstance(row[19], str) else "not_assessed"
    reliance_state = str(row[20]) if isinstance(row[20], str) else "not_eligible"
    authority_state = str(row[25]) if isinstance(row[25], str) else "missing"
    business_time_state = str(row[26]) if isinstance(row[26], str) else "missing"
    provenance_link_valid = bool(row[32])
    assurance_chain_valid = bool(row[33])
    consumption_chain_valid = bool(row[34])
    consumption_count = int(row[35]) if row[35] is not None else 0
    last_consumed_at = row[36].isoformat() if row[36] else None
    post_event_type = str(row[37]) if isinstance(row[37], str) else None
    post_event_at = row[38].isoformat() if row[38] else None
    policy_reason_codes = row[39] if isinstance(row[39], list) else []
    assurance_reason_codes = row[40] if isinstance(row[40], list) else []

    integrity_limitations = []
    if not provenance_link_valid:
        integrity_limitations.append("provenance_link_mismatch")
    if not assurance_chain_valid:
        integrity_limitations.append("assurance_event_chain_mismatch")
    if not consumption_chain_valid:
        integrity_limitations.append("consumption_event_chain_mismatch")

    conflict_limitations = [code for code in limitation_codes if code in {"authority_conflict", "business_time_conflict"}]
    authority_limitations = [code for code in limitation_codes if code.startswith("authority_") or code == "governance_waiting_for_external_evidence"]
    business_time_limitations = [code for code in limitation_codes if code.startswith("business_time_")]

    return {
        "identity": build_dimension(
            status="VERIFIED" if knowledge_id and source_fingerprint else "MISSING",
            evidence_refs=[f"knowledge:{knowledge_id}", f"record:{source_fingerprint}", f"source:{source_id}" if source_id else ""],
            limitations=[],
            verified_at=certification_timestamp,
        ),
        "provenance": build_dimension(
            status="VERIFIED" if provenance_link_valid else "INTEGRITY_FAILURE",
            evidence_refs=[f"knowledge:{knowledge_id}", f"record:{source_fingerprint}"],
            limitations=["provenance_link_mismatch"] if not provenance_link_valid else [],
            verified_at=certification_timestamp,
        ),
        "integrity": build_dimension(
            status="INTEGRITY_FAILURE" if integrity_limitations else "VERIFIED",
            evidence_refs=[f"assurance_chain:{knowledge_id}", f"consumption_chain:{knowledge_id}"],
            limitations=integrity_limitations,
            evaluated_at=last_consumed_at or certification_timestamp,
        ),
        "authority": build_dimension(
            status={"verified": "VERIFIED", "missing": "MISSING", "conflict": "CONFLICT", "revoked_or_superseded": "REVOKED_OR_SUPERSEDED"}.get(authority_state, "PARTIAL"),
            evidence_refs=[f"authority_assertions:record:{source_fingerprint}", f"source_registry:{source_id}" if source_id else ""],
            limitations=authority_limitations,
            policy_version=assurance_policy_version,
            evaluated_at=certification_timestamp,
        ),
        "business_time": build_dimension(
            status={"valid": "VERIFIED", "missing": "MISSING", "conflict": "CONFLICT"}.get(business_time_state, "PARTIAL"),
            evidence_refs=[f"business_time_evidence:{source_fingerprint}"],
            limitations=business_time_limitations,
            evaluated_at=certification_timestamp,
        ),
        "validation": build_dimension(
            status="VERIFIED" if quality_gate_outcome == "passed" else "PARTIAL",
            evidence_refs=[f"credibility_record:{source_fingerprint}"],
            limitations=[] if quality_gate_outcome == "passed" else ["validation_outcome_not_passed_or_not_recorded"],
            evaluated_at=certification_timestamp,
        ),
        "policy": build_dimension(
            status="VERIFIED" if row[22] and row[23] else "MISSING",
            evidence_refs=[f"policy_decision:{source_fingerprint}"],
            limitations=uniq([*policy_reason_codes, *assurance_reason_codes]),
            policy_version=str(row[23]) if isinstance(row[23], str) else None,
            evaluated_at=certification_timestamp,
        ),
        "human_review": build_dimension(
            status="REQUIRED" if row[24] == "human_required" else "NOT_REQUIRED",
            evidence_refs=[f"certification_event:{row[9]}"] if row[9] else [],
            limitations=["human_review_required"] if row[24] == "human_required" else [],
            verified_at=certification_timestamp,
        ),
        "certification": build_dimension(
            status="VERIFIED" if row[9] and certification_timestamp else "MISSING",
            evidence_refs=[f"certification_event:{row[9]}"] if row[9] else [],
            limitations=[],
            policy_version=certification_policy_version,
            verified_at=certification_timestamp,
        ),
        "currentness": build_dimension(
            status="VERIFIED" if currentness_state == "current_eligible" else "LIMITED",
            evidence_refs=[f"assurance_decision:{source_fingerprint}"],
            limitations=["currentness_limited"] if currentness_state != "current_eligible" else [],
            policy_version=assurance_policy_version,
            evaluated_at=certification_timestamp,
        ),
        "reliance": build_dimension(
            status="VERIFIED" if reliance_state == "eligible" else "NOT_RELIANCE_ELIGIBLE",
            evidence_refs=[f"assurance_decision:{source_fingerprint}"],
            limitations=["reliance_not_eligible"] if reliance_state != "eligible" else [],
            policy_version=assurance_policy_version,
            evaluated_at=certification_timestamp,
        ),
        "conflict": build_dimension(
            status="CONFLICT" if conflict_limitations else "CLEAR",
            evidence_refs=[f"authority_assertions:record:{source_fingerprint}", f"business_time_evidence:{source_fingerprint}"],
            limitations=conflict_limitations,
            evaluated_at=certification_timestamp,
        ),
        "revocation": build_dimension(
            status="REVOKED" if post_event_type == "revocation" else "CLEAR",
            evidence_refs=[f"post_registration:{knowledge_id}"] if post_event_type == "revocation" else [],
            limitations=["post_registration_terminal_event"] if post_event_type == "revocation" else [],
            evaluated_at=post_event_at,
        ),
        "supersession": build_dimension(
            status="SUPERSEDED" if post_event_type == "supersession" else "CLEAR",
            evidence_refs=[f"post_registration:{knowledge_id}"] if post_event_type == "supersession" else [],
            limitations=["post_registration_terminal_event"] if post_event_type == "supersession" else [],
            evaluated_at=post_event_at,
        ),
        "consumption": build_dimension(
            status="VERIFIED" if consumption_count > 0 and consumption_chain_valid else "NOT_VERIFIABLE" if consumption_count == 0 else "INTEGRITY_FAILURE",
            evidence_refs=[f"consumption_events:{knowledge_id}"],
            limitations=[] if consumption_count > 0 and consumption_chain_valid else ["consumption_history_missing"] if consumption_count == 0 else ["consumption_event_chain_mismatch"],
            evaluated_at=last_consumed_at,
        ),
    }


def row_to_passport_payload(row: tuple[object, ...], require_reliance_eligible: bool) -> dict[str, object]:
    limitation_codes = row[31] if isinstance(row[31], list) else []
    verification_result = finalize_passport_verification_result(str(row[30]), row[20] if isinstance(row[20], str) else None, require_reliance_eligible)
    dimensions = build_passport_dimensions(row, limitation_codes)
    return {
        "contract_version": "SDAS Assurance Passport v0.1",
        "knowledge_id": row[0],
        "source_fingerprint": row[1],
        "source_record_id": row[2],
        "source_id": row[3],
        "record_id": row[4],
        "quality_gate_outcome": row[5],
        "observed_at": row[6].isoformat() if row[6] else None,
        "ingested_at": row[7].isoformat() if row[7] else None,
        "acquired_at": row[8].isoformat() if row[8] else None,
        "certification": {
            "event_id": row[9],
            "actor": row[10],
            "timestamp": row[11].isoformat() if row[11] else None,
            "policy_version": row[12],
        },
        "assurance": {
            "level": row[13],
            "state": row[14],
            "policy_version": row[15],
            "authority_inheritance_state": row[16],
            "business_time_state": row[17],
            "risk_tier": row[18],
            "currentness_state": row[19],
            "reliance_state": row[20],
            "outcome": row[21],
            "reason_codes": row[40] if isinstance(row[40], list) else [],
        },
        "policy": {
            "policy_id": row[22],
            "policy_version": row[23],
            "approval_mode": row[24],
            "reason_codes": row[39] if isinstance(row[39], list) else [],
        },
        "authority": {
            "passport_authority_state": row[25],
            "source_registry_authority_status": row[26],
        },
        "transformations": {
            "count": row[27],
            "all_deterministic": row[28],
        },
        "verification_result": verification_result,
        "reason_codes": uniq(limitation_codes),
        "business_time_evidence": row[29] if isinstance(row[29], list) else [],
        "limitation_codes": limitation_codes,
        "chain_integrity": {
            "provenance_link_valid": row[32],
            "assurance_event_chain_valid": row[33],
            "consumption_event_chain_valid": row[34],
        },
        "consumption": {
            "count": row[35],
            "last_consumed_at": row[36].isoformat() if row[36] else None,
        },
        "post_registration": {
            "event_type": row[37],
            "event_at": row[38].isoformat() if row[38] else None,
        },
        "dimensions": dimensions,
        "request_constraints": {
            "require_reliance_eligible": require_reliance_eligible,
        },
    }


def row_to_portfolio_summary_payload(rows: list[tuple[object, ...]]) -> dict[str, object]:
    ordered_results = [
        "VERIFIED",
        "VERIFIED_WITH_LIMITATIONS",
        "HUMAN_REQUIRED",
        "NOT_RELIANCE_ELIGIBLE",
        "REVOKED_OR_SUPERSEDED",
        "QUARANTINED",
        "INTEGRITY_FAILURE",
    ]
    summary = {result: {"passport_count": 0, "limitation_code_counts": {}} for result in ordered_results}
    total = 0
    for result, count, limitation_counts in rows:
        if result not in PORTFOLIO_RESULTS:
            continue
        summary[result] = {
            "passport_count": int(count),
            "limitation_code_counts": limitation_counts if isinstance(limitation_counts, dict) else {},
        }
        total += int(count)
    return {"total_passports": total, "results": summary}


def row_to_exception_payload(row: tuple[object, ...]) -> dict[str, object]:
    return {
        "knowledge_id": row[0],
        "source_id": row[1],
        "source_record_id": row[2],
        "certification_timestamp": row[3].isoformat() if row[3] else None,
        "verification_result": row[4],
        "limitation_codes": row[5] if isinstance(row[5], list) else [],
        "passport_authority_state": row[6],
        "passport_business_time_state": row[7],
        "currentness_state": row[8],
        "reliance_state": row[9],
        "risk_tier": row[10],
        "latest_post_registration_event_type": row[11],
    }


def row_to_routing_summary_payload(rows: list[tuple[object, ...]]) -> dict[str, object]:
    ordered_results = ["policy_automatic", "human_required", "reject_or_quarantine"]
    summary = {result: {"record_count": 0, "reason_code_counts": {}} for result in ordered_results}
    total = 0
    for result, count, reason_counts in rows:
        if result not in ROUTING_RESULTS:
            continue
        summary[result] = {
            "record_count": int(count),
            "reason_code_counts": reason_counts if isinstance(reason_counts, dict) else {},
        }
        total += int(count)
    return {"total_records": total, "results": summary}


def row_to_routing_exception_payload(row: tuple[object, ...]) -> dict[str, object]:
    return {
        "record_fingerprint": row[0],
        "source_id": row[1],
        "record_id": row[2],
        "lifecycle_state": row[3],
        "quality_gate_outcome": row[4],
        "policy": {
            "policy_id": row[5],
            "policy_version": row[6],
            "approval_mode": row[7],
        },
        "assurance": {
            "policy_version": row[8],
            "outcome": row[9],
            "authority_inheritance_state": row[10],
            "business_time_state": row[11],
            "currentness_state": row[12],
            "reliance_state": row[13],
        },
        "governance_dependency_state": row[14],
        "effective_routing_outcome": row[15],
        "effective_reason_codes": row[16] if isinstance(row[16], list) else [],
        "observed_at": row[17].isoformat() if row[17] else None,
        "ingested_at": row[18].isoformat() if row[18] else None,
    }


def row_to_routing_detail_payload(row: tuple[object, ...]) -> dict[str, object]:
    return {
        "record_fingerprint": row[0],
        "source_id": row[1],
        "record_id": row[2],
        "record_state": {
            "lifecycle_state": row[3],
            "disposition": row[4],
            "quality_gate_outcome": row[5],
            "observed_at": row[6].isoformat() if row[6] else None,
            "ingested_at": row[7].isoformat() if row[7] else None,
        },
        "policy": {
            "policy_id": row[8],
            "policy_version": row[9],
            "approval_mode": row[10],
            "decision_timestamp": row[11].isoformat() if row[11] else None,
            "reason_codes": row[12] if isinstance(row[12], list) else [],
        },
        "assurance": {
            "policy_version": row[13],
            "outcome": row[14],
            "decision_timestamp": row[15].isoformat() if row[15] else None,
            "reason_codes": row[16] if isinstance(row[16], list) else [],
            "authority_inheritance_state": row[17],
            "business_time_state": row[18],
            "risk_tier": row[19],
            "currentness_state": row[20],
            "reliance_state": row[21],
        },
        "routing": {
            "matched_active_delegation_count": row[22],
            "governance_dependency_state": row[23],
            "effective_routing_outcome": row[24],
            "effective_reason_codes": row[25] if isinstance(row[25], list) else [],
        },
        "source": {
            "source_type": row[26],
            "system_location_identity": row[27],
            "owner_actor_id": row[28],
            "business_purpose": row[29],
            "authority_status": row[30],
            "authority_scope": row[31] if isinstance(row[31], dict) else {},
            "effective_from": row[32].isoformat() if row[32] else None,
            "effective_to": row[33].isoformat() if row[33] else None,
            "evidence_quality": row[34],
        },
        "matched_active_delegations": row[35] if isinstance(row[35], list) else [],
        "triage_signals": row[36] if isinstance(row[36], dict) else {},
    }


def collection_projection_state(collection_name: str) -> dict[str, object]:
    status, payload = qdrant_request(f"/collections/{collection_name}")
    if status == 200:
        result = payload.get("result", {}) if isinstance(payload, dict) else {}
        config = result.get("config", {}) if isinstance(result, dict) else {}
        params = config.get("params", {}) if isinstance(config, dict) else {}
        vectors = params.get("vectors", {}) if isinstance(params, dict) else {}
        return {
            "collection_exists": True,
            "collection_runtime_state": result.get("status"),
            "points_count": result.get("points_count"),
            "vector_dimension": vectors.get("size"),
            "distance_metric": vectors.get("distance"),
        }
    if status == 404:
        return {
            "collection_exists": False,
            "collection_runtime_state": "missing",
            "points_count": None,
            "vector_dimension": None,
            "distance_metric": None,
        }
    return {
        "collection_exists": False,
        "collection_runtime_state": "unavailable",
        "points_count": None,
        "vector_dimension": None,
        "distance_metric": None,
    }


def point_projection_state(*, collection_name: str, point_id: str, knowledge_id: str, source_fingerprint: str,
                           source_record_id: str, certification_event_id: int | None) -> dict[str, object]:
    status, payload = qdrant_request(
        f"/collections/{collection_name}/points",
        "POST",
        {"ids": [point_id], "with_payload": True, "with_vector": False},
    )
    if status != 200:
        return {
            "indexed_point_present": None,
            "payload_contract_valid": None,
            "payload_knowledge_id_match": None,
            "payload_source_fingerprint_match": None,
            "payload_source_record_id_match": None,
            "payload_certification_event_id_match": None,
            "point_runtime_state": "unavailable",
        }
    result = payload.get("result", []) if isinstance(payload, dict) else []
    point = result[0] if isinstance(result, list) and result else None
    if not isinstance(point, dict):
        return {
            "indexed_point_present": False,
            "payload_contract_valid": None,
            "payload_knowledge_id_match": None,
            "payload_source_fingerprint_match": None,
            "payload_source_record_id_match": None,
            "payload_certification_event_id_match": None,
            "point_runtime_state": "missing",
        }
    item = point.get("payload")
    payload_contract_valid = isinstance(item, dict) and set(item) == CERTIFIED_KNOWLEDGE_REQUIRED_FIELDS
    return {
        "indexed_point_present": True,
        "payload_contract_valid": payload_contract_valid,
        "payload_knowledge_id_match": item.get("knowledge_id") == knowledge_id if payload_contract_valid else None,
        "payload_source_fingerprint_match": item.get("source_fingerprint") == source_fingerprint if payload_contract_valid else None,
        "payload_source_record_id_match": item.get("source_record_id") == source_record_id if payload_contract_valid else None,
        "payload_certification_event_id_match": item.get("certification_event_id") == certification_event_id if payload_contract_valid else None,
        "point_runtime_state": "present",
    }


def build_passport_index_projection_state(*, row: tuple[object, ...], collection_state: dict[str, object],
                                          point_state: dict[str, object]) -> dict[str, object]:
    collection_exists = bool(collection_state["collection_exists"])
    indexed_point_present = point_state["indexed_point_present"]
    payload_checks = [
        point_state["payload_contract_valid"],
        point_state["payload_knowledge_id_match"],
        point_state["payload_source_fingerprint_match"],
        point_state["payload_source_record_id_match"],
        point_state["payload_certification_event_id_match"],
    ]
    if collection_state["collection_runtime_state"] == "unavailable":
        visibility_result = "index_runtime_unavailable"
    elif not collection_exists:
        visibility_result = "collection_missing"
    elif indexed_point_present is False:
        visibility_result = "certified_not_indexed"
    elif indexed_point_present is True and all(value is True for value in payload_checks):
        visibility_result = "indexed_certified_projection_visible"
    elif indexed_point_present is True:
        visibility_result = "indexed_payload_mismatch"
    else:
        visibility_result = "point_runtime_unavailable"
    return {
        "collection_name": row[5],
        "point_id": row[4],
        "collection_exists": collection_exists,
        "collection_runtime_state": collection_state["collection_runtime_state"],
        "points_count": collection_state["points_count"],
        "vector_dimension": collection_state["vector_dimension"],
        "distance_metric": collection_state["distance_metric"],
        "indexed_point_present": indexed_point_present,
        "point_runtime_state": point_state["point_runtime_state"],
        "payload_contract_valid": point_state["payload_contract_valid"],
        "payload_knowledge_id_match": point_state["payload_knowledge_id_match"],
        "payload_source_fingerprint_match": point_state["payload_source_fingerprint_match"],
        "payload_source_record_id_match": point_state["payload_source_record_id_match"],
        "payload_certification_event_id_match": point_state["payload_certification_event_id_match"],
        "visibility_result": visibility_result,
    }


def row_to_passport_index_payload(row: tuple[object, ...], index_projection: dict[str, object]) -> dict[str, object]:
    return {
        "contract_version": "SDAS Assurance Passport Index Adjunct v0.1",
        "knowledge_id": row[0],
        "source_fingerprint": row[1],
        "source_record_id": row[2],
        "certification": {
            "event_id": row[3],
            "timestamp": row[10].isoformat() if row[10] else None,
            "policy_version": row[11],
        },
        "assurance_context": {
            "passport_base_verification_result": row[6],
            "currentness_state": row[7],
            "reliance_state": row[8],
            "latest_post_registration_event_type": row[9],
            "limitation_codes": row[12] if isinstance(row[12], list) else [],
        },
        "index_projection": index_projection,
        "boundaries": {
            "certified_scope_only": True,
            "raw_vector_exposed": False,
            "provider_or_credential_state_exposed": False,
            "retrieval_threshold_changed": False,
            "certification_or_governance_mutated": False,
        },
    }


def build_sdas_assessment(row: tuple[object, ...]) -> dict[str, object]:
    """Assess only evidence already persisted; absent evidence remains missing."""
    provenance = row[6] if isinstance(row[6], dict) else {}
    source_reference = provenance.get("source_reference") if isinstance(provenance, dict) else None
    dimensions = {
        "source_identity": "present" if row[7] and source_reference else "partial",
        "acquisition": "missing",
        "timestamp_semantics": "partial" if row[4] and row[9] else "missing",
        "fingerprint_integrity": "partial",
        "extraction_transformation": "missing",
        "validation": "present" if row[10] else "missing",
        "reviewer_identity_role": "partial" if row[11] else "missing",
        "review_decision": "present",
        "certification": "present" if row[4] and row[5] and row[11] else "partial",
        "audit_linkage": "present" if row[12] else "missing",
        "certified_knowledge_registration": "present",
        "supersession_revocation_state": "missing",
        "consumption_provenance": "missing",
    }
    # SDAS-1 is intentionally limited to the already verifiable traceable
    # certification chain; it says nothing about authority, freshness, or use.
    traceable = all(dimensions[key] == "present" for key in ("source_identity", "validation", "review_decision", "certification", "audit_linkage", "certified_knowledge_registration"))
    level = "SDAS-1" if traceable else "SDAS-0"
    gaps = sorted(key for key, status in dimensions.items() if status != "present")
    return {"level": level, "state": "assessed_partial", "dimensions": dimensions, "gaps": gaps}


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
        parsed_path = urlparse(self.path)
        if parsed_path.path == "/health":
            self.send_json(
                HTTPStatus.OK,
                {"service": "enterprise-ai-ingestion", "status": "ok"},
            )
            return

        if parsed_path.path == "/v1/sdas/passport":
            query = parse_qs(parsed_path.query, keep_blank_values=True)
            knowledge_id = query.get("knowledge_id", [""])
            require_reliance_eligible = parse_boolean_flag(query.get("require_reliance_eligible", ["false"])[0])
            if len(knowledge_id) != 1 or not is_hex64(knowledge_id[0]) or not persistence_enabled():
                self.send_json(HTTPStatus.BAD_REQUEST, {"error": "invalid_assurance_passport_request"})
                return
            with database_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """SELECT knowledge_id, source_fingerprint, source_record_id, source_id, record_id,
                                  quality_gate_outcome, observed_at, ingested_at, acquired_at,
                                  certification_event_id, certifying_actor, certification_timestamp,
                                  certification_policy_version, assurance_level, assurance_state,
                                  assurance_policy_version, authority_inheritance_state,
                                  business_time_state, risk_tier, currentness_state, reliance_state,
                                  assurance_outcome, policy_id, policy_version, policy_approval_mode, passport_authority_state,
                                  source_registry_authority_status, transformation_count,
                                  all_transformations_deterministic, business_time_evidence,
                                  base_verification_result, limitation_codes, provenance_link_valid,
                                  assurance_event_chain_valid, consumption_event_chain_valid,
                                  consumption_count, last_consumed_at,
                                  latest_post_registration_event_type, latest_post_registration_event_at,
                                  policy_reason_codes, assurance_reason_codes
                           FROM ingestion.sdas_assurance_passport_projection
                           WHERE knowledge_id=%s""",
                        (knowledge_id[0],),
                    )
                    row = cursor.fetchone()
            if not row:
                self.send_json(HTTPStatus.NOT_FOUND, {"error": "assurance_passport_not_found"})
                return
            self.send_json(HTTPStatus.OK, row_to_passport_payload(row, require_reliance_eligible))
            return

        if parsed_path.path == "/v1/sdas/passports/summary":
            if not persistence_enabled():
                self.send_json(HTTPStatus.BAD_REQUEST, {"error": "assurance_passport_summary_unavailable"})
                return
            with database_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """SELECT verification_result, passport_count, limitation_code_counts
                           FROM ingestion.sdas_assurance_passport_portfolio_summary
                           ORDER BY verification_result"""
                    )
                    rows = cursor.fetchall()
            self.send_json(HTTPStatus.OK, row_to_portfolio_summary_payload(rows))
            return

        if parsed_path.path == "/v1/sdas/passports/exceptions":
            query = parse_qs(parsed_path.query, keep_blank_values=True)
            requested_result = query.get("verification_result", [""])[0].strip()
            if requested_result and requested_result not in PORTFOLIO_RESULTS:
                self.send_json(HTTPStatus.BAD_REQUEST, {"error": "invalid_exception_filter"})
                return
            if not persistence_enabled():
                self.send_json(HTTPStatus.BAD_REQUEST, {"error": "assurance_passport_exception_queue_unavailable"})
                return
            sql = """SELECT knowledge_id, source_id, source_record_id, certification_timestamp,
                            verification_result, limitation_codes, passport_authority_state,
                            passport_business_time_state, currentness_state, reliance_state,
                            risk_tier, latest_post_registration_event_type
                     FROM ingestion.sdas_assurance_passport_exception_queue"""
            params: tuple[object, ...] = ()
            if requested_result:
                sql += " WHERE verification_result=%s"
                params = (requested_result,)
            sql += " ORDER BY certification_timestamp DESC, knowledge_id LIMIT 500"
            with database_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(sql, params)
                    rows = cursor.fetchall()
            self.send_json(
                HTTPStatus.OK,
                {
                    "count": len(rows),
                    "verification_result_filter": requested_result or None,
                    "items": [row_to_exception_payload(row) for row in rows],
                },
            )
            return

        if parsed_path.path == "/v1/sdas/passport/index":
            query = parse_qs(parsed_path.query, keep_blank_values=True)
            knowledge_id = query.get("knowledge_id", [""])
            if len(knowledge_id) != 1 or not is_hex64(knowledge_id[0]) or not persistence_enabled():
                self.send_json(HTTPStatus.BAD_REQUEST, {"error": "invalid_assurance_passport_index_request"})
                return
            with database_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """SELECT knowledge_id, source_fingerprint, source_record_id, certification_event_id,
                                  qdrant_point_id, qdrant_collection_name, passport_base_verification_result,
                                  currentness_state, reliance_state, latest_post_registration_event_type,
                                  certification_timestamp, certification_policy_version, limitation_codes
                           FROM ingestion.sdas_assurance_passport_index_projection
                           WHERE knowledge_id=%s""",
                        (knowledge_id[0],),
                    )
                    row = cursor.fetchone()
            if not row:
                self.send_json(HTTPStatus.NOT_FOUND, {"error": "assurance_passport_index_not_found"})
                return
            collection_state = collection_projection_state(str(row[5]))
            point_state = point_projection_state(
                collection_name=str(row[5]),
                point_id=str(row[4]),
                knowledge_id=str(row[0]),
                source_fingerprint=str(row[1]),
                source_record_id=str(row[2]),
                certification_event_id=int(row[3]) if row[3] is not None else None,
            )
            self.send_json(
                HTTPStatus.OK,
                row_to_passport_index_payload(
                    row,
                    build_passport_index_projection_state(row=row, collection_state=collection_state, point_state=point_state),
                ),
            )
            return

        if parsed_path.path == "/v1/sdas/routing/summary":
            if not persistence_enabled():
                self.send_json(HTTPStatus.BAD_REQUEST, {"error": "sdas_routing_summary_unavailable"})
                return
            with database_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """SELECT effective_routing_outcome, record_count, reason_code_counts
                           FROM ingestion.sdas_record_policy_routing_summary
                           ORDER BY effective_routing_outcome"""
                    )
                    rows = cursor.fetchall()
            self.send_json(HTTPStatus.OK, row_to_routing_summary_payload(rows))
            return

        if parsed_path.path == "/v1/sdas/routing/exceptions":
            query = parse_qs(parsed_path.query, keep_blank_values=True)
            requested_outcome = query.get("outcome", [""])[0].strip()
            if requested_outcome and requested_outcome not in ROUTING_RESULTS:
                self.send_json(HTTPStatus.BAD_REQUEST, {"error": "invalid_routing_exception_filter"})
                return
            if not persistence_enabled():
                self.send_json(HTTPStatus.BAD_REQUEST, {"error": "sdas_routing_exception_queue_unavailable"})
                return
            sql = """SELECT record_fingerprint, source_id, record_id, lifecycle_state,
                            quality_gate_outcome, policy_id, policy_version,
                            policy_approval_mode, assurance_policy_version,
                            assurance_outcome, authority_inheritance_state,
                            business_time_state, currentness_state, reliance_state,
                            governance_dependency_state, effective_routing_outcome,
                            effective_reason_codes, observed_at, ingested_at
                     FROM ingestion.sdas_record_policy_routing_exception_queue"""
            params: tuple[object, ...] = ()
            if requested_outcome:
                sql += " WHERE effective_routing_outcome=%s"
                params = (requested_outcome,)
            sql += " LIMIT 500"
            with database_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(sql, params)
                    rows = cursor.fetchall()
            self.send_json(
                HTTPStatus.OK,
                {
                    "count": len(rows),
                    "outcome_filter": requested_outcome or None,
                    "items": [row_to_routing_exception_payload(row) for row in rows],
                },
            )
            return

        if parsed_path.path == "/v1/sdas/routing/detail":
            query = parse_qs(parsed_path.query, keep_blank_values=True)
            record_fingerprint = query.get("record_fingerprint", [""])
            if len(record_fingerprint) != 1 or not is_hex64(record_fingerprint[0]) or not persistence_enabled():
                self.send_json(HTTPStatus.BAD_REQUEST, {"error": "invalid_routing_detail_request"})
                return
            with database_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """SELECT record_fingerprint, source_id, record_id, lifecycle_state, disposition,
                                  quality_gate_outcome, observed_at, ingested_at, policy_id,
                                  policy_version, policy_approval_mode, policy_decision_timestamp,
                                  policy_reason_codes, assurance_policy_version, assurance_outcome,
                                  assurance_decision_timestamp, assurance_reason_codes,
                                  authority_inheritance_state, business_time_state, risk_tier,
                                  currentness_state, reliance_state,
                                  matched_active_delegation_count, governance_dependency_state,
                                  effective_routing_outcome, effective_reason_codes, source_type,
                                  system_location_identity, owner_actor_id, business_purpose,
                                  source_registry_authority_status, source_registry_authority_scope,
                                  source_registry_effective_from, source_registry_effective_to,
                                  source_registry_evidence_quality, matched_active_delegations,
                                  triage_signals
                           FROM ingestion.sdas_record_policy_routing_detail
                           WHERE record_fingerprint=%s""",
                        (record_fingerprint[0],),
                    )
                    row = cursor.fetchone()
            if not row:
                self.send_json(HTTPStatus.NOT_FOUND, {"error": "routing_detail_not_found"})
                return
            self.send_json(HTTPStatus.OK, row_to_routing_detail_payload(row))
            return

        if parsed_path.path != "/v1/knowledge":
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        query_values = parse_qs(parsed_path.query, keep_blank_values=True).get("query", [""])
        if len(query_values) != 1 or len(query_values[0]) > 128:
            self.send_json(HTTPStatus.BAD_REQUEST, {"error": "invalid_query"})
            return
        if not persistence_enabled():
            self.send_json(HTTPStatus.SERVICE_UNAVAILABLE, {"error": "knowledge_retrieval_unavailable"})
            return

        query = query_values[0].strip()
        with psycopg.connect(
            host=os.environ["INGESTION_DB_HOST"], port=os.environ.get("INGESTION_DB_PORT", "5432"),
            dbname=os.environ["INGESTION_DB_NAME"], user=os.environ["INGESTION_DB_USER"], password=os.environ["INGESTION_DB_PASSWORD"],
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """SELECT knowledge_id, source_fingerprint, source_record_id, certification_event_id, knowledge_text,
                              provenance, certifying_actor, certification_timestamp,
                              certification_policy_version
                       FROM ingestion.certified_knowledge_items
                       WHERE knowledge_text ILIKE %s
                       ORDER BY knowledge_id
                       LIMIT 100""",
                    (f"%{query}%",),
                )
                rows = cursor.fetchall()
        items = [
            {
                "knowledge_id": row[0], "source_fingerprint": row[1],
                "source_record_id": row[2], "certification_event_id": row[3],
                "knowledge_text": row[4], "provenance": row[5],
                "certifying_actor": row[6], "certification_timestamp": row[7].isoformat(),
                "certification_policy_version": row[8],
            }
            for row in rows
        ]
        self.send_json(HTTPStatus.OK, {"query": query, "count": len(items), "items": items})

    def do_POST(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        if self.path == "/v1/sdas/assess":
            self.handle_sdas_assess(); return
        if self.path == "/v1/sdas/consumption":
            self.handle_sdas_consumption(); return
        if self.path.startswith("/v1/records/") and self.path.endswith("/certify"):
            fingerprint = self.path.removeprefix("/v1/records/").removesuffix("/certify").strip("/")
            try:
                request = json.loads(self.rfile.read(int(self.headers.get("Content-Length", ""))))
                actor = request.get("actor_id")
                policy_version = request.get("policy_version", "st1-007-v1")
            except (ValueError, json.JSONDecodeError):
                actor, policy_version = None, None
            if not isinstance(actor, str) or not actor.strip() or policy_version not in {"st1-007-v1", "st1-023-historical-v1", "st1-026-source-attributed-v1", "st1-032-source-attributed-v1", "st1-041-source-attributed-v1", "st1-045-management-report-historical-v1", "st1-047-biweekly-management-report-v1"} or not persistence_enabled():
                self.send_json(HTTPStatus.BAD_REQUEST, {"error": "actor_id_required"}); return
            with psycopg.connect(host=os.environ["INGESTION_DB_HOST"], port=os.environ.get("INGESTION_DB_PORT", "5432"), dbname=os.environ["INGESTION_DB_NAME"], user=os.environ["INGESTION_DB_USER"], password=os.environ["INGESTION_DB_PASSWORD"]) as c:
                with c.cursor() as q:
                    q.execute("""WITH transitioned AS (UPDATE ingestion.credibility_records SET lifecycle_state='certified', certification_timestamp=now(), certification_actor=%s, certification_policy_version=%s WHERE record_fingerprint=%s AND lifecycle_state='certification_candidate' RETURNING record_fingerprint) INSERT INTO ingestion.certification_audit_events(record_fingerprint,previous_lifecycle_state,new_lifecycle_state,certification_timestamp,actor_identifier,policy_version) SELECT record_fingerprint,'certification_candidate','certified',now(),%s,%s FROM transitioned RETURNING record_fingerprint""", (actor.strip(), policy_version, fingerprint, actor.strip(), policy_version))
                    if q.fetchone(): self.send_json(HTTPStatus.OK, {"disposition":"certified","actor_id":actor.strip(),"policy_version":policy_version}); return
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

    def request_json(self) -> dict[str, object] | None:
        try:
            length = int(self.headers.get("Content-Length", ""))
            payload = json.loads(self.rfile.read(length))
        except (ValueError, json.JSONDecodeError):
            return None
        return payload if isinstance(payload, dict) else None

    def handle_sdas_assess(self) -> None:
        request = self.request_json()
        knowledge_id = request.get("knowledge_id") if request else None
        actor = request.get("actor_id") if request else None
        policy = request.get("assessment_policy_version") if request else None
        if not persistence_enabled() or not is_hex64(knowledge_id) or not isinstance(actor, str) or not actor.strip() or policy != SDAS_POLICY:
            self.send_json(HTTPStatus.BAD_REQUEST, {"error": "invalid_sdas_assessment_request"}); return
        with database_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""SELECT k.knowledge_id,k.source_fingerprint,k.source_record_id,k.certification_event_id,
                                  k.certification_timestamp,k.certification_policy_version,k.provenance,
                                  r.source_id,r.observed_at,r.ingested_at,r.quality_gate_outcome,
                                  r.certification_actor,a.event_id
                           FROM ingestion.certified_knowledge_items k
                           JOIN ingestion.credibility_records r ON r.record_fingerprint=k.source_fingerprint
                           JOIN ingestion.certification_audit_events a ON a.event_id=k.certification_event_id
                           WHERE k.knowledge_id=%s AND k.lifecycle_state='certified'""", (knowledge_id,))
                row = cursor.fetchone()
                if not row:
                    self.send_json(HTTPStatus.NOT_FOUND, {"error": "certified_knowledge_not_found"}); return
                assessment = build_sdas_assessment(row)
                envelope_payload = {
                    "knowledge_id": knowledge_id, "source_fingerprint": row[1], "policy": policy,
                    "level": assessment["level"], "state": assessment["state"],
                    "dimensions": assessment["dimensions"], "gaps": assessment["gaps"], "actor": actor.strip(),
                }
                envelope_fingerprint = fingerprint_record(envelope_payload)
                cursor.execute("""INSERT INTO ingestion.sdas_assurance_envelopes
                    (knowledge_id,source_fingerprint,assessment_policy_version,assurance_level,assurance_state,dimensions,gaps,assessed_by,envelope_fingerprint)
                    VALUES (%s,%s,%s,%s,%s,%s::jsonb,%s::jsonb,%s,%s)
                    ON CONFLICT (knowledge_id) DO NOTHING RETURNING knowledge_id""",
                    (knowledge_id,row[1],policy,assessment["level"],assessment["state"],json.dumps(assessment["dimensions"]),json.dumps(assessment["gaps"]),actor.strip(),envelope_fingerprint))
                if not cursor.fetchone():
                    self.send_json(HTTPStatus.CONFLICT, {"error": "already_assessed"}); return
                event_payload = {"envelope_fingerprint": envelope_fingerprint, "dimension_statuses": assessment["dimensions"]}
                event_hash = chained_event_hash(None, knowledge_id, "assessed_partial", policy, event_payload)
                cursor.execute("""INSERT INTO ingestion.sdas_assurance_events
                    (knowledge_id,previous_state,new_state,actor_identifier,policy_version,reason_code,event_payload,previous_event_hash,event_hash)
                    VALUES (%s,NULL,'assessed_partial',%s,%s,'pilot_back_assessment',%s::jsonb,NULL,%s)
                    RETURNING event_id""", (knowledge_id,actor.strip(),policy,json.dumps(event_payload),event_hash))
                event_id = cursor.fetchone()[0]
        self.send_json(HTTPStatus.CREATED, {"knowledge_id": knowledge_id, "assurance_level": assessment["level"], "assurance_state": assessment["state"], "assessment_event_id": event_id})

    def handle_sdas_consumption(self) -> None:
        request = self.request_json()
        if not request or not persistence_enabled():
            self.send_json(HTTPStatus.BAD_REQUEST, {"error": "invalid_consumption_request"}); return
        ids = request.get("knowledge_ids")
        required_strings = ("consumer_id", "purpose_class", "outcome_class", "retrieval_policy_version", "provenance_set_fingerprint", "output_fingerprint", "idempotency_key")
        if (not isinstance(ids, list) or not ids or len(ids) > 10 or len(set(ids)) != len(ids)
                or any(not is_hex64(value) for value in ids)
                or any(not isinstance(request.get(name), str) or not request[name].strip() for name in required_strings)
                or request["outcome_class"] not in {"grounded_answer", "insufficient_certified_evidence", "retrieval_only"}
                or any(not is_hex64(request[name]) for name in ("provenance_set_fingerprint", "output_fingerprint", "idempotency_key"))):
            self.send_json(HTTPStatus.BAD_REQUEST, {"error": "invalid_consumption_request"}); return
        threshold = request.get("retrieval_threshold")
        if not isinstance(threshold, (int, float)) or threshold < 0 or threshold > 1:
            self.send_json(HTTPStatus.BAD_REQUEST, {"error": "invalid_consumption_request"}); return
        inserted = 0
        with database_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT knowledge_id FROM ingestion.certified_knowledge_items WHERE knowledge_id = ANY(%s) AND lifecycle_state='certified'", (ids,))
                if {row[0] for row in cursor.fetchall()} != set(ids):
                    self.send_json(HTTPStatus.NOT_FOUND, {"error": "certified_knowledge_not_found"}); return
                for knowledge_id in sorted(ids):
                    cursor.execute("SELECT event_hash FROM ingestion.sdas_consumption_events WHERE knowledge_id=%s ORDER BY event_id DESC LIMIT 1", (knowledge_id,))
                    previous = (cursor.fetchone() or [None])[0]
                    event_payload = {"consumer_id": request["consumer_id"].strip(), "purpose_class": request["purpose_class"].strip(), "outcome_class": request["outcome_class"], "policy": request["retrieval_policy_version"].strip(), "threshold": float(threshold), "provenance_set_fingerprint": request["provenance_set_fingerprint"], "output_fingerprint": request["output_fingerprint"], "idempotency_key": request["idempotency_key"]}
                    event_hash = chained_event_hash(previous, knowledge_id, "consumed", request["retrieval_policy_version"].strip(), event_payload)
                    cursor.execute("""INSERT INTO ingestion.sdas_consumption_events
                      (knowledge_id,consumer_identifier,purpose_class,outcome_class,retrieval_policy_version,retrieval_threshold,provenance_set_fingerprint,output_fingerprint,idempotency_key,previous_event_hash,event_hash)
                      VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (knowledge_id,idempotency_key) DO NOTHING RETURNING event_id""",
                      (knowledge_id,request["consumer_id"].strip(),request["purpose_class"].strip(),request["outcome_class"],request["retrieval_policy_version"].strip(),threshold,request["provenance_set_fingerprint"],request["output_fingerprint"],request["idempotency_key"],previous,event_hash))
                    inserted += int(cursor.fetchone() is not None)
        status = HTTPStatus.CREATED if inserted else HTTPStatus.CONFLICT
        self.send_json(status, {"knowledge_count": len(ids), "inserted": inserted, "disposition": "consumption_recorded" if inserted else "duplicate_consumption"})

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


def evaluate_sdas_policy(*, policy_enabled: bool, policy_effective: bool,
                         source_type_allowed: bool, data_class_allowed: bool,
                         source_authority_verified: bool, acquisition_present: bool,
                         transformation_present: bool, integrity_valid: bool,
                         validation_passed: bool, duplicate: bool,
                         conflict: bool) -> tuple[str, list[str]]:
    """Deterministic SDAS v0.2 policy decision; never performs certification.

    The caller supplies only persisted facts.  A missing/ambiguous authority
    fact routes to accountable Human Review, never to policy auto-approval.
    """
    if not policy_enabled or not policy_effective:
        return "reject_or_quarantine", ["policy_disabled_or_expired"]
    if duplicate:
        return "reject_or_quarantine", ["duplicate_detected"]
    if not integrity_valid or not validation_passed:
        return "reject_or_quarantine", ["integrity_or_validation_failed"]
    if not source_type_allowed or not data_class_allowed:
        return "human_required", ["outside_policy_scope"]
    if conflict:
        return "human_required", ["evidence_conflict"]
    missing = []
    if not source_authority_verified:
        missing.append("authority_not_verified")
    if not acquisition_present:
        missing.append("acquisition_evidence_missing")
    if not transformation_present:
        missing.append("transformation_evidence_missing")
    if missing:
        return "human_required", missing
    return "policy_automatic", ["all_required_policy_evidence_present"]


def evaluate_sdas_governance_bootstrap_policy(*, delegation_active: bool, **policy_facts: bool) -> tuple[str, list[str]]:
    """Apply the SDAS v0.3 bootstrap gate before normal policy evaluation.

    A policy-model approval or pending proposal is not operational authority.
    Only an append-only lifecycle state of ``ACTIVE`` may permit the underlying
    LOW-risk evaluator to consider ``policy_automatic``. This function never
    certifies a record.
    """
    if not delegation_active:
        return "human_required", ["delegation_not_active"]
    return evaluate_sdas_policy(**policy_facts)


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
