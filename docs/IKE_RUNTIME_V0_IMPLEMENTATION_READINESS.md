# IKE Runtime v0 Implementation Readiness

## Purpose

This document is the last design-layer checkpoint before implementation begins.

It does not add new capability scope.
It answers:

1. what the first implementation slice should include
2. what must be true before implementation starts
3. what is intentionally deferred
4. what must be verified before the slice is accepted

## Current Verdict

`IKE Runtime v0` is close to implementation-ready, but only for a narrow first
slice.

The first build slice should implement the kernel, not the future platform.

## First Build Slice

The first implementation slice should include only:

1. durable project/task/decision tables
2. compressed v0 task state machine
3. append-only task events
4. durable worker leases
5. narrow `WorkContext` snapshot carrier
6. `MemoryPacket` metadata with explicit acceptance lifecycle
7. basic recovery from restart and lease expiry

The first slice should not include:

- graph memory
- semantic retrieval
- notification mesh
- general workflow marketplace
- broad public object APIs
- broad UI task board

## Preconditions Before Coding

Implementation should not start until these are true:

1. v0 state list is accepted:
   - `inbox`
   - `ready`
   - `active`
   - `waiting`
   - `review_pending`
   - `done`
   - `failed`

2. control actions are separated from task states:
   - `cancelled`
   - `dropped`
   - `deprioritized`

3. `MemoryPacket` lifecycle is accepted:
   - `draft`
   - `pending_review`
   - `accepted`

4. lease-expiry recovery defaults are accepted

5. JSONB discipline is accepted

6. controller/delegate/reviewer/runtime boundaries are accepted

## Implementation Order

### Slice A: Core Tables and State Semantics

Build:

- `runtime_projects`
- `runtime_tasks`
- `runtime_decisions`
- `runtime_task_events`
- `runtime_worker_leases`

Must prove:

- task creation
- legal state transitions
- append-only eventing
- no hidden state in docs or chat

### Slice B: WorkContext and Checkpoints

Build:

- `runtime_work_contexts`
- `runtime_task_checkpoints`

Must prove:

- current working set can be reconstructed
- `WorkContext` is not acting as a second truth source

### Slice C: MemoryPacket Metadata and Acceptance

Build:

- `runtime_memory_packets`
- accepted-upstream linkage

Must prove:

- packet existence does not imply trust
- trusted packets can be distinguished from drafts

### Slice D: Recovery and Queue Acceleration

Build:

- Redis queue support
- lease expiry handling
- recovery rebuild path from Postgres truth

Must prove:

- Redis loss does not destroy truth
- stale active leases do not silently finalize work

## Acceptance Checks

The first implementation slice is only acceptable if:

1. task states cannot be skipped illegally
2. delegates cannot self-accept reviewable work
3. runtime recovery cannot silently promote work to `done`
4. `waiting` vs `review_pending` remains machine-distinguishable
5. trusted `MemoryPacket` records are auditably tied to reviewed upstream work
6. Postgres can rebuild queue/caching state after Redis loss
7. `WorkContext` can be reconstructed without becoming a second truth source

## Known Deferred Work

These are intentionally deferred beyond the first slice:

- notification/follow-up objects
- richer relation graph
- temporal replay and event retrieval UX
- object access layer
- richer memory topology
- benchmark-driven procedural-memory promotion

## Main Risk if Started Too Early

The main failure mode is not under-design.
It is implementing too broad a runtime before the kernel semantics are proven.

The first slice should therefore be judged by:

- reversibility
- truthfulness
- recoverability
- auditability

not by feature count.
