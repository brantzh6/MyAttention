# IKE Runtime v0 R1-H Target Recovery Order

## Purpose

This note records the first controller target order for `R1-H` after `R1-H1`
made delegated/fallback evidence distribution explicit.

It is not a new runtime semantic plan.
It is the narrow recovery order for independent delegated evidence.

## Current Evidence Snapshot

From the current durable delegated result artifacts:

- `R1-D`
  - delegated: `coding`, `evolution`
  - fallback: `review`, `testing`
- `R1-E`
  - delegated: `coding`
  - fallback: `review`, `testing`, `evolution`
- `R1-F`
  - delegated: `coding`
  - fallback: `review`, `testing`, `evolution`
- `R1-G`
  - delegated: `coding`, `testing`
  - fallback: `review`, `evolution`

## Recovery Priority

### 1. `R1-G`

Why first:

- most recent completed runtime phase
- already has real coding and testing evidence
- only review/evolution remain fallback-backed

Target lanes:

- `R1-G2`
- `R1-G4`

### 2. `R1-F`

Why second:

- still close to the active runtime baseline
- controller-facing read surface should not remain review/testing/evolution
  fallback-heavy for long

Target lanes:

- `R1-F2`
- `R1-F3`
- `R1-F4`

### 3. `R1-E`

Why third:

- project-surface alignment remains important but is slightly older than `R1-F`

Target lanes:

- `R1-E2`
- `R1-E3`
- `R1-E4`

### 4. `R1-D`

Why fourth:

- closure semantics are materially stabilized
- review/testing recovery still matters, but less urgently than the newer
  runtime surfaces

Target lanes:

- `R1-D2`
- `R1-D3`

## Controller Rule

Do not claim a recovered lane unless:

- a durable delegated result exists
- the result is not merely a controller fallback note
- the result does not explicitly say independent delegated evidence is still
  missing
