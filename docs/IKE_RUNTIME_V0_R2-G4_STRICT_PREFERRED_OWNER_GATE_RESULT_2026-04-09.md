# IKE Runtime v0 R2-G4 Strict Preferred-Owner Gate Result

## Scope

`R2-G4 = strict preferred-owner gate for service preflight`

This is a narrow operational hardening slice.

It does not:
- redesign runtime truth
- introduce a service supervisor
- auto-kill stale processes
- widen runtime/API scope beyond service-preflight inspection

## What Is Now Real

- `service_preflight` now supports:
  - `strict_preferred_owner=False` as the current default
  - `strict_preferred_owner=True` as an explicit controller gate
- when strict mode is enabled:
  - healthy API + single listener is no longer enough for `ready`
  - current owner must also match the preferred repo-owned baseline
- the inspect route now accepts:
  - `{"strict_preferred_owner": true}`

## Code

- helper:
  - [D:\code\MyAttention\services\api\runtime\service_preflight.py](/D:/code/MyAttention/services/api/runtime/service_preflight.py)
- router:
  - [D:\code\MyAttention\services\api\routers\ike_v0.py](/D:/code/MyAttention/services/api/routers/ike_v0.py)
- tests:
  - [D:\code\MyAttention\services\api\tests\test_runtime_v0_service_preflight.py](/D:/code/MyAttention/services/api/tests/test_runtime_v0_service_preflight.py)
  - [D:\code\MyAttention\services\api\tests\test_routers_ike_v0.py](/D:/code/MyAttention/services/api/tests/test_routers_ike_v0.py)

## Controller Validation

- `PYTHONPATH=D:\code\MyAttention\services\api python -m pytest services/api/tests/test_runtime_v0_service_preflight.py services/api/tests/test_routers_ike_v0.py -q`
  - `67 passed, 28 warnings, 9 subtests passed`
- `python -m compileall D:\code\MyAttention\services\api\runtime\service_preflight.py D:\code\MyAttention\services\api\routers\ike_v0.py`
  - passed
- live helper snapshot:
  - `run_preflight_sync(port=8000, strict_preferred_owner=True)`
  - returned:
    - `status = ambiguous`
    - `details.preferred_owner.status = preferred_mismatch`
    - `details.strict_preferred_owner = true`

## Truthful Interpretation

This does not fix stale service ownership.

It does fix a controller-truth problem:
- previously, current `8000` could still report `ready` while being owned by
  the non-preferred system Python process
- now the controller has an explicit strict mode that truthfully refuses to
  treat that state as ready

This means:
- route semantics and machine-readable preflight already exist
- stale ownership is still an operational gap
- but current mismatch is no longer silently misclassified as safe

## Result

`R2-G4 = accept_with_changes`

## Remaining Gap

- stale service ownership still exists
- strict mode surfaces the mismatch; it does not resolve it
- detached Claude completion remains a separate active hardening gap
