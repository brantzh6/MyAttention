# IKE Runtime v0 - R2-H1 Result Milestone

Date: 2026-04-09
Phase: `R2-H Canonical Service Launch Path Normalization`

## Summary

`R2-H1` made the controller-acceptable canonical launch path explicit and
machine-readable.

This did not normalize the live canonical service yet.

It did establish a truthful baseline for what the canonical launch path should
be and surfaced that baseline in both backend preflight output and the settings
runtime panel.

## Landed Changes

- backend:
  - `service_preflight` now emits `details.canonical_launch`
- frontend:
  - settings runtime panel now displays the canonical launch command
- tests:
  - canonical launch-path definition is now covered in
    `test_runtime_v0_service_preflight.py`

## Validation

- `PYTHONPATH=D:\\code\\MyAttention\\services\\api python -m pytest services/api/tests/test_runtime_v0_service_preflight.py services/api/tests/test_routers_ike_v0.py -q`
  - `77 passed, 28 warnings, 9 subtests passed`
- `python -m compileall D:\\code\\MyAttention\\services\\api\\runtime\\service_preflight.py`
  - passed
- `npx tsc --noEmit`
  - passed

## Live Truth

Current canonical `8000` still serves stale preflight code and does not yet
expose the newly landed `canonical_launch` field.

That is consistent with the existing `R2-G` conclusion:

- canonical service ownership / served-code normalization is still incomplete

So this result should be treated as:

- code landed
- tests landed
- visible surface landed
- canonical live normalization still pending

## Truthful Judgment

- `R2-H1 = accept_with_changes`

## Next Narrow Step

Use the explicit canonical launch command as the baseline for the next
controller-accepted canonical service normalization attempt.
