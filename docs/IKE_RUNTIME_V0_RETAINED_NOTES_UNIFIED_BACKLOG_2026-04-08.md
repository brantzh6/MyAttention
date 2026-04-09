# IKE Runtime v0 Retained Notes Unified Backlog

## Purpose

This file closes the long-running review complaint that important retained
runtime notes were scattered across milestone docs and review files without one
unified backlog surface.

It does **not** mean every item is active now.
It means every important retained runtime note now has one durable home.

## Status Buckets

- `close_now`
- `next_gate`
- `deferred_but_committed`
- `watch`

## Close Now

### 1. `force=True` closure accounting

Status:

- `close_now`

Current truth:

- runtime code already enforces:
  - `force=True` requires explicit role
  - `force=True` is restricted to `controller` / `runtime`
- remaining gap was closure discipline, not missing runtime enforcement

Closure target:

- durably mark this item as closed for the original first-wave review demand

Primary references:

- [D:\code\MyAttention\services\api\runtime\transitions.py](/D:/code/MyAttention/services/api/runtime/transitions.py)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_FIRST_WAVE_RESULT_MILESTONE_2026-04-05.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_FIRST_WAVE_RESULT_MILESTONE_2026-04-05.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-A_REVIEW_SYNTHESIS_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-A_REVIEW_SYNTHESIS_2026-04-08.md)

### 2. `R1-J` repeated-green rule formalization

Status:

- `close_now`

Current truth:

- `R1-J` already established the narrow stability closure rule in a result
  milestone
- the remaining gap is making that rule easy to find and reuse

Closure target:

- formally record the rule as a reusable runtime method rule

Primary references:

- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R1-J_RESULT_MILESTONE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R1-J_RESULT_MILESTONE_2026-04-08.md)

## Next Gate

### 3. First real task lifecycle proof

Status:

- `next_gate`

Why it matters:

- runtime still needs one narrow, truthful inbox-to-done task proof to support
  the next integration gate

Why not now:

- `R2-A` is still settling closure discipline and readiness judgment

### 4. Kernel to benchmark narrow connection

Status:

- `next_gate`

Why it matters:

- runtime kernel should eventually accept benchmark output as structured task
  input

Why not now:

- readiness judgment should complete first

## Deferred But Committed

### 5. Second concept benchmark scheduling

Status:

- `deferred_but_committed`

Why it matters:

- `harness` alone cannot prove benchmark method generalization

Required next step:

- after `R2-A`, this must receive a formal planned phase/schedule

### 6. Procedural memory evolution scheduling

Status:

- `deferred_but_committed`

Why it matters:

- typed/procedural memory remains strategically necessary

Required next step:

- after `R2-A`, this must receive a formal planned phase/schedule

## Watch

### 7. Read-path trust enforcement below helper level

Status:

- `watch`

Why it matters:

- current read-path trust semantics are helper-level
- future broader read surfaces must not bypass them

Why not now:

- this is a valid future hardening direction, but not an immediate speculative
  schema/platform change inside `R2-A`
