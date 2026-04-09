# IKE Runtime v0 R1-F Controller Read Surface Plan

## Purpose

`R1-F` is the narrow phase after materially complete `R1-E`.

Its job is to give the controller one truthful, runtime-backed read surface for
the current operational state of a project.

## Why This Phase Exists

The runtime kernel now has:

- durable task/decision/memory/work-context truth
- operational closure
- project-level current context pointer alignment

But controller-facing "what is going on right now" visibility is still
fragmented across direct helper knowledge and scattered runtime objects.

## Core Scope

### R1-F1 Coding

Goal:

- add one helper/read model that assembles current project operational state
  from runtime truth

Must prove:

- read output is fully derivable from runtime truth
- no extra persistent summary object is introduced

### R1-F2 Review

Goal:

- review the read surface for hidden duplicated state or scope creep

### R1-F3 Testing

Goal:

- verify the read surface:
  - reflects active project pointer/current context
  - includes current active/waiting task visibility
  - includes latest finalized decision and trusted packet refs only
  - does not invent state when upstream truth is absent

### R1-F4 Evolution

Goal:

- capture what controller-facing runtime visibility rules should become durable
  method rules

## Boundaries

Allowed:

- narrow runtime helper/service updates
- narrow DB-backed tests
- read-model assembly from existing runtime truth

Not allowed:

- broad API design
- UI/runtime expansion
- notifications/follow-up surfaces
- graph memory
- benchmark/runtime fusion
- new runtime object families
