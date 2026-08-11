#!/usr/bin/env python3
"""Apply ST1-072's additive assurance-summary views on rddb."""
from __future__ import annotations

import base64
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SQL = (ROOT / "migrations" / "023_add_sdas_assurance_passport_summary.sql").read_text(encoding="utf-8")


def main() -> None:
    exists = subprocess.run(
        [
            "ssh", "-o", "BatchMode=yes", "enterprise-ai-rddb",
            "docker exec postgres-db psql -U postgres -d enterprise_ai_ingestion_mvp -tAc \"SELECT to_regclass('ingestion.sdas_assurance_passport_portfolio_summary') IS NOT NULL\"",
        ],
        text=True,
        capture_output=True,
    )
    if exists.returncode:
        raise SystemExit(exists.stderr.strip() or "ST1-072 summary preflight failed")
    if exists.stdout.strip() == "t":
        print("st1_072_assurance_summary_already_applied")
        return
    if exists.stdout.strip() != "f":
        raise SystemExit("ST1-072 summary preflight returned an unexpected result")
    payload = base64.b64encode(SQL.encode()).decode()
    command = (
        f"echo {payload} | base64 -d | "
        "docker exec -i postgres-db psql -v ON_ERROR_STOP=1 -U postgres -d enterprise_ai_ingestion_mvp"
    )
    result = subprocess.run(["ssh", "-o", "BatchMode=yes", "enterprise-ai-rddb", command], text=True, capture_output=True)
    if result.returncode:
        raise SystemExit(result.stderr.strip() or "ST1-072 summary deployment failed")
    print(result.stdout.strip())


if __name__ == "__main__":
    main()
