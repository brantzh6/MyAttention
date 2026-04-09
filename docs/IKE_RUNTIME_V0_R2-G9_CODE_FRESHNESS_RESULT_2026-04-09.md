# IKE Runtime v0 - R2-G9 Code Freshness Result

Date: 2026-04-09
Phase: `R2-G Runtime Service Stability And Delegated Closure Hardening`
Packet: narrow service-preflight code-freshness surfacing

## Summary

`service_preflight` now exposes a machine-readable code fingerprint and optional
code-freshness judgment, and the existing runtime settings panel can surface the
current `code_freshness` status without widening into a deployment system.

This is a narrow operational hardening step only.

It does **not**:
- normalize service ownership
- guarantee live `8000` is serving latest code
- introduce a service supervisor
- redefine runtime truth semantics

## Files Changed

- [D:\code\MyAttention\services\api\runtime\service_preflight.py](/D:/code/MyAttention/services/api/runtime/service_preflight.py)
- [D:\code\MyAttention\services\api\routers\ike_v0.py](/D:/code/MyAttention/services/api/routers/ike_v0.py)
- [D:\code\MyAttention\services\api\tests\test_runtime_v0_service_preflight.py](/D:/code/MyAttention/services/api/tests/test_runtime_v0_service_preflight.py)
- [D:\code\MyAttention\services\api\tests\test_routers_ike_v0.py](/D:/code/MyAttention/services/api/tests/test_routers_ike_v0.py)
- [D:\code\MyAttention\services\web\components\settings\ike-workspace-manager.tsx](/D:/code/MyAttention/services/web/components/settings/ike-workspace-manager.tsx)

## What Landed

### 1. Machine-readable code fingerprint

`run_preflight(...)` now records:
- `details.code_fingerprint`

Current shape:
- `status`
- `scope`
- `fingerprint`
- `sources`
- `source_count`

The fingerprint is derived from the current workspace copies of:
- `runtime/service_preflight.py`
- `routers/ike_v0.py`

### 2. Optional code-freshness evaluation

`run_preflight(...)` now accepts:
- `expected_code_fingerprint`
- `strict_code_freshness`

And records:
- `details.code_freshness`
- `details.strict_code_freshness`

Current `code_freshness.status` values:
- `unchecked`
- `match`
- `mismatch`
- `unavailable`

If `strict_code_freshness=True`, a fingerprint mismatch now truthfully forces:
- `status = ambiguous`

### 3. Route support

`POST /api/ike/v0/runtime/service-preflight/inspect` now accepts:
- `strict_preferred_owner`
- `expected_code_fingerprint`
- `strict_code_freshness`

This keeps the route inspect-style and narrow. It does not add a broad service
management surface.

### 4. Visible surfacing

The existing settings runtime panel now shows:
- `Code Freshness`

This is display-only surfacing of the existing narrow preflight result. It does
not bootstrap or restart services.

## Validation

Passed:

```powershell
$env:PYTHONPATH='D:\code\MyAttention\services\api'; python -m pytest services/api/tests/test_runtime_v0_service_preflight.py services/api/tests/test_routers_ike_v0.py -q
```

Result:
- `71 passed, 28 warnings, 9 subtests passed`

Passed:

```powershell
python -m compileall D:\code\MyAttention\services\api\runtime\service_preflight.py D:\code\MyAttention\services\api\routers\ike_v0.py
```

Passed:

```powershell
npx tsc --noEmit
```

Current local helper snapshot:

```text
status = ambiguous
preferred_owner.status = preferred_mismatch
owner_chain.status = parent_preferred_child_mismatch
code_fingerprint.fingerprint = 2c1cb7cf783aa7b4
code_freshness.status = unchecked
```

## Truthful Judgment

- `R2-G9 = accept_with_changes`

## Why `accept_with_changes`

Accepted because:
- code freshness is now machine-readable
- strict freshness mismatch can now gate live proof
- the route and visible surface are ready to carry this signal

Still `with_changes` because:
- current `8000` live route is still potentially stale relative to latest code
- code freshness is only `unchecked` unless a controller supplies an expected fingerprint
- service ownership normalization remains unresolved

## Controller Interpretation

`R2-G` no longer depends only on owner mismatch heuristics to reason about live
proof safety.

It now has:
- preferred-owner status
- owner-chain status
- code fingerprint
- optional strict code-freshness mismatch gating

This narrows the remaining operational gap further:
- not missing observability
- but still stale service ownership / stale served-code normalization
