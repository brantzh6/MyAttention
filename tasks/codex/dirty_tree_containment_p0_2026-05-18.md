# Dirty Tree Containment (P0)

Date: 2026-05-18
Lane: governance / worktree operations
SDLC stage: Design -> Operations correction
Risk: R2
Truth status: controller operations packet

## Objective

Prevent another round of mainline work from accumulating into an unreviewable
dirty tree.

This packet records the current incident and defines the immediate containment
rule. It does not authorize deletion, broad staging, broad commit, or broad PR.

## Current Evidence

Current branch:

```text
codex/pre-ike-restructure-2026-04-09
```

Current classifier result:

```text
total: 172
recommendation: requires_scoped_review_prep
largest group: flywheel_readiness: 72
```

Observed issue:

- Multiple accepted task/result/review/absorption artifacts remain untracked.
- Several tracked source and doc files have accumulated changes across lanes.
- Active docs still contained stale "clean" language while the actual tree was
  over budget.
- Automation previously counted low-value prep actions as progress, which let
  active packets and dirty-tree closure drift apart.

## Containment Rule

Until the dirty tree is reduced below the scoped budget:

1. No new implementation patch starts from the shared dirty tree.
2. Controller may write only:
   - task packets
   - result artifacts
   - review artifacts
   - absorption artifacts
   - active control-surface updates
3. Every implementation packet must name its scoped candidate files before
   dispatch.
4. After a packet is reviewed and absorbed, the controller must immediately
   choose one of:
   - prepare a scoped stage/PR package for that lane
   - park the lane with explicit blocker
   - reject/supersede the artifacts
5. Automation must not treat classifier-only runs, wrapper packets, or active
   artifact index updates as mainline progress when an active packet exists.

## Required Next Worktree Action

Prepare a scoped Flywheel readiness package first, because it is the largest
and most active group.

Candidate package owner:

```text
flywheel_readiness
```

The package must include only files required to explain and validate the
accepted Flywheel V1 loop state. It must not include unrelated runtime,
source-intelligence, or generic governance edits.

## Stop Condition

Stop after containment is recorded and reviewed. Do not delete, stage, commit,
or push until a scoped package file list is produced and accepted.
