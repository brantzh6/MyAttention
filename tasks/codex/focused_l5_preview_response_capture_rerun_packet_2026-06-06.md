# Test Packet: Focused L5 Preview Response Capture Rerun

## Task ID

`focused_l5_preview_response_capture_rerun_2026_06_06`

## Owner And Fallback

- Owner: `claude-code-test-runner`
- Fallback: `claude-code-runtime-operator` for runtime blocker evidence only

## Objective

Close the single remaining evidence gap from the accepted-with-changes focused
L5 run: capture the browser-derived HTTP status and bounded response shape for
`POST /api/conversation-runtime/flywheel/task-packet/preview`.

Reuse the proven UI-driven path from chat origin through inspect and candidate
selection. This packet validates only. It does not authorize product source
edits, runtime service operation, database changes, execution, promotion, or
controller absorption.

## Required Reads

- `AGENTS.md`
- `ops/state/current_state.json`
- `ops/runtime/latest.json`
- `ops/agents/ike-test-runner.md`
- `tasks/codex/focused_l5_single_run_preview_closure_validation_result_2026-06-05.md`
- `docs/reviews/active/review_for_focused_l5_single_run_preview_closure_validation_2026-06-05.md`
- `tasks/codex/focused_l5_browser_trace_2026-06-05.json`

## Runtime Preconditions

1. Confirm `ops/runtime/latest.json` reports `overall_reachability =
   all_healthy`.
2. Confirm `/control` returns HTTP 200 with both `file_derived` and
   `PM Watch Digest`.
3. Confirm API health returns healthy JSON.
4. Use the running runtime without starting, stopping, rebuilding, restarting,
   or repairing services.

If a precondition fails, write the result with recommendation `reject`, record
the precise runtime blocker, and stop.

## Required Validation

1. Run one browser session using the proven chat-origin UI path.
2. Submit a substantive chat message and use the visible UI handoff to
   Evolution/Flywheel.
3. Trigger inspect through the UI and wait for candidates.
4. Select at least one visible candidate through the manual absorption UI.
5. Confirm `Request Preview` is enabled and trigger it through the UI.
6. Capture the preview response synchronously using a response wait tied to the
   preview UI action, such as `page.waitForResponse`, before continuing.
7. Record preview request method, URL, timestamp, response timestamp, HTTP
   status, elapsed time, and a bounded response shape proving whether
   `candidate_packet` or `handoff_preview` content returned.
8. Record explicit no-execution, no-promotion, and runtime-unchanged evidence.

Do not substitute a direct API request for browser-derived preview response
evidence. A direct request may be used only as labeled diagnosis after the UI
attempt fails.

## Artifact Guidance

- Reuse or adapt the prior validation script under `tasks/codex/`.
- Await all critical response-body capture before writing the trace or exiting.
- Write new artifacts as UTF-8 without BOM and use ASCII punctuation.
- Record a process lease and clean only processes started by this run.

## Forbidden Actions

- Do not edit product source or runtime configuration.
- Do not operate runtime services.
- Do not mutate or cut over databases.
- Do not execute generated task packets.
- Do not stage, commit, push, merge, promote, or decide closure.
- Do not broaden validation beyond the preview-response evidence gap.

## Required Result

Write exactly:

`tasks/codex/focused_l5_preview_response_capture_rerun_result_2026-06-06.md`

Include:

1. summary
2. validation_run
3. process_lease
4. runtime_precheck_and_postcheck
5. ui_path_evidence
6. preview_request_evidence
7. preview_response_evidence
8. no_execution_or_promotion_evidence
9. files_changed
10. validation_gaps
11. known_risks
12. recommendation: `accept`, `accept_with_changes`, or `reject`

## Acceptance Boundary

Recommend `accept` only when one UI-driven browser run captures the preview
response status and bounded response shape while runtime remains healthy and no
forbidden action occurs.

Recommend `reject` if the preview response is not captured, the UI path does
not reach preview, runtime regresses, or any forbidden action occurs.

## Stop Condition

Stop after writing the result artifact. Independent review and controller
absorption remain separate gates.
