# IKE Runtime v0 - R2-G10 Targeted Preflight Result

Date: 2026-04-09
Phase: `R2-G Runtime Service Stability And Delegated Closure Hardening`
Packet: targeted service-preflight inspect for alternate live-proof ports

## Summary

The runtime service-preflight inspect route can now target an explicit
`host/port` pair instead of always inspecting the default `8000` service.

This is a narrow operational hardening step for controller live proof.

It does **not**:
- create a supervisor
- normalize service ownership
- guarantee that a fresh alternate-port service will launch cleanly
- widen into a general service-management API

## Files Changed

- [D:\code\MyAttention\services\api\routers\ike_v0.py](/D:/code/MyAttention/services/api/routers/ike_v0.py)
- [D:\code\MyAttention\services\api\tests\test_routers_ike_v0.py](/D:/code/MyAttention/services/api/tests/test_routers_ike_v0.py)

## What Landed

`POST /api/ike/v0/runtime/service-preflight/inspect` now accepts:
- `host`
- `port`
- `strict_preferred_owner`
- `expected_code_fingerprint`
- `strict_code_freshness`

This lets the controller inspect:
- the default `8000` service
- or a fresh alternate-port service such as `8011`

without changing the underlying preflight truth model.

## Validation

Passed:

```powershell
$env:PYTHONPATH='D:\code\MyAttention\services\api'; python -m pytest services/api/tests/test_runtime_v0_service_preflight.py services/api/tests/test_routers_ike_v0.py -q
```

Result:
- `72 passed, 28 warnings, 9 subtests passed`

Passed:

```powershell
python -m compileall D:\code\MyAttention\services\api\routers\ike_v0.py
```

## Operational Evidence

### Fresh route targeting support is real

The route contract is now test-proven for:
- explicit `host`
- explicit `port`

### Fresh live proof is still blocked by launch-path discipline

Controller attempted a repo `.venv` alternate-port live proof on `8011`.

Observed truth:
- the temporary `8011` service launched with:
  - repo `.venv` parent
  - system `Python312` child
- live route behavior on that service still reflected stale pre-hardening
  semantics
- the temporary `8011` service was cleaned up after the attempt

This means:
- targeted preflight inspect is ready
- but alternate-port fresh-code live proof is still blocked by the same launch /
  ownership chain problem already seen on `8000`

## Truthful Judgment

- `R2-G10 = accept_with_changes`

## Why `accept_with_changes`

Accepted because:
- controller can now inspect explicit alternate live-proof targets
- the route contract is no longer hardcoded to `8000`
- the change is test-backed and bounded

Still `with_changes` because:
- fresh alternate-port live proof is still not normalized
- repo `.venv` launch can still drift into a system-Python child
- code freshness on live alternate-port services is therefore still not fully
  trustworthy

## Controller Interpretation

The remaining `R2-G` blocker is now narrower and clearer:

- not lack of preflight observability
- not lack of route targeting
- but **launch-path discipline / served-code freshness normalization**

That should remain the next operational target before claiming stable unattended
live-proof conditions.
