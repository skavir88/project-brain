# SDAS Evidence Resolution

Authority evidence is append-only and scoped by subject (`source`,
`document_class`, or `record`), scope, accountable actor, evidence reference,
effective period, assertion time, verification method, and policy version.
Allowed bases are `authoritative_by_registered_system`,
`authoritative_by_accountable_owner`,
`authoritative_by_approved_document_class`, `corroborated_authority`,
`declared_not_verified`, `conflicting_authority`, and `authority_not_verified`.
Revocation/supersession is a later immutable assertion event; it cannot alter
prior evidence or fabricate native acquisition evidence.

Business-time evidence is independent of acquisition/filesystem time. Order of
use is: explicit approved `event_date`/`effective_date`, then approved
`report_period`, `issue_date`, or `approval_date`; `acquisition_timestamp`
and `filesystem_timestamp` are audit/discovery facts only and never business
substitutes. Conflicting values route to `human_required`; absent values stay
missing.

## Minimum human attestation

An accountable actor may assert: “This source or document class is
authoritative for **[subject]** within **[scope]** from **[effective_from]**
until revoked, verified by **[method/evidence reference]** under
**[policy/version]**.” The actor must also identify any report period, issue,
effective, event, or approval date they are attesting. This assertion is
policy-consumable, append-only, scoped, attributed, versioned, and cannot
retroactively change acquisition evidence.
