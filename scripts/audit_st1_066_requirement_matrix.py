#!/usr/bin/env python3
"""Build a requirement-by-requirement evidence matrix for ST1-066.

This is a local-only audit. It evaluates the current repository evidence
against the explicit requirements in the ST1-066 objective text and does not
mutate any runtime state.
"""

from __future__ import annotations

import json


def main() -> int:
    requirements = [
        {
            "requirement_id": "ST1-066-OBJ-001",
            "requirement": "A REAL organizational record must reach policy_automatic through SDAS v0.3.",
            "status": "NOT_YET_PROVEN",
            "evidence": [
                "evidence/sanitized/2026-08-11-st1-129-st1-066-readiness-audit.json",
                "CURRENT_STATE.md#ST1-120 Blocked Arrival Audit",
            ],
            "why_not_yet_proven": "No real selected-series bundle and no real selected-series native-record artifact have yet reached the runtime path.",
        },
        {
            "requirement_id": "ST1-066-OBJ-002",
            "requirement": "The path must not weaken any trust control.",
            "status": "PROVEN_SO_FAR",
            "evidence": [
                "CURRENT_STATE.md#ST1-135 First Real A1 Attestation Intake",
                "CURRENT_STATE.md#ST1-136 Post-A1 Submission Gate",
                "evidence/sanitized/2026-08-11-st1-136-post-a1-submission-gate.json",
            ],
            "notes": "All recent progress preserved non-activation, non-certification, and no-new-source-boundary constraints.",
        },
        {
            "requirement_id": "ST1-066-OBJ-003",
            "requirement": "The first real path must stop before automatic certification.",
            "status": "PROVEN_PREPARATION_ONLY",
            "evidence": [
                "evidence/sanitized/2026-08-11-st1-113-pre-certification-hard-stop-gate.json",
                "evidence/sanitized/2026-08-11-st1-119-execution-conformance.json",
            ],
            "notes": "Hard stop mechanics are proven synthetically; no real policy_automatic record has reached that gate yet.",
        },
        {
            "requirement_id": "ST1-066-A-001",
            "requirement": "Select one already-authorized, bounded, recurring, LOW-risk real document/data class from existing Maroon pilot sources.",
            "status": "PROVEN",
            "evidence": [
                "evidence/sanitized/2026-08-11-st1-122-first-real-policy-target.json",
                "CURRENT_STATE.md#ST1-122 First Real Policy-Automatic Target Realignment",
            ],
        },
        {
            "requirement_id": "ST1-066-A-002",
            "requirement": "Do NOT use ST1-061 as the success target.",
            "status": "PROVEN",
            "evidence": [
                "evidence/sanitized/2026-08-11-st1-122-first-real-policy-target.json",
                "NEXT_TASK.md",
            ],
        },
        {
            "requirement_id": "ST1-066-A-003",
            "requirement": "If no existing real source can satisfy the evidence without a real authority delegation, report the exact governance gap.",
            "status": "PROVEN",
            "evidence": [
                "evidence/sanitized/2026-08-11-st1-136-remaining-input-request-pack.json",
                "evidence/sanitized/2026-08-11-st1-136-completion-pack.json",
                "NEXT_TASK.md",
            ],
        },
        {
            "requirement_id": "ST1-066-B-001",
            "requirement": "Determine the minimum real governance objects required for the selected class.",
            "status": "PROVEN_PREPARATION_ONLY",
            "evidence": [
                "docs/ST1_076_PROJECT_CONTROLS_PROGRESS_WORKBOOK_BUNDLE.md",
                "docs/ST1_136_SELECTED_SERIES_COMPLETION_PACK_FA.md",
                "evidence/sanitized/2026-08-11-st1-124-series-governance-intake-kit.json",
            ],
            "notes": "Objects are specified and machine-checkable, but not all real evidence has arrived.",
        },
        {
            "requirement_id": "ST1-066-B-002",
            "requirement": "Do not create a real human/organizational authority delegation unless already validly approved.",
            "status": "PROVEN_SO_FAR",
            "evidence": [
                "CURRENT_STATE.md#ST1-135 First Real A1 Attestation Intake",
                "CURRENT_STATE.md#ST1-136 Completion Pack",
            ],
        },
        {
            "requirement_id": "ST1-066-B-003",
            "requirement": "If authority is the only missing requirement, prepare the smallest scoped delegation/attestation decision for the user.",
            "status": "PARTIALLY_APPLICABLE",
            "evidence": [
                "docs/ST1_070_BUSINESS_ATTESTATION_PACK.md",
                "docs/ST1_123_RECURRING_WORKBOOK_GOVERNANCE_REQUEST_FA.md",
                "docs/ST1_136_SELECTED_SERIES_COMPLETION_PACK_FA.md",
            ],
            "notes": "The path is beyond generic delegation design. One real A1 attestation exists; remaining gaps are A2, A3, source-registration evidence, stable series identifier, and the real native-record artifact.",
        },
        {
            "requirement_id": "ST1-066-C-001",
            "requirement": "Once already-authorized evidence requirements are satisfied, ingest one real record natively through registered source → acquisition → fingerprint → transformation → validation → business-time → authority → risk → policy decision.",
            "status": "NOT_YET_PROVEN",
            "evidence": [
                "evidence/sanitized/2026-08-11-st1-120-blocked-arrival-audit.json",
                "evidence/sanitized/2026-08-11-st1-136-post-a1-submission-gate.json",
            ],
            "why_not_yet_proven": "Real evidence requirements are still incomplete, so no real selected-series record has traversed the native path.",
        },
        {
            "requirement_id": "ST1-066-C-002",
            "requirement": "Expected success path is policy_automatic meaning routine Human Review is not required under this policy.",
            "status": "PROVEN_PREPARATION_ONLY",
            "evidence": [
                "evidence/sanitized/2026-08-11-st1-132-selected-series-dual-input-gate.json",
                "evidence/sanitized/2026-08-11-st1-136-post-a1-submission-gate.json",
            ],
            "notes": "The selected-series path to controlled review is proven synthetically, but no real record has yet reached policy_automatic.",
        },
        {
            "requirement_id": "ST1-066-C-003",
            "requirement": "policy_automatic must NOT mean human_approved/certified/current/reliance_eligible/insured.",
            "status": "PROVEN_SO_FAR",
            "evidence": [
                "CURRENT_STATE.md#ST1-121 Limited Pilot Governance Bootstrap",
                "docs/ST1_136_SELECTED_SERIES_COMPLETION_PACK_FA.md",
            ],
        },
        {
            "requirement_id": "ST1-066-D-001",
            "requirement": "Hard stop before certification of the first real policy_automatic record.",
            "status": "PROVEN_PREPARATION_ONLY",
            "evidence": [
                "evidence/sanitized/2026-08-11-st1-113-pre-certification-hard-stop-gate.json",
                "evidence/sanitized/2026-08-11-st1-119-execution-conformance.json",
            ],
        },
        {
            "requirement_id": "ST1-066-E-001",
            "requirement": "Before stopping, simulate the policy against existing historical/native pilot records without mutating them and report routing counts/reasons/reduction/safety checks.",
            "status": "PROVEN_SIMULATION_ONLY",
            "evidence": [
                "evidence/sanitized/2026-08-11-st1-090-selected-class-operating-model.json",
                "evidence/sanitized/2026-08-11-st1-091-selected-class-exception-queue.json",
            ],
        },
        {
            "requirement_id": "ST1-066-F-001",
            "requirement": "Define the operating model so future routine batches route to X policy_automatic, Y human_review_required, and Z quarantine and only Y exceptions are reviewed.",
            "status": "PROVEN",
            "evidence": [
                "evidence/sanitized/2026-08-11-st1-090-selected-class-operating-model.json",
                "evidence/sanitized/2026-08-11-st1-091-selected-class-exception-queue.json",
            ],
        },
        {
            "requirement_id": "ST1-066-G-001",
            "requirement": "Continue autonomously through additive, local, non-destructive work required to reach the first REAL policy_automatic hard gate.",
            "status": "PROVEN_SO_FAR",
            "evidence": [
                "SESSION_LOG.md#Session 139 - 2026-08-11",
                "SESSION_LOG.md#Session 140 - 2026-08-11",
                "SESSION_LOG.md#Session 141 - 2026-08-11",
                "SESSION_LOG.md#Session 142 - 2026-08-11",
                "SESSION_LOG.md#Session 143 - 2026-08-11",
            ],
        },
        {
            "requirement_id": "ST1-066-G-002",
            "requirement": "Stop before new real governance/authority delegation, certification of first real policy_automatic record, automatic certification, reliance eligibility, insurance semantics, new source/access boundary, credential/provider/model changes, destructive operations, or weakened trust controls.",
            "status": "PROVEN_SO_FAR",
            "evidence": [
                "CURRENT_STATE.md",
                "NEXT_TASK.md",
            ],
        },
    ]

    output = {
        "task_id": "ST1-137",
        "objective": "ST1-066 requirement-by-requirement completion audit",
        "overall_status": "NOT_COMPLETE",
        "success_criterion_proven": False,
        "requirements_total": len(requirements),
        "requirements_proven_like": sum(
            1 for item in requirements if item["status"] in {"PROVEN", "PROVEN_SO_FAR", "PROVEN_PREPARATION_ONLY", "PROVEN_SIMULATION_ONLY"}
        ),
        "requirements_not_yet_proven": [
            item["requirement_id"] for item in requirements if item["status"] == "NOT_YET_PROVEN"
        ],
        "critical_missing_real_world_evidence": [
            "A2_project_controls_accountability_confirmation",
            "A3_controlled_report_definition_confirmation",
            "stable_source_registration_evidence_reference",
            "stable_non_sensitive_source_series_identifier",
            "real_selected_series_native_record_artifact",
        ],
        "requirement_matrix": requirements,
        "invariants": {
            "st1_061_is_not_success_target": True,
            "automatic_certification_enabled": False,
            "reliance_eligibility_enabled": False,
            "new_source_boundary_required": False,
        },
    }
    print(json.dumps(output, sort_keys=True, separators=(",", ":"), ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
