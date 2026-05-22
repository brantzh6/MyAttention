# IKE Runtime v0 Packet R2-G2 Coding Brief

## Task ID

- `R2-G2`

## Goal

Implement one narrow, truthful service-preflight helper for runtime live proof.

## Problem

Current live proof can be polluted by duplicate local API launchers:
- repo `.venv` Python
- system `Python312`

The immediate need is not a new runtime truth feature.

The need is a small operational helper that can tell the controller whether the
local API surface is safe to use for live proof.

## Intended Scope

- inspect local API health and port ownership
- report whether live proof is:
  - `ready`
  - `ambiguous`
  - `down`
- keep the output machine-readable and controller-friendly

## Constraints

- no new runtime truth semantics
- no broad service supervisor
- no daemon/job manager
- no automatic kill-or-restart policy
- no UI work
- no benchmark/runtime changes

## Allowed Files

- `services/api/runtime/*`
- `services/api/tests/*`
- narrow supporting imports only if required

## Required Output

1. `summary`
2. `files_changed`
3. `validation_run`
4. `known_risks`
5. `recommendation`
