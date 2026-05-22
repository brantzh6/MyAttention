# IKE Runtime v0 Review Milestone 2026-04-04

## 0. Review Prompt

Please review the current `IKE Runtime v0` design milestone.

Primary review document:

- this document: `docs/IKE_RUNTIME_V0_REVIEW_MILESTONE_2026-04-04.md`

Supporting files:

- `docs/IKE_RUNTIME_V0_SUBPROJECT_DECISION.md`
- `docs/IKE_RUNTIME_V0_TASK_STATE_AND_STORAGE_ARCHITECTURE.md`
- `docs/IKE_RUNTIME_V0_DOCUMENT_AND_MEMORY_GOVERNANCE.md`
- `docs/IKE_RUNTIME_V0_DATA_MODEL_AND_TRANSACTION_BOUNDARIES.md`
- `docs/IKE_RUNTIME_V0_ROLE_PERMISSIONS_AND_TRANSITION_MATRIX.md`
- `docs/IKE_MAGMA_CHRONOS_MEMORY_RESEARCH_NOTE.md`

Context:

- `IKE Runtime v0` is not a full IKE rollout.
- It is the first runtime kernel for:
  - memory continuity
  - task governance
  - decision logging
  - work-context restoration
- It must serve both:
  - OpenClaw runtime continuity
  - controller/delegate engineering continuity

Please review the design with emphasis on:

1. state-machine correctness
2. role-permission correctness
3. task/decision/memory governance realism
4. Postgres/Redis/object-storage responsibility split
5. transaction boundary safety
6. backup/recovery realism
7. whether any critical first-class object is still missing
8. whether any current design choice would be expensive to reverse later

Please be critical about:

- fake durability
- hidden state in documents or chat history
- delegate self-acceptance
- runtime ambiguity between waiting/blocked/review_pending/done
- premature graph-memory complexity

Desired output:

1. overall verdict
2. top 5 risks
3. incorrect or weak state transitions
4. incorrect or weak permission boundaries
5. storage/queue/recovery concerns
6. recommended next design milestone before implementation

## Purpose

This is the shortest review brief for the current `IKE Runtime v0` design
milestone.

It is meant for:

- cross-model review
- architecture challenge
- implementation readiness check

It is intentionally shorter than the full runtime design tree.

## What Changed

`IKE Runtime v0` is now explicitly defined as the first independently
deliverable runtime kernel of IKE.

It is not:

- a separate rival project
- a full IKE rollout
- a memory-only patch

It is:

- the minimal control kernel needed by both
  - OpenClaw runtime continuity
  - controller/delegate engineering continuity
- a v0 design that has already absorbed one external review round before
  implementation

## Why This Exists

Two blocking problems now converge:

1. OpenClaw lacks stable memory and task governance in real multi-project use.
2. The current delegated development workflow also lacks durable task/state
   governance and is relying too much on conversation reconstruction.

## Main Decision

`IKE Runtime v0` must cover:

- `Project`
- `Task`
- `Decision`
- `MemoryPacket`
- `WorkContext`

This runtime kernel must not rely on:

- chat history as current truth
- docs as the only active-state source
- Redis as the only authority

## Runtime Truth Model

The current design separates four layers:

1. `Runtime State`
   - canonical operational truth
2. `Artifacts`
   - durable evidence and outputs
3. `Documents`
   - design intent, handoff, human-readable methods
4. `Memory`
   - selective recall layer

Short version:

- docs leave things behind
- state keeps system truth
- artifacts preserve evidence
- memory brings back what is relevant now

## Storage Decision

### PostgreSQL

Canonical source of truth for:

- projects
- tasks
- decisions
- work context
- task events
- task relations
- checkpoints
- memory packet metadata
- outbox events

### Redis

Acceleration only:

- queues
- leases
- hot pointers
- dedupe windows

### Object Storage

Heavy payloads:

- benchmark outputs
- study outputs
- closure payloads
- large checkpoints
- large memory packet bodies

## Task State Machine

Current minimum states:

