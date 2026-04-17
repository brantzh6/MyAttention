# IKE Runtime v0 - R2-H6 Controller Promotion Readiness Result

Date: 2026-04-10
Phase: `R2-H Canonical Service Launch Path Normalization`
Packet: `R2-H6 Controller Promotion Readiness`

## Scope

Make the controller-facing promotion path explicit after `R2-H5`.

This packet does not add a mutating controller API.
It only makes the promotion semantics machine-readable in the existing
service-preflight inspect surface.

## Implemented

- added controller promotion readiness evaluation in:
  - [D:\code\MyAttention\services\api\runtime\service_preflight.py](/D:/code/MyAttention/services/api/runtime/service_preflight.py)
- exposed the new field in the runtime preflight inspect response:
  - [D:\code\MyAttention\services\api\routers\ike_v0.py](/D:/code/MyAttention/services/api/routers/ike_v0.py)
- added focused tests in:
  - [D:\code\MyAttention\services\api\tests\test_runtime_v0_service_preflight.py](/D:/code/MyAttention/services/api/tests/test_runtime_v0_service_preflight.py)
  - [D:\code\MyAttention\services\api\tests\test_routers_ike_v0.py](/D:/code/MyAttention/services/api/tests/test_routers_ike_v0.py)

## New Preflight Field

The inspect payload now exposes:

- `controller_promotion`

This field is derived from `controller_acceptability`, but it answers a
different question:

- `controller_acceptability`
  - is this live shape acceptable for controller review?
- `controller_promotion`
  - can the controller promote this shape to `canonical_accepted` now, and if
    so under what confirmation rule?

## Current Promotion Rules

### 1. Direct canonical owner match

If:

- `controller_acceptability.status = canonical_ready`

Then:

- `controller_promotion.status = controller_can_promote_now`
- `eligible = true`
- `target_status = canonical_accepted`
- `controller_confirmation_required = false`
- `basis = direct_canonical_owner_match`

### 2. Windows venv redirector exception

If:

- `controller_acceptability.status = acceptable_windows_venv_redirector`

Then:

- `controller_promotion.status = controller_confirmation_required`
- `eligible = true`
- `target_status = canonical_accepted`
- `controller_confirmation_required = true`
- `basis = windows_venv_redirector_v1`

### 3. All blocked states

If controller acceptability is blocked, then:

- `controller_promotion.status = not_promotable`
- `eligible = false`

## Truth Boundary

This packet still does **not**:

- auto-upgrade any live service to `canonical_accepted`
- create a write-path or mutable controller action
- broaden the Windows exception beyond the reviewed narrow rule

It only makes the promotion step explicit and auditable in the inspect output.

## Validation

Commands run:

```powershell
$env:PYTHONPATH='D:\code\MyAttention\services\api'; python -m pytest services/api/tests/test_runtime_v0_service_preflight.py -q
$env:PYTHONPATH='D:\code\MyAttention\services\api'; python -m pytest services/api/tests/test_routers_ike_v0.py -q
python -m compileall D:\code\MyAttention\services\api\runtime\service_preflight.py D:\code\MyAttention\services\api\routers\ike_v0.py D:\code\MyAttention\services\api\tests\test_runtime_v0_service_preflight.py D:\code\MyAttention\services\api\tests\test_routers_ike_v0.py
```

Observed results:

- `53 passed, 1 warning`
- `29 passed, 28 warnings, 9 subtests passed`
- compile passed

## Controller Judgment

- `R2-H6 = accept_with_changes`

## Why Accept With Changes

This closes the semantic gap left by `R2-H5`, but two narrow follow-ups remain:

1. a later controller-facing action or procedure may still be needed if the
   project wants promotion to be explicitly recorded rather than only inspected
2. canonical service proof still depends on the live environment actually
   producing one reviewed promotable shape on demand
