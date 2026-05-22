# IKE Runtime v0 - R2-I18 Minimal Write Set

Date: 2026-04-11
Phase: `R2-I18 Controller Acceptance Record Boundary`
Status: `implementation boundary`

## Purpose

Fix the smallest credible file set for `R2-I18` so implementation does not
drift into a broad runtime refactor.

## Preferred Write Set

### 1. New Runtime Helper

Proposed new file:

- `services/api/runtime/controller_acceptance.py`

Responsibility:

- inspect latest acceptance record for scope
  `canonical_service_acceptance`
- record a new acceptance decision when eligible
- enforce idempotent reuse / explicit supersession rules
- append one runtime event
- update/alignment hook for work-context latest decision pointer

Why new file:

- keeps `service_preflight.py` read/diagnosis focused
- keeps router logic thin
- avoids stuffing write semantics into inspect helpers

### 2. Router Surface

Existing file:

- `services/api/routers/ike_v0.py`

Responsibility:

- add the two bounded routes:
  - inspect current acceptance record
  - record controller acceptance
- preserve explicit truth-boundary flags

### 3. Work-Context / Read-Surface Alignment

Likely reuse, minimal edit only if required:

- `services/api/runtime/operational_closure.py`
  or
- `services/api/runtime/project_surface.py`

Responsibility:

- reflect `latest_decision_id` truthfully after record path succeeds

Rule:

- prefer reuse of existing context reconstruction/alignment helpers
- do not create a separate acceptance-summary store

### 4. Tests

Most likely touched files:

- `services/api/tests/test_routers_ike_v0.py`
- `services/api/tests/test_runtime_v0_project_surface.py`
- optional new focused file:
  - `services/api/tests/test_runtime_v0_controller_acceptance.py`

Responsibility:

- inspect route is read-only
- record route writes only when eligible
- repeated same-basis confirm is idempotent
- changed eligible basis supersedes explicitly
- latest decision is visible on read surface after alignment

## Preferred Non-Write Areas

Do **not** widen into:

- `services/web/*`
- scheduler code
- watchdog code
- benchmark bridge code
- broad state-machine transitions

## Recommended First Implementation Order

1. helper
2. helper tests
3. router surface
4. router tests
5. project-surface alignment proof

## Recommendation

If implementation touches materially more than these areas, treat that as a
scope-drift warning and re-evaluate before continuing.
