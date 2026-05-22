# IKE Runtime v0 - R2-I14 Self-Check Review Pack

Date: 2026-04-10
Status: `review-ready`
Scope: `R2-I14 only`

## Review Prompt

Review this packet as a narrow runtime controller-facing preflight review.

Focus on:

1. whether `self_check_current_code` is a truthful mechanism for local
   code-freshness self-check rather than a shortcut that hides real mismatch
2. whether the reviewed Windows redirector acceptance rule remains confirmation
   gated and is not silently upgraded into direct canonical-ready
3. whether the helper and route tests cover the new self-check path with enough
   rigor
4. whether any new wording, flags, or behavior overstate runtime capability

Please prioritize:

- semantic honesty
- truth-boundary preservation
- controller usability without fake certainty
- regression risk in preflight semantics

Please return:

1. findings first, ordered by severity
2. validation gaps
3. recommendation:
   - `accept`
   - `accept_with_changes`
   - `reject`

## Main Changes Under Review

### 1. Service Preflight Helper

File:

- [D:\code\MyAttention\services\api\runtime\service_preflight.py](/D:/code/MyAttention/services/api/runtime/service_preflight.py)

Key addition:

- `self_check_current_code: bool = False`

Intended meaning:

- when `true`, and when the caller does not provide
  `expected_code_fingerprint`, the helper may derive the current local file
  fingerprint and compare against that

What this is supposed to enable:

- controller-facing local promotion-readiness self-check
- without manual fingerprint copy/paste

What this must not do:

- fake freshness across different code trees
- auto-promote to `canonical_accepted`
- blur `acceptable_windows_venv_redirector` into `canonical_ready`

### 2. Controller-Facing Route Surface

File:

- [D:\code\MyAttention\services\api\routers\ike_v0.py](/D:/code/MyAttention/services/api/routers/ike_v0.py)

Route under review:

- [ike_v0.py:581](/D:/code/MyAttention/services/api/routers/ike_v0.py#L581)

New request field:

- `self_check_current_code`

Expected route behavior:

- default behavior remains unchanged
- explicit self-check request can produce:
  - `code_freshness = match`
  - `controller_acceptability = acceptable_windows_venv_redirector`
  - `controller_promotion = controller_confirmation_required`

### 3. Focused Tests

Files:

- [D:\code\MyAttention\services\api\tests\test_runtime_v0_service_preflight.py](/D:/code/MyAttention/services/api/tests/test_runtime_v0_service_preflight.py)
- [D:\code\MyAttention\services\api\tests\test_routers_ike_v0.py](/D:/code/MyAttention/services/api/tests/test_routers_ike_v0.py)

New proof slices:

- helper-level self-check path
- route-level forwarding of `self_check_current_code`

## Validation Run

Commands run:

```powershell
python -m pytest tests/test_runtime_v0_service_preflight.py tests/test_routers_ike_v0.py -q
python -m compileall runtime routers tests
```

Observed result:

- `89 passed, 28 warnings, 9 subtests passed`
- compile passed

## Live Evidence

Canonical live route checked:

```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/ike/v0/runtime/service-preflight/inspect' -Method Post -ContentType 'application/json' -Body '{"self_check_current_code":true,"strict_code_freshness":true}'
```

Observed live result:

- `code_freshness.status = match`
- `controller_acceptability.status = acceptable_windows_venv_redirector`
- `controller_promotion.status = controller_confirmation_required`

## Current Claim Boundary

This packet claims only:

1. local controller-facing code-freshness self-check
2. preserved Windows redirector acceptance semantics
3. preserved controller-confirmation gate

This packet does **not** claim:

1. automatic promotion mutation
2. direct canonical owner equality
3. detached supervision
4. scheduler semantics

## Current Recommendation

- `accept_with_changes`

Reason:

- the packet materially improves controller usability and keeps the reviewed
  honesty boundary
- but it still needs external review before being treated as absorbed
