# Project Control Surface Anchor P0 Result

Date: 2026-05-08

Task ID: PROJECT_CONTROL_SURFACE_ANCHOR_P0_2026-05-06

Recommendation: accept_with_changes

## Summary

Implemented the first `/control` project control surface anchor.

The page shows the current IKE mainline, product objective, three first-class tasks, phase/gate, capability maturity/gaps, active lanes/owners, review/operations state, and next actions.

The surface is explicitly static and non-canonical. It does not call backend runtime APIs and does not imply live truth.

## Files Changed

- `services/web/app/control/layout.tsx`
- `services/web/app/control/page.tsx`
- `services/web/components/control/provenance-block.tsx`
- `services/web/components/ui/sidebar.tsx`
- `services/web/lib/control-surface/get-snapshot.ts`
- `services/web/lib/control-surface/static-snapshot.ts`
- `services/web/lib/control-surface/types.ts`

## Why This Solution

The mainline needs a visible anchor now, not a live truth backend. A static controller-curated snapshot is enough for Anchor P0 and avoids creating fake runtime truth.

The implementation keeps the data shape typed and isolated under `services/web/lib/control-surface/*`, so a future backend adapter can replace `getSnapshot()` without rewriting the UI.

## Validation Run

```powershell
cd services/web
npm run build
```

Result:

```text
passed
```

## Local Review

Local Claude Code L1 review was run against the UI diff.

Result:

```text
No blocking issues found.
```

Reviewer notes:

- provenance boundary is explicit
- no live backend implication
- scope stays within allowed UI files
- responsive layout is acceptable
- hardcoded freshness date is a non-blocking static Anchor P0 risk

One reviewer note about placeholder sidebar labels was rejected as an encoding/read artifact; the local source contains Chinese labels.

## Known Risks

- Snapshot freshness is manual.
- Capability maturity is estimated and controller-curated.
- The UI is not yet connected to live project state.
- Visual/browser QA beyond build has not yet been completed.

## Follow-Up

- Run browser visual smoke for `/control`.
- Update snapshot after PR #10 and Flywheel V1 browser smoke promotion.
- Replace static snapshot only after a separate live adapter packet exists.
