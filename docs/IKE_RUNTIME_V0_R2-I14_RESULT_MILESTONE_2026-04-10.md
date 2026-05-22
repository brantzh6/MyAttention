# IKE Runtime v0 - R2-I14 Result Milestone

Date: 2026-04-10
Phase: `R2-I14 Promotion Readiness Self-Check`
Status: `completed`

## Scope

Close one narrow controller-facing gap in runtime preflight:

- default live preflight left `code_freshness = unchecked`
- the reviewed Windows redirector acceptability path therefore required manual
  fingerprint copy/paste

This packet adds one explicit self-check path without adding automatic
promotion.

## Implemented

- extended the service-preflight helper with one explicit self-check option in:
  - [D:\code\MyAttention\services\api\runtime\service_preflight.py](/D:/code/MyAttention/services/api/runtime/service_preflight.py)
- extended the controller-facing preflight route request model in:
  - [D:\code\MyAttention\services\api\routers\ike_v0.py](/D:/code/MyAttention/services/api/routers/ike_v0.py)
- added focused helper and route coverage in:
  - [D:\code\MyAttention\services\api\tests\test_runtime_v0_service_preflight.py](/D:/code/MyAttention/services/api/tests/test_runtime_v0_service_preflight.py)
  - [D:\code\MyAttention\services\api\tests\test_routers_ike_v0.py](/D:/code/MyAttention/services/api/tests/test_routers_ike_v0.py)

## What Changed

New bounded request behavior:

- `self_check_current_code = true`

Meaning:

- if the caller does not supply `expected_code_fingerprint`
- the helper may derive the current file-tree fingerprint locally
- then use that derived value as the comparison basis for code freshness

This does not:

- auto-promote the service
- collapse the Windows redirector path into `canonical_ready`
- remove the controller confirmation requirement

## What The New Tests Prove

The new focused tests now prove:

1. route-level request forwarding includes `self_check_current_code`
2. helper-level self-check can close `unchecked -> match` for the current local
   file tree
3. on Windows redirector shape, self-check can truthfully produce:
   - `controller_acceptability = acceptable_windows_venv_redirector`
   - `controller_promotion = controller_confirmation_required`

## Live Canonical-Service Evidence

After controlled refresh on canonical `127.0.0.1:8000`, live request:

```json
{
  "self_check_current_code": true,
  "strict_code_freshness": true
}
```

returned:

- `code_freshness.status = match`
- `controller_acceptability.status = acceptable_windows_venv_redirector`
- `controller_promotion.status = controller_confirmation_required`
- `controller_promotion.eligible = true`
- `controller_promotion.target_status = canonical_accepted`

Current observed live fingerprint at proof time:

- `f0ce7260f201ae85`

## Mainline Meaning

The runtime mainline now has a truthful controller-facing self-check path for
canonical local preflight:

- no manual fingerprint copy/paste is required
- reviewed Windows redirector semantics remain intact
- controller confirmation is still explicitly required

This is a controller-usability hardening step, not an automatic acceptance
step.

## Validation

Focused validation:

```powershell
python -m pytest tests/test_runtime_v0_service_preflight.py tests/test_routers_ike_v0.py -q
python -m compileall runtime routers tests
```

Observed result:

- `89 passed, 28 warnings, 9 subtests passed`
- compile passed

Live validation:

```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/health'
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/ike/v0/runtime/service-preflight/inspect' -Method Post -ContentType 'application/json' -Body '{"self_check_current_code":true,"strict_code_freshness":true}'
```

Observed result:

- live canonical service healthy
- live self-check path returns `acceptable_windows_venv_redirector`
- live self-check path returns `controller_confirmation_required`

## Controller Judgment

- `R2-I14 = accept`

## Remaining Gaps

This still does not prove:

1. automatic controller promotion mutation
2. full canonical owner equality on Windows
3. detached supervision
4. scheduler semantics
