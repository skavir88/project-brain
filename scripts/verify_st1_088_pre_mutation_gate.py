#!/usr/bin/env python3
"""Deterministically verify pre-mutation readiness for the first real runtime attempt.

This gate is local-only and non-mutating. It sits immediately before the first
runtime write sequence and combines:

- ST1-078 bundle structural validity
- ST1-083 native-record readiness
- ST1-087 operator-kit readiness
- explicit operator-supplied runtime inputs

It never activates authority, registers a source, acquires a file, ingests a
record, or certifies anything.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

from validate_st1_078_real_evidence_bundle import CANDIDATE_CLASS_ID, PERMITTED_FACTS, PROJECT_SCOPE


ROOT = Path(__file__).resolve().parents[1]
KIT_SCRIPT = ROOT / "scripts" / "compile_st1_087_first_real_attempt_kit.py"
HEX_64 = re.compile(r"^[0-9a-f]{64}$")
ACTOR_ID_RE = re.compile(r"^[A-Za-z0-9._:@/-]{3,128}$")


def run_kit(bundle: Path, native_record: Path | None) -> dict[str, object]:
    command = [sys.executable, str(KIT_SCRIPT), "--bundle", str(bundle)]
    if native_record is not None:
        command.extend(["--native-record", str(native_record)])
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def is_sha256(value: object) -> bool:
    return isinstance(value, str) and HEX_64.fullmatch(value) is not None


def load_json(path: Path | None, missing_label: str) -> tuple[dict[str, object], list[str]]:
    if path is None:
        return {}, [f"{missing_label} not supplied"]
    try:
        return json.loads(path.read_text(encoding="utf-8")), []
    except FileNotFoundError:
        return {}, [f"{missing_label} file not found: {path}"]
    except json.JSONDecodeError as exc:
        return {}, [f"{missing_label} invalid JSON: {exc.msg}"]


def require_nonempty_str(errors: list[str], obj: dict[str, object], key: str, context: str) -> str | None:
    value = obj.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{context}.{key} must be a non-empty string")
        return None
    return value.strip()


def require_bool(errors: list[str], obj: dict[str, object], key: str, expected: bool, context: str) -> None:
    if obj.get(key) is not expected:
        errors.append(f"{context}.{key} must be {str(expected).lower()}")


def validate_operator_inputs(path: Path | None, expected_source_id: object, expected_report_period: object) -> tuple[str, list[str], dict[str, object]]:
    operator_inputs, load_errors = load_json(path, "operator_inputs")
    if load_errors:
        return "BLOCKED_OPERATOR_INPUTS_MISSING", load_errors, {}

    errors: list[str] = []
    required_sections = {
        "candidate_class_id",
        "project_scope",
        "accountable_actor_id",
        "bundle_fingerprints",
        "record_id",
        "observed_at",
        "fact_payload",
        "runtime_gate_assertions",
    }
    missing = sorted(required_sections - set(operator_inputs))
    if missing:
        errors.append(f"operator_inputs missing required sections: {', '.join(missing)}")

    if operator_inputs.get("candidate_class_id") != CANDIDATE_CLASS_ID:
        errors.append("operator_inputs.candidate_class_id mismatch")
    if operator_inputs.get("project_scope") != PROJECT_SCOPE:
        errors.append("operator_inputs.project_scope mismatch")

    actor_id = require_nonempty_str(errors, operator_inputs, "accountable_actor_id", "operator_inputs")
    if actor_id is not None and ACTOR_ID_RE.fullmatch(actor_id) is None:
        errors.append("operator_inputs.accountable_actor_id must use a stable non-secret identifier format")

    record_id = require_nonempty_str(errors, operator_inputs, "record_id", "operator_inputs")
    observed_at = require_nonempty_str(errors, operator_inputs, "observed_at", "operator_inputs")
    if record_id is not None and record_id.startswith("RUNTIME_"):
        errors.append("operator_inputs.record_id must not be a placeholder value")
    if observed_at is not None and observed_at.startswith("RUNTIME_"):
        errors.append("operator_inputs.observed_at must not be a placeholder value")

    bundle_fingerprints = operator_inputs.get("bundle_fingerprints")
    if not isinstance(bundle_fingerprints, dict):
        errors.append("operator_inputs.bundle_fingerprints must be an object")
        bundle_fingerprints = {}
    expected_fingerprint_keys = {"A1", "A2", "A3"}
    if set(bundle_fingerprints) != expected_fingerprint_keys:
        errors.append("operator_inputs.bundle_fingerprints must contain exactly A1, A2, and A3")
    for key in sorted(expected_fingerprint_keys):
        if not is_sha256(bundle_fingerprints.get(key)):
            errors.append(f"operator_inputs.bundle_fingerprints.{key} must be a lowercase sha256 hex string")

    fact_payload = operator_inputs.get("fact_payload")
    if not isinstance(fact_payload, dict):
        errors.append("operator_inputs.fact_payload must be an object")
        fact_payload = {}
    fact_class = require_nonempty_str(errors, fact_payload, "fact_class", "operator_inputs.fact_payload")
    if fact_class is not None and fact_class not in PERMITTED_FACTS:
        errors.append("operator_inputs.fact_payload.fact_class must remain inside the approved low-risk fact classes")
    require_nonempty_str(errors, fact_payload, "fact_value", "operator_inputs.fact_payload")
    report_period_value = require_nonempty_str(errors, fact_payload, "report_period_value", "operator_inputs.fact_payload")
    source_id = require_nonempty_str(errors, fact_payload, "source_id", "operator_inputs.fact_payload")
    if source_id is not None and source_id != expected_source_id:
        errors.append("operator_inputs.fact_payload.source_id must match native source_registration.source_id")
    if report_period_value is not None and report_period_value != expected_report_period:
        errors.append("operator_inputs.fact_payload.report_period_value must match native business_time.report_period_value")

    runtime_gate_assertions = operator_inputs.get("runtime_gate_assertions")
    if not isinstance(runtime_gate_assertions, dict):
        errors.append("operator_inputs.runtime_gate_assertions must be an object")
        runtime_gate_assertions = {}
    for key in (
        "bundle_independently_verified",
        "native_record_independently_verified",
        "exact_scope_reconfirmed",
        "hard_stop_before_certification_acknowledged",
        "automatic_certification_requested",
    ):
        if key == "automatic_certification_requested":
            require_bool(errors, runtime_gate_assertions, key, False, "operator_inputs.runtime_gate_assertions")
        else:
            require_bool(errors, runtime_gate_assertions, key, True, "operator_inputs.runtime_gate_assertions")

    if errors:
        if any(item.startswith("operator_inputs.fact_payload.") for item in errors):
            return "BLOCKED_FACT_PAYLOAD_INVALID", errors, operator_inputs
        return "BLOCKED_OPERATOR_INPUTS_INVALID", errors, operator_inputs

    return "READY_OPERATOR_INPUTS", [], operator_inputs


def summarize_reason_codes(kit_status: str, operator_status: str, operator_errors: list[str], kit_blockers: list[object]) -> list[str]:
    reason_codes: list[str] = []
    if kit_status != "READY_OPERATOR_KIT":
        reason_codes.append("operator_kit_not_ready")
    if operator_status == "BLOCKED_OPERATOR_INPUTS_MISSING":
        reason_codes.append("operator_inputs_missing")
    elif operator_status == "BLOCKED_OPERATOR_INPUTS_INVALID":
        reason_codes.append("operator_inputs_invalid")
    elif operator_status == "BLOCKED_FACT_PAYLOAD_INVALID":
        reason_codes.append("fact_payload_invalid")
    if any("automatic_certification_requested" in item for item in operator_errors):
        reason_codes.append("automatic_certification_not_allowed")
    if any("exact_scope" in item or "candidate_class_id" in item or "project_scope" in item for item in operator_errors):
        reason_codes.append("exact_scope_mismatch")
    if any("report_period_value" in item for item in operator_errors):
        reason_codes.append("business_time_mismatch")
    if kit_blockers and "operator_kit_not_ready" not in reason_codes:
        reason_codes.append("upstream_preflight_blocked")
    return sorted(set(reason_codes))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True, help="Path to the ST1-078 bundle JSON file")
    parser.add_argument("--native-record", type=Path, help="Path to the ST1-083 native-record JSON file")
    parser.add_argument("--operator-inputs", type=Path, help="Path to the ST1-088 operator-input JSON file")
    args = parser.parse_args()

    kit = run_kit(args.bundle, args.native_record)
    kit_status = kit.get("kit_status")
    preflight = kit.get("components", {}).get("preflight", {})
    expected_source_id = preflight.get("native_record_summary", {}).get("source_id")
    expected_report_period = preflight.get("native_record_summary", {}).get("resolution_source")
    native_payload, _ = load_json(args.native_record, "native_record")
    if native_payload:
        expected_report_period = native_payload.get("business_time", {}).get("report_period_value", expected_report_period)

    operator_status, operator_errors, operator_inputs = validate_operator_inputs(
        args.operator_inputs,
        expected_source_id,
        expected_report_period,
    )

    ready = kit_status == "READY_OPERATOR_KIT" and operator_status == "READY_OPERATOR_INPUTS"
    kit_blockers = kit.get("kit_summary", {}).get("primary_blockers", [])
    reason_codes = summarize_reason_codes(str(kit_status), operator_status, operator_errors, kit_blockers if isinstance(kit_blockers, list) else [])

    output = {
        "schema_version": "st1-088-pre-mutation-gate-v1",
        "candidate_class_id": CANDIDATE_CLASS_ID,
        "project_scope": PROJECT_SCOPE,
        "gate_result": "GO_FOR_FIRST_RUNTIME_MUTATION" if ready else "NO_GO_FOR_RUNTIME_MUTATION",
        "kit_status": kit_status,
        "operator_inputs_status": operator_status,
        "reason_codes": reason_codes,
        "kit_summary": {
            "ordered_runtime_step_count": kit.get("kit_summary", {}).get("ordered_runtime_step_count"),
            "required_operator_inputs": kit.get("kit_summary", {}).get("required_operator_inputs"),
            "hard_stops": kit.get("kit_summary", {}).get("hard_stops"),
            "primary_blockers": kit_blockers,
        },
        "operator_inputs_summary": {
            "accountable_actor_id": operator_inputs.get("accountable_actor_id") if operator_inputs else None,
            "record_id": operator_inputs.get("record_id") if operator_inputs else None,
            "fact_class": operator_inputs.get("fact_payload", {}).get("fact_class") if operator_inputs else None,
            "report_period_value": operator_inputs.get("fact_payload", {}).get("report_period_value") if operator_inputs else None,
            "errors": operator_errors,
        },
        "boundaries": {
            "real_delegation_activated": False,
            "real_source_registered": False,
            "real_file_acquired": False,
            "real_record_ingested": False,
            "real_policy_decision_executed": False,
            "real_certification_performed": False,
        },
    }
    print(json.dumps(output, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
