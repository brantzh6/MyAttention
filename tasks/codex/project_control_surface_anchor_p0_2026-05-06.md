# Project Control Surface Anchor P0

Date: 2026-05-06

Task ID: PROJECT_CONTROL_SURFACE_ANCHOR_P0_2026-05-06

Owner: controller scopes and accepts; Antigravity/UI delegate implements; backend/CC assists only if a static data adapter or build/test fix is needed.

## Purpose

Make IKE's current target impossible to lose again.

The UI must show the current mainline, phase, core goals, capability maturity, capability gaps, active lanes, owners, and review gates. This is operations infrastructure, not cosmetic UI.

## Corrected Mainline

The current mainline has three first-class tasks:

1. `evolution_flywheel_v1`: first usable inspect-only AI-assisted evolution loop.
2. `ai_conversation_entry`: AI conversation as the entry into typed candidates, controller packets, and review-gated next actions.
3. `project_control_surface`: visible project/progress/capability anchor for controller, user, and delegates.

`source_intelligence` is a support lane for flywheel input quality. It is not the top-level mainline.

## Required UI Content

The control surface must display:

- current mainline name: `flywheel_v1_ai_entry_control_surface`
- three mainline tasks and their current state
- current phase and next gate
- active lanes and owners:
  - controller
  - Antigravity UI
  - backend/CC
  - code review
  - test execution
  - GitHub/Codex review gate
- capability maturity / gap model:
  - information brain
  - knowledge brain
  - evolution brain
  - world model
  - thinking methods / method arsenal
- latest accepted support evidence:
  - PR #2 merged at `acf922c`
  - source-intelligence GitHub signal relation hints are support evidence
- next actions:
  - recover or recreate control-surface UI on a clean GitHub branch
  - run UI build
  - open bounded PR
  - trigger GitHub/Codex review
  - controller absorbs findings and decides promotion

## Allowed Files

Preferred UI files:

- `services/web/app/control/*`
- `services/web/components/control/*`
- `services/web/lib/control-surface/*`

Allowed support docs:

- `tasks/codex/project_control_surface_anchor_p0_2026-05-06.md`
- `docs/CURRENT_OPERATIONS.md`
- `docs/CURRENT_MAINLINE_CONTROL_2026-05-02.md`
- `docs/CURRENT_ACTIVE_ARTIFACTS.md`
- future bounded review/absorption artifacts under `docs/reviews/active/` and `docs/reviews/absorbed/`

## Non-Goals

- Do not change backend runtime truth.
- Do not add scheduler, persistence, memory, promotion, or worker execution semantics.
- Do not present static estimates as live truth.
- Do not broaden into general dashboard redesign.
- Do not rely on unpublished local quarantine refs. Recreate or recover the UI through a clean, reviewable branch.

## Static Truth Boundary

The first UI may use a static snapshot, but it must visibly state:

- snapshot source
- last reviewed or generated label
- provenance status
- whether each score is estimated, accepted, blocked, or unknown

Static data is allowed only as a project-control aid. It is not runtime truth.

## Collaboration Protocol

Implementation must use GitHub:

1. create a clean branch from the current post-PR #2 mainline that contains `acf922c`
2. restore or recreate only the allowed UI files
3. commit this task packet with the implementation
4. open a bounded PR
5. include validation results in the PR body
6. trigger GitHub/Codex review
7. controller absorbs review findings before promotion

Antigravity should work through the PR branch and review comments, not through manual chat-only handoff.

## Validation

Required:

```powershell
cd services/web
npm run build
```

Preferred if feasible:

```powershell
cd services/web
npm run lint
```

Manual/controller validation:

- UI shows all three mainline tasks.
- UI shows capability maturity and gaps.
- UI makes static/provenance boundary visible.
- UI does not imply backend truth or automatic promotion.
- PR diff stays inside the allowed lane.

## Stop Conditions

Stop and report if:

- UI requires backend fields that do not exist
- implementation needs files outside the allowed scope
- Antigravity output changes runtime truth or scheduler/persistence behavior
- build cannot run
- PR includes unrelated historical artifacts or depends on unpublished quarantine refs

## Recommendation

Implement next as the highest-priority UI/control-surface slice before opening another source-intelligence support slice.
