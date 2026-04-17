# IKE Repository Rename P2-D4 Runtime Preflight Test Path Result

Date: 2026-04-09
Status: accept_with_changes

## Summary

Removed hardcoded `D:\code\MyAttention` path assumptions from the runtime
service-preflight and router tests.

## Files Changed

- `services/api/tests/test_runtime_v0_service_preflight.py`
- `services/api/tests/test_routers_ike_v0.py`

## What Changed

- added test-local derived path constants based on `Path(__file__).resolve()`
- replaced hardcoded preferred-owner and repo-launcher path hints with values
  derived from the current repo root
- replaced hardcoded `.venv\Scripts\python.exe`,
  `.venv\Scripts\uvicorn.exe`, and `services/api/run_service.py` command-line
  fixtures with path values built from the current test environment

## Validation

- `python -m unittest services.api.tests.test_runtime_v0_service_preflight`
  - `49 passed`
- `python -m unittest services.api.tests.test_routers_ike_v0`
  - `29 passed`

## Known Risks

- this patch only removes hardcoded old-root assumptions from these two test
  files
- other rename/cutover references may still exist elsewhere in the repo and
  should continue to be handled in narrow packets

## Recommendation

- `accept_with_changes`
