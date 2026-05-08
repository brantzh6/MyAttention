# Flywheel V1 Browser Smoke Result

Date: 2026-05-08

Task ID: FLYWHEEL_V1_BROWSER_SMOKE_P0_2026-05-08

Recommendation: accept_with_changes

## Summary

The first Flywheel V1 smoke is closed as a usable V1 evidence baseline, with one UI-chain follow-up still tracked.

Confirmed:

- `/chat` renders.
- `/evolution` renders.
- `/control` renders.
- backend flywheel inspect succeeds with deterministic test input.
- task packet preview succeeds from selected inspect candidates.
- execution feedback inspect succeeds from the task packet preview summary.
- all inspected artifacts remain `inspect_only` / non-canonical.
- real browser click from a visible chat message's `Open in Flywheel` action navigates into `/evolution?handoff=chat`.
- handoff payload is imported into the flywheel panel, storage is cleared, and inspect is not auto-submitted.
- browser UI can submit a flywheel inspect request and render inspect candidates from a mocked response.
- browser UI can select inspect candidates and issue the task-packet preview request.

Still partial:

- browser automation did not yet stably verify task-packet preview rendering plus execution-feedback rendering in the same end-to-end UI script. Backend route chain for those two steps is already validated below.

## Environment

- Branch: `codex/pre-ike-restructure-2026-04-09`
- Commit tested: `b799dae`
- Web dev server: `http://localhost:3100`
- Backend chain validation: FastAPI `TestClient`
- Browser automation: temporary Playwright install under `%TEMP%\myattention-playwright-smoke`; no project dependency added

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
| real chat button click | passed | visible chat message action clicked, navigated to `/evolution?handoff=chat` |
| chat handoff prefill | passed | textarea contains user and assistant content; topic/task intent populated |
| handoff boundary | passed | storage cleared; no auto-submit; notice rendered |
| browser inspect render | passed | mocked inspect response rendered `chat_to_flywheel_bridge_verified` |
| browser preview request | passed | selecting two candidates enabled preview and issued one preview API call |
| browser preview + feedback render | partial | backend chain passed; UI render script needs a more stable selector/wait strategy |

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

Browser chat handoff smoke:

```text
passed=true
buttonCount=2
textareaHasUser=true
textareaHasAssistant=true
topic=flywheel_v1_ai_entry_control_surface
taskIntent=inspect chat turn for IKE flywheel candidate extraction
notice=true
storageCleared=true
autoSubmitted=false
```

Browser flywheel inspect and preview request smoke:

```text
inspect rendered: chat_to_flywheel_bridge_verified
selected candidates: 2
preview API calls: 1
preview render + feedback render: partial selector/wait follow-up
```

## Known Risks

- The full browser-rendered preview + execution-feedback loop still needs one stable UI automation pass.
- The backend chain smoke uses deterministic mocked LLM output through `TestClient`; it validates route wiring and boundaries, not live model quality.
- This is V1 usability evidence, not a production promotion decision.

## Follow-Up

Next local validation target:

```text
/evolution -> inspect -> select candidates -> preview renders -> worker feedback input -> execution feedback renders
```

Use local review/test only for this follow-up unless it is being packaged as a GitHub promotion candidate.
