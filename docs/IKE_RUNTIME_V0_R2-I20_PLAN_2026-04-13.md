# IKE Runtime v0 - R2-I20 Plan

Date: 2026-04-13
Phase: `R2-I20 Restart Recovery Closure`
Status: `controller_plan`

## Scope

Write one bounded result packet above existing evidence.

No new runtime routes.
No new DB objects.
No new recovery mechanism.

## Closure Shape

`R2-I20` closes exit criterion `D` by explicitly linking three already-landed
layers:

1. durable lifecycle truth
2. work-context reconstruction from canonical truth
3. project-surface alignment back onto reconstructed truth

## Evidence To Reuse

### 1. Durable lifecycle truth

- `execute_db_backed_lifecycle_proof(...)`
- `test_db_backed_lifecycle_proof_persists_truth_path`
- `test_db_backed_lifecycle_proof_failure_reports_durable_partial_state`

### 2. Work-context reconstruction and persistence

- `reconstruct_runtime_work_context(...)`
- `persist_reconstructed_work_context(...)`
- `align_project_current_work_context(...)`
- `get_project_current_work_context(...)`

### 3. Project-facing read-surface re-alignment

- `test_surface_aligns_with_db_backed_lifecycle_proof`
- project-surface inspect/bootstrap route tests in `test_routers_ike_v0.py`

## Intended Result Statement

After restart or session loss:

- runtime truth remains in Postgres
- current work context can be reconstructed from that truth
- project pointer can be re-aligned to the reconstructed active context
- controller/operator inspect surfaces can read that recovered state

## Non-Goals

- no live process restart automation
- no lease resumption claim
- no worker reconnection claim
- no daemon supervision claim

## Expected Follow-On

After `R2-I20`, `Runtime v0` should have only one final exit-oriented packet
left:

- explicit final exit review / out-of-scope handoff
