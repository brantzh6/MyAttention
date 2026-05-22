# IKE Runtime v0 - R2-I18 Idempotency Policy

Date: 2026-04-11
Phase: `R2-I18 Controller Acceptance Record Boundary`
Status: `draft policy`

## Problem

Once controller acceptance can be recorded durably, repeated confirmation
requests must not create ambiguous truth.

The system needs one explicit policy for:

- same basis repeated
- changed basis repeated
- stale/non-eligible repeated

## Core Rule

There must never be multiple simultaneously current acceptance records for the
same narrow scope without an explicit supersession chain.

Scope in this packet:

- `canonical_service_acceptance`

## Case 1 - Same Basis, Same Target, Same Live Shape

If the latest finalized decision already matches:

- same `decision_scope`
- same `basis`
- same `target_status`
- same live launch mode / host / port

Then repeated record requests should be:

- `recorded = false`
- `idempotent_reuse = true`

No new decision row should be created.
No new event should be created.

## Case 2 - Same Scope, Different Basis Or Different Live Shape

If current live truth is eligible but differs materially from the latest
finalized decision, then the new decision may be recorded only by explicit
supersession:

- create new finalized decision row
- set `supersedes_decision_id`
- append one new controller acceptance event

This keeps the audit trail clear and avoids silent overwrites.

## Case 3 - Current Live Truth No Longer Eligible

If current preflight truth is not:

- `controller_confirmation_required`

then the record route must reject the request.

It must not:

- silently reuse a stale prior decision
- silently create a new decision
- silently downgrade anything

## Case 4 - Missing Controller Identity

Reject.

The write path requires explicit controller identity.

## Preferred Response Signals

### Idempotent Reuse

```json
{
  "recorded": false,
  "idempotent_reuse": true,
  "decision_id": "...",
  "superseded": false
}
```

### New Superseding Record

```json
{
  "recorded": true,
  "idempotent_reuse": false,
  "decision_id": "...",
  "superseded": true,
  "supersedes_decision_id": "..."
}
```

### Rejected

```json
{
  "recorded": false,
  "rejected": true,
  "reason": "not_confirmation_eligible"
}
```

## Why This Policy Fits The Mainline

This policy stays narrow because it does not create:

- multi-review workflows
- pending approval queues
- complex actor arbitration

It only protects canonical truth from ambiguity.

## Recommendation

`R2-I18` should implement:

1. idempotent reuse for same live basis
2. explicit supersession for materially changed eligible basis
3. explicit rejection for non-eligible current truth
