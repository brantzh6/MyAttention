# Current Active Artifacts

Date: 2026-05-06

Truth status: manually curated active index; non-canonical promotion truth.

## Mainline Anchor

| Artifact | Status | Owner/Lane | Next Action |
| --- | --- | --- | --- |
| `docs/CURRENT_OPERATIONS.md` | active | controller operations | Use as the first-read runbook. Current mainline is `flywheel_v1_ai_entry_control_surface`. |
| `docs/CURRENT_MAINLINE_CONTROL_2026-05-02.md` | active | controller control surface | Defines the three first-class mainline tasks: evolution flywheel, AI entry, and project control surface. |
| `tasks/codex/project_control_surface_anchor_p0_2026-05-06.md` | active packet | project control surface | Implement next as the visible anchor before opening another source-intelligence support slice. |
| `tasks/codex/project_control_surface_antigravity_brief_2026-05-06.md` | superseded delegate brief | project control surface / prior Antigravity UI | Superseded by Gemini CLI UI execution; keep as historical/background context only. |
| `tasks/codex/flywheel_v1_e2e_gap_audit_p0_2026-05-06.md` | active audit packet | evolution flywheel v1 | Use for backend/test delegate gap audit and smoke validation. |
| `tasks/codex/flywheel_v1_e2e_gap_audit_result_2026-05-07.md` | accepted-with-changes audit result | evolution flywheel v1 | Backend inspect route chain is validated; next product gap is chat-to-flywheel handoff plus browser-level smoke. |
| `tasks/codex/flywheel_v1_browser_smoke_p0_2026-05-08.md` | queued validation packet | evolution flywheel v1 / test execution | Run after PR #10 is promoted or checked out; proves `/chat` to flywheel inspect in browser. |
| `tasks/codex/flywheel_v1_browser_smoke_result_2026-05-08.md` | accepted smoke result | evolution flywheel v1 / test execution | Browser smoke is the accepted evidence baseline; next action is controller rehearsal selection. |
| `tasks/codex/flywheel_v1_controller_rehearsal_p0_2026-05-09.md` | active controller packet | evolution flywheel v1 / controller | Use the verified loop to determine the next bounded Flywheel V1 implementation packet. |
| `tasks/codex/flywheel_v1_controller_rehearsal_result_2026-05-09.md` | accepted rehearsal result | evolution flywheel v1 / controller | Next bounded implementation packet selected. |
| `tasks/codex/flywheel_v1_controller_selection_packet_p0_2026-05-10.md` | accepted implementation packet | evolution flywheel v1 | Implemented by local delegate; local L1 review accepted. |
| `tasks/codex/flywheel_v1_controller_selection_result_2026-05-10.md` | accepted result | evolution flywheel v1 | Candidate packet preview now produces controller-ready advisory output while staying inspect-only. |
| `docs/reviews/active/review_for_flywheel_v1_controller_selection_packet_2026-05-10.md` | accepted review | local L1 review | Review recommendation: accept. |
| `tasks/codex/flywheel_v1_execution_handoff_preview_p0_2026-05-11.md` | active implementation packet | evolution flywheel v1 | Next mainline slice: turn accepted `candidate_packet` into an inspect-only delegate handoff preview. |
| `tasks/codex/flywheel_v1_execution_handoff_preview_review_packet_2026-05-11.md` | active review packet | local L1 review | Gemini L1 review returned `accept_with_changes`; required `allowed_files` fix absorbed. |
| `docs/reviews/active/review_for_flywheel_v1_execution_handoff_preview_2026-05-11.md` | accepted-with-changes review | local L1 review | Finding absorbed; backend validation rerun and passed. |
| `tasks/codex/flywheel_v1_execution_handoff_preview_absorption_2026-05-11.md` | accepted absorption | evolution flywheel v1 / controller | Handoff preview accepted; next Flywheel packet can be selected from the delegate-ready handoff path. |
| `tasks/codex/flywheel_v1_next_delegate_packet_selection_2026-05-12.md` | accepted controller selection | evolution flywheel v1 / controller | Selected delegate packet readiness as the next smallest mainline slice. |
| `tasks/codex/flywheel_v1_delegate_packet_readiness_p0_2026-05-12.md` | executed implementation packet | evolution flywheel v1 / backend delegate | Extended handoff preview with SDLC, risk, result artifact, write policy, and copy-ready markdown. |
| `tasks/codex/flywheel_v1_delegate_packet_readiness_result_2026-05-12.md` | reviewed delegate result | evolution flywheel v1 / backend delegate | Local validation passed; review concerns were absorbed by controller. |
| `tasks/codex/flywheel_v1_delegate_packet_readiness_absorption_2026-05-12.md` | accepted-with-changes absorption | evolution flywheel v1 / controller | Next action is one real bounded Flywheel packet through the accepted handoff interface. |
| `tasks/codex/flywheel_v1_handoff_ui_readability_p0_2026-05-12.md` | accepted implementation packet | evolution flywheel v1 / Gemini UI delegate | First real bounded packet dispatched through the accepted handoff interface. |
| `tasks/codex/flywheel_v1_handoff_ui_readability_absorption_2026-05-12.md` | accepted absorption | evolution flywheel v1 / controller | Handoff UI is readable; next product slice is chat context into typed preview/handoff without canonicalizing chat input. |
| `tasks/codex/project_control_surface_p1_mainline_sync_brief_2026-05-11.md` | superseded delegate brief | project control surface / prior Antigravity UI | Superseded by the Gemini CLI execution packet; keep as background context only. |
| `tasks/codex/project_control_surface_p1_gemini_ui_packet_2026-05-11.md` | executed UI delegate packet | project control surface / Gemini CLI UI | Gemini implementation returned; see result and controller absorption for current status. |
| `tasks/codex/project_control_surface_p1_gemini_ui_result_2026-05-11.md` | reviewed UI delegate result | project control surface / Gemini CLI UI | Implementation returned and local build passed; adapter write degradation recorded. |
| `tasks/codex/project_control_surface_p1_gemini_ui_absorption_2026-05-11.md` | accepted-with-changes absorption | project control surface / controller | Stale next action fixed; Gemini new-file artifact write and Claude review output remain mechanism gaps. |
| `docs/RUNTIME_OPERATOR_LOOP_PROTOCOL_2026-05-09.md` | active protocol | runtime operator / governance | Use `operator -> runtime review -> controller`; raw operator reports do not bypass review. |
| `tasks/codex/runtime_operator_ready_recheck_result_2026-05-09.md` | reviewed runtime digest | runtime operator | Runtime is ready enough for the active mainline; keep Redis PID and watchdog as operator follow-ups. |
| `.runtime/runtime-operator/reviews/runtime_operator_ready_recheck_review_2026-05-09.md` | accepted-with-changes runtime review | runtime review | Mainline unblocked; no controller escalation. |
| `tasks/codex/operations_adapter_and_automation_repair_absorption_2026-05-13.md` | accepted operations repair | controller governance | Claude CLI L1 review runner repaired; local stall executor reactivated; OpenClaw Kimi demoted until gateway readiness is repaired. |
| `tasks/codex/ai_conversation_entry_alignment_p0_2026-05-06.md` | active alignment packet | AI conversation entry | Use to define the smallest bridge from `/chat` into flywheel inspect/controller packets. |
| `tasks/codex/ai_conversation_entry_alignment_result_2026-05-07.md` | accepted-with-changes audit result | AI conversation entry | Use the UI-only bridge as the next implementation slice; do not add backend adapter first. |
| `tasks/codex/ai_conversation_entry_bridge_p0_2026-05-07.md` | active implementation packet | AI conversation entry | Implement the bounded UI-only `/chat` to flywheel inspect bridge; raw chat remains non-canonical. |
| `tasks/codex/ai_conversation_entry_bridge_result_2026-05-07.md` | accepted-with-changes result | AI conversation entry | `/chat` can hand transient input to `/evolution`; storage failure finding absorbed. |
| `tasks/codex/ai_entry_typed_handoff_provenance_p0_2026-05-13.md` | accepted implementation packet | AI conversation entry | Chat handoff provenance now flows into typed Flywheel reviewer note without canonicalizing raw chat. |
| `tasks/codex/ai_entry_typed_handoff_provenance_absorption_2026-05-13.md` | accepted absorption | AI conversation entry / controller | Next validation is browser smoke for chat message -> Flywheel prefill -> reviewerNote provenance -> typed preview/handoff. |
| `tasks/codex/ai_entry_typed_handoff_browser_smoke_result_2026-05-13.md` | partial test result | AI conversation entry / test delegate | Chat-to-Flywheel bridge was browser-validated; typed preview/handoff was not proven because mocks targeted the wrong endpoint and response shape. |
| `tasks/codex/ai_entry_typed_handoff_browser_smoke_absorption_2026-05-13.md` | accepted-with-changes absorption | AI conversation entry / controller | Delegate `ACCEPT` recommendation downgraded; next gate is a narrower corrected preview smoke. |
| `tasks/codex/ai_entry_typed_handoff_preview_smoke_fix_p0_2026-05-13.md` | queued test packet | AI conversation entry / test delegate | Validate reviewer-note provenance and typed preview payload with correct conversation-runtime mocks. |
| `tasks/codex/ai_entry_typed_handoff_preview_smoke_fix_result_2026-05-13.md` | rejected test result | AI conversation entry / test delegate | Timed out and produced contradictory selector-based evidence; not accepted as gate proof. |
| `tasks/codex/ai_entry_typed_handoff_preview_smoke_fix_absorption_2026-05-13.md` | rejected absorption | AI conversation entry / controller | Test lane needs deterministic script-based smoke before this gate can close. |
| `scripts/smoke/ai_entry_typed_handoff_preview_smoke.mjs` | accepted smoke helper | AI conversation entry / test tooling | Deterministic Playwright smoke for chat-originated typed preview payload validation. |
| `tasks/codex/ai_entry_typed_handoff_preview_smoke_script_result_2026-05-13.md` | accepted smoke result | AI conversation entry / controller | Typed preview request now preserves chat handoff provenance and `explicit_non_canonical=true`. |
| `.runtime/reviews/results/AI_ENTRY_TYPED_PREVIEW_SMOKE_AND_REVIEWER_NOTE_REVIEW_2026_05_13.md` | accepted-with-changes review | local L1 review | Correctness accepted; scope-change and dirty-worktree findings absorbed. |
| `tasks/codex/ai_entry_typed_preview_smoke_and_reviewer_note_review_absorption_2026-05-13.md` | accepted-with-changes absorption | AI conversation entry / controller | Records controller-approved product fix after test exposed reviewer note provenance loss. |
| `tasks/codex/flywheel_v1_execution_feedback_closure_smoke_p0_2026-05-13.md` | executed test packet | evolution flywheel v1 / test tooling | Extends the deterministic smoke through execution-feedback closure. |
| `tasks/codex/flywheel_v1_execution_feedback_closure_smoke_result_2026-05-13.md` | accepted smoke result | evolution flywheel v1 / controller | Browser smoke validates chat handoff -> inspect -> typed preview -> worker bridge -> execution feedback -> loop closure summary. |
| `.runtime/reviews/results/FLYWHEEL_V1_EXECUTION_FEEDBACK_CLOSURE_SMOKE_REVIEW_2026_05_13.md` | accepted review | local L1 review | Review accepted the execution-feedback closure smoke; mock/live backend gap recorded. |
| `tasks/codex/flywheel_v1_execution_feedback_closure_smoke_review_absorption_2026-05-13.md` | accepted absorption | evolution flywheel v1 / controller | Mainline can proceed to one real bounded delegate packet through the accepted inspect-only loop. |
| `tasks/codex/flywheel_v1_first_real_delegate_packet_smoke_script_command_p0_2026-05-14.md` | executed implementation packet | evolution flywheel v1 / frontend-test tooling delegate | First real bounded delegate packet after loop smoke; adds reusable npm commands for the accepted Flywheel smoke. |
| `tasks/codex/flywheel_v1_first_real_delegate_packet_smoke_script_command_result_2026-05-14.md` | reviewed delegate result | evolution flywheel v1 / frontend-test tooling delegate | Delegate added `smoke:flywheel-loop` and `smoke:flywheel-loop:check`; controller validation passed. |
| `.runtime/reviews/results/FLYWHEEL_V1_FIRST_REAL_DELEGATE_PACKET_SMOKE_SCRIPT_COMMAND_REVIEW_2026_05_14.md` | accepted review | local L1 review | Review accepted the bounded npm-script implementation. |
| `tasks/codex/flywheel_v1_first_real_delegate_packet_smoke_script_command_absorption_2026-05-14.md` | accepted absorption | evolution flywheel v1 / controller | First real bounded delegate packet accepted; next is a small product-facing packet through the same loop. |
| `tasks/codex/project_control_surface_loop_status_p2_gemini_ui_packet_2026-05-14.md` | executed UI packet | project control surface / UI delegate | Adds visible Flywheel V1 loop status and reusable smoke command to `/control`. |
| `tasks/codex/project_control_surface_loop_status_p2_gemini_ui_absorption_2026-05-14.md` | rejected delegate attempt | project control surface / Gemini UI delegate | Gemini timed out and did not complete required result artifact or flywheelLoop section. |
| `tasks/codex/project_control_surface_loop_status_p2_gemini_ui_result_2026-05-14.md` | reviewed UI result | project control surface / Claude UI fallback | Claude fallback completed the bounded UI packet after Gemini timeout. |
| `.runtime/reviews/results/PROJECT_CONTROL_SURFACE_LOOP_STATUS_P2_UI_REVIEW_2026_05_14.md` | accepted review | local L1 review | Review accepted the `/control` Flywheel loop status UI. |
| `tasks/codex/project_control_surface_loop_status_p2_ui_review_absorption_2026-05-14.md` | accepted absorption | project control surface / controller | `/control` now surfaces accepted loop state, reusable smoke command, and next product-facing gate. |
| `tasks/codex/project_control_surface_loop_status_product_packet_closure_2026-05-14.md` | accepted closure | project control surface / controller | First small product-facing packet completed through delegate result, review, controller absorption, and corrective validation. |
| `tasks/codex/flywheel_v1_worker_bridge_readability_p1_2026-05-14.md` | executed UI packet | evolution flywheel v1 / UI delegate | Improves Worker Packet Bridge and Execution Feedback visible labels for real handoff use. |
| `tasks/codex/flywheel_v1_worker_bridge_readability_result_2026-05-14.md` | reviewed UI result | evolution flywheel v1 / UI delegate | Delegate replaced visible mojibake labels with concise operational English copy. |
| `.runtime/reviews/results/FLYWHEEL_V1_WORKER_BRIDGE_READABILITY_REVIEW_2026_05_14.md` | accepted-with-changes review | local L1 review | Review found one remaining copied-state label; controller fixed it. |
| `tasks/codex/flywheel_v1_worker_bridge_readability_review_absorption_2026-05-14.md` | accepted absorption | evolution flywheel v1 / controller | Worker handoff and execution-feedback surfaces are readable enough for next real packet use. |
| `tasks/codex/flywheel_v1_inspect_panel_readability_p1_2026-05-15.md` | executed UI packet | evolution flywheel v1 / UI delegate | Cleans the primary Flywheel inspect panel labels for real product use. |
| `tasks/codex/flywheel_v1_inspect_panel_readability_result_2026-05-15.md` | reviewed UI result | evolution flywheel v1 / UI delegate | Delegate replaced visible inspect-panel mojibake labels with English operational copy. |
| `.runtime/reviews/results/FLYWHEEL_V1_INSPECT_PANEL_READABILITY_REVIEW_2026_05_15.md` | accepted review | local L1 review | Review accepted the inspect panel readability packet. |
| `tasks/codex/flywheel_v1_inspect_panel_readability_review_absorption_2026-05-15.md` | accepted absorption | evolution flywheel v1 / controller | Flywheel inspect entry is readable enough for real product use. |
| `tasks/codex/flywheel_v1_next_product_packet_selection_2026-05-15.md` | accepted controller selection | evolution flywheel v1 / controller | Selected copy-ready delegate packet export as the next product-facing packet. |
| `tasks/codex/flywheel_v1_copy_ready_delegate_packet_export_p0_2026-05-15.md` | executed implementation packet | evolution flywheel v1 / export path | Defines the bounded copy-ready Markdown delegate packet export slice. |
| `tasks/codex/flywheel_v1_copy_ready_delegate_packet_export_result_2026-05-16.md` | reviewed candidate result | evolution flywheel v1 / controller-authored candidate patch | Backend generated Markdown now has scope, acceptance criteria, validation commands, stop conditions, and `stop_condition` result field. |
| `.runtime/reviews/results/FLYWHEEL_V1_COPY_READY_DELEGATE_PACKET_EXPORT_REVIEW_2026_05_16.md` | accepted review | local L1 review | Review accepted the copy-ready export patch; wrapper timeout is an operations harness caveat. |
| `tasks/codex/flywheel_v1_copy_ready_delegate_packet_export_absorption_2026-05-16.md` | accepted absorption | evolution flywheel v1 / controller | Copy-ready inspect-only delegate packet export path accepted; next is one real bounded worker result through execution-feedback inspect. |
| `tasks/codex/flywheel_v1_copy_ready_export_browser_smoke_p0_2026-05-16.md` | executed worker packet | evolution flywheel v1 / test delegate | First real bounded worker task after copy-ready export acceptance; validates clipboard export path in browser smoke. |
| `tasks/codex/flywheel_v1_copy_ready_export_browser_smoke_result_2026-05-16.md` | reviewed worker result | evolution flywheel v1 / test delegate | Smoke helper now validates Copy Handoff Packet and clipboard Markdown sections. |
| `.runtime/reviews/results/FLYWHEEL_V1_COPY_READY_EXPORT_BROWSER_SMOKE_REVIEW_2026_05_16.md` | accepted-with-changes review | local L1 review | Review accepted scope and implementation; controller closed full-browser-smoke validation gap. |
| `tasks/codex/flywheel_v1_copy_ready_export_browser_smoke_absorption_2026-05-16.md` | accepted-with-changes absorption | evolution flywheel v1 / controller | First real bounded worker result consumed through review and controller validation. |
| `tasks/codex/flywheel_v1_execution_feedback_copy_ready_packet_p1_2026-05-16.md` | executed product-use worker packet | evolution flywheel v1 / development worker | Makes execution-feedback return packets copy-ready for controller absorption. |
| `tasks/codex/flywheel_v1_execution_feedback_copy_ready_packet_result_2026-05-16.md` | reviewed worker result | evolution flywheel v1 / development worker | Execution feedback copy button and copied Markdown feedback packet now include required absorption fields and boundaries. |
| `.runtime/reviews/results/FLYWHEEL_V1_EXECUTION_FEEDBACK_COPY_READY_PACKET_REVIEW_2026_05_16.md` | accepted-with-changes review | local L1 review | Review accepted implementation; controller closed full-browser-smoke validation gap. |
| `tasks/codex/flywheel_v1_execution_feedback_copy_ready_packet_absorption_2026-05-16.md` | accepted-with-changes absorption | evolution flywheel v1 / controller | Flywheel loop now has copy-ready forward handoff and return feedback packets; runtime API repair is next live-route blocker. |
| `tasks/codex/project_control_surface_current_mainline_sync_ui_review_result_2026-05-16.md` | accepted UI review evidence | Gemini UI delegate | `/control` static snapshot is aligned with current mainline; ACP artifact write remains noisy but file was verified locally. |
| `tasks/codex/runtime_operator_mainline_readiness_recheck_result_2026-05-16.md` | blocked runtime evidence | runtime operator | API is down on port 8000; runtime repair packet is required before live Flywheel route validation. |
| `tasks/codex/runtime_api_start_packet_2026-05-16.md` | executed runtime repair packet | runtime operator | Authorized API start and health verification only. |
| `tasks/codex/runtime_api_start_result_2026-05-16.md` | reviewed runtime repair result | runtime operator | API restored on port 8000; runtime degraded only for watchdog. |
| `tasks/codex/runtime_api_start_review_result_2026-05-16.md` | accepted runtime review | runtime review | Runtime repair stayed in scope and unblocked live Flywheel route validation. |
| `tasks/codex/runtime_api_start_absorption_2026-05-16.md` | accepted runtime absorption | controller | API runtime readiness accepted; proceed with live Flywheel route validation. |
| `tasks/codex/flywheel_v1_live_route_validation_p1_2026-05-16.md` | executed live validation packet | evolution flywheel v1 / test delegate | Validates live task-packet preview endpoint after runtime API repair. |
| `tasks/codex/flywheel_v1_live_route_validation_result_2026-05-16.md` | reviewed live validation result | evolution flywheel v1 / test delegate | Live preview endpoint returned candidate packet and copy-ready handoff preview while staying inspect-only. |
| `.runtime/reviews/results/FLYWHEEL_V1_LIVE_ROUTE_VALIDATION_REVIEW_2026_05_16.md` | accepted review | local L1 review | Review accepted live route validation with health utility timing caveat. |
| `tasks/codex/flywheel_v1_live_route_validation_absorption_2026-05-16.md` | accepted absorption | evolution flywheel v1 / controller | First live Flywheel task-packet preview route validation accepted after runtime repair. |
| `tasks/codex/flywheel_v1_chat_origin_guided_path_ui_packet_2026-05-16.md` | executed UI implementation packet | evolution flywheel v1 / UI delegate | Adds visible chat-origin guided path for the AI conversation entry into the Flywheel loop. |
| `tasks/codex/flywheel_v1_chat_origin_guided_path_ui_result_2026-05-16.md` | implemented UI result | evolution flywheel v1 / UI delegate | Guided path implemented using local UI state and explicit inspect-only boundary copy. |
| `tasks/codex/flywheel_v1_chat_origin_guided_path_smoke_result_2026-05-16.md` | test delegate result | evolution flywheel v1 / test delegate | Static smoke check passed; controller later closed browser smoke gap with full smoke. |
| `tasks/codex/flywheel_v1_chat_origin_guided_path_ui_absorption_2026-05-16.md` | accepted-with-changes absorption | evolution flywheel v1 / controller | Chat-origin guided path accepted after build and browser smoke passed. |
| `tasks/codex/flywheel_v1_candidate_selection_friction_packet_p0_2026-05-17.md` | incident evidence | evolution flywheel v1 / UI delegate | Original packet/result had mojibake and wrong validation commands; do not treat as accepted evidence. |
| `tasks/codex/flywheel_v1_candidate_selection_friction_correction_result_2026-05-17.md` | reviewed correction result | evolution flywheel v1 / controller correction | Manual candidate filter and smoke coverage corrected; validation passed. |
| `.runtime/reviews/results/FLYWHEEL_V1_CANDIDATE_SELECTION_FRICTION_REVIEW_2026_05_17.md` | accepted-with-changes review | local L1 review | Reviewer required controller browser smoke; condition satisfied by `ok: true` smoke. |
| `tasks/codex/flywheel_v1_candidate_selection_friction_absorption_2026-05-17.md` | accepted-with-changes absorption | evolution flywheel v1 / controller | Candidate-selection friction reduced; next gap is explicit post-preview next action without auto-dispatch. |
| `tasks/codex/flywheel_v1_post_preview_next_action_ui_packet_2026-05-17.md` | executed UI packet | evolution flywheel v1 / Gemini UI delegate | Adds explicit controller next-action panel after task preview. |
| `tasks/codex/flywheel_v1_post_preview_next_action_ui_result_2026-05-17.md` | reviewed UI result | evolution flywheel v1 / Gemini UI delegate | Controller corrected validation posture and completed browser smoke. |
| `.runtime/reviews/results/FLYWHEEL_V1_POST_PREVIEW_NEXT_ACTION_UI_REVIEW_2026_05_17.md` | accepted-with-changes review | local L1 review | Reviewer required controller browser smoke; condition satisfied by `ok: true` smoke. |
| `tasks/codex/flywheel_v1_post_preview_next_action_ui_absorption_2026-05-17.md` | accepted-with-changes absorption | evolution flywheel v1 / controller | Post-preview next action is explicit; next mainline step is one bounded product-use worker packet through the manual loop. |
| `tasks/codex/flywheel_v1_packet_builder_ascii_cleanup_packet_2026-05-17.md` | executed worker packet | evolution flywheel v1 / frontend coding delegate | First bounded product-use worker packet after post-preview gate; cleans copied packet builders. |
| `tasks/codex/flywheel_v1_packet_builder_ascii_cleanup_result_2026-05-17.md` | reviewed worker result | evolution flywheel v1 / frontend coding delegate | Copied packet labels and fallbacks are ASCII-safe; smoke validates copied output. |
| `.runtime/reviews/results/FLYWHEEL_V1_PACKET_BUILDER_ASCII_CLEANUP_REVIEW_2026_05_17.md` | accepted review | local L1 review | Review accepted scope and correctness; controller browser smoke passed. |
| `tasks/codex/flywheel_v1_packet_builder_ascii_cleanup_absorption_2026-05-17.md` | accepted absorption | evolution flywheel v1 / controller | First post-preview product-use worker packet accepted; next step is real delegated worker result through execution-feedback inspect. |
| `tasks/codex/flywheel_v1_real_worker_execution_feedback_inspect_packet_p0_2026-05-18.md` | active packet | evolution flywheel v1 / controller | Run one real worker result through execution-feedback inspect; produce result + review + absorption artifacts. |
| `tasks/codex/flywheel_v1_real_worker_execution_feedback_worker_brief_p0_2026-05-18.md` | active brief | evolution flywheel v1 / delegated worker | Worker-facing schema for a real result artifact suitable for execution-feedback inspect. |
| `tasks/codex/flywheel_candidate_chat_conversation_result.md` | accepted worker result | evolution flywheel v1 / local worker | Real delegated worker result consumed through execution-feedback inspect. |
| `tasks/codex/flywheel_v1_real_worker_execution_feedback_inspect_result_2026-05-18.md` | reviewed result | evolution flywheel v1 / controller | Live task-packet preview and execution-feedback inspect succeeded; full-result timeout recorded as runtime/LLM caveat. |
| `docs/reviews/active/review_for_flywheel_v1_real_worker_execution_feedback_inspect_2026-05-18.md` | accepted-with-changes review | local L1 review | Review accepts loop closure and tracks long-input timeout as operations risk. |
| `tasks/codex/flywheel_v1_real_worker_execution_feedback_inspect_absorption_2026-05-18.md` | accepted-with-changes absorption | evolution flywheel v1 / controller | Real worker-result feedback loop closed; next mainline gap is AI-entry-originated useful packet selection through the same loop. |
| `tasks/codex/ai_entry_useful_packet_selection_p0_2026-05-18.md` | accepted selection packet | AI conversation entry / controller | Selects AI Entry Task Packet Composer P0 as the next useful mainline packet. |
| `tasks/codex/ai_entry_useful_packet_selection_absorption_2026-05-18.md` | accepted-with-changes absorption | AI conversation entry / controller | Implementation is blocked until dirty-tree containment produces a scoped package boundary. |
| `tasks/codex/dirty_tree_containment_absorption_2026-05-18.md` | accepted containment | governance / worktree operations | No new implementation patch starts from the shared dirty tree until a scoped package boundary is accepted. |
| `tasks/codex/flywheel_readiness_scoped_package_boundary_2026-05-18.md` | accepted-with-changes package boundary | worktree operations / flywheel readiness | First candidate package is `flywheel_latest_feedback_loop_closure_2026-05-18`; staging waits on scope/CRLF checks. |
| `tasks/codex/flywheel_readiness_scoped_package_boundary_absorption_2026-05-18.md` | accepted-with-changes absorption | worktree operations / controller | Defines staging conditions before AI Entry Composer implementation can begin. |
| `tasks/codex/runtime_operator_node_spawn_pressure_diagnosis_result_2026-05-16.md` | runtime diagnosis result | runtime operator | Identifies stale Node process pressure as likely cause of transient Next `spawn UNKNOWN`; cleanup should stay in runtime lane. |
| `tasks/codex/runtime_operator_stale_node_cleanup_absorption_2026-05-16.md` | accepted runtime absorption | runtime / controller | Stale May 13 Next/smoke Node processes cleaned; build rerun completed without static worker crash logs. |
| `tasks/codex/governance_execution_record_reviewer_gate_correction_absorption_2026-05-17.md` | accepted-with-changes governance absorption | governance / controller | Material work now requires task packet, result artifact, independent reviewer artifact, and controller absorption. |
| `https://github.com/brantzh6/MyAttention/pull/2` | merged | source-intelligence support | Keep as accepted support evidence; do not treat source intelligence as the top-level mainline. |
| `https://github.com/brantzh6/MyAttention/pull/4` | merged | controller governance | Review gate absorbed and promoted; source-intelligence support no longer owns top-level mainline. |
| `https://github.com/brantzh6/MyAttention/pull/5` | merged | controller governance | Next mainline task packets are accepted; use issues #6, #7, and #8 as GitHub collaboration handles. |
| `https://github.com/brantzh6/MyAttention/pull/10` | merged | AI conversation entry | Chat-to-flywheel handoff bridge accepted into mainline. |
| `https://github.com/brantzh6/MyAttention/pull/11` | merged | evolution flywheel v1 / test execution | Browser smoke packet accepted into mainline. |
| `https://github.com/brantzh6/MyAttention/pull/12` | merged | project control surface | `/control` static project anchor accepted into mainline. |

