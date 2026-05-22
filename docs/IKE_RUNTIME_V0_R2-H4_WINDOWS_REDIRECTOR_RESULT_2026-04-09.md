# IKE Runtime v0 - R2-H4 Windows Redirector Result

Date: 2026-04-09
Phase: `R2-H Canonical Service Launch Path Normalization`

## Summary

The runtime preflight helper can now explicitly classify the current
parent-repo/child-system process shape as:

- `windows_venv_redirector_candidate`

This is a diagnosis-only improvement.

It does not change controller acceptance yet.

## Validation

- `PYTHONPATH=D:\\code\\MyAttention\\services\\api python -m pytest services/api/tests/test_runtime_v0_service_preflight.py services/api/tests/test_routers_ike_v0.py -q`
  - `78 passed, 28 warnings, 9 subtests passed`
- `python -m compileall D:\\code\\MyAttention\\services\\api\\runtime\\service_preflight.py`
  - passed
- local helper evidence:
  - `run_preflight_sync(port=8000, strict_preferred_owner=True)`
  - `details.windows_venv_redirector.status = windows_venv_redirector_candidate`

## Live Truth

The canonical `8000` route has not yet been freshly reloaded after this patch,
so the current live route response does not yet expose:

- `details.windows_venv_redirector`

This is truthful and expected under the current phase:

- helper/test evidence is current
- canonical live service still needs a fresh reload for this latest field

## Truthful Judgment

- `R2-H4 = accept_with_changes`

## Controller Interpretation

The current canonical-service blocker is now narrower again:

- not generic owner mismatch
- but a specific Windows `.venv` redirector-shaped mismatch candidate

The next step should be a controller decision on whether this pattern can be
accepted for canonical service proof or must remain blocked.
