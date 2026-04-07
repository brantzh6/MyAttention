# IKE Runtime v0 Second-Wave Enforcement Cycle

## Purpose

This document defines the next narrow runtime cycle after the first
`R1-A` hardening cycle completed with `accept_with_changes`.

It exists to prevent premature movement into `R1-B`.

Current controller judgment:

- `R1-A` proved the second-wave shape is real
- `R1-A` did not fully close the main enforcement soft spots
- one more narrow enforcement cycle should happen before a real task lifecycle

## What This Cycle Must Close

### 1. Legacy Force Softness

Current problem:

- `force=True` remains soft when `role=None`

Required direction:

- close the path entirely
- or add an explicit deprecation / rejection path
- do not preserve a silent legacy bypass

### 2. Verifier Trust Contract

Current problem:

- trusted memory still depends on caller-supplied verifier wiring

Required direction:

- narrow the contract
- make service-layer expectations explicit
- make fake or omitted verifier wiring harder to treat as trustworthy

### 3. Claim Proof Hardness

Current problem:

- `ClaimContext` is better than `allow_claim`, but internal validation is still
  weak and service-layer identity truth is not tightened enough

Required direction:

- strengthen claim validation semantics without broadening runtime scope

### 4. Test Invocation Stability

Current problem:

- migration validation currently depends on specific invocation assumptions

Required direction:

- make the test path stable and repeatable

## Packet Shape

### R1-A5

- coding
- narrow enforcement hardening only

### R1-A6

- review
- semantic truthfulness / enforcement boundary review

### R1-A7

- test
- explicit regression and negative-path validation

### R1-A8

- evolution
- absorb what should become durable method rules

## Entry Rule

Do not start `R1-B` until:

- `R1-A5` is complete
- `R1-A6` is reviewed
- `R1-A7` is validated
- `R1-A8` has durable absorption

## Not In Scope

- real task lifecycle
- broad UI
- scheduler expansion
- graph/semantic memory
- new first-class runtime objects

## Success Standard

This cycle succeeds if:

1. `role=None` is no longer a silent force escape hatch
2. verifier trust is more explicit and harder to fake
3. claim proof semantics are tighter than the current partial hardening
4. runtime tests are stable to run without fragile path assumptions
