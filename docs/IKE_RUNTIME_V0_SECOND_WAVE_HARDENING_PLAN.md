# IKE Runtime v0 Second-Wave Hardening Plan

## Purpose

This document defines the next runtime mainline after the first-wave
`R0-A ~ R0-F` packets completed with `accept_with_changes`.

It is not a broad new architecture branch.
It is the narrow hardening and integration phase that should happen before
larger runtime expansion.

## 1. Controller Judgment

Current judgment after the first-wave result review:

- direction is correct
- first-wave is good enough to continue
- second-wave must begin with hardening, not expansion

This means:

- do not jump to graph memory
- do not jump to scheduler platform work
- do not jump to broad UI/runtime surfaces
- do not treat first-wave as production-hardened

## 2. Core Review Consensus

Cross-review consensus from the current first-wave result reviews:

1. PostgreSQL as canonical truth remains correct
2. Redis as acceleration only remains correct
3. packet ordering was correct
4. the main remaining weakness is enforcement hardness, not direction
5. second-wave should start with a narrow hardening packet

## 3. Fix-Now Before Broader Second-Wave

These items are now the first second-wave priority.

### 3.1 Claim Semantics Hardening

Problem:

- `allow_claim` remains too caller-asserted

Required direction:

- move from caller-asserted claim permission toward object-backed or
  lease-backed validation

Reason:

- current semantics still rely too much on caller discipline

### 3.2 MemoryPacket Upstream Existence Verification

Problem:

- trusted recall currently depends on explicit linkage presence
- linkage presence alone is not strong enough

Required direction:

- verify upstream object existence, not only linkage fields

Reason:

- fake linkage must not pass the trust boundary

### 3.3 R0-A Migration Validation Hardening

Problem:

- runtime schema foundation still lacks controller-side automated migration
  verification

Required direction:

- add explicit upgrade/downgrade verification
- move toward pytest-backed migration proof when environment allows

Reason:

- runtime kernel cannot rely on unproven migration safety

### 3.4 Force-Path Restriction

Problem:

- `force=True` remains a misuse risk

Required direction:

- restrict force-paths to controller/runtime roles only

Reason:

- delegates should not bypass core transition rules

### 3.5 Unified Hardening Backlog

Problem:

- retained notes and residual `accept_with_changes` items can become diffuse

Required direction:

- unify first-wave retained hardening items under one active second-wave packet

Reason:

- hardening work should be visible and ordered, not scattered across review files

## 4. Validation and Evolution Requirements

Second-wave must explicitly use the newly formalized independent legs:

- testing leg
- evolution leg

This means:

### Testing

At least one explicit hardening packet must require:

- independent validation ownership
- regression checks for first-wave corrected semantics
- trust-boundary tests
- migration/recovery checks where applicable

Reference:

- [D:\code\MyAttention\docs\PROJECT_TEST_AGENT_AND_VALIDATION_MATRIX.md](/D:/code/MyAttention/docs/PROJECT_TEST_AGENT_AND_VALIDATION_MATRIX.md)

### Evolution

Second-wave must also produce:

- explicit `now_to_absorb`
- explicit `future_to_preserve`
- durable method updates if hardening reveals reusable rules

Reference:

- [D:\code\MyAttention\docs\PROJECT_EVOLUTION_LOOP_AND_METHOD_UPGRADE.md](/D:/code/MyAttention/docs/PROJECT_EVOLUTION_LOOP_AND_METHOD_UPGRADE.md)

## 5. Proposed Second-Wave Shape

### R1-A Hardening Pack

Purpose:

- absorb the fix-now items from first-wave review

Scope:

- claim semantics hardening
- upstream existence verification
- force-path restriction
- migration validation hardening
- retained-note consolidation

This is the highest-priority next packet group.

### R1-B First Real Task Lifecycle

Purpose:

- prove one real task end-to-end lifecycle through the runtime kernel

Tentative shape:

- `inbox -> ready -> active -> review_pending -> done`

Reason:

- first-wave proves kernel components
- second-wave should begin proving real lifecycle behavior

### R1-C Narrow Kernel Integration

Purpose:

- connect the runtime kernel to one narrow existing benchmark or observation path

Reason:

- prove the kernel is not isolated designware

## 6. Not Yet

Second-wave should not yet include:

- graph memory
- broad semantic retrieval
- notification mesh
- wide scheduler platform
- broad runtime UI
- major new first-class runtime objects

## 7. Success Standard

Second-wave is successful if:

1. first-wave residual risks are reduced by stronger enforcement
2. testing is explicit, not implied
3. evolution absorption is durable, not chat-only
4. one real task lifecycle is proven through the kernel
5. runtime remains narrow and truthful
