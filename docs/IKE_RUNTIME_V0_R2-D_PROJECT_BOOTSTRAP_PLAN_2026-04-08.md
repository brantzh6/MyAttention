# IKE Runtime v0 R2-D Project Bootstrap Plan

Date: 2026-04-08
Phase: `R2-D`

## Objective

Establish one truthful bootstrap path that ensures the runtime-visible surface
can resolve a real runtime project in the active DB.

## Scope

- choose one narrow bootstrap source for `RuntimeProject` presence
- keep bootstrap explicit and auditable
- preserve runtime truth ownership

## Non-Goals

- no broad UI integration
- no benchmark/runtime merge
- no knowledge-base backfill project synthesis
- no generic project sync engine

## Closure Standard

`R2-D` is complete when:

1. one runtime project bootstrap path is implemented
2. live runtime surface can resolve a truthful project instead of only `404`
3. the path stays explicit, narrow, and auditable
