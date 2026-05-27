# Runtime Operator Packet: /control live ops-state pre-PR validation

Task ID: control_live_ops_state_pre_pr_runtime_validation_2026_05_27
Owner lane: ike-operator
Requested by: codex-controller
Date: 2026-05-27

## Goal

Validate the coding-worker fix for `/control` live ops-state rendering before PR promotion.

This is runtime validation, not controller design and not source implementation.

## Workspace

Use this isolated worktree:

`D:\code\_worktrees\MyAttention-control-live-ops-state`

Branch:

`codex/control-live-ops-state-2026-05-27`

Expected changed source file:

`services/web/lib/control-surface/ops-state-adapter.ts`

## Context

PR22 merged `/control` to main and post-merge runtime validation confirmed `/control`, `/chat`, `/evolution`, and API `/health` return 200. The remaining accepted gate is that `/control` still renders static fallback instead of live ops-state derived data.

The coding worker fixed the adapter by adding bounded Next standalone cwd root resolution and by making optional state sections degrade without forcing total fallback.

Local reviewer recommendation: `accept_with_changes`; runtime validation is required before PR.

## Required Validation

1. Build the web app in the isolated worktree.
2. Run the web app from the isolated worktree in a way that exercises the built Next standalone runtime where feasible.
3. Ensure valid state files are available for the test:
   - `ops/state/current_state.json`
   - `ops/pm-runs/latest.json`
4. Visit or fetch `/control`.
5. Confirm whether `/control` renders live-derived project state, not static fallback:
   - expected visible/provenance signal: `Ops State Sync`
   - expected PM digest signal: `PM Watch Digest`
   - expected source kind behavior: live data derived from `ops/state/current_state.json`
6. Record any console/server errors relevant to `/control`.

## Boundaries

- Do not commit.
- Do not push.
- Do not edit product source unless runtime validation is impossible without a one-line local diagnostic change, and if so stop and report before editing.
- Do not use the main workspace dirty tree as implementation source.
- You may copy or stage runtime-only state data inside the isolated worktree for validation, but record what you copied and remove temporary files if they are not intended to be committed.

## Required Output

Write result to:

`D:\code\MyAttention\tasks\codex\control_live_ops_state_pre_pr_runtime_validation_result_2026-05-27.md`

Use this structure:

1. summary
2. commands run
3. validation evidence
4. runtime errors
5. verdict: accept, accept_with_changes, or reject
6. controller next action

Stop after writing the result.
