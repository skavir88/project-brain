#!/usr/bin/env python3
"""Create the local-only ST1-036 extraction manifest from the metadata index.

The manifest deliberately remains outside Git because it contains source-relative
locators. Console output is aggregate-only and never prints a locator or name.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path


ALIAS = "metadata-695d19f1b3ce5979"
CUTOFF = "2023-09-23T00:00:00Z"


def runtime(name: str) -> Path:
    return Path(os.environ["LOCALAPPDATA"]) / "EnterpriseAI" / "runtime" / name


def main() -> int:
    module_path = Path(__file__).with_name("index_pilot_metadata.py")
    spec = importlib.util.spec_from_file_location("metadata_index", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("metadata index module is unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    raw_excluded = json.loads(runtime("st1-028-excluded-locators.json").read_text(encoding="utf-8-sig"))
    excluded = set(raw_excluded if isinstance(raw_excluded, list) else raw_excluded.get("excluded_relative_locators", []))
    conn = module.connect(runtime("pilot_metadata_index.sqlite"))
    try:
        matches = module.query(conn, excluded, CUTOFF)["top_candidates"]
        candidate = next((item for item in matches if hashlib.sha256(item["relative_locator"].encode("utf-8")).hexdigest()[:16] == ALIAS.removeprefix("metadata-")), None)
        if candidate is None:
            raise RuntimeError("selected metadata candidate is unavailable or changed")
        base = Path(candidate["relative_locator"])
        files = []
        rows = conn.execute("SELECT relative_locator,parent_relative_locator,filename,extension,size_bytes,modified_utc FROM files WHERE enumeration_status='enumerated'")
        for relative, parent, filename, extension, size, modified in rows:
            if extension not in module.ALLOWED_EXTENSIONS or not modified or modified < CUTOFF:
                continue
            if not (parent == candidate["relative_locator"] or parent.startswith(candidate["relative_locator"] + "/")):
                continue
            probe = module.normalized(parent + "/" + filename)
            if not any(module.normalized(term) in probe for term in module.STATUS_TERMS):
                continue
            source = Path(relative)
            try:
                local_relative = source.relative_to(base)
            except ValueError as exc:
                raise RuntimeError("candidate includes a file outside its selected boundary") from exc
            files.append({"relative_locator": str(local_relative), "extension": extension, "size_bytes": size})
    finally:
        conn.close()
    files.sort(key=lambda item: item["relative_locator"].casefold())
    observed_extensions: dict[str, int] = {}
    for item in files:
        observed_extensions[item["extension"]] = observed_extensions.get(item["extension"], 0) + 1
    if (len(files) != candidate["document_count"] or observed_extensions != candidate["extension_distribution"]
            or sum(int(item["size_bytes"]) for item in files) != candidate["aggregate_size_bytes"]):
        raise RuntimeError("runtime selection does not reproduce the approved metadata signature")
    manifest = {
        "alias": ALIAS,
        "relative_locator": candidate["relative_locator"],
        "files": files,
        "selection_signature": {
            "document_count": candidate["document_count"],
            "extension_distribution": candidate["extension_distribution"],
            "aggregate_size_bytes": candidate["aggregate_size_bytes"],
        },
    }
    destination = runtime("st1-036-selection-manifest.json")
    destination.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "selection_alias": ALIAS,
        "document_count": manifest["selection_signature"]["document_count"],
        "extension_distribution": manifest["selection_signature"]["extension_distribution"],
        "aggregate_size_bytes": manifest["selection_signature"]["aggregate_size_bytes"],
        "manifest_written_outside_git": True,
    }, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
