# IKE Worker Skill Contract

Date: 2026-04-18
Status: controller contract

## Purpose

Define how IKE consumes a worker as a reusable capability instead of a
project-private script.

The worker is a necessary part of IKE once the product has an AI entrypoint.
It is not the main product identity, but it is part of the core execution
substrate.

## Core Judgment

IKE should treat a worker as a versioned skill that the harness can load,
validate, execute, and audit.

The first concrete implementation is `claude-worker`.

Future workers must be able to plug into the same contract.

## Relationship To IKE

- IKE owns the product objective, truth boundary, and task governance
- worker skills own execution behavior
- the harness owns loading, gating, sandboxing, and audit
- review/absorption owns durable acceptance

## Required Skill Shape

A worker skill should have:

- identity
- version/ref
- manifest
- supported execution modes
- provider/model requirements
- model switching interface
- prompt delivery policy
- artifact/result schema
- trust level
- validation hooks
- stop conditions

## Required Trust Boundary

The worker may execute tasks.

It may not redefine:

- project priorities
- acceptance criteria
- runtime truth
- AI evolution direction

The harness must continue to treat worker output as candidate evidence until
reviewed.

## Required Execution Semantics

The worker contract must support at least:

- single-agent task execution
- bounded prompt delivery
- detached finalization
- inspectable artifacts
- result projection

Later, the same contract may expand to multi-agent orchestration, but the
single-agent case must remain the minimal guaranteed path.

## Required Model Switching Semantics

Model switching is part of the worker skill contract.

Every worker implementation should expose the same conceptual interface:

- declare default model
- declare supported models/providers
- accept explicit model override per packet
- validate the selected model before execution
- persist the selected model/provider in artifacts and results
- return the actual model/provider used

The exact provider mechanics may differ between implementations, but the
contract shape should stay consistent across all workers.

Worker model switching is not a Claude-only exception.
It is a portable IKE capability requirement.

## Required Result Protocol

The worker result should expose at least:

- summary
- files_changed
- why_this_solution
- validation_run
- known_risks
- recommendation

And when relevant:

- execution_mode
- prompt_delivery
- lifecycle
- model provenance

## Required Harness Duties

The IKE harness must:

1. fetch the skill from a versioned source
2. validate the manifest and contract before execution
3. inject execution context
4. collect durable artifacts
5. enforce trust boundaries
6. validate model/provider selection
7. hand the result back to controller review

## Required Manifest Semantics

The skill should be importable through a machine-readable manifest.

The manifest should expose:

- identity
- version/ref
- entrypoint
- supported execution modes
- default model
- supported model/provider interface
- artifact contract
- trust boundary
- validation hooks
- stop conditions

## Current First Implementation

`claude-worker` is currently the first implementation of this skill shape.

It already demonstrates:

- durable prompt delivery
- detached finalization
- explicit execution modes
- structured result projection
- review-gated output
- explicit model selection and provenance

The current implementation is close enough to be useful, but the skill contract
still needs to be formalized in IKE so other worker implementations can share
the same loading and governance path.

## Phase Sequencing

### Phase 0

Single-agent execution under harness control.

### Phase 1

GitHub-backed skill import and contract validation.

### Phase 2

Multiple worker implementations under one harness contract.

### Phase 3

Multi-agent orchestration on top of the same skill contract.

## Non-Goals

- do not make the worker the product identity
- do not encode a single provider forever
- do not bypass harness review
- do not let worker output become truth without controller absorption
- do not jump straight to multi-agent orchestration

## Final Decision

Worker skills are a necessary IKE capability.

They should be loaded by the IKE harness as versioned, reviewable, bounded
skills.
