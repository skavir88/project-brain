#!/usr/bin/env python3
"""Run ST1-067 policy-gate checks in the ingestion service's own image."""

from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SERVICE_DIR = ROOT / "implementation" / "ingestion-service"
IMAGE = "enterprise-ai-st1-067-policy-test"
CHECK = (
    "import json,app; "
    "facts=dict(policy_enabled=True,policy_effective=True,source_type_allowed=True,"
    "data_class_allowed=True,source_authority_verified=True,acquisition_present=True,"
    "transformation_present=True,integrity_valid=True,validation_passed=True,"
    "duplicate=False,conflict=False); "
    "inactive=app.evaluate_sdas_governance_bootstrap_policy(delegation_active=False,**facts); "
    "active=app.evaluate_sdas_governance_bootstrap_policy(delegation_active=True,**facts); "
    "assert inactive == ('human_required',['delegation_not_active']); "
    "assert active == ('policy_automatic',['all_required_policy_evidence_present']); "
    "print(json.dumps({'inactive_outcome':inactive[0],'inactive_reason':inactive[1],"
    "'active_complete_synthetic_outcome':active[0],'automatic_certification':False},separators=(',',':')))"
)


def run(*command: str) -> None:
    result = subprocess.run(command, text=True, capture_output=True)
    if result.returncode:
        raise SystemExit(result.stderr.strip() or "ST1-067 policy-gate verification failed")
    if result.stdout.strip():
        print(result.stdout.strip())


def main() -> None:
    run("docker", "build", "-t", IMAGE, str(SERVICE_DIR))
    run("docker", "run", "--rm", "--entrypoint", "python", IMAGE, "-c", CHECK)


if __name__ == "__main__":
    main()
