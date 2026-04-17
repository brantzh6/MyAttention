# IKE Runtime v0 - R2-I13 Result Milestone

Date: 2026-04-10
Phase: `R2-I13 Live Route Freshness Closure`
Status: `completed`

## Scope

Close the newly observed gap between:

- code/test evidence for the DB-backed inspect route
- canonical live-service route availability on `127.0.0.1:8000`

This packet was operationally narrow.
It did not introduce new runtime semantics.

## What Was Proven

After a controlled canonical-service refresh, the live canonical service now
exposes:

- `POST /api/ike/v0/runtime/task-lifecycle/db-proof/inspect`

The route is now visible in the live OpenAPI surface and returns a successful
bounded DB-backed proof payload.

## Live Evidence

### 1. Live OpenAPI Route Presence

Confirmed present on canonical `8000`:

- `/api/ike/v0/runtime/service-preflight/inspect`
- `/api/ike/v0/runtime/task-lifecycle/proof/inspect`
- `/api/ike/v0/runtime/task-lifecycle/db-proof/inspect`

### 2. Live DB-Backed Inspect Call

Observed successful live result:

- `summary.success = true`
- `summary.final_status = done`
- `summary.persisted_event_count = 6`
- `truth_boundary.inspect_only = true`
- `truth_boundary.bounded_db_proof = true`
- `truth_boundary.persists_runtime_state = true`
- `truth_boundary.implies_general_task_runner = false`
- `truth_boundary.detached_execution = false`

### 3. Canonical Service Preflight After Refresh

The live route freshness gap is now closed, but there is still an important
split between:

- default preflight requests
- code-freshness-checked preflight requests

Observed truthful behavior:

Default request body `{}`:

- `code_freshness.status = unchecked`
- `controller_acceptability.status = blocked_owner_mismatch`
- `controller_promotion.status = not_promotable`

Request body with current expected fingerprint:

- `expected_code_fingerprint = 09bc108230eed093`
- `strict_code_freshness = true`

returns:

- `code_freshness.status = match`
- `controller_acceptability.status = acceptable_windows_venv_redirector`
- `controller_promotion.status = controller_confirmation_required`

So `R2-I13` closes live route freshness, but it does not yet close the gap
between:

- default controller-visible preflight semantics
- strict code-freshness-confirmed promotion semantics

## Mainline Meaning

The runtime mainline no longer has to infer DB-backed inspect freshness from:

- source code
- focused tests
- local file timestamps

It now has one real canonical-service proof that the route is live.

That also does not eliminate the remaining controller-experience gap:

- the reviewed Windows redirector acceptability path exists
- but it currently requires the caller to supply the expected fingerprint
  explicitly

## Validation

Live checks run:

```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/health'
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/openapi.json'
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/ike/v0/runtime/task-lifecycle/db-proof/inspect' -Method Post -ContentType 'application/json' -Body '{}'
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/ike/v0/runtime/service-preflight/inspect' -Method Post -ContentType 'application/json' -Body '{}'
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/ike/v0/runtime/service-preflight/inspect' -Method Post -ContentType 'application/json' -Body '{"expected_code_fingerprint":"09bc108230eed093","strict_code_freshness":true}'
```

Focused code validation already remained green in this same mainline slice:

```powershell
python -m pytest tests/test_runtime_v0_db_backed_lifecycle_proof.py tests/test_routers_ike_v0.py tests/test_runtime_v0_project_surface.py -q
python -m compileall runtime routers tests
```

Observed result:

- live canonical route now present and callable
- `49 passed, 28 warnings, 9 subtests passed`
- compile passed

## Controller Judgment

- `R2-I13 = accept_with_changes`

## Remaining Gaps

This still does not prove:

1. default preflight requests can self-close the code-freshness requirement
2. automatic controller promotion
3. detached runtime supervision
4. scheduler semantics
