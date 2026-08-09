#!/usr/bin/env python3
"""Perform bounded local Persian/English OCR for scanned ST1-040 PDF probes.

It uses the already installed local Tesseract executable and local `fas` data.
Rendered pages and extracted text are runtime-only and must not be versioned.
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


KEYWORDS = [
    "progress", "planned", "actual", "schedule", "delay", "risk", "issue", "milestone", "procurement", "engineering", "construction", "action", "management",
    "پیشرفت", "برنامه", "واقعی", "زمانبندی", "تاخیر", "تأخیر", "ریسک", "مسئله", "اقدام", "تدارکات", "مهندسی", "ساخت", "مدیریت",
]


def runtime(name: str) -> Path:
    return Path(os.environ["LOCALAPPDATA"]) / "EnterpriseAI" / "runtime" / name


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--probes", type=Path, default=runtime("st1-040-content-probes.json"))
    parser.add_argument("--output", type=Path, default=runtime("st1-040-pdf-ocr-probes.json"))
    parser.add_argument("--max-pages", type=int, default=8)
    parser.add_argument("--max-targets", type=int, help="bound the number of PDFs; metadata ordering is a probe selection aid only")
    parser.add_argument("--tesseract", type=Path, required=True)
    parser.add_argument("--tessdata", type=Path, required=True)
    parser.add_argument("--pdftoppm", type=Path, default=Path("pdftoppm"))
    args = parser.parse_args()
    if not args.root.is_dir() or not args.probes.is_file() or not args.tesseract.is_file() or not (args.tessdata / "fas.traineddata").is_file():
        raise SystemExit("required local OCR input is unavailable")
    probes = json.loads(args.probes.read_text(encoding="utf-8"))["probes"]
    targets = [item for item in probes if item.get("probe_status") == "extracted" and item.get("kind") == "pdf" and not item.get("keyword_signals")]
    targets.sort(key=lambda item: ((item["file"].get("modified_utc") or ""), item["file"]["relative_locator"].casefold()), reverse=True)
    if args.max_targets:
        targets = targets[:args.max_targets]
    results = []
    with tempfile.TemporaryDirectory(prefix="enterprise-ai-st1-040-ocr-") as temp:
        temp_dir = Path(temp)
        for index, item in enumerate(targets):
            source = args.root / item["file"]["relative_locator"]
            prefix = temp_dir / f"probe-{index}"
            result = {"family_locator": item["family_locator"], "file": item["file"], "status": "unknown"}
            try:
                poppler_args = ["-f", "1", "-l", str(args.max_pages), "-r", "200", "-png", str(source), str(prefix)]
                # The Codex runtime supplies Poppler through a Windows .cmd
                # wrapper, which must be invoked through cmd.exe.
                poppler_command = (["cmd.exe", "/c", str(args.pdftoppm), *poppler_args] if args.pdftoppm.suffix.casefold() == ".cmd" else [str(args.pdftoppm), *poppler_args])
                subprocess.run(poppler_command, check=True, capture_output=True, timeout=90)
                pages = sorted(temp_dir.glob(f"{prefix.name}-*.png"))
                page_text = []
                for page in pages:
                    # The local private tessdata directory intentionally holds
                    # Persian only; do not mix it with the system directory.
                    completed = subprocess.run([str(args.tesseract), str(page), "stdout", "-l", "fas", "--tessdata-dir", str(args.tessdata)], check=True, capture_output=True, timeout=90)
                    page_text.append(completed.stdout.decode("utf-8", errors="replace"))
                text = "\n".join(page_text)
                lower = text.casefold()
                result.update({"status": "ocr_extracted", "pages_ocr": len(pages), "keyword_signals": [term for term in KEYWORDS if term.casefold() in lower], "sample_text": text[:80000]})
            except Exception as exc:
                result.update({"status": "error", "error_type": type(exc).__name__})
            results.append(result)
    payload = {"schema_version": "st1-040-pdf-ocr-probes-v1", "generated_utc": datetime.now(UTC).isoformat(), "results": results, "boundaries": {"read_only": True, "max_pages_per_pdf": args.max_pages, "local_tesseract_languages": ["fas"], "external_model_use": False, "platform_persistence": False, "raw_output_outside_git": True}}
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"targets": len(targets), "ocr_extracted": sum(x["status"] == "ocr_extracted" for x in results), "errors": sum(x["status"] == "error" for x in results), "output_outside_git": True}, separators=(",", ":")))


if __name__ == "__main__":
    main()
