# IKE Runtime v0 R2-G2 Result Milestone

## Scope

`R2-G2 = Service Preflight Helper`

This is a narrow operational hardening slice for live-proof discipline.

It does not change runtime truth semantics.

## What Is Now Real

- runtime service preflight helper exists at:
  - [D:\code\MyAttention\services\api\runtime\service_preflight.py](/D:/code/MyAttention/services/api/runtime/service_preflight.py)
- test coverage exists at:
  - [D:\code\MyAttention\services\api\tests\test_runtime_v0_service_preflight.py](/D:/code/MyAttention/services/api/tests/test_runtime_v0_service_preflight.py)
- the helper can now produce machine-readable status:
  - `ready`
  - `ambiguous`
  - `down`

## Controller Validation

- `python -m pytest services/api/tests/test_runtime_v0_service_preflight.py -q`
  - `39 passed, 1 warning`
- `python -m compileall D:\code\MyAttention\services\api\runtime\service_preflight.py`
  - passed
- live health:
  - `GET http://127.0.0.1:8000/health`
  - returned `200`
- live preflight snapshot:
  - current status: `ready`
  - current live owner count: `1`
  - current listener process:
    - system `Python312` `python.exe`
  - current preferred-owner evaluation:
    - `preferred_mismatch`
- live route proof:
  - router tests are green
  - stale `8000` process did not immediately reflect the new route during direct validation
  - a fresh repo `.venv` `uvicorn` instance on `8011` successfully returned:
    - `POST /api/ike/v0/runtime/service-preflight/inspect` -> `200`

## Truthful Interpretation

`R2-G2` proves that the controller now has a narrow, machine-readable way to
check whether live proof is safe to proceed.

It does **not** prove that local API launch discipline is fully normalized.

Current live preflight says the surface is `ready`, but the observed process
owner is still the system Python launcher rather than the repo `.venv` path
that the controller prefers as the long-term truthful baseline.

The live route itself is now proven, but only under a fresh repo-owned runtime
instance on `8011`. That means the remaining blocker is stale service ownership,
not route semantics.

The service preflight helper now makes that mismatch machine-readable through
`details.preferred_owner`, so controller logic no longer has to infer it by
manually reading process command lines.

## Result

`R2-G2 = accept_with_changes`

## Remaining Gap

- live proof readiness can now be checked truthfully
- but service ownership policy is still not enforced
- repo `.venv` ownership is still a preferred baseline, not a guaranteed fact
