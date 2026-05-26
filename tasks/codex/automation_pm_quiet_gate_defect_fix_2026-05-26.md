# Automation PM Quiet-Gate Defect Fix

Date: 2026-05-26
Owner: codex-controller

## Problem

The OpenClaw `ike-pm` cron was running, but it could return `quiet` when
`last_real_progress_at` was recent even though the active gate remained
unresolved.

Concrete failure:

- PM run `openclaw_pm_run_20260526_224800` returned `decision: quiet`.
- Evidence said `next_action` was a clear PR14 retry-merge action.
- That action had not closed the `/control` mainline gate.
- PR14 was later found to have merged into non-main base
  `codex/flywheel-feedback-loop-package-2026-05-19`, not `main`.

This means the automation monitored activity, not gate closure.

## Fix Applied

Updated PM rules locally:

- `ops/openclaw/ike-pm-bootstrap-task.md`
- `D:\code\_agent-runtimes\openclaw-workspaces\ike-pm\AGENTS.md`
- `D:\code\_agent-runtimes\openclaw-workspaces\ike-pm\skills\ike-pm\SKILL.md`

New rule:

`last_real_progress_at` is not enough for quiet. If `next_action` still names
an unresolved merge, review absorption, runtime validation, automation repair,
or blocked promotion gate, PM must not return quiet unless that exact action is
already dispatched and in flight.

Promotion base correctness is also a gate. If a promotion PR merges into a
non-main base while the project claim requires main, PM must classify it as
incomplete mainline progress and trigger controller correction.

## Current Mainline Correction

PR14 was reviewed clean but merged into a non-main base. Controller created the
corrected main-based package:

- PR22: https://github.com/brantzh6/MyAttention/pull/22
- Review trigger: comment `4545593331`
- Local build: `npm --prefix services/web run build` passed

## Remaining Verification

The next PM cron run must not classify unresolved PR22 review/merge/runtime
validation as quiet merely because this controller update is recent. Acceptable
PM states are `monitoring` if PR22 review is in flight, or `triggered` /
`needs_controller_consult` if the review/merge gate becomes stale or blocked.
