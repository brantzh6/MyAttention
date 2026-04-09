# IKE Runtime v0 Packet R1-C7 Coding Brief

## Task ID

`IKE-RUNTIME-R1-C7`

## Goal

Remove the deprecated `allow_claim` compatibility parameter from the runtime
transition surface now that `ClaimContext` and Postgres-backed verification are
in place.

## Why This Exists

Current truthful state:

- `allow_claim=True` no longer grants executable access
- `ClaimContext` is the real claim-required path
- keeping `allow_claim` in the function signature preserves an obsolete mental
  model and weakens the truth boundary

## Scope

Allowed:

- remove `allow_claim` from runtime/state-machine pure logic
- update direct downstream runtime call sites
- update tests that still mention deprecated compatibility semantics

Not allowed:

- broader runtime redesign
- API/UI expansion
- scheduler changes
- new object families

## Acceptance Standard

1. `allow_claim` is removed from the runtime transition signature
2. claim-required transitions still work through `claim_context`
3. legal claim path remains green
4. illegal claim path remains green
5. no unrelated runtime broadening
