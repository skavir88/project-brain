#!/usr/bin/env python3
"""Deploy ST1-081 passport index visibility to the private stack."""
from __future__ import annotations

import subprocess
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RDAPP_HOST = "enterprise-ai-rdapp"
RDDB_HOST = "enterprise-ai-rddb"
REMOTE_APP = "/opt/enterprise-ai/ingestion-service/app.py"
REMOTE_DEPLOY_DIR = "/opt/enterprise-ai/deploy"
REMOTE_EVIDENCE_ROOT = "/var/tmp/enterprise-ai-evidence"


def run(args: list[str], timeout_ms: int = 120000) -> str:
    result = subprocess.run(args, text=True, capture_output=True, timeout=timeout_ms / 1000)
    if result.returncode:
        raise SystemExit(result.stderr.strip() or result.stdout.strip() or f"command failed: {' '.join(args)}")
    return result.stdout.strip()


def ssh(host: str, command: str, timeout_ms: int = 120000) -> str:
    return run(["ssh.exe", "-o", "BatchMode=yes", host, command], timeout_ms=timeout_ms)


def scp(local_path: Path, host: str, remote_path: str, timeout_ms: int = 120000) -> None:
    run(["scp.exe", str(local_path), f"{host}:{remote_path}"], timeout_ms=timeout_ms)


def main() -> None:
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    rdapp_backup_dir = f"{REMOTE_EVIDENCE_ROOT}/st1-081-{stamp}-rdapp"
    rddb_backup_dir = f"{REMOTE_EVIDENCE_ROOT}/st1-081-{stamp}-rddb"

    ssh(RDAPP_HOST, f"mkdir -p {rdapp_backup_dir} && cp {REMOTE_APP} {rdapp_backup_dir}/app.py.bak")
    ssh(
        RDDB_HOST,
        " && ".join(
            [
                f"mkdir -p {rddb_backup_dir}",
                (
                    "docker exec postgres-db psql -U postgres -d enterprise_ai_ingestion_mvp "
                    f"-tAc \"SELECT pg_get_viewdef('ingestion.sdas_assurance_passport_index_projection'::regclass, true);\" "
                    f"> {rddb_backup_dir}/passport-index-view-before.sql || true"
                ),
            ]
        ),
    )

    migration = ROOT / "migrations" / "026_add_sdas_assurance_passport_index_projection.sql"
    sql = migration.read_text(encoding="utf-8").replace('"', '\\"')
    ssh(
        RDDB_HOST,
        (
            "docker exec -i postgres-db psql -U postgres -d enterprise_ai_ingestion_mvp "
            f"-v ON_ERROR_STOP=1 -c \"{sql}\""
        ),
        timeout_ms=240000,
    )

    scp(ROOT / "implementation" / "ingestion-service" / "app.py", RDAPP_HOST, f"{REMOTE_APP}.st1_081")
    ssh(RDAPP_HOST, f"mv {REMOTE_APP}.st1_081 {REMOTE_APP}")
    ssh(
        RDAPP_HOST,
        f"cd {REMOTE_DEPLOY_DIR} && docker compose config > /dev/null && docker compose build ingestion-service && docker compose up -d ingestion-service",
        timeout_ms=600000,
    )
    print(
        f"applied_st1_081_passport_index_visibility rdapp_backup_dir={rdapp_backup_dir} "
        f"rddb_backup_dir={rddb_backup_dir}"
    )


if __name__ == "__main__":
    main()
