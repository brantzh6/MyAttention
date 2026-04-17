# IKE Runtime v0 - R2-I15 Result Milestone

Date: 2026-04-10
Phase: `R2-I15 Controller Decision Inspect Surface`
Status: `completed`

## Scope

Expose one explicit controller-facing decision surface above runtime service
preflight.

This packet is inspect-only.
It does not mutate controller acceptance or record a controller action.

## Implemented

- added one new controller-facing inspect route in:
  - [D:\code\MyAttention\services\api\routers\ike_v0.py](/D:/code/MyAttention/services/api/routers/ike_v0.py)
- added focused route coverage in:
  - [D:\code\MyAttention\services\api\tests\test_routers_ike_v0.py](/D:/code/MyAttention/services/api/tests/test_routers_ike_v0.py)

New route:

- `POST /api/ike/v0/runtime/service-preflight/controller-decision/inspect`

## What Changed

The new route reuses the existing bounded preflight request shape and returns a
controller-facing decision envelope with:

- `controller_acceptability`
- `controller_promotion`
- `decision`
  - `recommended_action`
  - `target_status`
  - `basis`
  - `eligible`
- `truth_boundary`
  - `inspect_only = true`
  - `mutates_acceptance = false`
  - `records_controller_decision = false`
  - `implies_canonical_accepted = false`

Recommendation mapping is now explicit:

- `controller_can_promote_now -> controller_may_accept_now`
- `controller_confirmation_required -> controller_confirmation_required`
- all other states -> `not_ready_for_controller_acceptance`

## What The New Tests Prove

The new focused tests now prove:

1. the new route forwards the same preflight request shape, including
   `self_check_current_code`
2. the controller-facing recommendation remains confirmation-gated when the
   reviewed Windows redirector shape is returned
3. the new route does not imply acceptance mutation

## Live Canonical-Service Evidence

The live canonical service now exposes the new route in OpenAPI:

- `/api/ike/v0/runtime/service-preflight/controller-decision/inspect`

Live request:

```json
{
  "self_check_current_code": true,
  "strict_code_freshness": true
}
```

returned:

- `controller_acceptability.status = blocked_owner_mismatch`
- `controller_promotion.status = not_promotable`
- `decision.recommended_action = not_ready_for_controller_acceptance`
- `truth_boundary.inspect_only = true`
- `truth_boundary.mutates_acceptance = false`
- `truth_boundary.records_controller_decision = false`

This is still a truthful result.
It means the new decision surface is live, but the current canonical `8000`
process ownership chain is not presently in the reviewed promotable Windows
redirector shape.

## Mainline Meaning

The runtime mainline now has one explicit controller-facing decision inspect
surface above preflight.

This closes a controller readability gap:

- the decision edge is now inspectable directly
- the truth boundary is explicit
- the route does not overclaim that inspection equals acceptance

It does not close the launch-discipline gap on its own.
If the live service is launched outside the reviewed owner chain, the new route
truthfully reports `not_ready_for_controller_acceptance`.

## Validation

Focused validation:

```powershell
python -m pytest tests/test_routers_ike_v0.py -q
python -m compileall routers tests
```

Observed result:

- `37 passed, 28 warnings, 9 subtests passed`
- compile passed

Live validation:

```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/health'
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/openapi.json'
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/ike/v0/runtime/service-preflight/controller-decision/inspect' -Method Post -ContentType 'application/json' -Body '{"self_check_current_code":true,"strict_code_freshness":true}'
```

Observed result:

- live canonical service healthy
- live OpenAPI exposes the new controller-decision inspect route
- live decision route remains inspect-only and non-mutating
- current live owner chain still resolves to `blocked_owner_mismatch`

## Controller Judgment

- `R2-I15 = accept_with_changes`

## Remaining Gaps

This still does not prove:

1. live canonical `8000` is back on the reviewed promotable owner chain
2. automatic controller promotion mutation
3. persisted controller decisions
4. detached supervision
5. scheduler semantics

## Follow-On Note

During the bounded service restart for live proof, Windows console logging also
re-exposed a separate operational debt:

- Unicode log writes can still raise `UnicodeEncodeError` under some console
  encodings

That issue is real, but it is outside the narrow scope of `R2-I15`.
