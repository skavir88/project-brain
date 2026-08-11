#!/usr/bin/env python3
"""Verify ST1-083 first-native-record readiness for the selected class.

This verifier is local-only and non-destructive. It combines:

1. ST1-078 bundle structural/readiness assessment; and
2. first native-record metadata readiness for the selected workbook class.

It never activates a delegation, registers a source, acquires a real file,
ingests a record, or certifies anything.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from assess_st1_078_real_evidence_bundle import readiness_from_statuses
from validate_st1_078_real_evidence_bundle import (
    CANDIDATE_CLASS_ID,
    EXPECTED_REPORTING_SOURCES,
    PROJECT_SCOPE,
    collect_validation_errors,
    load_bundle,
)


HEX_64 = re.compile(r"^[0-9a-f]{64}$")
ALLOWED_MEDIA_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}
READY = "READY_FOR_FIRST_REAL_RUNTIME_ATTEMPT"


def is_sha256(value: object) -> bool:
    return isinstance(value, str) and HEX_64.fullmatch(value) is not None


def require_nonempty_str(errors: list[str], obj: dict[str, object], key: str, context: str) -> None:
    value = obj.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{context}.{key} must be a non-empty string")


def require_bool(errors: list[str], obj: dict[str, object], key: str, expected: bool, context: str) -> None:
    if obj.get(key) is not expected:
        errors.append(f"{context}.{key} must be {str(expected).lower()}")


def validate_native_record(path: Path | None) -> tuple[str, list[str], dict[str, object]]:
    if path is None:
        return "BLOCKED_NATIVE_RECORD_METADATA_MISSING", ["native_record metadata not supplied"], {}
    try:
        native = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return "BLOCKED_NATIVE_RECORD_METADATA_MISSING", [f"native_record file not found: {path}"], {}
    except json.JSONDecodeError as exc:
        return "BLOCKED_NATIVE_RECORD_METADATA_INVALID", [f"native_record invalid JSON: {exc.msg}"], {}

    errors: list[str] = []
    top_required = {
        "candidate_class_id",
        "project_scope",
        "source_registration",
        "acquisition",
        "transformation",
        "business_time",
        "policy_context",
        "independent_verification",
    }
    missing = sorted(top_required - set(native))
    if missing:
        errors.append(f"native_record missing required sections: {', '.join(missing)}")

    if native.get("candidate_class_id") != CANDIDATE_CLASS_ID:
        errors.append("native_record.candidate_class_id mismatch")
    if native.get("project_scope") != PROJECT_SCOPE:
        errors.append("native_record.project_scope mismatch")

    source_registration = native.get("source_registration")
    if not isinstance(source_registration, dict):
        errors.append("source_registration must be an object")
        source_registration = {}
    for key in ("source_id", "source_type", "non_sensitive_location_class", "owning_role_class", "evidence_reference"):
        require_nonempty_str(errors, source_registration, key, "source_registration")
    if source_registration.get("project_scope") != PROJECT_SCOPE:
        errors.append("source_registration.project_scope must be maroon_pilot")
    if source_registration.get("report_class") != CANDIDATE_CLASS_ID:
        errors.append("source_registration.report_class must be project_controls_progress_workbook")

    acquisition = native.get("acquisition")
    if not isinstance(acquisition, dict):
        errors.append("acquisition must be an object")
        acquisition = {}
    for key in ("acquired_at", "source_reference", "acquisition_method", "media_type"):
        require_nonempty_str(errors, acquisition, key, "acquisition")
    require_bool(errors, acquisition, "read_only", True, "acquisition")
    if not is_sha256(acquisition.get("original_fingerprint")):
        errors.append("acquisition.original_fingerprint must be a lowercase sha256 hex string")
    size_bytes = acquisition.get("size_bytes")
    if not isinstance(size_bytes, int) or size_bytes <= 0:
        errors.append("acquisition.size_bytes must be a positive integer")
    if acquisition.get("media_type") not in ALLOWED_MEDIA_TYPES:
        errors.append("acquisition.media_type must be one of the approved allowlisted document formats")

    transformation = native.get("transformation")
    if not isinstance(transformation, dict):
        errors.append("transformation must be an object")
        transformation = {}
    for key in ("tool_name", "tool_version", "transformed_at", "transformation_type"):
        require_nonempty_str(errors, transformation, key, "transformation")
    require_bool(errors, transformation, "deterministic", True, "transformation")
    require_bool(errors, transformation, "lineage_complete", True, "transformation")
    if not is_sha256(transformation.get("input_fingerprint")):
        errors.append("transformation.input_fingerprint must be a lowercase sha256 hex string")
    if not is_sha256(transformation.get("output_fingerprint")):
        errors.append("transformation.output_fingerprint must be a lowercase sha256 hex string")
    if transformation.get("input_fingerprint") != acquisition.get("original_fingerprint"):
        errors.append("transformation.input_fingerprint must match acquisition.original_fingerprint")

    business_time = native.get("business_time")
    if not isinstance(business_time, dict):
        errors.append("business_time must be an object")
        business_time = {}
    require_bool(errors, business_time, "resolved", True, "business_time")
    require_nonempty_str(errors, business_time, "resolution_source", "business_time")
    require_nonempty_str(errors, business_time, "report_period_value", "business_time")
    if business_time.get("resolution_source") not in EXPECTED_REPORTING_SOURCES:
        errors.append("business_time.resolution_source must use the approved workbook-level reporting-period rule")
    substitutes = business_time.get("disallowed_substitutes_used")
    if not isinstance(substitutes, list):
        errors.append("business_time.disallowed_substitutes_used must be a list")
    elif substitutes:
        errors.append("business_time.disallowed_substitutes_used must remain empty")

    policy_context = native.get("policy_context")
    if not isinstance(policy_context, dict):
        errors.append("policy_context must be an object")
        policy_context = {}
    if policy_context.get("policy_id") != "project-controls-progress-low-risk":
        errors.append("policy_context.policy_id must be project-controls-progress-low-risk")
    require_nonempty_str(errors, policy_context, "policy_version", "policy_context")
    if policy_context.get("risk_tier") != "LOW":
        errors.append("policy_context.risk_tier must be LOW")
    require_bool(errors, policy_context, "automatic_certification_requested", False, "policy_context")

    independent = native.get("independent_verification")
    if not isinstance(independent, dict):
        errors.append("independent_verification must be an object")
        independent = {}
    require_bool(errors, independent, "bundle_independently_verified", True, "independent_verification")
    require_bool(errors, independent, "source_control_independently_verified", True, "independent_verification")
    require_bool(errors, independent, "business_time_rule_independently_verified", True, "independent_verification")

    if errors:
        if any(item.startswith("business_time.") for item in errors):
            status = "BLOCKED_BUSINESS_TIME_RULE_INVALID"
        elif any(item.startswith("acquisition.") or item.startswith("transformation.") for item in errors):
            status = "BLOCKED_NATIVE_EVIDENCE_INCOMPLETE"
        else:
            status = "BLOCKED_NATIVE_RECORD_METADATA_INVALID"
    else:
        status = READY
    return status, errors, native


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True, help="Path to the ST1-078 bundle JSON file")
    parser.add_argument("--native-record", type=Path, help="Path to the first-native-record metadata JSON file")
    args = parser.parse_args()

    bundle = load_bundle(args.bundle)
    bundle_errors = collect_validation_errors(bundle)
    section_statuses = {"bundle": "PARTIAL", "A1": "PARTIAL", "A2": "PARTIAL", "A3": "PARTIAL", "source_registration": "PARTIAL"}
    if bundle_errors:
        # Preserve the established ST1-078 readiness semantics.
        section_statuses = {"bundle": "REJECTED", "A1": "MISSING", "A2": "MISSING", "A3": "MISSING", "source_registration": "MISSING"}
    bundle_readiness = readiness_from_statuses(section_statuses) if not bundle_errors else "WAITING_FOR_SCOPE_OR_POLICY_CORRECTION"

    native_status, native_errors, native_payload = validate_native_record(args.native_record)
    preflight_ready = bundle_readiness == "PENDING_INDEPENDENT_VERIFICATION" and native_status == READY
    output = {
        "schema_version": "st1-083-first-native-record-preflight-v1",
        "candidate_class_id": CANDIDATE_CLASS_ID,
        "project_scope": PROJECT_SCOPE,
        "bundle_readiness": {
            "status": bundle_readiness,
            "structural_validation_passed": len(bundle_errors) == 0,
            "errors": bundle_errors,
        },
        "native_record_readiness": {
            "status": native_status,
            "errors": native_errors,
        },
        "preflight_result": READY if preflight_ready else "BLOCKED",
        "ready_for_real_runtime_attempt": preflight_ready,
        "boundaries": {
            "real_delegation_activated": False,
            "real_source_registered": False,
            "real_file_acquired": False,
            "real_record_ingested": False,
            "real_certification_performed": False,
        },
        "native_record_summary": {
            "source_id": native_payload.get("source_registration", {}).get("source_id") if native_payload else None,
            "media_type": native_payload.get("acquisition", {}).get("media_type") if native_payload else None,
            "resolution_source": native_payload.get("business_time", {}).get("resolution_source") if native_payload else None,
        },
    }
    print(json.dumps(output, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
