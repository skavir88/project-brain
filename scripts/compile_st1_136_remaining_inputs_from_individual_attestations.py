#!/usr/bin/env python3
"""Compile an ST1-136 supplement from individual A2 and A3 attestation artifacts.

This is local-only and non-destructive. It lets the next real-world submission
arrive as independent A2/A3 attestations plus a few source-registration fields,
then compiles them into the exact ST1-136 supplement shape.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


TARGET_SOURCE_ID = "maroon_project_controls_progress_workbook_series"
PROJECT_SCOPE = "maroon_pilot"


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"FAIL: file not found: {path}", file=sys.stderr)
        raise SystemExit(2)
    except json.JSONDecodeError as exc:
        print(f"FAIL: invalid JSON in {path}: {exc.msg}", file=sys.stderr)
        raise SystemExit(2)


def require_attestation(payload: dict, expected_version: str, expected_kind: str, label: str) -> dict:
    if payload.get("attestation_version") != expected_version:
        print(f"FAIL: {label}.attestation_version must be {expected_version}", file=sys.stderr)
        raise SystemExit(2)
    if payload.get("project_scope") != PROJECT_SCOPE:
        print(f"FAIL: {label}.project_scope must be {PROJECT_SCOPE}", file=sys.stderr)
        raise SystemExit(2)
    if payload.get("target_source_id") != TARGET_SOURCE_ID:
        print(f"FAIL: {label}.target_source_id must be {TARGET_SOURCE_ID}", file=sys.stderr)
        raise SystemExit(2)
    evidence = payload.get("evidence_item")
    if not isinstance(evidence, dict):
        print(f"FAIL: {label}.evidence_item must be an object", file=sys.stderr)
        raise SystemExit(2)
    if evidence.get("attestation_kind") != expected_kind:
        print(f"FAIL: {label}.evidence_item.attestation_kind must be {expected_kind}", file=sys.stderr)
        raise SystemExit(2)
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--a2", type=Path, required=True, help="Path to ST1-136 A2 attestation JSON")
    parser.add_argument("--a3", type=Path, required=True, help="Path to ST1-136 A3 attestation JSON")
    parser.add_argument("--stable-source-series-identifier", required=True, help="Stable non-sensitive series identifier")
    parser.add_argument("--stable-source-series-identifier-kind", required=True, help="Kind of stable series identifier")
    parser.add_argument("--non-sensitive-location-class", required=True, help="Non-sensitive source location class")
    parser.add_argument("--source-owning-role-class", required=True, help="Owning role class for the selected source series")
    parser.add_argument("--source-evidence-reference", required=True, help="Stable non-sensitive source-registration evidence reference")
    parser.add_argument("--output", type=Path, required=True, help="Output ST1-136 supplement path")
    args = parser.parse_args()

    a2_payload = load_json(args.a2)
    a3_payload = load_json(args.a3)
    a2_evidence = require_attestation(a2_payload, "st1-136-a2/v1", "project_controls_accountability", "a2")
    a3_evidence = require_attestation(a3_payload, "st1-136-a3/v1", "controlled_report_definition", "a3")

    supplement = {
        "supplement_version": "st1-136/v1",
        "project_scope": PROJECT_SCOPE,
        "target_source_id": TARGET_SOURCE_ID,
        "series_scope": {
            "stable_source_series_identifier": args.stable_source_series_identifier,
            "stable_source_series_identifier_kind": args.stable_source_series_identifier_kind,
        },
        "evidence_items": {
            "A2": a2_evidence,
            "A3": a3_evidence,
        },
        "source_registration": {
            "non_sensitive_location_class": args.non_sensitive_location_class,
            "owning_role_class": args.source_owning_role_class,
            "evidence_reference": args.source_evidence_reference,
        },
    }

    args.output.write_text(json.dumps(supplement, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "task_id": "ST1-136",
        "compile_result": "OK",
        "output_path": str(args.output),
        "selected_target_source_id": TARGET_SOURCE_ID,
        "inputs": {
            "a2_path": str(args.a2),
            "a3_path": str(args.a3),
        },
    }, sort_keys=True, separators=(",", ":"), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
