#!/usr/bin/env python3
"""Freeze the available subset of the already approved ST1-036 corpus locally."""

from __future__ import annotations

import json
import os
import argparse
from collections import Counter
from pathlib import Path

from extract_st1_019_status_corpus import PILOT_ROOT


def main() -> int:
    runtime = Path(os.environ["LOCALAPPDATA"]) / "EnterpriseAI" / "runtime"
    parser = argparse.ArgumentParser(description="Freeze a stable subset of an approved local selection manifest.")
    parser.add_argument("--source-manifest", type=Path, default=runtime / "st1-036-selection-manifest.json")
    parser.add_argument("--output", type=Path, default=runtime / "st1-036-stable-selection-manifest.json")
    args = parser.parse_args()
    manifest = json.loads(args.source_manifest.read_text(encoding="utf-8"))
    subset = Path(PILOT_ROOT) / manifest["relative_locator"]
    stable = []
    for item in manifest["files"]:
        source = subset / item["relative_locator"]
        if source.is_file() and source.stat().st_size == int(item["size_bytes"]):
            stable.append(item)
    stable.sort(key=lambda item: item["relative_locator"].casefold())
    extensions = dict(sorted(Counter(item["extension"] for item in stable).items()))
    stable_manifest = {
        "alias": manifest["alias"] + "-stable",
        "relative_locator": manifest["relative_locator"],
        "files": stable,
        "selection_signature": {
            "document_count": len(stable),
            "extension_distribution": extensions,
            "aggregate_size_bytes": sum(int(item["size_bytes"]) for item in stable),
        },
        "coverage_limitation": "47 of the originally approved 58 files were unavailable at bounded revalidation",
    }
    args.output.write_text(json.dumps(stable_manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "selection_alias": stable_manifest["alias"],
        **stable_manifest["selection_signature"],
        "manifest_written_outside_git": True,
    }, separators=(",", ":")))
    return 0 if stable else 1


if __name__ == "__main__":
    raise SystemExit(main())
