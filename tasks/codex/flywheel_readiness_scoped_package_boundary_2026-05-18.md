# Flywheel Readiness Scoped Package Boundary

Date: 2026-05-18
Lane: worktree operations / flywheel readiness
SDLC stage: Scoped package prep
Risk: R2
Truth status: controller package boundary candidate

## objective

Define the first scoped package boundary that can reduce the dirty tree without
mixing unrelated lanes.

This file does not stage, commit, push, delete, or promote anything. It names a
candidate package for review.

## package_name

```text
flywheel_latest_feedback_loop_closure_2026-05-18
```

## why_this_package_first

The latest accepted mainline gate is the real worker execution-feedback inspect
closure. It is small enough to review as one package and directly updates the
visible mainline state. Packaging it first prevents the next AI-entry
implementation from being mixed with the just-accepted loop-closure evidence.

## included_files

Latest Flywheel loop closure evidence:

- `tasks/codex/flywheel_v1_real_worker_execution_feedback_inspect_packet_p0_2026-05-18.md`
- `tasks/codex/flywheel_v1_real_worker_execution_feedback_worker_brief_p0_2026-05-18.md`
- `tasks/codex/flywheel_v1_real_worker_execution_feedback_inspect_local_dispatch_2026-05-18.md`
- `tasks/codex/flywheel_candidate_chat_conversation_result.md`
- `tasks/codex/flywheel_v1_real_worker_execution_feedback_inspect_result_2026-05-18.md`
- `docs/reviews/active/review_for_flywheel_v1_real_worker_execution_feedback_inspect_2026-05-18.md`
- `tasks/codex/flywheel_v1_real_worker_execution_feedback_inspect_absorption_2026-05-18.md`

Mainline/control state updated because of that accepted gate:

- `docs/CURRENT_MAINLINE_CONTROL_2026-05-02.md`
- `docs/CURRENT_ACTIVE_ARTIFACTS.md`
- `services/web/lib/control-surface/static-snapshot.ts`

Automation/operations correction directly tied to why this gate had stalled:

- `docs/CURRENT_OPERATIONS.md`

Total candidate files: 11

## excluded_files

Exclude from this first package:

- older `tasks/codex/flywheel_v1_*` artifacts from 2026-05-09 through 2026-05-17
- AI-entry selection artifacts from 2026-05-18
- dirty-tree containment artifacts from 2026-05-18
- runtime repair artifacts from 2026-05-16 and 2026-05-18
- `services/api/conversation_runtime/*`
- `services/api/tests/test_flywheel_inspect_route.py`
- `services/web/components/evolution/*`
- `services/web/components/chat/chat-interface.tsx`
- `services/web/lib/api-client.ts`
- `services/web/package.json`
- `data/`
- `tasks/codex/_write_smoke.tmp`

## linked_evidence

- Worker result: `tasks/codex/flywheel_candidate_chat_conversation_result.md`
- Controller result: `tasks/codex/flywheel_v1_real_worker_execution_feedback_inspect_result_2026-05-18.md`
- Review: `docs/reviews/active/review_for_flywheel_v1_real_worker_execution_feedback_inspect_2026-05-18.md`
- Absorption: `tasks/codex/flywheel_v1_real_worker_execution_feedback_inspect_absorption_2026-05-18.md`

## validation_commands

Already run for the accepted gate:

```text
python -m py_compile services/api/conversation_runtime/contracts.py services/api/conversation_runtime/task_packet_preview.py
python -m pytest services/api/tests/test_flywheel_inspect_route.py -q
npm run build
python manage.py health --json
```

Before staging this package, rerun:

```text
git diff --check -- docs/CURRENT_MAINLINE_CONTROL_2026-05-02.md docs/CURRENT_ACTIVE_ARTIFACTS.md docs/CURRENT_OPERATIONS.md services/web/lib/control-surface/static-snapshot.ts
git status --short -- <included files>
```

## review_gate

Required before staging:

```text
local L1 review of this package boundary -> controller absorption -> scoped staging
```

## known_risks

- `docs/CURRENT_OPERATIONS.md` also contains broader operations changes. The
  package review must confirm those edits are required for this gate and not an
  unrelated governance bundle.
- `services/web/lib/control-surface/static-snapshot.ts` may include earlier
  accepted control-surface changes in the same file; package review must treat
  existing dirty context separately from the latest gate update.
- This package reduces only the latest closure boundary; it does not clean the
  older Flywheel artifact backlog.

## recommendation

`accept_with_changes`

Accept as the first scoped package candidate if local review agrees the 11
files form one coherent latest-gate closure package.

## stop_condition

Stop after package boundary review and controller absorption. Do not stage or
commit in this packet.
