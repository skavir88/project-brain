#!/usr/bin/env python3
"""Merge the ST1-136 remaining-input supplement onto the ST1-135 A1 bundle.

This is local-only and non-destructive. It helps the next real submission use
the already-captured A1 evidence while adding only A2/A3/source-registration/
stable-series-id inputs.
"""

from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path


TARGET_SOURCE_ID = "maroon_project_controls_progress_workbook_series"


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"FAIL: file not found: {path}", file=sys.stderr)
        raise SystemExit(2)
    except json.JSONDecodeError as exc:
        print(f"FAIL: invalid JSON in {path}: {exc.msg}", file=sys.stderr)
        raise SystemExit(2)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-bundle", type=Path, required=True, help="Path to the ST1-135 A1 partial bundle JSON")
    parser.add_argument("--supplement", type=Path, required=True, help="Path to the ST1-136 remaining-input supplement JSON")
    parser.add_argument("--output", type=Path, required=True, help="Path to write the merged bundle JSON")
    args = parser.parse_args()

    base = load_json(args.base_bundle)
    supplement = load_json(args.supplement)

    if supplement.get("target_source_id") != TARGET_SOURCE_ID:
        print("FAIL: supplement.target_source_id does not match the selected series", file=sys.stderr)
        return 2
    if base.get("source_registration", {}).get("source_id") != TARGET_SOURCE_ID:
        print("FAIL: base bundle is not the expected selected-series A1 bundle", file=sys.stderr)
        return 2

    merged = deepcopy(base)
    merged.setdefault("evidence_items", {})
    merged["evidence_items"]["A2"] = supplement["evidence_items"]["A2"]
    merged["evidence_items"]["A3"] = supplement["evidence_items"]["A3"]

    merged.setdefault("source_registration", {})
    merged["source_registration"]["non_sensitive_location_class"] = supplement["source_registration"]["non_sensitive_location_class"]
    merged["source_registration"]["owning_role_class"] = supplement["source_registration"]["owning_role_class"]
    merged["source_registration"]["evidence_reference"] = supplement["source_registration"]["evidence_reference"]

    merged.setdefault("series_scope", {})
    merged["series_scope"]["stable_source_series_identifier"] = supplement["series_scope"]["stable_source_series_identifier"]
    merged["series_scope"]["stable_source_series_identifier_kind"] = supplement["series_scope"]["stable_source_series_identifier_kind"]

    args.output.write_text(json.dumps(merged, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "task_id": "ST1-136",
                "merge_result": "OK",
                "selected_target_source_id": TARGET_SOURCE_ID,
                "output_path": str(args.output),
                "a1_preserved": True,
                "merged_sections": ["A2", "A3", "source_registration", "series_scope"],
            },
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
