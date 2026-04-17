# IKE Runtime v0 Packet - R2-I13 Coding Brief

Date: 2026-04-10
Packet: `R2-I13`
Type: `coding`
Phase: `R2-I13 Live Route Freshness Closure`

## Objective

Close one narrow mainline gap:

- the code tree and focused tests say the DB-backed inspect route exists
- the canonical live service on `127.0.0.1:8000` currently returns `404`

The task is to make controller-visible truth honest in the narrowest possible
way.

## Existing Evidence

- route implementation:
  - [D:\code\MyAttention\services\api\routers\ike_v0.py](/D:/code/MyAttention/services/api/routers/ike_v0.py)
- DB-backed proof helper:
  - [D:\code\MyAttention\services\api\runtime\db_backed_lifecycle_proof.py](/D:/code/MyAttention/services/api/runtime/db_backed_lifecycle_proof.py)
- focused route/test evidence:
  - [D:\code\MyAttention\services\api\tests\test_routers_ike_v0.py](/D:/code/MyAttention/services/api/tests/test_routers_ike_v0.py)
  - [D:\code\MyAttention\services\api\tests\test_runtime_v0_db_backed_lifecycle_proof.py](/D:/code/MyAttention/services/api/tests/test_runtime_v0_db_backed_lifecycle_proof.py)

## Required Outcome

Produce the narrowest acceptable closure for this mismatch.

Acceptable end states:

1. canonical `8000` serves
   `POST /api/ike/v0/runtime/task-lifecycle/db-proof/inspect` successfully
   after a controlled refresh, with durable proof recorded
2. or the runtime controller-facing inspect surface explicitly reports that the
   live service does not expose the expected route shape

## Guardrails

Do not:

- add a broad deployment framework
- add general service-management APIs
- widen into scheduler or supervisor semantics
- silently treat file-tree fingerprint as proof of live route freshness

## Validation Expectation

At minimum:

- one live canonical-service check against `127.0.0.1:8000`
- focused pytest slice for any new helper/route checks
- compile/import checks
- one durable result note recording what was actually proven

## Suggested Lane

Prefer Claude Code `glm-5.1` or OpenClaw `qwen3.6-plus` for delegated
implementation, then return to controller review.
