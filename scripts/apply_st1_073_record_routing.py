#!/usr/bin/env python3
"""Apply ST1-073's additive SDAS record-routing summary views on rddb."""
from __future__ import annotations

import base64
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SQL = (ROOT / "migrations" / "024_add_sdas_record_routing_summary.sql").read_text(encoding="utf-8")


def main() -> None:
    exists = subprocess.run(
        [
            "ssh", "-o", "BatchMode=yes", "enterprise-ai-rddb",
            "docker exec postgres-db psql -U postgres -d enterprise_ai_ingestion_mvp -tAc \"SELECT to_regclass('ingestion.sdas_record_policy_routing_summary') IS NOT NULL\"",
        ],
        text=True,
        capture_output=True,
    )
    if exists.returncode:
        raise SystemExit(exists.stderr.strip() or "ST1-073 routing preflight failed")
    if exists.stdout.strip() == "t":
        print("st1_073_record_routing_already_applied")
        return
    if exists.stdout.strip() != "f":
        raise SystemExit("ST1-073 routing preflight returned an unexpected result")
    payload = base64.b64encode(SQL.encode()).decode()
    command = (
        f"echo {payload} | base64 -d | "
        "docker exec -i postgres-db psql -v ON_ERROR_STOP=1 -U postgres -d enterprise_ai_ingestion_mvp"
    )
    result = subprocess.run(["ssh", "-o", "BatchMode=yes", "enterprise-ai-rddb", command], text=True, capture_output=True)
    if result.returncode:
        raise SystemExit(result.stderr.strip() or "ST1-073 routing deployment failed")
    print(result.stdout.strip())


if __name__ == "__main__":
    main()
