"""Read-only extraction for the selected real-data pilot subset.

Raw document text and relative source paths are written only to a caller-supplied
runtime location outside the repository. Standard output is a non-sensitive
aggregate summary suitable for later sanitization.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from collections import Counter, deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from xml.etree import ElementTree


ALLOWED_EXTENSIONS = {".pdf", ".xlsx"}
STATUS_PATTERN = re.compile(r"progress|status|monthly|weekly|report|پیشرفت|وضعیت|ماهانه|هفتگی|گزارش", re.I)


def utc_iso(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp, timezone.utc).isoformat()


def content_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_reparse(path: Path) -> bool:
    return bool(getattr(path.stat(), "st_file_attributes", 0) & 0x400)


def discover_selected_subset(root: Path) -> Path:
    """Resolve the user-selected metadata candidate without emitting a source path."""
    queue: deque[tuple[Path, int | None]] = deque([(root, None)])
    candidates: list[dict[str, Any]] = []
    while queue:
        directory, active_candidate = queue.popleft()
        try:
            children = list(directory.iterdir())
        except OSError:
            continue
        for child in children:
            try:
                if child.is_dir():
                    child_candidate = active_candidate
                    if STATUS_PATTERN.search(child.name):
                        candidates.append({"path": child, "count": 0, "bytes": 0, "extensions": Counter()})
                        child_candidate = len(candidates) - 1
                    if not is_reparse(child):
                        queue.append((child, child_candidate))
                elif active_candidate is not None and child.suffix.lower() in ALLOWED_EXTENSIONS:
                    candidate = candidates[active_candidate]
                    candidate["count"] += 1
                    candidate["bytes"] += child.stat().st_size
                    candidate["extensions"][child.suffix.lower()] += 1
            except OSError:
                continue
    selected = [
        candidate for candidate in candidates
        if candidate["count"] == 19
        and candidate["bytes"] == 23606611
        and candidate["extensions"] == Counter({".pdf": 18, ".xlsx": 1})
    ]
    if len(selected) != 1:
        raise RuntimeError("selected metadata candidate could not be resolved")
    return selected[0]["path"]


def selected_files(selected: Path) -> list[Path]:
    queue: deque[Path] = deque([selected])
    files: list[Path] = []
    while queue:
        directory = queue.popleft()
        try:
            children = list(directory.iterdir())
        except OSError as error:
            raise RuntimeError("selected subset enumeration failed") from error
        for child in children:
            try:
                if child.is_dir():
                    if not is_reparse(child):
                        queue.append(child)
                elif child.suffix.lower() in ALLOWED_EXTENSIONS:
                    files.append(child)
            except OSError:
                continue
    return files


def extract_pdf(path: Path) -> tuple[str, dict[str, Any]]:
    executable = shutil.which("pdftotext")
    if executable is None:
        raise RuntimeError("pdftotext is unavailable")
    completed = subprocess.run(
        [executable, "-enc", "UTF-8", "-layout", str(path), "-"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=60,
    )
    if completed.returncode != 0:
        raise RuntimeError("pdf_text_extraction_failed")
    return completed.stdout.decode("utf-8", errors="replace"), {"method": "pdftotext_utf8_layout"}


def extract_xlsx(path: Path) -> tuple[str, dict[str, Any]]:
    namespace = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with zipfile.ZipFile(path) as archive:
        shared: list[str] = []
        if "xl/sharedStrings.xml" in archive.namelist():
            shared_root = ElementTree.fromstring(archive.read("xl/sharedStrings.xml"))
            shared = ["".join(node.itertext()) for node in shared_root.findall("main:si", namespace)]
        sheets = sorted(name for name in archive.namelist() if re.fullmatch(r"xl/worksheets/sheet\d+\.xml", name))
        extracted: list[str] = []
        for sheet in sheets:
            root = ElementTree.fromstring(archive.read(sheet))
            values: list[str] = []
            for cell in root.findall(".//main:c", namespace):
                value = cell.find("main:v", namespace)
                if value is None or value.text is None:
                    continue
                if cell.attrib.get("t") == "s":
                    try:
                        values.append(shared[int(value.text)])
                    except (IndexError, ValueError):
                        values.append(value.text)
                else:
                    values.append(value.text)
            extracted.append(f"{sheet}:\n" + "\n".join(values))
    return "\n\n".join(extracted), {"method": "xlsx_ooxml_values", "sheet_count": len(sheets)}


def sensitivity_categories(text: str) -> list[str]:
    findings: list[str] = []
    if re.search(r"\b\d{10}\b", text):
        findings.append("possible_national_identifier")
    if re.search(r"\b\+?\d[\d\s-]{8,}\b", text):
        findings.append("possible_phone_number")
    if re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", text):
        findings.append("email_address")
    return findings


def main() -> int:
    root_value = os.environ.get("EAI_PILOT_ROOT")
    output_value = os.environ.get("EAI_RUNTIME_OUTPUT")
    if not root_value or not output_value:
        raise SystemExit("EAI_PILOT_ROOT and EAI_RUNTIME_OUTPUT are required")
    root = Path(root_value)
    selected_override = os.environ.get("EAI_SELECTED_SUBSET_ROOT")
    selected = Path(selected_override) if selected_override else discover_selected_subset(root)
    files = selected_files(selected)
    files.sort(key=lambda item: item.relative_to(selected).as_posix())
    extensions = Counter(path.suffix.lower() for path in files)
    if len(files) != 19 or sum(path.stat().st_size for path in files) != 23606611 or extensions != Counter({".pdf": 18, ".xlsx": 1}):
        raise SystemExit("selected subset no longer matches approved metadata boundary")

    records: list[dict[str, Any]] = []
    failures: Counter[str] = Counter()
    sensitive: Counter[str] = Counter()
    for path in files:
        try:
            if path.suffix.lower() == ".pdf":
                text, extraction = extract_pdf(path)
            else:
                text, extraction = extract_xlsx(path)
            flags = sensitivity_categories(text)
            sensitive.update(flags)
            records.append({
                "source_alias": "status_candidate_b",
                "source_relative_reference": path.relative_to(selected).as_posix(),
                "source_timestamp_utc": utc_iso(path.stat().st_mtime),
                "content_fingerprint": content_hash(path),
                "document_type": path.suffix.lower(),
                "extraction": extraction,
                "text": text,
                "sensitivity_categories": flags,
            })
        except (OSError, RuntimeError, subprocess.TimeoutExpired, zipfile.BadZipFile, ElementTree.ParseError) as error:
            failures[type(error).__name__] += 1
    output = Path(output_value)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"records": records}, ensure_ascii=False), encoding="utf-8")
    summary = {
        "source_alias": "status_candidate_b",
        "approved_document_count": len(files),
        "extracted_document_count": len(records),
        "extraction_failure_count": sum(failures.values()),
        "failure_categories": dict(sorted(failures.items())),
        "document_type_distribution": dict(sorted(extensions.items())),
        "unique_content_fingerprint_count": len({record["content_fingerprint"] for record in records}),
        "sensitivity_category_counts": dict(sorted(sensitive.items())),
        "raw_content_output_outside_git": True,
        "source_modified": False,
    }
    print(json.dumps(summary, ensure_ascii=False, separators=(",", ":")))
    return 0 if len(records) == len(files) else 1


if __name__ == "__main__":
    raise SystemExit(main())
