# IKE Runtime v0 - R2-I13 Phase Judgment

Date: 2026-04-10
Phase: `R2-I13 Live Route Freshness Closure`
Status: `candidate next packet inside R2-I`

## Why This Packet Exists

After `R2-I12` review absorption, the next runtime uncertainty is no longer:

- helper semantics
- route-shape semantics
- reviewability of the failure-honesty packet

The new narrow uncertainty is live canonical-service freshness.

Current observed fact chain:

1. the current code tree contains:
   - `POST /api/ike/v0/runtime/task-lifecycle/db-proof/inspect`
2. focused tests for that route pass locally
3. canonical `127.0.0.1:8000` health is currently healthy
4. canonical runtime service preflight still reports a live service on `8000`
5. but the live service returns `404 Not Found` for the DB-backed inspect route

That means the mainline now has a real gap between:

- code-tree/runtime-proof evidence
- live canonical service surface

## Intended Scope

If opened, `R2-I13` should close this gap in the narrowest possible way.

Acceptable packet shape:

1. either prove that the canonical service now exposes the DB-backed inspect
   route live
2. or make the mismatch machine-readable enough that controller review is not
   misled by file-tree freshness alone

## Explicit Non-Goals

- no broad service manager
- no new daemon framework
- no scheduler semantics
- no broad deployment pipeline work

## Controller Judgment

`R2-I13` is the correct next packet if the current goal is to ensure that the
runtime mainline is not over-claiming live canonical-service readiness from
code/test evidence alone.
