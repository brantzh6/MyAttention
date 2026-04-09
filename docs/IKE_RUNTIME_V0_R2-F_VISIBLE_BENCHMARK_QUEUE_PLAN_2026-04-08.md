# IKE Runtime v0 R2-F Visible Benchmark Queue Plan

## Goal

Add one narrow visible-surface action that imports the current reviewed benchmark candidate into runtime as a `pending_review` packet.

## Scope

- backend runtime import endpoint
- bounded router tests
- bounded benchmark-bridge tests
- settings-surface action button
- bounded status/error feedback

## Out Of Scope

- auto bootstrap
- auto import on page load
- auto acceptance
- broad task board
- broader benchmark/runtime fusion

## Success Criteria

- route exists and is tested
- import requires an existing runtime project
- imported packet status is `pending_review`
- frontend compiles
- settings surface exposes one explicit action

## Truth Rule

Imported benchmark candidates remain reviewable runtime packets, not trusted memory.
