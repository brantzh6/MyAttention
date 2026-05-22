# IKE Runtime v0 Task State and Storage Architecture

## Purpose

This document hardens the task-management side of `IKE Runtime v0`.

It exists because task governance is now a critical system boundary for both:

- OpenClaw runtime continuity
- controller/delegate engineering continuity

If this layer is designed loosely now, later migration cost will be high.
Therefore this document prioritizes:

- explicit state semantics
- explicit storage responsibilities
- explicit recovery model
- explicit operational tradeoffs

This is a design document, not an implementation shortcut.

## 1. Core Judgment

Task management in `IKE Runtime v0` is **not** just a UI queue.

It is the control layer that must reliably answer:

- what is active
- what is blocked
- what is waiting on whom
- what changed
- what decision already constrained the next step
- what can be safely resumed after interruption

Therefore the system must treat:

- task state
- decision state
- work context
- memory packet

as durable first-class runtime state, not chat-derived convenience data.

## 2. Design Principles

### 2.1 Postgres is the source of truth

Task state must not live primarily in:

- chat history
- ephemeral in-memory objects
- Redis-only queues
- benchmark artifacts only

The source of truth must be durable relational state in PostgreSQL.

### 2.2 Redis is acceleration, not authority

Redis may be used for:

- hot work queues
- locks / leases
- fast checkpoint pointers
- dedupe windows
- recent active-index acceleration

Redis must not become the only place where task truth exists.

### 2.3 State machine before automation

Do not add smart automation before task states are explicit.

If the system cannot faithfully distinguish:

- `waiting`
- `blocked`
- `paused`
- `retryable_failed`
- `done`

then automation will create confusion faster than it creates value.

### 2.4 Decisions constrain tasks

Task management without durable `Decision` objects will drift.

The system must preserve:

- why a task was created
- why a task was deferred
- why a task was rejected
- why the next action changed

### 2.5 Resume must be first-class

Every active or long-running task should be designed as resumable by default.

If a task cannot be resumed, that must be explicit.

## 3. Minimum Runtime Objects

`IKE Runtime v0` should start from five core objects:

- `Project`
- `Task`
- `Decision`
- `MemoryPacket`
- `WorkContext`

Additional supporting objects:

- `TaskEvent`
- `TaskRelation`
- `TaskCheckpoint`
- `WorkLease`
- `OutboxEvent`

## 4. Task Types

Task type and task state must be distinct.

### 4.1 Task Types

Minimum task types:

- `inbox`
  - untriaged captured work
- `study`
  - bounded research or review packet
- `implementation`
  - bounded coding/change packet
- `review`
  - bounded review/acceptance packet
- `maintenance`
  - operational/runtime upkeep
- `workflow`
  - multi-step orchestration task
- `daemon`
  - recurring or watch-style task instance

Do not overload type to express status.

## 5. Task State Machine

### 5.1 Canonical States

Recommended v0 task states:

- `inbox`
- `ready`
- `active`
- `waiting`
- `review_pending`
- `done`
- `failed`

These states are intentionally compressed for v0.

Deferred distinctions such as:

- `triaged`
- `blocked`
- `cancelled`
- `dropped`

should not become separate durable v0 states unless later implementation proves
they are necessary.

### 5.2 State Semantics

- `inbox`
  - captured but not yet evaluated
- `ready`
  - executable now; prerequisites are satisfied
- `active`
  - currently owned by a worker, delegate, or controller
- `waiting`
  - paused pending expected external progress
  - example: waiting for user input, waiting for delegate result, waiting on a
    missing dependency, waiting on manual intervention
- `review_pending`
  - execution ended, awaiting controller or review gate
- `done`
  - completed and accepted
- `failed`
  - execution ended unsuccessfully without a reviewed recovery path

### 5.3 Critical Distinctions

#### `waiting` reasons

V0 should model blocked situations through `waiting_reason`, not a separate
durable `blocked` state.

Recommended examples:

- `external_input`
- `delegate_result`
- `dependency_unmet`
- `capability_missing`
- `manual_intervention`

#### `done` vs `review_pending`

- `review_pending`
  - execution result exists
  - not yet controller-accepted
