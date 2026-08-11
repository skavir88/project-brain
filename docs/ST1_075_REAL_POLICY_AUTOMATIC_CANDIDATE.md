# ST1-075 Real Policy-Automatic Candidate

## Selected real candidate class

Recurring Project Controls progress workbook.

Current bounded in-scope source family anchor:

- runtime `source_id`: `enterprise_ai_real_action_plan_weekly_observation`
- existing certified historical records from this family: `10`
- existing simulated native-policy decisions from this family:
  `10 x human_required` under `sdas-low-risk-native/simulation-v1`

## Why this class was selected

This class is the strongest already-authorized real candidate for the first
truthful SDAS v0.3 `policy_automatic` hard stop because current repository
evidence already proves all of the following:

1. It is a workbook/report class, not an unstructured narrative document.
2. It contains deterministic labelled Plan/Actual/progress field groups.
3. It contains an explicit workbook-level reporting week in document content.
4. It supports sheet/cell provenance.
5. It can be constrained to LOW-risk source-attributed reported facts.
6. It does not require claiming current executive status, entitlement,
   payment, liability, safety certification, or reliance eligibility.

## Evidence anchors

- ST1-022 selected an internally dated workbook class suitable for
  row/cell-level provenance.
- ST1-031 verified deterministic workbook schema and explicit reporting-week
  semantics for the same class:
  - `Contractor Plan Progress%`
  - `Actual Progress`
  - `Activities Plan Volume`
  - `Activities Actual Volume`
  - workbook-labelled reporting week `1402/06/25–1402/06/31`
- ST1-032 verified that ten low-risk source-attributed observations from this
  class could be human-reviewed and certified historically without changing
  currentness semantics.
- Runtime simulation still routes all ten matching records to
  `human_required`, which proves the class is in scope but not yet governance-
  complete for native automatic routing.

## Not selected first

### Daily status workbook series

`enterprise_ai_real_historical_status` remains useful evidence, but it is less
suitable as the first real `policy_automatic` target because the currently
captured evidence shows:

- many snapshots with copy-forward deduplication,
- broader issue/stoppage semantics,
- greater ambiguity for first routine auto-routing,
- and no smaller governance gap than the selected weekly progress workbook.

### Management-report families

These remain valuable for executive historical status, but they are less
deterministic than the selected workbook class for the first LOW-risk policy
automatic path.

## Permitted fact classes for this candidate

Only source-attributed LOW-risk reported facts should be eligible:

- reporting period
- reported Plan values
- reported Actual values
- reported progress metrics
- reported activity status
- reported milestone status
- reported Project Controls issue/constraint observations

## Explicitly prohibited fact classes

- contractual delay determination
- entitlement or claims
- payment authorization or payment status
- financial liability
- legal conclusions
- safety/compliance certification
- final completion
- current executive status outside the stated reporting period
- reliance eligibility
- insurance/guarantee semantics

## Minimum required real governance/control objects

### Already evidenced enough to reuse as class suitability

- deterministic workbook structure
- bounded recurring class suitability
- workbook-level reporting-period field semantics
- low-risk fact-class boundary candidate

### Still missing before the first real `policy_automatic` hard stop

1. Governance authority evidence (`E1`)
   - who may approve/activate the pilot governance scope for this class

2. Project Controls / PMO accountability evidence (`E2`)
   - which organizational role is accountable for this recurring report class

3. Controlled recurring-report definition evidence (`E3`, currently `PARTIAL`)
   - owning role
   - controlled source/location class
   - deterministic reporting-period rule
   - document/version convention
   - release/approval convention if applicable

4. Real registered source/system identity for this class
   - the real source/system must be registered with exact project scope

5. Real source ownership/control verification
   - exact match between registered source, accountable role, project, and
     report class

6. Native real acquisition + integrity + transformation chain
   - read-only acquisition
   - original SHA-256
   - deterministic transformation lineage
   - business-time resolution from the approved workbook rule

7. Exact-scope active delegation bootstrap lifecycle
   - only after 1–5 are truly evidenced

## Business-time rule for this class

The reporting/business time must come from the workbook-labelled reporting-week
header or designated reporting-period field. Row-level planned dates are not
the report period and filesystem/acquisition timestamps are not business time.

## Truthful blocker conclusion

The blocker is not only "authority missing".

The smallest truthful governance gap is the unresolved A1/A2/A3 evidence set
for this exact recurring workbook class, plus absence of a registered real
source/system scoped to that class. After those are resolved, native
read-only acquisition and policy evaluation can proceed without weakening
trust controls.
