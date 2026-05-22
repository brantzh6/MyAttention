# IKE Claude Code B2 Memdir Study

## Purpose

This document records the controller-level `B2` study of the `memdir`
subsystem in `Claude Code`.

It is based on direct inspection of:

- `D:\claude-code\src\memdir\memdir.ts`
- `D:\claude-code\src\memdir\memoryTypes.ts`
- `D:\claude-code\src\memdir\findRelevantMemories.ts`
- `D:\claude-code\src\services\extractMemories\extractMemories.ts`

## Overall Judgment

`memdir` is the strongest first reusable pattern cluster found so far in
`Claude Code`.

Current recommendation:

- `study`

Potential next recommendation after a bounded IKE prototype:

- `prototype`

## What Memdir Actually Is

`memdir` is not just a note store.
It is a memory subsystem with four distinct characteristics:

1. typed memory taxonomy
2. entrypoint/index discipline
3. retrieval-time relevance filtering
4. background extraction from transcripts

This makes it strategically relevant to IKE because the current IKE gap is not
simply “we need more notes”.
The gap is:

- weak procedural capture
- weak memory structure
- weak connection between task completion and durable improvement

## Key Findings

### 1. Typed memory taxonomy is real, not decorative

Evidence:

- `memoryTypes.ts` defines exactly four memory types:
  - `user`
  - `feedback`
  - `project`
  - `reference`
- each type includes:
  - what it means
  - when to save it
  - how to use it
  - examples
  - what not to save

Why this matters:

- the taxonomy constrains memory scope
- it prevents uncontrolled dumping of code facts into memory
- it separates durable guidance from derivable workspace state

IKE relevance:

- highly relevant
- IKE needs typed procedural memory, not undifferentiated memory blobs

### 2. The entrypoint/index pattern is explicit

Evidence:

- `memdir.ts` defines `MEMORY.md` as the entrypoint
- entrypoint size is bounded by line and byte caps
- large details are pushed into topic files instead of bloating the entrypoint

Why this matters:

- working memory stays inspectable
- the model gets a stable top-level memory map
- detail is available without making the main prompt collapse under weight

IKE relevance:

- highly relevant
- this directly maps to the “active work surface understandable” problem

### 3. Memory retrieval is selective, not naive

Evidence:

- `findRelevantMemories.ts` scans memory headers
- uses a side model query to select up to 5 clearly useful memories
- filters out already surfaced files
- explicitly avoids re-surfacing irrelevant tool docs during active tool use

Why this matters:

- memory is treated as a retrieval problem, not just storage
- relevance is bounded
- prompt budget is protected

IKE relevance:

- highly relevant
- supports both token-pressure reduction and active-surface clarity

### 4. Memory extraction runs in the background

Evidence:

- `extractMemories.ts` runs at the end of a query loop
- uses a forked-agent pattern
- shares prompt cache
- is strongly permission-bounded
- skips redundant extraction if the main agent already wrote memory

Why this matters:

- procedural improvement is captured without blocking the main interaction loop
- memory extraction is treated as a secondary controlled workflow
- this is much closer to an evolution-support subsystem than a notes feature

IKE relevance:

- highest-value finding in this packet
- directly relevant to:
  - memory capture
  - procedural learning
  - controlled delegation

## What Should Be Reused

### Reusable pattern 1: typed memory taxonomy

Best transfer idea:

- IKE should adopt a small typed memory taxonomy for durable non-derivable
  knowledge

Candidate IKE-oriented categories:

- `user`
- `feedback`
- `project`
- `reference`
- `procedure`
- `source_quality`

Controller note:

- do not import Claude Code taxonomy unchanged
- but the discipline itself is reusable

### Reusable pattern 2: bounded index plus detail files

Best transfer idea:

- a compact memory entrypoint should summarize what exists
- deeper details should live in bounded topic files or structured records

Why:

- helps prompt efficiency
- helps human inspection
- helps future retrieval

### Reusable pattern 3: background extraction after task completion

Best transfer idea:

- IKE should consider extraction after:
  - bounded study completion
  - decision handoff
  - successful task closure

This is stronger than ad hoc memory saving because it links:

- work performed
- lesson extracted
- durable memory written

### Reusable pattern 4: selective memory retrieval

Best transfer idea:

- IKE memory recall should select only clearly useful memory slices
- not dump all historical memory into the active context

## What Should Not Be Copied Directly

### 1. Taxonomy details as-is

Why:

- Claude Code serves a coding assistant product
- IKE serves a broader evolving knowledge/research system

So:

- the structure is reusable
- the exact categories are not authoritative for IKE

### 2. Product-specific prompt prose

Why:

- much of the prompt text is tuned for Claude Code behavior and user model
- IKE needs its own task semantics and evolution semantics

### 3. Full memory implementation shape

Why:

- Claude Code uses filesystem-local memory conventions
- IKE may need hybrid structured storage, runtime artifacts, and durable object
  links

So:

- do not copy storage form wholesale
- study the control pattern, not the exact persistence format

## Mainline Gap Mapping

### Gap: memory capture and procedural improvement are still weak

Support level:

- `direct`

Mechanism:

- background extraction after work completion
- typed durable memory
- explicit “what not to save” discipline

### Gap: make active work surface understandable

Support level:

- `partial`

Mechanism:

- bounded memory entrypoint
- relevance filtering
- top-level memory map instead of unstructured accumulation

### Gap: reduce token pressure through controlled delegation

Support level:

- `partial`

Mechanism:

- side-query memory selection
- forked extraction outside the main loop
- bounded recall set

## Current Best Prototype Candidate

Candidate:

- `IKE procedural memory extraction`

Bounded idea:

- after a bounded benchmark study or decision handoff completes,
  generate a small structured memory candidate containing:
  - lesson type
  - why it mattered
  - how to apply it later
  - confidence
  - source artifact reference

Do not start with full user/project/reference coverage.
Start with:

- `procedure`
- `feedback`
- possibly `reference`

## Current Recommendation

Recommendation:

- `accept_with_changes`

Reason:

- the study is strong enough to advance
- but the next step should be a very small IKE-oriented prototype plan, not a
  direct implementation jump

## Next Packet

Next best packet:

- `Claude Code B3 Procedural Memory Prototype Plan`

That packet should answer:

1. where IKE would trigger memory extraction
2. what minimal taxonomy IKE should use first
3. what should be stored as memory vs remain derivable artifact
4. what the smallest safe prototype would be
