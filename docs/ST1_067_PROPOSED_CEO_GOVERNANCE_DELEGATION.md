# ST1-067 Proposed CEO Governance Delegation

Status: `proposed_for_ceo_review_not_registered`

This is a proposed SDAS v0.3 governance policy. It is not a delegation,
authority assertion, policy decision, certification, or source-authority
finding. All `REQUIRED_INPUT` values must be supplied or verified before an
append-only delegation can be created.

## Proposed Decision Fields and Rationale

| Required field | Proposed value | Rationale |
|---|---|---|
| Organization | `REQUIRED_INPUT` | The organization identity is not independently established in the current evidence. |
| Governance authority | CEO; `delegating_actor_id=REQUIRED_INPUT` | The CEO approves the policy but is not the operational data approver. A stable non-secret actor-registry identity is required. |
| Delegated accountable role | `Project Controls / PMO accountable owner` | A narrow operational role avoids inventing a named individual's authority. |
| Project/domain | `Maroon pilot project` | Limits inheritance to the approved pilot boundary. |
| Registered source/system | `REQUIRED_INPUT` | A registered, stable source-system identity has not been established for this reusable class. |
| Document/data classes | `recurring Project Controls progress/status reporting documents and workbooks` | Constrains automatic routing to a repeatable, deterministic reporting class. |
| Permitted fact classes | `report_period`, `reported_plan`, `reported_actual`, `reported_progress`, `reported_activity`, `reported_milestone`, `reported_project_control_issue` | These are low-risk, source-attributed observations only. |
| Prohibited fact classes | `contractual_delay_determination`, `entitlement`, `claim`, `payment_authorization_or_status`, `financial_liability`, `legal_conclusion`, `safety_or_compliance_certification`, `final_completion`, `current_executive_status_outside_report_period`, `reliance_eligibility`, `insurance_or_guarantee_status` | These are high-risk, legal, financial, safety, or currentness-sensitive assertions and always remain outside this delegation. |
| Business-time rule | Approved report header, registered source-system period field, document-control evidence, or accountable-owner attestation | Enforces reporting/business time without treating filesystem or acquisition time as a substitute. |
| Document-control / approval evidence | `REQUIRED_INPUT` | The approving control (for example, document-control identifier, signature/approval state, or approved reporting convention) must be specified by the accountable governance authority. |
| Native integrity requirements | Native read-only acquisition; original SHA-256; immutable acquisition event; complete transformation lineage; validation success; provenance completeness | Preserves verifiable source-to-record integrity. |
| Authority inheritance rule | All scope, time, integrity, provenance, conflict, revocation/supersession, document-control, and policy-version conditions must match exactly | Prevents a broad role or source from authorizing unrelated facts. |
| Risk tier | `LOW` only | Any non-LOW, prohibited, conflicting, or incomplete record is excluded from automatic routing. |
| Policy identifier/version | `project-controls-progress-low-risk/v1` | Provides an explicit, append-only policy scope. |
| Effective from | `REQUIRED_INPUT_AT_APPROVAL` (prospective only) | The real delegation must begin at approval time; it cannot make reconstructed historical evidence native. |
| Effective until | `null` | The delegation remains active only until append-only revocation, supersession, expiry, or scope change. |
| Revocation authority | CEO; `REQUIRED_INPUT_CEO_ACTOR_ID` | Keeps governance revocation distinct from operational reporting. |
| Audit rule | Append-only delegation, delegation events, and policy decisions; attributable actor and evidence references | Preserves reproducibility and non-repudiable lineage. |
| Certification rule | `automatic_certification=false` | `policy_automatic` bypasses routine review only; it never certifies. |
| Currentness / reliance rule | `currentness=not_assessed`; `reliance=not_eligible` | A valid delegated report fact neither proves present state nor enables reliance. |

## Machine-Readable Proposed Delegation Object

This object is deliberately not insertable until all `REQUIRED_INPUT` values
are replaced through CEO-approved, independently evidenced governance data.

```json
{
  "status": "proposed_for_ceo_review_not_registered",
  "delegation_id": "REQUIRED_INPUT_GENERATED_AFTER_APPROVAL",
  "delegating_actor_id": "REQUIRED_INPUT_CEO_ACTOR_ID",
  "organization": "REQUIRED_INPUT",
  "delegated_role": "Project Controls / PMO accountable owner",
  "data_domain": "maroon_pilot_project",
  "source_system_scope": {
    "registered_source_system_id": "REQUIRED_INPUT",
    "project_scope": "maroon_pilot_project",
    "required_document_control_evidence": "REQUIRED_INPUT"
  },
  "document_data_classes": [
    "recurring_project_controls_progress_report",
    "recurring_project_controls_status_report",
    "recurring_project_controls_progress_workbook"
  ],
  "permitted_fact_classes": [
    "report_period",
    "reported_plan",
    "reported_actual",
    "reported_progress",
    "reported_activity",
    "reported_milestone",
    "reported_project_control_issue"
  ],
  "prohibited_fact_classes": [
    "contractual_delay_determination",
    "entitlement",
    "claim",
    "payment_authorization_or_status",
    "financial_liability",
    "legal_conclusion",
    "safety_or_compliance_certification",
    "final_completion",
    "current_executive_status_outside_report_period",
    "reliance_eligibility",
    "insurance_or_guarantee_status"
  ],
  "business_time_rule": {
    "accepted_evidence": [
      "approved_report_header",
      "registered_source_system_period_field",
      "document_control_evidence",
      "accountable_owner_attestation"
    ],
    "disallowed_substitutes": [
      "filesystem_timestamp",
      "acquisition_timestamp"
    ]
  },
  "inheritance_requirements": {
    "active_delegation": true,
    "exact_source_system_match": true,
    "exact_project_match": true,
    "exact_document_class_match": true,
    "exact_fact_class_match": true,
    "valid_business_period": true,
    "native_integrity_evidence": true,
    "complete_provenance": true,
    "no_conflict": true,
    "no_revocation_or_supersession": true,
    "document_control_evidence": true,
    "exact_policy_version": "project-controls-progress-low-risk/v1"
  },
  "risk_tier": "LOW",
  "policy_version": "project-controls-progress-low-risk/v1",
  "effective_from": "REQUIRED_INPUT_AT_APPROVAL",
  "effective_until": null,
  "revocation_authority_actor_id": "REQUIRED_INPUT_CEO_ACTOR_ID",
  "delegation_basis_reference": "REQUIRED_INPUT_CEO_APPROVAL_REFERENCE",
  "automatic_certification": false,
  "currentness_state": "not_assessed",
  "reliance_state": "not_eligible"
}
```

