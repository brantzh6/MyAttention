# IKE Runtime v0 R1-H Delegated Evidence Recovery Plan

## Purpose

`R1-H` is a narrow quality-loop hardening phase.

It does not change runtime truth semantics.
It improves the confidence and auditability of the runtime second-wave by
recovering independent delegated evidence where recent phases still rely mainly
on controller fallback.

## Target Problem

Recent phases such as `R1-D`, `R1-E`, `R1-F`, and `R1-G` are materially
complete, but plain `accept` is still blocked by missing or unstable delegated:

- review
- testing
- evolution

evidence.

That gap should be tightened before the runtime platform grows wider.

## Phase Goal

Make the recent runtime phases rest on:

- real coding results
- real controller validation
- durable delegated review/testing/evolution evidence

with controller fallback preserved as backup, not as the primary proof path.

## Narrow Inclusions

1. identify the recent runtime phases whose final judgments are still mainly
   backed by fallback review records
2. rerun or normalize bounded delegated review/testing/evolution packets for
   those phases
3. update milestone docs so they distinguish:
   - delegated evidence recovered
   - fallback still in use
4. preserve any transport/provider instability as process findings, not runtime
   semantic findings

## Exclusions

`R1-H` must not:

- create new runtime DB objects
- change task/decision/memory truth rules
- widen project/controller read surfaces
- open benchmark or UI work
- treat chat-only results as durable evidence

## Initial Focus

Start with the recent phases that are already materially complete but still
explicitly recorded as:

- `materially complete with fallback review coverage`

Priority order:

1. `R1-G`
2. `R1-F`
3. `R1-E`
4. `R1-D`

## Success Criteria

`R1-H` is successful if:

1. at least the most recent runtime phase (`R1-G`) has durable delegated
   review/testing/evolution evidence recovered or truthfully marked as still
   unavailable after rerun
2. the project has one clear durable rule for when controller fallback remains
   acceptable and when it must be retried
3. active mainline docs no longer blur delegated evidence and fallback evidence

## Deliverables

- bounded delegated packet reruns or normalized result recovery
- updated phase milestone docs
- controller review note for what was recovered and what remains fallback-only
