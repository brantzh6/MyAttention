# IKE Runtime v0 Packet R1-C5 Coding Brief

## Task ID

`IKE-RUNTIME-R1-C5`

## Goal

Wire `ClaimVerifier` to Postgres-backed runtime truth for the narrow delegate-claim path.

## Why This Exists

`R1-C1` closed executable `allow_claim=True` access and introduced a verifier boundary.

What still remains soft:

- verifier is only an adapter
- no runtime/service implementation verifies:
  - delegate identity
  - assignment linkage
  - active lease linkage

## Current Controller Constraint

For `v0`, explicit assignment truth is fixed to:

- `runtime_tasks.owner_kind/owner_id`

Do not broaden this packet into:

- event-sourced assignment reconstruction
- a new assignment table/object family

See:

- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-C5_ASSIGNMENT_TRUTH_OPTIONS.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-C5_ASSIGNMENT_TRUTH_OPTIONS.md)

## Scope

Allowed:

- narrow runtime/service-layer implementation for Postgres-backed claim verification
- narrow tests for legal/illegal delegate claim paths using the real verifier path

Not allowed:

- scheduler/platform redesign
- new first-class runtime object families
- runtime UI/API expansion
- graph memory
- broad runtime repository refactor

## Acceptance Standard

1. `ClaimVerifier` is wired to runtime-owned truth
2. legal delegate claim path succeeds via real verification
3. illegal delegate claim path fails via real verification
4. review boundary remains intact
5. no broadening beyond claim verification path