## GitHub/Codex Review

| Artifact | Status | Owner/Lane | Next Action |
| --- | --- | --- | --- |
| `https://github.com/brantzh6/MyAttention/pull/1` | merged | GitHub/Codex review | Keep historical review evidence only; mainline can continue from the merge commit. |
| `docs/IKE_SCOPED_GITHUB_CODEX_REVIEW_PREP_2026-04-29.md` | active prep record | controller governance | Keep scoped PR separate from dirty controller worktree. |
| `docs/IKE_PR1_GITHUB_CODEX_REVIEW_FINDINGS_REVIEW_ABSORPTION_2026-04-30.md` | active review absorption | GitHub/Codex review | Records the two actionable findings now fixed locally. |

## Review Automation

| Artifact | Status | Owner/Lane | Next Action |
| --- | --- | --- | --- |
| `docs/IKE_REVIEW_CADENCE_AND_AUTOMATION_POLICY_2026-04-29.md` | active policy | review automation governance | Use as current review cadence boundary. |
| `docs/IKE_REVIEW_AUTOMATION_P0_IMPLEMENTATION_PACKET_2026-04-29.md` | accepted packet | review automation | Keep as PR #1 scope evidence. |
| `docs/IKE_REVIEW_AUTOMATION_P0_RESULT_2026-04-29.md` | accepted result | review automation | Historical note: PR #1 review outcome was later resolved and merged. |
| `docs/IKE_REVIEW_AUTOMATION_P1_EXECUTION_BRIDGE_PACKET_2026-04-29.md` | accepted packet | review automation | Keep delegated execution bridge bounded. |
| `docs/IKE_REVIEW_AUTOMATION_P1_EXECUTION_BRIDGE_RESULT_2026-04-29.md` | accepted result | review automation | Historical note: PR #1 review outcome was later resolved and merged. |
| `docs/IKE_REVIEW_AUTOMATION_P2_REAL_L1_OPERATIONAL_SMOKE_PACKET_2026-04-29.md` | accepted-with-changes packet | review automation | Require controller verification of result-file completion. |
| `docs/IKE_REVIEW_AUTOMATION_P2_REAL_L1_OPERATIONAL_SMOKE_RESULT_2026-04-29.md` | accepted-with-changes result | review automation | Do not treat wrapper success as completed review output. |

