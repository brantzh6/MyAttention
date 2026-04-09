# IKE Runtime v0 R2-G8 Live Route Stale-Code Note

## Scope

Record one truthful operational constraint discovered during `R2-G`.

This is not a new feature.

## Current Evidence

The local helper and test surfaces now include:
- `details.preferred_owner`
- `details.owner_chain`

Controller validation already proved:
- strict helper snapshot on `8000` returns:
  - `preferred_owner.status = preferred_mismatch`
  - `owner_chain.status = parent_preferred_child_mismatch`

However, the live `8000` route:
- `POST /api/ike/v0/runtime/service-preflight/inspect`

currently still returns:
- `preferred_owner`
- but not `owner_chain`

## Truthful Interpretation

This means the current `8000` listener is serving a stale code path relative to
the latest workspace state.

So for the newest `service_preflight` fields:
- local targeted tests
- compile checks
- direct helper invocation

are currently stronger evidence than the live `8000` route response.

## Result

Current truthful controller interpretation:

- route semantics are materially real
- current `8000` health is real
- but current `8000` code freshness is still not normalized

## Follow-Up Pressure

Do not over-claim that the active `8000` route reflects the latest workspace
runtime code until service ownership/code freshness is normalized.
