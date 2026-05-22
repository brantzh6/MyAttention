# IKE Claude Code B1 Mapping

## Purpose

This document records the controller-level first-pass mapping from `Claude Code`
to IKE.

It is not a full subsystem audit.
It is the first accepted study output after:

- local primary artifact inspection of `D:\claude-code`
- structured secondary orientation from `.qoder/repowiki`

## Evidence Basis

Primary evidence inspected directly:

- `D:\claude-code\README.md`
- `D:\claude-code\src\context.ts`
- `D:\claude-code\src\QueryEngine.ts`
- `D:\claude-code\src\memdir\memdir.ts`
- `D:\claude-code\src\coordinator\coordinatorMode.ts`
- `D:\claude-code\src\utils\permissions\permissions.ts`

Secondary orientation:

- `D:\code\MyAttention\.qoder\repowiki\en\content\Project Overview.md`
- `D:\code\MyAttention\.qoder\repowiki\en\content\Architecture and Design\Architecture and Design.md`

## Accepted First-Pass Mapping

### 1. `memdir`

Judgment:

- highest-value first study target

Why:

- persistent memory directory pattern
- typed memory organization
- explicit memory prompt loading
- direct relation to IKE gap:
  - `memory capture and procedural improvement are still weak`

Current transferability judgment:

- `high`

### 2. `permissions`

Judgment:

- important but not first

Why:

- rule + classifier layering is relevant
- directly touches:
  - safer delegation
  - less brittle tool approval
  - evolution beyond pure rule-engine checks

Current transferability judgment:

- `medium`

### 3. `coordinator mode`

Judgment:

- important for controlled delegation study

Why:

- task lifecycle
- worker orchestration
- scratchpad / worker context
- directly relevant to:
  - `task / experiment / closure substrate still immature`
  - `reduce token pressure through controlled delegation`

Current transferability judgment:

- `medium`

### 4. `context.ts`

Judgment:

- useful pattern reference, but not a direct blueprint

Why:

- shows memoized workspace context injection
- useful for thinking about active work surface
- still heavily code-workspace-centric

Current transferability judgment:

- `medium` for mechanism
- `weak` for direct reuse

### 5. `QueryEngine`

Judgment:

- broad importance, low immediate transfer value

Why:

- central orchestration is real
- implementation is tightly coupled to Claude Code product/runtime/UI choices

Current transferability judgment:

- `low`

## Reusable Pattern Candidates

Current best candidates:

1. typed memory taxonomy + indexed memory directory
2. forked/background memory extraction pattern
3. rule-first plus model-assisted gate pattern
4. worker lifecycle and notification protocol

## Non-Transferable Or Low-Value Areas

Current examples:

- React/Ink terminal UI structure
- Bun-specific bundling choices
- Anthropic-specific streaming/tool API details
- product-coupled internals that do not map to IKE's mainline gaps

## Current Mainline Relevance

Most relevant current IKE gaps:

- memory capture and procedural improvement are still weak
- task / experiment / closure substrate still immature
- evolution is still too rule-engine heavy
- reduce token pressure through controlled delegation

## Current Recommendation

Recommendation:

- `study`

Next packet priority:

- `Claude Code B2 memdir study`

Reason:

- strongest direct fit to a current IKE gap
- bounded enough to study without widening scope
- likely to yield concrete reusable patterns and explicit non-transferable ones

## Known Limits

- this is still a first-pass mapping
- repowiki was useful for orientation but is not primary proof
- one delegated analysis result was content-useful but malformed JSON, so it was
  not accepted as-is
- this document reflects controller judgment backed by direct file inspection
