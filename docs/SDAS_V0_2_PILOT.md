# SDAS v0.2 Private Pilot Contract

SDAS v0.2 is a private Enterprise AI pilot. It does not establish legal
assurance, authority, currentness, reliance eligibility, or automatic
certification.

| Edge | Required evidence | Actor | Timestamp | Integrity | Failure / missing behavior |
|---|---|---|---|---|---|
| Source → Acquisition | stable source ID, type, purpose, declared authority scope | registered source/service actor | acquisition time | source and evidence fingerprints | route `human_required`; never infer authority |
| Acquisition → Original Object | acquisition ID, reference, media/size when available | acquisition actor | acquisition time | original fingerprint + immutable evidence hash | `human_required` when absent; reject malformed integrity |
| Original Object → Transformation | parent acquisition, tool/version, input/output fingerprints, coordinates | transformation service | transform time | deterministic flag and transformation hash | `human_required` for missing lineage; reject integrity failure |
| Record → Policy Decision | persisted validation/duplicate/provenance facts and enabled policy version | `sahra_policy_engine` | decision time | immutable policy decision hash | deterministic `policy_automatic`, `human_required`, or `reject_or_quarantine` |
| Review → Certification | explicit accountable human approval and existing lifecycle eligibility | human reviewer and certification actor | review/certification times | existing append-only certification audit | no approval means no certification; automatic policy is insufficient |
| Certification → Registration | CK identity, audit linkage, certification policy | registration service | registration time | registration hash | registration is rejected if linkage is absent; no overwrite |
| Registration → Lifecycle | event type, actor, reason, evidence reference/fingerprint | authorized actor | event time | append-only event hash | inactive until separately approved; no implicit supersession/revocation |
| Certified Knowledge → Consumption | consumer, purpose, output/provenance fingerprints, retrieval policy/threshold | consuming application | consumption time | append-only chained event hash | reject malformed/unqualified consumption; do not claim use if missing |

Evidence quality is always explicit: `native`, `corroborated_historical`,
`reconstructed`, `declared_unverified`, or `missing`. Backfilled evidence is
never native. Historical reconstructed records remain human-review-required
for v0.2 native-policy purposes.

## Policy safety

The runtime evaluator tests the following deterministic outcomes:

- complete permitted native evidence including verified authority:
  `policy_automatic`;
- incomplete lineage, unverified authority, conflict, or outside scope:
  `human_required`;
- duplicate, disabled/expired policy, failed integrity, or failed validation:
  `reject_or_quarantine`.

`policy_automatic != human_approved` and it never invokes certification.
The existing certification lifecycle remains the only certification path.
Policy enable/disable state is itself append-only evidence. A later
`disabled` status event blocks subsequent decisions for that policy/version;
rollback is a separately evidenced later status event, not an update or
deletion of prior policy evidence.
