# IKE Runtime v0 Packet - R2-I5 Coding Brief

Date: 2026-04-10
Packet: `R2-I5`
Type: `coding`
Phase: `R2-I5 PG-Backed Lifecycle Proof`

## Objective

Implement one narrow PG-backed runtime lifecycle proof.

## Existing Building Blocks

Already available:

- runtime schema in:
  - [D:\code\MyAttention\services\api\db\models.py](/D:/code/MyAttention/services/api/db/models.py)
- lifecycle state-machine helpers in:
  - [D:\code\MyAttention\services\api\runtime\task_lifecycle.py](/D:/code/MyAttention/services/api/runtime/task_lifecycle.py)
- DB-backed claim verification in:
  - [D:\code\MyAttention\services\api\runtime\postgres_claim_verifier.py](/D:/code/MyAttention/services/api/runtime/postgres_claim_verifier.py)
- DB-backed test fixture in:
  - [D:\code\MyAttention\services\api\tests\conftest.py](/D:/code/MyAttention/services/api/tests/conftest.py)

## Required Outcome

Produce the narrowest implementation that proves one lifecycle through durable
runtime truth:

- `runtime_tasks`
- `runtime_task_events`
- `runtime_worker_leases`

Acceptable shapes:

1. one DB-backed helper with focused tests
2. one DB-backed helper plus one inspect route if a route is needed for proof
   exposure

## Guardrails

Do not:

- add general task CRUD
- add broad service execution semantics
- add scheduler/queue concepts
- bypass `PostgresClaimVerifier` with in-memory fallback in the real proof path

## Validation Expectation

At minimum:

- focused DB-backed pytest slice
- compile/import checks
- explicit proof of persisted task row, event rows, and lease row

## Suggested Lane

Prefer Claude Code `glm-5.1` if delegated, because this is backend truth-path
logic rather than simple route glue.
