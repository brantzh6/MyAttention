# IKE Runtime v0 Document and Memory Governance

## Core Judgment

Documentation is necessary, but documentation alone is not stable enough to act
as the runtime control kernel.

Reasons:

- documents are loosely structured
- documents are editable by humans and tools
- documents are not safe as the only transactional state
- documents are not enough for queueing, leasing, resume, or recovery

Therefore the system must distinguish four layers:

1. durable runtime state
2. auditable artifacts
3. human-readable documents
4. runtime recall / memory

These layers must cooperate, not collapse into one.

## 1. The Four Layers

### 1.1 Durable Runtime State

This is the source of truth for active control.

Examples:

- `Project`
- `Task`
- `Decision`
- `MemoryPacket` metadata
- `WorkContext`
- `TaskEvent`
- `TaskCheckpoint`

Required properties:

- transactional
- queryable
- versionable
- recoverable
- not dependent on chat replay

Storage:

- PostgreSQL first

### 1.2 Auditable Artifacts

These are outputs that support reasoning, review, and replay.

Examples:

- study result
- benchmark report
- closure payload
- review packet
- large memory snapshot

Required properties:

- immutable or append-only by default
- referenced by runtime state
- content-addressable or versioned when possible

Storage:

- object storage for heavy payloads
- metadata in Postgres

### 1.3 Human-Readable Documents

Documents are for:

- design intent
- long-lived methods
- architectural boundaries
- phase plans
- review packets
- operator handoff

Documents are **not** the only place where current runtime truth should live.

Documents should answer:

- what the system is supposed to do
- why a design exists
- what changed at a milestone
- what method should be followed

Documents should not be the only mechanism for answering:

- what task is active right now
- what is blocked right now
- what lease expired
- what decision is the latest accepted decision

### 1.4 Runtime Recall / Memory

Memory is the selective retrieval layer that makes current work possible.

Memory should pull from:

- runtime state
- artifacts
- stable semantic memory
- procedural memory

Memory should not be a free-form substitute for the layers above.

Short version:

- documents leave things behind
- runtime state keeps system truth
- artifacts preserve evidence
- memory brings the relevant parts back

## 2. Why Search Alone Is Not Enough

If the system only:

- searches documents
- searches chat history
- searches artifacts ad hoc

then it cannot reliably distinguish:

- current truth vs stale design
- accepted decision vs draft idea
- active task vs historical task
- stable method vs abandoned experiment

Therefore search is a retrieval mechanism, not a truth model.

## 3. Stability Rules

### Rule 1: Current control state must live in structured objects

Current active control state must come from runtime objects, not inferred only
from markdown.

### Rule 2: Documents must mirror, not replace, structured truth

For active work:

- runtime object = control truth
- document = readable mirror or design explanation

### Rule 3: Important documents must be versioned and milestone-linked

Methods, architecture, and phase decisions should be:

- committed in Git
- reflected in `CHANGELOG.md`
- reflected in `PROGRESS.md` or handoff docs when operationally relevant

### Rule 4: Artifacts should be immutable by default

Study outputs and closures should not be silently overwritten.

Prefer:

- new version
- parent linkage
- accepted/rejected status

### Rule 5: Memory packets are derived, not authoritative

`MemoryPacket` should be treated as:

- compact recovery carriers
- resumable working summaries

They should be derived from accepted state and accepted artifacts, not replace
them.

## 4. Anti-Patterns

Do not rely on:

- a markdown file as the only current task list
- chat transcript as the only recovery source
- Redis keys as the only active-state truth
- mutable benchmark report as the only study output
- ad hoc search to reconstruct controller state

These all create hidden drift.

## 5. Recommended Governance Model

### 5.1 For Runtime Truth

Use:

- PostgreSQL

### 5.2 For Heavy Evidence

Use:

- object storage

### 5.3 For Fast Access

Use:

- Redis as cache/queue/lease acceleration

### 5.4 For Human Handoff

Use:

- docs
- changelog
- progress
- handoff notes

### 5.5 For Work Recall

Use:

- `MemoryPacket`
- typed memory layers
- selective recall from runtime state + artifacts

## 6. Change Safety

Because documents can be modified by:

- humans
- agents
- tooling

important operational documents should be treated as controlled surfaces.

Recommended rules:

- architecture/method docs require milestone recording when materially changed
- handoff docs should stay short and operational
- benchmark conclusions should point to evidence artifacts
- accepted runtime decisions should not depend on free-form document edits

## 7. Practical Meaning For IKE Runtime v0

`IKE Runtime v0` should not be built as:

- a document search system
- a memory file pile
- a chat-history replay engine

It should be built as:

- a structured state kernel
- an artifact-backed evidence system
- a document-supported human operating layer
- a memory layer that selectively rehydrates the right state

## 8. Current Recommendation

Going forward:

1. keep methods and architecture in docs
2. move active task/decision/work state into runtime objects
3. treat artifacts as append-only evidence surfaces
4. generate memory packets from accepted state and evidence
5. use search only as retrieval, never as the sole truth model

This is the only stable way to avoid:

- silent document drift
- stale context reuse
- hidden controller state
- memory hallucination
- chat-dependent recovery

