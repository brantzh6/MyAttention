# IKE Runtime v0 - R2-I18 Validated Review Absorption

Date: 2026-04-13
Scope: `R2-I18 Controller Acceptance Record Boundary`
Status: `selective_absorption_completed`

## Reviewed Inputs

Accepted as materially in-scope:

- `claude`
- `chatgpt`

Rejected as mixed-context / out-of-scope:

- `gemini`

Reason for rejecting `gemini`:

- it still mixes unrelated runtime packets and broader architecture topics
- it discusses multi-tenant isolation, DB-backed lifecycle proof, and `R3`
  external-agent progression that are not part of the current `R2-I18`
  validated review pack
- this is scope drift, not trustworthy packet-local review evidence

## Accepted Conclusions

The following conclusions are accepted:

1. `R2-I18` remains narrow and honest
2. inspect-vs-record separation is clean
3. the current task-anchor rule is acceptable for this packet
4. focused local validation materially closes this packet

## Accepted Changes

### 1. Supersession behavior is now explicitly proven

Accepted review point:

- changed-basis supersession should have one focused DB-backed proof

Applied change:

- added focused DB-backed test in
  [test_runtime_v0_controller_acceptance.py](../services/api/tests/test_runtime_v0_controller_acceptance.py)

The new proof asserts:

- first record writes one final decision
- changed basis writes a new final decision
- the old final decision becomes `SUPERSEDED`
- `supersedes_decision_id` points to the old decision

### 2. Test style cleanup applied

Accepted review point:

- the no-task-anchor rejection test should use `pytest.raises`

Applied change:

- replaced manual `try/except` assertion with `pytest.raises(...)`

### 3. Persistence wording tightened

Accepted review point:

- `R2-I18` should not be described as if it only updates
  `runtime_work_contexts.latest_decision_id`

Absorbed wording:

- `R2-I18` reuses existing runtime persistence only:
  - `runtime_decisions`
  - `runtime_task_events`
  - standard reconstructed work-context closure via existing
    `operational_closure` helpers

## Deferred Notes

### 1. `conftest.py` whitelist -> marker migration

Decision:

- defer

Reason:

- bounded test-only debt
- not an `R2-I18` blocker

### 2. `ike_v0.py` modularization

Decision:

- defer

Reason:

- real maintenance note
- not an `R2-I18` packet defect

## Updated Controller Judgment

- code-level packet: `accept`
- project/controller judgment: `accept_with_changes`

The remaining `with_changes` meaning is now narrow:

1. keep the stop rule explicit:
   - this is a bounded controller acceptance record path
   - not a generic approval workflow seed
2. keep persistence-boundary wording precise in future packs
