# IKE Runtime v0 R1-C7 Allow-Claim Removal Plan

## Purpose

`R1-C5` and `R1-C6` are now materially complete.

The remaining `R1-C` hardening item is narrower than a new phase:

- remove the deprecated `allow_claim` compatibility parameter from the
  pure-logic/runtime call surface once real claim truth is already in place

## Why This Is The Next Narrow Step

What is already true:

- `ClaimContext` is the only executable path for CLAIM_REQUIRED transitions
- Postgres-backed claim verification now exists
- DB-backed schema-foundation truth is restored

What is still soft:

- `runtime.state_machine.validate_transition(...)` still accepts
  `allow_claim` as a deprecated no-op compatibility argument
- this keeps an obsolete mental model alive in the API surface even though it
  no longer grants access

## Scope

Allowed:

- remove `allow_claim` from the pure-logic/runtime call surface
- update downstream runtime call sites and tests that still mention it as a
  compatibility parameter
- keep the packet narrow to runtime logic/tests/docs directly touched by the
  old compatibility surface

Not allowed:

- broader runtime API redesign
- scheduler/platform changes
- new runtime object families
- UI/API expansion

## Acceptance Standard

1. `allow_claim` no longer exists as a runtime transition parameter
2. all remaining claim-required paths use `claim_context`
3. tests no longer rely on deprecated compatibility semantics
4. no legal claim path regresses
5. no broadening beyond deprecation removal

## Output

This plan should materialize into the next narrow packet:

- `R1-C7` coding
- plus the usual review/test/evolution follow-through if execution proceeds
