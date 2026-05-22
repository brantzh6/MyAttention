# IKE Runtime v0 Packet - R2-I14 Coding Brief

Date: 2026-04-10
Packet: `R2-I14`
Type: `coding`
Phase: `R2-I14 Promotion Readiness Self-Check`

## Objective

Close one narrow controller-facing gap in live runtime preflight:

- default live preflight currently leaves `code_freshness = unchecked`
- that default path therefore reports `blocked_owner_mismatch`
- but the same live service reaches the reviewed Windows redirector acceptance
  path when the caller supplies the current fingerprint explicitly

The task is to make this self-check truthful and controller-usable without
manual fingerprint copy/paste.

## Existing Evidence

- live preflight logic:
  - [D:\code\MyAttention\services\api\runtime\service_preflight.py](/D:/code/MyAttention/services/api/runtime/service_preflight.py)
- preflight route surface:
  - [D:\code\MyAttention\services\api\routers\ike_v0.py](/D:/code/MyAttention/services/api/routers/ike_v0.py)
- focused preflight tests:
  - [D:\code\MyAttention\services\api\tests\test_runtime_v0_service_preflight.py](/D:/code/MyAttention/services/api/tests/test_runtime_v0_service_preflight.py)

## Required Outcome

Produce the narrowest truthful mechanism that allows a controller-facing
preflight request to self-check current code freshness for the canonical local
service.

Acceptable semantics:

1. the route/helper may derive the current fingerprint from the current file
   tree for a local self-check path
2. mismatch must still be detectable and block
3. Windows redirector acceptance must still remain confirmation-gated
4. no automatic promotion mutation is added

## Guardrails

Do not:

- auto-promote to `canonical_accepted`
- collapse `acceptable_windows_venv_redirector` into `canonical_ready`
- widen into service restart or deployment framework work
- hide the difference between self-check and externally supplied expectations

## Validation Expectation

At minimum:

- focused pytest slice for preflight helper/route behavior
- compile/import checks
- one live canonical-service check showing the self-check path result

## Suggested Lane

Prefer OpenClaw `qwen3.6-plus` or Claude Code `glm-5.1` for delegated
implementation, then return to controller review.
