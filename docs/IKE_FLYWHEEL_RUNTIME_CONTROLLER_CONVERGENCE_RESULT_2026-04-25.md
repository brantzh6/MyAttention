# IKE Flywheel Runtime Controller Convergence Result 2026-04-25

## Summary

This slice continues flywheel runtime state convergence without changing inspect-only semantics or adding new bridge behavior.

The main change is extracting runtime orchestration out of `flywheel-inspect-panel.tsx` into a bounded controller hook:

- inspect submit
- task preview request
- execution feedback inspect request
- review / absorption / decision / worker / feedback packet copy actions
- reducer-backed field updates and lane changes

The panel now acts more like a render surface and less like a mixed render + orchestration file.

## Files Changed

- `services/web/components/evolution/flywheel-inspect-panel.tsx`
- `services/web/components/evolution/use-flywheel-runtime-state.ts`
- `services/web/components/evolution/use-flywheel-runtime-controller.ts`

## Why This Solution

The current flywheel mainline is no longer blocked on first-path capability.
It is blocked on runtime readability and maintainability.

After section decomposition and phase-1 state convergence, the next structural debt was that the panel still owned too much async orchestration and packet-copy behavior.

Moving those bounded actions into a controller hook:

- keeps reducer state as the single runtime truth source
- reduces prop/event wiring pressure in the panel
- makes later work on AI entry and worker loop closure less likely to re-bloat the UI component
- preserves the existing manual review / absorption / decision / worker / feedback flow

## Validation Run

```powershell
cd D:\code\MyAttention\services\web
npm run build
```

Result:

- success

```powershell
cd D:\code\MyAttention
python -m unittest services.api.tests.test_conversation_runtime_route services.api.tests.test_flywheel_inspect_route
```

Result:

- `36` tests passed

## Known Risks

- This slice does not yet unify all flywheel presentational sections under a single runtime controller contract; the panel still renders a large amount of manual bridge UI inline.
- `CollapsibleSection` still uses local expansion state plus forced-open hints; that behavior was preserved intentionally and was not normalized in this slice.
- This is still a manual AI-assisted loop surface, not a durable autonomous runtime loop.

## Recommendation

`accept`
