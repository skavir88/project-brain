# ST1-079 Assurance Passport Gap Matrix

| Capability | Exists? | Source of truth | Missing control | Implementation required? |
|---|---|---|---|---|
| Claim identity | Yes | `credibility_records`, `certified_knowledge_items` | Versioned passport contract surface | Yes |
| Source identity | Yes | `sdas_source_registry`, `credibility_records` | Dimension-level projection | Yes |
| Native acquisition evidence | Yes | `sdas_acquisition_events` | Passport exposure | Yes |
| Original fingerprint continuity | Partial | `credibility_records`, `certified_knowledge_items`, `sdas_acquisition_events` | Explicit integrity classification | Yes |
| Transformations | Yes | `sdas_transformations` | Deterministic exposure in passport | Yes |
| Transformation fingerprints | Partial | `sdas_transformations` | Direct dimension-level explanation | Yes |
| Validation result | Partial | `credibility_records.quality_gate_outcome` | Passport exposure | Yes |
| Business/effective time | Yes | `sdas_business_time_evidence`, `sdas_assurance_decisions` | Dimension-level state and limitations | Yes |
| Actor/assertor | Partial | `certification_audit_events`, `sdas_authority_assertions`, `sdas_actor_registry` | Unified per-passport read contract | Yes |
| Authority assertion/delegation | Yes | `sdas_authority_assertions`, `sdas_active_delegation_bootstrap`, `sdas_assurance_decisions` | Stable parked external dependency marker | Yes |
| Policy and policy version | Yes | `sdas_policy_decisions`, `sdas_policy_versions` | Reason-code exposure in passport | Yes |
| Human Review involvement | Partial | `sdas_policy_decisions`, certification audit | Explicit dimension contract | Yes |
| Certification | Yes | `certification_audit_events`, `certified_knowledge_items` | Dimension contract | Yes |
| Certification policy | Yes | `certified_knowledge_items`, `certification_audit_events` | Dimension contract | Yes |
| SDAS assessment | Yes | `sdas_assurance_envelopes`, `sdas_assurance_decisions`, `sdas_assurance_events` | Explicit verifier outcomes | Yes |
| Currentness | Yes | `sdas_assurance_decisions` | Dimension contract | Yes |
| Reliance eligibility | Yes | `sdas_assurance_decisions` | Deterministic downgrade and dimension contract | Yes |
| Conflict state | Partial | `sdas_authority_assertions`, `sdas_business_time_evidence` | Independent dimension and reason-code exposure | Yes |
| Revocation | Yes | `sdas_post_registration_events`, `sdas_authority_assertions` | Independent dimension contract | Yes |
| Supersession | Yes | `sdas_post_registration_events`, `sdas_authority_assertions` | Independent dimension contract | Yes |
| Certified Knowledge projection | Yes | `certified_knowledge_items` | Integrated passport explanation | Yes |
| Vector/index projection | Partial | Qdrant / Dify bridge runtime | Safe passport-bound exposure is not yet implemented | No for ST1-079 |
| Consumption history | Yes | `sdas_consumption_events` | Explicit dimension and chain verification | Yes |
| Evidence/hash-chain integrity | Partial | `sdas_assurance_events`, `sdas_consumption_events`, fingerprint links | Separate `INTEGRITY_FAILURE` outcome | Yes |

## Conclusion

The repository already had most source-of-truth evidence needed for an
Assurance Passport. The real missing layer was not more storage but a
versioned, deterministic, dimension-based read contract and verifier over the
existing append-only truth.
