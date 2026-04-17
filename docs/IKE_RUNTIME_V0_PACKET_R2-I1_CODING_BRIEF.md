# IKE Runtime v0 Packet - R2-I1 Coding Brief

Date: 2026-04-10
Packet: `R2-I1`
Type: `coding`
Phase: `R2-I First Real Task Lifecycle On Canonical Service`

## Objective

Implement the narrowest possible live-service-adjacent runtime lifecycle proof
surface on top of the current canonical service baseline.

## Current Baseline

Already true:

- runtime helper-level lifecycle proof exists:
  - [D:\code\MyAttention\services\api\runtime\task_lifecycle.py](/D:/code/MyAttention/services/api/runtime/task_lifecycle.py)
- runtime project surface exists:
  - [D:\code\MyAttention\services\api\runtime\project_surface.py](/D:/code/MyAttention/services/api/runtime/project_surface.py)
- runtime preflight canonical service proof is now narrowed and live-reviewed:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-H8_CONTROLLER_DECISION_BRIEF_2026-04-10.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-H8_CONTROLLER_DECISION_BRIEF_2026-04-10.md)

Not yet true:

- one live canonical-service-adjacent lifecycle proof surface

## Required Outcome

Produce one narrow implementation that lets the runtime service expose or run
one auditable lifecycle proof without becoming a broad task runner.

Acceptable implementation shapes include:

1. one inspect-style endpoint that runs the bounded proof and returns an audit
   envelope
2. one narrow service helper plus one inspect route
3. one DB-backed proof adapter if that is required to connect the existing
   helper-level proof to the live service baseline

## Guardrails

Do not:

- add a general task create/update API family
- add scheduler semantics
- add background worker supervision
- invent frontend-only state to represent lifecycle truth
- widen into general runtime orchestration

## Strong Preference

Prefer:

- reuse of existing proof logic
- audit-shaped output
- provisional / inspect semantics
- minimal file footprint

## Suggested Model

Because this packet may involve non-trivial backend and business-logic shaping,
Claude Code with `glm-5.1` is an acceptable preferred lane after manual
provider switch.

If that is not practical, use latest `qwen3.6`.

## Validation Expectation

At minimum:

- targeted pytest coverage for the new narrow proof surface
- compile / import checks for touched backend files
- one explicit statement of what remains out of scope

## Required Delivery Format

Return:

1. `summary`
2. `files_changed`
3. `why_this_solution`
4. `validation_run`
5. `known_risks`
6. `recommendation`
