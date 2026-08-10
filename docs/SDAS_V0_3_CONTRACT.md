# SDAS Authority & Automated Assurance Framework v0.3

This private pilot is inspired by entity/activity/agent provenance, data
quality, zero-trust, and audit principles; it claims no formal compliance.
Every decision traces Source → Acquisition → Integrity → Transformation →
Business Time → Authority → Validation → Policy → Certification → Knowledge →
Consumption without overwriting prior lineage.

Authority is scoped across governance authority, accountable role, source
system/identity, project/domain, document class, fact class, permitted and
prohibited claims, effective period, evidence, conflict and revocation rules.
Exact matching is required; any mismatch is no inheritance. LOW operational
reported facts may be automatic only when all controls pass; MEDIUM is review
by default; HIGH (financial, legal, contractual, safety, executive current
status) remains Human Review.

Certified, authoritative, current, reliance-eligible, and insured/guaranteed
are separate states. Reliance is always `not_eligible` in this pilot.
Currentness is independently assessed; latest verified period is not current
status. Missing/ambiguous authority or business time routes to Human Review;
integrity/validation failure routes to quarantine.
