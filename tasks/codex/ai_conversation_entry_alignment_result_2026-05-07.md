# AI Conversation Entry Alignment Result

Date: 2026-05-07

Task ID: AI_CONVERSATION_ENTRY_ALIGNMENT_P0_2026-05-06

Result type: controller audit result

Recommendation: accept_with_changes

## Summary

`/chat` is currently a capable AI interaction surface, but it is not yet positioned as the entry into the IKE evolution flywheel.

The backend already has the narrow inspect-only runtime routes needed for the first bridge. A new backend adapter is not justified yet. The smallest implementation slice is a UI-only handoff from `/chat` to the existing `/evolution` flywheel inspect panel, with explicit non-canonical labeling.

## Current Chat Behavior

`/chat` calls `/api/chat`, streams assistant output, and displays conversation context including brain-plan, voting, and source evidence. It remains primarily a knowledge-brain chat surface.

Relevant files:

- `services/api/routers/chat.py`
- `services/web/app/chat/page.tsx`
- `services/web/components/chat/chat-interface.tsx`

## Current Flywheel Entry Behavior

The current flywheel entry starts from the evolution UI, not from chat.

Relevant files:

- `services/api/routers/conversation_runtime.py`
- `services/web/app/evolution/page.tsx`
- `services/web/components/evolution/flywheel-inspect-panel.tsx`
- `services/web/components/evolution/use-flywheel-runtime-controller.ts`

The evolution UI can inspect candidate input, produce controller packets, preview worker task packets, and inspect execution feedback. It does not currently receive a selected chat turn as first-class input.

## Gap Summary

- `/chat` does not expose a visible "send to flywheel" or equivalent action.
- A user cannot intentionally convert a conversation segment into typed candidates from the chat surface.
- Brain-plan evidence is visible in chat, but it is not connected to the flywheel inspect workflow.
- The route contract needed for inspect-only handoff already exists, so backend expansion would be premature.

## Recommended Smallest Patch

Implement candidate patch 1 from the task packet:

```text
UI-only entry bridge from /chat to the existing flywheel inspect surface.
```

Suggested implementation boundary:

- Add an action on a chat message, selected conversation excerpt, or current user turn: "Open in Flywheel" or equivalent.
- Carry only transient text plus minimal provenance into `/evolution`.
- Prefill the existing flywheel inspect input without submitting automatically.
- Show that the imported text is non-canonical, inspect-only, and controller-curated.
- Require the user/controller to explicitly run flywheel inspect.

Do not add a backend route unless the UI cannot safely pass transient handoff state to `/evolution`.

## Files Likely Involved

- `services/web/components/chat/chat-interface.tsx`
- `services/web/components/evolution/flywheel-inspect-panel.tsx`
- `services/web/components/evolution/use-flywheel-runtime-state.ts`
- Optional narrow helper under `services/web/lib/` if the bridge needs a typed transient handoff parser.

Backend files should not be touched for the first patch unless implementation proves the current route contract insufficient.

## Validation Needed For The Patch

If only frontend files are touched:

```powershell
cd services/web
npm run build
```

Preferred if available:

```powershell
cd services/web
npm run lint
```

After implementation, add or run a browser-level smoke for:

```text
/chat message action -> /evolution prefilled flywheel input -> manual inspect succeeds
```

## Boundary Requirements

- Raw chat remains non-canonical.
- The bridge must not write memory.
- The bridge must not create runtime truth.
- The bridge must not auto-promote candidates.
- The bridge must not start worker execution.
- The bridge must not change scheduler or persistence behavior.

## Known Risks

- A convenience handoff can be mistaken for promotion unless the UI states the provenance boundary clearly.
- Browser storage or query-string handoff can leak stale input if not cleared or visibly labeled.
- Adding an over-broad bridge would blur the distinction between chat output, controller evidence, and accepted project truth.
