# IKE Runtime v0 - R2-I15 Phase Judgment

Date: 2026-04-10
Phase: `R2-I15 Controller Decision Inspect Surface`
Status: `candidate next packet inside R2-I`

## Why This Packet Exists

`R2-I14` closed one narrow usability gap in preflight:

- the controller can now self-check current code freshness

But one controller-facing shape was still only implicit inside the raw
preflight payload:

- `controller_acceptability`
- `controller_promotion`
- especially `controller_confirmation_required`

That means the reviewed decision boundary still required controller-side field
interpretation instead of one explicit inspect surface.

## Intended Scope

If opened, `R2-I15` should answer one narrow question only:

- can the runtime expose one explicit controller-facing decision envelope above
  service preflight, while remaining inspect-only and non-mutating?

The target is not new promotion logic.
The target is clearer controller-visible decision shape.

## Explicit Non-Goals

- no acceptance mutation
- no persisted controller decision record
- no automatic promotion
- no service-manager work
- no scheduler semantics

## Expected Truth Boundary

If this packet lands correctly, the new surface should make the following
explicit:

- `inspect_only = true`
- `mutates_acceptance = false`
- `records_controller_decision = false`
- `implies_canonical_accepted = false`

## Controller Judgment

`R2-I15` is the correct next packet if the current goal is to expose the
controller decision edge more directly without widening runtime semantics.
