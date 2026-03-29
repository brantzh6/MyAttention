# IKE v0 Implementation Slices

## Purpose

This document breaks the IKE v0 plan into bounded implementation slices.

It exists for two reasons:

1. keep the v0 migration executable without broad rewrites
2. make delegation possible without giving away main control

This is not a full backlog.
It is the first practical slice map for implementation and review.

## Main Controller Rule

The main controller should keep control of:

- migration order
- object contract decisions
- acceptance criteria
- slice boundaries
- review and acceptance decisions

Implementation work should usually be delegated.

## Slice Design Rules

Every v0 slice should be:

- narrow
- inspectable
- independently testable
- reversible
- useful to the v0 loop

Every slice should contribute to:

`Observation -> Entity/Claim -> ResearchTask -> Experiment -> Decision -> HarnessCase`

## Slice Set

### Slice 1. Shared Envelope and IDs

Goal:

- introduce the minimum shared envelope shape for v0 objects
- standardize typed IDs and common metadata fields

Outputs:

- common typed ID helpers
- common envelope/schema definitions
- explicit version/status/provenance/confidence/reference fields

Good delegation target:

- yes

Reason:

- bounded
- contract-focused
- easy to review

Main-controller concerns:

- object naming
- typed ID policy
- minimum required fields

### Slice 2. Observation Contract Over Current Feed Inputs

Goal:

- define an IKE-facing `Observation` object on top of current `raw_ingest + feed_items`

Outputs:

- observation schema
- observation mapper or adapter over existing information objects
- provenance/reference consistency

Good delegation target:

- yes

Reason:

- bounded
- additive
- low-risk if kept behind adapters

Main-controller concerns:

- what qualifies as an observation
- how much current feed/source state should be exposed vs wrapped

### Slice 3. Entity / Claim Extraction Contract

Goal:

- create explicit `Entity` and `Claim` outputs from one observation

Outputs:

- entity schema
- claim schema
- one inspectable extraction path

Good delegation target:

- partly

Reason:

- implementation is delegable
- but the main controller should keep:
  - claim granularity
  - confidence semantics
  - subject/evidence linkage rules

### Slice 4. ResearchTask Adapter

Goal:

- map the current task runtime to explicit `ResearchTask` semantics for the first v0 loop

Outputs:

- research task schema
- task creation adapter
- inspectable state transition mapping

Good delegation target:

- yes, if bounded

Reason:

- implementation can be delegated
- state semantics must still be reviewed carefully

Main-controller concerns:

- trigger types
- owner brain semantics
- state mapping

### Slice 5. Experiment Stub

Goal:

- create one explicit experiment record from a research task

Outputs:

- experiment schema
- one real experiment type for the first v0 loop
- experiment evidence linkage

Good delegation target:

- yes

Reason:

- bounded
- does not require full experiment platform design

Preferred first experiment types:

- compare two source-intelligence candidate sets
- compare two attention-policy outputs
- compare two extraction outputs

### Slice 6. Decision Record

Goal:

- record one explicit `Decision` from task + experiment + evidence

Outputs:

- decision schema
- decision persistence path
- inspectable decision rationale/evidence linkage

Good delegation target:

- partly

Reason:

- storage and view wiring is delegable
- decision semantics should remain controller-reviewed

### Slice 7. Harness Case for the Loop

Goal:

- validate whether the v0 loop actually executed correctly

Outputs:

- harness case schema
- one v0 harness record
- pass/fail criteria for loop completeness and traceability

Good delegation target:

- yes

Reason:

- bounded
- naturally test-oriented

Main-controller concerns:

- pass/fail contract
- what counts as loop completeness

### Slice 8. Minimum API Surface

Goal:

- expose only the minimum inspectable v0 control API

Recommended endpoints/families:

- observation submit/view
- entity/claim view
- research task creation/view
- experiment trigger/view
- decision record/view
- harness case view

Good delegation target:

- yes, in bounded sub-slices

Reason:

- routers should stay thin
- implementation can be split endpoint by endpoint

Constraint:

- do not try to build the whole future IKE API

### Slice 9. Minimum UI Surface

Goal:

- provide the thinnest human-inspectable surface for the v0 loop

Recommended views:

- thin workspace shell
- active task surface
- entity/claim inspection view
- decision review view

Good delegation target:

- yes

Reason:

- bounded frontend tasks are ideal delegation candidates

Constraint:

- do not turn this into a large redesign

### Slice 10. Runtime Flow Wiring

Goal:

- connect the slices into one real vertical loop

Outputs:

- one end-to-end v0 runtime path
- one reconstructible chain of object refs
- one inspectable loop instance

Good delegation target:

- partly

Reason:

- individual glue tasks can be delegated
- the full end-to-end composition should remain main-controller supervised

## Suggested Execution Order

Recommended order:

1. Shared Envelope and IDs
2. Observation Contract
3. ResearchTask Adapter
4. Experiment Stub
5. Decision Record
6. Harness Case
7. Entity / Claim Extraction
8. Minimum API Surface
9. Minimum UI Surface
10. Runtime Flow Wiring

Reasoning:

- the object shell and workflow shell should stabilize before broader surface work
- entity/claim extraction is essential, but the first workflow chain can still be staged in parallel once contracts are clear
- UI should come after loop objects and API visibility are stable enough to avoid rework

## Delegation Strategy By Slice

### Best first delegation targets

- Slice 1
- Slice 2
- Slice 5
- Slice 7
- Slice 8
- Slice 9

These are bounded and easy to review.

### Controller-heavy slices

- Slice 3
- Slice 6
- Slice 10

These involve semantics and acceptance judgment that should not be handed off without tighter supervision.

## Definition of Success

This slice plan is working if:

1. implementation tasks can be delegated without scope drift
2. each accepted slice makes the v0 loop more explicit
3. the codebase gains IKE objects without broad destabilization
4. the first complete v0 loop can be assembled from accepted slices
