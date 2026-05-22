# IKE Runtime v0 Implementation Packets

## Purpose

This document turns the current `IKE Runtime v0` design into bounded
implementation packets.

It is intentionally narrower than the full design tree.
It is meant for controller-driven delegation.

## Packet Design Rule

Each packet must:

- be additive where possible
- own a narrow write scope
- preserve truthful semantics
- avoid widening runtime capability beyond the current slice

These packets are for implementation preparation.
They are not acceptance by themselves.

## Packet R0-A: Core Runtime Schema Foundation

### Goal

Create the first durable schema layer for the runtime kernel.

### Scope

Add only the first canonical tables needed for the kernel:

- `runtime_projects`
- `runtime_tasks`
- `runtime_decisions`
- `runtime_task_events`
- `runtime_worker_leases`

### Allowed write scope

- migration files
- runtime ORM model definitions
- narrow schema/unit tests

### Forbidden expansion

- no queue workers
- no public API surface
- no notification objects
- no graph-memory structures
- no broad UI

### Acceptance target

- schema exists
- indexes exist
- status fields and key foreign links are explicit
- tests prove table/model shape

## Packet R0-B: Compressed Task State Machine Semantics

### Goal

Implement the compressed v0 task state model and guardrails.

### Scope

Support only:

- `inbox`
- `ready`
- `active`
- `waiting`
- `review_pending`
- `done`
- `failed`

Support controller actions as evented actions, not durable states:

- `cancelled`
- `dropped`
- `deprioritized`

### Allowed write scope

- runtime state helpers
- validation logic
- transition tests

### Forbidden expansion

- no custom workflow DSL
- no broad task orchestration engine
- no hidden state transitions in UI or chat logic

### Acceptance target

- illegal transitions are blocked
- `waiting` remains distinct from `review_pending`
- delegates cannot move reviewable work directly to `done`

## Packet R0-C: Task Event Log and Lease Semantics

### Goal

Make execution auditable and recoverable.

### Scope

Implement:

- append-only runtime task events
- durable worker lease records
- lease-expiry policy hooks by task type

### Allowed write scope

- event/lease persistence layer
- runtime recovery helpers
- tests for lease expiry paths

### Forbidden expansion

- no distributed scheduler redesign
- no outbox dispatcher implementation beyond current v0 need

### Acceptance target

- lease claim and expiry are durable
- recovery paths produce explicit events
- recovery cannot silently mark work `done`

## Packet R0-D: WorkContext Snapshot Carrier

### Goal

Create the narrowest restorable project working set object.

### Scope

Implement:

- `runtime_work_contexts`
- reconstruction helpers from canonical state

### Required constraint

`WorkContext` must not become a second truth source.

### Acceptance target

- one active work context per project
- fields are reconstructable from task/decision state plus accepted packet refs

## Packet R0-E: MemoryPacket Metadata and Acceptance

### Goal

Introduce truthful memory packet handling without pretending memory is already a
complete subsystem.

### Scope

Implement:

- `runtime_memory_packets`
- `draft -> pending_review -> accepted`
- accepted-upstream linkage

### Forbidden expansion

- no semantic retrieval engine
- no automatic memory trust promotion
- no broad memory graph

### Acceptance target

- packet existence does not imply trust
- accepted packets are auditably linked to reviewed upstream work

## Packet R0-F: Redis Acceleration and Recovery Rebuild

### Goal

Add acceleration without moving truth out of Postgres.

### Scope

Implement only:

- ready/active queue acceleration
- dedupe windows where already designed
- cache rebuild path from Postgres truth

### Acceptance target

- Redis loss does not destroy operational truth
- queues can be rebuilt from canonical state

## Controller Note

Recommended execution order:

1. `R0-A`
2. `R0-B`
3. `R0-C`
4. `R0-D`
5. `R0-E`
6. `R0-F`

Do not start with:

- UI
- public APIs
- richer memory
- notification/follow-up
- graph or semantic retrieval

Those belong to later runtime stages, not the first kernel slice.
