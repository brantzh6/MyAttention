# IKE Long-Horizon Backlog and Decision Log

## Purpose

This document exists to prevent a recurring failure mode:

- short-term review correctly narrows scope
- valuable long-term ideas are acknowledged
- but then disappear because they are neither current mainline work nor formal
  rejected items

This file is the holding structure for:

- strategically valuable but deferred work
- future-facing architecture directions
- research lines that should not be forgotten
- decisions that are "not now", not "no"

It is not a current sprint backlog.
It is not a vague wish list.
It is the durable record of:

- what matters later
- why it matters
- why it is deferred now
- what condition should reactivate it

## Status Categories

Each item should be placed in one of these buckets:

- `active_now`
- `deferred_but_committed`
- `watch_and_research`
- `not_before_prerequisite`
- `rejected`

Important distinction:

- `deferred_but_committed` means the direction is still strategically accepted
- `rejected` means the direction should not silently come back

## 1. Current Long-Horizon Directions

### 1.1 Thinking Model Armory

Status:

- `active_now`

Why it matters:

- benchmark execution methods are downstream of thinking models
- without a clear armory, method selection will continue to drift

Current state:

- now materially addressed by
  [D:\code\MyAttention\docs\IKE_THINKING_MODELS_AND_METHOD_ARMORY.md](/D:/code/MyAttention/docs/IKE_THINKING_MODELS_AND_METHOD_ARMORY.md)

Notes:

- still needs later refinement, but it is no longer an unrecorded deferred idea

### 1.2 Rich Typed Memory Architecture

Status:

- `deferred_but_committed`

Why it matters:

- IKE will ultimately need typed, layered, selective memory
- this is reinforced by Claude Code, Chronos, and MAGMA research

Why deferred now:

- current priority is durable state kernel, not advanced memory engine

Reactivation condition:

- after `Project / Task / Decision / WorkContext / MemoryPacket` truth model is
  stable

Notes:

- future direction includes:
  - temporal memory
  - event-aware memory
  - relation-aware memory
  - procedural memory evolution
- after `R2-A`, procedural memory evolution should no longer remain an implicit
  carry item; it must receive a formal planned reactivation point
- formal scheduling note:
  - [D:\code\MyAttention\docs\IKE_STRATEGIC_SCHEDULING_NOTE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_STRATEGIC_SCHEDULING_NOTE_2026-04-08.md)
- current planned placement:
  - after `R2-B`
  - likely `R2-C` or `R3`, depending on runtime gate outcome

### 1.3 Event- and Time-Aware Retrieval

Status:

- `watch_and_research`

Why it matters:

- chronology is essential for task recovery, benchmark evolution, and decision
  traceability

Why deferred now:

- event/time structures should sit on top of a stable runtime state kernel

Reactivation condition:

- once `TaskEvent` and recovery flows are implemented in runtime v0

### 1.4 Relation-Aware / Multi-View Memory Topology

Status:

- `watch_and_research`

Why it matters:

- flat memory retrieval will not be enough for long-horizon IKE evolution

Why deferred now:

- current runtime truth model is more urgent than graph-native memory

Reactivation condition:

- after runtime v0 and at least one real closure-to-memory loop are proven

### 1.5 Knowledge / Research Trigger Integration

Status:

- `not_before_prerequisite`

Why it matters:

- runtime kernel should eventually support benchmark/research/evolution
  workflows end to end

Why deferred now:

- runtime kernel should first prove memory/task/decision control without trying
  to carry the full research system

Prerequisite:

- runtime v0 stable
- benchmark method frame stable
- closure flow stable

### 1.6 Notification / Follow-Up Surfaces

Status:

- `watch_and_research`

Why it matters:

- controller/delegate continuity will eventually need explicit notification and
  follow-up objects

Why deferred now:

- not required to prove the v0 kernel

Reactivation condition:

- after task state, review gate, and work context are stable

### 1.7 Object Access Layer / Stable Retrieval

Status:

- `not_before_prerequisite`

Why it matters:

- long-term IKE will need stable object reads and richer object lifecycle

Why deferred now:

- current system truth is not yet ready for fake durability

Prerequisite:

- canonical object identity
- stable runtime truth
- accepted persistence rules

### 1.8 Claude Code-Inspired Runtime Borrowing

Status:

- `deferred_but_committed`

Why it matters:

- Claude Code remains a high-value reference for:
  - procedural memory
  - selective recall
  - permissions
  - coordinator patterns

Why deferred now:

