# ST1-066 Real Policy-Automatic Gate

Candidate class: recurring Project Controls progress workbook, restricted to
reported Plan, Actual, progress, activity, reporting-period, milestone, and
project-control issue facts. Excluded: payment, delay entitlement, claims,
financial liability, safety-critical facts, current executive status, and
reliance/insurance facts.

Required reusable policy: `project-controls-progress-low-risk/v1`; LOW risk;
native read-only acquisition, SHA-256 integrity, complete transformation
lineage, explicit report period, active scoped delegation, registered source,
exact document/fact/project match, and no conflict/revocation.

Current real governance gap: zero non-synthetic delegations and zero real
authority assertions exist. The smallest required CEO/governance decision is
to approve a named governance authority to delegate the Project Controls role
for the named registered source/system and this report class, with permitted
and prohibited facts, effective period, report-period evidence rule, and
document-control/signature requirement. That decision is reusable, not
record-specific.

Operating model: N records → X exact policy matches (`policy_automatic`) → Y
missing/conflict/high-risk exceptions (`human_required`) → Z integrity or
validation failures (`reject_or_quarantine`). Only Y is presented to Human
Review. `policy_automatic` never certifies.
