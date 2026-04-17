# IKE Runtime v0 - R2-H5 Result Milestone

Date: 2026-04-09
Phase: `R2-H Canonical Service Launch Path Normalization`
Packet: `R2-H5 Windows Redirector Acceptability Decision`

## Scope

Apply the approved narrow Option B controller rule for the Windows `.venv`
redirector shape without broadening canonical acceptance semantics.

## Implemented

- updated runtime service preflight controller acceptability logic in:
  - [D:\code\MyAttention\services\api\runtime\service_preflight.py](/D:/code/MyAttention/services/api/runtime/service_preflight.py)
- updated focused service-preflight tests in:
  - [D:\code\MyAttention\services\api\tests\test_runtime_v0_service_preflight.py](/D:/code/MyAttention/services/api/tests/test_runtime_v0_service_preflight.py)
- updated route-level preflight response assertions in:
  - [D:\code\MyAttention\services\api\tests\test_routers_ike_v0.py](/D:/code/MyAttention/services/api/tests/test_routers_ike_v0.py)

## Controller Rule

The previous narrow controller status:

- `bounded_live_proof_ready`

is now replaced for the reviewed Windows redirector shape by:

- `acceptable_windows_venv_redirector`

This status only appears when all of the following are true:

1. API health is good
2. port ownership is clear
3. `platform.system() == "Windows"`
4. `windows_venv_redirector.status == "windows_venv_redirector_candidate"`
5. `repo_launcher.status == "parent_and_child_repo_launcher_match"`
6. `owner_chain.status == "parent_preferred_child_mismatch"`
7. `canonical_launch.status == "defined"`
8. `code_freshness.status == "match"`

## Truth Boundary

This does **not** auto-upgrade the service to canonical accepted state.

The returned controller acceptability payload now explicitly preserves:

- `status = acceptable_windows_venv_redirector`
- `acceptable = true`
- `controller_confirmation_required = true`

So this remains an intermediate controller-facing state, not a silent
relaxation of the canonical rule.

## Validation

Commands run:

```powershell
$env:PYTHONPATH='D:\code\MyAttention\services\api'; python -m pytest services/api/tests/test_runtime_v0_service_preflight.py -q
$env:PYTHONPATH='D:\code\MyAttention\services\api'; python -m pytest services/api/tests/test_routers_ike_v0.py -q
python -m compileall D:\code\MyAttention\services\api\runtime\service_preflight.py D:\code\MyAttention\services\api\tests\test_runtime_v0_service_preflight.py D:\code\MyAttention\services\api\tests\test_routers_ike_v0.py
```

Observed results:

- `50 passed, 1 warning`
- `29 passed, 28 warnings, 9 subtests passed`
- compile passed

## Controller Judgment

- `R2-H5 = accept_with_changes`

## Why Accept With Changes

This patch correctly absorbs the reviewed Windows `.venv` redirector decision,
but two follow-up constraints remain explicit:

1. controller still needs a durable final rule for when
   `acceptable_windows_venv_redirector` is manually promoted to fully canonical
   accepted status
2. the platform-specific exception should remain documented as a narrow Windows
   implementation detail, not a general owner-mismatch relaxation

