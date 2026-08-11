#!/usr/bin/env python3
"""Run the selected-series dual-input convergence gate for ST1-132.

This combines the exact selected-series bundle gate, the exact selected-series
native-record gate, and the independent-verification handoff into one truthful
local-only readiness surface.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def run_json(command: list[str]) -> dict:
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True, help="Path to the selected-series bundle JSON file")
    parser.add_argument("--native-record", type=Path, required=True, help="Path to the selected-series native-record JSON file")
    args = parser.parse_args()

    bundle_gate = run_json([sys.executable, "scripts/run_st1_125_series_bundle_gate.py", "--bundle", str(args.bundle)])
    native_gate = run_json([sys.executable, "scripts/verify_st1_131_selected_series_native_record.py", "--native-record", str(args.native_record)])

    bundle_ready = bundle_gate.get("gate_summary", {}).get("activation_readiness") == "PENDING_INDEPENDENT_VERIFICATION"
    native_ready = native_gate.get("ready_for_selected_series_runtime_path") is True

    handoff = None
    if bundle_ready:
        handoff = run_json(
            [
                sys.executable,
                "scripts/compile_st1_127_independent_verification_handoff.py",
                "--bundle",
                str(args.bundle),
            ]
        )

    output = {
        "task_id": "ST1-132",
        "bundle_path": str(args.bundle),
        "native_record_path": str(args.native_record),
        "bundle_gate": {
            "activation_readiness": bundle_gate.get("gate_summary", {}).get("activation_readiness"),
            "selected_series_match": bundle_gate.get("gate_summary", {}).get("selected_series_match"),
            "structurally_complete": bundle_gate.get("gate_summary", {}).get("structurally_complete"),
        },
        "native_record_gate": {
            "class_level_native_readiness": native_gate.get("class_level_native_readiness", {}).get("status"),
            "selected_series_native_readiness": native_gate.get("selected_series_native_readiness", {}).get("status"),
            "ready_for_selected_series_runtime_path": native_gate.get("ready_for_selected_series_runtime_path"),
        },
        "dual_input_status": {
            "bundle_ready_for_independent_review": bundle_ready,
            "native_record_ready_for_selected_series_runtime_path": native_ready,
            "can_begin_controlled_review": bundle_ready and native_ready,
            "next_truthful_step": (
                "begin_independent_controlled_review"
                if bundle_ready and native_ready
                else "wait_for_missing_or_invalid_selected_series_input"
            ),
        },
        "independent_review_handoff": handoff,
        "boundary": {
            "real_delegation_activation": False,
            "real_source_registration": False,
            "real_native_acquisition": False,
            "real_policy_mutation": False,
            "real_certification": False,
            "st1_061_is_success_target": False,
        },
    }
    print(json.dumps(output, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
