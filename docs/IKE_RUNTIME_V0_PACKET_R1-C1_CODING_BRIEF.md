# IKE Runtime v0 Packet R1-C1 Coding Brief

## Task ID

- `R1-C1`

## Goal

Harden the runtime truth layer so the lifecycle proof path no longer relies on
legacy executable `allow_claim=True`.

## Scope

Allowed focus:

- runtime claim-required transition path
- runtime-owned delegate identity / assignment / lease verification adapter
- narrow lifecycle-proof support updates
- narrow tests required by this hardening

Do not:

- redesign task state model
- add scheduler/platform work
- add UI/API surfaces
- add new first-class runtime object families

## Required outcome

After this packet:

- lifecycle proof path should not depend on raw `allow_claim=True`
- runtime should own the truth rule for whether a delegate can claim/continue
  work in the proof path
- tests should prove both success and rejection paths

## Validation

At minimum:

- runtime lifecycle proof tests
- task state semantics tests
- events/leases tests

## Stop Conditions

Stop and return boundedly if:

- removing legacy `allow_claim=True` requires broad scheduler redesign
- the packet would need new major runtime objects
- the change would broaden beyond truth-layer hardening
