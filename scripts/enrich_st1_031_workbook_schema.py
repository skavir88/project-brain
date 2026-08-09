#!/usr/bin/env python3
"""Read one approved XLSX locally and emit runtime-only schema evidence.

This utility does not modify the workbook or SMB share. Raw labels, locators,
formulas, and row values are deliberately written only to a local runtime JSON.
"""
from __future__ import annotations

import argparse
import json
import re
import zipfile
from collections import defaultdict
from pathlib import Path
from xml.etree import ElementTree as ET

S = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
P = "{http://schemas.openxmlformats.org/package/2006/relationships}"
CELL_RE = re.compile(r"([A-Z]+)(\d+)$")


def cell_parts(reference: str) -> tuple[str, int]:
    match = CELL_RE.fullmatch(reference)
    if not match:
        raise ValueError(f"invalid cell reference: {reference}")
    return match.group(1), int(match.group(2))


def column_index(column: str) -> int:
    result = 0
    for char in column:
        result = result * 26 + ord(char) - ord("A") + 1
    return result


def load_cells(path: Path, sheet_name: str) -> tuple[dict[str, dict], list[str]]:
    with zipfile.ZipFile(path) as archive:
        shared: list[str] = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            shared = ["".join(node.itertext()).strip() for node in root.findall(f"{S}si")]
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        targets = {rel.attrib["Id"]: rel.attrib["Target"] for rel in rels.findall(f"{P}Relationship")}
        sheet = next((item for item in workbook.findall(f".//{S}sheet") if item.attrib.get("name") == sheet_name), None)
        if sheet is None:
            raise RuntimeError("requested sheet is absent")
        target = targets.get(sheet.attrib.get(f"{R}id", ""), "")
        if not target:
            raise RuntimeError("sheet relationship is absent")
        root = ET.fromstring(archive.read("xl/" + target.lstrip("/")))
        cells: dict[str, dict] = {}
        for cell in root.findall(f".//{S}c"):
            reference = cell.attrib.get("r")
            if not reference:
                continue
            kind = cell.attrib.get("t", "")
            value_node = cell.find(f"{S}v")
            value = "" if value_node is None else value_node.text or ""
            if kind == "s" and value.isdigit() and int(value) < len(shared):
                value = shared[int(value)]
            elif kind == "inlineStr":
                value = "".join(cell.itertext()).strip()
            formula = cell.find(f"{S}f")
            cells[reference] = {
                "value": value,
                "formula": None if formula is None else formula.text or "",
                "data_type": kind or "number_or_formula",
                "style": cell.attrib.get("s"),
            }
        merged = [item.attrib["ref"] for item in root.findall(f".//{S}mergeCell")]
    return cells, merged


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workbook", type=Path, required=True)
    parser.add_argument("--sheet", required=True)
    parser.add_argument("--rows", required=True, help="comma-separated target row numbers")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not args.workbook.is_file():
        raise RuntimeError("approved workbook is unavailable")
    target_rows = {int(item) for item in args.rows.split(",")}
    cells, merged = load_cells(args.workbook, args.sheet)
    relevant_columns = sorted({cell_parts(ref)[0] for ref in cells if cell_parts(ref)[1] in target_rows}, key=column_index)
    header_rows = sorted({cell_parts(ref)[1] for ref, item in cells.items() if cell_parts(ref)[1] < min(target_rows) and str(item["value"]).strip()})
    # Preserve all populated rows before the first reviewed record: header/legend
    # structure is source evidence and must not be guessed from numeric patterns.
    headers = {
        str(row): {column: cells.get(f"{column}{row}") for column in relevant_columns if f"{column}{row}" in cells}
        for row in header_rows
    }
    rows = {
        str(row): {column: cells.get(f"{column}{row}") for column in relevant_columns if f"{column}{row}" in cells}
        for row in sorted(target_rows)
    }
    formulas = {
        reference: item for reference, item in cells.items()
        if cell_parts(reference)[1] in target_rows and item["formula"] is not None
    }
    output = {
        "schema_version": "st1-031-workbook-schema-v1",
        "source": "local approved workbook only",
        "sheet": args.sheet,
        "target_rows": sorted(target_rows),
        "relevant_columns": relevant_columns,
        "header_rows": headers,
        "target_rows_data": rows,
        "merged_ranges": merged,
        "target_formula_cells": formulas,
        "read_only": True,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"output_outside_git": True, "sheet": args.sheet, "target_rows": len(target_rows), "relevant_columns": len(relevant_columns), "header_rows": len(headers), "merged_ranges": len(merged), "target_formula_cells": len(formulas)}, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
