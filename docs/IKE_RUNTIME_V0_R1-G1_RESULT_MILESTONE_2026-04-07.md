# IKE Runtime v0 R1-G1 Result Milestone

## Scope

`R1-G1` hardened runtime review-submission provenance inside the existing
`memory_packets` and `operational_closure` paths.

This change stayed inside existing runtime metadata discipline.
It did **not** introduce a new review object family.

## Real Code Surface

Implemented in:

- [D:\code\MyAttention\services\api\runtime\memory_packets.py](/D:/code/MyAttention/services/api/runtime/memory_packets.py)
- [D:\code\MyAttention\services\api\runtime\operational_closure.py](/D:/code/MyAttention/services/api/runtime/operational_closure.py)
- [D:\code\MyAttention\services\api\tests\conftest.py](/D:/code/MyAttention/services/api/tests/conftest.py)
- [D:\code\MyAttention\services\api\tests\test_runtime_v0_memory_packets.py](/D:/code/MyAttention/services/api/tests/test_runtime_v0_memory_packets.py)
- [D:\code\MyAttention\services\api\tests\test_runtime_v0_operational_closure.py](/D:/code/MyAttention/services/api/tests/test_runtime_v0_operational_closure.py)

Key hardening:

- `transition_to_review(...)` now records:
  - `review_submitted_by`
  - `review_submitted_by_id`
  - `review_submitted_at`
  - `review_reason`
  - nested `review_submission`
- `transition_packet_to_review(...)` now derives review provenance from the
  packet's real `created_by_kind/created_by_id` instead of hardcoding
  `delegate`
- empty review-submission actor ids are now rejected

## Validation

Controller validation run:

```powershell
python -m compileall services/api/runtime/memory_packets.py services/api/runtime/operational_closure.py services/api/tests/test_runtime_v0_memory_packets.py services/api/tests/test_runtime_v0_operational_closure.py
$env:PYTHONPATH='D:\code\MyAttention\services\api'; python -m pytest services/api/tests/test_runtime_v0_memory_packets.py -k "draft_to_review or truthful_actor_for_non_delegate or actor_id" -q
$env:PYTHONPATH='D:\code\MyAttention\services\api'; python -m pytest services/api/tests/test_runtime_v0_operational_closure.py -k "review_submission_provenance or empty_created_by_id" -q
$env:PYTHONPATH='D:\code\MyAttention\services\api'; python -m pytest services/api/tests/test_runtime_v0_project_surface.py -q
python -m compileall services/api/tests/conftest.py
$env:PYTHONPATH='D:\code\MyAttention\services\api'; python -m pytest services/api/tests/test_runtime_v0_project_surface.py services/api/tests/test_runtime_v0_operational_closure.py services/api/tests/test_runtime_v0_memory_packets.py -q
```

Observed results:

- compile check: passed
- narrow memory-packet provenance slice: `3 passed, 48 deselected, 1 warning`
- DB-backed operational-closure provenance slice:
  - `2 passed, 8 deselected, 1 warning`
- standalone `project_surface` verification:
  - `4 passed, 1 warning`
- combined DB-backed provenance/runtime slice:
  - `65 passed, 1 warning`

## What Was Proved

1. review submission now records both actor kind and actor id
2. runtime helper submission provenance is truthful to the packet creator role
   instead of assuming `delegate`
3. malformed review-submission provenance with empty actor id is rejected
4. acceptance provenance remains unchanged and compatible with existing trusted
   packet rules

## Narrow Test Hardening Included

- `services/api/tests/conftest.py` now includes
  `test_runtime_v0_project_surface.py` in the shared runtime table cleanup set.
- This removed the previously observed cross-suite DB-backed persistence
  interaction and confirmed it was a test-isolation issue, not an `R1-G1`
  semantics regression.

## Truthful Judgment

`R1-G1 = accept_with_changes`

Why not plain `accept`:

- coding and DB-backed proof are real
- independent delegated review/testing/evolution evidence is not yet recovered
