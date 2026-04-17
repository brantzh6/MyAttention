# IKE Runtime v0 - R2-I5 Phase Judgment

Date: 2026-04-10
Phase: `R2-I5 PG-Backed Lifecycle Proof`
Status: `candidate next packet inside R2-I`

## Why This Packet Exists

Review #11 corrected the meaning of `R2-I1`:

- `R2-I1` proves a live-service-adjacent state-machine lifecycle path
- it does not yet prove a Postgres-backed lifecycle fact path

The next narrow runtime question is therefore not whether the proof route works.
It is whether one lifecycle path can be executed through the current durable
runtime truth surfaces:

- `runtime_tasks`
- `runtime_task_events`
- `runtime_worker_leases`
- `PostgresClaimVerifier`

## Intended Scope

Prove one narrow lifecycle path through the PG-backed runtime truth layer.

Target shape:

- one runtime project
- one runtime task
- one durable lease-backed delegate claim
- append-only task events
- truthful final task row

## Explicit Non-Goals

- no general task CRUD API
- no scheduler or daemon layer
- no broad DB-backed task platform
- no broad UI/runtime integration
- no broad work-context persistence redesign

## Why This Is Narrow Enough

The current project already has:

- runtime schema
- DB-backed pytest fixture
- `PostgresClaimVerifier`

So `R2-I5` is not opening a new subsystem.
It is closing the precise semantic gap identified by review.

## Controller Judgment

`R2-I5` is the correct next narrow packet if the runtime mainline wants to
answer the review concern directly instead of deferring it behind unrelated debt.
