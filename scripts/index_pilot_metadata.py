#!/usr/bin/env python3
"""Resumable, metadata-only local index for the approved SMB pilot root.

The SQLite database is runtime operational data outside Git. It stores only
filesystem discovery metadata, never document content, hashes of contents, or
credentials. Enumeration uses one worker and never follows reparse points.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import time
import unicodedata
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path

FILE_ATTRIBUTE_REPARSE_POINT = 0x400
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".xlsx"}
STATUS_TERMS = {
    "projectstatus", "statusreport", "progressreport", "monthlyreport", "weeklyreport",
    "managementreport", "projectcontrols", "updatedschedule", "progressdashboard", "actionplan",
    "\u06af\u0632\u0627\u0631\u0634\u0648\u0636\u0639\u06cc\u062a", "\u06af\u0632\u0627\u0631\u0634\u067e\u06cc\u0634\u0631\u0641\u062a", "\u06af\u0632\u0627\u0631\u0634\u0645\u0627\u0647\u0627\u0646\u0647", "\u06af\u0632\u0627\u0631\u0634\u0647\u0641\u062a\u06af\u06cc", "\u06af\u0632\u0627\u0631\u0634\u0645\u062f\u06cc\u0631\u06cc\u062a\u06cc", "\u06a9\u0646\u062a\u0631\u0644\u067e\u0631\u0648\u0698\u0647", "\u0628\u0631\u0646\u0627\u0645\u0647\u0631\u06cc\u0632\u06cc", "\u067e\u06cc\u0634\u0631\u0641\u062a\u0641\u06cc\u0632\u06cc\u06a9\u06cc",
}


def runtime_default(name: str) -> Path:
    return Path(os.environ["LOCALAPPDATA"]) / "EnterpriseAI" / "runtime" / name


def normalized(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).replace("\u064a", "\u06cc").replace("\u0643", "\u06a9")
    return "".join(ch for ch in value.casefold() if not ch.isspace() and unicodedata.category(ch) != "Cf")


def is_reparse(entry: os.DirEntry[str]) -> bool:
    try:
        return bool(entry.stat(follow_symlinks=False).st_file_attributes & FILE_ATTRIBUTE_REPARSE_POINT)
    except OSError:
        return False


def utc(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp, UTC).isoformat()


def connect(database: Path) -> sqlite3.Connection:
    database.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(database)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS directories (
      relative_locator TEXT PRIMARY KEY,
      parent_relative_locator TEXT,
      status TEXT NOT NULL,
      enumeration_error TEXT,
      scanned_utc TEXT,
      is_reparse INTEGER NOT NULL DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS files (
      relative_locator TEXT PRIMARY KEY,
      parent_relative_locator TEXT NOT NULL,
      source_alias TEXT NOT NULL,
      filename TEXT NOT NULL,
      extension TEXT NOT NULL,
      size_bytes INTEGER NOT NULL,
      created_utc TEXT,
      modified_utc TEXT,
      metadata_fingerprint TEXT NOT NULL,
      enumeration_status TEXT NOT NULL,
      enumeration_error TEXT
    );
    CREATE INDEX IF NOT EXISTS files_parent_idx ON files(parent_relative_locator);
    CREATE INDEX IF NOT EXISTS directories_status_idx ON directories(status);
    """)
    return conn


def initialize(conn: sqlite3.Connection) -> None:
    conn.execute("INSERT OR IGNORE INTO directories(relative_locator,parent_relative_locator,status) VALUES('.','', 'pending')")
    conn.commit()


