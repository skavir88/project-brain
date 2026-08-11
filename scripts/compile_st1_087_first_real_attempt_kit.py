#!/usr/bin/env python3
"""Compile a submission-ready non-secret operator kit for the first real attempt.

This compiler is local-only and non-mutating. It packages the existing:
- ST1-083 preflight
- ST1-084 dry-run planner
- ST1-085 execution manifest
- ST1-086 operator handoff

into one deterministic artifact set suitable for immediate use when real
verified evidence arrives.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HANDOFF_SCRIPT = ROOT / "scripts" / "generate_st1_086_operator_handoff.py"
MANIFEST_SCRIPT = ROOT / "scripts" / "compile_st1_085_first_real_attempt_manifest.py"
DRY_RUN_SCRIPT = ROOT / "scripts" / "plan_st1_084_first_real_runtime_attempt.py"
PREFLIGHT_SCRIPT = ROOT / "scripts" / "verify_st1_083_first_native_record_preflight.py"


def run_json(script: Path, bundle: Path, native_record: Path | None) -> dict[str, object]:
    command = [sys.executable, str(script), "--bundle", str(bundle)]
    if native_record is not None:
        command.extend(["--native-record", str(native_record)])
    result = subprocess.run(command, text=True, capture_output=True, check=True)
    return json.loads(result.stdout)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True, help="Path to the ST1-078 bundle JSON file")
    parser.add_argument("--native-record", type=Path, help="Path to the native-record metadata JSON file")
    args = parser.parse_args()

    preflight = run_json(PREFLIGHT_SCRIPT, args.bundle, args.native_record)
    dry_run = run_json(DRY_RUN_SCRIPT, args.bundle, args.native_record)
    manifest = run_json(MANIFEST_SCRIPT, args.bundle, args.native_record)
    handoff = run_json(HANDOFF_SCRIPT, args.bundle, args.native_record)

    ready = (
        preflight.get("ready_for_real_runtime_attempt") is True
        and dry_run.get("planner_result") == "READY_DRY_RUN_PLAN"
        and manifest.get("compiler_result") == "READY_EXECUTION_MANIFEST"
        and handoff.get("handoff", {}).get("checklist_status") == "READY_OPERATOR_HANDOFF"
    )

    output: dict[str, object] = {
        "schema_version": "st1-087-first-real-attempt-operator-kit-v1",
        "candidate_class_id": preflight["candidate_class_id"],
        "project_scope": preflight["project_scope"],
        "kit_status": "READY_OPERATOR_KIT" if ready else "BLOCKED_OPERATOR_KIT",
        "runtime_mutation_performed": False,
        "components": {
            "preflight": preflight,
            "dry_run": dry_run,
            "execution_manifest": manifest,
            "operator_handoff": handoff,
        },
        "kit_summary": {
            "contains_secret_values": False,
            "ordered_runtime_step_count": len(manifest.get("execution_manifest", [])),
            "required_operator_inputs": manifest.get("manifest_summary", {}).get("requires_runtime_operator_inputs", []),
            "hard_stops": dry_run.get("hard_stops", []),
            "primary_blockers": handoff.get("handoff", {}).get("blocking_conditions", []),
            "evidence_artifacts_required_before_real_run": [
                "independently verified ST1-078 evidence bundle",
                "independently verified native-record metadata artifact",
            ],
        },
    }
    print(json.dumps(output, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
