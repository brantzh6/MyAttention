# IKE Runtime Evolution Roadmap

## Purpose

This document prevents `IKE Runtime v0` from becoming a local optimum.

It does not expand the current implementation scope.
It defines:

- what `v0` is for
- what must come after `v0`
- what is explicitly deferred
- what must not be implemented too early

## Design Rule

`v0` must be designed tightly enough to implement safely, but loosely enough
that later stages can extend it without rewriting the kernel.

Therefore:

- `v0` gets implementation-grade detail
- `v0.1 / v1 / v2` get capability-grade roadmapping
- long-horizon items remain durable backlog entries until prerequisites exist

## Long-Horizon Direction

`IKE Runtime` is expected to evolve toward:

1. durable operational truth
2. recoverable task and decision governance
3. typed procedural and semantic memory
4. temporal and event-aware retrieval
5. stronger closure-to-memory integration
6. richer evolution/governance integration
7. broader IKE control-plane integration

It is not intended to become:

- a chat-history state store
- a document-only operating system
- a premature graph-memory platform
- a giant general workflow engine before kernel stability

## Version Path

### v0: Durable State Kernel

Primary goal:

- establish the first trustworthy runtime kernel

Must include:

- `Project`
- `Task`
- `Decision`
- `MemoryPacket`
- `WorkContext`
- task events
- task relations
- checkpoints
- leases
- recovery model

Success criteria:

- tasks have clear durable state transitions
- controller/delegate/reviewer boundaries are explicit
- runtime can recover from restart and lease loss
- docs are no longer acting as the only active-state source
- memory candidates can be attached truthfully to reviewed upstream work

Must not expand into:

- full graph memory
- notification mesh
- public durable object retrieval for everything
- broad autonomy beyond review-gated governance

### v0.1: Operational Closure Layer

Primary goal:

- make runtime closure more usable without redefining the kernel

Expected additions:

- better `WorkContext` reconstruction and narrowing
- clearer closure-to-memory routing
- stronger accepted-upstream linkage for `MemoryPacket`
- limited notification/follow-up surfaces
- better controller-facing task visibility

Entry condition:

- `v0` state kernel is stable enough that closure outputs do not drift

Do not do yet:

- global memory graph
- heavy semantic retrieval engine
- broad multi-project orchestration marketplace logic

### v1: Structured Memory and Retrieval Layer

Primary goal:

- move from durable state only to durable state plus useful memory

Expected additions:

- richer typed memory taxonomy
- temporal/event-aware retrieval
- relation-aware memory traversal
- explicit promotion paths from closure artifacts into trusted memory objects
- stronger retrieval discipline for controller/delegate continuity

Entry condition:

- `v0` and `v0.1` prove that upstream truth is stable enough to back memory

Risks to avoid:

- inventing semantic truth without accepted upstream evidence
- letting retrieval become a second hidden state system

### v2: Governance and Evolution Integration

Primary goal:

- connect runtime state and memory to stronger evolution/governance behavior

Expected additions:

- stronger benchmark/research closure integration
- decision follow-through and escalation surfaces
- richer evaluation operations
- controlled semi-autonomous workflows
- broader IKE control-plane integration

Entry condition:

- memory and closure pipelines already produce trustworthy inputs

Do not assume:

- full autonomy
- fully automatic method adoption
- unconstrained delegate execution

## Deferred but Committed Threads

These are not current implementation targets, but they are expected future
threads:

- notification and follow-up surfaces
- object access layer
- relation-aware memory topology
- temporal replay and event retrieval
- benchmark generalization beyond `harness`
- Claude Code inspired runtime borrowing beyond `memdir`

They should remain tracked in:

- [D:\code\MyAttention\docs\IKE_LONG_HORIZON_BACKLOG_AND_DECISION_LOG.md](/D:/code/MyAttention/docs/IKE_LONG_HORIZON_BACKLOG_AND_DECISION_LOG.md)

## Current Planning Rule

Until `v0` is implemented and validated:

- new design work should prefer tightening the kernel
- new review work should challenge reversibility risk
- new research work should be recorded as backlog or roadmap input
- new implementation should not bypass the state kernel in favor of ad hoc docs,
  chat state, or Redis-only control logic

## Immediate Next Design Milestone

Before implementation begins, the next design pass should finish:

1. compressed v0 state-machine revision acceptance
2. `MemoryPacket` acceptance semantics
3. lease-expiry recovery table finalization
4. JSONB discipline acceptance
5. implementation-readiness summary for the first runtime build slice