- `inbox`
- `ready`
- `active`
- `waiting`
- `review_pending`
- `done`
- `failed`

Critical distinctions:

- `waiting` carries structured waiting reasons; `blocked` is not a separate
  durable v0 state
- `review_pending` != `done`
- `failed` != controller cancellation or deprioritization actions

Non-state control actions:

- `cancelled`
- `dropped`
- `deprioritized`

These are recorded as explicit events and controller decisions, not as first-cut
durable task states.

## Governance Decision

Roles are now explicitly separated:

- `controller`
- `delegate`
- `reviewer`
- `runtime`
- `scheduler`
- `user`

Most important rule:

- delegates may move bounded work to `review_pending`
- only controller may move reviewable work to `done`

## Transaction Boundary Decision

The design now requires atomic handling for:

- task creation
- state transitions
- review acceptance
- lease claim / expiry recovery
- checkpoint pointer updates
- outbox-backed side effects

The current v0 design also now requires:

- explicit `MemoryPacket` acceptance flow:
  - `draft -> pending_review -> accepted`
- explicit JSONB discipline:
  - extension space only
  - no canonical task state, acceptance state, waiting semantics, lease policy,
    or primary references may live only in JSONB

## Recovery Decision

The system must recover from:

- process restart
- stale active leases
- Redis loss
- partial side-effect failure
- artifact reference loss

Recovery order:

1. restore Postgres truth
2. restore object payload references
3. replay outbox
4. rebuild Redis caches and active queues

Lease expiry is expected to follow task-type policy rather than open-ended
operator judgment:

- `implementation -> waiting`
- `review -> review_pending`
- `study -> failed`
- `daemon -> ready`
- `workflow -> waiting`
- `maintenance -> ready`

## What This Is Trying To Prevent

The milestone is explicitly trying to prevent:

- task drift
- controller-state hidden in chat
- delegate self-acceptance
- fake durability through docs/search
- runtime truth hidden in Redis only
- memory hallucination caused by missing durable state

## Open Design Questions

These are the current highest-value review targets:

1. Is the current minimum object set sufficient, or still missing a critical
   first-class object?
2. Is the task state machine too large, too small, or semantically incorrect?
3. Are the role-permission boundaries correct, especially around:
   - `review_pending -> done`
   - runtime recovery transitions
   - memory packet acceptance
4. Is PostgreSQL + Redis + object storage the right early split?
5. Are the transaction boundaries correct enough to prevent silent drift?
6. Is `WorkContext` better as a durable object or should it later become
   partially derived?

## Review Absorption Since Initial Draft

The first external runtime review round has already been absorbed into the
design. The main changes were:

1. compress the v0 task state machine
2. move `blocked/cancelled/dropped` out of the durable state list
3. make `MemoryPacket` trust semantics explicit
4. define task-type lease expiry recovery policy
5. constrain JSONB so canonical state cannot drift into extension blobs

## Key Files

- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_SUBPROJECT_DECISION.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_SUBPROJECT_DECISION.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_TASK_STATE_AND_STORAGE_ARCHITECTURE.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_TASK_STATE_AND_STORAGE_ARCHITECTURE.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_DOCUMENT_AND_MEMORY_GOVERNANCE.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_DOCUMENT_AND_MEMORY_GOVERNANCE.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_DATA_MODEL_AND_TRANSACTION_BOUNDARIES.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_DATA_MODEL_AND_TRANSACTION_BOUNDARIES.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_ROLE_PERMISSIONS_AND_TRANSITION_MATRIX.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_ROLE_PERMISSIONS_AND_TRANSITION_MATRIX.md)
- [D:\code\MyAttention\docs\IKE_MAGMA_CHRONOS_MEMORY_RESEARCH_NOTE.md](/D:/code/MyAttention/docs/IKE_MAGMA_CHRONOS_MEMORY_RESEARCH_NOTE.md)

## Current Recommendation

This design is now ready for a focused cross-model architecture review before
implementation starts.

The main thing to challenge is not UI or polish.
It is whether the state model, role boundaries, and storage split are correct
enough to avoid expensive redesign later.
