# IKE Runtime v0 - R2-G13 Controller Acceptability Result

Date: 2026-04-09
Phase: `R2-G Runtime Service Stability And Delegated Closure Hardening`
Focus: machine-readable controller acceptability for live proof

## Summary

`service_preflight` now produces a controller-facing acceptability judgment
separate from the lower-level service status.

This preserves the original runtime preflight contract:

- `ready`
- `ambiguous`
- `down`

while giving the controller a more useful interpretation layer.

## Files Changed

- [D:\code\MyAttention\services\api\runtime\service_preflight.py](/D:/code/MyAttention/services/api/runtime/service_preflight.py)
- [D:\code\MyAttention\services\api\routers\ike_v0.py](/D:/code/MyAttention/services/api/routers/ike_v0.py)
- [D:\code\MyAttention\services\api\tests\test_runtime_v0_service_preflight.py](/D:/code/MyAttention/services/api/tests/test_runtime_v0_service_preflight.py)
- [D:\code\MyAttention\services\api\tests\test_routers_ike_v0.py](/D:/code/MyAttention/services/api/tests/test_routers_ike_v0.py)
- [D:\code\MyAttention\services\web\components\settings\ike-workspace-manager.tsx](/D:/code/MyAttention/services/web/components/settings/ike-workspace-manager.tsx)

## What Landed

### 1. New machine-readable field

`run_preflight(...)` now records:

- `details.controller_acceptability`

Current values include:

- `canonical_ready`
- `bounded_live_proof_ready`
- `blocked_api_down`
- `blocked_port_ambiguity`
- `blocked_code_freshness`
- `blocked_owner_mismatch`
- `blocked_other`

### 2. Important semantic rule

The outer preflight `status` is **not** changed by this work.

This means:

- the system can still truthfully report `ambiguous`
- while also telling the controller:
  - this is acceptable for a bounded live proof

### 3. Route and panel surfacing

The inspect route now exposes:

- `data.controller_acceptability`

The settings runtime panel now surfaces:

- `Controller Acceptability`

## Validation

Passed:

```powershell
$env:PYTHONPATH='D:\code\MyAttention\services\api'; python -m pytest services/api/tests/test_routers_ike_v0.py services/api/tests/test_runtime_v0_service_preflight.py -q
```

Result:

- `76 passed, 28 warnings, 9 subtests passed`

Passed:

```powershell
python -m compileall D:\code\MyAttention\services\api\routers\ike_v0.py
```

Passed:

```powershell
npx tsc --noEmit
```

Current local helper snapshot on `8000`:

- `controller_acceptability.status = blocked_owner_mismatch`
- `controller_acceptability.acceptable = False`

## Truthful Judgment

- `R2-G13 = accept_with_changes`

## Why `accept_with_changes`

Accepted because:

- the controller now has a clear interpretation layer
- this does not distort the underlying preflight truth
- route and visible surface are aligned with the new field

Still `with_changes` because:

- the actual controller rule usage still needs one explicit narrow policy note
- current `8000` remains blocked at the acceptability layer
- launch-path discipline is still not normalized for the canonical service

## Controller Interpretation

`R2-G` is now ready to move from:

- observability hardening

to:

- explicit controller rule hardening

The next narrow question is:

- when should `bounded_live_proof_ready` be accepted
- and when should it still be rejected in practice
