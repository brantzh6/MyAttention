# IKE Runtime v0 Packet Brief: R0-A Core Runtime Schema Foundation

## Task ID

`IKE-RUNTIME-R0-A`

## Goal

Create the first durable schema foundation for `IKE Runtime v0`.

This task is only about the kernel schema layer.
It is not a behavior or API rollout.

## Scope

Add the first canonical runtime tables needed by the whole first-wave kernel so
later packets do not have to reopen schema scope:

- `runtime_projects`
- `runtime_tasks`
- `runtime_decisions`
- `runtime_task_events`
- `runtime_worker_leases`
- `runtime_work_contexts`
- `runtime_memory_packets`
- `runtime_task_checkpoints`
- `runtime_outbox_events`

## Allowed Files

Expected write scope should stay inside files like:

- migration files for the runtime schema
- runtime ORM model definitions
- narrow tests for schema/model presence and key constraints

## Forbidden Changes

Do not add:

- public API routes
- runtime UI
- notification objects
- graph-memory or retrieval structures
- semantic ranking/reasoning behavior
- broad scheduler redesign

Do not silently introduce:

- extra durable task states beyond the compressed v0 set
- fake acceptance semantics
- JSONB-only canonical state

## Required Context

- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_IMPLEMENTATION_READINESS.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_IMPLEMENTATION_READINESS.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_DATA_MODEL_AND_TRANSACTION_BOUNDARIES.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_DATA_MODEL_AND_TRANSACTION_BOUNDARIES.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_TASK_STATE_AND_STORAGE_ARCHITECTURE.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_TASK_STATE_AND_STORAGE_ARCHITECTURE.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_ROLE_PERMISSIONS_AND_TRANSITION_MATRIX.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_ROLE_PERMISSIONS_AND_TRANSITION_MATRIX.md)

## Validation

Minimum validation expected:

1. migration applies locally
2. ORM/model layer loads
3. rollback viability for the migration
4. narrow tests confirm tables and key fields/index assumptions
5. no extra runtime capability is introduced

Recommended acceptance checks:

- all first-wave runtime tables exist
- key state/acceptance fields use explicit constraints
- append-only/event tables are not left implicitly mutable by omission

## Stop Conditions

Stop and report if:

- another packet is required to define canonical task semantics first
- the schema requires adding extra task states not present in the v0 design
- the design appears to require new first-class objects beyond this brief
- existing legacy schema creates a conflict that forces architectural decisions

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
