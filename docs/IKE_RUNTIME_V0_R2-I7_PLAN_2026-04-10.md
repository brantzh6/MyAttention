# IKE Runtime v0 - R2-I7 Plan

Date: 2026-04-10
Phase: `R2-I7 DB-Backed Inspect Surface`
Status: `candidate`

## Goal

Expose one controller-facing inspect route for the durable DB-backed lifecycle
proof, while keeping the route explicitly non-executive and non-general.

## Proposed Shape

1. reuse `execute_db_backed_lifecycle_proof()`
2. add one inspect-style route in `ike_v0`
3. return:
   - proof audit summary
   - truth-boundary flags
   - explicit non-goals
4. add focused router tests

## Preferred Semantics

The route should be honest about what it does:

- it executes one bounded proof helper
- it persists one lifecycle path as part of that proof
- it is not a general task runner
- it is not detached execution

## Success Condition

`R2-I7` should count as successful only if:

1. the route is inspect-scoped and explicitly bounded
2. the returned payload exposes durable-proof semantics truthfully
3. controller-facing truth-boundary flags make the non-goals explicit
4. focused tests prove the route does not imply broader orchestration

## Failure Condition

`R2-I7` fails if it:

- blurs inspect vs execute semantics
- introduces reusable general task execution semantics
- hides persistence side effects
- claims scheduler-like capability
