#!/usr/bin/env python3
"""Emit a deterministic fingerprint for the parked ST1-078 external gate."""
from __future__ import annotations

import argparse
import json
from hashlib import sha256


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--e1", default="MISSING")
    parser.add_argument("--e2", default="MISSING")
    parser.add_argument("--e3", default="PARTIAL")
    parser.add_argument("--real-active-delegations", type=int, default=0)
    parser.add_argument("--policy-automatic-available", action="store_true")
    args = parser.parse_args()

    payload = {
        "candidate_class_id": "project_controls_progress_workbook",
        "external_gate": "WAITING_FOR_EXTERNAL_EVIDENCE",
        "e1": args.e1,
        "e2": args.e2,
        "e3": args.e3,
        "real_active_delegations": args.real_active_delegations,
        "real_policy_automatic_path_available": args.policy_automatic_available,
    }
    fingerprint = sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    print(json.dumps({"gate_state": payload, "dependency_fingerprint": fingerprint}, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
