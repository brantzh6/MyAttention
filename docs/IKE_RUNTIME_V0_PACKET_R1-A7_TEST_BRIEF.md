# IKE Runtime v0 Packet R1-A7 Test Brief

## Task ID

`IKE-RUNTIME-R1-A7`

## Goal

Independently validate the `R1-A5` enforcement hardening.

## Required Scenarios

- `role=None` no longer acts as a silent force bypass
- unauthorized `force=True` still fails
- privileged force path still works only for allowed roles
- fake or omitted verifier path does not get treated as trustworthy by mistake
- claim-path regression checks still pass
- migration-validation support still runs from a stable invocation pattern

## Required Output

- scenarios_run
- commands_run
- pass_fail
- gaps_not_tested
- risks_remaining
- recommendation
