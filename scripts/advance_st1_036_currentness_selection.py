#!/usr/bin/env python3
"""Exclude the insufficient ST1-036 boundary and select the next local candidate."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from collections import Counter
from pathlib import Path


CUTOFF = "2023-09-23T00:00:00Z"


def runtime(name: str) -> Path:
    return Path(os.environ["LOCALAPPDATA"]) / "EnterpriseAI" / "runtime" / name


def main() -> int:
    spec = importlib.util.spec_from_file_location("metadata_index", Path(__file__).with_name("index_pilot_metadata.py"))
    if spec is None or spec.loader is None:
        raise RuntimeError("metadata index module is unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    current = json.loads(runtime("st1-036-selection-manifest.json").read_text(encoding="utf-8"))
    raw = json.loads(runtime("st1-028-excluded-locators.json").read_text(encoding="utf-8-sig"))
    excluded = set(raw if isinstance(raw, list) else raw.get("excluded_relative_locators", []))
    excluded.add(current["relative_locator"])
    runtime("st1-028-excluded-locators.json").write_text(json.dumps(sorted(excluded), ensure_ascii=False, indent=2), encoding="utf-8")
    conn = module.connect(runtime("pilot_metadata_index.sqlite"))
    try:
        choices = module.query(conn, excluded, CUTOFF)
        if not choices["top_candidates"]:
            print(json.dumps({"candidate_count": 0, "new_smb_traversal": False}, separators=(",", ":")))
            return 2
        candidate = choices["top_candidates"][0]
        base = Path(candidate["relative_locator"])
        files = []
        rows = conn.execute("SELECT relative_locator,parent_relative_locator,filename,extension,size_bytes,modified_utc FROM files WHERE enumeration_status='enumerated'")
        for relative, parent, filename, extension, size, modified in rows:
            if extension not in module.ALLOWED_EXTENSIONS or not modified or modified < CUTOFF:
                continue
            if not (parent == candidate["relative_locator"] or parent.startswith(candidate["relative_locator"] + "/")):
                continue
            if not any(module.normalized(term) in module.normalized(parent + "/" + filename) for term in module.STATUS_TERMS):
                continue
            files.append({"relative_locator": str(Path(relative).relative_to(base)), "extension": extension, "size_bytes": size})
    finally:
        conn.close()
    files.sort(key=lambda item: item["relative_locator"].casefold())
    distribution = dict(sorted(Counter(item["extension"] for item in files).items()))
    if len(files) != candidate["document_count"] or distribution != candidate["extension_distribution"] or sum(int(item["size_bytes"]) for item in files) != candidate["aggregate_size_bytes"]:
        raise RuntimeError("candidate signature did not reproduce")
    alias = "metadata-" + hashlib.sha256(candidate["relative_locator"].encode("utf-8")).hexdigest()[:16]
    manifest = {"alias": alias, "relative_locator": candidate["relative_locator"], "files": files, "selection_signature": {"document_count": len(files), "extension_distribution": distribution, "aggregate_size_bytes": candidate["aggregate_size_bytes"]}}
    runtime("st1-037-selection-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"candidate_count": choices["candidate_count"], "selection_alias": alias, **manifest["selection_signature"], "new_smb_traversal": False, "manifest_written_outside_git": True}, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