- `done`
  - reviewed and accepted

Delegates should not place their own tasks directly into `done`.

#### `failed` vs non-priority continuation

V0 only needs `failed` as the canonical unsuccessful terminal state.

Abandonment, deprioritization, or cancellation should be represented through:

- task event reason
- controller decision
- project/task metadata

### 5.4 Allowed State Transitions

```text
inbox -> ready
ready -> active
active -> waiting
active -> review_pending
active -> failed
waiting -> ready
review_pending -> done
review_pending -> active
failed -> ready
```

Invalid transitions should be rejected at the application layer.

Any stop/deprioritize path should be modeled as:

- evented control action
- explicit controller decision
- metadata / closure note

not as a separate first-cut durable task state.

## 6. Project State Model

Project state should remain simpler than task state.

Recommended project states:

- `active`
- `paused`
- `blocked`
- `completed`
- `archived`

Project state is not derived automatically only from task counts.
It should be explicit, with metrics as support, not replacement.

## 7. Decision State Model

Recommended decision outcomes:

- `adopt`
- `reject`
- `defer`
- `escalate`

Recommended decision lifecycle:

- `draft`
- `review_pending`
- `final`
- `superseded`

Do not collapse decision outcome into task state.

## 8. Storage Responsibilities

### 8.1 PostgreSQL

Postgres should store:

- canonical `Project`
- canonical `Task`
- canonical `Decision`
- canonical `MemoryPacket` metadata
- canonical `WorkContext`
- `TaskEvent`
- `TaskRelation`
- `TaskCheckpoint` metadata
- `OutboxEvent`
- audit timestamps and actor references

Postgres is responsible for:

- integrity
- foreign keys
- replayable state
- recovery after restart
- historical queryability

### 8.2 Redis

Redis should store only acceleration primitives:

- active task queue
- per-project ready queue
- worker lease keys
- short-lived dedupe windows
- recent pointer caches
- checkpoint hot pointers

Redis is responsible for:

- fast dispatch
- lease expiration
- low-latency active-set lookup

If Redis is lost, the system should degrade but remain recoverable from Postgres.

### 8.3 Queue Layer

Prefer a queue built from:

- Postgres-backed truth
- Redis-backed dispatch acceleration

Do **not** start with a heavy external workflow engine.

`IKE Runtime v0` should first prove:

- durable state
- resumable execution
- clean handoff

before buying more orchestration complexity.

### 8.4 Object / Blob Storage

Use object storage for:

- large artifacts
- large memory packet payloads
- study outputs
- benchmark closure payloads
- snapshots/checkpoints too large for inline DB storage

Postgres stores references and metadata, not the large blob itself.

## 9. Suggested Relational Model

### 9.1 Tables

Minimum recommended tables:

- `runtime_projects`
- `runtime_tasks`
- `runtime_decisions`
- `runtime_memory_packets`
- `runtime_work_contexts`
- `runtime_task_events`
- `runtime_task_relations`
- `runtime_task_checkpoints`
- `runtime_outbox_events`
- `runtime_worker_leases`

### 9.2 Key Constraints

- unique task id
- unique decision id
- foreign key task -> project
- foreign key task event -> task
- foreign key relation source/target validated by type-aware application logic
- only one current active `WorkContext` per project
- only one active lease per task

## 10. Task Ownership and Leases

Task ownership should be explicit.

Fields to preserve:

- `owner_kind`
  - `controller`
  - `delegate`
  - `runtime`
- `owner_id`
- `lease_expires_at`
- `heartbeat_at`

This is necessary because:

- controller work
- delegated work
- automated recurring work

must all coexist without ghost ownership.

### Lease Rule

A task in `active` should normally have an active lease.
If lease expires:

- task should not silently stay trusted as active forever
- system should move it to:
  - `waiting`
  - or `blocked`
  - or a recovery triage path

depending on task type and policy

## 11. Checkpoints and Resume

Every non-trivial task should support checkpoint metadata:

- last durable step
- last artifact emitted
- next resumable input
- known blocker / open question

Task checkpoints should not require replaying full chat history.

### Checkpoint Storage Rule

