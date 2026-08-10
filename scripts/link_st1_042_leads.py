#!/usr/bin/env python3
"""Find bounded metadata-only follow-up families for certified ST1-041 leads.

Raw locators and filenames are emitted only to a runtime-local JSON file. The
script neither opens source documents nor changes any source or platform data.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
import sqlite3
import unicodedata
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path


LEADS = {
    "engineering": ["anchor", "expansion", "foundation", "compressor", "approval", "response", "فونداسیون", "کمپرسور", "تایید", "تأیید", "پاسخ"],
    "procurement": ["inspection", "release", "shipment", "delivery", "receipt", "installation", "irn", "بازرسی", "حمل", "تحویل", "نصب"],
    "document_follow_up": ["screw", "package", "review", "approval", "closure", "action", "پکیج", "بررسی", "تایید", "تأیید", "اقدام"],
    "overall_status": ["progress report", "status report", "weekly report", "monthly report", "dashboard", "project control", "schedule", "گزارش پیشرفت", "گزارش وضعیت", "گزارش هفتگی", "گزارش ماهانه", "داشبورد", "کنترل پروژه", "برنامه زمان"],
}
ALLOWED = {".pdf", ".docx", ".xlsx"}
NEGATIVE = ["claim", "legal", "tender", "bid", "لایحه", "دعاوی", "حقوقی", "مناقصه"]


def runtime(name: str) -> Path:
    return Path(os.environ["LOCALAPPDATA"]) / "EnterpriseAI" / "runtime" / name


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKC", value or "").replace("ي", "ی").replace("ك", "ک")
    return " ".join(value.casefold().split())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", type=Path, default=runtime("pilot_metadata_index.sqlite"))
    parser.add_argument("--review-package", type=Path, default=runtime("st1-040-human-review-package.json"))
    parser.add_argument("--output", type=Path, default=runtime("st1-042-linkage-discovery.json"))
    parser.add_argument("--limit", type=int, default=12)
    args = parser.parse_args()
    package = json.loads(args.review_package.read_text(encoding="utf-8"))
    approved_aliases = {candidate["source_alias"] for candidate in package["candidates"]}
    conn = sqlite3.connect(args.database)
    try:
        rows = conn.execute("SELECT relative_locator,parent_relative_locator,source_alias,filename,extension,size_bytes,modified_utc FROM files WHERE enumeration_status='enumerated'").fetchall()
    finally:
        conn.close()
    by_parent: dict[str, dict] = defaultdict(lambda: {"files": [], "lead_signals": defaultdict(set), "same_family": False})
    for relative, parent, source_alias, filename, extension, size, modified in rows:
        haystack = normalize(f"{parent}/{filename}")
        lead_hits = {category: [term for term in terms if normalize(term) in haystack] for category, terms in LEADS.items()}
        lead_hits = {category: hits for category, hits in lead_hits.items() if hits}
        prefix_match = any(source_alias.startswith(alias) for alias in approved_aliases)
        if not lead_hits and not prefix_match:
            continue
        item = by_parent[parent]
        item["files"].append({"relative_locator": relative, "source_alias": source_alias, "filename": filename, "extension": extension, "size_bytes": size, "modified_utc": modified})
        item["same_family"] |= prefix_match
        for category, hits in lead_hits.items():
            item["lead_signals"][category].update(hits)
    ranked = []
    for parent, item in by_parent.items():
        files = item["files"]
        probeable = [file for file in files if file["extension"] in ALLOWED]
        if not probeable or len(files) > 80 or any(normalize(term) in normalize(parent) for term in NEGATIVE):
            continue
        signals = {key: sorted(value) for key, value in item["lead_signals"].items()}
        score = sum({"overall_status": 12, "engineering": 7, "procurement": 7, "document_follow_up": 6}[key] for key in signals) + (5 if item["same_family"] else 0) + min(5, len(probeable) // 2)
        ranked.append({"relative_locator": parent, "alias": "st1-042-" + hashlib.sha256(parent.encode("utf-8")).hexdigest()[:16], "score": score, "same_family_as_certified_lead": item["same_family"], "lead_signals": signals, "document_count": len(files), "probeable_document_count": len(probeable), "extension_distribution": dict(sorted(Counter(file["extension"] for file in files).items())), "aggregate_size_bytes": sum(int(file["size_bytes"] or 0) for file in files), "files": files})
    ranked.sort(key=lambda item: (-item["score"], -item["probeable_document_count"], item["aggregate_size_bytes"], item["relative_locator"].casefold()))
    result = {"schema_version":"st1-042-linkage-discovery-v1","generated_utc":datetime.now(UTC).isoformat(),"certified_lead_count":len(approved_aliases),"candidate_family_count":len(ranked),"top_families":ranked[:args.limit],"boundaries":{"metadata_only":True,"content_opened":False,"new_smb_traversal":False,"raw_output_outside_git":True}}
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"certified_lead_count":len(approved_aliases),"candidate_family_count":len(ranked),"top_family_count":len(result["top_families"]),"output_outside_git":True}, separators=(",",":")))


if __name__ == "__main__":
    main()
