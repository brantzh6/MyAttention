# Flywheel V1 Worker Brief: Real Result for Execution-Feedback Inspect (P0)

Date: 2026-05-18
Lane: delegated worker (manual)
SDLC stage: Execution -> Result (inspect-only)
Risk: R2
Truth status: non-canonical / inspect-only

## Objective

Take a *copied* Flywheel V1 delegate handoff packet (provided separately by the controller) and produce a **real** worker result artifact that can be fed into **execution-feedback inspect**.

Hard boundaries:

- No automatic execution.
- No persistence/runtime truth expansion.
- No self-acceptance as final; you provide a recommendation only.

## Inputs

You will receive exactly one markdown handoff packet from the controller.

## Output (required schema)

Return one markdown result with these exact top-level sections:

- `summary`
- `files_changed` (may be empty)
- `why_this_solution`
- `validation_run` (may be empty)
- `known_risks`
- `recommendation`: `accept` | `accept_with_changes` | `reject`
- `stop_condition`

## Work Rules

- Stay within the handoff packet's allowed scope and write policy.
- If any required context is missing or instructions are ambiguous, **stop** and report what is missing (do not invent behavior).
- Prefer the smallest safe change that meets the objective.
- Keep the result copy-ready (ASCII-safe if possible).

## Stop Condition

Stop after delivering the result artifact only. Do not proceed into follow-up implementation unless the controller explicitly dispatches a new packet.
