# IKE Runtime v0 Packet Brief: R0-E MemoryPacket Metadata and Acceptance

## Task ID

`IKE-RUNTIME-R0-E`

## Goal

Implement truthful `MemoryPacket` metadata and acceptance handling for
`IKE Runtime v0`.

This packet is about trusted memory candidates.
It is not a full memory engine.

## Scope

Implement only:

- `runtime_memory_packets`
- `draft -> pending_review -> accepted`
- accepted-upstream linkage
- packet metadata and storage references

## Required Constraint

Packet existence must not imply trust.

Accepted packets must be auditably tied to reviewed upstream work such as:

- accepted task closure
- accepted decision handoff
- explicit controller-approved upstream artifact path

## Allowed Files

Expected write scope should stay inside files like:

- runtime memory-packet persistence/model layer
- acceptance helpers
- narrow tests for packet trust semantics

## Forbidden Changes

Do not add:

- semantic retrieval engine
- graph-memory structures
- automatic memory promotion without accepted upstream evidence
- hidden controller assumptions stored only in packet text

Do not silently allow:

- `accepted` packets without upstream review linkage
- packets to act as mutable living documents
- packet summaries to replace canonical task/decision truth

## Required Context

- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_DOCUMENT_AND_MEMORY_GOVERNANCE.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_DOCUMENT_AND_MEMORY_GOVERNANCE.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_DATA_MODEL_AND_TRANSACTION_BOUNDARIES.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_DATA_MODEL_AND_TRANSACTION_BOUNDARIES.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_IMPLEMENTATION_READINESS.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_IMPLEMENTATION_READINESS.md)
- [D:\code\MyAttention\docs\IKE_MAGMA_CHRONOS_MEMORY_RESEARCH_NOTE.md](/D:/code/MyAttention/docs/IKE_MAGMA_CHRONOS_MEMORY_RESEARCH_NOTE.md)

## Validation

Minimum validation expected:

1. packets move only through `draft -> pending_review -> accepted`
2. accepted packets require explicit upstream linkage
3. packet presence alone does not mark trust
4. packet metadata and storage refs remain auditable

Recommended controller-facing proof:

- trust-boundary test:
  - delegate-created packet cannot self-promote to `accepted`
  - non-accepted packet is excluded from trusted recall paths
  - explicit reviewed upstream linkage is required before trust promotion

## Stop Conditions

Stop and report if:

- upstream acceptance semantics are not stable enough yet
- packet trust requires introducing a broader memory system
- packet lifecycle conflicts with task/decision review boundaries

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
