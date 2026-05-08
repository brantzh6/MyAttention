# AI Conversation Entry Bridge Result

Date: 2026-05-07

Task ID: AI_CONVERSATION_ENTRY_BRIDGE_P0_2026-05-07

Source alignment result: `tasks/codex/ai_conversation_entry_alignment_result_2026-05-07.md`

Recommendation: accept_with_changes

## Summary

Implemented a narrow UI-only bridge from `/chat` to the existing `/evolution` flywheel inspect panel.

The bridge lets a user intentionally send a chat message or assistant turn into the flywheel inspect surface as transient input. It does not submit the inspect request automatically and does not change backend runtime truth.

## Files Changed

- `services/web/lib/flywheel-handoff.ts`
- `services/web/components/chat/chat-interface.tsx`
- `services/web/components/evolution/flywheel-inspect-panel.tsx`
- `services/web/components/evolution/use-flywheel-runtime-controller.ts`
- `tasks/codex/ai_conversation_entry_bridge_result_2026-05-07.md`

## Why This Solution

The existing backend `conversation_runtime` routes already support inspect-only flywheel input. Adding a backend adapter first would expand the contract before the UI need is proven.

This patch uses browser `sessionStorage` as a transient handoff buffer and `/evolution?handoff=chat` as the visible route signal. The evolution panel reads the handoff once, removes it from browser storage, pre-fills the inspect form, and shows a non-canonical boundary notice.

## Boundaries Preserved

- Raw chat remains non-canonical.
- No memory write.
- No persistence change.
- No scheduler change.
- No worker execution change.
- No promotion semantics change.
- No automatic inspect submission.
- No backend route change.

## Validation Run

```powershell
cd services/web
npm run build
```

Result:

```text
passed
```

Attempted:

```powershell
cd services/web
npm run lint
```

Result:

```text
not usable yet; Next.js entered interactive ESLint configuration because the project has no committed ESLint setup.
```

## Review Absorption

GitHub/Codex review on PR #10 raised one P2 finding:

```text
Handle sessionStorage failures during handoff.
```

Absorption:

- accepted
- wrapped `sessionStorage.setItem` in `try/catch`
- added a visible handoff failure message in the chat UI
- kept the fallback non-persistent and did not add a backend adapter

Validation after absorption:

```powershell
cd services/web
npm run build
```

Result:

```text
passed
```

## Known Risks

- Browser `sessionStorage` is transient and tab-local. That is intentional for V1, but it is not a durable handoff.
- Query-string plus storage handoff can produce an empty `/evolution?handoff=chat` state if the user opens the URL without the originating chat action.
- The UI labels the boundary, but browser-level smoke is still needed before promotion.

## Follow-Up

Run browser-level smoke for:

```text
/chat message action -> /evolution prefilled flywheel input -> manual flywheel inspect succeeds
```

Only after that smoke should the Flywheel V1 task be marked beyond `partial`.