## Flywheel Readiness

| Artifact | Status | Owner/Lane | Next Action |
| --- | --- | --- | --- |
| `docs/IKE_FLYWHEEL_INSPECT_DECISION_READINESS_TAGS_P0_PACKET_2026-04-29.md` | accepted packet | flywheel readiness | Keep inspect-only truth boundary. |
| `docs/IKE_FLYWHEEL_INSPECT_DECISION_READINESS_TAGS_P0_RESULT_2026-04-29.md` | accepted result | flywheel readiness | Historical note: PR #1 review outcome was later resolved and merged. |

## Visual Control Surface

| Artifact | Status | Owner/Lane | Next Action |
| --- | --- | --- | --- |
| prior `/control` UI evidence | optional local evidence | visual control surface | May exist only in an unpublished local quarantine snapshot; do not rely on it for collaboration. Recreate or recover through a clean GitHub branch/PR. |
| prior `control-surface` snapshot evidence | optional local evidence | visual control surface | May inform implementation if available locally, but the PR must be reviewable without unpublished refs. |
| `docs/IKE_VISUAL_CONTROL_SURFACE_BRANCH_DESIGN_2026-04-29.md` | active design evidence | visual control surface | Reuse as background only; the next packet must reflect the corrected three-task mainline. |
| `docs/IKE_VISUAL_CONTROL_SURFACE_P0_PROVENANCE_FOLLOWUP_PACKET_2026-04-29.md` | historical packet | UI implementation delegate | Preserve static provenance boundary. |
| `docs/IKE_VISUAL_CONTROL_SURFACE_P0_PROVENANCE_FOLLOWUP_RESULT_2026-04-29.md` | historical accepted evidence | visual control surface | Build evidence exists historically, but current clean mainline does not contain the UI files. |
| `docs/IKE_VISUAL_CONTROL_SURFACE_P0_PROVENANCE_FOLLOWUP_REVIEW_ABSORPTION_2026-04-30.md` | historical review absorption | visual control surface | L1 findings were fixed historically; future promotion still requires clean PR review. |
| `docs/IKE_VISUAL_CONTROL_SURFACE_P1_PROGRESS_DASHBOARD_RESULT_2026-04-30.md` | historical result | visual control surface | Use as design input for Project Control Surface Anchor P0. |

