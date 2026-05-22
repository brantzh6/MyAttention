# IKE Runtime v0 Packet R1-C6 Test Brief

## Task ID

`IKE-RUNTIME-R1-C6`

## Goal

Restore DB-backed runtime test truth for the schema-foundation and related runtime suites.

## Why This Exists

Current truthful testing state:

- narrow runtime suites are green
- wide runtime sweep is partially blocked by missing `db_session` fixture/environment support

This is now a real testing-lane gap and should stop being mixed into semantic judgments.

## Scope

Allowed:

- narrow fixture/environment restoration for DB-backed runtime tests
- validation that wide runtime DB-backed tests can run meaningfully

Not allowed:

- schema redesign
- broad test-framework rewrite
- unrelated test cleanup outside runtime scope

## Acceptance Standard

1. DB-backed runtime suite has a real `db_session` path
2. wide runtime results are interpretable as acceptance evidence
3. fixture restoration does not silently change runtime semantics
