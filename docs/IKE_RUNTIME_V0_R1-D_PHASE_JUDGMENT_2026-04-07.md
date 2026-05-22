# IKE Runtime v0 R1-D Phase Judgment

## Purpose

This note records the controller judgment for what should come immediately
after `R1-C` truth-layer completion.

It exists to prevent the runtime mainline from drifting into:

- broader platform integration
- premature UI/API expansion
- memory-engine ambition beyond current kernel truth

## Current Baseline

What is now materially true:

- `R1-B` lifecycle proof exists and is durable
- `R1-C5` Postgres-backed claim verification exists for the narrow delegate
  claim path
- `R1-C6` DB-backed schema-foundation runtime truth is green
- `R1-C7` removed the deprecated `allow_claim` compatibility surface from the
  runtime validator

Interpretation:

- task/lease/claim truth is now strong enough to stop doing truth-layer repair
- the next phase should exercise what the kernel is *for*, not reopen the same
  semantics

## Candidate Next Phases Considered

### Option A: Wider Runtime DB Sweep

Pros:

- more validation evidence
- low semantic risk

Why it is not the next phase:

- this is a validation action, not a new runtime capability phase
- it should accompany the next phase, not define it

### Option B: Operational Closure Layer

Meaning:

- connect `WorkContext` reconstruction and `MemoryPacket` acceptance to the
  real runtime truth path
- prove that reviewed upstream work can produce trusted closure artifacts
  without creating a second truth source

Pros:

- directly matches the runtime roadmap
- exercises why the kernel exists
- stays inside current runtime scope
- prepares later memory/task governance without opening a graph-memory branch

### Option C: Broader Runtime Integration/UI

Why not now:

- too early
- would hide remaining kernel issues under controller-facing surfaces
- violates current phase discipline

## Controller Decision

Accepted next phase:

- **`R1-D = Operational Closure Layer`**

Core target:

- prove that runtime-owned task/decision truth can reconstruct
  `WorkContext` and promote reviewed closure artifacts into trusted
  `MemoryPacket` records

## What R1-D Should Include

1. runtime-backed `WorkContext` reconstruction path
2. runtime-backed `MemoryPacket` acceptance/promotion path
3. proof that trusted closure artifacts are tied to reviewed upstream work
4. narrow validation showing no second truth source is introduced

## What R1-D Should Not Include

- benchmark/kernel integration
- notification surfaces
- broad UI task board
- graph memory
- general retrieval engine
- broader scheduler/autonomy work

## Resulting Mainline Rule

After `R1-C`, do not open `R1-E` or any broader runtime branch first.

Open:

- `R1-D Operational Closure Layer`

and keep it narrow.
