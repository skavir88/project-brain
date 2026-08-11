#!/usr/bin/env python3
"""Verify deployed ST1-080 passport runtime behavior on the private stack."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(args: list[str], timeout_ms: int = 120000) -> str:
    result = subprocess.run(args, text=True, capture_output=True, timeout=timeout_ms / 1000)
    if result.returncode:
        raise SystemExit(result.stderr.strip() or result.stdout.strip() or f"command failed: {' '.join(args)}")
    return result.stdout.strip()


def main() -> None:
    local_contract = json.loads(run([sys.executable, str(ROOT / "scripts" / "verify_st1_079_assurance_passport_v01.py")]))
    projection = json.loads(run([sys.executable, str(ROOT / "scripts" / "verify_st1_071_assurance_passport.py")], timeout_ms=240000))
    summary = json.loads(run([sys.executable, str(ROOT / "scripts" / "verify_st1_072_assurance_summary.py")], timeout_ms=240000))
    remote_health = json.loads(
        run(
            [
                "ssh.exe",
                "-o",
                "BatchMode=yes",
                "enterprise-ai-rdapp",
                "python3 - <<'PY'\nimport json,urllib.request,urllib.error\nout=[]\nfor path in ['/health','/v1/sdas/passport?knowledge_id=bad']:\n    try:\n        with urllib.request.urlopen('http://127.0.0.1:8081'+path) as r:\n            out.append({'path':path,'status':r.status})\n    except urllib.error.HTTPError as e:\n        out.append({'path':path,'status':e.code})\nprint(json.dumps(out,separators=(',',':')))\nPY",
            ]
        )
    )
    remote_columns = run(
        [
            "ssh.exe",
            "-o",
            "BatchMode=yes",
            "enterprise-ai-rddb",
            "docker exec postgres-db psql -U postgres -d enterprise_ai_ingestion_mvp -tAc \"SELECT string_agg(column_name, ',') FROM information_schema.columns WHERE table_schema='ingestion' AND table_name='sdas_assurance_passport_projection' AND column_name IN ('quality_gate_outcome','policy_reason_codes','assurance_reason_codes');\"",
        ]
    )
    print(
        json.dumps(
            {
                "local_contract": local_contract,
                "projection": projection,
                "summary": summary,
                "remote_health": remote_health,
                "remote_projection_columns": remote_columns,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
    )


if __name__ == "__main__":
    main()
