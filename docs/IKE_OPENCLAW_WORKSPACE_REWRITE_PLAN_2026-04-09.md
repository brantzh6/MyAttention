# IKE OpenClaw Workspace Rewrite Plan

Date: 2026-04-09
Status: proposed

## Current Problem

Current OpenClaw agents all use:

- `workspace = D:\code\MyAttention`

This means:

- coding lanes
- review lanes
- analysis lanes

all share one mutable project root.

That increases the chance of:

- source-tree pollution
- overlapping changes
- stray temporary files
- low-auditability worktree state

## Target State

Keep one canonical project root:

- `D:\code\IKE`

But do not use that root as the default shared mutable workspace for all
OpenClaw agents.

## Recommended Workspace Layout

### Option 1. Isolated workspaces under external runtime root

- `D:\code\_ike-runtime\openclaw\workspaces\coder-qwen`
- `D:\code\_ike-runtime\openclaw\workspaces\reviewer-qwen`
- `D:\code\_ike-runtime\openclaw\workspaces\kimi-review`

### Option 2. Git worktrees

If Git worktrees are preferred:

- controller root:
  - `D:\code\IKE`
- coding worktree:
  - `D:\code\IKE-worktrees\coder-qwen`
- review worktree:
  - `D:\code\IKE-worktrees\reviewer-qwen`
- kimi review worktree:
  - `D:\code\IKE-worktrees\kimi-review`

## Recommended Per-Agent Rules

### `myattention-coder`

- should use isolated mutable workspace
- may modify source
- must not share mutable root with reviewer lanes

### `myattention-reviewer`

- should use isolated workspace or read-biased workspace
- output should go to structured result locations, not arbitrary root files

### `myattention-kimi-review`

- should use isolated review workspace
- output should be primarily report/result artifacts

## Migration Sequence

1. create target isolated workspaces
2. copy or worktree-checkout project source into each workspace
3. rewrite OpenClaw agent configs
4. run one narrow probe on each agent
5. only then retire shared-root workspace usage

## Non-Goals

- do not redesign OpenClaw itself
- do not change model-routing semantics during the same migration step
