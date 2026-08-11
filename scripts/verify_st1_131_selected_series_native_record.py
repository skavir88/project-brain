#!/usr/bin/env python3
"""Verify selected-series native-record readiness for the ST1-122 target.

This wraps ST1-083 class-level native-record readiness with exact ST1-122 /
ST1-124 / ST1-125 selected-series boundary checks.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from verify_st1_083_first_native_record_preflight import validate_native_record


TARGET_SOURCE_ID = "maroon_project_controls_progress_workbook_series"
TARGET_SOURCE_ALIAS = "source-a08f4a79cf2116b1"
TARGET_FILENAME = "070-TWRP-24 1402-12-05.xlsx"
TARGET_PERIOD = "1402/11/21–1402/12/05"


def verify_series_scope(native: dict) -> tuple[str, list[str]]:
    scope = native.get("series_scope")
    if not isinstance(scope, dict):
        return "BLOCKED_SELECTED_SERIES_SCOPE_MISSING", ["series_scope must be supplied for the selected-series native-record path"]
    errors: list[str] = []
    if scope.get("target_source_id") != TARGET_SOURCE_ID:
        errors.append(f"series_scope.target_source_id must be {TARGET_SOURCE_ID}")
    if scope.get("representative_source_alias") != TARGET_SOURCE_ALIAS:
        errors.append(f"series_scope.representative_source_alias must be {TARGET_SOURCE_ALIAS}")
    if scope.get("representative_filename") != TARGET_FILENAME:
        errors.append(f"series_scope.representative_filename must be {TARGET_FILENAME}")
    if scope.get("observed_reporting_period_example") != TARGET_PERIOD:
        errors.append("series_scope.observed_reporting_period_example must preserve the approved selected-series example period")

    source_registration = native.get("source_registration", {})
    if source_registration.get("source_id") != TARGET_SOURCE_ID:
        errors.append(f"source_registration.source_id must be {TARGET_SOURCE_ID}")

    business_time = native.get("business_time", {})
    if business_time.get("report_period_value") != TARGET_PERIOD:
        errors.append("business_time.report_period_value must match the approved selected-series example period for this synthetic selected-series gate")

    if errors:
        return "BLOCKED_SELECTED_SERIES_SCOPE_INVALID", errors
    return "READY_FOR_SELECTED_SERIES_NATIVE_PATH", []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--native-record", type=Path, required=True, help="Path to the native-record JSON file")
    args = parser.parse_args()

    native_status, native_errors, native_payload = validate_native_record(args.native_record)
    series_status = "BLOCKED_SELECTED_SERIES_SCOPE_MISSING"
    series_errors: list[str] = []
    if native_payload:
        series_status, series_errors = verify_series_scope(native_payload)

    ready = native_status == "READY_FOR_FIRST_REAL_RUNTIME_ATTEMPT" and series_status == "READY_FOR_SELECTED_SERIES_NATIVE_PATH"
    output = {
        "task_id": "ST1-131",
        "native_record_path": str(args.native_record),
        "selected_target": {
            "target_source_id": TARGET_SOURCE_ID,
            "representative_source_alias": TARGET_SOURCE_ALIAS,
            "representative_filename": TARGET_FILENAME,
            "observed_reporting_period_example": TARGET_PERIOD,
        },
        "class_level_native_readiness": {
            "status": native_status,
            "errors": native_errors,
        },
        "selected_series_native_readiness": {
            "status": series_status,
            "errors": series_errors,
        },
        "ready_for_selected_series_runtime_path": ready,
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
