# IKE Flywheel Execution Feedback Provenance Result

**Task ID:** IKE_FLYWHEEL_EXECUTION_FEEDBACK_PROVENANCE_2026-04-21
**Date:** 2026-04-21
**Status:** Complete

**Canonical review file:** [D:\code\MyAttention\docs\reviews\active\review_for_IKE_FLYWHEEL_EXECUTION_FEEDBACK_PROVENANCE_RESULT_2026-04-21.md](/D:/code/MyAttention/docs/reviews/active/review_for_IKE_FLYWHEEL_EXECUTION_FEEDBACK_PROVENANCE_RESULT_2026-04-21.md)

**Review pack:** [D:\code\MyAttention\.runtime\review-packs\IKE_FLYWHEEL_EXECUTION_FEEDBACK_PROVENANCE_RESULT_2026-04-21.zip](/D:/code/MyAttention/.runtime/review-packs/IKE_FLYWHEEL_EXECUTION_FEEDBACK_PROVENANCE_RESULT_2026-04-21.zip)

---

## Summary

Added a minimal inspect-only provenance layer to the existing execution feedback bridge, enabling pasted worker results to carry caller-provided worker/run/artifact identity without becoming trusted/canonical state.

The provenance fields are explicitly marked as caller-provided and unverified throughout:
- Request/response contracts
- AI prompt context
- Controller packet notes
- Truth boundary disclaimers
- Frontend display with inspect-only/caller-provided badges

---

## Files Changed

| File | Changes |
|------|---------|
| `services/api/conversation_runtime/contracts.py` | Added `worker_run_id`, `worker_provider`, `worker_model`, `worker_artifact_ref` optional fields to `FlywheelExecutionFeedbackInspectRequest`. Added `WorkerProvenance` model with `provenance_source="caller_provided"` and `verified=False`. Added `provenance` field to response. |
| `services/api/conversation_runtime/flywheel.py` | Extended `_execution_feedback_truth_boundary()` with provenance disclaimers. Extended `_build_execution_feedback_prompt()` to include provenance context section when provided. Extended `run_execution_feedback_inspect()` to build and return `WorkerProvenance` with notes indicating unverified status. |
| `services/api/tests/test_flywheel_inspect_route.py` | Added `test_execution_feedback_inspect_with_provenance_echoed_unverified` verifying provenance is echoed as unverified/caller-provided. Added `test_execution_feedback_inspect_missing_provenance_valid` verifying missing provenance remains valid. |
| `services/web/lib/api-client.ts` | Added `FlywheelWorkerProvenance` interface. Extended `FlywheelExecutionFeedbackInspectRequest` with optional provenance fields. Extended `FlywheelExecutionFeedbackInspectResponse` with `provenance` field. |
| `services/web/components/evolution/flywheel-inspect-panel.tsx` | Added compact optional provenance input fields near execution feedback input. Added provenance display section showing returned provenance with inspect-only/caller-provided/未验证 badge. Extended API call to send provenance fields. |

---

## Why This Solution

1. **Inspect-only design**: Provenance is explicitly caller-provided and not verified by the endpoint, maintaining the inspect-only boundary of the execution feedback route.

2. **No truth state changes**: The provenance fields do not affect `candidate`, `promotion_state`, or `review_gate` semantics—they are purely informational context for human/controller review.

3. **Truth boundary integration**: Provenance disclaimer is included in the truth boundary list, ensuring callers are reminded that provenance is not verified.

4. **Prompt context inclusion**: When provenance fields are provided, they are included in the AI prompt as a dedicated section marked as caller-provided and not verified, allowing the AI to reference them in its reflection without treating them as canonical.

5. **Frontend transparency**: Provenance display includes a visible badge indicating inspect-only/caller-provided/unverified status, preventing users from misinterpreting provenance as verified worker identity.

---

## Validation Run

### Python Tests
```
python -m unittest services.api.tests.test_flywheel_inspect_route -v

test_execution_feedback_inspect_extracts_reflection_candidates ... ok
test_execution_feedback_inspect_missing_provenance_valid ... ok
test_execution_feedback_inspect_no_action_fallback ... ok
test_execution_feedback_inspect_with_provenance_echoed_unverified ... ok
test_flywheel_inspect_discards_out_of_scope_correction ... ok
test_flywheel_inspect_evolution_only_triggers_review ... ok
test_flywheel_inspect_explicit_non_canonical_boundary ... ok
test_flywheel_inspect_extracts_knowledge_and_evolution_candidates ... ok
test_flywheel_inspect_filters_invalid_delta_types ... ok
test_flywheel_inspect_handles_invalid_json_gracefully ... ok
test_flywheel_inspect_noisy_input_yields_no_candidates ... ok
test_flywheel_inspect_with_source_candidate_and_correction ... ok
test_task_packet_preview_empty_no_action_fallback ... ok
test_task_packet_preview_empty_with_reviewer_note ... ok
test_task_packet_preview_evolution_only ... ok
test_task_packet_preview_explicit_non_canonical_boundary ... ok
test_task_packet_preview_knowledge_evolution_driven ... ok
test_task_packet_preview_knowledge_only ... ok
test_task_packet_preview_label_normalization ... ok
test_task_packet_preview_source_only ... ok
test_task_packet_preview_whitespace_only_labels_fall_back_to_no_action ... ok

----------------------------------------------------------------------
Ran 21 tests in 0.110s

OK
```

### Frontend Build
```
npm run -s --prefix services/web build

○  (Static)   prerendered as static content
ƒ  (Dynamic)  server-rendered on demand

Build succeeded with no errors.
```

---

## Known Risks

1. **Provenance spoofing**: Since provenance is caller-provided and unverified, malicious callers could inject false worker identity. This is acceptable given the inspect-only nature of the endpoint—provenance is informational context only, not canonical state.

2. **AI prompt leakage**: The provenance context is included in the AI prompt; if the AI hallucinates additional provenance details not provided by the caller, this could confuse human reviewers. The prompt explicitly notes provenance is caller-provided to mitigate this.

3. **Provenance field naming collision**: If future IKE versions introduce verified worker identity fields, naming conventions must distinguish verified vs. caller-provided provenance. Current naming (worker_run_id, etc.) with explicit `provenance_source="caller_provided"` should avoid collision.

---

## Recommendation

**Accept.** The implementation meets all requirements:
- Optional provenance fields in request
- Structured provenance in response with `provenance_source="caller_provided"` and `verified=False`
- Provenance context included in AI prompt and controller packet notes
- No changes to candidate truth state, promotion_state, or review_gate semantics
- Truth boundary includes provenance disclaimer
- Frontend has compact provenance input fields and displays returned provenance with unverified badge
- Tests verify provenance is echoed as unverified/caller-provided and missing provenance remains valid

The implementation is minimal, bounded, and maintains the inspect-only contract of the execution feedback endpoint.

---

## Delegation Notes

- `20260421T060852-7a9a5dc1`: `qwen-bailian-coding / glm-5`, aborted after long no-output wait.
- `20260421T061546-e50646df`: `z-ai / glm-5.1`, failed with provider `429 Rate limit reached for requests`.
- `20260421T062156-4ae63ff8`: `qwen-bailian-coding / glm-5`, succeeded; prompt delivery verified.
