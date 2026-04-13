# IKE Runtime v0 - R2-I20 Result Milestone

Date: 2026-04-13
Phase: `R2-I20 Restart Recovery Closure`
Status: `materially_landed`

## Scope

Close exit criterion `D` for `Runtime v0` using existing bounded runtime truth,
reconstruction, and operator-surface evidence.

## Conclusion

`Runtime v0` now materially satisfies exit criterion `D`.

The bounded claim is:

- after process/session interruption, current runtime operational state can be
  recovered from canonical runtime truth rather than rebuilt from chat memory
  alone

## Evidence Chain

### 1. Durable truth already survives interruption

Existing DB-backed lifecycle proof already establishes that runtime truth is
persisted in canonical tables:

- `runtime_projects`
- `runtime_tasks`
- `runtime_task_events`
- `runtime_worker_leases`

Focused evidence:

- `test_db_backed_lifecycle_proof_persists_truth_path`
- `test_db_backed_lifecycle_proof_failure_reports_durable_partial_state`

Truthful meaning:

- both successful and partial-failure lifecycle facts survive in Postgres

### 2. Current work context can be reconstructed from canonical truth

`runtime/operational_closure.py` already provides the bounded recovery helpers:

- `reconstruct_runtime_work_context(...)`
- `persist_reconstructed_work_context(...)`
- `align_project_current_work_context(...)`
- `get_project_current_work_context(...)`

Truthful meaning:

- current runtime work context is derivative of canonical truth
- it can be rebuilt after interruption without inventing a second truth source

### 3. Recovered context can be surfaced back to controller/operator read paths

`runtime/project_surface.py` already reads current operational state from the
aligned runtime truth.

Focused evidence:

- `test_build_surface_follows_project_pointer_and_runtime_context`
- `test_surface_aligns_with_db_backed_lifecycle_proof`
- project-surface route tests in `test_routers_ike_v0.py`

Truthful meaning:

- recovered runtime truth is not trapped in storage
- it can be re-exposed through the existing operator/controller inspect surface

## Why Exit Criterion `D` Is Now Materially Satisfied

Exit criterion `D` required:

- recovery of current runtime state from durable truth after interruption

Current truthful judgment:

- this is now materially satisfied for the bounded Runtime v0 kernel

Reason:

1. lifecycle facts persist durably
2. work context can be reconstructed from those facts
3. project pointer can be re-aligned to the reconstructed active context
4. controller/operator inspect surfaces can read the aligned recovered state

## Truth Boundary

This result does not claim:

1. detached subprocess resumption
2. daemon or scheduler recovery
3. live worker-session continuation
4. full product recovery semantics

It only claims:

- bounded restart/session-loss recovery of current runtime operational state
  from canonical runtime truth

## Controller Judgment

- `R2-I20 = accept_with_changes`

## Remaining Exit Work

Above this packet, `Runtime v0` should now have one final closure item left:

1. final explicit exit review
2. explicit out-of-scope handoff for what remains outside Runtime v0

