# IKE Runtime v0 - R2-I1 Result Milestone

Date: 2026-04-10
Phase: `R2-I First Real Task Lifecycle On Canonical Service`
Packet: `R2-I1`

## Scope

Add the narrowest possible live-service-adjacent lifecycle proof surface on top
of the current canonical runtime service.

This packet intentionally does not add:

- general task CRUD
- scheduler semantics
- broad task-runner APIs
- durable runtime-state persistence for the proof itself

## Implemented

- added one inspect-style lifecycle proof route in:
  - [D:\code\MyAttention\services\api\routers\ike_v0.py](/D:/code/MyAttention/services/api/routers/ike_v0.py)
- added focused route tests in:
  - [D:\code\MyAttention\services\api\tests\test_routers_ike_v0.py](/D:/code/MyAttention/services/api/tests/test_routers_ike_v0.py)

## New Route

- `POST /api/ike/v0/runtime/task-lifecycle/proof/inspect`

The route:

1. runs the existing bounded lifecycle proof helper
2. returns an audit-shaped provisional response
3. returns derived work-context output
4. explicitly marks the boundary as:
   - `inspect_only = true`
   - `persists_runtime_state = false`
   - `implies_general_task_runner = false`

## Validation

Commands run:

```powershell
$env:PYTHONPATH='D:\code\MyAttention\services\api'; python -m pytest services/api/tests/test_routers_ike_v0.py -q
python -m compileall D:\code\MyAttention\services\api\routers\ike_v0.py D:\code\MyAttention\services\api\tests\test_routers_ike_v0.py
```

Observed results:

- `31 passed, 28 warnings, 9 subtests passed`
- compile passed

## Live Proof

The canonical local service on `127.0.0.1:8000` now returns a successful
runtime lifecycle proof through the new inspect route.

Observed live result:

- `POST /api/ike/v0/runtime/task-lifecycle/proof/inspect`
  - `200 OK`
  - `success = true`
  - `final_status = done`
  - `integrity.valid = true`
  - `integrity.auditable = true`

The returned live payload included:

- 4 canonical state transitions
- aligned event sequence
- lease record
- derived work context
- explicit truth-boundary flags

## Important Truth Boundary

This packet proves:

- live route honesty
- bounded lifecycle state-machine behavior
- audit-shaped proof output on the canonical service

This packet does **not yet** prove:

- PG-backed lifecycle persistence
- PG-backed claim verification
- a full Postgres-backed runtime lifecycle fact path

## Controller Judgment

- `R2-I1 = accept_with_changes`

## Why Accept With Changes

This packet successfully proves a live-service-adjacent lifecycle proof path,
but it still remains intentionally narrow.

What still remains for later packets:

1. review whether this route shape is the right long-term narrow surface
2. decide whether any later packet should connect this proof more directly to
   DB-backed runtime read surfaces
3. keep this from drifting into a general runtime task-execution API
