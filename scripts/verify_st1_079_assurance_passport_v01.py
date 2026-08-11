#!/usr/bin/env python3
"""Verify the local SDAS Assurance Passport v0.1 contract helpers."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SERVICE_DIR = ROOT / "implementation" / "ingestion-service"
IMAGE = "enterprise-ai-st1-079-passport-v01-test"

SNIPPET = r"""
import json,app

def mk_row(*, base_result, reliance_state, provenance_link_valid, assurance_chain_valid, consumption_chain_valid, post_event_type=None):
    return (
        'k'*64, 'a'*64, 'record-1', 'source-1', 'record-1',
        'passed', None, None, None,
        10, 'reviewer', None, 'cert-policy-v1',
        'SDAS-2', 'certified_assured', 'assurance-policy-v1',
        'eligible', 'valid', 'low', 'historical', reliance_state,
        'policy_automatic', 'policy-id', 'policy-v1', 'policy_automatic',
        'verified', 'authoritative', 1, True, [],
        base_result,
        ['currentness_limited'] if base_result != 'INTEGRITY_FAILURE' else ['provenance_link_mismatch'],
        provenance_link_valid, assurance_chain_valid, consumption_chain_valid,
        1, None, post_event_type, None,
        ['all_required_policy_evidence_present'],
        ['synthetic_assurance'],
    )

verified_payload = app.row_to_passport_payload(
    mk_row(
        base_result='VERIFIED_WITH_LIMITATIONS',
        reliance_state='not_eligible',
        provenance_link_valid=True,
        assurance_chain_valid=True,
        consumption_chain_valid=True,
    ),
    True,
)
integrity_payload = app.row_to_passport_payload(
    mk_row(
        base_result='INTEGRITY_FAILURE',
        reliance_state='not_eligible',
        provenance_link_valid=False,
        assurance_chain_valid=False,
        consumption_chain_valid=True,
    ),
    False,
)

print(json.dumps({
    'verified_contract_version': verified_payload['contract_version'],
    'verified_result': verified_payload['verification_result'],
    'verified_dimension_keys': sorted(verified_payload['dimensions'].keys()),
    'verified_reliance_dimension': verified_payload['dimensions']['reliance']['status'],
    'integrity_result': integrity_payload['verification_result'],
    'integrity_dimension': integrity_payload['dimensions']['integrity']['status'],
    'integrity_provenance_dimension': integrity_payload['dimensions']['provenance']['status'],
}, sort_keys=True, separators=(',',':')))
"""


def main() -> None:
    build = subprocess.run(["docker", "build", "-t", IMAGE, str(SERVICE_DIR)], text=True, capture_output=True)
    if build.returncode:
        raise SystemExit(build.stderr.strip() or "ST1-079 local image build failed")
    run = subprocess.run(["docker", "run", "--rm", "--entrypoint", "python", IMAGE, "-c", SNIPPET], text=True, capture_output=True)
    if run.returncode:
        raise SystemExit(run.stderr.strip() or "ST1-079 passport contract verification failed")
    print(run.stdout.strip())


if __name__ == "__main__":
    main()
