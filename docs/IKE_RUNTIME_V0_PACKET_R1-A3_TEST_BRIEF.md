# IKE Runtime v0 Packet R1-A3 Test Brief

## Task ID

- `R1-A3`

## Goal

Independently validate the `R1-A1` hardening changes.

## Validation Level

- Level 2 minimum

## Required Scenarios

### Migration Validation

- upgrade path succeeds
- downgrade/rollback path succeeds where defined

### Claim Gate Validation

- legal claim path succeeds
- illegal claim path fails

### Memory Trust Validation

- linkage-only fake path fails
- upstream-existing valid path succeeds

### Force-Path Restriction

- unauthorized force-path fails
- authorized restricted path behaves as defined

## Required Output

1. scenarios_run
2. commands_run
3. pass_fail
4. gaps_not_tested
5. risks_remaining
6. recommendation

## Stop Conditions

Stop and report if the packet cannot prove these scenarios independently.
