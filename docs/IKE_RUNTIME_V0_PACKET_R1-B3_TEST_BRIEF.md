# IKE Runtime v0 Packet R1-B3 Test Brief

## Task ID

`IKE-RUNTIME-R1-B3`

## Goal

Independently validate the first real runtime lifecycle proof.

## Required Scenarios

- lifecycle starts in `inbox`
- controller can move `inbox -> ready`
- legal claim path moves `ready -> active`
- work completion moves `active -> review_pending`
- controller review moves `review_pending -> done`
- event records reflect the same ordered path
- no illegal shortcut path is required

## Required Output

- scenarios_run
- commands_run
- pass_fail
- gaps_not_tested
- risks_remaining
- recommendation
