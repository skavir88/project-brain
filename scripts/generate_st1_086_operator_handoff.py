#!/usr/bin/env python3
"""Generate a concise operator readiness checklist for the first real attempt.

This generator is local-only and non-mutating. It composes:
1. the ST1-083 preflight,
2. the ST1-084 dry-run planner, and
3. the ST1-085 execution manifest,

into a concise operator-facing handoff/checklist artifact.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_SCRIPT = ROOT / "scripts" / "compile_st1_085_first_real_attempt_manifest.py"


def run_manifest(bundle: Path, native_record: Path | None) -> dict[str, object]:
    command = [sys.executable, str(MANIFEST_SCRIPT), "--bundle", str(bundle)]
    if native_record is not None:
        command.extend(["--native-record", str(native_record)])
    result = subprocess.run(command, text=True, capture_output=True, check=True)
    return json.loads(result.stdout)


def blocked_checklist(manifest: dict[str, object]) -> dict[str, object]:
    preflight = manifest["dry_run_plan"]["preflight"]
    return {
        "checklist_status": "BLOCKED_OPERATOR_HANDOFF",
        "operator_may_start_runtime_mutation": False,
        "blocking_conditions": [
            {
                "gate": "preflight_not_ready",
                "bundle_readiness": preflight["bundle_readiness"]["status"],
                "native_record_readiness": preflight["native_record_readiness"]["status"],
                "native_record_errors": preflight["native_record_readiness"]["errors"],
            }
        ],
        "hard_stops": manifest["dry_run_plan"]["hard_stops"],
    }


def ready_checklist(manifest: dict[str, object]) -> dict[str, object]:
    summary = manifest["manifest_summary"]
    execution_manifest = manifest["execution_manifest"]
    return {
        "checklist_status": "READY_OPERATOR_HANDOFF",
        "operator_may_start_runtime_mutation": True,
        "prerequisites_confirmed": [
            "bundle_readiness = PENDING_INDEPENDENT_VERIFICATION",
            "native_record_readiness = READY_FOR_FIRST_REAL_RUNTIME_ATTEMPT",
            "dry_run_plan = READY_DRY_RUN_PLAN",
            "execution_manifest = READY_EXECUTION_MANIFEST",
        ],
        "operator_must_supply_before_runtime": summary["requires_runtime_operator_inputs"],
        "ordered_runtime_actions": [
            {
                "sequence": step["sequence"],
                "target": step["target"],
                "purpose": step["purpose"],
                "must_match_manifest_payload_shape": True,
            }
            for step in execution_manifest
        ],
        "must_verify_immediately_before_step_1": [
            "verified bundle artifacts remain the exact approved class and project scope",
            "the native record still uses the approved workbook-level reporting-period source",
            "no automatic certification request has been introduced",
            "no secret values are being copied into repository artifacts",
        ],
        "must_stop_if_any_of_the_following_is_false": [
            "exact-scope active delegation is not actually present at runtime",
            "business-time evidence no longer matches the approved workbook rule",
            "native acquisition or transformation continuity is incomplete",
            "record intake does not return certification_candidate",
            "policy decision cannot truthfully remain policy_automatic under exact controls",
        ],
        "hard_stops": summary["hard_stops"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True, help="Path to the ST1-078 bundle JSON file")
    parser.add_argument("--native-record", type=Path, help="Path to the native-record metadata JSON file")
    args = parser.parse_args()

    manifest = run_manifest(args.bundle, args.native_record)
    ready = manifest["compiler_result"] == "READY_EXECUTION_MANIFEST"
    output = {
        "schema_version": "st1-086-first-real-run-operator-handoff-v1",
        "candidate_class_id": manifest["candidate_class_id"],
        "project_scope": manifest["project_scope"],
        "runtime_mutation_performed": False,
        "source_artifacts": {
            "preflight_schema": manifest["dry_run_plan"]["preflight"]["schema_version"],
            "dry_run_schema": manifest["dry_run_plan"]["schema_version"],
            "manifest_schema": manifest["schema_version"],
        },
        "handoff": ready_checklist(manifest) if ready else blocked_checklist(manifest),
    }
    print(json.dumps(output, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
