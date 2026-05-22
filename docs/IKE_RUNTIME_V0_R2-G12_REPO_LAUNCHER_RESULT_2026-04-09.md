# IKE Runtime v0 - R2-G12 Repo Launcher Result

Date: 2026-04-09
Phase: `R2-G Runtime Service Stability And Delegated Closure Hardening`
Focus: separate repo-launcher evidence from interpreter ownership

## Summary

`service_preflight` now records repo-launcher evidence separately from:

- preferred interpreter ownership
- owner chain
- code freshness

This closes another observability gap inside `R2-G`.

The controller can now distinguish:

- repo launcher match
- owner mismatch
- code freshness match

instead of collapsing all launch-path ambiguity into a single ownership signal.

## Files Changed

- [D:\code\MyAttention\services\api\runtime\service_preflight.py](/D:/code/MyAttention/services/api/runtime/service_preflight.py)
- [D:\code\MyAttention\services\api\routers\ike_v0.py](/D:/code/MyAttention/services/api/routers/ike_v0.py)
- [D:\code\MyAttention\services\api\tests\test_runtime_v0_service_preflight.py](/D:/code/MyAttention/services/api/tests/test_runtime_v0_service_preflight.py)
- [D:\code\MyAttention\services\api\tests\test_routers_ike_v0.py](/D:/code/MyAttention/services/api/tests/test_routers_ike_v0.py)
- [D:\code\MyAttention\services\web\components\settings\ike-workspace-manager.tsx](/D:/code/MyAttention/services/web/components/settings/ike-workspace-manager.tsx)

## What Landed

### 1. Machine-readable `repo_launcher`

`run_preflight(...)` now records:

- `details.repo_launcher`

Current statuses include:

- `parent_and_child_repo_launcher_match`
- `child_repo_launcher_match`
- `parent_repo_launcher_match`
- `repo_launcher_mismatch`
- `indeterminate`
- `unspecified`

### 2. Route surfacing

`POST /api/ike/v0/runtime/service-preflight/inspect` now also returns:

- `data.repo_launcher`

### 3. Visible surfacing

The existing settings runtime panel now shows:

- `Repo Launcher`

without widening into a general operations UI.

## Validation

Passed:

```powershell
$env:PYTHONPATH='D:\code\MyAttention\services\api'; python -m pytest services/api/tests/test_runtime_v0_service_preflight.py services/api/tests/test_routers_ike_v0.py -q
```

Result:

- `74 passed, 28 warnings, 9 subtests passed`

Passed:

```powershell
python -m compileall D:\code\MyAttention\services\api\routers\ike_v0.py
```

Passed:

```powershell
npx tsc --noEmit
```

Current local helper snapshot on `8000`:

- `preferred_owner.status = preferred_mismatch`
- `owner_chain.status = parent_preferred_child_mismatch`
- `repo_launcher.status = parent_and_child_repo_launcher_match`

## Truthful Judgment

- `R2-G12 = accept_with_changes`

## Why `accept_with_changes`

Accepted because:

- launch-path evidence is now better separated
- controller can reason about launcher correctness without losing ownership truth
- route and visible panel are aligned with the new field

Still `with_changes` because:

- this is still observability and discipline hardening
- it does not itself decide whether `parent_preferred_child_mismatch` is acceptable
- the controller acceptance rule for that case is still the next real decision

## Controller Interpretation

`R2-G` remaining work is now even narrower:

- not more preflight fields
- not more route visibility
- but deciding the controller rule for:
  - `repo_launcher = match`
  - `code_freshness = match`
  - `owner_chain = parent_preferred_child_mismatch`
