# IKE Claude Code Research Decision

## Decision

Do **not** split Claude Code research into a separate project yet.

Current decision:

- continue Claude Code research **inside the current IKE project**
- treat it as a strategic reference track
- only split into a standalone project later if the extracted patterns become clearly reusable across multiple projects

## Why Not Split Now

### 1. The current value is still IKE-directed

The current research is not generic enough yet.

It is being used to improve:

- IKE procedural memory
- IKE controller/delegate engineering
- IKE task closure
- IKE active work surface clarity
- IKE long-running AI-assisted development method

That means the nearest proof of value is still inside IKE.

### 2. Splitting now would create premature divergence

A separate repo would immediately create:

- another planning surface
- another review surface
- another maintenance surface
- risk of method drift between research and implementation

At the current maturity level, that cost is higher than the benefit.

### 3. The right test is “can this improve IKE in practice?”

The current stage should answer:

- does `memdir`-inspired procedural memory improve our workflow?
- do Claude-style constraints improve collaboration quality?
- do closure-to-memory patterns survive real benchmark use?

Until those answers are stronger, a separate project would mostly be organizational overhead.

## What To Do Now

Continue the Claude Code line in the current project as a staged reference track.

### Stage 1. Mapping

Already underway:

- subsystem mapping
- identify which parts are strategically valuable

### Stage 2. Focused study

Current focus order:

1. `memdir`
2. `permissions`
3. `coordinator`

### Stage 3. IKE-local prototype

Only borrow patterns through narrow prototypes:

- procedural memory
- truthful closure adapter
- bounded task/memory loops

### Stage 4. Validate inside real IKE work

Prove value through:

- benchmark closure
- procedural-memory candidates
- improved controller/delegate quality

## When To Split Into A New Project

Only split later if most of these become true:

1. at least 2-3 extracted patterns are clearly project-agnostic
2. the patterns are no longer tightly tied to IKE semantics
3. another project would plausibly benefit from the same harness/memory/runtime layer
4. the standalone surface is clearer than keeping it embedded

Examples of possible future standalone outcomes:

- agent memory harness
- AI development control plane
- procedural-memory runtime
- task closure / decision handoff toolkit

## Current Recommendation

Short-term recommendation:

- **research inside IKE**

Medium-term recommendation:

- **update the starter kit with validated lessons**

Long-term recommendation:

- **consider a standalone project only after the reusable layer is proven**
