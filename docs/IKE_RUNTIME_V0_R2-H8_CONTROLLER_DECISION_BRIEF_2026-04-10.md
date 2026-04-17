# IKE Runtime v0 - R2-H8 Controller Decision Brief

Date: 2026-04-10
Phase: `R2-H Canonical Service Launch Path Normalization`
Type: `controller decision brief`

## Decision Requested

Should the current canonical Windows service shape now be treated as
controller-accepted canonical proof?

## Short Answer

Recommendation:

- `accept_with_changes`

Meaning:

- accept the current local canonical `8000` service as the reviewed Windows
  canonical proof shape
- keep the acceptance narrow and platform-specific
- record that this is not a general owner-mismatch relaxation

## Evidence Chain

### 1. `R2-H5`

- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-H5_RESULT_MILESTONE_2026-04-09.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-H5_RESULT_MILESTONE_2026-04-09.md)

What it established:

- Windows redirector shape can be `acceptable_windows_venv_redirector`
- `acceptable = true`
- `controller_confirmation_required = true`

### 2. `R2-H6`

- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-H6_CONTROLLER_PROMOTION_READINESS_RESULT_2026-04-10.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-H6_CONTROLLER_PROMOTION_READINESS_RESULT_2026-04-10.md)

What it established:

- promotion semantics are now machine-readable
- current reviewed Windows exception is promotion-eligible but confirmation-gated

### 3. `R2-H7`

- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-H7_LIVE_PROMOTABLE_SHAPE_RESULT_2026-04-10.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-H7_LIVE_PROMOTABLE_SHAPE_RESULT_2026-04-10.md)

What it established:

- the real local canonical `127.0.0.1:8000` service now reaches that reviewed
  shape
- live `controller_acceptability = acceptable_windows_venv_redirector`
- live `controller_promotion.eligible = true`

## Current Technical Reading

The remaining mismatch is now narrow and understood:

- child listener uses system `Python312`
- parent launcher uses repo `.venv\Scripts\python.exe`
- both parent and child run repo `run_service.py`
- code freshness matches

This matches the reviewed Windows venv redirector interpretation rather than a
real launch-integrity drift.

## What Accepting Means

If accepted, the controller is saying:

1. this specific reviewed Windows redirector shape is good enough to count as
   canonical local service proof
2. the canonical launch-path normalization phase no longer blocks the runtime
   mainline
3. the next narrow runtime step can open above this baseline

## What It Does Not Mean

Acceptance does **not** mean:

- all owner mismatches are acceptable
- non-Windows environments get the same exception
- service supervision or daemonization is solved
- mutable acceptance recording is already implemented

## Recommended Next Step After Acceptance

Open the next runtime phase above `R2-H`:

- first real task lifecycle on top of the now-reviewed canonical service path

## Recommendation

- `accept_with_changes`

Changes still remaining after acceptance:

1. keep the Windows exception durably documented as narrow
2. later decide whether canonical acceptance should also be written into a
   durable controller action record, not just inferred from inspect evidence
