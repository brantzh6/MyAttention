# IKE Runtime v0 R1-C Result Milestone

## Purpose

This milestone records the truthful current status of `R1-C` truth-layer integration.

`R1-C` was opened to absorb the remaining substantive soft spots exposed after
`R1-B` lifecycle proof:

1. remove executable dependence on legacy `allow_claim=True`
2. move delegate-claim truth toward a runtime-owned verification boundary
3. convert lifecycle-proof learnings into durable method rules

## Current Status

Current controller judgment: `accept_with_changes`

Phase legs now have durable outputs:

- coding:
  - [D:\code\MyAttention\.runtime\delegation\results\ike-runtime-r1-c1-truth-layer-coding-glm.json](/D:/code/MyAttention/.runtime/delegation/results/ike-runtime-r1-c1-truth-layer-coding-glm.json)
- review:
  - [D:\code\MyAttention\.runtime\delegation\results\ike-runtime-r1-c2-truth-layer-review-kimi.json](/D:/code/MyAttention/.runtime/delegation/results/ike-runtime-r1-c2-truth-layer-review-kimi.json)
- testing:
  - [D:\code\MyAttention\.runtime\delegation\results\ike-runtime-r1-c3-truth-layer-test.json](/D:/code/MyAttention/.runtime/delegation/results/ike-runtime-r1-c3-truth-layer-test.json)
- evolution:
  - [D:\code\MyAttention\.runtime\delegation\results\ike-runtime-r1-c4-truth-layer-evolution-kimi.json](/D:/code/MyAttention/.runtime/delegation/results/ike-runtime-r1-c4-truth-layer-evolution-kimi.json)

## What Is Now True

- executable `allow_claim=True` access is closed for CLAIM_REQUIRED transitions
- `TransitionRequest` now carries `claim_context`
- runtime now contains a `ClaimVerifier` adapter boundary and `InMemoryClaimVerifier`
- runtime now also contains a narrow Postgres-backed verifier implementation:
  - [D:\code\MyAttention\services\api\runtime\postgres_claim_verifier.py](/D:/code/MyAttention/services/api/runtime/postgres_claim_verifier.py)
- deprecated `allow_claim` compatibility surface has now been removed from the
  pure runtime transition validator
- claim-required runtime suites remain green after `allow_claim` removal:
  - `194 passed, 1 warning`
- `R1-C6` DB-backed schema-foundation suite is green:
  - `53 passed, 1 warning`
- `R1-C5` targeted Postgres-backed claim-verifier suite is green:
  - `4 passed, 1 warning`
- combined narrow DB-backed runtime evidence is green:
  - `57 passed, 1 warning`
- `EXPLICIT_ASSIGNMENT` now uses the accepted v0 durable truth:
  - `runtime_tasks.owner_kind/owner_id`
- `ACTIVE_LEASE` verification now uses runtime-owned DB truth:
  - `runtime_tasks.current_lease_id`
  - `runtime_worker_leases`
- narrow runtime validation passed:
  - `256 passed`
  - state machine
  - task state semantics
  - events and leases
  - lifecycle proof
- method absorption is now clearer:
  - narrow semantic validation and wider environment-coupled validation must be recorded separately
  - fixture/environment failures should be treated as testing-lane gaps, not silent semantic regressions

## What Is Not Yet True

- wide DB-backed runtime sweeps beyond the current narrow acceptance subset have
  not yet been rerun as a larger packet

## Transport Truth

Review/evolution output recovery improved, but the outer OpenClaw shell still
timed out while the result payloads were being written.

Interpretation:

- this is no longer the main semantic blocker for `R1-C`
- but it remains an execution-lane reliability issue worth preserving

## Recommended Next Step

Do not reopen broader runtime design from inside `R1-C`.

Treat `R1-C` as materially complete and open the next runtime phase judgment
from this stabilized truth-layer baseline.
