#!/usr/bin/env python3
"""Verify ST1-081 passport index visibility locally and on the private stack."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import types
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(args: list[str], timeout_ms: int = 120000) -> str:
    result = subprocess.run(args, text=True, capture_output=True, timeout=timeout_ms / 1000)
    if result.returncode:
        raise SystemExit(result.stderr.strip() or result.stdout.strip() or f"command failed: {' '.join(args)}")
    return result.stdout.strip()


def load_app_module():
    app_path = ROOT / "implementation" / "ingestion-service" / "app.py"
    spec = importlib.util.spec_from_file_location("enterprise_ai_ingestion_app", app_path)
    if spec is None or spec.loader is None:
        raise SystemExit("unable to load ingestion-service app module")
    if "psycopg" not in sys.modules:
        stub = types.ModuleType("psycopg")
        stub.Connection = object
        stub.connect = None
        sys.modules["psycopg"] = stub
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def local_synthetic_checks(module) -> dict[str, object]:
    knowledge_id = "a" * 64
    row = (
        knowledge_id,
        "b" * 64,
        "synthetic-record-001",
        321,
        module.point_id_from_knowledge_id(knowledge_id),
        "enterprise_ai_certified_knowledge_v1",
        "VERIFIED_WITH_LIMITATIONS",
        "historical",
        "not_eligible",
        None,
        datetime(2026, 8, 11, 9, 0, tzinfo=UTC),
        "synthetic-policy-v1",
        ["currentness_limited", "reliance_not_eligible"],
    )
    collection_present = {
        "collection_exists": True,
        "collection_runtime_state": "green",
        "points_count": 50,
        "vector_dimension": 3072,
        "distance_metric": "Cosine",
    }
    point_present = {
        "indexed_point_present": True,
        "payload_contract_valid": True,
        "payload_knowledge_id_match": True,
        "payload_source_fingerprint_match": True,
        "payload_source_record_id_match": True,
        "payload_certification_event_id_match": True,
        "point_runtime_state": "present",
    }
    indexed_projection = module.build_passport_index_projection_state(row=row, collection_state=collection_present, point_state=point_present)
    indexed_payload = module.row_to_passport_index_payload(row, indexed_projection)

    point_missing = {
        "indexed_point_present": False,
        "payload_contract_valid": None,
        "payload_knowledge_id_match": None,
        "payload_source_fingerprint_match": None,
        "payload_source_record_id_match": None,
        "payload_certification_event_id_match": None,
        "point_runtime_state": "missing",
    }
    nonindexed_projection = module.build_passport_index_projection_state(row=row, collection_state=collection_present, point_state=point_missing)

    payload_mismatch = {
        "indexed_point_present": True,
        "payload_contract_valid": True,
        "payload_knowledge_id_match": False,
        "payload_source_fingerprint_match": True,
        "payload_source_record_id_match": True,
        "payload_certification_event_id_match": True,
        "point_runtime_state": "present",
    }
    mismatch_projection = module.build_passport_index_projection_state(row=row, collection_state=collection_present, point_state=payload_mismatch)
    return {
        "indexed_visibility_result": indexed_projection["visibility_result"],
        "indexed_payload_contract_valid": indexed_projection["payload_contract_valid"],
        "indexed_reliance_state": indexed_payload["assurance_context"]["reliance_state"],
        "nonindexed_visibility_result": nonindexed_projection["visibility_result"],
        "payload_mismatch_visibility_result": mismatch_projection["visibility_result"],
        "boundary_flags": indexed_payload["boundaries"],
    }


def remote_runtime_checks() -> dict[str, object]:
    knowledge_id = run(
        [
            "ssh.exe",
            "-o",
            "BatchMode=yes",
            "enterprise-ai-rddb",
            (
                "docker exec postgres-db psql -U postgres -d enterprise_ai_ingestion_mvp "
                "-tAc \"SELECT knowledge_id FROM ingestion.sdas_assurance_passport_index_projection "
                "WHERE reliance_state='not_eligible' ORDER BY certification_timestamp DESC LIMIT 1;\""
            ),
        ]
    ).strip()
    if not knowledge_id:
        raise SystemExit("no certified knowledge row available for ST1-081 runtime verification")
    runtime_script = f"""python3 - <<'PY'
import json, urllib.request, urllib.error
knowledge_id = '{knowledge_id}'
paths = [
    ('indexed', '/v1/sdas/passport/index?knowledge_id=' + knowledge_id),
    ('missing', '/v1/sdas/passport/index?knowledge_id=' + ('0' * 64)),
]
out = []
for name, path in paths:
    try:
        with urllib.request.urlopen('http://127.0.0.1:8081' + path, timeout=30) as response:
            out.append({{'name': name, 'status': response.status, 'payload': json.load(response)}})
    except urllib.error.HTTPError as error:
        out.append({{'name': name, 'status': error.code, 'payload': json.load(error)}})
print(json.dumps(out, separators=(',',':')))
PY"""
    responses = json.loads(
        run(["ssh.exe", "-o", "BatchMode=yes", "enterprise-ai-rdapp", runtime_script], timeout_ms=240000)
    )
    indexed = next(item for item in responses if item["name"] == "indexed")
    missing = next(item for item in responses if item["name"] == "missing")
    return {
        "verified_knowledge_id": knowledge_id,
        "indexed_status": indexed["status"],
        "indexed_visibility_result": indexed["payload"]["index_projection"]["visibility_result"],
        "indexed_collection_exists": indexed["payload"]["index_projection"]["collection_exists"],
        "indexed_point_present": indexed["payload"]["index_projection"]["indexed_point_present"],
        "indexed_vector_dimension": indexed["payload"]["index_projection"]["vector_dimension"],
        "indexed_payload_contract_valid": indexed["payload"]["index_projection"]["payload_contract_valid"],
        "indexed_reliance_state": indexed["payload"]["assurance_context"]["reliance_state"],
        "missing_status": missing["status"],
        "missing_error": missing["payload"].get("error"),
    }


def main() -> None:
    module = load_app_module()
    print(
        json.dumps(
            {
                "local_synthetic": local_synthetic_checks(module),
                "remote_runtime": remote_runtime_checks(),
            },
            sort_keys=True,
            separators=(",", ":"),
        )
    )


if __name__ == "__main__":
    main()
