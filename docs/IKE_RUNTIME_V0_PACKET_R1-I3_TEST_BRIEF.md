# IKE Runtime v0 Packet R1-I3 Test Brief

## Task ID

- `R1-I3`

## Goal

Independently validate the `R1-I1` operational guardrails.

## Required focus

At minimum verify:

1. explicit alignment to archived/non-active context is rejected
2. no-active-context behavior is explicit and bounded
3. tightened trust checks still preserve valid reviewed-upstream closure flows
4. combined runtime truth-adjacent suites remain green

## Required output

- `scenarios_run`
- `pass_fail`
- `gaps_not_tested`
- `risks_remaining`
- `recommendation`
