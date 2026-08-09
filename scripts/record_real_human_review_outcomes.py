"""Record explicit real-data Human Review outcomes in a local-only audit file."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path


ALLOWED = {"APPROVE", "REJECT", "NEEDS_MORE_EVIDENCE", "CONFLICT"}


def main() -> int:
    package_path = os.environ.get("EAI_REVIEW_PACKAGE_INPUT")
    output_path = os.environ.get("EAI_REVIEW_OUTCOMES_OUTPUT")
    decisions_value = os.environ.get("EAI_REVIEW_DECISIONS_JSON")
    actor = os.environ.get("EAI_REVIEW_ACTOR", "user")
    if not package_path or not output_path or not decisions_value:
        raise SystemExit("EAI_REVIEW_PACKAGE_INPUT, EAI_REVIEW_OUTCOMES_OUTPUT, and EAI_REVIEW_DECISIONS_JSON are required")
    package = json.loads(Path(package_path).read_text(encoding="utf-8"))
    decisions = json.loads(decisions_value)
    candidates = package["review_items"]
    candidate_ids = {candidate["review_item_id"] for candidate in candidates}
    if set(decisions) != candidate_ids or not all(value in ALLOWED for value in decisions.values()):
        raise SystemExit("decisions must contain exactly one permitted value for every candidate")
    audit_events = [
        {
            "event_type": "human_review_decision",
            "candidate_id": candidate["review_item_id"],
            "actor_identifier": actor,
            "decision": decisions[candidate["review_item_id"]],
            "certification_performed": False,
            "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        }
        for candidate in candidates
    ]
    result = {
        "schema_version": "st1-016-human-review-outcomes-v1",
        "source_alias": package["source_alias"],
        "review_package_reference": Path(package_path).name,
        "events": audit_events,
        "policy": {"certification_performed": False, "stored_outside_git": True},
    }
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "recorded_event_count": len(audit_events),
        "decision_counts": {value: list(decisions.values()).count(value) for value in sorted(set(decisions.values()))},
        "certification_performed": False,
        "raw_review_data_outside_git": True,
    }, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
