#!/usr/bin/env python3
"""Compile a deterministic handoff from verified external evidence to dossier-ready inputs.

This compiler is local-only and non-mutating. It translates the selected-class
external evidence bundle plus native-record metadata into dossier-ready input
shapes without ad-hoc manual reinterpretation.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from validate_st1_078_real_evidence_bundle import CANDIDATE_CLASS_ID, PERMITTED_FACTS, PROJECT_SCOPE


ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT_SCRIPT = ROOT / "scripts" / "verify_st1_083_first_native_record_preflight.py"


def run_json(script: Path, args: list[str]) -> dict[str, object]:
    result = subprocess.run([sys.executable, str(script), *args], capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True, help="Path to ST1-078 bundle JSON")
    parser.add_argument("--native-record", type=Path, required=True, help="Path to ST1-083 native-record JSON")
    args = parser.parse_args()

    preflight = run_json(
        PREFLIGHT_SCRIPT,
        ["--bundle", str(args.bundle), "--native-record", str(args.native_record)],
    )
    bundle = load_json(args.bundle)
    native_record = load_json(args.native_record)

    if preflight.get("ready_for_real_runtime_attempt") is not True:
        output = {
            "schema_version": "st1-094-external-evidence-to-dossier-handoff-v1",
            "candidate_class_id": CANDIDATE_CLASS_ID,
            "project_scope": PROJECT_SCOPE,
            "handoff_status": "BLOCKED_DOSSIER_HANDOFF",
            "blocking_reasons": {
                "preflight_result": preflight.get("preflight_result"),
                "bundle_readiness": preflight.get("bundle_readiness", {}).get("status"),
                "native_record_readiness": preflight.get("native_record_readiness", {}).get("status"),
                "bundle_errors": preflight.get("bundle_readiness", {}).get("errors", []),
                "native_record_errors": preflight.get("native_record_readiness", {}).get("errors", []),
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

    source_registration = native_record["source_registration"]
    business_time = native_record["business_time"]
    acquisition = native_record["acquisition"]
    transformation = native_record["transformation"]
    evidence_items = bundle["evidence_items"]

    output = {
        "schema_version": "st1-094-external-evidence-to-dossier-handoff-v1",
        "candidate_class_id": CANDIDATE_CLASS_ID,
        "project_scope": PROJECT_SCOPE,
        "handoff_status": "READY_DOSSIER_HANDOFF",
        "verified_external_evidence_summary": {
            "bundle_readiness": preflight["bundle_readiness"]["status"],
            "native_record_readiness": preflight["native_record_readiness"]["status"],
            "source_id": source_registration["source_id"],
            "report_class": source_registration["report_class"],
            "report_period_value": business_time["report_period_value"],
            "resolution_source": business_time["resolution_source"],
        },
        "dossier_ready_inputs": {
            "bundle_reference": str(args.bundle).replace("\\", "/"),
            "native_record_reference": str(args.native_record).replace("\\", "/"),
            "derived_operator_inputs_template": {
                "candidate_class_id": CANDIDATE_CLASS_ID,
                "project_scope": PROJECT_SCOPE,
                "accountable_actor_id": "RUNTIME_REQUIRED_INPUT_FROM_VERIFIED_EVIDENCE",
                "bundle_fingerprints": {
                    "A1": evidence_items["A1"]["signed_artifact_fingerprint"],
                    "A2": evidence_items["A2"]["signed_artifact_fingerprint"],
                    "A3": evidence_items["A3"]["signed_artifact_fingerprint"],
                },
                "record_id": "RUNTIME_REQUIRED_INPUT",
                "observed_at": "RUNTIME_REQUIRED_INPUT",
                "fact_payload": {
                    "fact_class": "RUNTIME_REQUIRED_INPUT_FROM_ALLOWED_SET",
                    "fact_value": "RUNTIME_REQUIRED_INPUT",
                    "source_id": source_registration["source_id"],
                    "report_period_value": business_time["report_period_value"],
                },
                "runtime_gate_assertions": {
                    "bundle_independently_verified": True,
                    "native_record_independently_verified": True,
                    "exact_scope_reconfirmed": True,
                    "hard_stop_before_certification_acknowledged": True,
                    "automatic_certification_requested": False,
                },
            },
            "receipt_contract_expectations": {
                "expected_source_id": source_registration["source_id"],
                "expected_fact_classes": sorted(PERMITTED_FACTS),
                "expected_policy_id": native_record["policy_context"]["policy_id"],
                "expected_policy_version": native_record["policy_context"]["policy_version"],
                "expected_risk_tier": native_record["policy_context"]["risk_tier"],
            },
            "native_evidence_chain": {
                "original_fingerprint": acquisition["original_fingerprint"],
                "transformation_output_fingerprint": transformation["output_fingerprint"],
                "source_reference": acquisition["source_reference"],
                "acquisition_method": acquisition["acquisition_method"],
                "read_only_acquisition": acquisition["read_only"],
            },
            "remaining_runtime_only_fields": [
                "accountable_actor_id",
                "record_id",
                "observed_at",
                "fact_class",
                "fact_value",
                "runtime receipt after actual execution",
                "batch routing input only if exception-queue simulation is needed for the same run",
            ],
        },
        "boundaries": {
            "real_delegation_activated": False,
            "real_source_registered": False,
            "real_file_acquired": False,
            "real_record_ingested": False,
            "real_policy_decision_executed": False,
            "real_certification_performed": False,
            "trust_boundary_changed": False,
        },
    }
    print(json.dumps(output, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
