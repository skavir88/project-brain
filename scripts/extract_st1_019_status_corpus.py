#!/usr/bin/env python3
"""Read-only, local extraction for the explicitly selected ST1-019 corpus.

Raw source locators and extracted organizational content are deliberately written
only to the workstation runtime directory. Console output contains aggregates
only; this script never writes to the repository or modifies the SMB source.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from xml.etree import ElementTree as ET

EXPECTED_BY_ALIAS = {
    "status_oriented_candidate_1": ({".pdf": 7, ".docx": 4, ".xlsx": 7}, 18, 20_923_849),
    "status_oriented_candidate_2": ({".pdf": 15, ".docx": 1, ".xlsx": 5}, 21, 90_763_372),
}
PILOT_ROOT = r"\\172.20.190.4\pns\06- طرح ها و پروژهها\0624 پروژه ايستگاه مارون 3 و 5 و رامشير"
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
S = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
P = "{http://schemas.openxmlformats.org/package/2006/relationships}"


def runtime_file(name: str) -> Path:
    root = Path(os.environ["LOCALAPPDATA"]) / "EnterpriseAI" / "runtime"
    root.mkdir(parents=True, exist_ok=True)
    return root / name


def compact(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def docx_segments(path: Path) -> list[dict]:
    with zipfile.ZipFile(path) as archive:
        root = ET.fromstring(archive.read("word/document.xml"))
    segments: list[dict] = []
    paragraph_index = 0
    table_index = 0
    for child in root.find(f"{W}body"):
        if child.tag == f"{W}p":
            paragraph_index += 1
            text = compact("".join(child.itertext()))
            if text:
                segments.append({"location": f"paragraph:{paragraph_index}", "text": text})
        elif child.tag == f"{W}tbl":
            table_index += 1
            for row_index, row in enumerate(child.findall(f"{W}tr"), start=1):
                for cell_index, cell in enumerate(row.findall(f"{W}tc"), start=1):
                    text = compact(" ".join("".join(p.itertext()) for p in cell.findall(f".//{W}p")))
                    if text:
                        segments.append({"location": f"table:{table_index},row:{row_index},cell:{cell_index}", "text": text})
    return segments


def xlsx_segments(path: Path) -> list[dict]:
    with zipfile.ZipFile(path) as archive:
        shared: list[str] = []
        if "xl/sharedStrings.xml" in archive.namelist():
            shared_root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            shared = [compact("".join(node.itertext())) for node in shared_root.findall(f"{S}si")]
        wb = ET.fromstring(archive.read("xl/workbook.xml"))
        rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        relmap = {r.attrib["Id"]: r.attrib["Target"] for r in rels.findall(f"{P}Relationship")}
        segments: list[dict] = []
        for sheet in wb.findall(f".//{S}sheet"):
            rid = sheet.attrib.get(f"{R}id")
            target = relmap.get(rid, "")
            if not target:
                continue
            sheet_path = "xl/" + target.lstrip("/")
            try:
                sheet_root = ET.fromstring(archive.read(sheet_path))
            except KeyError:
                continue
            sheet_name = sheet.attrib.get("name", "unnamed")
            for cell in sheet_root.findall(f".//{S}c"):
                reference = cell.attrib.get("r", "unknown")
                kind = cell.attrib.get("t", "")
                value_node = cell.find(f"{S}v")
                value = "" if value_node is None else value_node.text or ""
                if kind == "s" and value.isdigit() and int(value) < len(shared):
                    value = shared[int(value)]
                elif kind == "inlineStr":
                    value = compact("".join(cell.itertext()))
                value = compact(value)
                if value:
                    segments.append({"location": f"sheet:{sheet_name},cell:{reference}", "text": value})
    return segments


def pdf_segments(path: Path, tessdata: Path | None) -> tuple[list[dict], dict]:
    try:
        import fitz  # type: ignore
        from pypdf import PdfReader  # type: ignore
    except ImportError as exc:
        raise RuntimeError("missing local PDF dependencies") from exc
    segments: list[dict] = []
    stats = {"pages": 0, "direct_text_pages": 0, "ocr_pages": 0}
    with tempfile.TemporaryDirectory(prefix="enterprise-ai-st1-019-") as td:
        staged = Path(td) / "document.pdf"
        shutil.copyfile(path, staged)
        reader = PdfReader(str(staged))
        document = fitz.open(staged)
        stats["pages"] = len(reader.pages)
        for page_index, page in enumerate(reader.pages, start=1):
            text = compact(page.extract_text() or "")
            method = "direct_text"
            if len(text) < 80 and tessdata and shutil.which("tesseract"):
                image = document[page_index - 1].get_pixmap(matrix=fitz.Matrix(3, 3), alpha=False)
                image_path = Path(td) / f"page-{page_index}.png"
                image.save(image_path)
                result = subprocess.run(
                    ["tesseract", str(image_path), "stdout", "-l", "fas", "--tessdata-dir", str(tessdata)],
                    capture_output=True, text=True, encoding="utf-8", errors="replace", check=False,
                )
                ocr = compact(result.stdout)
                if ocr:
                    text, method = ocr, "local_ocr_fas"
                    stats["ocr_pages"] += 1
            if text:
                if method == "direct_text":
                    stats["direct_text_pages"] += 1
                segments.append({"location": f"page:{page_index}", "text": text, "method": method})
        document.close()
    return segments, stats


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract the user-selected ST1-019 corpus locally and read-only.")
    parser.add_argument("--runtime-discovery", type=Path, default=runtime_file("st1-018-status-discovery.json"))
    parser.add_argument("--candidate-alias", default="status_oriented_candidate_1")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--selection-manifest", type=Path)
    parser.add_argument("--root", type=Path)
    args = parser.parse_args()
    if args.selection_manifest:
        candidate = json.loads(args.selection_manifest.read_text(encoding="utf-8"))
        required = {"alias", "relative_locator", "files", "selection_signature"}
        if not required <= set(candidate):
            raise RuntimeError("local selection manifest is incomplete")
        expected_extensions = candidate["selection_signature"]["extension_distribution"]
        expected_count = int(candidate["selection_signature"]["document_count"])
        expected_total = int(candidate["selection_signature"]["aggregate_size_bytes"])
    else:
        discovery = json.loads(args.runtime_discovery.read_text(encoding="utf-8"))
        candidate = next((x for x in discovery["top_candidates"] if x["alias"] == args.candidate_alias), None)
        if not candidate:
            raise RuntimeError("selected candidate is absent from local discovery state")
        if args.candidate_alias not in EXPECTED_BY_ALIAS:
            raise RuntimeError("candidate alias is not an approved extraction boundary")
        expected_extensions, expected_count, expected_total = EXPECTED_BY_ALIAS[args.candidate_alias]
    files = candidate["files"]
    counts = Counter(x["extension"].lower() for x in files)
    total = sum(int(x["size_bytes"]) for x in files)
    if len(files) != expected_count or dict(counts) != expected_extensions or total != expected_total:
        raise RuntimeError("selected corpus signature does not match the approved extraction boundary")
    subset = (args.root or Path(PILOT_ROOT)) / candidate["relative_locator"]
    if not subset.is_dir():
        raise RuntimeError("selected runtime locator is unavailable; extraction was not attempted")
    tessdata = Path(os.environ.get("LOCALAPPDATA", "")) / "EnterpriseAI" / "tessdata"
    tessdata = tessdata if (tessdata / "fas.traineddata").is_file() else None
    documents, aggregate = [], {"pdf_pages": 0, "pdf_direct_text_pages": 0, "pdf_ocr_pages": 0, "docx_segments": 0, "xlsx_cells": 0}
    for item in files:
        source = subset / item["relative_locator"]
        if not source.is_file() or source.stat().st_size != int(item["size_bytes"]):
            raise RuntimeError("selected corpus no longer matches discovery metadata; extraction halted")
        ext = item["extension"].lower()
        error = None
        try:
            if ext == ".pdf":
                segments, stats = pdf_segments(source, tessdata)
                aggregate["pdf_pages"] += stats["pages"]
                aggregate["pdf_direct_text_pages"] += stats["direct_text_pages"]
                aggregate["pdf_ocr_pages"] += stats["ocr_pages"]
            elif ext == ".docx":
                segments = docx_segments(source)
                aggregate["docx_segments"] += len(segments)
            elif ext == ".xlsx":
                segments = xlsx_segments(source)
                aggregate["xlsx_cells"] += len(segments)
            else:
                raise RuntimeError("unapproved extension in selected corpus")
        except (zipfile.BadZipFile, ET.ParseError, RuntimeError, OSError) as exc:
            # Continue within the approved corpus: a malformed or non-OOXML entry
            # is a bounded coverage limitation, never a reason to broaden scope.
            segments = []
            error = {"type": type(exc).__name__, "message": str(exc)}
        documents.append({"source_relative_locator": item["relative_locator"], "extension": ext, "size_bytes": item["size_bytes"], "sha256": sha256_file(source), "segments": segments, "extraction_error": error})
    output_path = args.output or runtime_file(f"{candidate['alias']}-extraction.json")
    output = {"schema_version": "bounded-status-extraction-v2", "generated_utc": datetime.now(UTC).isoformat(), "selection_alias": candidate["alias"], "selection_signature": {"document_count": len(files), "extension_distribution": dict(counts), "aggregate_size_bytes": total}, "documents": documents, "aggregate": aggregate}
    output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    safe = {"selection_alias": candidate["alias"], "document_count": len(documents), "extension_distribution": dict(counts), "aggregate": aggregate, "extraction_error_count": sum(x["extraction_error"] is not None for x in documents), "output_written_outside_git": True}
    print(json.dumps(safe, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({"status": "failed", "error_type": type(exc).__name__, "message": str(exc)}, ensure_ascii=True), file=sys.stderr)
        raise SystemExit(1)
