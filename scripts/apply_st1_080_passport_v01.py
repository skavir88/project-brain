#!/usr/bin/env python3
"""Apply ST1-080 Assurance Passport v0.1 runtime upgrade on rddb + rdapp."""
from __future__ import annotations

import base64
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP_PATH = ROOT / "implementation" / "ingestion-service" / "app.py"
SQL_FILES = [
    ROOT / "migrations" / "022_add_sdas_assurance_passport_projection.sql",
    ROOT / "migrations" / "023_add_sdas_assurance_passport_summary.sql",
]


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, text=True, capture_output=True)
    if result.returncode:
        raise SystemExit(result.stderr.strip() or result.stdout.strip() or f"command failed: {' '.join(command)}")
    return result


def ssh(host: str, command: str) -> subprocess.CompletedProcess[str]:
    return run(["ssh.exe", "-o", "BatchMode=yes", host, command])


def main() -> None:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    rdapp_backup_dir = f"/var/tmp/enterprise-ai-evidence/st1-080-{ts}-rdapp"
    rddb_backup_dir = f"/var/tmp/enterprise-ai-evidence/st1-080-{ts}-rddb"

    ssh("enterprise-ai-rdapp", f"mkdir -p {rdapp_backup_dir} && cp /opt/enterprise-ai/ingestion-service/app.py {rdapp_backup_dir}/app.py.bak")
    ssh(
        "enterprise-ai-rdapp",
        f"docker inspect deploy-ingestion-service-1 --format '{{{{.Image}}}}' > {rdapp_backup_dir}/container-image-id.txt",
    )
    ssh("enterprise-ai-rddb", f"mkdir -p {rddb_backup_dir}")
    ssh(
        "enterprise-ai-rddb",
        f"docker exec postgres-db pg_dump -U postgres -d enterprise_ai_ingestion_mvp -s -t ingestion.sdas_assurance_passport_projection -t ingestion.sdas_assurance_passport_portfolio_summary -t ingestion.sdas_assurance_passport_exception_queue > {rddb_backup_dir}/passport-views-before.sql",
    )

    for sql_file in SQL_FILES:
        payload = base64.b64encode(sql_file.read_bytes()).decode()
        ssh(
            "enterprise-ai-rddb",
            f"echo {payload} | base64 -d | docker exec -i postgres-db psql -v ON_ERROR_STOP=1 -U postgres -d enterprise_ai_ingestion_mvp",
        )

    remote_tmp = f"{rdapp_backup_dir}/app.py.new"
    run(["scp.exe", str(APP_PATH), f"enterprise-ai-rdapp:{remote_tmp}"])
    ssh("enterprise-ai-rdapp", f"cp {remote_tmp} /opt/enterprise-ai/ingestion-service/app.py")
    ssh(
        "enterprise-ai-rdapp",
        "cd /opt/enterprise-ai/deploy && docker compose config > /dev/null && docker compose build ingestion-service && docker compose up -d ingestion-service",
    )

    print(
        f"applied_st1_080_passport_v01 rdapp_backup_dir={rdapp_backup_dir} rddb_backup_dir={rddb_backup_dir}"
    )


if __name__ == "__main__":
    main()
