# IKE Runtime v0 Data Model and Transaction Boundaries

## Purpose

This document translates the runtime-kernel direction into implementation-grade
design constraints.

It answers three questions:

1. what the minimum durable schema should look like
2. where transactional boundaries must exist
3. how recovery should work when execution is interrupted or partially fails

This is still a design document.
It is intended to reduce implementation drift before code is written.

## 1. Canonical Rule

The runtime kernel must separate:

- durable control state
- execution acceleration
- evidence payloads
- recall summaries

The implementation must not collapse these into one table, one queue, or one
document search layer.

## 2. Minimum Durable Schema

PostgreSQL is the canonical source of truth.

### 2.1 `runtime_projects`

Represents a long-lived project scope.

Minimum fields:

- `project_id` UUID or typed string primary key
- `project_key` stable human-readable unique key
- `title`
- `goal`
- `status`
- `current_phase`
- `priority`
- `owner_type`
- `owner_id`
- `current_work_context_id` nullable
- `blocker_summary` nullable
- `next_milestone` nullable
- `created_at`
- `updated_at`
- `closed_at` nullable
- `metadata` JSONB

Required indexes:

- unique `project_key`
- `status`
- `updated_at`

### 2.2 `runtime_tasks`

Represents a durable executable or reviewable work unit.

Minimum fields:

- `task_id`
- `project_id`
- `task_type`
- `title`
- `goal`
- `status`
- `priority`
- `owner_kind`
- `owner_id` nullable
- `parent_task_id` nullable
- `decision_id` nullable
- `active_checkpoint_id` nullable
- `current_lease_id` nullable
- `review_required` boolean
- `review_status` nullable
- `waiting_reason` nullable
- `waiting_detail` nullable
- `lease_expiry_policy` nullable
- `next_action_summary` nullable
- `result_summary` nullable
- `created_at`
- `started_at` nullable
- `ended_at` nullable
- `updated_at`
- `metadata` JSONB

Required indexes:

- `project_id, status`
- `status, priority`
- `owner_kind, owner_id`
- `parent_task_id`
- `updated_at`

### 2.3 `runtime_decisions`

Represents durable decision state.

Minimum fields:

- `decision_id`
- `project_id`
- `task_id` nullable
- `decision_scope`
- `title`
- `summary`
- `rationale`
- `outcome`
- `status`
- `impact_scope`
- `supersedes_decision_id` nullable
- `created_by_kind`
- `created_by_id`
- `created_at`
- `finalized_at` nullable
- `metadata` JSONB

Required indexes:

- `project_id, status`
- `task_id`
- `outcome`
- `finalized_at`

### 2.4 `runtime_memory_packets`

Represents compact recoverable runtime summaries.

Minimum fields:

- `memory_packet_id`
- `project_id`
- `task_id` nullable
- `packet_type`
- `status`
- `acceptance_trigger` nullable
- `title`
- `summary`
- `storage_ref` nullable
- `content_hash` nullable
- `parent_packet_id` nullable
- `created_by_kind`
- `created_by_id`
- `created_at`
- `accepted_at` nullable
- `metadata` JSONB

Rule:

- packets are snapshots, not mutable living documents
- packet acceptance must be explicit or policy-linked

### 2.5 `runtime_work_contexts`

Represents the current restorable working set for a project.

Minimum fields:

- `work_context_id`
- `project_id`
- `status`
- `active_task_id` nullable
- `latest_decision_id` nullable
- `current_focus`
- `blockers_summary` nullable
- `next_steps_summary` nullable
- `packet_ref_id` nullable
- `updated_at`
- `metadata` JSONB

Recommended rule:

- one active work context per project

Important:

- `runtime_work_contexts` must not become a second truth source
- its fields should be derivable from canonical task/decision state and accepted
  packet references

### 2.6 `runtime_task_events`

Append-only event log for state transitions and important execution actions.

Minimum fields:

- `event_id`
- `project_id`
- `task_id`
- `event_type`
- `from_status` nullable
- `to_status` nullable
- `triggered_by_kind`
- `triggered_by_id`
- `reason`
- `payload` JSONB
- `created_at`

Rule:

- append-only

### 2.7 `runtime_task_relations`

Explicit relation table.

Minimum fields:

- `relation_id`
- `source_task_id`
- `relation_type`
- `target_task_id`
- `created_at`
- `metadata` JSONB

Supported early relation types:

- `depends_on`
- `blocks`
- `refines`
- `reviews`
- `follows`

### 2.8 `runtime_task_checkpoints`

Checkpoint metadata table.

Minimum fields:

- `checkpoint_id`
- `task_id`
- `checkpoint_type`
- `step_label`
- `summary`
- `storage_ref` nullable
- `created_at`
- `metadata` JSONB

### 2.9 `runtime_worker_leases`

Ephemeral-but-durable ownership records.

Minimum fields:

- `lease_id`
- `task_id`
- `owner_kind`
- `owner_id`
- `lease_status`
- `heartbeat_at`
- `expires_at`
- `created_at`
- `metadata` JSONB

Rule:

- only one active lease per task

### 2.10 `runtime_outbox_events`

Supports reliable side effects.

Minimum fields:

- `outbox_id`
- `aggregate_type`
- `aggregate_id`
- `event_type`
- `payload` JSONB
- `publish_status`
- `attempt_count`
- `last_attempt_at` nullable
- `created_at`

Current implementation note:

- keep this as an architectural slot
- allow first implementation to defer a full dispatcher if same-process
  transaction-bound side effects are sufficient

## 3. What Should Not Be Inline

Large payloads should not live inline in Postgres rows when avoidable.

Move to object storage when payloads are:

- large benchmark result bodies
- large study outputs
- full delegate result packages
- large memory snapshots
- detailed checkpoints

Store in Postgres:

