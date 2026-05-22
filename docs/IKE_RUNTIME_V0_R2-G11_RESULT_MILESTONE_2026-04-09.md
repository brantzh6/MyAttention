# IKE Runtime v0 - R2-G11 Result Milestone

Date: 2026-04-09
Phase: `R2-G Runtime Service Stability And Delegated Closure Hardening`
Focus: launch-path discipline and fresh-code live proof

## Summary

`R2-G11` proved a truthful fresh alternate-port live route can now expose the
latest `service_preflight` fields, including:

- `preferred_owner`
- `owner_chain`
- `code_fingerprint`
- `code_freshness`

This means the remaining live-proof ambiguity is no longer code freshness.

It is now narrower:

- listener owner is still system `Python312`
- owner chain is still `parent_preferred_child_mismatch`

## Files Changed

No additional source patch was required beyond the already-landed `R2-G9` and
`R2-G10` work.

This milestone is based on live operational proof against a fresh alternate-port
service.

## Live Proof

Fresh alternate-port service used:

- `127.0.0.1:8013`

Launch path used:

- repo `.venv`
- `uvicorn.exe`
- working directory:
  - `D:\code\MyAttention\services\api`

Observed process truth:

- listener process:
  - system `Python312`
- parent process:
  - repo `.venv` Python
- owner-chain status:
  - `parent_preferred_child_mismatch`

## Proof 1: latest fields are live-visible

Controller called:

```powershell
POST http://127.0.0.1:8013/api/ike/v0/runtime/service-preflight/inspect
```

with:

- `host = 127.0.0.1`
- `port = 8013`
- `strict_preferred_owner = true`
- `expected_code_fingerprint = 2c1cb7cf783aa7b4`
- `strict_code_freshness = true`

Result:

- route returned latest fields
- `owner_chain` was present
- `code_fingerprint` was present
- `code_freshness.status = mismatch`

This proved:

- the live route on the fresh service was no longer stale relative to the latest
  workspace schema

## Proof 2: code freshness can close independently

Controller repeated the same route call using the fresh returned fingerprint:

- `expected_code_fingerprint = d228e4a7cc94ba1f`

Result:

- `code_freshness.status = match`
- overall status still `ambiguous`

This proved:

- current ambiguity is no longer caused by served-code drift
- it is now caused by owner mismatch / launch-path discipline

## Truthful Judgment

- `R2-G11 = accept_with_changes`

## Why `accept_with_changes`

Accepted because:

- fresh alternate-port live proof is now real
- latest preflight fields are now confirmed live-visible on a fresh service
- code freshness can now be confirmed live and independently

Still `with_changes` because:

- preferred-owner mismatch remains
- current owner chain still resolves to:
  - `parent_preferred_child_mismatch`
- launch-path discipline is still not normalized enough to call live proof
  fully stable

## Controller Interpretation

`R2-G` has now advanced from:

- stale live route uncertainty

to:

- live route freshness proven
- remaining ambiguity isolated to launch-path / interpreter ownership

That is a materially narrower blocker.
