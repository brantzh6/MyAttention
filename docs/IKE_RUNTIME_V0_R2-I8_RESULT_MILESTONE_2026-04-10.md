# IKE Runtime v0 - R2-I8 Result Milestone

Date: 2026-04-10
Phase: `R2-I8 Repeated Proof Hardening`
Status: `completed`

## Scope

Prove the narrowest repeated-run safety property above the existing DB-backed
proof lane:

- two sequential proof runs must stay isolated
- ids must not collide
- persisted rows for those two runs must remain separable

This packet does not claim broad concurrency, queueing, or detached execution.

## Implemented

- extended DB-backed lifecycle proof tests with one repeated-run isolation proof:
  - [D:\code\MyAttention\services\api\tests\test_runtime_v0_db_backed_lifecycle_proof.py](/D:/code/MyAttention/services/api/tests/test_runtime_v0_db_backed_lifecycle_proof.py)

## What The Test Proves

The new test now proves:

1. two sequential `execute_db_backed_lifecycle_proof()` runs use different:
   - `project_id`
   - `task_id`
   - `lease_id`
   - `event_ids`
2. the two runs do not reuse event ids
3. persisted rows for those run-specific ids can be queried independently
4. the combined event count for those two runs matches the sum of their
   reported persisted event counts

## Validation

Commands run:

```powershell
python -m pytest tests/test_runtime_v0_db_backed_lifecycle_proof.py tests/test_routers_ike_v0.py -q
python -m compileall runtime routers tests
```

Observed results:

- `36 passed, 28 warnings, 9 subtests passed`
- compile passed

## Mainline Meaning

`R2-I8` does not prove true concurrent execution.

It does prove that the bounded durable proof lane is no longer only a
single-shot success case; sequential repeated execution now has an explicit
isolation guarantee in the test surface.

## Controller Judgment

- `R2-I8 = accept_with_changes`

## Remaining Gaps

This still does not prove:

1. simultaneous concurrent proof runs
2. detached execution durability
3. cancellation/abort semantics for durable proof runs
4. broad task orchestration behavior
