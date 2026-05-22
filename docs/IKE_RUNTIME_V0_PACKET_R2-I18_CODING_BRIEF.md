# IKE Runtime v0 - Packet R2-I18 Coding Brief

Date: 2026-04-10
Packet: `R2-I18 Controller Acceptance Record Boundary`
Status: `ready for bounded implementation`

## Goal

Implement one narrow durable controller-acceptance record boundary above the
current live `controller_confirmation_required` state.

## Scope

Implement only the minimum needed to prove:

1. one controller acceptance decision can be durably recorded
2. one append-only audit event can be durably recorded beside it
3. the current work surface can inspect that decision truthfully

## Non-Goals

- no generic approval workflow
- no multi-step review pipeline
- no detached job control
- no scheduler semantics
- no broad decisions CRUD surface

## Preferred Data Landing

Use existing runtime canonical structures:

- `runtime_decisions`
- `runtime_task_events`
- `runtime_work_contexts.latest_decision_id`

Do not introduce a new table unless a hard blocker is discovered.

## Suggested Narrow API Shape

### 1. Inspect

One inspect-style route for current canonical-service acceptance state.

Purpose:

- show whether an acceptance record exists
- show its basis and current finality

### 2. Record

One explicit controller action route for recording acceptance.

Guardrails:

- explicit controller actor required
- explicit target scope required
- only allowed when current inspect state is
  `controller_confirmation_required`
- must not auto-fire from inspect

## Required Truth Boundary

The implementation must preserve:

- inspect is read-only
- record is explicit write
- no claim of automatic promotion
- no claim of general controller workflow support

## Suggested Record Shape

### Runtime Decision

- `decision_scope = canonical_service_acceptance`
- `outcome = adopt`
- `status = final`
- `created_by_kind = controller`
- metadata should include:
  - `controller_acceptability`
  - `controller_promotion`
  - `decision_basis`
  - `launch_mode`
  - `host`
  - `port`

### Runtime Event

- `event_type = controller_acceptance_recorded`
- payload includes:
  - `decision_id`
  - `decision_scope`
  - `target_status`
  - `basis`

### Work Context

- update/reflect `latest_decision_id` through canonical truth
- do not invent extra mutable acceptance fields elsewhere

## Edge Cases To Handle

1. repeated confirmation request
   - explicit no-op or supersede
   - never create ambiguous active truth silently
2. inspect when no acceptance record exists
3. record attempt when current preflight is not confirmation-eligible
4. record attempt with missing controller identity

## Validation Required

Run at least:

```powershell
python -m pytest tests/test_runtime_v0_service_preflight.py tests/test_routers_ike_v0.py <new narrow decision tests> -q
python -m compileall runtime routers tests
```

And one live local proof after service refresh.

## Delivery Requirements

Return:

1. `summary`
2. `files_changed`
3. `why_this_solution`
4. `validation_run`
5. `known_risks`
6. `recommendation`

Default recommendation target:

- `accept_with_changes`

unless the full narrow proof and idempotency semantics are clearly landed.
