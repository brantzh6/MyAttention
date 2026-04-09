# IKE Runtime v0 R1-C5 Assignment Truth Options

## Purpose

`R1-C5` cannot truthfully wire a Postgres-backed `ClaimVerifier` until
`EXPLICIT_ASSIGNMENT` has one explicit durable truth source.

This note narrows the viable options and records the controller
recommendation.

## The Problem

The runtime currently distinguishes two claim types:

- `ACTIVE_LEASE`
- `EXPLICIT_ASSIGNMENT`

`ACTIVE_LEASE` already has a clear durable truth source:

- `runtime_worker_leases`
- `runtime_tasks.current_lease_id`

`EXPLICIT_ASSIGNMENT` does not.

The current schema has these nearby fields:

- `runtime_tasks.owner_kind`
- `runtime_tasks.owner_id`
- `runtime_task_events`

But there is no dedicated runtime assignment table.

## Option A: Use Task Ownership Fields As Assignment Truth

Definition:

- a task is explicitly assigned when:
  - `runtime_tasks.owner_kind = delegate`
  - `runtime_tasks.owner_id = <delegate_id>`
- event log remains audit evidence, not the primary truth source

Pros:

- uses existing durable schema
- keeps `R1-C5` narrow
- does not introduce a new runtime object family
- makes current truth simple to query

Cons:

- task ownership semantics must be tightened and documented
- controller/runtime must be careful about when ownership is assignment vs
  temporary execution state

## Option B: Use Task Events As Assignment Truth

Definition:

- `EXPLICIT_ASSIGNMENT` is reconstructed from append-only task events

Pros:

- preserves a pure event-history story
- no new table required

Cons:

- reconstructing current truth from events is heavier
- more error-prone for v0
- makes `ClaimVerifier` more complex than needed
- risks mixing audit history with current truth

## Option C: Add A New Assignment Object

Definition:

- create a new durable runtime assignment object/table and verify against it

Pros:

- semantically clean
- future-extensible

Cons:

- broadens `R1-C5`
- introduces a new runtime object family
- expensive to reverse if done too early
- not aligned with current narrow `R1-C` hardening envelope

## Controller Recommendation

Recommended for `v0`:

- choose **Option A**

Interpretation:

- task ownership fields become the current durable truth for explicit
  assignment
- task events remain the audit trail explaining when that assignment happened
- active lease remains a separate, stricter execution claim verified through
  lease tables

## Guardrail

If Option A is accepted, `R1-C5` must still not:

- treat ownership and lease as the same thing
- skip event/audit recording
- silently infer assignment from arbitrary metadata fields

## What Changes After Decision

If Option A is accepted:

1. `R1-C5` becomes execution-ready
2. `ClaimVerifier` can verify:
   - `EXPLICIT_ASSIGNMENT` via `runtime_tasks.owner_kind/owner_id`
   - `ACTIVE_LEASE` via `runtime_worker_leases`
3. `R1-C5` remains a narrow runtime/service-layer packet

## Decision

Decision date:

- `2026-04-07`

Decision:

- accepted
- `R1-C5` will use **Option A**
- `runtime_tasks.owner_kind/owner_id` is the current `v0` durable truth source
  for `EXPLICIT_ASSIGNMENT`

Implication:

- `R1-C5` is now execution-ready after `R1-C6`
