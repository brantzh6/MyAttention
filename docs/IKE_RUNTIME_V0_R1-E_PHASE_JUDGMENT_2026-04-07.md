# IKE Runtime v0 R1-E Phase Judgment

## Purpose

This note records the controller judgment for what should come immediately
after materially complete `R1-D`.

It exists to keep the runtime mainline from drifting into:

- broad UI/runtime integration
- notification mesh design
- premature retrieval/memory-engine expansion

## Current Baseline

What is now materially true:

- `R1-C` truth-layer work is materially complete
- `R1-D` operational closure is materially complete with durable fallback
  review coverage
- runtime can now:
  - reconstruct `WorkContext`
  - promote reviewed upstream work into trusted `MemoryPacket`
  - preserve closure truth without inventing a second source

## Candidate Next Phases Considered

### Option A: Wider delegated reruns only

Pros:

- more independent evidence

Why it is not the next phase:

- it is a validation activity, not the next runtime capability step
- it should accompany the next phase, not define it

### Option B: Project-facing visibility and pointer alignment

Meaning:

- connect runtime closure outputs back to the project-level pointer surface
- narrow the gap between:
  - durable closure truth
  - controller-facing current project state

Concrete scope:

- project-level `current_work_context_id` alignment
- truthful project-surface linkage to the active reconstructed context
- no broad UI/API expansion

Pros:

- directly follows the preserved `R1-D` gap
- matches the roadmap's v0.1 direction of better controller-facing visibility
- still stays inside runtime scope

### Option C: Notification/follow-up surfaces now

Why not now:

- still too early
- would broaden runtime operational surfaces before project-pointer truth is
  aligned

## Controller Decision

Accepted next phase:

- **`R1-E = Project Surface Alignment`**

Core target:

- make project-level current work visibility point at the now-proven runtime
  closure truth without broadening into a UI/runtime branch

## What R1-E Should Include

1. truthful update path for `RuntimeProject.current_work_context_id`
2. narrow project-facing helper proving active context visibility comes from
   runtime truth
3. tests proving project pointer alignment does not create a second truth source

## What R1-E Should Not Include

- broad task board/UI work
- notification mesh
- benchmark integration
- graph memory
- retrieval engine work

## Resulting Mainline Rule

After `R1-D`, do not jump to broader `v0.1` surfaces first.

Open:

- `R1-E Project Surface Alignment`

and keep it narrow.
