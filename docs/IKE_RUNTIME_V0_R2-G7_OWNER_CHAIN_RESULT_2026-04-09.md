# IKE Runtime v0 R2-G7 Owner Chain Result

## Scope

`R2-G7 = machine-readable owner-chain diagnosis for service preflight`

This is a narrow operational hardening step inside `R2-G`.

It does not:
- normalize service ownership
- add a supervisor
- change runtime truth semantics
- widen runtime visible-surface scope

## What Is Now Real

- `service_preflight` now captures parent-process ownership details for the
  single listener case on Windows
- `details.owner_chain` is now machine-readable
- current live `8000` can now be classified as:
  - `preferred_mismatch`
  - and more specifically:
    - `parent_preferred_child_mismatch`

## Code

- helper:
  - [D:\code\MyAttention\services\api\runtime\service_preflight.py](/D:/code/MyAttention/services/api/runtime/service_preflight.py)
- tests:
  - [D:\code\MyAttention\services\api\tests\test_runtime_v0_service_preflight.py](/D:/code/MyAttention/services/api/tests/test_runtime_v0_service_preflight.py)

## Controller Validation

- `PYTHONPATH=D:\code\MyAttention\services\api python -m pytest services/api/tests/test_runtime_v0_service_preflight.py -q`
  - `44 passed, 1 warning`
- `python -m compileall D:\code\MyAttention\services\api\runtime\service_preflight.py`
  - passed
- live strict snapshot on current `8000`:
  - `status = ambiguous`
  - `details.preferred_owner.status = preferred_mismatch`
  - `details.owner_chain.status = parent_preferred_child_mismatch`

## Truthful Interpretation

This materially improves the operational diagnosis.

Before this slice, controller could only say:
- the live owner is not preferred

Now controller can say:
- the preferred repo-owned launcher is present in the parent chain
- but the actual listener is still a system-Python child

That means the remaining issue is more precise than generic process drift:
- it is an **interpreter/ownership chain drift** inside the current launch path

## Result

`R2-G7 = accept_with_changes`

## Remaining Gap

- ownership mismatch is now better diagnosed
- ownership is still not normalized
- detached Claude completion remains a separate active hardening track
