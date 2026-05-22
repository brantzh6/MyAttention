# AI Entry Useful Packet Selection Result

Date: 2026-05-18
Lane: controller / AI conversation entry
SDLC stage: Design result
Risk: R2
Truth status: non-canonical controller selection

## selected_packet_title

AI Entry Task Packet Composer P0

## selected_packet_goal

Make the AI conversation entry produce a useful, controller-visible task packet
candidate from chat context, then route that candidate into the accepted
Flywheel preview/handoff/feedback loop without automatic execution or
promotion.

## why_this_is_next

The previous mainline gate proved the loop mechanics:

```text
copy-ready handoff packet -> real worker result -> execution-feedback inspect -> review -> absorption
```

The remaining product gap is not another infrastructure proof. It is user value:
from the AI conversation entry, the controller should be able to turn a useful
chat intent into the next bounded packet candidate and carry it through the
reviewed loop.

This keeps the mainline aligned:

1. Evolution Flywheel V1 remains the product loop.
2. AI conversation becomes the entry into typed candidates and controller
   packets.
3. `/control` can display a concrete current phase instead of abstract
   readiness.

## scoped_file_candidates

Implementation should be scoped to one AI-entry/Flywheel UI slice.

Candidate files:

- `services/web/components/chat/chat-interface.tsx`
- `services/web/components/evolution/flywheel-inspect-panel.tsx`
- `services/web/components/evolution/task-preview-section.tsx`
- `services/web/components/evolution/worker-packet-bridge-section.tsx`
- `services/web/components/evolution/use-flywheel-runtime-state.ts`
- `services/web/components/evolution/use-flywheel-runtime-controller.ts`
- `services/web/lib/api-client.ts`
- `services/web/lib/flywheel-handoff.ts`
- `scripts/smoke/ai_entry_typed_handoff_preview_smoke.mjs`
- `services/web/package.json` only if a validation command must be added or
  corrected

Do not touch backend contracts unless the frontend cannot express the packet
with existing API fields.

## expected_behavior

Minimum product behavior:

1. A chat-originated context can be turned into a visible task packet composer
   state.
2. The composer shows the selected chat-origin provenance as non-canonical.
3. The controller can preview a candidate packet before delegation.
4. The controller can copy a handoff packet.
5. The UI makes the next step explicit:
   - dispatch manually
   - paste worker result into execution-feedback inspect
   - review before absorption
6. No automatic execution or persistence is introduced.

## validation_commands

Required:

```text
npm run build
npm run smoke:flywheel-loop:check
```

If the implementation changes chat-origin behavior, also run:

```text
node scripts/smoke/ai_entry_typed_handoff_preview_smoke.mjs
```

Runtime truth must be recorded separately if live routes are used:

```text
python manage.py health --json
```

## review_gate

Default gate:

```text
implementation result -> local L1 review -> controller absorption
```

GitHub/Codex review is not required until this becomes a promotion-ready GitHub
PR or the user explicitly requests cloud review.

## dirty_tree_handling_plan

Do not start implementation until a scoped package decision is made for the
current dirty tree.

Immediate containment:

1. Treat current worktree as over budget.
2. Do not add another implementation diff on top of the shared dirty tree.
3. First prepare the Flywheel readiness scoped package file list from the
   accepted artifacts.
4. Only then dispatch this AI Entry Task Packet Composer implementation on a
   scoped file set.

If urgent implementation is required before cleanup, create a separate scoped
branch/worktree or explicitly name the exact files that are allowed to change
and verify they do not overlap unrelated dirty groups.

## known_risks

- Current dirty tree may already include modifications in the same frontend
  files that this next packet would need. Starting implementation now would
  make review attribution worse.
- The task may be tempting to expand into generic chat redesign. That is out
  of scope.
- Runtime LLM latency was observed during execution-feedback inspect with long
  worker artifacts. This packet should keep feedback payloads concise and
  artifact-referenced.

## recommendation

`accept_with_changes`

Accept this as the next mainline direction, but do not dispatch implementation
until dirty-tree containment has produced an accepted scoped package boundary.

## stop_condition

Stop after local review of this selection. Do not implement the selected packet
inside this task.
