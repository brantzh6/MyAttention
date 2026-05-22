# IKE Runtime v0 R2-E Surface Activation Plan

Date: 2026-04-08
Phase: `R2-E`

## Objective

Make the explicit runtime bootstrap/surface path directly usable from the
existing settings-facing surface while preserving runtime truth boundaries.

## Scope

- one narrow settings-surface activation path
- truthful runtime-visible state before and after activation
- no hidden auto-bootstrap on page load

## Non-Goals

- no broad UI/runtime redesign
- no generic project management UI
- no benchmark/runtime merge
- no notifications or graph-memory work

## Closure Standard

`R2-E` is complete when:

1. a bounded settings-surface activation path exists
2. it uses explicit runtime bootstrap truth
3. the visible runtime surface remains narrow and auditable
