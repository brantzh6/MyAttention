# IKE v0 Execution Plan

## Purpose

This document defines the first executable IKE slice.

It is not the full IKE roadmap.
It is the smallest end-to-end loop that proves the IKE direction is real in the current codebase.

## v0 Goal

v0 must prove that the current MyAttention system can execute one inspectable IKE-aligned loop:

`Observation -> Entity/Claim -> ResearchTask -> Experiment -> Decision -> HarnessCase`

The result must be:

- real
- inspectable
- repeatable
- narrow

## What v0 Must Prove

v0 must prove all of the following:

1. a targeted observation can be ingested through the existing runtime
2. that observation can produce structured interpretation output
3. the interpretation can create an explicit research task
4. the research task can spawn an experiment
5. the experiment can produce evidence
6. a decision can be recorded from that evidence
7. a harness record can show whether the loop behaved as expected

## What v0 Must Not Try To Prove

Do not use v0 to prove:

- full knowledge graph completeness
- large-scale model governance
- distributed service boundaries
- generalized multi-agent orchestration
- perfect source-intelligence quality
- final UX polish
- final durable object retrieval semantics

If v0 tries to prove all of that, it will fail by scope.

## Recommended v0 Loop

### Step 1. Observation

Reuse current:

- `raw_ingest`
- `feed_items`
- source-intelligence candidate or feed item input

v0 requirement:

- define an explicit IKE-facing observation contract
- observation must carry provenance, timestamps, confidence, and references

### Step 2. Entity / Claim extraction

Produce a minimal structured output from one observation:

- entities
- one or more claims
- optional relation hints

v0 requirement:

- the output must be explicit and inspectable
- do not rely only on embedded text or opaque LLM summaries

### Step 3. ResearchTask creation

Create one explicit `ResearchTask` from:

- a signal gap
- a confidence gap
- a contradiction
- a source-intelligence quality issue

Recommended starter case:

- source-intelligence quality or frontier-observation ambiguity

This is better than inventing a synthetic research problem.

### Step 4. Experiment stub

Spawn one experiment from that task.

Examples:

- compare two source-intelligence candidate sets
- compare two policy selections
- compare two extraction outputs

v0 requirement:

- the experiment can be small
- but it must have explicit state, evidence, and outcome

### Step 5. Decision

Record one explicit decision:

- adopt
- reject
- defer
- escalate

The decision must be attached to:

- task
- experiment
- evidence

### Step 6. HarnessCase

Create one harness record for this loop.

The harness case must answer:

- what was expected
- what actually happened
- did the loop satisfy the v0 contract

## v0 Object Set

The first v0 objects should be:

- `Observation`
- `Entity`
- `Claim`
- `ResearchTask`
- `Experiment`
- `Decision`
- `HarnessCase`

Do not attempt to fully implement all IKE first-class objects in v0.

## Implementation Strategy

### Strategy 1. Reuse current substrates

Use existing runtime infrastructure where possible:

- PostgreSQL
- task/context/artifact/history
- feed/source ingestion
- evolution/self-test infrastructure

### Strategy 2. Add explicit contracts first

Before broad code changes:

- define the IKE-facing object contracts
- define state transitions
- define provenance/version/confidence fields

### Strategy 3. Keep the slice vertical and narrow

Do not spread v0 across many unrelated features.

One vertical slice is better than ten partially aligned subsystems.

## Execution Order

### Phase V0-1. Define contracts

Deliverables:

- `IKE_SHARED_OBJECTS_V0.md`
- minimal field definitions for observation/entity/claim/task/experiment/decision/harness

### Phase V0-2. Map onto current runtime

Deliverables:

- `IKE_RUNTIME_MIGRATION_SEQUENCE.md`
- explicit mapping from current tables/runtime objects to v0 objects

### Phase V0-3. Implement one loop

Deliverables:

- one real loop in the running system
- one harness case
- one inspectable decision record

### Phase V0-3a. Keep the API honest

Before exposing a broad API surface:

- prefer create/generate/extract/preview/inspect style endpoints
- do not expose standard `GET /{type}/{id}` unless the runtime can truly support durable retrieval

Reference:

- `docs/IKE_API_TRANSITION_PRINCIPLES.md`

### Phase V0-4. Review and tighten

Deliverables:

- evidence that the loop is repeatable
- identified gaps for v1
- no premature expansion

## Acceptance Criteria

v0 is complete only if all of the following are true:

1. one real observation can enter the loop
2. one explicit structured interpretation is produced
3. one research task is created
4. one experiment record is created and completed
5. one decision record exists
6. one harness case exists
7. the full chain is inspectable without reading raw logs

## Failure Conditions

v0 should be considered failed or out of scope if:

- it becomes a large platform rewrite
- it requires immediate service decomposition
- it depends on perfect source discovery first
- it produces only documents and no running loop
- it produces only runtime glue and no explicit decision object
- it exposes a stable-looking resource API that the current runtime cannot honestly support

## Current Recommendation

The first v0 loop should start from the strongest existing substrate:

- source-intelligence observation
- or evolution-detected quality issue

This is preferable to starting from chat, because:

- the object chain is clearer
- the current system already has more runtime structure there
- it connects directly to the IKE thesis of research and self-improvement
