# IKE Runtime v0 R1-C5/R1-C6 Diagnosis

## Purpose

This note records the controller-side diagnosis for the two remaining `R1-C`
follow-ups:

1. `R1-C5` Postgres-backed claim verification
2. `R1-C6` DB-backed runtime test restoration

The purpose is to prevent the next execution packet from broadening scope or
inventing missing truth.

## Current Judgment

- `R1-C6` DB-backed schema-foundation suite is now restored and green
- `R1-C5` is execution-ready after the assignment-truth decision

Reason:

- `R1-C6` had a concrete, localizable fixture gap and is now reduced to a
  bounded test-side correction with green evidence
- `R1-C5` now has a fixed truth-source decision

## R1-C6: DB-Backed Testing Gap Is Restored

Current observable facts:

- [test_runtime_v0_schema_foundation.py](/D:/code/MyAttention/services/api/tests/test_runtime_v0_schema_foundation.py)
  expects a `db_session` fixture
- there is no repository-level `conftest.py` providing that fixture
- [session.py](/D:/code/MyAttention/services/api/db/session.py) only exposes async runtime
  dependencies
- a narrow repo-level pytest harness has now been added at:
  - [conftest.py](/D:/code/MyAttention/services/api/tests/conftest.py)
- local Postgres connectivity was restored:
  - `MyAttentionPostgres` is running again
  - port `5432` is reachable
- runtime kernel migration was applied to the current local DB:
  - `migrations/013_runtime_v0_kernel_foundation.sql`
- the schema-foundation suite now passes:
  - `53 passed, 1 warning`
- one narrow test-side mismatch had to be corrected:
  - `done` state fixtures must provide `result_summary`

Controller interpretation:

- fixture restoration was a bounded testing-lane repair and is complete
- `R1-C6` is no longer blocked by pytest plumbing or local DB reachability
- DB-backed schema truth now exists for the migration-foundation suite
- the remaining runtime follow-up is `R1-C5`, not additional `R1-C6` recovery

## R1-C5: Truth Source Is Still Underspecified

Current observable facts:

- [leases.py](/D:/code/MyAttention/services/api/runtime/leases.py) contains only an
  adapter boundary for `ClaimVerifier`
- the current runtime schema contains durable truth for:
  - `runtime_tasks.owner_kind`
  - `runtime_tasks.owner_id`
  - `runtime_tasks.current_lease_id`
  - `runtime_worker_leases`
  - `runtime_task_events`
- the current runtime schema does **not** expose an obvious first-class
  assignment table
- existing docs and comments still describe explicit assignment verification as
  if an assignment record already exists

Controller interpretation:

- `ACTIVE_LEASE` verification has a clear candidate truth source:
  `runtime_worker_leases`
- `EXPLICIT_ASSIGNMENT` verification does **not** yet have a clearly fixed
  runtime-owned truth source

Decision outcome:

- explicit assignment truth is fixed to:
  - `runtime_tasks.owner_kind/owner_id`
- event history remains audit evidence, not the primary truth source

## Execution Order Update

Recommended order:

1. keep the restored DB-backed schema-foundation suite as durable evidence
2. execute `R1-C5` using task ownership fields as explicit assignment truth

## Non-Negotiable Guardrail

Do not let a delegate "solve" `R1-C5` by:

- fabricating assignment truth in controller-side code
- silently treating task ownership fields as assignment truth without controller
  approval
- adding a broad new assignment subsystem without an explicit phase decision
