# IKE Runtime v0 - R2-I Plan

Date: 2026-04-10
Phase: `R2-I First Real Task Lifecycle On Canonical Service`
Status: `candidate, gated on R2-H controller acceptance`

## Goal

Prove one real runtime task lifecycle on top of the now-reviewed canonical
service baseline, without widening runtime scope.

## Why This Phase Exists

Earlier `R2-B` proved that the hardened runtime kernel can carry one truthful
task lifecycle at the helper/test level.

What is still not durably proven is narrower and more operational:

- the current canonical local service path
- on the reviewed Windows redirector shape
- can support one real runtime task lifecycle above the live runtime baseline

## Target Question

Can the current canonical service baseline host one truthful lifecycle proof
without introducing:

- new truth sources
- broad new service-management APIs
- broad UI/runtime expansion

## Proposed Narrow Shape

`R2-I` should prefer a narrow inspect/trigger proof surface rather than broad
task orchestration.

Preferred shape:

1. use existing runtime task-lifecycle proof logic as the kernel baseline
2. add the thinnest live-service-adjacent execution surface needed for one
   auditable proof
3. keep output provisional / inspect-style / audit-oriented
4. avoid implying general task execution or scheduler semantics

## Expected Deliverable Types

- one narrow coding packet
- one review packet
- one testing packet
- one evolution/controller packet

## Likely Acceptance Questions

1. does the lifecycle proof remain runtime-truth-owned?
2. does the proof stay narrow and auditable?
3. does the live service surface avoid becoming a premature task runner API?
4. can current project/runtime read surfaces reflect the proof outcome without
   inventing shadow state?

## Explicit Non-Goals

- no general task execution API
- no multi-task queue or scheduler
- no broad delegate runtime integration
- no broad memory-system expansion
- no broad UI redesign
- no benchmark/runtime merge reopening
