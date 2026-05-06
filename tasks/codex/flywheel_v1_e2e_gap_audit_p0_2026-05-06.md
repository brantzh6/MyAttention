# Flywheel V1 E2E Gap Audit P0

Date: 2026-05-06

Task ID: FLYWHEEL_V1_E2E_GAP_AUDIT_P0_2026-05-06

Owner: controller scopes and accepts; backend/CC or test delegate may execute audit and smoke validation.

## Goal

Determine what is missing for the first usable inspect-only IKE evolution flywheel loop.

This is a gap audit and smoke packet, not a feature expansion packet.

## Target Loop

The first usable loop is:

```text
AI/conversation input
  -> flywheel inspect
  -> controller packet / candidate objects
  -> task packet preview
  -> worker packet bridge
  -> worker result pasted back
  -> execution feedback inspect
  -> review-gated controller next decision
```

## Existing Surfaces To Inspect

Backend:

- `services/api/routers/conversation_runtime.py`
- `services/api/conversation_runtime/flywheel_inspect.py`
- `services/api/conversation_runtime/task_packet_preview.py`
- `services/api/conversation_runtime/execution_feedback.py`
- `services/api/conversation_runtime/contracts.py`
- `services/api/tests/test_flywheel_inspect_route.py`
- `services/api/tests/test_conversation_runtime_route.py`

Frontend:

- `services/web/app/evolution/page.tsx`
- `services/web/components/evolution/flywheel-inspect-panel.tsx`
- `services/web/components/evolution/task-preview-section.tsx`
- `services/web/components/evolution/worker-packet-bridge-section.tsx`
- `services/web/components/evolution/execution-feedback-section.tsx`
- `services/web/components/evolution/use-flywheel-runtime-controller.ts`
- `services/web/components/evolution/use-flywheel-runtime-state.ts`

## Questions To Answer

1. Can the backend route chain run with deterministic test data?
2. Can the frontend drive each step without manual hidden state outside the UI?
3. Does each step preserve inspect-only / non-canonical truth boundaries?
4. Where does the loop currently require manual copy/paste?
5. Where does the loop lack enough provenance to make a controller decision?
6. What is the smallest next implementation patch to make the loop demonstrably usable?

## Validation

Required audit validation:

```powershell
python -m pytest services/api/tests/test_flywheel_inspect_route.py services/api/tests/test_conversation_runtime_route.py -q
```

Required compile validation:

```powershell
python -m py_compile services/api/routers/conversation_runtime.py services/api/conversation_runtime/flywheel_inspect.py services/api/conversation_runtime/task_packet_preview.py services/api/conversation_runtime/execution_feedback.py
```

Frontend validation if frontend files are touched:

```powershell
cd services/web
npm run build
```

## Non-Goals

- no persistence
- no automatic worker execution
- no scheduler changes
- no promotion semantics
- no memory write
- no broad UI redesign
- no source-intelligence heuristic expansion

## Expected Output

Return:

1. loop status by step
2. files inspected
3. validation run
4. confirmed usable path
5. gaps / blockers
6. recommended next patch
7. recommendation: `accept`, `accept_with_changes`, or `reject`

## Stop Conditions

Stop and report if:

- a route cannot be imported
- tests cannot run
- any required step would require persistence or automatic execution
- frontend and backend contracts disagree in a way that needs implementation
