# Review Packet: /control live ops-state adapter fix

Task ID: control_live_ops_state_adapter_fix_review_2026_05_27
Owner lane: local Claude Code reviewer
Requested by: codex-controller
Date: 2026-05-27

## Scope

Review only the current worktree diff for:

- services/web/lib/control-surface/ops-state-adapter.ts
- tasks/codex/control_live_ops_state_adapter_fix_result_2026-05-27.md

Do not perform a greenfield project review.
Do not review unrelated dirty-tree state in the main workspace.
Do not edit source files.

## Context

PR22 merged the corrected main-based /control surface into main. Post-merge runtime validation showed /control returns 200 but still renders STATIC_SNAPSHOT fallback instead of live ops-state derived data. The accepted next gate is to repair /control live ops-state rendering so it can consume:

- ops/state/current_state.json
- ops/pm-runs/latest.json

The implementation worker identified a Next standalone cwd root-resolution gap and changed ops-state-adapter.ts.

## Review Questions

1. Does the path-resolution fix correctly handle repo root, services/web cwd, and services/web/.next/standalone cwd without broad unsafe filesystem walking?
2. Is graceful degradation for dirty_tree_state and next_action acceptable, or does it hide required project-state integrity failures?
3. Did the worker keep the patch scoped?
4. Is the validation evidence sufficient for promotion, or is additional targeted validation required before PR?

## Required Output

Write the review result to:

tasks/codex/control_live_ops_state_adapter_fix_review_result_2026-05-27.md

Use this structure:

1. findings
2. validation gaps
3. recommendation: accept, accept_with_changes, or reject
4. required controller action

Stop after writing the review result.
