# IKE Visual Control Surface Branch Design 2026-04-29

## Purpose

This branch creates a visible control surface for IKE without blocking the active mainline.

The goal is not to finish backend intelligence. The goal is to make project state, phase progress, flywheel closure, and current capability understandable from UI before the full backend loop is complete.

Branch:

- `codex/ike-visual-control-surface`

Primary delegate:

- Antigravity / UI implementation lane

## Problem Statement

Current development is auditable through documents and review packets, but the user cannot see progress directly.

The project therefore feels like a black box:

- progress exists only in controller summaries
- phase/milestone state is buried in Markdown files
- evolution flywheel pieces exist but do not read as a closed loop
- UI is not showing the actual project blueprint, current capability, or degree of completion

This is now a product/governance gap, not a cosmetic UI issue.

## Design Principle

Build a UI-first control surface with adapter seams.

Rules:

- static/mock-first is allowed
- do not wait for backend endpoints
- do not fake backend execution
- clearly label mock/static state as `planned`, `manual`, `derived`, or `live`
- all components must later be connectable to backend data through typed adapters
- no mutation APIs in the first visual slice
- no automatic promotion or execution

## Product Shape

The UI should answer five questions immediately:

1. What is IKE trying to become?
2. What phase are we in?
3. What capabilities exist now?
4. Where is the evolution flywheel blocked or incomplete?
5. What is the next concrete action?

## Proposed Routes

### 1. `/control`

Primary visual control surface.

Sections:

- project phase map
- milestone progress
- current capability matrix
- evolution flywheel loop map
- active risks and blockers
- next action queue

This should become the first page a human opens to understand project state.

### 2. `/control/flywheel`

Focused flywheel visibility surface.

Sections:

- loop graph:
  - inspect
  - packet
  - delegate
  - review
  - absorption
  - decision
  - next task
- status per node:
  - `not_started`
  - `ready`
  - `running`
  - `blocked`
  - `accepted`
- latest artifacts
- manual action needed

### 3. `/control/source-intelligence`

Source Intelligence visibility surface.

Sections:

- current Source Intelligence phase
- person discovery hardening summary
- candidate-quality improvements
- known remaining risks
- next possible design packets

## Data Model For UI Adapter

Create a typed local data model first. Backend can later supply the same shape.

Suggested types:

```ts
export type ProgressStatus =
  | 'not_started'
  | 'planned'
  | 'in_progress'
  | 'blocked'
  | 'review_required'
  | 'accepted'
  | 'deferred'

export interface ProjectPhase {
  id: string
  title: string
  status: ProgressStatus
  percent: number
  summary: string
  visibleOutcome: string
  currentMilestone?: string
  risks: string[]
}

export interface CapabilityCard {
  id: string
  title: string
  status: ProgressStatus
  maturity: 'concept' | 'prototype' | 'usable' | 'hardened'
  proof: string
  limitation: string
}

export interface FlywheelNode {
  id: string
  title: string
  status: ProgressStatus
  evidence: string
  nextAction?: string
}

export interface MainlineSnapshot {
  generatedAt: string
  overallProgress: number
  currentPhase: string
  currentMilestone: string
  phases: ProjectPhase[]
  capabilities: CapabilityCard[]
  flywheel: FlywheelNode[]
  risks: string[]
  nextActions: string[]
}
```

## Initial Static Snapshot

Use this as the first static payload. Values are approximate controller estimates, not backend truth.

Phases:

1. `governance-runtime-substrate`
   - title: Governance + Runtime Substrate
   - status: `accepted`
   - percent: `75`
   - visible outcome: auditable delegation, review, validation, handoff
2. `source-intelligence-v1`
   - title: Source Intelligence V1
   - status: `in_progress`
   - percent: `55`
   - visible outcome: candidate discovery, person/signal hardening, advisory review surfaces
3. `evolution-flywheel-v0`
   - title: Evolution Flywheel V0
   - status: `in_progress`
   - percent: `45`
   - visible outcome: inspect, packet, manual review, absorption, decision bridges exist but loop is not visually closed
4. `visual-control-surface`
   - title: Visual Control Surface
   - status: `planned`
   - percent: `10`
   - visible outcome: this branch should make project progress understandable
5. `autonomous-iteration`
   - title: Autonomous Iteration
   - status: `not_started`
   - percent: `5`
   - visible outcome: future loop automation after UI and governance are stable

Capabilities:

- Source discovery candidates: `usable`
- Person discovery hardening: `usable`
- AI judgment advisory: `prototype`
- Flywheel inspect: `prototype`
- Manual review / absorption / decision bridge: `prototype`
- Closed evolution loop: `concept`
- Visual project governance dashboard: `planned`

Flywheel nodes:

- inspect: `accepted`
- task packet: `accepted`
- delegate: `in_progress`
- review: `accepted`
- absorption: `in_progress`
- decision: `prototype`
- next task: `blocked`

## Antigravity Implementation Packet

Task ID:

- `IKE_VISUAL_CONTROL_SURFACE_P0`

Goal:

- create a UI-visible project progress and flywheel control surface that can run with static data now and backend adapter later

Allowed files:

- `services/web/app/control/page.tsx`
- `services/web/app/control/flywheel/page.tsx`
- `services/web/app/control/source-intelligence/page.tsx`
- `services/web/components/control/*`
- `services/web/lib/control-surface/*`
- `services/web/components/ui/sidebar.tsx`

Non-goals:

- no backend API implementation
- no database schema
- no mutation actions
- no automatic execution
- no claim that progress percentages are canonical truth

Required UI:

- phase progress cards
- capability matrix
- flywheel loop visualization
- next action panel
- risk/blocker panel
- clear labels for `static estimate`, `manual`, `live`, `planned`

Acceptance Criteria:

- user can open `/control` and understand project stage within 30 seconds
- user can open `/control/flywheel` and see why the flywheel is not yet closed
- UI works without backend running
- implementation has typed adapter boundary
- sidebar exposes the new control route
- no existing evolution page behavior is broken

Validation:

```powershell
cd D:\code\MyAttention\services\web
npm run lint
npm run build
```

If lint/build scripts are unavailable or already broken, return the exact blocker and do not mask it.

Expected Result Format:

```text
summary:
files_changed:
ui_surfaces:
adapter_boundary:
validation_run:
known_risks:
recommendation: accept | accept_with_changes | reject
```

## Handoff To Backend Later

The first backend adapter can read:

- `CURRENT_MAINLINE_HANDOFF.md`
- milestone result docs
- `/api/evolution/*`
- future `/api/control-surface/snapshot`

But P0 must not depend on that endpoint.

## Controller Judgment

Recommendation: proceed in parallel.

This branch is allowed to move independently from the source-intelligence mainline because it is UI/static-adapter-first and does not change backend truth.