- only the narrowest borrowable patterns should be adopted before runtime v0 is
  stable

Reactivation condition:

- after runtime v0 has a stable task and memory kernel

### 1.9 Second and Third Benchmark Generalization

Status:

- `deferred_but_committed`

Why it matters:

- `harness` alone cannot prove benchmark method generalization

Why deferred now:

- `harness` entity judgment and benchmark method frame still need tightening

Reactivation condition:

- once benchmark method frame is fixed and `harness` is rerun under it

Notes:

- after `R2-A`, the second concept benchmark should receive a formal planned
  phase/schedule rather than continuing as an implicit deferred direction
- formal scheduling note:
  - [D:\code\MyAttention\docs\IKE_STRATEGIC_SCHEDULING_NOTE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_STRATEGIC_SCHEDULING_NOTE_2026-04-08.md)
- current planned placement:
  - after `R2-B`
  - likely `R2-C` if the runtime gate passes

### 1.10 First-Class Test Agent System

Status:

- `active_now`

Why it matters:

- coding and review alone are not enough for runtime, trust-boundary, and
  closure work

Why now:

- current packets already show the need for independent validation

Current state:

- now materially addressed by
  [D:\code\MyAttention\docs\PROJECT_TEST_AGENT_AND_VALIDATION_MATRIX.md](/D:/code/MyAttention/docs/PROJECT_TEST_AGENT_AND_VALIDATION_MATRIX.md)

### 1.11 First-Class Evolution Loop

Status:

- `active_now`

Why it matters:

- without an explicit evolution leg, valuable review findings still risk
  disappearing into chat or controller memory

Why now:

- the project is already generating repeated review/closure artifacts

Current state:

- now materially addressed by
  [D:\code\MyAttention\docs\PROJECT_EVOLUTION_LOOP_AND_METHOD_UPGRADE.md](/D:/code/MyAttention/docs/PROJECT_EVOLUTION_LOOP_AND_METHOD_UPGRADE.md)

## 2. Runtime v0-Specific Deferred Items

These are not rejected.
They are intentionally not in the first implementation cut.

### 2.1 Full Outbox Dispatcher

Status:

- `not_before_prerequisite`

Reason:

- conceptually valuable
- maybe too heavy for the first cut if single-process flow is enough

Prerequisite:

- confirm that direct transaction-bound side effects are insufficient

### 2.2 Persistent Notification Object

Status:

- `watch_and_research`

Reason:

- likely useful later

### 2.3 DB-Level Append-Only Enforcement for Task Events

Status:

- `deferred_but_committed`

Why it matters:

- append-only intent is stronger when enforced at the database level than only
  at API/service discipline

Why deferred now:

- second-wave first priority is claim/trust hardening and migration proof

Reactivation condition:

- after `R1-A` hardening pack is complete

### 2.4 Lease Renewal / Heartbeat Hardening

Status:

- `watch_and_research`

Why it matters:

- longer-running delegated work may later need stronger lease renewal semantics

Why deferred now:

- v0 can remain on simpler expiry/recovery semantics if hardening closes the
  current claim path risk

Reactivation condition:

- once real task lifecycle packets reveal that simple expiry is insufficient

### 2.5 Queryable Upstream Trust Model for Memory

Status:

- `deferred_but_committed`

Why it matters:

- trusted recall should ultimately rely on queryable upstream truth, not only
  JSONB linkage markers

Why deferred now:

- first hardening step is existence verification, not a full schema redesign

Reactivation condition:

- after second-wave hardening proves the narrower trust gate

### 2.6 First Real Task Lifecycle Proof

Status:

- `active_now`

Why it matters:

- first-wave proves components, not yet a full real runtime lifecycle

Why now:

- current second-wave should prove one narrow real task path through the kernel

### 2.7 Narrow Kernel-to-Benchmark Integration

Status:

- `active_now`

Why it matters:

- runtime kernel must connect back to real benchmark/observation work, not stay
  isolated as designware

Why now:

- after first-wave execution, a narrow integration slice is the next truthful
  proof step

### 2.8 Development-Process Multi-Agent Proof

Status:

- `active_now`

Why it matters:

- future IKE runtime is a multi-brain system, so project development should
  begin proving controller/coding/review/testing/evolution collaboration in
  practice

Why now:

- second-wave runtime hardening is the right narrow place to prove this without
  opening a broad new branch

### 2.3 Richer Lease Policy and Concurrency Hardening

Status:

- `deferred_but_committed`

Why it matters:

