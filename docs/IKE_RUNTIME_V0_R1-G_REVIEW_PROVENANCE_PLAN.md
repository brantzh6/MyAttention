# IKE Runtime v0 R1-G Review Provenance Plan

## Purpose

`R1-G` is the narrow phase after materially complete `R1-F`.

Its job is to harden runtime review-submission and acceptance provenance
without creating new workflow objects.

## Why This Phase Exists

The runtime kernel now has:

- closure truth
- project pointer alignment
- controller-facing read visibility

But review/acceptance attribution is still not as explicitly hardened as the
rest of the runtime truth layer.

## Core Scope

### R1-G1 Coding

Goal:

- tighten runtime review-submission / acceptance provenance in existing helper
  paths

Must prove:

- reviewed closure/memory transitions record truthful actor attribution
- no second provenance system is introduced

### R1-G2 Review

Goal:

- review the provenance hardening for hidden attribution drift

### R1-G3 Testing

Goal:

- validate truthful review submission / acceptance attribution
- reject malformed or misleading attribution shapes where applicable

### R1-G4 Evolution

Goal:

- extract durable runtime review-provenance method rules

## Boundaries

Allowed:

- narrow helper/runtime updates
- narrow DB-backed tests
- metadata-discipline hardening within existing runtime objects

Not allowed:

- new review object families
- broad API/UI work
- notifications
- graph/retrieval work
- benchmark integration
