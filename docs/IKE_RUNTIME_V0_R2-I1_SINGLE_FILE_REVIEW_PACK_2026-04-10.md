# IKE Runtime v0 - R2-I1 Single-File Review Pack

Date: 2026-04-10
Purpose: external review pack
Scope: `R2-I1 live lifecycle proof route`

## What Changed

This packet adds one narrow inspect-style route:

- `POST /api/ike/v0/runtime/task-lifecycle/proof/inspect`

Primary file:

- [D:\code\MyAttention\services\api\routers\ike_v0.py](/D:/code/MyAttention/services/api/routers/ike_v0.py)

Primary supporting test files:

- [D:\code\MyAttention\services\api\tests\test_routers_ike_v0.py](/D:/code/MyAttention/services/api/tests/test_routers_ike_v0.py)
- [D:\code\MyAttention\services\api\tests\test_runtime_v0_task_lifecycle_proof.py](/D:/code/MyAttention/services/api/tests/test_runtime_v0_task_lifecycle_proof.py)

Primary supporting helper:

- [D:\code\MyAttention\services\api\runtime\task_lifecycle.py](/D:/code/MyAttention/services/api/runtime/task_lifecycle.py)

## Intent

The route is meant to prove one live-service-adjacent runtime lifecycle path on
top of the canonical service baseline.

It is explicitly **not** intended to become:

- a general task runner
- a scheduler API
- a broad task CRUD surface
- a durable acceptance action

## Route Semantics

The route:

1. runs the existing bounded lifecycle proof helper
2. returns a provisional audit-shaped envelope
3. exposes:
   - lifecycle summary
   - integrity result
   - transitions
   - events
   - lease
   - derived work context
4. explicitly returns:
   - `inspect_only = true`
   - `persists_runtime_state = false`
   - `implies_general_task_runner = false`

## Why This Is Mainline-Relevant

Earlier runtime work proved lifecycle correctness at helper/test level.

This packet lifts that proof into the current live canonical service surface,
without widening scope into a task platform.

## Review Questions

1. Does this route stay narrow enough to count as proof infrastructure rather
   than feature creep?
2. Does it preserve runtime-owned truth rather than introducing shadow state?
3. Does the response shape honestly communicate that this is inspect/proof
   output only?
4. Is there any hidden drift toward general orchestration or persistence?
5. Is there any structural issue in how lease / event / derived work-context
   data are exposed?

## Validation Run

Commands:

```powershell
$env:PYTHONPATH='D:\code\MyAttention\services\api'; python -m pytest services/api/tests/test_runtime_v0_task_lifecycle_proof.py services/api/tests/test_routers_ike_v0.py -q
python -m compileall D:\code\MyAttention\services\api\runtime\task_lifecycle.py D:\code\MyAttention\services\api\routers\ike_v0.py D:\code\MyAttention\services\api\tests\test_runtime_v0_task_lifecycle_proof.py D:\code\MyAttention\services\api\tests\test_routers_ike_v0.py
```

Observed:

- `54 passed, 28 warnings, 9 subtests passed`
- compile passed

## Live Proof

Observed against canonical local service:

- `POST http://127.0.0.1:8000/api/ike/v0/runtime/task-lifecycle/proof/inspect`
  - `200 OK`
  - `success = true`
  - `final_status = done`
  - `integrity.valid = true`
  - `integrity.auditable = true`

## Recommended Review Output Format

Please return:

1. `summary`
2. `findings`
3. `validation_gaps`
4. `known_risks`
5. `recommendation`
