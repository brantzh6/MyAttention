# IKE Runtime v0 - R2-I10 Result Milestone

Date: 2026-04-10
Phase: `R2-I10 Abort And Failure Boundary`
Status: `completed`

## Scope

Harden failure-path honesty for the bounded DB-backed proof lane.

The target was not broader supervision. The target was:

- if the proof fails after some commits have already landed
- the returned result should reflect durable partial truth instead of stale
  in-memory state

## Implemented

- hardened failure reporting in:
  - [D:\code\MyAttention\services\api\runtime\db_backed_lifecycle_proof.py](/D:/code/MyAttention/services/api/runtime/db_backed_lifecycle_proof.py)
- added focused failure-path tests in:
  - [D:\code\MyAttention\services\api\tests\test_runtime_v0_db_backed_lifecycle_proof.py](/D:/code/MyAttention/services/api/tests/test_runtime_v0_db_backed_lifecycle_proof.py)

## What Changed

On failure, the helper now:

1. rolls back the current transaction
2. re-reads the durable task row when possible
3. re-counts durable task events when possible
4. returns:
   - durable `final_status`
   - durable `persisted_event_count`

instead of trusting expired ORM state after rollback.

## What The New Tests Prove

The new focused failure test now proves:

1. a synthetic failure at `ready -> active` returns `success = false`
2. the returned `final_status` is `ready`, matching durable truth
3. the returned `persisted_event_count` is `2`
4. the database still truthfully contains the partial committed state:
   - one `ready` task row
   - one `state_transition` event
   - one `lease_claimed` event

## Validation

Commands run:

```powershell
python -m pytest tests/test_runtime_v0_db_backed_lifecycle_proof.py tests/test_routers_ike_v0.py tests/test_runtime_v0_project_surface.py -q
python -m compileall runtime routers tests
```

Observed results:

- `48 passed, 28 warnings, 9 subtests passed`
- compile passed

## Mainline Meaning

The bounded durable proof lane now has evidence for:

- success-path truth
- repeated-run isolation
- overlapping-run isolation
- failure-path honesty

That is still not a task platform.

It is a stronger truth boundary for one narrow proof lane.

## Controller Judgment

- `R2-I10 = accept`

## Remaining Gaps

This still does not prove:

1. external abort semantics against a live detached worker
2. general retry logic
3. scheduler semantics
4. production supervision guarantees
