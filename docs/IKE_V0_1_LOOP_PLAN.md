# IKE v0.1 Loop Plan

This document defines the next milestone after the current IKE v0 migration
seam:

- not more isolated preview endpoints
- not premature durable object retrieval
- but one real inspectable loop running on top of current substrates

## 1. Goal

Prove exactly one narrow, inspectable, runtime-backed IKE loop:

`Observation -> Entity/Claim -> ResearchTask -> Experiment -> Decision -> HarnessCase`

The purpose of v0.1 is to move the project from:

- "contracts and transitional APIs exist"

to:

- "one real IKE loop can run and be inspected honestly"

This loop proof is necessary, but not sufficient.

The next visible milestone must eventually be judged against a real-world
benchmark, not just internal inspectability. See:

- `docs/IKE_REAL_WORLD_BENCHMARKS.md`
- `docs/IKE_B1_HARNESS_BENCHMARK_PLAN.md`

## 2. Why This Is The Next Milestone

Three review sources converged on the same judgment:

1. The current milestone is architecturally sound as a migration seam.
2. The transitional API choice is correct.
3. The main remaining gap is not more schema work, but a real inspectable loop.

Therefore the next milestone must prove runtime truth, not add more surface area.

Current accepted packet status:

- `L1` shared-envelope deduplication
- `L2` research-task substrate wiring
- `L3` experiment runtime wiring
- `L4` chain artifact + inspect surface
- `L5` harness loop validation

The next remaining gap is controller-supervised end-to-end loop composition,
not more isolated schema or preview work.

## 3. Scope

### In Scope

1. One real loop starting from a trusted existing substrate.
2. Real mapping into:
   - Observation
   - Entity/Claim
   - ResearchTask
   - Experiment
   - Decision
   - HarnessCase
3. One inspectable chain artifact or chain view.
4. At least one harness assertion proving the loop is complete.

### Out Of Scope

1. Stable `GET /{type}/{id}` retrieval.
2. Canonical durable object store.
3. Full object-access subsystem.
4. Broad new UI surface area.
5. Large repo restructuring.

## 4. Recommended Starter Slice

Start from an already trusted runtime substrate:

- source-intelligence observation
  or
- evolution-detected quality issue

These are better starters than chat because:

- they already exist in the system
- they already carry provenance
- they already participate in real operational workflows

## 5. Required Deliverables

### 5.1 Runtime-backed Mapping Path

At least one current substrate must produce:

- an Observation
- then a derived Entity and/or Claim
- then a ResearchTask
- then an Experiment stub
- then a Decision
- then a HarnessCase

### 5.2 Inspectable Chain

The full chain must be inspectable through a stable surface such as:

- one chain artifact
- one chain inspection endpoint
- or one thin workspace/inspect page

The user or operator must not need raw log inspection to understand the loop.

### 5.3 Harness Assertion

At least one HarnessCase must verify:

- the loop exists
- the references are present
- the chain is not truncated

### 5.4 Provenance Preservation

Across the loop, the following must stay visible:

- source references
- object refs
- timestamps
- confidence
- provenance

## 6. API Direction

v0.1 must preserve the current transitional API stance:

- use `preview / inspect / generate / derive` style surfaces
- do not add durable-looking `GET /{id}` retrieval

Returned objects must continue to expose provisional lifecycle metadata.

## 7. Minimal Internal Runtime Need

v0.1 may require a small internal seam for cross-step object passing, but it
must remain internal and transitional.

Allowed:

- session-scoped chain assembly
- chain artifact records
- task artifact linkage

Not yet allowed:

- public stable object retrieval
- pretending a canonical persistent store already exists

## 8. Controller Rules For v0.1

1. If semantic drift is found, correct it immediately.
2. Do not broaden scope into a general object platform.
3. Do not add durable retrieval shortcuts.
4. Prefer one truthful vertical slice over many incomplete APIs.

## 9. Suggested Work Order

1. Shared-envelope deduplication if still needed.
2. Real ResearchTask / Experiment mapping onto current substrates.
3. Chain artifact or inspect surface.
4. HarnessCase validation of the chain.
5. Thin UI inspection surface if needed for human validation.
6. Reframe the next visible milestone around a real-world benchmark rather
   than a pure technical inspect surface.

## 10. Success Condition

v0.1 is complete when:

1. one real loop runs on the current system
2. the chain is inspectable end to end
3. no fake durability promise is introduced
4. the loop can be validated without raw log reading

That is the first true IKE proof point.

But it is still only an internal proof point.
The next milestone after v0.1 should prove user-understandable value on at
least one real-world benchmark case.
