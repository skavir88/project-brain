# SDAS Delegated Data Authority

Hierarchy: Organization → Governance Authority → Accountable Role → Registered
Source/System → Document/Data Class → Record → Claim. Delegation grants a role
permission to establish scoped authority evidence; it never makes all records
or claims authoritative.

Record/claim inheritance requires an active delegation, role/source/class/fact
scope match, valid business time, integrity/provenance, no conflict or later
revocation/supersession, and any policy-required signature/document-control
evidence. Failure routes to `human_required`; integrity failure routes to
`reject_or_quarantine`.

For recurring reports, business time accepts only an approved header,
document-control period, approved report-number/date convention, registered
source-system period field, or accountable-owner attestation. Precedence is
explicit event/effective date, then report period, then issue/approval date;
filesystem and acquisition timestamps are audit-only.

ST1-061 has no real delegation, authority assertion, or qualifying business
time. It remains `authority=not_verified`, `business_time=missing_not_inferred`,
and `human_required`.

Minimum CEO decision: appoint the governance authority and approve a scoped
delegation to the Project Controls role for a named source/system, report
class, permitted facts, prohibited facts, effective period, and required
document-control/signature evidence. This can reduce per-record review for
matching recurring records, but exceptions/conflicts still require review.
