#!/usr/bin/env python3
"""Read-only, local extraction for the user-confirmed ST1-044 source token.

Raw source locators and extracted organizational text are written only to the
runtime-local output. The script revalidates the five allowlisted source files
against the metadata index, opens no archives or XLSB files, and contacts no
external or platform service.
"""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from xml.etree import ElementTree


ALLOWLIST = {".pdf", ".docx"}
TOKEN = "st1-043-e3aca7f9868040d6"


def runtime(name: str) -> Path:
    return Path(os.environ["LOCALAPPDATA"]) / "EnterpriseAI" / "runtime" / name


def read_pdf(path: Path) -> dict:
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    pages = []
    for number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        pages.append({"page": number, "text": text})
    return {"kind": "pdf", "page_count": len(pages), "pages": pages}


def paragraph_text(node: ElementTree.Element) -> str:
    return "".join(node.itertext()).strip()


def read_docx(path: Path) -> dict:
    with zipfile.ZipFile(path) as archive:
        root = ElementTree.fromstring(archive.read("word/document.xml"))
    paragraphs = []
    for index, paragraph in enumerate(root.findall(".//{*}body/{*}p"), start=1):
        text = paragraph_text(paragraph)
        if text:
            paragraphs.append({"paragraph": index, "text": text})
    tables = []
    for table_index, table in enumerate(root.findall(".//{*}body/{*}tbl"), start=1):
        rows = []
        for row_index, row in enumerate(table.findall("./{*}tr"), start=1):
            cells = [paragraph_text(cell) for cell in row.findall("./{*}tc")]
            if any(cells):
                rows.append({"row": row_index, "cells": cells})
        if rows:
            tables.append({"table": table_index, "rows": rows})
    return {"kind": "docx", "paragraphs": paragraphs, "tables": tables}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--database", type=Path, default=runtime("pilot_metadata_index.sqlite"))
    parser.add_argument("--locator", type=Path, default=runtime("st1-043-authoritative-source-locator.json"))
    parser.add_argument("--output", type=Path, default=runtime("st1-044-management-report-extraction.json"))
    args = parser.parse_args()
    if not args.root.is_dir() or not args.database.is_file() or not args.locator.is_file():
        raise SystemExit("required read-only source root or runtime-local state is unavailable")

    locator = json.loads(args.locator.read_text(encoding="utf-8"))
    selected = next((x for x in locator["locations"] if x["locator_token"] == TOKEN), None)
    if selected is None:
        raise SystemExit("approved source token is absent from runtime-local locator state")

    conn = sqlite3.connect(args.database)
    try:
        rows = conn.execute(
            """SELECT relative_locator, source_alias, filename, extension, size_bytes,
                      created_utc, modified_utc, metadata_fingerprint
                 FROM files
                 WHERE parent_relative_locator = ? AND enumeration_status = 'enumerated'
                 ORDER BY filename""",
            (selected["relative_locator"],),
        ).fetchall()
    finally:
        conn.close()

    files = []
    for relative, alias, filename, extension, size, created, modified, fingerprint in rows:
        if extension.casefold() not in ALLOWLIST:
            continue
        source = args.root / relative
        item = {
            "relative_locator": relative,
            "source_alias": alias,
            "filename": filename,
            "extension": extension,
            "indexed_size_bytes": size,
            "indexed_created_utc": created,
            "indexed_modified_utc": modified,
            "metadata_fingerprint": fingerprint,
            "revalidation": {"available": source.is_file()},
        }
        if source.is_file():
            stat = source.stat()
            item["revalidation"]["size_matches"] = stat.st_size == size
            item["revalidation"]["observed_size_bytes"] = stat.st_size
        files.append(item)

    extracted = []
    for item in files:
        result = dict(item)
        source = args.root / item["relative_locator"]
        if not item["revalidation"]["available"] or not item["revalidation"].get("size_matches"):
            result["extraction_status"] = "not_opened_revalidation_failed"
        else:
            try:
                result.update(read_pdf(source) if item["extension"].casefold() == ".pdf" else read_docx(source))
                result["extraction_status"] = "extracted"
            except Exception as exc:
                result["extraction_status"] = "error"
                result["error_type"] = type(exc).__name__
        extracted.append(result)

    payload = {
        "schema_version": "st1-044-management-report-extraction-v1",
        "generated_utc": datetime.now(UTC).isoformat(),
        "approved_token": TOKEN,
        "selection_signature": {
            "folder_file_count": len(rows),
            "allowlisted_file_count": len(files),
            "processed_extensions": sorted(ALLOWLIST),
            "excluded_extension_count": len(rows) - len(files),
        },
        "documents": extracted,
        "boundaries": {
            "read_only": True,
            "archives_opened": False,
            "xlsb_opened": False,
            "new_smb_traversal": False,
            "external_model_use": False,
            "platform_persistence": False,
            "automatic_certification": False,
            "raw_output_outside_git": True,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "approved_token": TOKEN,
        "folder_file_count": len(rows),
        "allowlisted_file_count": len(files),
        "available": sum(x["revalidation"]["available"] for x in files),
        "metadata_match": sum(x["revalidation"].get("size_matches") is True for x in files),
        "extracted": sum(x["extraction_status"] == "extracted" for x in extracted),
        "errors": sum(x["extraction_status"] == "error" for x in extracted),
        "output_outside_git": True,
    }, separators=(",", ":")))


if __name__ == "__main__":
    raise SystemExit(main())
