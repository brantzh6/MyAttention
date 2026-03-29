# IKE Migration Alignment

## Purpose

This document aligns the new IKE architecture with the current MyAttention codebase.

It does not redefine IKE.
It explains how to move from the current implementation state toward IKE without a full restart.

## Decision

Use `IKE as the top-level design source` and `migration as the implementation strategy`.

Do not:

- start a fresh repository
- rewrite the whole system from scratch
- keep extending the current codebase without an IKE target

The chosen path is:

1. keep the existing runtime and data foundation
2. introduce IKE-aligned shared objects and contracts
3. progressively re-route current modules onto the IKE object/workflow/governance model
4. retire legacy structures only after the new path is real and inspectable

## Why Not Fresh Start

Fresh start is not justified at current cost/benefit.

The current codebase already contains reusable foundations:

- modular monolith structure
- PostgreSQL/Redis/Qdrant/object-storage runtime
- task/context/artifact/history primitives
- source plans and source-plan versioning
- brain control-plane foundation
- observation and feed ingestion pipeline
- evolution runtime and health loop

Rebuilding these from zero would consume time without reducing the main risks enough.

The real problem is not "too much code exists".
The real problem is "the current implementation is not yet organized around the IKE object model and workflow model".

That is a migration problem, not a greenfield problem.

## Current-to-IKE Mapping

### 1. Information Brain

IKE target:

- Source
- Observation
- watch targets
- source evaluation
- ongoing sensing and review

Current equivalents:

- `sources`
- `feed_items`
- `raw_ingest`
- `source_plans`
- `source_plan_items`
- source discovery / attention policy logic

Assessment:

- partially aligned
- strongest reusable asset in the current system
- main weakness is candidate quality and object relations, not total absence of structure

Migration direction:

- treat `feed_items` and `raw_ingest` as early `Observation`
- evolve `source_plans` toward `attention plans / watch targets`
- keep moving from domain-centric discovery to object-centric discovery

### 2. Knowledge Brain

IKE target:

- Entity
- Relation
- Claim
- Event
- Concept
- structured knowledge memory

Current equivalents:

- knowledge-base management
- vector/RAG infrastructure
- partial feed-to-knowledge linkage
- some category and extraction scaffolding

Assessment:

- weakly aligned
- current foundation is usable
- current implementation is still too document/RAG-oriented and not yet a proper IKE object graph

Migration direction:

- define explicit `Entity / Relation / Claim / Event` objects
- stop treating knowledge primarily as chunks + vectors
- keep vector retrieval as one substrate, not the top-level knowledge model

### 3. Evolution Brain

IKE target:

- ResearchTask
- Experiment
- Decision
- GovernanceReview
- adoption / reject / defer / escalate loop

Current equivalents:

- auto-evolution loops
- self-test
- issue generation
- task processor
- task contexts / artifacts / histories

Assessment:

- partially aligned
- runtime orchestration exists
- reasoning/governance layer is still too weak
- still too much watchdog/rule-engine and not enough model-assisted prioritization and diagnosis

Migration direction:

- treat current task system as the execution substrate
- introduce explicit `ResearchTask / Experiment / Decision / EvaluationRecord`
- move from operational alerts toward inspectable research-and-adoption loops

### 4. Thinking-Model Layer

IKE target:

- ThinkingModel
- Paradigm
- model selection
- model combination
- evaluation and governance

Current equivalents:

- attention policy
- problem framing / method selection docs
- brain routing / execution plans
- multi-model chat/voting

Assessment:

- conceptually aligned
- implementation is still fragmented across docs, routes, and runtime policies

Migration direction:

- formalize `ThinkingModel` and `Paradigm` as first-class objects
- turn current method/policy documents into governed procedural knowledge objects
- keep the current route/policy work, but move it under IKE governance

### 5. Shared Memory Layer

IKE target:

- observation memory
- evidence memory
- structured knowledge memory
- working research memory
- governance memory
- long-term adopted memory

Current equivalents:

- memory facts
- source-plan evidence
- task artifacts
- task histories
- raw ingest / feed facts
- partial vector memory

Assessment:

- partially aligned
- memory exists in multiple local forms
- not yet unified under IKE memory strata

Migration direction:

- keep current storage substrates
- unify memory semantics before replacing storage implementations
- avoid treating chat history as the memory model

## Reusable Assets

These should be preserved and re-aligned instead of replaced early:

- runtime bootstrap and local process/service control
- PostgreSQL schema migration path
- task/context/artifact/history runtime
- source plan and version management
- feed ingestion pipeline
- Redis-backed feed cache path
- qoder/openclaw controlled delegation infrastructure

## Structures Likely To Be Reworked

These are useful now but should not be treated as final:

- current `feed_items` as the main universal information object
- current router-heavy source discovery implementation in `feeds.py`
- current rule-heavy evolution logic
- fragmented memory semantics
- brain/policy configuration spread across docs + runtime tables without a unified IKE object layer

## First Migration Slice

The first migration slice should follow the IKE v0 principle:

`Observation -> Entity/Claim -> ResearchTask -> Experiment -> Decision -> HarnessCase`

### Recommended v0 slice

1. Observation
- reuse `raw_ingest + feed_items`
- define an explicit IKE-facing `Observation` contract

2. Entity/Claim
- add minimal extraction output contract from observation
- do not overbuild a full graph first

3. ResearchTask
- map one real source-intelligence or evolution issue into explicit `ResearchTask`

4. Experiment
- add a small experiment stub with state transitions and evidence capture

5. Decision
- record adopt/reject/defer/escalate as an explicit object

6. HarnessCase
- add one inspectable harness record to prove the loop is real

Exit condition:

- one complete IKE-aligned loop exists in the running system and can be inspected end-to-end

## Implementation Rules

### Keep

- modular monolith
- contract-first changes
- explicit provenance/version/confidence/reference fields
- bounded delegation for coding work

### Avoid

- full rewrite
- premature service splitting
- giant generic agent framework before the object/workflow loop is real
- portfolio-style model governance too early

## Immediate Next Documents

After this alignment document, the next implementation-facing documents should be:

1. `IKE_V0_EXECUTION_PLAN.md`
2. `IKE_SHARED_OBJECTS_V0.md`
3. `IKE_RUNTIME_MIGRATION_SEQUENCE.md`

Each should stay narrow and implementation-facing.
