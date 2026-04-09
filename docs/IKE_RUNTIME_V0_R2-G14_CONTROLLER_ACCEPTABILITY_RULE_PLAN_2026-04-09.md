# IKE Runtime v0 - R2-G14 Controller Acceptability Rule Plan

Date: 2026-04-09
Phase: `R2-G Runtime Service Stability And Delegated Closure Hardening`

## Purpose

Turn the new machine-readable `controller_acceptability` signal into an explicit
controller usage rule.

## Current State

The system can now distinguish:

- raw service status
- preferred owner
- owner chain
- repo launcher
- code freshness
- controller acceptability

What is still not fixed:

- which combinations are acceptable for:
  - bounded live proof
  - canonical service proof
  - routine unattended proof

## Narrow Rule To Fix

Define controller policy for at least these cases:

### Case A

- `status = ready`
- `controller_acceptability = canonical_ready`

Interpretation:

- fully acceptable

### Case B

- `status = ambiguous`
- `controller_acceptability = bounded_live_proof_ready`

Interpretation candidate:

- acceptable for bounded alternate-port live proof
- not acceptable as canonical service proof

### Case C

- `status = ambiguous`
- `controller_acceptability = blocked_owner_mismatch`

Interpretation:

- not acceptable

### Case D

- `status = ambiguous`
- `controller_acceptability = blocked_code_freshness`

Interpretation:

- not acceptable

## Success Criteria

- one explicit controller rule note is written
- handoff no longer leaves `bounded_live_proof_ready` to implicit interpretation
- `R2-G` can be considered materially complete once the rule is fixed
