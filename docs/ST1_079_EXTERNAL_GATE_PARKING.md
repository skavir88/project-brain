# ST1-079 External Gate Parking

The selected recurring Project Controls progress workbook class remains blocked
by external organizational evidence, not by a technical defect.

Current parked state:

- `E1 = MISSING`
- `E2 = MISSING`
- `E3 = PARTIAL`
- `real_active_delegations = 0`
- `real_policy_automatic_path = unavailable`
- `external_gate = WAITING_FOR_EXTERNAL_EVIDENCE`

This parked state should reopen only when new real controlled evidence changes
one or more of those inputs for the exact selected workbook class.

## Stable dependency fingerprint

Use `scripts/fingerprint_st1_078_external_gate.py` to calculate a deterministic
fingerprint over the parked gate state.

If the fingerprint does not change, the repository should not create new
technical tasks merely to restate the same external blocker.
