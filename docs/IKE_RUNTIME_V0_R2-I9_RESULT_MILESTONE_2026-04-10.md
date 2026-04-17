# IKE Runtime v0 - R2-I9 Result Milestone

Date: 2026-04-10
Phase: `R2-I9 Concurrent Proof Boundary`
Status: `completed`

## Scope

Prove the narrowest overlapping-run safety property above `R2-I8`:

- two DB-backed proof runs started concurrently must not collide on durable ids
- their persisted task, lease, and event rows must remain separable

This packet does not claim production-grade concurrency or scheduler semantics.

## Implemented

- extended DB-backed lifecycle proof tests with one overlapping-run isolation proof:
  - [D:\code\MyAttention\services\api\tests\test_runtime_v0_db_backed_lifecycle_proof.py](/D:/code/MyAttention/services/api/tests/test_runtime_v0_db_backed_lifecycle_proof.py)

## What The Test Proves

The new test now proves:

1. two proof runs can start from separate threads with separate:
   - `asyncio.Runner`
   - `AsyncSession`
   - `SyncAsyncSessionAdapter`
2. those overlapping runs still keep distinct:
   - `project_id`
   - `task_id`
   - `lease_id`
   - `event_ids`
3. persisted rows for those ids remain independently queryable after the runs complete
4. the engine pool can be explicitly disposed after the threaded proof to avoid
   stale closed-loop connections in later tests

## Validation

Commands run:

```powershell
python -m pytest tests/test_runtime_v0_db_backed_lifecycle_proof.py tests/test_routers_ike_v0.py tests/test_runtime_v0_project_surface.py -q
python -m compileall runtime routers tests
```

Observed results:

- `47 passed, 28 warnings, 9 subtests passed`
- compile passed

## Mainline Meaning

`R2-I9` does not mean the runtime now has a broad concurrent execution
platform.

It does mean the current bounded DB-backed proof lane now has evidence for:

- single-run success
- repeated sequential isolation
- bounded overlapping-run isolation

## Controller Judgment

- `R2-I9 = accept_with_changes`

## Remaining Gaps

This still does not prove:

1. cancel/abort behavior for overlapping durable proof runs
2. detached execution supervision
3. queue/scheduler semantics
4. production multi-tenant concurrency guarantees
