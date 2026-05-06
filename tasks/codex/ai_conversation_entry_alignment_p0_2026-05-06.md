# AI Conversation Entry Alignment P0

Date: 2026-05-06

Task ID: AI_CONVERSATION_ENTRY_ALIGNMENT_P0_2026-05-06

Owner: controller scopes and accepts; backend/CC and UI delegate may inspect or implement only after controller selects a bounded patch.

## Goal

Align the AI conversation entry with the IKE flywheel mainline.

`/chat` must not remain just a generic chat surface. The product direction is that AI conversation becomes the entry into typed candidates, controller packets, and review-gated next actions.

This packet is an alignment/gap packet. It does not authorize broad chat redesign.

## Surfaces To Inspect

Backend:

- `services/api/routers/chat.py`
- `services/api/routers/conversation_runtime.py`
- `services/api/brains/control_plane.py`
- `services/api/conversation_runtime/p0.py`
- `services/api/conversation_runtime/contracts.py`

Frontend:

- `services/web/app/chat/page.tsx`
- `services/web/components/chat/chat-interface.tsx`
- `services/web/app/evolution/page.tsx`
- `services/web/components/evolution/flywheel-inspect-panel.tsx`

## Questions To Answer

1. What does `/chat` currently do?
2. Does `/chat` expose the brain route / control-plane decision clearly enough?
3. Is there a UI path from a chat turn to flywheel inspect?
4. Can a user intentionally convert a conversation segment into typed candidates or a controller packet?
5. Does the existing conversation runtime already provide the needed backend route?
6. What is the smallest implementation slice to make AI conversation an entry into the flywheel without turning raw chat into truth?

## Required Boundary

Raw conversation remains:

- non-canonical
- inspect-only unless explicitly reviewed
- not memory
- not runtime truth
- not automatically promoted

Any candidate objects or next actions must be review-gated.

## Candidate Next Patches

The audit should recommend one of:

1. UI-only entry bridge: add a visible action in `/chat` to send selected text to the existing flywheel inspect surface.
2. Backend alignment: add a narrow adapter route only if existing `conversation_runtime` routes cannot support the UI bridge.
3. Documentation/control-surface update only, if the capability already exists but is hidden.

Do not implement more than one without a new controller decision.

## Validation

Backend validation if backend files are touched:

```powershell
python -m pytest services/api/tests/test_conversation_runtime_route.py -q
python -m py_compile services/api/routers/chat.py services/api/routers/conversation_runtime.py services/api/conversation_runtime/p0.py
```

Frontend validation if frontend files are touched:

```powershell
cd services/web
npm run build
```

## Non-Goals

- no generic chat rewrite
- no new memory or persistence
- no automatic absorption
- no scheduler or worker execution changes
- no broad RAG/voting redesign
- no source-intelligence quality patch

## Expected Output

Return:

1. current `/chat` behavior
2. current flywheel entry behavior
3. gap summary
4. recommended smallest patch
5. files likely involved
6. validation needed
7. recommendation: `accept`, `accept_with_changes`, or `reject`

## Stop Conditions

Stop and report if:

- the route contract is unclear
- the UI requires backend data that does not exist
- the fix would imply raw chat becomes canonical truth
- the fix would require persistence or promotion semantics
