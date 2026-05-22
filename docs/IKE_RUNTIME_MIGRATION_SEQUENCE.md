# IKE Runtime Migration Sequence

## Purpose

This document defines the practical migration order for turning the current MyAttention runtime into the first implementable IKE runtime.

It is not a greenfield repo plan.
It is the execution bridge between:

- `docs/ike_master_delivery/*`
- `docs/IKE_MIGRATION_ALIGNMENT.md`
- `docs/IKE_V0_EXECUTION_PLAN.md`
- `docs/IKE_SHARED_OBJECTS_V0.md`

## Core Decision

The runtime migration strategy is:

- keep the current monorepo and running skeleton;
- do not rewrite repo structure first;
- add IKE-aligned contracts and services inside the current codebase;
- migrate by vertical slice, not by folder-tree purity.

Additional runtime rule:

- keep external interfaces honest about current runtime capability;
- do not expose durable-looking object retrieval before a real canonical storage/retrieval path exists.

This means:

- keep `services/api`
- keep `services/web`
- keep PostgreSQL / Redis / Qdrant / object-storage assumptions
- introduce IKE shared objects and service seams before any large repo move

## What To Reuse As-Is

Preserve and build around:

- `services/api` as the first application runtime
- `services/web` as the first human-facing console/runtime
- existing FastAPI router shell
- existing worker-ish runtime helpers and scheduler loops
- PostgreSQL, Redis, Qdrant, object-storage direction
- current feed/source/task/control-plane foundations

The rule is:

`preserve running skeletons, refactor inward`

## What Not To Do First

Do not start migration with:

- repo-wide `apps/` and `packages/` re-layout
- microservice extraction
- large router rewrites
- a complete console redesign
- full graph database introduction
- full model portfolio governance

These are target-state concerns, not first-slice requirements.

## First Runtime Target

The first runtime target remains the v0 loop:

`Observation -> Entity/Claim -> ResearchTask -> Experiment -> Decision -> HarnessCase`

The runtime migration succeeds only if this loop can run on the current stack with explicit objects and inspectable artifacts.

The migration is not considered proven merely because schemas and preview
routes exist. A slice is only truly proven when the loop becomes inspectable in
the running system.

Reference:

- `docs/IKE_MIGRATION_EXIT_CRITERIA.md`

## Recommended Migration Order

### Stage 0. Freeze the current shape

Before deeper implementation work:

- keep current repo structure stable
- avoid broad moves/renames
- stop adding new behavior directly into routers where possible
- keep new IKE work additive and bounded

This stage is about drift control, not feature growth.

### Stage 1. Introduce shared object contracts

First add explicit object contracts for:

- `Source`
- `Observation`
- `Entity`
- `Claim`
- `ResearchTask`
- `Experiment`
- `Decision`
- `HarnessCase`

Notes:

- `Source` is required at the Information Brain boundary even if it is not the center of the first v0 loop.
- `HarnessCase` remains the primary v0 evaluation object.
- if an implementation also needs a runtime `HarnessRun`, treat it as the execution record around the case, not as a replacement for the case contract.

Implementation guidance:

- first add schemas and typed payload shapes
- then map current runtime objects onto them
- do not wait for perfect storage purity

### Stage 2. Add thin service seams

Inside the current backend, add or formalize these service seams:

- `schemas/`
- `objects/`
- `workflow/`
- `governance/`

This does not require a repo-wide restructure yet.
It only requires that new contracts stop living implicitly inside routers and ad hoc payloads.

Suggested first placement:

- under `services/api/` if that is the lowest-risk path

The goal is:

- stable contracts first
- cleaner service boundaries second
- repo relocation later if still justified

### Stage 3. Expose the minimum API surface

The first IKE-facing API surface should stay small.

Recommended first direction:

- transitional operation endpoints
- not canonical object-resource endpoints

Examples:

- submit or register an `Observation`
- extract or preview `Entity` / `Claim` outputs from an observation
- generate or open a `ResearchTask`
- create or inspect an `Experiment`
- record a `Decision`
- inspect a `HarnessCase`

Important constraint:

- do not try to expose the whole future IKE API surface in v0
- make only the loop inspectable
- do not promise stable `GET by id` semantics before the store/retrieval layer is real

Reference:

- `docs/IKE_API_TRANSITION_PRINCIPLES.md`

### Stage 4. Build the minimum UI surface

The first UI should also stay narrow.

Recommended minimum UI slices:

- a thin workspace shell
- a task board or active task surface
- an entity/claim inspection view
- a decision review view

Not recommended for v0:

- a large paradigm library UI
- full governance console breadth
- a broad multi-workspace product surface

The workspace should be treated as a lightweight container, not a large product program.

### Stage 5. Add the minimum harness

The first harness should validate the loop, not the whole system.

It should answer:

- did one observation enter the loop
- did explicit objects get created
- are artifact refs traceable
- can the task, experiment, decision, and harness record be reconstructed without raw logs

This is the first real proof that IKE is becoming operational.

## Runtime Mapping Guidance

### Information Brain mapping

Current likely substrate:

- `feeds/`
- `routers/feeds.py`
- raw ingest and feed item persistence
- source plans and source-plan versions

Migration rule:

- keep information ingestion running
- gradually expose `Source` and `Observation` as first-class IKE objects

### Knowledge Brain mapping

Current likely substrate:

- `knowledge/`
- `rag/`
- memory-linked retrieval helpers

Migration rule:

- do not confuse retrieval with the whole Knowledge Brain
- first expose `Entity` and `Claim`
- relation-heavy expansion can come later

### Evolution Brain mapping

Current likely substrate:

- `routers/evolution.py`
- `routers/testing.py`
- task/context/artifact/history runtime

Migration rule:

- keep watchdog and health checks alive
- but begin shifting the meaningful outputs toward:
  - `ResearchTask`
  - `Experiment`
  - `Decision`
  - `HarnessCase`

## Suggested First Concrete Slice

The best first slice is still:

- a source-intelligence observation
- or an evolution-detected source-quality issue

Why:

- it already exists in runtime form
- it already touches Information and Evolution
- it naturally leads to a research task and an experiment stub

This is stronger than starting from chat or a broad UI rewrite.

## What To Accept From External Suggestions

The following suggestions are good and should be adopted:

1. keep the current repo and runtime shape
2. add schemas and governance-related structure before major rewrites
3. define core objects early
4. build the smallest possible API loop
5. build the smallest possible UI loop
6. add a minimal harness that proves traceability

## What To Modify From External Suggestions

Two refinements are required:

1. `Source` should be included as a first-class information object, but it should not displace the v0 loop center of gravity away from `Observation -> ... -> HarnessCase`.

2. `workspace` should remain a thin shell in v0.
   It should not become a broad product redesign before the object and workflow loop is stable.

## Definition of Success

This migration sequence is working if:

1. the codebase keeps running during migration
2. new IKE contracts become explicit without a rewrite
3. the first vertical loop is real and inspectable
4. routers become thinner over time instead of fatter
5. new work is guided by shared objects, workflow state, and harness evidence rather than by ad hoc feature additions
6. transitional APIs do not overpromise persistence or retrieval guarantees
