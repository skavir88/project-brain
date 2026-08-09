#!/usr/bin/env python3
"""Verify only the approved ST1-036 manifest paths before content extraction."""

from __future__ import annotations

import json
import os
from collections import Counter
from pathlib import Path

from extract_st1_019_status_corpus import PILOT_ROOT


def main() -> int:
    runtime = Path(os.environ["LOCALAPPDATA"]) / "EnterpriseAI" / "runtime"
    manifest = json.loads((runtime / "st1-036-selection-manifest.json").read_text(encoding="utf-8"))
    subset = Path(PILOT_ROOT) / manifest["relative_locator"]
    if not subset.is_dir():
        print(json.dumps({"selection_root_available": False, "files_checked": 0}, separators=(",", ":")))
        return 1
    observed = Counter()
    unavailable = Counter()
    for item in manifest["files"]:
        source = subset / item["relative_locator"]
        extension = item["extension"]
        if not source.is_file():
            unavailable["not_found"] += 1
        elif source.stat().st_size != int(item["size_bytes"]):
            unavailable["size_mismatch"] += 1
        else:
            observed[extension] += 1
    print(json.dumps({
        "selection_root_available": True,
        "files_checked": len(manifest["files"]),
        "stable_files": sum(observed.values()),
        "stable_extension_distribution": dict(sorted(observed.items())),
        "unavailable_or_changed": dict(sorted(unavailable.items())),
        "content_opened": False,
        "new_smb_traversal": False,
    }, separators=(",", ":")))
    return 0 if not unavailable else 2


if __name__ == "__main__":
    raise SystemExit(main())
