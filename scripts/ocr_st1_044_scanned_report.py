#!/usr/bin/env python3
"""OCR the single higher-quality ST1-044 scanned report, page by page.

It reads only the approved runtime-local source alias, renders pages to a
temporary local directory, and stores OCR text/provenance only in runtime
state. It intentionally avoids the same-period alternate scan, archives, and
XLSB file.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tempfile
from datetime import UTC, datetime
from pathlib import Path


TARGET_ALIAS = "source-6fcc3a7e7c915aee"


def runtime(name: str) -> Path:
    return Path(os.environ["LOCALAPPDATA"]) / "EnterpriseAI" / "runtime" / name


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--input", type=Path, default=runtime("st1-044-management-report-extraction.json"))
    parser.add_argument("--output", type=Path, default=runtime("st1-044-management-report-ocr.json"))
    parser.add_argument("--tesseract", type=Path, required=True)
    parser.add_argument("--tessdata", type=Path, required=True)
    parser.add_argument("--pdftoppm", type=Path, required=True)
    parser.add_argument("--dpi", type=int, default=200)
    parser.add_argument("--first-page", type=int, default=1)
    parser.add_argument("--last-page", type=int, help="inclusive; defaults to the report page count")
    args = parser.parse_args()
    if not args.root.is_dir() or not args.input.is_file() or not args.tesseract.is_file() or not (args.tessdata / "fas.traineddata").is_file() or not args.pdftoppm.is_file():
        raise SystemExit("required local OCR input is unavailable")
    extraction = json.loads(args.input.read_text(encoding="utf-8"))
    item = next((x for x in extraction["documents"] if x["source_alias"] == TARGET_ALIAS), None)
    if item is None or item.get("kind") != "pdf" or item.get("extraction_status") != "extracted":
        raise SystemExit("approved scanned report is unavailable or was not extracted")
    source = args.root / item["relative_locator"]
    if not source.is_file() or source.stat().st_size != item["indexed_size_bytes"]:
        raise SystemExit("approved scanned report failed revalidation")
    first_page = args.first_page
    last_page = args.last_page or item["page_count"]
    if first_page < 1 or last_page < first_page or last_page > item["page_count"]:
        raise SystemExit("invalid requested page range")
    with tempfile.TemporaryDirectory(prefix="enterprise-ai-st1-044-ocr-") as temp:
        temp_dir = Path(temp)
        prefix = temp_dir / "report"
        subprocess.run([str(args.pdftoppm), "-f", str(first_page), "-l", str(last_page), "-r", str(args.dpi), "-png", str(source), str(prefix)], check=True, capture_output=True, timeout=180)
        images = sorted(temp_dir.glob("report-*.png"), key=lambda x: int(x.stem.rsplit("-", 1)[1]))
        if len(images) != (last_page - first_page + 1):
            raise RuntimeError("rendered page count does not match requested page range")
        pages = []
        for image in images:
            number = int(image.stem.rsplit("-", 1)[1])
            completed = subprocess.run([str(args.tesseract), str(image), "stdout", "-l", "fas", "--tessdata-dir", str(args.tessdata)], check=True, capture_output=True, timeout=120)
            pages.append({"page": number, "text": completed.stdout.decode("utf-8", errors="replace")})
    existing_pages = []
    if args.output.is_file():
        prior = json.loads(args.output.read_text(encoding="utf-8"))
        if prior.get("source_alias") != TARGET_ALIAS:
            raise RuntimeError("existing OCR output does not match this source")
        existing_pages = [x for x in prior.get("pages", []) if not (first_page <= x["page"] <= last_page)]
    merged_pages = sorted(existing_pages + pages, key=lambda x: x["page"])
    payload = {
        "schema_version": "st1-044-management-report-ocr-v1",
        "generated_utc": datetime.now(UTC).isoformat(),
        "source_alias": TARGET_ALIAS,
        "page_count": item["page_count"],
        "ocr_page_count": len(merged_pages),
        "pages": merged_pages,
        "completed_page_ranges": [[first_page, last_page]],
        "boundaries": {
            "read_only": True,
            "single_approved_source": True,
            "alternate_same_period_scan_opened": False,
            "archives_opened": False,
            "xlsb_opened": False,
            "external_model_use": False,
            "platform_persistence": False,
            "raw_output_outside_git": True,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"source_alias": TARGET_ALIAS, "pages_ocr_this_run": len(pages), "pages_ocr_total": len(merged_pages), "requested_range": [first_page,last_page], "output_outside_git": True}, separators=(",", ":")))


if __name__ == "__main__":
    raise SystemExit(main())
