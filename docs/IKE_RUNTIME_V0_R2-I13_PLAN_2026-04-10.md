# IKE Runtime v0 - R2-I13 Plan

Date: 2026-04-10
Phase: `R2-I13 Live Route Freshness Closure`
Status: `candidate`

## Goal

Close the newly observed gap between:

- current code/test proof for the DB-backed inspect route
- current canonical `127.0.0.1:8000` live route surface

## Current Evidence

Observed on 2026-04-10:

1. `POST /api/ike/v0/runtime/service-preflight/inspect` returns healthy data
2. the same live service reports:
   - `controller_acceptability.status = blocked_owner_mismatch`
   - `controller_promotion.status = not_promotable`
3. `POST /api/ike/v0/runtime/task-lifecycle/db-proof/inspect` currently
   returns `404 Not Found` on the live canonical service

## Proposed Shape

1. confirm whether the current live-service mismatch is:
   - stale service process
   - incomplete route freshness detection
   - both
2. implement the narrowest correction that makes controller-visible truth
   honest:
   - either live route availability after controlled refresh
   - or machine-readable detection that the live service does not expose the
     expected route set
3. add one durable result record with explicit claim boundary

## Success Condition

`R2-I13` should count as successful only if one of these becomes true:

1. canonical `8000` now serves the DB-backed inspect route live and the result
   is durably recorded
2. the runtime inspect/preflight surface now truthfully reports the live route
   mismatch instead of allowing controller review to infer freshness from the
   file tree alone

## Failure Condition

`R2-I13` fails if it:

- keeps the live `404` gap implicit
- claims the route is live without proving it
- broadens into service orchestration or deployment work
