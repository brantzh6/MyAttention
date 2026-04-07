# IKE MAGMA and Chronos Memory Research Note

## Purpose

This note records a controller-level research judgment on two memory-relevant
research tracks mentioned during current IKE runtime planning:

- `MAGMA`
- `Chronos`

The goal is not to collect names.
The goal is to decide:

- what each contributes
- what is strategically relevant to IKE
- what should be borrowed now
- what should remain future-facing

## Primary Sources Reviewed

### MAGMA

- [MAGMA: A Multi-Graph based Agentic Memory Architecture for AI Agents](https://arxiv.org/abs/2601.03236)

Important distinction:

- this is the **memory architecture** MAGMA paper
- not the separate Microsoft multimodal foundation model also named `Magma`

### Chronos

- [Chronos: Temporal-Aware Conversational Agents with Structured Event Retrieval for Long-Term Memory](https://arxiv.org/abs/2603.16862)

## Core Judgment

Both are relevant.
But they help at different layers.

- `Chronos` is immediately relevant to **temporal/event-aware retrieval and
  long-horizon conversational memory**
- `MAGMA` is immediately relevant to **structured memory topology**

Neither should be copied wholesale into `IKE Runtime v0`.
But both strengthen the current IKE direction that:

- memory cannot be a flat vector store
- memory must be structured
- time and events are first-class
- retrieval must be selective and typed

## 1. What Chronos Contributes

Chronos is valuable because it emphasizes:

- structured event extraction
- temporal spans
- retrieval guided by time constraints
- iterative multi-hop memory tool use

### Why This Matters

IKE currently needs to answer questions like:

- what happened recently in this project
- what was decided before this task was blocked
- what changed between two benchmark passes
- which event triggered the current next action

Flat semantic recall is not enough for these.
Chronos reinforces that long-term agent memory needs:

- event-shaped storage
- time-aware filtering
- retrieval paths that understand chronology, not only semantic similarity

### Immediate IKE Relevance

Chronos is directly relevant to:

- `TaskEvent`
- `Decision` timelines
- `WorkContext` restoration
- benchmark event capture
- future event-triggered follow-up flows

### Immediate Borrowing Recommendation

Borrow now:

- event-shaped memory objects
- explicit temporal metadata
- time-aware recall paths
- distinction between event retrieval and semantic retrieval

Do not borrow yet:

- full conversational memory pipeline as the primary kernel
- heavy query orchestration before task/state truth is stable

## 2. What MAGMA Contributes

MAGMA is valuable because it argues that agent memory should not be represented
as one undifferentiated retrieval pool.

Its multi-graph perspective highlights that memory relationships may need
different structural views, including:

- semantic
- temporal
- causal
- entity-centered

### Why This Matters

IKE is already moving toward memory layers such as:

- session
- task
- semantic
- episodic
- procedural

MAGMA reinforces that this separation is not just a convenience.
It is an architectural necessity if the system must later support:

- explanation
- replay
- cross-reference reasoning
- procedural improvement
- long-horizon agent continuity

### Immediate IKE Relevance

MAGMA is directly relevant to:

- procedural memory evolution
- cross-object relationship design
- benchmark evidence graphs
- future knowledge / event / task relationship modeling

### Immediate Borrowing Recommendation

Borrow now:

- the principle that memory needs multiple structural views
- explicit relation modeling
- temporal and causal distinctions
- stronger separation between memory item and memory relation

Do not borrow yet:

- a full graph-native memory engine as the runtime kernel
- large graph infrastructure before `Project / Task / Decision / WorkContext`
  state is stable

## 3. What This Means For IKE Runtime v0

The current runtime priority remains correct:

1. stable project/task/decision state
2. memory packet and work-context restoration
3. checkpoint and event history
4. closure-to-memory

`MAGMA` and `Chronos` do **not** invalidate that order.
They strengthen it.

The right current reading is:

- Chronos says: your runtime must treat time/events as first-class
- MAGMA says: your runtime must not collapse all memory into one flat store

Therefore:

- Postgres-backed runtime state remains the correct first step
- Redis remains acceleration, not truth
- object storage remains payload backing
- memory recall later becomes typed and relation-aware on top of this kernel

## 4. Current IKE Recommendation

### Adopt Now

- explicit `TaskEvent`
- explicit temporal fields and time-scoped retrieval
- typed memory layers
- relation-aware memory design
- clear separation between runtime truth and recall layer

### Defer

- full graph memory engine
- large-scale memory graph traversal system
- complex agentic multi-hop retrieval runtime as the default control layer

## 5. Strategic Conclusion

The research direction is valid:

- Claude Code gives a strong engineering reference for procedural memory and
  selective recall
- Chronos strengthens the temporal/event side
- MAGMA strengthens the structural/relational side

Together they support a future IKE memory direction that is:

- typed
- temporal
- event-aware
- relation-aware
- selective
- closure-driven

But `IKE Runtime v0` should still start with:

- durable state kernel first
- richer memory architecture second

That is the stable path.

