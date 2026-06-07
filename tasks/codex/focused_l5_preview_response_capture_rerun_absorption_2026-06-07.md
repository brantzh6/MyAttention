# Controller Absorption: Focused L5 Preview Response Capture Rerun

Date: 2026-06-07
Controller: codex-controller

## Decision

accept_with_changes

## Absorbed Evidence

- Packet:
  `tasks/codex/focused_l5_preview_response_capture_rerun_packet_2026-06-06.md`
- Result:
  `tasks/codex/focused_l5_preview_response_capture_rerun_result_2026-06-06.md`
- Trace:
  `tasks/codex/focused_l5_browser_trace_rerun_2026-06-06.json`
- Independent review:
  `docs/reviews/active/review_for_focused_l5_preview_response_capture_rerun_2026-06-07.md`
- Current runtime truth:
  `ops/runtime/latest.json`

## Accepted Product Claim

The first usable Evolution Flywheel v1 L5 inspect-only loop is accepted:

1. User submits a real message through `/chat`.
2. The UI exposes and executes the chat-origin handoff to Evolution/Flywheel.
3. Inspect runs through the UI and returns HTTP 200 with candidates.
4. The user selects candidates through the manual absorption UI.
5. Request Preview becomes enabled and is triggered through the UI.
6. Preview returns HTTP 200 with the accepted inspect-only response contract:
   task-packet summary, selected label groups, controller review packet, truth
   boundaries, and `promotion_state=inspect_only`.
7. No execution, promotion, source edit, stage, commit, push, merge, or runtime
   service operation occurs.

## Explicit Boundary

This closure proves the first usable inspect-only evolution loop. It does not
prove or authorize:

- automatic worker execution;
- automatic promotion to canonical truth;
- populated execution-bound `candidate_packet` or `handoff_preview`;
- production cutover or release readiness.

Null `candidate_packet` and `handoff_preview` values are accepted for the
current inspect-only preview contract.

The browser trace proves route reachability and the supported product
interaction path. It does not prove that runtime remained continuously healthy
throughout the validation window because precheck and postcheck referenced the
same earlier runtime probe. Current runtime readiness is separate operational
truth and is not retroactive validation evidence.

## Automation Closure Finding

The OpenClaw PM -> Codex bridge has been triggering and producing real progress,
but the prior controller wakeup contract stopped after one bounded action. That
forced packet, result, review, and absorption into separate four-hour cycles.

The controller wakeup contract is corrected to allow a bounded continuation
loop of up to three gate-safe actions. OpenClaw remains the scheduler and
monitor; strong local Claude Code/Qoder/Gemini surfaces remain the complex
execution workers.

## Next Phase

The next controller phase is not another flywheel v1 proof rerun. It is:

1. synchronize `/control` and project state with this accepted milestone;
2. define the bounded promotion/package for the accepted first-usable loop;
3. reduce dirty-tree risk before broad new feature work;
4. separately repair the Claude delegate helper no-runspace defect.
