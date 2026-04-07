# IKE Runtime v0 Packet Brief: R0-C Task Event Log and Lease Semantics

## Task ID

`IKE-RUNTIME-R0-C`

## Goal

Implement the first auditable runtime event log and durable worker-lease
semantics for `IKE Runtime v0`.

This packet is about recoverability and auditability.
It is not a general scheduler redesign.

## Scope

Implement only:

- append-only `runtime_task_events`
- durable `runtime_worker_leases`
- lease claim / heartbeat / expiry semantics
- task-type lease-expiry recovery hooks

Supported task-type expiry defaults:

- `implementation -> waiting`
- `review -> review_pending`
- `study -> failed`
- `daemon -> ready`
- `workflow -> waiting`
- `maintenance -> ready`

## Allowed Files

Expected write scope should stay inside files like:

- runtime lease/event persistence layer
- runtime recovery helpers
- narrow model/service code for lease semantics
- tests for event append discipline and lease-expiry recovery

## Forbidden Changes

Do not add:

- full queue worker runtime
- broad outbox executor framework
- notification/follow-up subsystem
- extra runtime task states

Do not silently allow:

- lease expiry to finalize work as `done`
- recovery to invent acceptance or review outcomes
- event mutation or rewrite behavior

## Required Context

- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_DATA_MODEL_AND_TRANSACTION_BOUNDARIES.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_DATA_MODEL_AND_TRANSACTION_BOUNDARIES.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_TASK_STATE_AND_STORAGE_ARCHITECTURE.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_TASK_STATE_AND_STORAGE_ARCHITECTURE.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_ROLE_PERMISSIONS_AND_TRANSITION_MATRIX.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_ROLE_PERMISSIONS_AND_TRANSITION_MATRIX.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_IMPLEMENTATION_READINESS.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_IMPLEMENTATION_READINESS.md)

## Validation

Minimum validation expected:

1. event log is append-only
2. lease claim and expiry are durable
3. task-type expiry policy drives recovery destination
4. recovery emits explicit events
5. recovery cannot silently promote reviewable work to `done`

## Stop Conditions

Stop and report if:

- state semantics from `R0-B` are not stable enough to encode recovery
- lease expiry policy requires introducing new durable states
- implementation requires hidden scheduler state outside canonical tables
- append-only event semantics cannot be preserved with the current design

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