## Proposed CEO Decision Statement

> As CEO and Enterprise AI governance authority for `REQUIRED_INPUT_ORGANIZATION`,
> I approve a prospective, scoped delegation to the **Project Controls / PMO
> accountable owner** (`REQUIRED_INPUT_ROLE_REFERENCE`) for the registered
> Project Controls source/system `REQUIRED_INPUT_SOURCE_SYSTEM_ID`, limited to
> the Maroon pilot project and recurring Project Controls progress/status
> reporting documents and workbooks.
>
> The delegation permits only source-attributed LOW-risk reported facts:
> reporting period, Plan, Actual, progress metrics, Project Controls
> activities, milestones, and Project Controls issues/constraints. It excludes
> contractual delay determinations, entitlement, claims, payment
> authorization/status, financial liability, legal conclusions, safety or
> compliance certification, final completion, current executive status outside
> the reporting period, reliance eligibility, and insurance/guarantee status.
>
> Authority inheritance requires exact scope matching, valid business time,
> native integrity evidence, complete provenance, `REQUIRED_INPUT_DOCUMENT_CONTROL_EVIDENCE`,
> no conflict, no revocation/supersession, and policy
> `project-controls-progress-low-risk/v1`. The delegation takes effect
> prospectively at `REQUIRED_INPUT_APPROVAL_TIMESTAMP` and remains active until
> an append-only revocation, supersession, expiry, or scope change.
>
> A matching LOW-risk record may route to `policy_automatic`, meaning routine
> Human Review is not required under that policy. This does not mean human
> approval, certification, currentness, reliance eligibility, insurance, or
> guarantee. Automatic certification is not authorized.

## Unresolved Required Inputs

1. `REQUIRED_INPUT_ORGANIZATION`.
2. `REQUIRED_INPUT_CEO_ACTOR_ID` registered in the SDAS actor registry.
3. `REQUIRED_INPUT_ROLE_REFERENCE` for the accountable Project Controls / PMO role.
4. `REQUIRED_INPUT_SOURCE_SYSTEM_ID` for the registered Project Controls source/system.
5. `REQUIRED_INPUT_DOCUMENT_CONTROL_EVIDENCE` acceptable for this report class.
6. `REQUIRED_INPUT_CEO_APPROVAL_REFERENCE` and prospective approval timestamp.

### Read-Only Registry Check

The 2026-08-10 aggregate registry check found three native-evidence actor
entries and two native-evidence source entries, but zero registered CEO-role
matches, zero Project Controls/PMO-role matches, and zero sources with an
authority status beyond `declared_unverified`. It therefore cannot supply any
of the required identities or source-control fields above.

## Expected Human Review Reduction

The verified current baseline is **zero** real automatic routes: 50 existing
records remain `human_required`. After approval, the reduction is conditional:
each new record that satisfies every exact LOW-risk control may avoid routine
Human Review. The numeric reduction cannot be estimated truthfully until the
registered source-system identity, report class, and eligible native batch are
known. All exceptions remain Human Review or quarantine.

## Risks and Exclusions

- This proposal never proves source authority, document approval, report
  currentness, or factual correctness by filename, folder, filesystem time, or
  acquisition time.
- Historical reconstructed evidence remains reconstructed/retrospective unless
  independently supported; it is not made native by this delegation.
- ST1-061 remains `human_required` unless its missing authority and
  business-time evidence are separately resolved.
- Legal, financial, safety, payment, claims, executive-currentness, and
  reliance matters remain excluded regardless of otherwise matching metadata.

## Automatic Actions After Approval

1. Validate all required inputs and register the CEO actor/role/source only if
   the supplied identities are independently valid.
2. Append one scoped delegation and `created` event; never overwrite history.
3. Evaluate only exact matching, newly acquired native LOW-risk records.
4. Route complete matches to `policy_automatic`; route missing or ambiguous
   evidence to `human_required`; route integrity/validation failures to
   `reject_or_quarantine`.
5. Produce sanitized audit evidence and stop before certification of the first
   real `policy_automatic` record.

## What Still Requires Human Review

- Any fact outside the permitted LOW-risk classes.
- Missing, ambiguous, conflicting, expired, revoked, superseded, or
  out-of-scope evidence.
- MEDIUM/HIGH-risk claims and all prohibited classes.
- Any certification decision, including a record that is `policy_automatic`.

## Non-Mutation Confirmation

No real delegation, actor, authority assertion, policy decision,
certification, Certified Knowledge projection, Qdrant index, or source access
has been created or changed by preparing this proposal.
