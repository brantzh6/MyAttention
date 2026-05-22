# IKE Runtime v0 Packet Brief: R0-D WorkContext Snapshot Carrier

## Task ID

`IKE-RUNTIME-R0-D`

## Goal

Implement the narrowest truthful `WorkContext` snapshot carrier for
`IKE Runtime v0`.

This packet is about restoring the current working set.
It is not a second truth system.

## Scope

Implement only:

- `runtime_work_contexts`
- narrow reconstruction helpers from canonical runtime state
- one-active-context-per-project discipline

## Required Constraint

`WorkContext` must remain reconstructable from:

- canonical task state
- canonical decision state
- accepted packet references

It must not become a parallel mutable truth source.

## Allowed Files

Expected write scope should stay inside files like:

- runtime work-context persistence/model layer
- reconstruction helpers
- narrow tests for reconstruction and one-active-context rules

## Forbidden Changes

Do not add:

- broad dashboard/task board UI
- chat-derived hidden context truth
- free-form context blobs that replace canonical runtime state
- notification/follow-up subsystem

Do not silently allow:

- `WorkContext` fields to drift from task/decision truth
- multiple active work contexts per project without explicit design approval

## Required Context

- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_DOCUMENT_AND_MEMORY_GOVERNANCE.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_DOCUMENT_AND_MEMORY_GOVERNANCE.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_DATA_MODEL_AND_TRANSACTION_BOUNDARIES.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_DATA_MODEL_AND_TRANSACTION_BOUNDARIES.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_IMPLEMENTATION_READINESS.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_IMPLEMENTATION_READINESS.md)

## Validation

Minimum validation expected:

1. one active work context per project is enforced
2. work context can be rebuilt from canonical state
3. work context does not invent hidden task/decision state
4. stale context snapshots can be replaced without rewriting upstream truth

Recommended controller-facing proof:

- reconstruction test:
  - create work context
  - invalidate or remove the snapshot
  - rebuild it from canonical task/decision state plus accepted packet refs
  - confirm no material truth is lost

## Stop Conditions

Stop and report if:

- `WorkContext` requires fields that are not derivable from canonical state
- the implementation would force a second mutable truth source
- acceptance semantics from `MemoryPacket` are required first for correctness

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
