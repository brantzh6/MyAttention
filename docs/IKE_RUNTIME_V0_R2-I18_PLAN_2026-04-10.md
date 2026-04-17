# IKE Runtime v0 - R2-I18 Plan

Date: 2026-04-10
Phase: `R2-I18 Controller Acceptance Record Boundary`
Status: `planned`

## Objective

Add one narrow durable controller-acceptance record boundary above the current
live `controller_confirmation_required` inspect state, without widening runtime
into a workflow engine.

## Why This Plan Is Narrow

This plan does **not** try to solve:

- general approval workflows
- multi-review routing
- detached execution control
- scheduler semantics

It only asks:

- can one reviewed controller action be durably recorded in canonical runtime
  truth so acceptance is no longer only inferred from inspect evidence?

## Existing Canonical Landing Points

The current schema already provides the right narrow landing points:

1. `runtime_decisions`
   - durable decision state already exists
   - suitable for one explicit controller-reviewed acceptance record
2. `runtime_work_contexts.latest_decision_id`
   - allows the current work surface to reflect the latest acceptance decision
3. `runtime_task_events`
   - suitable for one append-only audit event describing the controller action

This means `R2-I18` should prefer reuse over introducing new tables.

## Proposed Narrow Outcome

If implemented, the packet should produce one bounded capability:

- record a controller acceptance decision for the current canonical local
  Windows proof shape

Minimum truthful outputs:

- one `runtime_decisions` row with scope such as
  `canonical_service_acceptance`
- one linked runtime audit event indicating controller confirmation occurred
- one inspect/read surface that can expose:
  - acceptance exists
  - basis
  - target status
  - created/finalized by whom
  - whether it supersedes a prior decision

## Preferred Shape

### Decision Record

Use `runtime_decisions` with a narrow scoped record:

- `decision_scope = canonical_service_acceptance`
- `title` describing the canonical local Windows acceptance
- `summary` and `rationale` tied to the reviewed rule
- `outcome = adopt`
- `status = final`
- `created_by_kind = controller`
- `created_by_id = controller-...`
- `metadata` carrying:
  - `controller_acceptability`
  - `controller_promotion`
  - `decision_basis`
  - `launch_mode`
  - `host`
  - `port`

### Audit Event

Persist one append-only runtime event rather than mutating hidden state only.

Candidate shape:

- `event_type = controller_acceptance_recorded`
- payload includes:
  - `decision_id`
  - `decision_scope`
  - `accepted_status`
  - `basis`

### Work Context Reflection

If a decision is recorded, the current runtime work context may reflect it via:

- `latest_decision_id`

This remains derived/read-surface alignment, not a second truth source.

## Suggested Surface

Prefer one narrow inspect/action pair rather than a broad decisions API.

Candidate bounded addition:

1. inspect route:
   - inspect current acceptance record state
2. record route:
   - explicit controller action
   - bounded to the current canonical local service acceptance use case

The action route must remain explicit and honest:

- no implicit auto-accept
- no background mutation
- no hidden write during inspect

## Validation Target

Minimum required validation if this packet opens:

1. focused DB-backed tests proving one decision record can be written
2. focused tests proving one audit event is appended
3. focused tests proving inspect remains read-only
4. live local proof that:
   - decision record can be created once
   - latest decision becomes inspectable
   - repeated creation does not silently fork ambiguous active truth

## Key Risks

1. over-widening into a generic approval subsystem
2. creating acceptance truth in two places
3. letting inspect and mutate semantics blur together
4. failing to define supersession/idempotency for repeated confirmations

## Preferred Guardrails

1. one narrow decision scope only
2. explicit controller actor required
3. inspect and mutate surfaces separated
4. repeated confirm should supersede or no-op explicitly, never duplicate
   ambiguous live truth
5. work-context reflection must remain derived from canonical decision truth

## Recommendation

- `R2-I18` should be implemented only as a narrow decision-record packet
- reuse `runtime_decisions`, `runtime_task_events`, and
  `runtime_work_contexts.latest_decision_id`
- do not introduce a new approval framework
