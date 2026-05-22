# IKE Runtime v0 - R2-G14 Controller Acceptability Rule Result

Date: 2026-04-09
Phase: `R2-G Runtime Service Stability And Delegated Closure Hardening`

## Summary

The controller usage rule for runtime service preflight is now explicitly fixed.

This rule does not change the underlying machine-readable service truth.

It only defines how the controller should interpret:

- `status`
- `controller_acceptability.status`

together.

## Fixed Rule

### Case A

- `status = ready`
- `controller_acceptability = canonical_ready`

Controller interpretation:

- acceptable for canonical live proof
- acceptable for normal controller validation against the main service

### Case B

- `status = ambiguous`
- `controller_acceptability = bounded_live_proof_ready`

Controller interpretation:

- acceptable only for **bounded alternate-port live proof**
- acceptable only when:
  - scope is explicit
  - service is temporary
  - result is treated as bounded proof evidence
- **not** acceptable as canonical service proof
- **not** acceptable as routine unattended service baseline

### Case C

- `status = ambiguous`
- `controller_acceptability = blocked_owner_mismatch`

Controller interpretation:

- not acceptable

### Case D

- `status = ambiguous`
- `controller_acceptability = blocked_code_freshness`

Controller interpretation:

- not acceptable

### Case E

- `status = down`
- any controller_acceptability

Controller interpretation:

- not acceptable

## Why This Rule

Current evidence shows:

- fresh alternate-port services can now return the latest preflight schema
- code freshness can now be proven live
- repo launcher evidence can now be separated from interpreter ownership

So the controller no longer needs to reject all `ambiguous` cases equally.

At the same time, the canonical `8000` service still does not satisfy the
preferred owner rule, so broader acceptance would be dishonest.

This rule preserves both truths:

- bounded live proof can move
- canonical service proof still remains blocked

## Truthful Judgment

- `R2-G14 = accept`

## Controller Interpretation

`R2-G` now has:

- sufficient observability
- sufficient machine-readable state
- an explicit controller usage rule

The remaining unresolved issue is no longer runtime-phase ambiguity.

It is an environment / launch-path normalization problem for the canonical
service.
