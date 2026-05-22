# IKE Shared Objects v0

## Purpose

This document defines the minimum first-class object contracts required for the IKE v0 loop.

It is not the final IKE schema set.
It is the minimum shared object layer needed to implement one real end-to-end loop.

The v0 loop is:

`Observation -> Entity/Claim -> ResearchTask -> Experiment -> Decision -> HarnessCase`

## Design Rules

### 1. Contracts first

These objects must exist as explicit contracts before broad implementation work.

### 2. Keep them small

Only include fields required for:

- inspectability
- provenance
- state transitions
- evidence linkage
- repeatability

### 3. Shared envelope

All v0 objects should carry a common envelope concept:

- `id`
- `kind`
- `version`
- `status`
- `created_at`
- `updated_at`
- `provenance`
- `confidence`
- `references`

The exact storage representation can vary, but the contract must exist.

## v0 Objects

### 1. Observation

Purpose:

- represent one externally observed unit before it becomes structured interpretation

Required fields:

- `id`
- `kind = observation`
- `version`
- `status`
- `source_ref`
- `raw_ref`
- `observed_at`
- `captured_at`
- `title`
- `summary`
- `content_ref | content_excerpt`
- `signal_type`
- `confidence`
- `provenance`
- `references`

Notes:

- v0 can map this onto current `raw_ingest + feed_items`
- observation is not yet a claim or accepted fact

### 2. Entity

Purpose:

- represent a first-class identified object in the world or system

Required fields:

- `id`
- `kind = entity`
- `version`
- `status`
- `entity_type`
- `canonical_key`
- `display_name`
- `aliases`
- `confidence`
- `provenance`
- `references`

Examples:

- person
- organization
- repository
- product
- concept

### 3. Claim

Purpose:

- represent one interpretable statement derived from an observation or evidence set

Required fields:

- `id`
- `kind = claim`
- `version`
- `status`
- `claim_type`
- `statement`
- `subject_refs`
- `evidence_refs`
- `source_observation_refs`
- `confidence`
- `provenance`
- `references`

Notes:

- claim is not automatically accepted truth
- it is a structured unit of interpretation

### 4. ResearchTask

Purpose:

- represent one deliberate inquiry created from a gap, signal, contradiction, or governance action

Required fields:

- `id`
- `kind = research_task`
- `version`
- `status`
- `task_type`
- `title`
- `goal`
- `trigger_type`
- `input_refs`
- `priority`
- `owner_brain`
- `created_at`
- `updated_at`
- `provenance`
- `references`

State expectations:

- `draft`
- `open`
- `in_progress`
- `blocked`
- `completed`
- `cancelled`

### 5. Experiment

Purpose:

- represent one concrete attempt to test or compare something for a research task

Required fields:

- `id`
- `kind = experiment`
- `version`
- `status`
- `task_ref`
- `experiment_type`
- `title`
- `hypothesis`
- `method_ref`
- `input_refs`
- `evidence_refs`
- `result_summary`
- `confidence`
- `provenance`
- `references`

State expectations:

- `draft`
- `running`
- `completed`
- `failed`
- `invalidated`

### 6. Decision

Purpose:

- represent one adoption/rejection/defer/escalate decision based on evidence

Required fields:

- `id`
- `kind = decision`
- `version`
- `status`
- `task_ref`
- `experiment_refs`
- `decision_type`
- `decision_outcome`
- `rationale`
- `evidence_refs`
- `confidence`
- `provenance`
- `references`
- `review_required`
- `review_status`

Outcomes:

- `adopt`
- `reject`
- `defer`
- `escalate`

### 7. HarnessCase

Purpose:

- represent one inspectable evaluation of whether a loop behaved correctly

Required fields:

- `id`
- `kind = harness_case`
- `version`
- `status`
- `case_type`
- `subject_refs`
- `expected_behavior`
- `actual_behavior`
- `pass_fail`
- `evidence_refs`
- `notes`
- `provenance`
- `references`

## v0 Relationship Rules

At minimum the following references must be possible:

- `Observation -> Entity`
- `Observation -> Claim`
- `ResearchTask -> Observation | Claim`
- `Experiment -> ResearchTask`
- `Decision -> ResearchTask`
- `Decision -> Experiment`
- `HarnessCase -> Task | Experiment | Decision`

v0 does not require a complete graph engine.
It does require explicit references.

## Mapping to Current System

### Observation

Current likely sources:

- `raw_ingest`
- `feed_items`

### ResearchTask / Experiment / Decision / HarnessCase

Current likely substrate:

- `tasks`
- `task_contexts`
- `task_artifacts`
- `task_histories`

### Entity / Claim

Current status:

- not properly first-class yet
- requires a new explicit contract even if first implemented as artifact payloads

## v0 Implementation Guidance

### Allowed shortcut

For v0, explicit objects may first be materialized as:

- dedicated tables
- or strongly typed artifact payloads with stable contracts

The key requirement is not "final persistence purity".
The key requirement is that the objects are explicit, inspectable, and versioned.

### Not allowed

Do not treat:

- free-form chat text
- unstructured JSON blobs with no contract
- implicit runtime state

as the final object form for v0.

## Acceptance Criteria

This object layer is sufficient for v0 only if:

1. each object type can be instantiated explicitly
2. each object type carries provenance and references
3. task/experiment/decision/harness states are inspectable
4. one full loop can be reconstructed from stored objects without reading raw logs
