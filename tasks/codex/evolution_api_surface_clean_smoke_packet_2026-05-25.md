# Coding Packet: Evolution API Surface Clean Smoke

Date: 2026-05-25
Controller: Codex
Owner lane: coding_delegate
Worktree: `D:\code\_worktrees\MyAttention-evolution-api-surface-clean-smoke`
Risk: R2 API surface/runtime smoke

## Objective

Remove the remaining browser smoke console 404s by adding the minimal read-only
API surface that the evolution dashboard already calls:

- `GET /api/evolution/contexts`
- `GET /api/evolution/contexts/{context_id}`
- `GET /api/evolution/memories/task`
- `GET /api/evolution/memories/procedural`

The first usable inspect-only flywheel loop is already working on main. This
task only makes the evolution page API surface honest enough for clean product
smoke.

## Allowed Files

- `services/api/routers/evolution.py`
- `services/api/tests/test_evolution_api_surface.py`

## Non-Goals

- Do not implement persistence semantics.
- Do not invent canonical memory truth.
- Do not change frontend code.
- Do not change scheduler, worker, promotion, or flywheel inspect semantics.
- Do not add dependencies.

## Acceptance Criteria

- The four routes return valid JSON and list endpoints do not 404.
- Detail route behavior is deterministic.
- Existing routes remain unchanged.
- Tests cover all new routes.
- Newly added lines are ASCII-clean where practical.

## Required Validation

```powershell
python -m py_compile services/api/routers/evolution.py services/api/tests/test_evolution_api_surface.py
python -m pytest services/api/tests/test_evolution_api_surface.py -q
git diff --check
```

