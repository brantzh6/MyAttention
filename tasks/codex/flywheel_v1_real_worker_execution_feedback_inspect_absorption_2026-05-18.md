# Controller Absorption: Flywheel V1 Real Worker Execution-Feedback Inspect

Date: 2026-05-18
Controller decision: `accept_with_changes`
Lane: evolution flywheel v1
Truth status: non-canonical / inspect-only

## absorbed_artifacts

- Packet: `tasks/codex/flywheel_v1_real_worker_execution_feedback_inspect_packet_p0_2026-05-18.md`
- Worker brief: `tasks/codex/flywheel_v1_real_worker_execution_feedback_worker_brief_p0_2026-05-18.md`
- Worker result: `tasks/codex/flywheel_candidate_chat_conversation_result.md`
- Controller result: `tasks/codex/flywheel_v1_real_worker_execution_feedback_inspect_result_2026-05-18.md`
- Review artifact: `docs/reviews/active/review_for_flywheel_v1_real_worker_execution_feedback_inspect_2026-05-18.md`
- Runtime review source: `.runtime/reviews/results/FLYWHEEL_V1_REAL_WORKER_EXECUTION_FEEDBACK_INSPECT_REVIEW_2026_05_18.md`

## decision

Accept the mainline loop closure with changes.

This closes the specific P0 objective:

```text
copy-ready delegate handoff packet -> worker result -> execution-feedback inspect -> controller absorption
```

The accepted evidence is inspect-only and does not promote extracted knowledge/evolution candidates into canonical truth.

## controller_absorption

Accepted:

- A real copied handoff packet was generated from the live task-packet preview route.
- A local delegated worker produced a structured worker result artifact.
- The worker result was fed back into the live execution-feedback inspect route.
- Execution-feedback inspect returned a controller packet with complete caller-provided provenance and `promotion_state=inspect_only`.
- Local validation passed:
  - `python -m py_compile services/api/conversation_runtime/contracts.py services/api/conversation_runtime/task_packet_preview.py`
  - `python -m pytest services/api/tests/test_flywheel_inspect_route.py -q`
  - `python manage.py health --json` with API healthy.
- Local L1 review recommended `accept_with_changes`.

Accepted with changes:

- The first full worker-result inspect call timed out after 180 seconds.
- The retry succeeded with compressed feedback text plus full artifact provenance.
- This is an operations/runtime concern for long LLM inspect inputs, not a rejection of the loop closure.

## follow_up

1. Track execution-feedback long-input latency as a runtime/operator issue if it recurs.
2. Move the mainline from "prove the loop can consume a real worker result" to "make the AI conversation entry select and launch a useful next bounded packet through this loop."
3. Keep `/control` synchronized so the visible project anchor no longer says this closed gate is still next.

## stop_condition

Do not auto-promote inspect candidates or schedule follow-up work from the execution-feedback response. The next task must be explicitly selected by the controller.
