#!/usr/bin/env python3
"""Run the exact post-A1 selected-series submission gate for ST1-136.

This combines:
- ST1-136 supplement verification
- deterministic merge onto the preserved ST1-135 A1 partial bundle
- ST1-125 selected-series bundle gate
- optional ST1-131 selected-series native-record gate
- optional ST1-132 dual-input gate
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


def run_json(command: list[str]) -> tuple[int, dict | None, str]:
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    payload = result.stdout.strip() or result.stderr.strip()
    parsed = None
    if payload:
        try:
            parsed = json.loads(payload)
        except json.JSONDecodeError:
            parsed = None
    return result.returncode, parsed, payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-bundle", type=Path, required=True, help="Path to the preserved ST1-135 A1 partial bundle")
    parser.add_argument("--supplement", type=Path, required=True, help="Path to the ST1-136 remaining-input supplement")
    parser.add_argument("--native-record", type=Path, help="Optional selected-series native-record JSON")
    args = parser.parse_args()

    supplement_check = [sys.executable, "scripts/verify_st1_136_remaining_inputs_supplement.py", "--supplement", str(args.supplement)]

    with tempfile.TemporaryDirectory(prefix="st1-136-") as tmp_dir:
        merged_path = Path(tmp_dir) / "merged_bundle.json"
        merge_cmd = [
            sys.executable,
            "scripts/apply_st1_136_remaining_selected_series_inputs.py",
            "--base-bundle", str(args.base_bundle),
            "--supplement", str(args.supplement),
            "--output", str(merged_path),
        ]
        supplement_code, supplement_json, supplement_text = run_json(supplement_check)
        merge_code, merge_json, merge_text = run_json(merge_cmd)

        bundle_code = bundle_json = None
        bundle_text = ""
        if merge_code == 0:
            bundle_code, bundle_json, bundle_text = run_json(
                [sys.executable, "scripts/run_st1_125_series_bundle_gate.py", "--bundle", str(merged_path)]
            )

        native_code = native_json = None
        native_text = ""
        dual_code = dual_json = None
        dual_text = ""
        if args.native_record is not None:
            native_code, native_json, native_text = run_json(
                [sys.executable, "scripts/verify_st1_131_selected_series_native_record.py", "--native-record", str(args.native_record)]
            )
            if merge_code == 0:
                dual_code, dual_json, dual_text = run_json(
                    [
                        sys.executable,
                        "scripts/run_st1_132_selected_series_dual_input_gate.py",
                        "--bundle", str(merged_path),
                        "--native-record", str(args.native_record),
                    ]
                )

        output = {
            "task_id": "ST1-136",
            "base_bundle_path": str(args.base_bundle),
            "supplement_path": str(args.supplement),
            "native_record_path": str(args.native_record) if args.native_record else None,
            "supplement_verification": {
                "exit_code": supplement_code,
                "result": supplement_json if supplement_json is not None else supplement_text,
            },
            "merge_result": {
                "exit_code": merge_code,
                "result": merge_json if merge_json is not None else merge_text,
            },
            "bundle_gate": {
                "exit_code": bundle_code,
                "result": bundle_json if bundle_json is not None else bundle_text,
            } if merge_code == 0 else None,
            "native_record_gate": {
                "exit_code": native_code,
                "result": native_json if native_json is not None else native_text,
            } if args.native_record is not None else None,
            "dual_input_gate": {
                "exit_code": dual_code,
                "result": dual_json if dual_json is not None else dual_text,
            } if dual_code is not None else None,
            "boundary": {
                "real_delegation_activation": False,
                "real_source_registration": False,
                "real_native_acquisition": False,
                "real_policy_mutation": False,
                "real_certification": False,
                "st1_061_is_success_target": False,
            },
        }
        print(json.dumps(output, sort_keys=True, separators=(",", ":"), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
