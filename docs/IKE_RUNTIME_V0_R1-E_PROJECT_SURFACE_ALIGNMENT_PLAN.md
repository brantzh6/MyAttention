# IKE Runtime v0 R1-E Project Surface Alignment Plan

## Purpose

`R1-E` is the narrow phase after materially complete `R1-D`.

Its job is to align project-level current-work visibility with the now-proven
runtime closure layer.

## Why This Phase Exists

The runtime kernel can now truthfully reconstruct and persist `WorkContext`.

The preserved gap is that project-level current-state visibility has not yet
been wired to that active context truth.

## Core Scope

### R1-E1 Coding

Goal:

- wire a narrow project-level pointer/update path to the active reconstructed
  `WorkContext`

Must prove:

- `RuntimeProject.current_work_context_id` reflects runtime truth
- no second project-level truth source is introduced

### R1-E2 Review

Goal:

- review project-surface alignment for hidden pointer drift

### R1-E3 Testing

Goal:

- add runtime-backed tests for:
  - project pointer update
  - reconstructed active context visibility
  - rejection of stale pointer drift

### R1-E4 Evolution

Goal:

- capture what `R1-E` proves about truthful controller-facing runtime
  visibility

## Boundaries

Allowed:

- narrow runtime helper/service updates
- narrow DB-backed tests
- project-pointer truth alignment

Not allowed:

- broad UI/API work
- notification/follow-up surfaces
- benchmark integration
- graph memory
- new runtime object families
