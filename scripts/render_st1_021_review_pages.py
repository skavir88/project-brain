#!/usr/bin/env python3
"""Render the three bounded ST1-021 PDF review pages locally for visual table review."""

from __future__ import annotations

import json
import os
from pathlib import Path

import fitz  # type: ignore

PILOT_ROOT = r"\\172.20.190.4\pns\06- طرح ها و پروژهها\0624 پروژه ايستگاه مارون 3 و 5 و رامشير"
TARGETS = {
    "change_log": ("PNS - Change management-robati Rev00.pdf", 2),
    "financial_ipc": ("1-TOTAL.pdf", 39),
    "site_support": ("1-TOTAL.pdf", 36),
}


def main() -> int:
    runtime = Path(os.environ["LOCALAPPDATA"]) / "EnterpriseAI" / "runtime"
    discovery = json.loads((runtime / "st1-018-status-discovery.json").read_text(encoding="utf-8"))
    candidate = next(x for x in discovery["top_candidates"] if x["alias"] == "status_oriented_candidate_1")
    available = {entry["relative_locator"]: entry for entry in candidate["files"]}
    output_dir = runtime / "st1-021-visual-review"
    output_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for safe_name, (relative, page_number) in TARGETS.items():
        if relative not in available:
            raise RuntimeError("expected selected file is absent")
        source = Path(PILOT_ROOT) / candidate["relative_locator"] / relative
        if not source.is_file():
            raise RuntimeError("bounded selected source is unavailable")
        document = fitz.open(source)
        if page_number > len(document):
            raise RuntimeError("requested page is out of range")
        image = document[page_number - 1].get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
        target = output_dir / f"{safe_name}-page-{page_number}.png"
        image.save(target)
        document.close()
        written.append(target.name)
    print(json.dumps({"rendered_page_count": len(written), "output_directory_outside_git": True, "artifacts": written}))
    return 0


if __name__ == "__main__":
    import json
    raise SystemExit(main())
