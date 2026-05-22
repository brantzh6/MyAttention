# IKE Runtime v0 - R2-I17 Controller Confirmation Review Pack

Date: 2026-04-10
Status: `review-ready`
Scope: `R2-I15 ~ R2-I17 only`

## Review Prompt

Review this packet as a narrow runtime controller-confirmation review for the
current live Windows canonical service shape.

Focus on:

1. whether the controller-facing decision surface is semantically honest and
   still clearly inspect-only
2. whether the live canonical `127.0.0.1:8000` shape truly satisfies the
   reviewed narrow Windows redirector rule rather than relying on an
   over-broad exception
3. whether the machine-readable `canonical_launch` baseline now matches the
   launch discipline that is actually validated live
4. whether any wording, flags, or docs overstate runtime capability or
   controller acceptance

Please prioritize:

- semantic honesty
- truth-boundary preservation
- reviewed narrowness of the Windows exception
- regression risk in runtime controller-facing semantics

Please return:

1. findings first, ordered by severity
2. validation gaps
3. recommendation:
   - `accept`
   - `accept_with_changes`
   - `reject`

## Main Changes Under Review

### 1. Controller Decision Route

File:

- [D:\code\MyAttention\services\api\routers\ike_v0.py](/D:/code/MyAttention/services/api/routers/ike_v0.py)

Route under review:

- `POST /api/ike/v0/runtime/service-preflight/controller-decision/inspect`

Expected behavior:

- expose one controller-facing decision envelope above preflight
- remain:
  - inspect-only
  - non-mutating
  - non-recording
  - non-promoting

### 2. Canonical Launch Baseline

File:

- [D:\code\MyAttention\services\api\runtime\service_preflight.py](/D:/code/MyAttention/services/api/runtime/service_preflight.py)

Expected behavior:

- `canonical_launch` should now truthfully reflect the validated Windows live
  launch discipline
- current Windows live expectation:
  - `launch_mode = repo_uvicorn_entry`
  - `launcher_path = .venv\\Scripts\\uvicorn.exe`

### 3. Focused Tests

Files:

- [D:\code\MyAttention\services\api\tests\test_runtime_v0_service_preflight.py](/D:/code/MyAttention/services/api/tests/test_runtime_v0_service_preflight.py)
- [D:\code\MyAttention\services\api\tests\test_routers_ike_v0.py](/D:/code/MyAttention/services/api/tests/test_routers_ike_v0.py)

Proof slices:

- self-check path stays truthful
- controller-decision inspect stays confirmation-gated
- canonical launch baseline is machine-readable and Windows-aware

## Evidence Chain

- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-I15_RESULT_MILESTONE_2026-04-10.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-I15_RESULT_MILESTONE_2026-04-10.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-I16_RESULT_MILESTONE_2026-04-10.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-I16_RESULT_MILESTONE_2026-04-10.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-I17_RESULT_MILESTONE_2026-04-10.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-I17_RESULT_MILESTONE_2026-04-10.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-I17_CONTROLLER_DECISION_BRIEF_2026-04-10.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-I17_CONTROLLER_DECISION_BRIEF_2026-04-10.md)

## Validation Run

Commands run:

```powershell
python -m pytest tests/test_runtime_v0_service_preflight.py tests/test_routers_ike_v0.py -q
python -m compileall runtime tests
```

Observed result:

- `91 passed, 28 warnings, 9 subtests passed`
- compile passed

## Live Evidence

Canonical live routes checked:

```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/health'
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/ike/v0/runtime/service-preflight/inspect' -Method Post -ContentType 'application/json' -Body '{"self_check_current_code":true,"strict_code_freshness":true}'
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/ike/v0/runtime/service-preflight/controller-decision/inspect' -Method Post -ContentType 'application/json' -Body '{"self_check_current_code":true,"strict_code_freshness":true}'
```

Observed live result:

- `controller_acceptability.status = acceptable_windows_venv_redirector`
- `controller_promotion.status = controller_confirmation_required`
- `decision.recommended_action = controller_confirmation_required`
- `canonical_launch.launch_mode = repo_uvicorn_entry`
- `canonical_launch.launcher_path = D:\\code\\MyAttention\\.venv\\Scripts\\uvicorn.exe`

## Current Claim Boundary

This packet claims only:

1. explicit controller-facing decision inspection
2. reclaimed live canonical Windows redirector proof shape
3. machine-readable alignment between documented canonical launch baseline and
   validated Windows live baseline

This packet does **not** claim:

1. automatic controller acceptance mutation
2. persisted controller-decision recording
3. detached supervision
4. scheduler semantics
5. resolution of the separate Windows Unicode logging debt

## Current Recommendation

- `accept_with_changes`

Reason:

- the current live controller-facing runtime shape is materially coherent and
  truthful
- but the acceptance remains intentionally narrow and still deserves external
  review before being treated as absorbed
