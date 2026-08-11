#!/usr/bin/env python3
"""Run the full ST1-125 series-bundle gate without activating any authority.

This combines:
- ST1-078 structural validation
- ST1-078 readiness assessment
- ST1-124 exact selected-series alignment verification

It is local-only, additive, and non-destructive.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def run_json_command(command: list[str]) -> tuple[int, dict | None, str]:
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    stdout = result.stdout.strip()
    stderr = result.stderr.strip()
    payload_text = stdout or stderr
    parsed = None
    if payload_text:
      try:
          parsed = json.loads(payload_text)
      except json.JSONDecodeError:
          parsed = None
    return result.returncode, parsed, payload_text


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True, help="Path to the series-scoped bundle JSON file")
    args = parser.parse_args()

    validate_cmd = [sys.executable, "scripts/validate_st1_078_real_evidence_bundle.py", "--bundle", str(args.bundle)]
    assess_cmd = [sys.executable, "scripts/assess_st1_078_real_evidence_bundle.py", "--bundle", str(args.bundle)]
    series_cmd = [sys.executable, "scripts/verify_st1_124_recurring_workbook_governance_bundle.py", "--bundle", str(args.bundle)]

    validate_code, validate_json, validate_text = run_json_command(validate_cmd)
    assess_code, assess_json, assess_text = run_json_command(assess_cmd)
    series_code, series_json, series_text = run_json_command(series_cmd)

    output = {
        "task_id": "ST1-125",
        "bundle_path": str(args.bundle),
        "structural_validation": {
            "exit_code": validate_code,
            "result": validate_json if validate_json is not None else validate_text,
        },
        "readiness_assessment": {
            "exit_code": assess_code,
            "result": assess_json if assess_json is not None else assess_text,
        },
        "series_alignment_verification": {
            "exit_code": series_code,
            "result": series_json if series_json is not None else series_text,
        },
        "gate_summary": {
            "structurally_complete": validate_code == 0,
            "activation_readiness": assess_json.get("activation_readiness") if isinstance(assess_json, dict) else None,
            "selected_series_match": (
                isinstance(series_json, dict)
                and series_json.get("selected_target", {}).get("target_source_id")
                == "maroon_project_controls_progress_workbook_series"
            ),
            "real_delegation_activation": False,
            "real_source_registration": False,
            "real_certification": False,
            "st1_061_is_success_target": False,
        },
    }
    print(json.dumps(output, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
