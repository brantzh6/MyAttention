# IKE Runtime v0 - R2-I5 Result Milestone

Date: 2026-04-10
Phase: `R2-I5 PG-Backed Lifecycle Proof`
Status: `completed`

## Scope

Prove one narrow lifecycle path through durable runtime truth:

- `runtime_tasks`
- `runtime_task_events`
- `runtime_worker_leases`
- `PostgresClaimVerifier`

This packet intentionally does not add a new route or a general task runner.

## Implemented

- added one DB-backed lifecycle proof helper:
  - [D:\code\MyAttention\services\api\runtime\db_backed_lifecycle_proof.py](/D:/code/MyAttention/services/api/runtime/db_backed_lifecycle_proof.py)
- added focused DB-backed tests:
  - [D:\code\MyAttention\services\api\tests\test_runtime_v0_db_backed_lifecycle_proof.py](/D:/code/MyAttention/services/api/tests/test_runtime_v0_db_backed_lifecycle_proof.py)

## What The Helper Proves

The helper now durably proves:

1. one runtime project row is created
2. one runtime task row moves from `inbox -> ready -> active -> review_pending -> done`
3. one durable worker lease row is created and later released
4. `PostgresClaimVerifier` validates the delegate claim against durable truth
5. task transition events are durably appended to `runtime_task_events`

## Validation

Commands run:

```powershell
$env:PYTHONPATH='D:\code\MyAttention\services\api'; python -m pytest services/api/tests/test_runtime_v0_db_backed_lifecycle_proof.py services/api/tests/test_runtime_v0_postgres_claim_verifier.py -q
python -m compileall D:\code\MyAttention\services\api\runtime\db_backed_lifecycle_proof.py D:\code\MyAttention\services\api\tests\test_runtime_v0_db_backed_lifecycle_proof.py
```

Observed results:

- `6 passed, 1 warning`
- compile passed

## Mainline Meaning

This closes the key semantic gap raised by review #11:

- `R2-I1` proved a live state-machine lifecycle path
- `R2-I5` now proves one PG-backed lifecycle fact path

Together they now show:

- honest live proof surface
- and one durable runtime truth path behind it

## Controller Judgment

- `R2-I5 = accept_with_changes`

## Why Accept With Changes

This packet proves one narrow durable lifecycle path, but it is still only one
proof shape.

It does not yet prove:

1. broad lifecycle orchestration
2. route-level exposure of the DB-backed proof
3. repeated concurrency behavior