- checkpoint metadata in Postgres
- large checkpoint payload in object storage when necessary
- hot pointer in Redis allowed, but only as cache

## 12. Outbox and Side Effects

If task transitions produce side effects such as:

- notifications
- downstream queue dispatch
- memory packet creation
- benchmark closure updates

use an outbox pattern.

Reason:

- state transition and side effect publication should not drift apart

Recommended flow:

1. state change transaction writes durable task state
2. same transaction writes `runtime_outbox_events`
3. async dispatcher reads outbox and publishes side effects
4. publication status is recorded

This reduces lost-event and double-dispatch problems.

## 13. Backup and Recovery

### 13.1 What Must Be Recoverable

At minimum, the system must be able to recover:

- projects
- tasks and statuses
- decisions
- current next actions
- checkpoints
- memory packet references
- work context

### 13.2 Backup Strategy

Minimum recommended strategy:

- PostgreSQL logical backups on schedule
- object storage snapshot/versioning for artifact payloads
- exportable project/task/decision state dumps
- periodic restore drill, not just backup existence

Redis persistence is optional for performance recovery, but not sufficient for
system recovery.

### 13.3 Restore Priority

Restore order should be:

1. Postgres canonical state
2. object storage references
3. replay outbox if needed
4. rebuild Redis caches and queues from Postgres

## 14. Failure Modes to Design For

### 14.1 Delegate never returns

System behavior:

- lease expires
- task moves from `active` to recovery path
- controller can see it as stale rather than silently lost

### 14.2 Chat/session lost

System behavior:

- task and next action remain reconstructable from runtime state
- not dependent on raw conversation replay

### 14.3 Redis loss

System behavior:

- dispatch slows
- active queues rebuild from Postgres truth

### 14.4 Partial side effect failure

System behavior:

- task state already durable
- outbox records pending side effect
- dispatcher retries safely

### 14.5 Benchmark/story closure emitted but not accepted

System behavior:

- remains `review_pending`
- does not become durable accepted procedural memory automatically

## 15. Controller/Delegate Development Use

This runtime kernel should also support the project's own AI-assisted delivery.

That means task objects must be able to represent:

- external delegate packet
- coding packet
- review packet
- study packet
- closure packet

And preserve:

- packet id
- delegate type
- allowed files
- validation expectation
- review status
- accepted outcome
- next packet

Without this, the project's own development process will continue to rely on
chat reconstruction and manual memory.

## 16. Recommended First Implementation Cut

Do not implement the entire runtime kernel at once.

Recommended cut:

### Cut A

- `Project`
- `Task`
- `Decision`
- `TaskEvent`
- minimal state machine enforcement
- Postgres only, no Redis dependency yet for correctness

### Cut B

- `MemoryPacket`
- `WorkContext`
- checkpoint metadata
- closure-to-memory adapter

### Cut C

- Redis acceleration
- leases
- ready/active queues
- stale-task recovery helpers

### Cut D

- outbox dispatcher
- notifications / packet follow-up hooks

This sequence keeps correctness before speed.

## 17. Open Questions That Must Be Resolved Before Build

1. Is `WorkContext` a durable table or a derived materialized view over active
   tasks and latest decisions?
   - recommendation: start durable, derive later if needed

2. Should `MemoryPacket` be immutable snapshots or mutable rolling summaries?
   - recommendation: immutable snapshots with explicit parent linkage

3. Do recurring daemon-style tasks share the same table as normal tasks?
   - recommendation: yes, with a `task_type` and recurrence metadata

4. How are cross-project personal inbox items represented?
   - recommendation: a special inbox project or user-scoped project bucket,
     not orphan tasks

5. What qualifies as controller acceptance for `done`?
   - recommendation: explicit accepted event, not absence of objection

## 18. Current Recommendation

Lock this task/state/storage architecture before major implementation starts.

The cost of changing:

- task states
- lease semantics
- source-of-truth location
- recovery strategy

later will be much higher than spending extra design time now.

Short version:

- Postgres for truth
- Redis for speed
- object storage for heavy artifacts
- explicit state machine
- explicit leases
- explicit outbox
- explicit recovery model
- one runtime kernel serving both product continuity and engineering continuity
