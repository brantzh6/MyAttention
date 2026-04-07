# IKE v0 Delegation Backlog

## Purpose

This document converts the IKE v0 implementation slices into a delegation-ready backlog.

It is not a generic roadmap.
It is a bounded-task source for qoder, openclaw, or any other delegated implementation agent.

Use together with:

- `docs/IKE_V0_IMPLEMENTATION_SLICES.md`
- `docs/DELEGATION_BRIEF_TEMPLATE.md`
- `docs/CONTROLLED_DELEGATION_STRATEGY.md`
- `AGENTS.md`

## Delegation Rules For This Backlog

All tasks in this file follow these assumptions:

- main controller keeps architecture and acceptance control
- implementation is delegated by default
- every task must stay bounded
- every task must return auditable output

Default required return:

1. `summary`
2. `files_changed`
3. `why_this_solution`
4. `validation_run`
5. `known_risks`
6. `recommendation`

## Backlog Structure

Tasks are grouped into:

- `Now`
- `Next`
- `Later`

`Now` means suitable for immediate bounded delegation without waiting for deeper architectural decisions.

## Now

### Task V0-A1. Shared Envelope Schema Skeleton

Priority:

- `P0`

Supports slice:

- Slice 1

Goal:

- add the minimum shared envelope schema skeleton for v0 object contracts

Suggested scope:

- introduce a dedicated schema location under the current backend
- define shared fields:
  - `id`
  - `kind`
  - `version`
  - `status`
  - `created_at`
  - `updated_at`
  - `provenance`
  - `confidence`
  - `references`

Good delegate:

- qoder `coding-agent`

Do not delegate:

- final object semantics
- final repo restructuring

Acceptance:

- bounded schema package/path added
- no repo-wide restructure
- no router behavior change yet
- tests or schema-level validation included

### Task V0-A2. Typed ID Helper Layer

Priority:

- `P0`

Supports slice:

- Slice 1

Goal:

- define typed ID helpers/patterns for v0 object classes

Focus:

- `src_`
- `obs_`
- `ent_`
- `clm_`
- `tsk_`
- `exp_`
- `dec_`
- `hrn_`

Good delegate:

- qoder `coding-agent`

Acceptance:

- helpers are explicit and bounded
- no random adoption across the whole repo in the same patch
- tests included

### Task V0-B1. Observation Contract Adapter

Priority:

- `P0`

Supports slice:

- Slice 2

Goal:

- wrap current `raw_ingest + feed_items` into an explicit v0 `Observation` contract

Suggested bounded scope:

- create adapter/schema
- map existing fields into v0 observation shape
- do not rewrite ingestion flow

Good delegate:

- qoder `coding-agent`

Acceptance:

- one observation can be materialized explicitly from current persisted inputs
- provenance/reference fields are present
- no broad feed router rewrite

### Task V0-B2. Observation Inspection Endpoint

Priority:

- `P0`

Supports slice:

- Slice 8

Goal:

- expose a minimal read path for observation inspection

Good delegate:

- qoder `coding-agent`

Acceptance:

- one bounded endpoint/family
- thin router
- explicit schema response
- no full API redesign

### Task V0-C1. ResearchTask Schema and Adapter

Priority:

- `P0`

Supports slice:

- Slice 4

Goal:

- map current task substrate to explicit `ResearchTask` v0 contract

Good delegate:

- qoder `coding-agent`

Controller review focus:

- state mapping
- trigger semantics
- owner brain semantics

Acceptance:

- explicit v0 research task object exists
- adapter uses current task runtime instead of replacing it
- states are inspectable

### Task V0-D1. Experiment Stub Contract

Priority:

- `P0`

Supports slice:

- Slice 5

Goal:

- create one bounded experiment contract and persistence path

Preferred first experiment:

- compare two source-intelligence candidate sets

Good delegate:

- qoder `coding-agent`

Acceptance:

- explicit experiment object
- small experiment type only
- evidence linkage exists

### Task V0-E1. HarnessCase Schema and First Record Path

Priority:

- `P0`

Supports slice:

- Slice 7

Goal:

- define `HarnessCase` contract and first runtime path to create one

Good delegate:

- qoder `coding-agent`
- or `test-fixer-agent`

Acceptance:

- one harness case can be persisted or explicitly materialized
- expected vs actual behavior are inspectable
- pass/fail is explicit

