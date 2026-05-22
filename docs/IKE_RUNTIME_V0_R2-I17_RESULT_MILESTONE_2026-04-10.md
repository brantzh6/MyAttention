# IKE Runtime v0 - R2-I17 Result Milestone

Date: 2026-04-10
Phase: `R2-I17 Canonical Launch Baseline Alignment`
Status: `completed`

## Scope

Align the machine-readable `canonical_launch` surface with the Windows launch
discipline that is actually validated live.

This packet is narrow and runtime-local.
It does not introduce new controller semantics.

## Implemented

- updated the runtime preflight helper in:
  - [D:\code\MyAttention\services\api\runtime\service_preflight.py](/D:/code/MyAttention/services/api/runtime/service_preflight.py)
- extended focused helper coverage in:
  - [D:\code\MyAttention\services\api\tests\test_runtime_v0_service_preflight.py](/D:/code/MyAttention/services/api/tests/test_runtime_v0_service_preflight.py)

## What Changed

`canonical_launch` is now platform-aware:

- on Windows with repo `uvicorn.exe` available:
  - `launch_mode = repo_uvicorn_entry`
  - `launcher_path = .venv\\Scripts\\uvicorn.exe`
  - `command_line = "…\\uvicorn.exe" main:app --host … --port …`
- on other paths/platforms:
  - it falls back to the existing `python run_service.py` shape

The surface now also keeps explicit context fields:

- `interpreter_path`
- `launcher_path`
- `launch_mode`
- `service_entry_path`
- `launcher_exists`

## What The New Tests Prove

The focused helper tests now prove:

1. `canonical_launch` remains machine-readable
2. Windows can explicitly surface the repo `uvicorn.exe` launch baseline
3. non-Windows or missing-uvicorn cases still retain the existing fallback

## Live Canonical-Service Evidence

After controlled refresh on canonical `127.0.0.1:8000`, live preflight now
returns:

- `canonical_launch.launch_mode = repo_uvicorn_entry`
- `canonical_launch.launcher_path = D:\\code\\MyAttention\\.venv\\Scripts\\uvicorn.exe`
- `canonical_launch.command_line = "D:\\code\\MyAttention\\.venv\\Scripts\\uvicorn.exe" main:app --host 127.0.0.1 --port 8000`
- `controller_acceptability.status = acceptable_windows_venv_redirector`
- `controller_promotion.status = controller_confirmation_required`

Live controller-decision inspect still returns:

- `decision.recommended_action = controller_confirmation_required`
- `truth_boundary.inspect_only = true`
- `truth_boundary.mutates_acceptance = false`

## Mainline Meaning

The runtime mainline no longer has to tolerate a mismatch between:

- the machine-readable canonical launch baseline
- the Windows launch chain that is actually validated live

This improves runtime honesty at the controller surface without widening the
claim boundary.

## Validation

Focused validation:

```powershell
python -m pytest tests/test_runtime_v0_service_preflight.py tests/test_routers_ike_v0.py -q
python -m compileall runtime tests
```

Observed result:

- `91 passed, 28 warnings, 9 subtests passed`
- compile passed

Live validation:

```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/health'
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/ike/v0/runtime/service-preflight/inspect' -Method Post -ContentType 'application/json' -Body '{"self_check_current_code":true,"strict_code_freshness":true}'
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/ike/v0/runtime/service-preflight/controller-decision/inspect' -Method Post -ContentType 'application/json' -Body '{"self_check_current_code":true,"strict_code_freshness":true}'
```

Observed result:

- canonical `8000` healthy
- live `canonical_launch` now reflects the validated Windows `uvicorn.exe`
  chain
- live decision surface remains `controller_confirmation_required`

## Controller Judgment

- `R2-I17 = accept`

## Remaining Gaps

This still does not prove:

1. automatic controller acceptance mutation
2. persisted controller decision recording
3. detached supervision
4. scheduler semantics
5. resolution of the separate Windows console Unicode logging debt
