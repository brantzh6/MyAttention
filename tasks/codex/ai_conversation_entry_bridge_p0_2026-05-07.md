# AI Conversation Entry Bridge P0

Date: 2026-05-07

Task ID: AI_CONVERSATION_ENTRY_BRIDGE_P0_2026-05-07

Owner: controller scopes and accepts; frontend implementation may be done by controller only as a bounded corrective slice or delegated to frontend/CC.

## Goal

Add the smallest visible bridge from `/chat` into the existing `/evolution` flywheel inspect surface.

The bridge should let a user intentionally send a chat turn into flywheel inspection as transient input. It must not make raw chat canonical truth.

## Source Evidence

- `tasks/codex/ai_conversation_entry_alignment_p0_2026-05-06.md`
- `tasks/codex/ai_conversation_entry_alignment_result_2026-05-07.md`
- `tasks/codex/flywheel_v1_e2e_gap_audit_result_2026-05-07.md`

## Allowed Files

- `services/web/components/chat/chat-interface.tsx`
- `services/web/components/evolution/flywheel-inspect-panel.tsx`
- `services/web/components/evolution/use-flywheel-runtime-state.ts`
- `services/web/components/evolution/use-flywheel-runtime-controller.ts`
- narrow helper under `services/web/lib/*`
- direct task/result/review artifacts for this bridge only

Backend files are not allowed unless implementation proves the current runtime routes cannot support a transient UI handoff.

## Required Behavior

1. Add a visible action from `/chat` to open a selected chat message or turn in the flywheel workflow.
2. Carry only transient text plus minimal provenance.
3. Prefill the existing flywheel inspect form.
4. Do not submit the inspect request automatically.
5. Make the non-canonical boundary visible.
6. Keep the handoff inspect-only and controller-curated.

## Boundaries

- no memory write
- no persistence change
- no scheduler change
- no worker execution change
- no promotion semantics change
- no raw chat as runtime truth
- no automatic absorption
- no new backend adapter unless separately justified

## Validation

Required if frontend files are touched:

```powershell
cd services/web
npm run build
```

Preferred if available:

```powershell
cd services/web
npm run lint
```

Browser-level smoke before promotion:

```text
/chat message action -> /evolution prefilled flywheel input -> manual inspect succeeds
```

## Expected Output

Return:

1. `summary`
2. `files_changed`
3. `why_this_solution`
4. `validation_run`
5. `known_risks`
6. `recommendation`: `accept`, `accept_with_changes`, or `reject`

## Stop Conditions

Stop and report if:

- the bridge requires backend route changes
- the UI would imply raw chat is canonical truth
- persistence or memory is required
- browser storage cannot be used safely without a visible fallback
- validation cannot run
