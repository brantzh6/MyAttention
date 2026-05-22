# IKE Runtime v0 Packet Brief: R0-B Compressed Task State Machine Semantics

## Task ID

`IKE-RUNTIME-R0-B`

## Goal

Implement the compressed `IKE Runtime v0` task state machine and its transition
guardrails.

This packet is about truthful runtime task semantics.
It is not a workflow platform rollout.

## Scope

Support only the approved durable v0 states:

- `inbox`
- `ready`
- `active`
- `waiting`
- `review_pending`
- `done`
- `failed`

Support non-state control actions only as controller/runtime actions and event
records:

- `cancelled`
- `dropped`
- `deprioritized`

## Allowed Files

Expected write scope should stay inside files like:

- runtime task state helpers
- transition validation logic
- runtime task model/service helpers
- narrow tests for legal and illegal transitions

## Forbidden Changes

Do not add:

- extra durable task states
- custom workflow DSL
- broad orchestration engine logic
- UI-driven hidden transitions
- chat-history-derived state truth

Do not silently redefine:

- `waiting` as equivalent to `blocked`
- `review_pending` as equivalent to `done`
- `failed` as equivalent to `cancelled`

## Required Context

- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_TASK_STATE_AND_STORAGE_ARCHITECTURE.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_TASK_STATE_AND_STORAGE_ARCHITECTURE.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_DATA_MODEL_AND_TRANSACTION_BOUNDARIES.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_DATA_MODEL_AND_TRANSACTION_BOUNDARIES.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_ROLE_PERMISSIONS_AND_TRANSITION_MATRIX.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_ROLE_PERMISSIONS_AND_TRANSITION_MATRIX.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_IMPLEMENTATION_READINESS.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_IMPLEMENTATION_READINESS.md)

## Validation

Minimum validation expected:

1. legal transitions succeed
2. illegal transitions fail explicitly
3. delegate cannot move reviewable work directly to `done`
4. `waiting`, `review_pending`, and `failed` remain machine-distinguishable
5. controller/runtime recovery paths do not silently self-accept work

## Stop Conditions

Stop and report if:

- an extra durable state appears necessary for correctness
- role-permission rules conflict with the compressed state model
- recovery semantics require broader lease/event design from another packet
- implementation would require inventing hidden state outside canonical task
  status plus events

## Delivery Format

Return:

1. `summary`
2. `files_changed`
3. `why_this_solution`
4. `validation_run`
5. `known_risks`
6. `recommendation`

If blocked, return:

- blocker
- what was attempted
- what is missing
