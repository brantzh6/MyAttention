# IKE Flywheel Runtime State Convergence Result

**Date:** 2026-04-25
**Status:** Implementation complete for phase 1

## Summary

Implemented the first state-convergence slice for the flywheel runtime surface.

The main change is that `flywheel-inspect-panel.tsx` no longer manually resets a large number of independent `useState` values when starting a new inspect / preview / execution-feedback cycle.

Instead, flywheel runtime state now flows through a dedicated reducer-backed hook:

- `services/web/components/evolution/use-flywheel-runtime-state.ts`

This provides atomic reset behavior for the lower half of the manual flywheel loop and reduces the risk of stale preview / feedback / provenance data leaking into the next run.

## Files Changed

| File | Change |
|---|---|
| `services/web/components/evolution/use-flywheel-runtime-state.ts` | New reducer-backed runtime state hook for the flywheel UI. |
| `services/web/components/evolution/flywheel-inspect-panel.tsx` | Switched major runtime state lifecycle from scattered `useState` resets to reducer dispatch. |

## What Converged

- `startInspect` now atomically resets:
  - selections
  - review note
  - task-preview state
  - execution-feedback state
  - caller-provided provenance fields
  - worker copy state
- `startTaskPreview` / `taskPreviewSuccess` / `taskPreviewError` now go through reducer transitions
- `startExecutionFeedback` / `executionFeedbackSuccess` / `executionFeedbackError` now go through reducer transitions
- copy flag toggles now go through reducer transitions
- selection toggles and section toggles now go through reducer transitions

## Semantics Preserved

No intended changes to:

- flywheel inspect behavior
- task-preview request semantics
- worker packet content
- execution-feedback inspect behavior
- inspect-only / non-canonical boundaries
- caller-provided provenance semantics

## Validation Run

```text
python -m unittest services.api.tests.test_conversation_runtime_route services.api.tests.test_flywheel_inspect_route
36 tests OK

npm run build
success
```

## Known Risks

1. `flywheel-inspect-panel.tsx` still owns orchestration and still dispatches many field-level updates.
2. Upstream manual review / absorption / decision surfaces are still inline and not yet state-sliced.
3. Prop drilling across section components is reduced in lifecycle risk but not yet fully collapsed into bounded state adapters.

## Recommendation

`accept_with_changes`

Accept this as state convergence phase 1. The next step should decide whether to keep the current reducer as a local panel mechanism or push one level further into bounded hooks / action adapters for the extracted sections.
