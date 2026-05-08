# Flywheel V1 Browser Smoke P0

Date: 2026-05-08

Task ID: FLYWHEEL_V1_BROWSER_SMOKE_P0_2026-05-08

Owner: controller scopes and accepts; test execution may be delegated to CC/test runner after PR #10 is promoted or checked out.

## Goal

Prove the first inspect-only product loop can be driven through the browser after the AI conversation entry bridge lands.

This is a smoke validation packet, not a feature packet.

## Prerequisites

- PR #10 is merged, or the tester has checked out `codex/ai-entry-flywheel-bridge-20260507`.
- Web app can start locally.
- API app can start locally, or the smoke is limited to bridge prefill and records the backend startup blocker.

## Target Path

```text
/chat
  -> send or load a chat turn
  -> click Open in Flywheel
  -> /evolution?handoff=chat
  -> flywheel inspect form is prefilled
  -> user manually submits inspect
  -> inspect result renders
  -> task packet preview can be requested
  -> execution feedback inspect surface remains available
```

## Required Checks

1. `/chat` renders.
2. A visible `Open in Flywheel` action exists on non-empty chat messages.
3. Clicking the action navigates to `/evolution?handoff=chat`.
4. The flywheel inspect form is prefilled with transient chat text.
5. The evolution panel shows a non-canonical / inspect-only handoff notice.
6. The inspect request is not submitted automatically.
7. Manual inspect succeeds when backend is available.
8. Task packet preview can be requested from the inspect result.
9. Execution feedback inspect UI is present after task preview.
10. No memory, persistence, scheduler, worker execution, or promotion action is triggered by the smoke.

## Validation Commands

Frontend build:

```powershell
cd services/web
npm run build
```

Backend route tests:

```powershell
python -m pytest services/api/tests/test_flywheel_inspect_route.py services/api/tests/test_conversation_runtime_route.py -q
```

Manual or automated browser smoke:

```text
Record browser, viewport, branch/commit, steps executed, pass/fail by required check, screenshots if available, and blockers.
```

## Expected Output

Return:

1. `summary`
2. `environment`
3. `commit_tested`
4. `checks`
5. `validation_run`
6. `screenshots_or_evidence`
7. `known_risks`
8. `recommendation`: `accept`, `accept_with_changes`, or `reject`

## Stop Conditions

Stop and report if:

- PR #10 has unresolved actionable review feedback
- the backend cannot start and the smoke requires manual inspect
- the browser cannot execute client-side navigation
- the UI implies raw chat became canonical truth
- any smoke step would require memory/persistence/promotion changes
