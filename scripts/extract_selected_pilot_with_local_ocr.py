"""Read-only, local OCR extraction for a validated Enterprise AI pilot subset.

All raw text, paths, and page-level provenance are written only to a caller
supplied runtime path outside Git. The script calls only local PDF/OCR tools.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree

import fitz
from pypdf import PdfReader


def utc_iso(value: float) -> str:
    return datetime.fromtimestamp(value, timezone.utc).isoformat()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def executable(name: str, fallback: str | None = None) -> str:
    result = shutil.which(name) or fallback
    if not result or not Path(result).exists():
        raise RuntimeError(f"required local executable unavailable: {name}")
    return result


def pdf_page_count(path: Path) -> int:
    return len(PdfReader(str(path)).pages)


def pdftotext_page(pdftotext: str, path: Path, page: int) -> str:
    result = subprocess.run(
        [pdftotext, "-f", str(page), "-l", str(page), "-enc", "UTF-8", "-layout", str(path), "-"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, timeout=60,
    )
    if result.returncode != 0:
        return ""
    return result.stdout.decode("utf-8", errors="replace").strip()


def ocr_page(tesseract: str, tessdata: Path, path: Path, page: int, temp_dir: Path) -> str:
    image_base = temp_dir / f"page-{page}"
    image = image_base.with_suffix(".png")
    with fitz.open(str(path)) as document:
        pixmap = document.load_page(page - 1).get_pixmap(matrix=fitz.Matrix(300 / 72, 300 / 72), alpha=False)
        pixmap.save(str(image))
    if not image.exists():
        raise RuntimeError("pdf_render_failed")
    result = subprocess.run(
        [tesseract, str(image), "stdout", "-l", "fas", "--tessdata-dir", str(tessdata)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, timeout=120,
    )
    if result.returncode != 0:
        raise RuntimeError("local_ocr_failed")
    return result.stdout.decode("utf-8", errors="replace").strip()


def xlsx_signature(path: Path) -> str:
    with path.open("rb") as source:
        header = source.read(16)
    if header.startswith(b"PK\x03\x04"):
        return "zip_ooxml"
    if header.startswith(bytes.fromhex("D0CF11E0A1B11AE1")):
        return "ole_compound_legacy_or_renamed"
    if header[:1] in (b"<", b"{", b"["):
        return "text_or_markup"
    return "unknown_non_ooxml"


def extract_xlsx(path: Path) -> tuple[str, int]:
    namespace = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with zipfile.ZipFile(path) as archive:
        shared: list[str] = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ElementTree.fromstring(archive.read("xl/sharedStrings.xml"))
            shared = ["".join(node.itertext()) for node in root.findall("main:si", namespace)]
        sheets = sorted(name for name in archive.namelist() if name.startswith("xl/worksheets/sheet") and name.endswith(".xml"))
        result: list[str] = []
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
                    except (ValueError, IndexError):
                        values.append(value.text)
                else:
                    values.append(value.text)
            result.append(f"{sheet}:\n" + "\n".join(values))
    return "\n\n".join(result), len(sheets)


def main() -> int:
    locator_value = os.environ.get("EAI_LOCATOR_RUNTIME_INPUT")
    subset_value = os.environ.get("EAI_SELECTED_SUBSET_ROOT")
    output_value = os.environ.get("EAI_OCR_RUNTIME_OUTPUT")
    tessdata_value = os.environ.get("EAI_TESSDATA_DIR")
    if not all((locator_value, subset_value, output_value, tessdata_value)):
        raise SystemExit("EAI_LOCATOR_RUNTIME_INPUT, EAI_SELECTED_SUBSET_ROOT, EAI_OCR_RUNTIME_OUTPUT, and EAI_TESSDATA_DIR are required")
    locator = json.loads(Path(locator_value).read_text(encoding="utf-8"))
    subset = Path(subset_value)
    expected = locator["files"]
    actual: list[tuple[dict, Path]] = []
    for item in expected:
        path = subset / item["relative_reference"]
        if not path.is_file() or path.stat().st_size != item["size_bytes"]:
            raise SystemExit("validated subset no longer matches runtime locator")
        actual.append((item, path))
    extensions = Counter(path.suffix.lower() for _, path in actual)
    total_size = sum(path.stat().st_size for _, path in actual)
    if len(actual) != 19 or extensions != Counter({".pdf": 18, ".xlsx": 1}) or total_size != 23606611:
        raise SystemExit("validated subset signature mismatch")

    pdftotext = executable("pdftotext")
    tesseract = executable("tesseract", r"C:\Program Files\Tesseract-OCR\tesseract.exe")
    tessdata = Path(tessdata_value)
    records: list[dict] = []
    failures: Counter[str] = Counter()
    page_count = text_pages = ocr_pages = 0
    with tempfile.TemporaryDirectory(prefix="enterprise-ai-ocr-") as temporary:
        temp_dir = Path(temporary)
        for item, path in actual:
            fingerprint = sha256(path)
            base = {
                "source_alias": "status_candidate_b",
                "source_relative_reference": item["relative_reference"],
                "source_timestamp_utc": utc_iso(path.stat().st_mtime),
                "content_fingerprint": fingerprint,
                "document_type": path.suffix.lower(),
            }
            try:
                if path.suffix.lower() == ".xlsx":
                    signature = xlsx_signature(path)
                    record = {**base, "xlsx_signature": signature, "extraction": {"method": "not_attempted"}}
                    if signature == "zip_ooxml":
                        text, sheet_count = extract_xlsx(path)
                        record["text"] = text
                        record["extraction"] = {"method": "xlsx_ooxml_values", "sheet_count": sheet_count}
                    records.append(record)
                    continue
                staged_pdf = temp_dir / f"{fingerprint}.pdf"
                shutil.copyfile(path, staged_pdf)
                pages: list[dict] = []
                for page in range(1, pdf_page_count(staged_pdf) + 1):
                    page_count += 1
                    text = pdftotext_page(pdftotext, staged_pdf, page)
                    method = "pdftotext_utf8_layout"
                    if len(text) < 80:
                        text = ocr_page(tesseract, tessdata, staged_pdf, page, temp_dir)
                        method = "local_tesseract_fas_300dpi"
                        ocr_pages += 1
                    if text:
                        text_pages += 1
                    pages.append({"page": page, "method": method, "text": text})
                records.append({**base, "pages": pages, "extraction": {"method": "page_level_pdf_text_or_local_ocr"}})
            except (OSError, RuntimeError, subprocess.TimeoutExpired, zipfile.BadZipFile, ElementTree.ParseError) as error:
                category = type(error).__name__
                if isinstance(error, RuntimeError):
                    category = f"RuntimeError:{str(error)}"
                failures[category] += 1
    output = Path(output_value)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"locator": locator, "records": records}, ensure_ascii=False), encoding="utf-8")
    xlsx_records = [record for record in records if record["document_type"] == ".xlsx"]
    print(json.dumps({
        "validated_document_count": len(actual),
        "pdf_page_count": page_count,
        "text_bearing_page_count": text_pages,
        "ocr_page_count": ocr_pages,
        "extraction_failure_categories": dict(sorted(failures.items())),
        "xlsx_signature": xlsx_records[0].get("xlsx_signature") if xlsx_records else "not_recorded",
        "xlsx_extraction_method": xlsx_records[0].get("extraction", {}).get("method") if xlsx_records else "not_recorded",
        "raw_output_outside_git": True,
        "source_modified": False,
    }, ensure_ascii=False, separators=(",", ":")))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
