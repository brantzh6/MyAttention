# Antigravity Brief: Project Control Surface Anchor P0

Date: 2026-05-06

Task ID: PROJECT_CONTROL_SURFACE_ANTIGRAVITY_BRIEF_2026-05-06

Delegate: Antigravity UI implementation.

Controller: Codex/controller owns scope, review absorption, and promotion decision.

## Goal

Implement the first visible IKE project control surface so the user, controller, and delegates can keep the same target without relying on chat memory or scattered historical docs.

This is a UI/control-surface task, not a backend truth task.

## Base

Create the implementation branch from the updated mainline after this task-packet PR is merged.

Do not depend on unpublished local quarantine refs. Prior UI evidence may be useful if locally available, but the PR must be reviewable from GitHub alone.

## Required Surface

Build or recover a `/control` surface that shows:

1. Mainline
   - active mainline: `flywheel_v1_ai_entry_control_surface`
   - product objective: first usable IKE evolution loop with AI conversation entry and visible project control
   - latest accepted support evidence: PR #2 `acf922c`, PR #4 `29d0443`

2. Three first-class tasks
   - `evolution_flywheel_v1`
   - `ai_conversation_entry`
   - `project_control_surface`

3. Capability maturity and gaps
   - information brain
   - knowledge brain
   - evolution brain
   - world model
   - thinking methods / method arsenal

4. Active lanes and owners
   - controller
   - Antigravity UI
   - backend/CC
   - code review
   - test execution
   - GitHub/Codex review gate

5. Review and operations state
   - PR review gate is evidence, not promotion authority
   - controller owns promotion
   - review gates terminate when findings are absorbed and no unresolved thread remains
   - no standing review monitor unless a review is actively pending

## Allowed Files

- `services/web/app/control/*`
- `services/web/components/control/*`
- `services/web/lib/control-surface/*`
- this brief and direct control-surface task/result/review artifacts

If implementation requires files outside this list, stop and report.

## Static Snapshot Rules

The first implementation may use static data only if it is visibly marked:

- source: controller-curated static snapshot
- provenance: static / non-canonical
- last reviewed label
- each score status: estimated, accepted, blocked, or unknown

Do not present static estimates as runtime truth.

## Non-Goals

- no backend runtime truth changes
- no scheduler, persistence, memory, worker execution, or promotion semantics
- no broad dashboard redesign
- no fake live status
- no source-intelligence behavior changes
- no evolution flywheel route changes
- no generic chat UI redesign

## Validation

Required:

```powershell
cd services/web
npm run build
```

Preferred if available:

```powershell
cd services/web
npm run lint
```

Controller visual validation:

- `/control` is directly usable as the project anchor.
- The first viewport makes the three mainline tasks visible.
- Capability scores/gaps are visible without reading historical docs.
- Static/provenance boundary is explicit.
- Text does not overflow or overlap on desktop and mobile.

## Expected Result Format

Return:

1. `summary`
2. `files_changed`
3. `why_this_solution`
4. `validation_run`
5. `known_risks`
6. `recommendation`: `accept`, `accept_with_changes`, or `reject`

## Stop Conditions

Stop and report if:

- build cannot run
- required source data is unavailable
- implementation needs backend fields that do not exist
- scope expands outside allowed files
- UI would imply live runtime truth
- PR diff contains unrelated historical artifacts
