# IKE Runtime v0 R1-C Follow-Up Plan

## Purpose

`R1-C` is now materially implemented and controller-validated as `accept_with_changes`.

Two narrow follow-ups have now been completed:

1. `R1-C5` wired `ClaimVerifier` to Postgres-backed truth
2. `R1-C6` restored DB-backed schema-foundation runtime truth

The remaining work is now a single deprecation/hardening item inside the same
truth-layer envelope:

1. remove the deprecated `allow_claim` compatibility parameter

## Remaining Substantive Gaps

### 1. Runtime-Owned Truth Is Now Narrowed To Surface Cleanup

Current truthful state:

- `ClaimContext` is now the only executable path for CLAIM_REQUIRED transitions
- `ClaimVerifier` now has a Postgres-backed implementation
- DB-backed schema-foundation truth is restored

Meaning:

- runtime truth is materially closed for the narrow claim path
- the remaining soft spot is that the old `allow_claim` compatibility parameter
  still survives in the pure-logic surface

## Follow-Up Packets

### R1-C7 Coding

Goal:

- remove the deprecated `allow_claim` compatibility parameter from the runtime
  transition surface

Boundaries:

- no scheduler expansion
- no new first-class runtime families
- no runtime UI/API work
- no graph memory

Success:

- `allow_claim` is gone from the runtime transition surface
- legal and illegal claim paths remain green through `claim_context`
- no truth-layer regression is introduced by removing the compatibility shim

## Not Yet

Do not treat these follow-ups as permission to open:

- `R1-D`
- benchmark/kernel integration
- notifications
- broader runtime APIs
- procedural-memory promotion states

Those remain later decisions.
