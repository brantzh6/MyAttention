# IKE Runtime v0 - R2-I5 Plan

Date: 2026-04-10
Phase: `R2-I5 PG-Backed Lifecycle Proof`
Status: `candidate`

## Goal

Close the semantic gap between:

- state-machine lifecycle proof
- PG-backed lifecycle fact path

by proving one narrow lifecycle through durable runtime truth.

## Proposed Proof Shape

1. create one runtime project
2. create one runtime task in `inbox` or `ready`
3. execute one controller/delegate/controller lifecycle through:
   - `runtime_tasks`
   - `runtime_worker_leases`
   - `runtime_task_events`
4. verify lifecycle truth from persisted rows, not only returned in-memory
   structures

## Preferred Implementation Shape

Prefer a narrow DB-backed helper first, then optionally a narrow inspect route
if needed.

Priority order:

1. DB-backed helper
2. focused DB-backed tests
3. only then decide whether a route is needed

## Success Condition

`R2-I5` should only count as successful if all of the following are true:

1. a lease-backed delegate claim is verified through `PostgresClaimVerifier`
2. task status changes are durably reflected in `runtime_tasks`
3. transition history is durably reflected in `runtime_task_events`
4. lease ownership is durably reflected in `runtime_worker_leases`
5. final verification is based on persisted DB truth

## Failure Condition

`R2-I5` fails if it:

- silently falls back to in-memory verification
- fakes DB persistence by returning helper state only
- broadens into a task-execution framework

## Suggested Delivery Lane

Because this is concentrated backend/business-logic work with non-trivial truth
constraints, Claude Code `glm-5.1` is a valid preferred lane after manual
provider switch.
