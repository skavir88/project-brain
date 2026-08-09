#!/usr/bin/env python3
"""Read-only extraction of the clearly status-oriented ST1-022 candidate series.

Source locators, document contents, and cell values remain in workstation-local
runtime state. Repository output is limited to sanitized aggregate evidence.
"""

from __future__ import annotations

import argparse
import json
import os
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

from extract_st1_019_status_corpus import PILOT_ROOT, sha256_file, xlsx_segments


def runtime(name: str) -> Path:
    base = Path(os.environ["LOCALAPPDATA"]) / "EnterpriseAI" / "runtime"
    base.mkdir(parents=True, exist_ok=True)
    return base / name


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract the selected ST1-022 status-oriented XLSX series locally.")
    parser.add_argument("--alias", default="status_oriented_candidate_3")
    parser.add_argument("--discovery", type=Path, default=runtime("st1-018-status-discovery.json"))
    parser.add_argument("--output", type=Path, default=runtime("st1-022-dated-status-extraction.json"))
    args = parser.parse_args()
    discovery = json.loads(args.discovery.read_text(encoding="utf-8"))
    candidate = next((x for x in discovery["top_candidates"] if x["alias"] == args.alias), None)
    if not candidate:
        raise RuntimeError("approved status candidate is absent from local discovery state")
    files = candidate["files"]
    distribution = Counter(x["extension"].lower() for x in files)
    total = sum(int(x["size_bytes"]) for x in files)
    if candidate["labels"] != ["project_status"] or distribution != {".xlsx": 10} or len(files) != 10:
        raise RuntimeError("candidate does not match the approved bounded project-status series")
    subset = Path(PILOT_ROOT) / candidate["relative_locator"]
    if not subset.is_dir():
        raise RuntimeError("runtime-local bounded locator is unavailable; no extraction attempted")
    documents = []
    for item in files:
        source = subset / item["relative_locator"]
        if not source.is_file() or source.stat().st_size != int(item["size_bytes"]):
            raise RuntimeError("selected source no longer matches discovery metadata; extraction halted")
        segments = xlsx_segments(source)
        documents.append({"source_relative_locator": item["relative_locator"], "size_bytes": item["size_bytes"], "sha256": sha256_file(source), "segments": segments})
    output = {
        "schema_version": "st1-022-extraction-v1",
        "generated_utc": datetime.now(UTC).isoformat(),
        "selection_alias": args.alias,
        "selection_signature": {"document_count": len(files), "extension_distribution": dict(distribution), "aggregate_size_bytes": total},
        "documents": documents,
        "aggregate": {"non_empty_cell_count": sum(len(x["segments"]) for x in documents), "workbook_count": len(documents)},
    }
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"selection_alias": args.alias, "workbook_count": len(documents), "non_empty_cell_count": output["aggregate"]["non_empty_cell_count"], "output_written_outside_git": True}, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
