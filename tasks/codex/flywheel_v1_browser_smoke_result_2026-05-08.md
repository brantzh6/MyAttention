# Flywheel V1 Browser Smoke Result

Date: 2026-05-08

Task ID: FLYWHEEL_V1_BROWSER_SMOKE_P0_2026-05-08

Recommendation: accept_with_changes

## Summary

The first Flywheel V1 smoke is partially closed with automated evidence.

Confirmed:

- `/chat` renders.
- `/evolution` renders.
- `/control` renders.
- backend flywheel inspect succeeds with deterministic test input.
- task packet preview succeeds from selected inspect candidates.
- execution feedback inspect succeeds from the task packet preview summary.
- all inspected artifacts remain `inspect_only` / non-canonical.

Not yet confirmed:

- real browser click from a visible chat message's `Open in Flywheel` action into `/evolution?handoff=chat`.

## Environment

- Branch: `codex/pre-ike-restructure-2026-04-09`
- Commit tested: `4bf4e82`
- Web dev server: `http://localhost:3100`
- Backend chain validation: FastAPI `TestClient`
- Browser automation: not available in the current environment without adding a new dependency

## Checks

| Check | Status | Evidence |
| --- | --- | --- |
| `/chat` renders | passed | HTTP 200, length 17059 |
| `/evolution` renders | passed | HTTP 200, length 14242 |
| `/control` renders | passed | HTTP 200, length 45832 |
| flywheel inspect route | passed | `segment_intent=flywheel_signal` |
| task packet preview route | passed | `packet_intent=mixed` |
| execution feedback inspect route | passed | `feedback_intent=execution_feedback` |
| inspect-only boundary | passed | responses asserted `promotion_state=inspect_only` |
| non-canonical boundary | passed | controller packets asserted non-canonical / explicit non-canonical |
| real chat button click | partial | route renders, but browser click automation unavailable |

## Validation Run

Backend route tests:

```powershell
python -m pytest services/api/tests/test_flywheel_inspect_route.py services/api/tests/test_conversation_runtime_route.py -q
```

Result:

```text
37 passed, 3 warnings in 0.65s
```

Frontend route smoke:

```powershell
Invoke-WebRequest http://localhost:3100/chat
Invoke-WebRequest http://localhost:3100/evolution
Invoke-WebRequest http://localhost:3100/control
```

Result:

```text
/chat status=200 length=17059
/evolution status=200 length=14242
/control status=200 length=45832
```

Backend chain smoke:

```text
POST /api/conversation-runtime/flywheel/inspect
POST /api/conversation-runtime/flywheel/task-packet/preview
POST /api/conversation-runtime/flywheel/execution-feedback/inspect
```

Result:

```text
backend_chain=passed
inspect_intent=flywheel_signal
preview_intent=mixed
feedback_intent=execution_feedback
preview_summary=Topic 'flywheel_v1_ai_entry_control_surface' intent 'inspect chat turn for IKE flywheel candidate extraction' has 2 labels (knowledge:1, evolution:1)
```

## Screenshots Or Evidence

No screenshot was captured. The current environment does not have a usable Playwright/browser automation package, and browser automation was not added as a project dependency.

## Known Risks

- Real click-level UX is not fully verified.
- The chat handoff action should still be manually checked in a browser before calling Flywheel V1 completed.
- The backend chain smoke uses deterministic mocked LLM output through `TestClient`; it validates route wiring and boundaries, not live model quality.

## Follow-Up

Run a manual or delegated browser click smoke:

```text
/chat -> create or load non-empty message -> Open in Flywheel -> /evolution?handoff=chat -> prefilled form -> manual inspect
```

If that passes, Flywheel V1 can move from `partial` to first usable V1 evidence.
