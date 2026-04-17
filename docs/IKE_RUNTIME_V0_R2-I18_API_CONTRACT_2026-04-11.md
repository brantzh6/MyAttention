# IKE Runtime v0 - R2-I18 API Contract

Date: 2026-04-11
Phase: `R2-I18 Controller Acceptance Record Boundary`
Status: `draft contract`

## Purpose

Define the narrow API contract for recording and inspecting one durable
controller acceptance decision above the current
`controller_confirmation_required` runtime state.

## Design Rule

There must be two clearly separate surfaces:

1. inspect
   - read-only
   - no hidden writes
2. record
   - explicit controller action
   - bounded write

## Route 1 - Inspect Current Acceptance Record

### Path

- `POST /api/ike/v0/runtime/service-preflight/controller-decision/record/inspect`

### Why `POST`

Keep request shape parallel to current runtime inspect patterns and allow a
bounded request body without pretending this is a durable REST resource API.

### Request Shape

```json
{
  "host": "127.0.0.1",
  "port": 8000,
  "self_check_current_code": true,
  "strict_code_freshness": true
}
```

All fields may reuse the current preflight request shape.

### Response Shape

```json
{
  "ref": {
    "id": "runtime_controller_acceptance_record_inspect:...",
    "kind": "runtime_controller_acceptance_record_inspect",
    "id_scope": "provisional",
    "stability": "experimental",
    "permalink": null
  },
  "data": {
    "status": "ready",
    "current_preflight": {},
    "decision_record": {
      "exists": false,
      "decision_id": null,
      "decision_scope": "canonical_service_acceptance",
      "outcome": null,
      "status": null,
      "basis": null,
      "target_status": null,
      "finalized_at": null,
      "supersedes_decision_id": null
    },
    "truth_boundary": {
      "inspect_only": true,
      "mutates_acceptance": false,
      "records_controller_decision": false,
      "implies_canonical_accepted": false
    }
  }
}
```

### Inspect Rules

1. must re-evaluate current preflight truth
2. must read the latest finalized decision for scope
   `canonical_service_acceptance`
3. must not create or update any row
4. if no record exists, return `exists = false`

## Route 2 - Record Controller Acceptance

### Path

- `POST /api/ike/v0/runtime/service-preflight/controller-decision/record`

### Request Shape

```json
{
  "host": "127.0.0.1",
  "port": 8000,
  "self_check_current_code": true,
  "strict_code_freshness": true,
  "controller_id": "controller-001",
  "summary": "Accept current Windows redirector canonical local proof baseline",
  "rationale": "Reviewed Windows redirector shape is promotion-eligible and confirmed by controller"
}
```

### Required Fields

- `controller_id`

### Optional Fields

- `summary`
- `rationale`

If omitted, summary/rationale may be generated from the bounded current
preflight basis, but must remain narrow and mechanical.

### Record Preconditions

The record route may proceed only if current preflight truth says:

- `controller_promotion.status = controller_confirmation_required`

Otherwise the route must reject the write.

### Response Shape

```json
{
  "ref": {
    "id": "runtime_controller_acceptance_record:...",
    "kind": "runtime_controller_acceptance_record",
    "id_scope": "provisional",
    "stability": "experimental",
    "permalink": null
  },
  "data": {
    "recorded": true,
    "decision_id": "...",
    "decision_scope": "canonical_service_acceptance",
    "outcome": "adopt",
    "status": "final",
    "target_status": "canonical_accepted",
    "basis": "windows_venv_redirector_v1",
    "work_context_updated": true,
    "event_recorded": true,
    "truth_boundary": {
      "inspect_only": false,
      "mutates_acceptance": true,
      "records_controller_decision": true,
      "implies_canonical_accepted": false
    }
  }
}
```

### Important Honesty Rule

Even after the record route succeeds, it still must **not** claim that runtime
has a complete approval workflow. It only claims one narrow durable acceptance
record for one scope.

## Canonical Persistence Shape

### RuntimeDecision

- `decision_scope = canonical_service_acceptance`
- `outcome = adopt`
- `status = final`
- `created_by_kind = controller`
- `created_by_id = <controller_id>`
- `metadata` includes:
  - `host`
  - `port`
  - `controller_acceptability`
  - `controller_promotion`
  - `target_status`
  - `launch_mode`

### RuntimeTaskEvent

- `event_type = controller_acceptance_recorded`
- `triggered_by_kind = controller`
- `triggered_by_id = <controller_id>`
- payload includes:
  - `decision_id`
  - `decision_scope`
  - `target_status`
  - `basis`

### RuntimeWorkContext

- update `latest_decision_id`

## Rejection Cases

The record route must fail clearly for:

1. missing `controller_id`
2. current preflight not in `controller_confirmation_required`
3. ambiguous live port ownership
4. current code freshness mismatch under strict self-check

## Recommendation

Implement this contract narrowly and do not add generic decision CRUD as part
of the same packet.
