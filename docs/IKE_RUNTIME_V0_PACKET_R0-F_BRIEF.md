# IKE Runtime v0 Packet Brief: R0-F Redis Acceleration and Recovery Rebuild

## Task ID

`IKE-RUNTIME-R0-F`

## Goal

Add Redis-based acceleration to `IKE Runtime v0` without moving truth out of
Postgres.

This packet is about speed and rebuildability.
It is not a truth-model redesign.

## Scope

Implement only:

- ready/active queue acceleration
- hot pointers where already justified
- dedupe windows where already justified
- rebuild path from canonical Postgres truth after Redis loss

## Required Constraint

Redis must remain acceleration only.

Loss of Redis must not destroy:

- current task truth
- decision truth
- accepted memory truth
- recovery eligibility

## Allowed Files

Expected write scope should stay inside files like:

- queue/cache adapter layer
- rebuild helpers
- narrow recovery tests

## Forbidden Changes

Do not add:

- Redis as primary truth
- scheduler-owned hidden canonical state
- broad distributed task runner framework
- semantic memory or retrieval features

Do not silently allow:

- queue-only tasks that cannot be reconstructed from Postgres
- Redis loss to drop active/reviewable work on the floor

## Required Context

- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_TASK_STATE_AND_STORAGE_ARCHITECTURE.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_TASK_STATE_AND_STORAGE_ARCHITECTURE.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_DATA_MODEL_AND_TRANSACTION_BOUNDARIES.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_DATA_MODEL_AND_TRANSACTION_BOUNDARIES.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_IMPLEMENTATION_READINESS.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_IMPLEMENTATION_READINESS.md)

## Validation

Minimum validation expected:

1. queue/caching state can be rebuilt from canonical Postgres truth
2. Redis loss does not destroy runtime truth
3. active/reviewable tasks remain recoverable after cache rebuild
4. acceleration layer does not invent hidden state transitions

## Stop Conditions

Stop and report if:

- the current kernel tables are not stable enough to rebuild from truth
- acceleration requires introducing hidden scheduler state
- Redis is being used to store canonical state not present in Postgres

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
