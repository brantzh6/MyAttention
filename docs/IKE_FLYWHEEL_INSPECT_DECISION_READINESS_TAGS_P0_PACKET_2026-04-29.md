# IKE Flywheel Inspect Decision Readiness Tags P0 Packet

Date: 2026-04-29

## Status

- lifecycle stage: Design / Implementation Packet
- project level: L2
- project type: C
- risk: R2 if bounded to existing response fields
- controller owner: main controller
- implementation owner: delegated worker
- review lane: L1 delegated review after implementation

## Purpose

Make the existing inspect-only flywheel output easier for a controller to read and act on without adding schema, persistence, promotion semantics, or UI panel work.

## Context

The flywheel manual AI-participation closure line is phase-stopped. The project should not continue adding closure packet fields or pseudo-workflow affordances by default.

This packet is deliberately narrower:

- reuse existing `controller_packet.reason_tags`
- reuse existing `operational_advice.controller_notes`
- clarify whether an inspect result is ready for task-packet preview, still needs controller review, or lacks enough signal
- do not add any new API fields
- do not change runtime truth or promotion state

## Goal

Add decision-readiness tags and notes to the current inspect-only response.

Expected examples:

- `ready_for_task_packet_preview` when knowledge/evolution candidates exist and a task-packet preview would be meaningful
- `needs_controller_review` when the result contains candidates or manual-review conditions
- `insufficient_signal` when the inspected segment has no actionable candidate signal
- existing tags such as `knowledge_delta_review`, `evolution_trigger_review`, `manual_review_required`, and `no_action` must remain compatible

## Non-Goals

- Do not add fields to `FlywheelInspectResponse`, `ConversationControllerPacket`, or route schemas.
- Do not change persistence, scheduler behavior, worker execution, promotion state, or runtime truth.
- Do not touch frontend/UI files.
- Do not split panels.
- Do not reopen worker-return evidence design waves.
- Do not alter task-packet preview semantics except tests may assert its existing boundaries if needed.

## Allowed Files

Implementation is limited to:

- `D:\code\MyAttention\services\api\conversation_runtime\flywheel_inspect.py`
- `D:\code\MyAttention\services\api\tests\test_flywheel_inspect_route.py`
- `D:\code\MyAttention\docs\IKE_FLYWHEEL_INSPECT_DECISION_READINESS_TAGS_P0_RESULT_2026-04-29.md`

If another file is required, stop and report blocker.

## Existing Dirty Worktree Warning

`test_flywheel_inspect_route.py` already has pre-existing modifications in the shared worktree.

Before editing, the worker must inspect the target sections and avoid overwriting unrelated existing changes. Do not normalize, reformat, or rewrite the whole test file.

## Implementation Guidance

Keep this as a small helper-level change.

Suggested shape:

- add or adjust a helper that derives decision-readiness tags from existing candidate counts and `suggested_next_step`
- append the new tags into `controller_packet.reason_tags`
- append concise controller notes into `operational_advice.controller_notes`
- keep tags deterministic and lowercase snake_case
- preserve current no-action behavior for `segment_intent == "other"`

Suggested semantics:

- knowledge or evolution candidates:
  - include `ready_for_task_packet_preview`
  - include `needs_controller_review`
- source candidates or correction-only/manual review conditions:
  - include `needs_controller_review`
  - do not claim task-packet readiness unless existing selected labels would support it
- no candidates and no manual action:
  - include `insufficient_signal` or keep `no_action` plus a note explaining insufficient inspect signal

Do not overclaim. These are controller-readable inspect hints, not promotion facts.

## Required Validation

Run:

```powershell
$env:PYTHONPATH='D:\code\MyAttention\services\api'
python -m pytest D:\code\MyAttention\services\api\tests\test_flywheel_inspect_route.py D:\code\MyAttention\services\api\tests\test_conversation_runtime_route.py
```

If unrelated tests fail because of pre-existing dirty worktree state, report exact failures and do not fix unrelated files.

## Required Result

Create:

- `D:\code\MyAttention\docs\IKE_FLYWHEEL_INSPECT_DECISION_READINESS_TAGS_P0_RESULT_2026-04-29.md`

Include:

- summary
- files_changed
- why_this_solution
- validation_run
- delegation evidence or blocker
- known_risks
- recommendation: `accept`, `accept_with_changes`, or `reject`

## Review Requirement

After implementation, controller must run L1 delegated code review. No external manual review is required unless scope expands into schema, persistence, runtime truth, promotion boundary, worker execution, or UI behavior.
