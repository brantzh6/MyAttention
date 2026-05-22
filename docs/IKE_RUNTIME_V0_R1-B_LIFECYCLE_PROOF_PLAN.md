# IKE Runtime v0 R1-B Lifecycle Proof Plan

## Purpose

`R1-B` is the first real task lifecycle proof through the runtime kernel.

It should prove one narrow path:

- `inbox -> ready -> active -> review_pending -> done`

This is not broad runtime integration.
It is the smallest truthful proof that the current kernel can carry one real task
through its intended durable states, events, and review boundary.

## Preconditions

Satisfied before `R1-B`:

- `R0-A ~ R0-F` first-wave kernel exists
- `R1-A` hardening cycle completed
- `R1-A5-FIX` restored legal claim behavior and stabilized migration subset tests

Remaining preserved items do not block `R1-B`:

- legacy `allow_claim=True` removal
- service-layer identity verification
- live Postgres migration up/down proof

## Proof Target

The lifecycle proof must demonstrate:

1. one task record can be created in `inbox`
2. controller triage can move it to `ready`
3. a legal claim path can move it to `active`
4. execution completion can move it to `review_pending`
5. controller review can move it to `done`
6. task events reflect the path in order
7. task updates remain consistent with state-machine rules

## Not In Scope

- broad scheduler integration
- real benchmark/runtime connection
- work-context UI
- graph memory
- broad object access
- multi-task orchestration

## Packet Shape

### R1-B1

- coding
- create the narrow lifecycle proof helper and tests

### R1-B2

- review
- inspect lifecycle truthfulness and state/event consistency

### R1-B3

- test
- independently validate one real lifecycle path

### R1-B4

- evolution
- extract method upgrades from the first true lifecycle proof

## Success Standard

`R1-B` succeeds if:

1. one real lifecycle path passes under live tests
2. state and event history align
3. review boundary is preserved
4. no new runtime objects are invented just to make the demo pass
