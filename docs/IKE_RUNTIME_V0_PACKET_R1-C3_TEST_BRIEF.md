# IKE Runtime v0 Packet R1-C3 Test Brief

## Task ID

- `R1-C3`

## Goal

Independently validate the `R1-C1` truth-layer hardening.

## Required focus

At minimum verify:

1. legal lifecycle proof path still passes
2. illegal delegate claim path fails
3. controller-only `review_pending -> done` still holds
4. event history remains coherent for the proof path

## Required output

- `scenarios_run`
- `pass_fail`
- `gaps_not_tested`
- `risks_remaining`
- `recommendation`
