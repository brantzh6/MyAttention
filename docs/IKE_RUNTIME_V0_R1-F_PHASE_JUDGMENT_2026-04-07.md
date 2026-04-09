# IKE Runtime v0 R1-F Phase Judgment

## Purpose

This note records the controller judgment for what should come immediately
after materially complete `R1-E`.

## Current Baseline

What is now materially true:

- `R1-D` proved runtime-backed operational closure
- `R1-E` proved project-level current-work pointer alignment to runtime truth
- `RuntimeProject.current_work_context_id` can now point at the active
  reconstructed runtime context without creating a second truth source

## Preserved Gap After R1-E

The remaining gap is not pointer truth.

It is:

- controller-facing current runtime visibility is still spread across direct
  table access and helper-specific knowledge
- there is not yet one narrow runtime-backed read surface that summarizes the
  current project operational state for controller use

## Candidate Next Phases Considered

### Option A: Broader UI/runtime expansion now

Why not now:

- still too early
- would broaden runtime surface area before the controller-facing read model is
  stabilized

### Option B: Notification/follow-up surfaces now

Why not now:

- still belongs to later `v0.1` capability growth
- would add operational surface before the current-state read model is settled

### Option C: Narrow controller-facing runtime read model

Meaning:

- add one narrow runtime-backed helper/read surface for "current project
  operational state"
- assemble current project visibility from:
  - `RuntimeProject`
  - active `RuntimeWorkContext`
  - current active/waiting tasks
  - latest finalized decision
  - latest trusted memory packet refs

Why this is the right next phase:

- directly follows `R1-E`
- stays inside runtime scope
- improves controller-facing usability without opening UI/runtime sprawl

## Controller Decision

Accepted next phase:

- **`R1-F = Controller Runtime Read Surface`**

## What R1-F Should Include

1. one narrow runtime-backed helper/read model for current project state
2. tests proving the read model is derived only from runtime truth
3. no duplicate persistent summary state

## What R1-F Should Not Include

- broad UI/API rollout
- notifications/follow-up mesh
- graph/retrieval work
- benchmark integration
- new runtime object families

## Resulting Mainline Rule

After `R1-E`, do not jump to wider surfaces yet.

Open:

- `R1-F Controller Runtime Read Surface`

and keep it helper-level and truth-derived.
