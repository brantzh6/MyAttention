# IKE Claude Code B3 Procedural Memory Prototype Plan

## Purpose

`B3` is the first prototype-planning packet derived from the accepted
`Claude Code memdir` study.

The goal is not to implement memory immediately.
The goal is to define the smallest safe IKE prototype that tests whether
procedural memory extraction is actually useful.

## Why B3 Exists

The `B2` study concluded:

- typed memory discipline is reusable
- bounded memory entrypoint/indexing is reusable
- background extraction after task completion is highly relevant
- direct full-copying of Claude Code memory is not appropriate

This means IKE is now ready for a bounded prototype plan.

## Prototype Goal

Design a first procedural-memory prototype for IKE that:

1. captures non-derivable lessons from bounded work
2. does not flood the system with low-value summaries
3. remains inspectable by both the controller and future retrieval logic

## Prototype Boundary

Start with one narrow class of memory only:

- `procedure`

Optional second class only if needed:

- `feedback`

Do not start with:

- full user profile memory
- broad project memory
- general note-taking
- full knowledge graph integration

## Candidate Trigger Points

The prototype should evaluate only these trigger points:

1. bounded benchmark `study_result`
2. `decision_handoff`
3. `task_closure`

Do not trigger on every conversation turn.

## Candidate Memory Shape

Minimum proposed fields:

- `memory_type`
- `title`
- `lesson`
- `why_it_mattered`
- `how_to_apply`
- `confidence`
- `source_artifact_ref`
- `created_from`
- `applicability_scope`

## What Must Stay Derivable

Do not store as memory:

- code facts
- file paths
- current repo structure
- raw task logs
- generic benchmark summaries

Those should remain derivable from artifacts or code.

## Success Condition

`B3` succeeds if it yields a prototype spec that is:

- small
- inspectable
- difficult to spam
- directly linked to bounded work completion

## Failure Condition

`B3` fails if it turns into:

- a generic notes system
- broad chat summarization
- uncontrolled auto-save of everything