- metadata
- references
- content hash
- acceptance status

## 4. Transaction Boundaries

This is the most important implementation constraint.

### 4.1 Task Creation Transaction

One transaction should create:

- `runtime_tasks` row
- optional initial `runtime_task_events` row
- optional `runtime_task_relations`
- optional `runtime_outbox_events`

This prevents task creation without lifecycle trace.

### 4.2 State Transition Transaction

A task state transition should be one transaction that writes:

- new `runtime_tasks.status`
- `updated_at`
- any changed `waiting_reason`
- any changed `next_action_summary`
- new `runtime_task_events` row
- optional `runtime_outbox_events`

Do not split state update and event append into different non-atomic steps.

### 4.3 Review Acceptance Transaction

When a reviewable task becomes `done`, one transaction should update:

- `runtime_tasks.status = done`
- `review_status = accepted`
- acceptance event
- optional linked decision finalization
- optional memory packet acceptance or packet-review request

This is necessary to avoid "accepted in spirit but not in state."

### 4.4 Lease Claim Transaction

Claiming a task for execution should atomically:

- verify task is claimable
- create or activate lease
- move task to `active`
- append task event

### 4.5 Lease Expiry Recovery Transaction

When lease expiry is detected, a recovery transaction should:

- mark lease expired
- move task away from stale `active`
- append recovery event
- optionally emit outbox follow-up

Recommended v0 lease expiry policy table:

| task_type | default recovery target | note |
|---|---|---|
| `implementation` | `waiting` | may resume after reassignment |
| `review` | `review_pending` | produced output may still be reviewable |
| `study` | `failed` | interrupted study usually needs explicit restart |
| `daemon` | `ready` | future recurrence can re-dispatch |
| `workflow` | `waiting` | preserve chain, require explicit next action |
| `maintenance` | `ready` | retries are normal |

### 4.6 Checkpoint Transaction

Checkpoint writes should atomically:

- store checkpoint metadata
- update task's active checkpoint pointer
- append event

Large payload upload may be external, but final pointer registration should be
the atomic DB step.

## 5. Outbox Discipline

Outbox is mandatory for any state transition that triggers async side effects.

Examples:

- notify controller
- dispatch review packet
- create memory packet
- emit benchmark closure update
- enqueue delegate follow-up

Rule:

- never rely on "write state, then hope the side effect succeeds"

## 6. Read Paths

### 6.1 Project Dashboard Read

Should read from Postgres truth:

- project
- active tasks
- blocked tasks
- latest decisions
- latest work context

Redis may accelerate active lists, but must not be required for correctness.

### 6.2 Resume Project Read

Should reconstruct from:

- current `runtime_work_contexts`
- active or waiting tasks
- latest accepted decisions
- latest accepted memory packet

Not from raw chat search.

### 6.3 Engineering Workflow Read

For controller/delegate continuity, the system should be able to read:

- active project
- active task
- pending review tasks
- blocked tasks
- recent accepted decisions
- next action

without diffing free-form notes.

## 7. Recovery Strategy

### 7.1 Normal Restart

After normal service restart:

1. load active projects
2. load tasks with `active/waiting/blocked/review_pending`
3. detect expired leases
4. rebuild Redis caches from Postgres
5. resume dispatcher from outbox

### 7.2 Partial Failure Recovery

If a process dies after DB commit but before async work:

- outbox guarantees eventual replay

If a process dies before DB commit:

- no partial state should be visible

### 7.3 Stale Active Task Recovery

Any task in `active` without healthy lease must be recoverable into:

- `waiting`
- `blocked`
- or recovery-triage

depending on policy

### 7.4 Artifact Loss Handling

If object-storage payload is missing but metadata exists:

- task must not be considered silently healthy
- mark derived reads as degraded
- emit integrity event

## 8. Backup Strategy

### 8.1 PostgreSQL

Required:

- scheduled logical backup
- WAL or snapshot strategy if available
- restore drills

### 8.2 Object Storage

Required:

- versioning or snapshot policy
- content-hash integrity checks for important payloads

### 8.3 Redis

Optional:

- persistence for warm recovery

But Redis restore is not the system restore strategy.

## 9. JSONB Discipline

JSONB is extension space, not primary model space.

Do not store these primarily inside JSONB:

- canonical task state
- review acceptance state
- waiting semantics
- lease policy
- decision outcome
- key object references

Safe JSONB usage:

- low-stability auxiliary metadata
- provider-specific fragments
- optional provenance detail
- debug support payloads

## 10. Concurrency Rules

### Rule 1

No task should have two active leases.

### Rule 2

Only controller acceptance can move reviewable delegate work from
`review_pending` to `done`.

### Rule 3

`Decision` finalization should not be implicit side effect from a task finishing.

### Rule 4

`MemoryPacket` should not be treated as accepted unless linked from accepted
state or accepted review flow.

## 11. MemoryPacket Acceptance Flow

Recommended v0 packet lifecycle:

1. `draft`
2. `pending_review`
3. `accepted`

Recommended rule:

- packet existence does not imply packet trust
- accepted upstream task/decision state may make a packet reviewable
- controller acceptance or explicit policy should make it trusted

## 12. Implementation Order

### Phase A

- schema
- canonical state transitions
- event append
- review gate semantics

### Phase B

- work context
- checkpoint pointers
- decision linkage

### Phase C

- lease model
- Redis acceleration
- stale-active recovery

### Phase D

- outbox dispatcher
- artifact-backed packets
- closure-to-memory wiring

## 13. Current Recommendation

Do not begin implementation from:

- UI task board
- free-form note system
- Redis queue first
- vector memory first

Begin from:

- canonical Postgres schema
- explicit state transitions
- events
- decisions
- work context

That is the only stable foundation for later memory and intelligence layers.
