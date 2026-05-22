# IKE Second Benchmark Shortlist

## Purpose

This document narrows the next benchmark candidates after `harness`.

The second benchmark should stress-test whether the current benchmark method
generalizes beyond a repo-heavy, implementation-visible concept.

## Selection Criteria

The second benchmark should be:

- relevant to IKE
- semantically different from `harness`
- likely to expose weak entity judgment
- likely to expose weak concept-boundary judgment
- useful for method evolution even if the benchmark remains conservative

## Shortlist

### Candidate 1. `agent memory`

Why it is strong:

- semantically broader and more ambiguous than `harness`
- directly relevant to IKE knowledge/evolution/memory work
- likely to expose differences between:
  - note-taking
  - retrieval
  - procedural memory
  - persistent memory
  - context injection

Why it is a good stress test:

- likely to reveal weak concept-boundary reasoning
- likely to surface entity authority problems
- likely to connect directly to current Claude Code `memdir` research

### Candidate 2. `permissions`

Why it is strong:

- directly relevant to safe agent execution and controller/delegate boundaries
- less repo-centric than `harness`
- likely to surface official/product/implementation evidence differences

Why it is a good stress test:

- likely to expose whether the system can distinguish:
  - permission model
  - approval workflow
  - sandboxing
  - trust boundary

### Candidate 3. `coordinator`

Why it is strong:

- directly relevant to long-running multi-agent work
- less obvious than `harness`
- likely to expose ambiguity between:
  - routing
  - orchestration
  - controller logic
  - runtime coordination

Why it is a good stress test:

- likely to reveal whether concept summaries are still too adjacency-driven

## Preferred First Choice

Current preferred second benchmark candidate:

- `agent memory`

Reason:

- strongest semantic contrast with `harness`
- directly connected to current mainline work
- directly linked to current Claude Code `memdir` reference line
- likely to produce useful method value even if the benchmark stays conservative

## Current Non-Decision

This shortlist is not yet the final second benchmark selection.

It exists to keep the next choice narrow and intentional.
