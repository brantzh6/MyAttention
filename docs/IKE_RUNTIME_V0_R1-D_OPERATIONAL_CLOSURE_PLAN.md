# IKE Runtime v0 R1-D Operational Closure Plan

## Purpose

`R1-D` is the first phase after truth-layer hardening.

Its job is to prove that the runtime kernel can support a truthful operational
closure loop:

- reviewed upstream work
- reconstructed work context
- trusted memory packet promotion

without inventing a second truth source.

## Why This Phase Exists

The runtime kernel now has:

- stable task state truth
- stable claim/lease truth
- DB-backed validation for the kernel foundation

What it still lacks is a closed operational loop showing that:

1. current work state can be reconstructed for controller/delegate continuity
2. reviewed upstream work can produce a trusted memory artifact
3. trusted memory remains derivative, not canonical

## Core Scope

### R1-D1 Coding

Goal:

- wire `WorkContext` reconstruction and `MemoryPacket` acceptance into a narrow
  runtime-backed service/helper path

Must prove:

- `WorkContext` is rebuilt from canonical runtime truth
- accepted `MemoryPacket` records require reviewed upstream linkage
- no mutable second truth source is introduced

### R1-D2 Review

Goal:

- review the operational closure path for second-truth drift

Focus:

- `WorkContext` not becoming canonical
- packet trust not bypassing review
- accepted-upstream linkage remaining explicit

### R1-D3 Testing

Goal:

- add runtime-backed tests for:
  - reconstructable `WorkContext`
  - trusted packet promotion
  - rejection of invalid trusted-memory promotion

### R1-D4 Evolution

Goal:

- capture what the phase proves about runtime closure-to-memory discipline
- preserve future-but-not-now improvements without broadening implementation

## Boundaries

Allowed:

- narrow service/helper integration
- narrow DB-backed tests
- narrow controller-facing runtime truth proofs

Not allowed:

- runtime UI expansion
- benchmark integration
- notification/follow-up mesh
- graph memory
- semantic retrieval
- new first-class runtime object families

## Acceptance Standard

1. `WorkContext` can be reconstructed from runtime truth after state change
2. accepted `MemoryPacket` records are tied to reviewed upstream work
3. non-accepted packets are still excluded from trusted recall
4. no second truth source is introduced
5. narrow runtime validation is green

## Output

This phase should materialize as:

- `R1-D1` coding brief
- `R1-D2` review brief
- `R1-D3` testing brief
- `R1-D4` evolution brief
