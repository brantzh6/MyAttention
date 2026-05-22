# IKE Runtime v0 Second-Wave Multi-Agent Cycle

## Purpose

This document turns the second-wave runtime direction into an explicit
multi-agent collaboration cycle.

The goal is not only to harden the runtime kernel.
It is also to make the project's own development process closer to the future
IKE collaboration model:

- controller
- coding
- review
- testing
- evolution

## 1. Why Second-Wave Must Be Multi-Agent

First-wave proved:

- bounded coding packets work
- controller review works
- durable review recording works

First-wave also revealed the next limit:

- controller still carries too much testing and evolution burden

Second-wave should therefore prove two things at once:

1. runtime hardening can proceed safely
2. development collaboration itself can run with a fuller multi-agent shape

## 2. Cycle Structure

### Controller

Owns:

- packet shape
- packet ordering
- acceptance/rejection
- review absorption

### Coding Agent

Owns:

- implementation of the hardening packet

Primary route:

- `openclaw-glm`

### Review Agent

Owns:

- semantic drift review
- scope drift review
- truth-boundary review

Primary route:

- `openclaw-kimi`

### Test Agent

Owns:

- independent validation of migration, claim, trust, and role restrictions

Primary route:

- use the project test-agent model even if the exact executor remains
  controller-assisted at first

### Evolution Agent

Owns:

- extracting method improvements from the hardening cycle
- preserving future-value findings
- proposing packet/harness/test upgrades

Primary route:

- `openclaw-kimi` or controller-assisted bounded analysis until a separate
  evolution delegate is stable

## 3. R1-A Packet Family

### R1-A1

- coding packet
- implement the hardening changes

### R1-A2

- review packet
- inspect the hardening patch for semantic truthfulness and enforcement gaps

### R1-A3

- test packet
- independently validate migration, claim gate, trust boundary, and force-path
  restrictions

### R1-A4

- evolution packet
- turn the hardening cycle into durable method updates and future backlog items

## 4. Entry Rule

Do not start `R1-B` or broader second-wave work until:

- `R1-A1` is implemented
- `R1-A2` review is complete
- `R1-A3` validation is complete
- `R1-A4` evolution absorption is recorded

## 5. Success Standard

This cycle succeeds if:

1. runtime hardening reduces caller-discipline dependency
2. testing is explicit and independent
3. evolution outputs are durable, not chat-only
4. the project's own collaboration method becomes more like the intended IKE
   runtime control model
