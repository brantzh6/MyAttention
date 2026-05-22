# IKE Claude Code B4 Closure Adapter Plan

## Purpose

`B4` defines the bridge between the procedural-memory v1 prototype and the
current IKE runtime substrate.

The current prototype can write a `procedure` memory record.
What it still lacks is a truthful adapter from existing bounded completion
artifacts into that record shape.

## Why B4 Exists

Current state:

- procedural-memory v1 exists
- it is file-based and bounded
- it is not yet connected to a real IKE completion path

Current runtime reality:

- there is no dedicated `task_closure.py` object yet
- there is a chain/loop substrate and bounded completion artifacts

Therefore the next step should be a narrow adapter, not a broad runtime change.

## Main Goal

Create a minimal closure adapter that can transform an existing bounded
completion payload into a procedural-memory input shape.

The adapter should be:

- additive
- truthful
- testable
- not automatically wired into all runtime flows

## Candidate Inputs

The first adapter should accept one narrow completion payload shape based on
existing runtime artifacts, for example:

- a bounded task closure payload
- or a chain artifact completion summary

But it must not invent missing runtime objects.

## Output Shape

The adapter should produce only the fields needed by procedural-memory v1:

- `title`
- `lesson`
- `why_it_mattered`
- `how_to_apply`
- `confidence`
- `source_artifact_ref`

## Constraints

Do not:

- create a broad event bus
- auto-trigger on every chain artifact
- add general recall behavior
- widen the memory taxonomy

Do:

- keep the adapter explicit
- keep the input shape narrow
- fail loudly if the payload does not contain enough information

## Success Condition

`B4` succeeds if IKE can take one bounded completion payload and derive one
valid procedural-memory candidate without pretending that a full task-closure
runtime already exists.

## Current Result

`B4` is now accepted only in its truthful form:

- the adapter validates explicit closure payload fields
- the adapter persists them via procedural-memory v1
- the adapter does **not** derive lesson/confidence/guidance heuristically

This means the next problem is no longer adapter design.
The next problem is:

- where explicit closure payloads should come from
