# IKE Runtime v0 R2-C1 Result Milestone

Date: 2026-04-08
Phase: `R2-C1`
Title: `Runtime-backed visible surface narrow proof`
Status: `accept_with_changes`

## What Landed

`R2-C1` adds a narrow runtime-backed visible surface proof without widening into
generic UI/runtime integration.

Delivered pieces:

- runtime helper:
  - [D:\code\MyAttention\services\api\runtime\project_surface.py](/D:/code/MyAttention/services/api/runtime/project_surface.py)
- API read surface:
  - [D:\code\MyAttention\services\api\routers\ike_v0.py](/D:/code/MyAttention/services/api/routers/ike_v0.py)
- settings page integration:
  - [D:\code\MyAttention\services\web\app\settings\ike\page.tsx](/D:/code/MyAttention/services/web/app/settings/ike/page.tsx)
  - [D:\code\MyAttention\services\web\components\settings\ike-workspace-manager.tsx](/D:/code/MyAttention/services/web/components/settings/ike-workspace-manager.tsx)

The visible surface now reads a narrow runtime-backed project/work summary and
shows a truthful unavailable state when runtime project truth is absent.

## Truthful Scope

This phase proves:

- runtime truth can feed one visible project/work surface
- benchmark/story surface and runtime surface can coexist without pretending to
  be one merged knowledge layer
- reviewed benchmark imports still remain bounded by runtime trust gates

This phase does **not** prove:

- broad UI/runtime integration
- generic knowledge-base/runtime unification
- trusted benchmark-to-memory promotion
- notification or graph-memory expansion

## Validation

- targeted runtime-visible slice:
  - `34 passed, 28 warnings, 9 subtests passed`
- combined DB-backed slice:
  - `89 passed, 1 warning`
- frontend compile:
  - `npx tsc --noEmit`
- live API route:
  - `POST /api/ike/v0/runtime/project-surface/inspect`
  - truthful `404` when no runtime project exists

## Narrow Fix Included

While stabilizing `R2-C1`, one existing DB-backed helper drift was corrected:

- [D:\code\MyAttention\services\api\tests\test_runtime_v0_operational_closure.py](/D:/code/MyAttention/services/api/tests/test_runtime_v0_operational_closure.py)

`_make_project(...)` now round-trips the persisted runtime project row before
reuse, aligning it with the newer DB-backed runtime test helpers.

## Known Follow-up

- `R2-C2 / R2-C3 / R2-C4` still need durable review/testing/evolution closure
- visible surface is still narrow and controller/settings scoped
- live runtime panel may truthfully show unavailable until a runtime project is
  actually present in the active DB

## Controller Judgment

`R2-C1` is accepted with changes because the narrow proof is now real and
validated, but the broader `R2-C` phase is still open until review/testing/
evolution lanes are durably closed.
