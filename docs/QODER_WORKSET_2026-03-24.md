# Qoder Workset 2026-03-24

## Purpose

This document defines the bounded tasks that can be handed to another coding agent (`qoder`) while preserving mainline control.

It is not a transfer of project ownership.
It is a controlled delegation package.

Use together with:

- [D:\code\MyAttention\docs\CURRENT_MAINLINE_HANDOFF.md](/D:/code/MyAttention/docs/CURRENT_MAINLINE_HANDOFF.md)
- [D:\code\MyAttention\docs\DELEGATION_BRIEF_TEMPLATE.md](/D:/code/MyAttention/docs/DELEGATION_BRIEF_TEMPLATE.md)
- [D:\code\MyAttention\docs\CONTROLLED_DELEGATION_STRATEGY.md](/D:/code/MyAttention/docs/CONTROLLED_DELEGATION_STRATEGY.md)

## Mainline Context

Current mainline priorities:

1. Improve `source intelligence` quality.
2. Make the active work surface understandable.
3. Move evolution from watchdog/rule checks toward better reasoning, without destabilizing runtime.

Do not start new architecture branches.
Do not redesign the whole system.
Do not treat “more object types” as “quality solved”.

## Tasks That Can Be Delegated Now

### Task A: Active Source Plans View

Priority: `P0`

Goal:

- Make `settings/sources` clearly show which plans are active/current versus historical/noisy.

Allowed files:

- `D:\code\MyAttention\services\web\components\settings\sources-manager.tsx`

Allowed reads:

- `D:\code\MyAttention\docs\CURRENT_MAINLINE_HANDOFF.md`
- `D:\code\MyAttention\services\api\routers\feeds.py`

Do not change:

- backend API contracts
- DB schema
- global layout/shell

Acceptance:

- active/recent plans are visually distinct
- stale/history-heavy plans are visually de-emphasized
- no backend changes required
- `npx tsc --noEmit` passes

### Task B: Evolution Task Surface Cleanup

Priority: `P0`

Goal:

- Make the evolution task surface easier to understand by separating active issues from noisy historical instances.

Allowed files:

- `D:\code\MyAttention\services\web\components\evolution\evolution-dashboard.tsx`
- `D:\code\MyAttention\services\web\app\evolution\page.tsx`

Optional bounded backend read-only inspection:

- `D:\code\MyAttention\services\api\routers\evolution.py`

Do not change:

- task DB model
- issue generation semantics
- watchdog/runtime scheduling

Acceptance:

- current actionable issues are visually separated from historical noise
- repeated same-name tasks no longer dominate the primary view
- `npx tsc --noEmit` passes

### Task C: Source Intelligence UI Clarity

Priority: `P1`

Goal:

- Improve readability of `Source Intelligence` object groups so person/org/repo/release/signal differences are obvious.

Allowed files:

- `D:\code\MyAttention\services\web\components\settings\sources-manager.tsx`

Do not change:

- backend selection logic
- policy logic

Acceptance:

- object groups are easier to scan
- important metadata is surfaced without flooding the page
- no visual regression on mobile-width layout

### Task D: Frontend Freshness Perception Review

Priority: `P1`

Goal:

- Review whether homepage/feed freshness cues are understandable and propose or implement bounded UI improvements.

Allowed files:

- `D:\code\MyAttention\services\web\components\feed\feed-list.tsx`

Acceptance:

- user can tell whether data is stale, cached, or recently refreshed
- no backend changes required

## Tasks That Should Not Be Delegated

Do not hand these to qoder as autonomous tasks:

- mainline priority decisions
- attention-policy strategy decisions
- source-intelligence ranking philosophy
- evolution-brain architecture changes
- task model redesign
- versioning architecture
- multi-brain control-plane decisions

These require main controller judgment.

## Constraints Qoder Must Follow

1. Keep patches narrow.
2. Do not rewrite large files unnecessarily.
3. Do not add new infrastructure or dependencies.
4. Do not silently change backend behavior when the task is UI-only.
5. Use UTF-8 only.
6. If backend API fields are insufficient, stop and report instead of inventing behavior.
7. Every task result must include validation evidence.

## Required Delivery Format From Qoder

When qoder finishes a task, it should return:

1. `summary`
2. `files_changed`
3. `why_this_solution`
4. `validation_run`
5. `known_risks`
6. `recommendation`
   - `accept`
   - `accept_with_changes`
   - `reject`

## What To Bring Back For Review

When you come back for review, qoder should provide all of the following:

1. A short task brief
   - what task it attempted
   - what was in scope

2. Exact files changed

3. The actual diff or commit hash

4. Validation evidence
   - commands run
   - test/typecheck results
   - page URLs checked

5. Known limitations
   - what it did not solve
   - where it stopped

6. If UI was changed, screenshots are strongly preferred

Without these, review quality will be worse and acceptance may be blocked.

## Best Review Entry Point Later

When returning for review, point me first at:

- the task brief
- the diff/commit
- validation evidence

Then I can do a focused review instead of reloading the entire project context.
