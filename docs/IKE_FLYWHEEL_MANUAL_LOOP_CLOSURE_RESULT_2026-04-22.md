# IKE Flywheel Manual Loop Closure Result

**Date:** 2026-04-22
**Status:** Ready for review

## Summary

This slice demonstrates the current manual AI-assisted flywheel loop without adding new API fields or persistence.

The loop used real AI calls and one delegated worker run:

```text
bounded information input
-> Qwen flywheel inspect
-> task-packet preview
-> claude-worker / glm-5 read-only worker execution
-> Qwen execution-feedback inspect with caller-provided provenance
```

The result proves a manual, non-canonical loop can run end-to-end. It does not prove verified provenance, automatic absorption, or runtimeized execution.

## Runtime Artifacts

Runtime artifacts are intentionally outside git:

- `D:\code\MyAttention\.runtime\flywheel-loop-demo-2026-04-22\01_flywheel_inspect.json`
- `D:\code\MyAttention\.runtime\flywheel-loop-demo-2026-04-22\02_task_packet_preview.json`
- `D:\code\MyAttention\.runtime\flywheel-loop-demo-2026-04-22\03_execution_feedback_inspect.json`

Worker run:

- `run_id`: `20260421T164215-398e1412`
- provider: `qwen-bailian-coding`
- model: `glm-5`
- mode: `one_shot`
- status: `succeeded`
- prompt delivery: verified
- artifact: `D:\code\_agent-runtimes\claude-worker-dev\runs\20260421T164215-398e1412\final.json`

## Step 1: AI Flywheel Inspect

Input segment:

```text
IKE now has manual AI-assisted flywheel bridges: flywheel inspect, manual candidate selection,
worker packet preview, delegated worker execution, and execution feedback inspect with
caller-provided provenance. The next step should prove one end-to-end manual loop and avoid
adding more bridge fields until flywheel.py and the frontend panel are decomposed.
```

Qwen output summary:

- `segment_intent`: `flywheel_signal`
- knowledge labels:
  - `current_manual_bridges`
  - `bridge_field_constraint`
- evolution labels:
  - `prove_end_to_end_manual_loop`
  - `decompose_flywheel_and_frontend`

## Step 2: Task Packet Preview

Selected labels:

- knowledge: `current_manual_bridges`, `bridge_field_constraint`
- evolution: `prove_end_to_end_manual_loop`, `decompose_flywheel_and_frontend`

Preview result:

- `packet_intent`: `mixed`
- `suggested_lane`: `mixed_review`
- `suggested_next_step`: `prioritize_and_sequence`
- `promotion_state`: `inspect_only`

## Step 3: Delegated Worker Execution

The worker was asked to perform a read-only analysis of the task packet. It did not edit files.

Worker summary:

```text
Task packet identifies 2 knowledge labels and 2 evolution labels. Documentation confirms:
(1) six bounded manual bridges now exist completing the information -> knowledge -> evolution path,
(2) field constraint is explicit - no more bridge field stacking without decomposition,
(3) the accepted scenario shape matches the evolution labels exactly.
```

Worker validation gaps:

- read-only worker scenario; no execution validation performed
- end-to-end manual loop proof run had not yet been documented at worker time
- `flywheel.py` and `flywheel-inspect-panel.tsx` decomposition scope not yet bounded in a packet

## Step 4: Execution Feedback Inspect

The worker result was pasted back into execution feedback inspect with caller-provided provenance.

Qwen feedback inspect result:

- `feedback_intent`: `execution_feedback`
- `feedback_summary`: review confirms six existing manual bridges, enforces constraints against field stacking, and prioritizes end-to-end proof or decomposition as next steps
- knowledge labels:
  - `current_manual_bridges`
  - `bridge_field_constraint`
- evolution labels:
  - `prove_end_to_end_manual_loop`
  - `decompose_flywheel_and_frontend`
- `promotion_state`: `inspect_only`

Provenance echo:

```json
{
  "worker_run_id": "20260421T164215-398e1412",
  "worker_provider": "claude-worker:qwen-bailian-coding",
  "worker_model": "glm-5",
  "provenance_source": "caller_provided",
  "verified": false
}
```

## Supporting UI Decomposition

The provenance UI was extracted from the large flywheel panel into:

- `services/web/components/evolution/execution-feedback-provenance.tsx`

This is a small decomposition step only. It does not change backend semantics.

The panel now resets provenance fields on a new flywheel inspect run to avoid stale run identity leaking across scenarios.

## Validation Run

```text
python -m unittest services.api.tests.test_conversation_runtime_route services.api.tests.test_flywheel_inspect_route
36 tests OK

npm run -s --prefix services/web build
success
```

Real AI/worker calls used:

- Qwen `qwen3.6-plus` for flywheel inspect
- `claude-worker` with `qwen-bailian-coding / glm-5` for delegated read-only worker execution
- Qwen `qwen3.6-plus` for execution feedback inspect

## Known Risks

1. This is still a manual loop; no runtime scheduler or persistence exists.
2. Worker provenance is annotation only and remains unverified.
3. The worker task was read-only; it did not validate a production code change.
4. `flywheel.py` and `flywheel-inspect-panel.tsx` still need larger decomposition.

## Recommendation

`accept_with_changes`

Accept this as proof that the manual AI-assisted flywheel can close once end-to-end.

Do not claim trusted runtime closure. The next implementation step should be bounded decomposition before any new bridge capability.

---

## Review Absorption

Absorption doc:

- [D:\code\MyAttention\docs\IKE_FLYWHEEL_MANUAL_LOOP_CLOSURE_REVIEW_ABSORPTION_2026-04-22.md](/D:/code/MyAttention/docs/IKE_FLYWHEEL_MANUAL_LOOP_CLOSURE_REVIEW_ABSORPTION_2026-04-22.md)

Review convergence:

- Claude: `accept`
- ChatGPT: `accept_with_changes`
- Gemini: `accept_with_changes`

Controller judgment: `accept_with_changes`.

Accepted as: short-term manual flywheel closure milestone.

Required next phase: structural decomposition, not more bridge fields.
