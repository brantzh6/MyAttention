# Flywheel V1 E2E Gap Audit Result

Date: 2026-05-07

Task ID: FLYWHEEL_V1_E2E_GAP_AUDIT_P0_2026-05-06

Result type: controller audit result

Recommendation: accept_with_changes

## Summary

The inspect-only flywheel substrate is present and testable.

Backend route coverage exists for:

- flywheel inspect
- task packet preview
- execution feedback inspect

The frontend evolution surface can drive the manual loop through the existing flywheel inspect panel and controller hook. The current product gap is not missing backend routes. The gap is that the loop is not yet demonstrably usable from the intended AI conversation entry, and it lacks browser-level E2E evidence.

## Loop Status

1. AI/conversation input
   - Status: partial.
   - Evidence: `/chat` can produce assistant output and brain-plan metadata, but it does not expose an intentional handoff into the flywheel inspect surface.

2. Flywheel inspect
   - Status: completed for inspect-only backend and frontend route wiring.
   - Evidence: `services/api/routers/conversation_runtime.py`, `services/api/conversation_runtime/flywheel_inspect.py`, `services/web/components/evolution/use-flywheel-runtime-controller.ts`.

3. Controller packet / candidate objects
   - Status: partial.
   - Evidence: the evolution controller hook builds review, absorption, decision, worker, and loop packets from inspect results, but the packet path starts inside the evolution UI rather than from a chat turn.

4. Task packet preview
   - Status: completed for inspect-only preview.
   - Evidence: `services/api/conversation_runtime/task_packet_preview.py`, `services/web/components/evolution/use-flywheel-runtime-controller.ts`.

5. Worker packet bridge
   - Status: partial.
   - Evidence: the UI supports manual packet copying and worker-result pasteback. This is acceptable for V1, but it is still a manual bridge.

6. Execution feedback inspect
   - Status: completed for inspect-only feedback analysis.
   - Evidence: `services/api/conversation_runtime/execution_feedback.py`, `services/web/components/evolution/use-flywheel-runtime-controller.ts`.

7. Review-gated controller next decision
   - Status: partial.
   - Evidence: the UI can produce decision/absorption artifacts, but promotion remains a controller action outside the runtime surface.

## Files Inspected

- `services/api/routers/conversation_runtime.py`
- `services/api/conversation_runtime/flywheel_inspect.py`
- `services/api/conversation_runtime/task_packet_preview.py`
- `services/api/conversation_runtime/execution_feedback.py`
- `services/api/conversation_runtime/contracts.py`
- `services/api/tests/test_flywheel_inspect_route.py`
- `services/api/tests/test_conversation_runtime_route.py`
- `services/web/components/evolution/flywheel-inspect-panel.tsx`
- `services/web/components/evolution/use-flywheel-runtime-controller.ts`
- `services/web/lib/api-client.ts`
- `services/api/routers/chat.py`
- `services/web/app/chat/page.tsx`
- `services/web/components/chat/chat-interface.tsx`

## Validation Run

```powershell
python -m pytest services/api/tests/test_flywheel_inspect_route.py services/api/tests/test_conversation_runtime_route.py -q
```

Result:

```text
37 passed, 3 warnings in 0.60s
```

```powershell
python -m py_compile services/api/routers/conversation_runtime.py services/api/conversation_runtime/flywheel_inspect.py services/api/conversation_runtime/task_packet_preview.py services/api/conversation_runtime/execution_feedback.py
```

Result:

```text
passed
```

No frontend files were changed in this audit, so `npm run build` was not required for this result.

## Confirmed Usable Path

The usable path today is:

```text
/evolution
  -> enter source/context manually
  -> run flywheel inspect
  -> generate review/absorption/decision/task/worker packets
  -> paste worker result manually
  -> run execution feedback inspect
  -> controller consumes result outside the runtime as promotion evidence
```

This is enough for an inspect-only V1 control loop rehearsal. It is not yet enough to claim the product has an AI conversation entry into the flywheel.

## Gaps And Blockers

- No explicit `/chat` to flywheel handoff.
- No browser-level smoke proving the whole `/evolution` manual loop works after frontend rendering.
- Worker execution remains manual by design for V1.
- Promotion remains outside runtime by design and must not be automated in this patch.
- Provenance is sufficient for inspection, but not yet enough for automatic runtime truth or memory writes.

## Recommended Next Patch

Implement the AI conversation entry bridge as a narrow UI patch:

- Add an intentional action in `/chat` for sending a chosen turn or current conversation excerpt to the existing flywheel inspect surface.
- Preserve the boundary that raw chat is non-canonical and inspect-only.
- Reuse existing `conversation_runtime` backend routes.
- Do not add persistence, scheduler behavior, memory writes, automatic worker execution, or promotion semantics.

After that bridge exists, run a browser-level smoke for:

```text
/chat -> handoff -> /evolution flywheel inspect -> task preview -> execution feedback inspect
```

## Known Risks

- A UI-only bridge can still create false confidence if it visually implies the chat turn became canonical truth.
- Local prefill state must be labeled as transient input, not persisted runtime state.
- If the bridge uses URL or browser storage, the implementation must avoid treating that state as a source of truth.
