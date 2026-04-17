# IKE Runtime v0 - R2-I10/I11 Failure Review Pack

Date: 2026-04-10
Status: `review-ready`
Scope: `R2-I10 + R2-I11 only`

## Review Prompt

Review this packet as a narrow runtime failure-honesty review.

Focus on:

1. whether helper-level failure reporting now reflects durable partial truth
   instead of stale in-memory ORM state
2. whether controller-visible route inspection preserves that same failure
   honesty without implying broader execution capability
3. whether the new overlapping-run test setup is technically defensible and
   avoids fake concurrency claims
4. whether any new wording, flags, or tests overstate runtime capability

Please prioritize:

- semantic honesty
- durable truth alignment
- hidden failure-mode risk
- test realism

Please return:

1. findings first, ordered by severity
2. validation gaps
3. recommendation:
   - `accept`
   - `accept_with_changes`
   - `reject`

## Main Changes Under Review

### 1. Helper-Level Failure Honesty

File:

- [D:\code\MyAttention\services\api\runtime\db_backed_lifecycle_proof.py](/D:/code/MyAttention/services/api/runtime/db_backed_lifecycle_proof.py)

Key additions:

- failure-path durable snapshot helper:
  - `_load_persisted_failure_snapshot(...)`
- failure fallback no longer trusts rollback-expired ORM state:
  - uses `task.__dict__.get("status", RuntimeTaskStatus.INBOX)`
- failure result now returns:
  - durable `final_status`
  - durable `persisted_event_count`

Relevant lines:

- [db_backed_lifecycle_proof.py:110](/D:/code/MyAttention/services/api/runtime/db_backed_lifecycle_proof.py#L110)
- [db_backed_lifecycle_proof.py:372](/D:/code/MyAttention/services/api/runtime/db_backed_lifecycle_proof.py#L372)

### 2. DB-Backed Proof Test Hardening

File:

- [D:\code\MyAttention\services\api\tests\test_runtime_v0_db_backed_lifecycle_proof.py](/D:/code/MyAttention/services/api/tests/test_runtime_v0_db_backed_lifecycle_proof.py)

New proof slices:

- overlapping-run isolation proof:
  - [test_runtime_v0_db_backed_lifecycle_proof.py:132](/D:/code/MyAttention/services/api/tests/test_runtime_v0_db_backed_lifecycle_proof.py#L132)
- synthetic failure honesty proof:
  - [test_runtime_v0_db_backed_lifecycle_proof.py:225](/D:/code/MyAttention/services/api/tests/test_runtime_v0_db_backed_lifecycle_proof.py#L225)

Important implementation note:

- the overlapping-run proof uses separate thread-local:
  - `asyncio.Runner`
  - `create_async_engine(..., poolclass=NullPool)`
  - `AsyncSession`

This was chosen to avoid fake concurrency claims and to avoid cross-loop pool
contamination on Windows/asyncpg.

### 3. Route-Level Failure Honesty

File:

- [D:\code\MyAttention\services\api\tests\test_routers_ike_v0.py](/D:/code/MyAttention/services/api/tests/test_routers_ike_v0.py)

New route proof:

- [test_routers_ike_v0.py:1207](/D:/code/MyAttention/services/api/tests/test_routers_ike_v0.py#L1207)

Route under review:

- [D:\code\MyAttention\services\api\routers\ike_v0.py](/D:/code/MyAttention/services/api/routers/ike_v0.py)
- inspect endpoint:
  - [ike_v0.py:732](/D:/code/MyAttention/services/api/routers/ike_v0.py#L732)

What the new route test checks:

- `summary.success = false`
- durable `summary.final_status = "ready"`
- durable `summary.persisted_event_count = 2`
- explicit `summary.error`
- stable truth-boundary flags on failure

## Validation Run

Commands run:

```powershell
python -m pytest tests/test_runtime_v0_db_backed_lifecycle_proof.py tests/test_routers_ike_v0.py tests/test_runtime_v0_project_surface.py -q
python -m compileall runtime routers tests
```

Observed result:

- `49 passed, 28 warnings, 9 subtests passed`
- compile passed

## Current Claim Boundary

This packet claims only:

1. bounded DB-backed proof success-path truth
2. repeated sequential isolation
3. bounded overlapping-run isolation
4. helper-level failure honesty
5. route-level failure honesty

This packet does **not** claim:

1. general task runner capability
2. detached supervision
3. scheduler semantics
4. production-grade concurrency guarantees

## Current Recommendation

- `accept_with_changes`

Reason:

- the current failure-honesty lane is materially stronger and more reviewable
- but the overall runtime still remains a bounded proof lane, not a task
  platform