- runtime lease behavior will eventually need stronger renewal, heartbeat,
  concurrency-claim, and reclaim semantics than the first-cut v0 defaults

Why deferred now:

- first priority is proving the durable kernel and basic expiry recovery

Reactivation condition:

- after `R0-C` is implemented and real recovery behavior is observed

Notes:

- future design should revisit:
  - lease renewal policy
  - heartbeat policy
  - concurrent claim safety
  - rebuild behavior for active leases after Redis loss

### 2.4 Cause-Based State Semantics Beyond Label-Level v0

Status:

- `watch_and_research`

Why it matters:

- long term, state labels alone may be insufficient; richer cause-based
  semantics may be needed for pause/block/review/retry reasoning

Why deferred now:

- v0 should first prove the compressed state machine without re-expanding the
  state model

Reactivation condition:

- after `R0-B` is implemented and controller review shows repeated ambiguity
  that cannot be solved by current fields plus events

### 2.5 Full Outbox Dispatcher and Side-Effect Hardening

Status:

- `not_before_prerequisite`

Why it matters:

- the full outbox-dispatcher pattern may become necessary once side effects go
  beyond simple first-cut runtime behavior

Why deferred now:

- v0 can keep the outbox object and architectural slot without forcing a full
  dispatcher implementation on day one

Prerequisite:

- evidence that direct first-cut side-effect handling is insufficient

### 2.6 Stronger Review-to-Recall Trust Filtering

Status:

- `deferred_but_committed`

Why it matters:

- trusted recall should ultimately enforce stronger filtering rules than the
  minimal `accepted-upstream linkage` in first-cut v0

Why deferred now:

- current priority is proving that untrusted packets do not masquerade as
  accepted memory

Reactivation condition:

- after `R0-E` is implemented and the first real memory promotion flows exist
- not essential for proving the first kernel

### 2.7 Queryable Upstream Linkage for MemoryPacket Trust

Status:

- `deferred_but_committed`

Why it matters:

- accepted `MemoryPacket` trust should eventually depend on explicit,
  queryable upstream references rather than linkage hidden inside JSONB

Why deferred now:

- current priority is proving the first truthful trust boundary, not widening
  the schema before the kernel baseline is stable

Reactivation condition:

- after `R0-E` is accepted and the first real recall/review flows are observed

### 2.8 DB-Backed Upstream Existence Verification for Trusted Recall

Status:

- `not_before_prerequisite`

Why it matters:

- future trusted recall should verify that linked upstream task/decision
  objects really exist and remain valid, not just that linkage fields are
  present

Why deferred now:

- first-cut v0 only needs to prove that packets cannot become trusted without
  explicit upstream linkage

Prerequisite:

- stable runtime task/decision persistence
- accepted memory-packet baseline
- evidence that metadata-only linkage is no longer sufficient

### 2.9 Real Redis Execution Adapter and Acceleration Observability

Status:

- `deferred_but_committed`

Why it matters:

- first-cut `R0-F` proves truthful command generation and rebuild semantics,
  but production runtime use will need a thin real execution layer with
  pipeline handling, failure reporting, and basic acceleration observability

Why deferred now:

- current priority is proving Redis remains acceleration only, not building a
  full operational Redis subsystem

Reactivation condition:

- after `R0-F` baseline is accepted and real runtime usage starts consuming
  queue/pointer rebuild commands

### 2.10 Unified Incremental Queue Sync Discipline

Status:

- `watch_and_research`

Why it matters:

- runtime should eventually converge on one truthful incremental queue-sync
  contract so callers do not drift between rebuild-style helpers and
  transition-style helpers

Why deferred now:

- first-cut runtime can tolerate separate helper surfaces while kernel
  semantics are still stabilizing

Reactivation condition:

- after first real runtime integration exposes repeated ambiguity between
  rebuild helpers and state-transition sync helpers

### 2.3 Expanded State Machine

Status:

- `watch_and_research`

Reason:

- later versions may need richer distinction between
  `blocked / waiting / paused / dropped / cancelled`
- but v0 may need simplification

## 3. Decision Logging Rules

Whenever a design is narrowed in review, do not just decide:

- "do now"
- "do not do now"

Also record:

- is it strategically accepted later?
- what bucket is it in?
- what reactivation condition should bring it back?

If that is missing, the item will be forgotten.

## 4. Current Recommendation

From now on, every major review should classify deferred ideas into this file.

That is the only reliable way to prevent:

- short-term scope discipline from erasing long-term strategy
- good ideas from vanishing between review rounds
- repeating the same strategic discussion from scratch
