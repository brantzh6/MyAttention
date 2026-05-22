# IKE Runtime v0 Packet - R2-I7 Coding Brief

Date: 2026-04-10
Packet: `R2-I7`
Type: `coding`
Phase: `R2-I7 DB-Backed Inspect Surface`

## Objective

Add one bounded controller-facing inspect route for the existing DB-backed
lifecycle proof.

## Existing Building Blocks

Already available:

- DB-backed lifecycle proof helper:
  - [D:\code\MyAttention\services\api\runtime\db_backed_lifecycle_proof.py](/D:/code/MyAttention/services/api/runtime/db_backed_lifecycle_proof.py)
- existing inspect-style lifecycle route:
  - [D:\code\MyAttention\services\api\routers\ike_v0.py](/D:/code/MyAttention/services/api/routers/ike_v0.py)
- project read surface tests:
  - [D:\code\MyAttention\services\api\tests\test_runtime_v0_project_surface.py](/D:/code/MyAttention/services/api/tests/test_runtime_v0_project_surface.py)

## Required Outcome

Produce the narrowest route-level exposure that lets the controller inspect one
DB-backed lifecycle proof result.

Expected shape:

1. one inspect route
2. one bounded response payload
3. truth-boundary flags that explicitly say:
   - `bounded_db_proof = true`
   - `general_task_runner = false`
   - `detached_execution = false`
4. focused tests only

## Guardrails

Do not:

- add general task CRUD
- add queue or daemon semantics
- add multi-task orchestration
- hide that the proof persists rows

## Validation Expectation

At minimum:

- focused router pytest slice
- compile/import checks
- explicit assertions on truth-boundary flags

## Suggested Lane

Prefer OpenClaw `qwen3.6-plus` or Claude Code `glm-5.1` for delegated
implementation, then return to controller review.