def scan(root: Path, conn: sqlite3.Connection, max_directories: int, max_seconds: int) -> dict:
    started = time.monotonic()
    processed = errors = files_seen = reparse_skipped = 0
    while processed < max_directories and time.monotonic() - started < max_seconds:
        row = conn.execute("SELECT relative_locator FROM directories WHERE status='pending' ORDER BY relative_locator LIMIT 1").fetchone()
        if row is None:
            break
        relative = row[0]
        directory = root if relative == "." else root / relative
        try:
            entries = sorted(os.scandir(directory), key=lambda item: item.name.casefold())
            for entry in entries:
                child_relative = entry.name if relative == "." else f"{relative}/{entry.name}"
                if is_reparse(entry):
                    conn.execute("INSERT OR REPLACE INTO directories(relative_locator,parent_relative_locator,status,is_reparse,scanned_utc) VALUES(?,?,?,?,?)", (child_relative, relative, "skipped_reparse", 1, utc(time.time())))
                    reparse_skipped += 1
                    continue
                try:
                    if entry.is_dir(follow_symlinks=False):
                        conn.execute("INSERT OR IGNORE INTO directories(relative_locator,parent_relative_locator,status) VALUES(?,?, 'pending')", (child_relative, relative))
                        continue
                    if not entry.is_file(follow_symlinks=False):
                        continue
                    stat = entry.stat(follow_symlinks=False)
                    extension = Path(entry.name).suffix.lower()
                    fingerprint = hashlib.sha256(f"{child_relative}|{stat.st_size}|{stat.st_mtime_ns}".encode("utf-8")).hexdigest()
                    conn.execute("""INSERT OR REPLACE INTO files(relative_locator,parent_relative_locator,source_alias,filename,extension,size_bytes,created_utc,modified_utc,metadata_fingerprint,enumeration_status,enumeration_error) VALUES(?,?,?,?,?,?,?,?,?,?,NULL)""", (child_relative, relative, "source-" + hashlib.sha256(child_relative.encode("utf-8")).hexdigest()[:16], entry.name, extension, stat.st_size, utc(stat.st_ctime), utc(stat.st_mtime), fingerprint, "enumerated"))
                    files_seen += 1
                except OSError as exc:
                    errors += 1
                    conn.execute("INSERT OR REPLACE INTO files(relative_locator,parent_relative_locator,source_alias,filename,extension,size_bytes,enumeration_status,enumeration_error,metadata_fingerprint) VALUES(?,?,?,?,?,?,?,?,?)", (child_relative, relative, "source-" + hashlib.sha256(child_relative.encode("utf-8")).hexdigest()[:16], entry.name, Path(entry.name).suffix.lower(), 0, "error", type(exc).__name__, hashlib.sha256(child_relative.encode("utf-8")).hexdigest()))
            conn.execute("UPDATE directories SET status='completed',enumeration_error=NULL,scanned_utc=? WHERE relative_locator=?", (utc(time.time()), relative))
        except OSError as exc:
            errors += 1
            conn.execute("UPDATE directories SET status='error',enumeration_error=?,scanned_utc=? WHERE relative_locator=?", (type(exc).__name__, utc(time.time()), relative))
        conn.commit()
        processed += 1
    counts = dict(conn.execute("SELECT status,count(*) FROM directories GROUP BY status"))
    return {"directories_processed_this_run": processed, "files_seen_this_run": files_seen, "enumeration_errors_this_run": errors, "reparse_points_skipped_this_run": reparse_skipped, "directory_status_counts": counts, "pending_directories": counts.get("pending", 0), "complete": counts.get("pending", 0) == 0}


def query(conn: sqlite3.Connection, excluded: set[str], min_modified_utc: str | None) -> dict:
    aggregate: dict[str, dict] = defaultdict(lambda: {"files": [], "score": 0, "signals": set()})
    rows = conn.execute("SELECT relative_locator,parent_relative_locator,filename,extension,size_bytes,modified_utc FROM files WHERE enumeration_status='enumerated'")
    for relative, parent, filename, extension, size, modified in rows:
        if extension not in ALLOWED_EXTENSIONS:
            continue
        if any(parent == item or parent.startswith(item + "/") for item in excluded):
            continue
        if min_modified_utc and modified and modified < min_modified_utc:
            continue
        probe = normalized(parent + "/" + filename)
        signals = {term for term in STATUS_TERMS if normalized(term) in probe}
        if not signals:
            continue
        for ancestor in [parent, *Path(parent).parents]:
            key = str(ancestor).replace("\\", "/")
            if key == ".":
                continue
            entry = aggregate[key]
            entry["files"].append((relative, extension, size, modified))
            entry["score"] += len(signals)
            entry["signals"].update(signals)
    candidates = []
    for locator, item in aggregate.items():
        if any(locator == excluded_locator or locator.startswith(excluded_locator + "/") or excluded_locator.startswith(locator + "/") for excluded_locator in excluded):
            continue
        unique = {row[0]: row for row in item["files"]}
        values = list(unique.values())
        count = len(values)
        total = sum(row[2] for row in values)
        if not (10 <= count <= 100 and total <= 1024 * 1024 * 1024):
            continue
        extensions = dict(sorted(Counter(row[1] for row in values).items()))
        dates = [row[3] for row in values if row[3]]
        candidates.append({"relative_locator": locator, "document_count": count, "aggregate_size_bytes": total, "extension_distribution": extensions, "metadata_date_range": [min(dates), max(dates)] if dates else None, "metadata_signals": sorted(item["signals"]), "score": item["score"]})
    candidates.sort(key=lambda item: (-item["score"], item["aggregate_size_bytes"], item["relative_locator"].casefold()))
    return {"candidate_count": len(candidates), "top_candidates": candidates[:3]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--database", type=Path, default=runtime_default("pilot_metadata_index.sqlite"))
    parser.add_argument("--max-directories", type=int, default=250)
    parser.add_argument("--max-seconds", type=int, default=90)
    parser.add_argument("--excluded-json", type=Path)
    parser.add_argument("--min-modified-utc")
    args = parser.parse_args()
    if not args.root.is_dir():
        raise SystemExit("approved pilot root is unavailable")
    conn = connect(args.database)
    initialize(conn)
    scan_result = scan(args.root, conn, args.max_directories, args.max_seconds)
    excluded = set()
    if args.excluded_json and args.excluded_json.is_file():
        excluded = set(json.loads(args.excluded_json.read_text(encoding="utf-8-sig")))
    query_result = query(conn, excluded, args.min_modified_utc) if scan_result["complete"] else {"candidate_count": None, "top_candidates": []}
    print(json.dumps({"index_database_outside_git": True, **scan_result, "query": query_result}, separators=(",", ":")))


if __name__ == "__main__":
    main()