## Governance / Worktree Cleanup

| Artifact | Status | Owner/Lane | Next Action |
| --- | --- | --- | --- |
| `docs/IKE_WORKTREE_DOC_KNOWLEDGE_GOVERNANCE_PLAN_2026-04-29.md` | active design plan | governance | Use active-state manifest as Phase 1 implementation. |
| `docs/IKE_MAINLINE_STATE_MANIFEST_P0_PACKET_2026-04-29.md` | accepted packet | documentation/governance worker | Keep active state manifest current. |
| `docs/CURRENT_MAINLINE_STATE.json` | accepted active state | documentation/governance worker | Use as active governance source. |
| `docs/CURRENT_ACTIVE_ARTIFACTS.md` | accepted active index | documentation/governance worker | Keep active artifacts compact. |
| `docs/CURRENT_REVIEW_QUEUE.md` | accepted review queue | documentation/governance worker | Keep open reviews visible. |
| `docs/CURRENT_MAINLINE_HANDOFF_COMPACT_2026-04-30.md` | accepted compact handoff | controller governance | Use this as the first-read continuation surface. |
| `docs/IKE_MAINLINE_STATE_MANIFEST_P0_RESULT_2026-04-29.md` | accepted result | documentation/governance worker | Use as manifest P0 evidence. |
| `scripts/governance/classify_worktree.py` | accepted tool | governance tooling | Run before scoped review prep. |
| `scripts/governance/README.md` | accepted usage note | governance tooling | Keep classifier usage documented. |
| local dirty-worktree classifier packet evidence | optional local evidence | governance tooling | Historical classifier packet may exist in local quarantine only; not an active continuation dependency. |
| local dirty-worktree classifier result evidence | optional local evidence | governance tooling | Historical classifier result may exist in local quarantine only; current active classifier truth comes from rerunning `scripts/governance/classify_worktree.py`. |
| `docs/IKE_WORKTREE_ARCHIVE_INDEX_PLAN_P0_RESULT_2026-04-30.md` | accepted-with-changes plan | governance cleanup | Use as planning boundary; no movement authorized. |
| `docs/IKE_WORKTREE_ARCHIVE_INDEX_PLAN_P0_REVIEW_ABSORPTION_2026-04-30.md` | accepted review absorption | governance cleanup | Latest observed planning count: 197 entries, 9 groups. |
| `docs/IKE_DIRTY_WORKTREE_RECONCILIATION_DOCS_ONLY_RESULT_2026-04-30.md` | accepted result | governance cleanup | Documents the docs-only cleanup slice for controller-facing surfaces. |
| `docs/IKE_CURRENT_CONTINUATION_HISTORY_RECONCILIATION_RESULT_2026-04-30.md` | accepted result | controller continuation | Removes stale PR #1 wait semantics from active surfaces. |
| `docs/IKE_ACTIVE_SURFACES_HISTORY_ONLY_RECONCILIATION_RESULT_2026-04-30.md` | accepted result | controller continuation | Confirms the active surfaces are history-only for PR #1 wait wording. |
| `docs/IKE_DIRTY_WORKTREE_SCOPED_CLEANUP_PLANNING_RESULT_2026-04-30.md` | accepted result | governance cleanup | Plans the next bounded cleanup node for the mixed worktree. |
| `docs/IKE_DIRTY_WORKTREE_SCOPED_CLEANUP_PACKET_2026-04-30.md` | accepted packet | governance cleanup | Historical packet that defined the docs-only scoped cleanup slice. |
| `docs/IKE_DIRTY_WORKTREE_SCOPED_CLEANUP_PACKET_RESULT_2026-04-30.md` | accepted result | governance cleanup | Accepts the docs-only scoped cleanup packet as the next bounded node. |
| `docs/IKE_CONTROLLER_SURFACE_HISTORY_AUDIT_PACKET_2026-04-30.md` | accepted packet | controller continuation | Historical packet for auditing the active surfaces for live blocker wording. |
| `docs/IKE_CONTROLLER_SURFACE_HISTORY_AUDIT_RESULT_2026-04-30.md` | accepted result | controller continuation | Confirms the active surfaces are history-only. |
| `docs/IKE_LONG_HANDOFF_HISTORY_NOTE_NORMALIZATION_PACKET_2026-04-30.md` | accepted packet | controller continuation | Historical packet that normalized the remaining long-handoff PR #1 wording into evidence-only text. |
| `docs/IKE_LONG_HANDOFF_HISTORY_NOTE_NORMALIZATION_RESULT_2026-04-30.md` | accepted result | controller continuation | Confirms the long handoff is evidence-only for the remaining PR #1 wording. |
| `docs/IKE_LONG_HANDOFF_REVIEW_TIME_OBSERVATION_NORMALIZATION_PACKET_2026-04-30.md` | accepted packet | controller continuation | Historical packet that normalized the remaining review-time observation wording in the long handoff. |
| `docs/IKE_LONG_HANDOFF_REVIEW_TIME_OBSERVATION_NORMALIZATION_RESULT_2026-04-30.md` | accepted result | controller continuation | Confirms the long handoff review-time observation is historical evidence. |
| `docs/IKE_LONG_HANDOFF_BLOCKER_NOTE_NORMALIZATION_PACKET_2026-04-30.md` | accepted packet | controller continuation | Historical packet that normalized remaining blocker-style wording in the long handoff. |
| `docs/IKE_LONG_HANDOFF_BLOCKER_HISTORY_NORMALIZATION_PACKET_2026-04-30.md` | accepted packet | controller continuation | Historical packet that normalized the remaining blocker-style wording in the long handoff into historical evidence. |
| `docs/IKE_LONG_HANDOFF_BLOCKER_HISTORY_NORMALIZATION_RESULT_2026-04-30.md` | accepted result | controller continuation | Confirms the long handoff blocker-style wording is historical evidence. |
| `docs/IKE_LONG_HANDOFF_FINAL_BLOCKER_HISTORY_NORMALIZATION_PACKET_2026-04-30.md` | accepted packet | controller continuation | Historical packet that normalized the last remaining current-blocker phrases in the long handoff. |
| `docs/IKE_LONG_HANDOFF_FINAL_BLOCKER_HISTORY_NORMALIZATION_RESULT_2026-04-30.md` | accepted result | controller continuation | Confirms the long handoff no longer contains live-looking current-blocker phrases. |
| `docs/IKE_SOURCE_INTELLIGENCE_GITHUB_SIGNAL_RELATION_HINTS_PACKET_2026-05-02.md` | merged support packet | source intelligence support | Included in PR #2; source intelligence now supports flywheel input quality. |
| `docs/IKE_SOURCE_INTELLIGENCE_GITHUB_SIGNAL_RELATION_HINTS_RESULT_2026-05-02.md` | merged support result | source intelligence support | PR #2 merged at `acf922c`; keep as accepted support evidence. |
| `docs/IKE_SOURCE_INTELLIGENCE_GITHUB_SIGNAL_RELATION_HINTS_REVIEW_ABSORPTION_2026-05-02.md` | accepted review absorption | source intelligence quality | Captures the accepted re-review and controller absorption for the fixed slice. |
| `docs/IKE_ARCHIVE_INDEX_SCHEMA_P0_RESULT_2026-04-30.md` | accepted schema | governance cleanup | Use for index-only archive/review identity packets. |
| `docs/IKE_ARCHIVE_INDEX_SCHEMA_P0_REVIEW_ABSORPTION_2026-04-30.md` | accepted review absorption | governance cleanup | L1 findings fixed; movement manifest design deferred. |
| `docs/archive/REVIEW_ARTIFACT_IDENTITY_INDEX_2026-04.md` | accepted index-only artifact | review artifact governance | Representative review identity map; no rename/move authorized. |
| `docs/IKE_REVIEW_ARTIFACT_IDENTITY_INDEX_P0_RESULT_2026-04-30.md` | accepted result | review artifact governance | Historical note: PR #1 payload was not available at the time of the access check. |
| `docs/IKE_PR1_CODEX_REVIEW_ACCESS_HISTORY_ONLY_RESULT_2026-04-30.md` | accepted result | review artifact governance | Converts the access check into history-only evidence. |
| `docs/IKE_REVIEW_ARTIFACT_IDENTITY_INDEX_P0_REVIEW_ABSORPTION_2026-04-30.md` | accepted review absorption | review artifact governance | No L1 findings. |
| `docs/archive/ARCHIVE_INDEX_2026-04.md` | accepted-with-changes index-only artifact | documentation archive governance | Representative April docs index; no movement authorized. |
| `docs/IKE_DOC_ARCHIVE_INDEX_2026_04_P0_RESULT_2026-04-30.md` | accepted-with-changes result | documentation archive governance | Bundle-dir P1 finding fixed. |
| `docs/IKE_DOC_ARCHIVE_INDEX_2026_04_P0_REVIEW_ABSORPTION_2026-04-30.md` | accepted review absorption | documentation archive governance | Records delegated review and controller fallback fix. |
