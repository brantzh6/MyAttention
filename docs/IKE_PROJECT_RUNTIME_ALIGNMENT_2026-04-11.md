# IKE Project Runtime Alignment

Date: 2026-04-11
Status: controller baseline

## Purpose

Define how the current project-governance layer relates to the future runtime
task / decision / memory system.

This document exists to prevent a dangerous split:

- one task-memory system for building IKE
- another incompatible task-memory system inside IKE

That split is not allowed.

## Core Judgment

The current project governance layer is a **pre-runtime controller shell**.

It is not a separate long-term task/memory architecture.

That means:

1. it must be usable now
2. it must remain semantically compatible with runtime
3. it must not introduce a state model that runtime will later need to undo
4. it must not drift into a permanently hard-coded substitute for the later
   AI-driven kernel

## The Loop We Must Respect

IKE runtime is being built to manage:

- tasks
- decisions
- memory
- work context
- promotion and review boundaries

But before runtime is complete, the project itself also needs:

- task management
- decision recording
- memory retention
- promotion and rollback discipline

So the project is temporarily using an external controller-governance layer to
manage the creation of the runtime that will later internalize those same
capabilities.

## Non-Conflict Rule

The project governance layer and runtime layer must satisfy four conditions:

1. same core concepts where possible
2. no contradictory state transitions
3. no chat-only canonical truth
4. current durable records must be migratable or mappable later

## Alignment Model

### 1. Project mainline / support tracks / research tracks

Current governance concept:

- project work tracks
- mainline priorities
- support tracks
- research backlog

Runtime-aligned meaning:

- these should eventually map to `RuntimeProject` plus grouped `RuntimeTask`
  structures

Current rule:

- do not invent a second permanent project taxonomy that runtime cannot
  represent

### 2. Task

Current governance concept:

- task packet
- coding brief
- review brief
- implementation queue item
- support-track action

Runtime-aligned meaning:

- should map to `runtime_tasks`

Current rule:

- governance tasks should already behave like bounded runtime tasks:
  - one scope
  - one owner lane
  - explicit validation
  - explicit stop conditions

### 3. Decision

Current governance concept:

- controller decision
- review outcome
- promotion decision
- acceptance / reject / defer

Runtime-aligned meaning:

- should map to `runtime_decisions`

Current rule:

- governance decisions must be explicit and auditable, because runtime also
  treats decision as a first-class durable object

### 4. Memory

Current governance concept:

- result docs
- review docs
- progress notes
- changelog
- governance docs
- archived research notes

Runtime-aligned meaning:

- these are temporary controller-facing memory carriers
- they should eventually map to reviewed runtime memory objects, artifacts, or
  trusted packet-like summaries

Current rule:

- documentation is allowed as the current durable shell
- chat is not allowed as canonical memory

### 5. Work context

Current governance concept:

- current mainline map
- current runtime index
- governance index
- handoff file

Runtime-aligned meaning:

- these are the current manual equivalent of `WorkContext`
- runtime later reconstructs work context from canonical task/decision/packet
  truth

Current rule:

- these docs must summarize current state
- they must not silently become a second contradictory truth source

### 6. Promotion

Current governance concept:

- proposal
- implementation
- review
- validation
- archive
- promotion
- release

Runtime-aligned meaning:

- this is the external controller analogue of explicit state transitions and
  reviewed decision gates inside runtime

Current rule:

- project governance may be more manual than runtime
- it may not be more ambiguous than runtime

### 7. Environment

Current governance concept:

- controller-dev
- sandbox-evolution
- staging-runtime
- prod-runtime

Runtime-aligned meaning:

- this should stay compatible with runtime harness ideas:
  - sandbox identity
  - capability policy
  - write scope
  - promotion target

Current rule:

- environment naming and separation should be treated as future runtime
  execution-context inputs, not one-off admin conventions

## What The Governance Layer Is Allowed To Be

The governance layer may be:

- more manual
- more document-driven
- more controller-operated

It may not be:

- semantically contradictory to runtime
- dependent on chat memory
- a parallel permanent truth model

## What Will Likely Be Absorbed By Runtime Later

These current governance artifacts are expected to become partially absorbed by
runtime over time:

1. bounded task packets
2. controller acceptance records
3. project current-state summaries
4. milestone result records
5. review-linked trusted knowledge summaries

## What Should Stay Outside Runtime

Not everything should move into runtime.

Some things should remain external controller governance:

1. high-level project strategy
2. release governance policy
3. human organizational rules
4. meta-rules about what runtime is allowed to mutate

So the goal is not "put everything into runtime."

The goal is:

- runtime owns operational task/decision/memory truth
- controller governance owns the rules and boundaries around that system

## Immediate Controller Rules

Effective immediately:

1. new governance docs should use runtime-compatible language where possible
2. important project actions should be framed as bounded tasks or decisions
3. important retained knowledge should be written in ways that can later be
   packetized or mapped into runtime memory
4. no new project-management concept should be introduced if it directly
   conflicts with current runtime object semantics

## Practical Meaning

The project is currently using a manual external shell to build the internal
system that will later automate much of that shell.

That is acceptable.

Building two incompatible systems is not.
