# IKE Runtime v0 - R2-I18 Result Milestone

Date: 2026-04-11
Phase: `R2-I18 Controller Acceptance Record Boundary`
Status: `implemented_and_focused_validation_closed`

## Scope

Add one explicit durable controller acceptance record path above the current
`controller_confirmation_required` runtime service proof surface.

This packet is still narrow:

- one decision scope only: `canonical_service_acceptance`
- one inspect route
- one explicit record route
- no generic approval workflow
- no scheduler or detached supervisor semantics

## Implemented

- added a new narrow helper:
  - [D:\code\MyAttention\services\api\runtime\controller_acceptance.py](/D:/code/MyAttention/services/api/runtime/controller_acceptance.py)
- extended the IKE v0 router:
  - [D:\code\MyAttention\services\api\routers\ike_v0.py](/D:/code/MyAttention/services/api/routers/ike_v0.py)
- added focused router coverage:
  - [D:\code\MyAttention\services\api\tests\test_routers_ike_v0.py](/D:/code/MyAttention/services/api/tests/test_routers_ike_v0.py)
- added focused DB-backed helper coverage:
  - [D:\code\MyAttention\services\api\tests\test_runtime_v0_controller_acceptance.py](/D:/code/MyAttention/services/api/tests/test_runtime_v0_controller_acceptance.py)
- extended runtime DB-backed test cleanup registration:
  - [D:\code\MyAttention\services\api\tests\conftest.py](/D:/code/MyAttention/services/api/tests/conftest.py)

## What Changed

### New helper

`runtime/controller_acceptance.py` now provides two bounded sync helpers:

1. `inspect_controller_acceptance_record(...)`
2. `record_controller_acceptance(...)`

The helper reuses existing runtime truth only:

- `runtime_decisions`
- `runtime_task_events`
- standard reconstructed work-context closure via existing
  `operational_closure` helpers

### New inspect route

- `POST /api/ike/v0/runtime/service-preflight/controller-decision/record/inspect`

Behavior:

- reruns current preflight truth
- resolves one runtime project
- reads the latest finalized decision for
  `decision_scope = canonical_service_acceptance`
- returns explicit non-mutation boundary flags

### New record route

- `POST /api/ike/v0/runtime/service-preflight/controller-decision/record`

Behavior:

- reruns current preflight truth
- requires:
  - `controller_promotion.status = controller_confirmation_required`
  - non-empty `controller_id`
- records one explicit finalized `RuntimeDecision`
- records one explicit `RuntimeTaskEvent`
- reconstructs and persists one derived `RuntimeWorkContext`
- realigns the project pointer to the updated work context

## Narrow Persistence Policy

The persisted decision shape is:

- `decision_scope = canonical_service_acceptance`
- `outcome = adopt`
- `status = final`
- `created_by_kind = controller`

The helper also implements:

- idempotent reuse when current live basis matches the latest finalized record
- explicit supersession when the same narrow scope changes materially
- rejection when current live truth is not confirmation-eligible
- focused DB-backed supersession proof for changed basis

## Explicit Audit Constraint

`runtime_task_events.task_id` is currently required by schema.

So this packet uses one explicit narrow audit rule:

- the controller acceptance event is anchored to the latest runtime task in the
  target project
- if the project has no runtime task at all, the write is rejected

This is intentional bounded honesty, not hidden fabrication.

## Validation

Compile validation passed:

```powershell
python -m compileall runtime routers tests
```

Observed result:

- compile passed for the new helper, router, and tests

Focused runtime validation is now partially closed:

- router / inspect surface slice now passes under pytest once the test cleanup
  fixture stops forcing DB connection for every file
- command:

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
python -m pytest tests/test_routers_ike_v0.py -q
```

- observed result:
  - `40 passed, 28 warnings, 9 subtests passed`

DB-backed validation is now closed for the focused packet:

- command:

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
python -m pytest tests/test_runtime_v0_controller_acceptance.py -q
```

- observed result:
  - `5 passed, 1 warning`

Combined focused validation is also closed:

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
python -m pytest tests/test_runtime_v0_controller_acceptance.py tests/test_routers_ike_v0.py -q
```

- observed result:
  - `44 passed, 28 warnings, 9 subtests passed`

Validation note:

- D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-I18_VALIDATION_BLOCKER_NOTE_2026-04-11.md
- review absorption:
  - [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-I18_VALIDATED_REVIEW_ABSORPTION_2026-04-13.md](./IKE_RUNTIME_V0_R2-I18_VALIDATED_REVIEW_ABSORPTION_2026-04-13.md)

## Mainline Meaning

`R2-I18` moves the runtime mainline above pure inspect semantics:

- before this packet:
  - runtime could say `controller_confirmation_required`
  - runtime could not durably record one explicit controller confirmation
- after this packet:
  - runtime now has one narrow durable acceptance-record path
  - the write path is explicit, bounded, and auditable
  - the claim boundary still stops short of a full approval workflow

## Controller Judgment

- `R2-I18 = accept_with_changes`

## Remaining Gaps

This still does not prove:

1. full runtime-suite closure beyond the focused `R2-I18` slice
2. a taskless project acceptance path
3. broad approval workflow semantics
4. detached execution or supervision semantics
5. any claim that a recorded acceptance automatically means the whole runtime
   has generic controller-governed promotion workflows