### Task V0-F1. Minimum Task Surface UI

Priority:

- `P1`

Supports slice:

- Slice 9

Goal:

- expose a thin active task surface for the v0 loop

Suggested UI scope:

- active task board only
- no large console redesign

Good delegate:

- qoder `coding-agent`

Acceptance:

- current v0-relevant tasks are inspectable
- historical noise is de-emphasized
- no broad visual redesign

## Next

### Task V0-G1. Entity Schema Skeleton

Priority:

- `P1`

Supports slice:

- Slice 3

Goal:

- define minimal `Entity` contract

Constraint:

- implementation may be delegated
- semantics require controller review

### Task V0-G2. Claim Schema Skeleton

Priority:

- `P1`

Supports slice:

- Slice 3

Goal:

- define minimal `Claim` contract

Constraint:

- claim granularity and confidence semantics require controller review

### Task V0-H1. Decision Record Path

Priority:

- `P1`

Supports slice:

- Slice 6

Goal:

- create one explicit decision record path

Constraint:

- delegate implementation
- keep controller review over decision semantics

### Task V0-I1. Thin Entity/Claim Inspection View

Priority:

- `P1`

Supports slice:

- Slice 9

Goal:

- provide a thin inspectable view for one observation's entity/claim outputs

### Task V0-L1. Shared Envelope Deduplication

Priority:

- `P0`

Supports slice:

- v0.1 loop hardening

Goal:

- remove shared-envelope field duplication across the v0 object layer

Constraint:

- keep object semantics unchanged
- reduce drift risk without broad schema redesign

### Task V0-L2. ResearchTask Substrate Wiring

Priority:

- `P0`

Supports slice:

- v0.1 real loop

Goal:

- wire `ResearchTask` onto the current task/context/artifact substrate for one
  real loop path

Constraint:

- one starter slice only
- no generalized task-platform redesign

### Task V0-L3. Experiment Stub Runtime Wiring

Priority:

- `P0`

Supports slice:

- v0.1 real loop

Goal:

- create one real experiment stub that attaches to the chosen `ResearchTask`

Constraint:

- one experiment type only
- one evidence linkage path only

### Task V0-L4. Chain Artifact / Inspect Surface

Priority:

- `P0`

Supports slice:

- v0.1 real loop

Goal:

- expose one inspectable chain surface for:
  - `Observation`
  - `Entity/Claim`
  - `ResearchTask`
  - `Experiment`
  - `Decision`
  - `HarnessCase`

Constraint:

- do not add durable `GET /{type}/{id}`
- keep this as inspect/chain surface, not a fake object-store API

### Task V0-L5. Harness Loop Validation

Priority:

- `P0`

Supports slice:

- v0.1 real loop

Goal:

- make `HarnessCase` validate loop completeness and traceability for the first
  real runtime-backed chain

Constraint:

- pass/fail criteria must stay explicit
- no broad harness platform redesign

## Later

### Task V0-J1. End-to-End Runtime Wiring

Priority:

- `P2`

Supports slice:

- Slice 10

Goal:

- connect all accepted slices into one full v0 runtime loop

Constraint:

- must remain main-controller supervised
- delegate only bounded glue tasks, not the whole composition as one black-box task

## Recommended First Delegation Sequence

Recommended first sequence:

1. `V0-A1`
2. `V0-A2`
3. `V0-B1`
4. `V0-C1`
5. `V0-D1`
6. `V0-E1`

Reason:

- this gets the object shell and workflow shell into the codebase before broader UI/API spread
- after the current seam is present, the next controller-approved sequence is:
  7. `V0-L1`
  8. `V0-L2`
  9. `V0-L3`
  10. `V0-L4`
  11. `V0-L5`

Additional reason:

- the next proof point is not more isolated preview endpoints
- it is one real inspectable runtime loop

## What Not To Delegate From This Backlog

Do not delegate as autonomous tasks:

- final object semantics for `Claim` and `Decision`
- end-to-end runtime composition as one large task
- migration-order changes
- repo-wide restructuring
- source-intelligence strategy changes
- evolution-brain architecture changes

## Definition of Success

This backlog is useful only if:

1. tasks can be issued directly as bounded briefs
2. delegates can complete them without broadening scope
3. accepted tasks accumulate into the v0 loop
4. the main controller does not need to re-explain the entire architecture for each task
