# IKE Runtime v0 Role Permissions and Transition Matrix

## Purpose

This document defines:

- which runtime roles exist
- which roles may move which objects between which states
- which transitions require controller acceptance

Without this layer, the task state machine will drift in practice even if the
state names are correct.

## 1. Core Judgment

State transitions are not just data changes.
They are governance decisions.

Therefore:

- not every actor may perform every transition
- delegate execution does not imply delegate acceptance
- automatic runtime recovery does not imply controller approval

## 2. Runtime Roles

Minimum role set:

- `controller`
- `delegate`
- `reviewer`
- `runtime`
- `scheduler`
- `user`

### 2.1 `controller`

Owns:

- project priority
- final acceptance
- semantic conflict resolution
- decision finalization
- transition override in exceptional cases

### 2.2 `delegate`

Owns:

- bounded task execution
- bounded study / implementation / review preparation
- checkpointing during owned execution

Delegate does **not** own:

- final acceptance
- strategic reprioritization
- closing reviewable work as `done`

### 2.3 `reviewer`

Owns:

- bounded review analysis
- review findings
- recommendation

Reviewer does **not** own:

- final task acceptance
- decision finalization

### 2.4 `runtime`

Owns:

- lease expiry handling
- daemon/maintenance task orchestration
- queue transitions allowed by policy
- non-semantic recovery transitions

Runtime does **not** own:

- strategic meaning
- final review acceptance

### 2.5 `scheduler`

Owns:

- recurring task instantiation
- enqueueing task instances

Scheduler does **not** own:

- execution acceptance
- semantic resolution

### 2.6 `user`

Owns:

- external instruction input
- explicit stop/pause/cancel intent
- project-level overrides where allowed

## 3. Object-Level Permission Rules

### 3.1 Project

Controller-only transitions by default:

- `active -> paused`
- `active -> blocked`
- `active -> completed`
- `completed -> archived`
- `blocked -> active`

User may request these transitions, but controller or policy layer should record
the effective transition.

### 3.2 Task

Task transitions are split by role.

### 3.3 Decision

Only controller should finalize a decision to `final`.

Reviewer and delegate may propose decision artifacts, but not finalize them.

### 3.4 MemoryPacket

Creation may be runtime-assisted or delegate-assisted.

Acceptance of a memory packet as trusted packet should depend on:

- accepted task state
- or accepted controller/review flow

## 4. Task Transition Permission Matrix

Legend:

- `Y` = allowed directly
- `R` = allowed only via review/controller confirmation
- `P` = allowed only by runtime policy/recovery logic
- `N` = not allowed

### 4.1 Transitions from `inbox`

| Transition | Controller | Delegate | Reviewer | Runtime | Scheduler | User |
|---|---|---:|---:|---:|---:|---:|
| `inbox -> ready` | Y | N | N | P | N | N |

### 4.2 Transitions into `active`

| Transition | Controller | Delegate | Reviewer | Runtime | Scheduler | User |
|---|---|---:|---:|---:|---:|---:|
| `ready -> active` | Y | Y | N | P | N | N |
| `review_pending -> active` | Y | N | N | N | N | N |
| `failed -> active` | N | N | N | N | N | N |

Rule:

- `delegate` may move `ready -> active` only when explicitly assigned or when
  lease claim succeeds under policy

### 4.3 Transitions during execution

| Transition | Controller | Delegate | Reviewer | Runtime | Scheduler | User |
|---|---|---:|---:|---:|---:|---:|
| `active -> waiting` | Y | Y | N | P | N | N |
| `active -> review_pending` | Y | Y | N | N | N | N |
| `active -> failed` | Y | Y | N | P | N | N |

Rule:

- delegate may move work to `review_pending`, but not to `done`
- runtime may move stale or policy-managed tasks to `waiting/failed`
  only through explicit recovery logic

### 4.4 Recovery transitions

| Transition | Controller | Delegate | Reviewer | Runtime | Scheduler | User |
|---|---|---:|---:|---:|---:|---:|
| `waiting -> ready` | Y | N | N | P | N | N |
| `failed -> ready` | Y | N | N | P | N | N |

Rule:

- runtime may perform these only for policy-based recovery, lease expiry, or
  automated retry paths
- semantic reclassification belongs to controller

### 4.5 Review completion transitions

| Transition | Controller | Delegate | Reviewer | Runtime | Scheduler | User |
|---|---|---:|---:|---:|---:|---:|
| `review_pending -> done` | Y | N | N | N | N | N |
| `review_pending -> active` | Y | N | N | N | N | N |

This is the most important gate:

- only controller can move reviewable delegate work to `done`

### 4.6 Non-state terminal actions

V0 treats cancel/drop/deprioritize as evented control actions rather than
first-class durable task states.

These actions may still originate from:

- controller
- user request routed through controller/policy

but should be represented through:

- task event reason
- controller decision
- metadata / closure note

## 5. Decision Permission Matrix

### Drafting

Allowed:

- controller
- delegate
- reviewer
- runtime (only for machine-generated recommendation records, not final decision)

### Review Pending

Allowed:

- controller
- reviewer

### Finalization

Allowed:

- controller only

### Superseding

Allowed:

- controller only

## 6. MemoryPacket Permission Matrix

### Create Draft Packet

Allowed:

- controller
- delegate
- runtime

### Accept Packet as Trusted Recovery Packet

Allowed:

- controller
- runtime only when linked to already-accepted task/decision closure by policy

Recommended early rule:

- controller acceptance first
- packet status should move through `draft -> pending_review -> accepted`

## 7. Lease and Ownership Rules

### Claim

Allowed:

- delegate
- runtime
- controller

### Heartbeat

Allowed:

- current owner only

### Expire

Allowed:

- runtime only

### Reassign

Allowed:

- controller
- runtime only under stale-lease policy

## 8. Guardrails

### Guardrail 1

No delegate may directly mark their own reviewable work `done`.

### Guardrail 2

No runtime recovery path may silently finalize a strategic decision.

### Guardrail 3

No scheduler-created task should enter `active` without a valid claim path.

### Guardrail 4

No accepted memory packet should exist without accepted upstream state or
accepted review.

## 9. Recommended Early Implementation Policy

Keep the first version strict.

Prefer:

- fewer allowed transitions
- explicit controller acceptance
- explicit runtime recovery rules

Avoid:

- optimistic implicit state promotion
- auto-done behavior
- delegate self-acceptance

## 10. Current Recommendation

Implement the state machine together with this permission matrix.

Do not:

- implement states first and governance later
- let each worker tool invent its own task semantics
- rely on convention instead of explicit transition checks

The whole point of `IKE Runtime v0` is to stop losing control as delegation
increases.
