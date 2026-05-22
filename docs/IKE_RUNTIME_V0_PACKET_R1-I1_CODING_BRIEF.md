# IKE Runtime v0 Packet R1-I1 Coding Brief

## Task ID

- `R1-I1`

## Goal

Implement the narrow operational guardrails identified after `R1-H`.

## Required focus

1. Reject explicit project-pointer alignment to archived/non-active
   `RuntimeWorkContext`
2. Make no-active-context helper failure explicit and bounded
3. Tighten closure/trust checks where existence-only verification is too weak
4. Stay inside existing runtime helper/test surfaces

## Required output

- `summary`
- `files_changed`
- `validation_run`
- `known_risks`
- `recommendation`
