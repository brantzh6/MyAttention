# IKE Runtime v0 Subproject Decision

## Decision

Create a dedicated subproject track named:

- `IKE Runtime v0`

Recommended descriptive scope:

- `IKE Runtime v0: Memory, Task, and Decision Control`

This is **not** a parallel architecture outside IKE.
It is the first independently deliverable runtime kernel of IKE.

## Why This Exists

Two different but related problems are now blocking sustainable progress:

1. OpenClaw lacks stable memory and task governance in real multi-project use.
2. Our own controller + delegate development process now involves enough delegation,
   packets, reviews, closures, and follow-up work that task/state management is
   becoming a delivery risk.

The problem is no longer only product-side memory.
It is **work-state governance** across both:

- runtime interaction
- engineering execution

## Core Judgment

Memory alone is not enough.

If the system remembers facts but cannot reliably answer:

- what project is active
- what task is active
- what decision was already made
- what is blocked
- what the next action is

then both product behavior and development behavior will drift.

Therefore `IKE Runtime v0` must include:

- memory governance
- task governance
- decision logging
- work-context restoration

## Scope

### In Scope

- `Project` as a first-class state object
- `Task` as a first-class state object
- `Decision` as a first-class state object
- `MemoryPacket` as a compact recoverable state carrier
- `WorkContext` / active working set restoration
- minimal task state machine
- explicit next action tracking
- closure-to-memory hooks
- support for both:
  - product runtime use
  - controller/delegate engineering workflow use

### Out of Scope

- full IKE information brain implementation
- full knowledge graph implementation
- complete evolution brain reasoning stack
- autonomous multi-agent planner
- large workflow platform rewrite
- broad UI redesign

## Required Principle

`IKE Runtime v0` must serve two fronts at once:

1. **Runtime front**
   - OpenClaw or other gateways should stop forgetting obvious project/task state.

2. **Engineering front**
   - delegated development should stop relying on chat history as the primary task
     system.

If it solves only runtime and not engineering execution, it is incomplete.
If it solves only engineering execution and not runtime memory/task continuity,
it is also incomplete.

## Minimum Object Set

The minimum object set should remain aligned with the current direction from
the OpenClaw decision note:

- `Project`
- `Task`
- `Decision`
- `MemoryPacket`
- `WorkContext`

These should be future-compatible with IKE shared objects rather than become a
second incompatible ontology.

## Relationship To Existing IKE Work

`IKE Runtime v0` should be treated as:

- a runtime kernel beneath benchmark/research/evolution work
- a stabilizer for controller/delegate execution
- a bridge between Claude Code-inspired memory methods and IKE's longer-term
  governance model

It should not replace:

- benchmark research methodology
- entity discovery methodology
- thinking-model armory

Instead, it should make those capabilities operationally sustainable.

## Success Criteria

Short-term success is **stability**, not intelligence theater.

`IKE Runtime v0` is successful when:

- project switching no longer causes obvious context bleed
- active task and next action can be restored without replaying chat
- decisions are explicitly recoverable
- closure can produce truthful memory packets
- delegated engineering work can be tracked outside conversation text
- main controller can see project/task/decision state without reconstructing it
  manually from history

## Priority Order

1. project/task state kernel
2. decision log and next-action discipline
3. memory packet and work-context restoration
4. closure-to-memory integration
5. later integration with benchmark/evolution flows

## Current Recommendation

Proceed with `IKE Runtime v0` as an explicit subproject track inside IKE.

Do not frame it as:

- a separate rival project
- a complete IKE rollout
- a purely OpenClaw-specific patch set

Frame it as:

- the minimal control kernel IKE now requires
- the same kernel needed by both runtime interaction and delegated engineering

Follow-up design:

- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_TASK_STATE_AND_STORAGE_ARCHITECTURE.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_TASK_STATE_AND_STORAGE_ARCHITECTURE.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_DOCUMENT_AND_MEMORY_GOVERNANCE.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_DOCUMENT_AND_MEMORY_GOVERNANCE.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_DATA_MODEL_AND_TRANSACTION_BOUNDARIES.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_DATA_MODEL_AND_TRANSACTION_BOUNDARIES.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_ROLE_PERMISSIONS_AND_TRANSITION_MATRIX.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_ROLE_PERMISSIONS_AND_TRANSITION_MATRIX.md)
