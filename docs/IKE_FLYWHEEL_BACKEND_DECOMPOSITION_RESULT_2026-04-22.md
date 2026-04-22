# IKE Flywheel Backend Decomposition Result

**Date:** 2026-04-22
**Status:** Ready for review

## Summary

Performed a semantics-preserving backend decomposition of `services/api/conversation_runtime/flywheel.py`.

The previous monolithic file handled:

- flywheel inspect
- task-packet preview
- execution-feedback inspect

It is now a compatibility facade that re-exports the existing public route functions while the implementation lives in smaller bounded modules.

## Files Changed

| File | Change |
|---|---|
| `services/api/conversation_runtime/flywheel.py` | Reduced to compatibility facade and public re-exports. |
| `services/api/conversation_runtime/flywheel_inspect.py` | New module for flywheel inspect prompting, candidate normalization, advice, controller packet, and route function. |
| `services/api/conversation_runtime/task_packet_preview.py` | New module for selected-label normalization and task-packet preview. |
| `services/api/conversation_runtime/execution_feedback.py` | New module for execution-feedback prompt, reflection normalization, provenance echo, and route function. |

## Compatibility Contract

Public imports used by the router are preserved:

```python
from conversation_runtime.flywheel import (
    run_execution_feedback_inspect,
    run_flywheel_inspect,
    run_task_packet_preview,
)
```

The facade also preserves `conversation_runtime.flywheel.LLMAdapter` for existing tests that patch this symbol.

## Semantics Preserved

No intended changes to:

- route paths
- request/response shapes
- truth boundaries
- candidate proposal state
- review gates
- absorption state
- `promotion_state`
- caller-provided provenance semantics

## Delegation Notes

Implementation was delegated to `claude-worker`.

- run_id: `20260422T011922-6291c782`
- provider/model: `qwen-bailian-coding / glm-5`
- prompt delivery: verified
- result status: aborted by controller after a long no-final/no-stdout wait
- useful patch: yes
- controller action: accepted the patch after local validation

This is a worker lifecycle issue, not a code semantics issue: the worker edited files but did not return a structured final result.

## Validation Run

```text
python -m unittest services.api.tests.test_flywheel_inspect_route
21 tests OK

python -m unittest services.api.tests.test_conversation_runtime_route services.api.tests.test_flywheel_inspect_route
36 tests OK

python -m py_compile services/api/conversation_runtime/flywheel_inspect.py services/api/conversation_runtime/task_packet_preview.py services/api/conversation_runtime/execution_feedback.py
passed
```

## Known Risks

1. The new modules intentionally reuse shared candidate normalization from `flywheel_inspect.py` inside `execution_feedback.py`; this is acceptable for now but may become a separate shared helper later.
2. The facade keeps `LLMAdapter` patch compatibility for tests. This is pragmatic but should be revisited if tests move to patching the concrete modules directly.
3. Frontend panel decomposition is still incomplete.
4. The worker run had to be aborted after producing a patch, so the worker lifecycle remains a support-track reliability concern.

## Recommendation

`accept_with_changes`

Accept this as backend decomposition phase 1. The next decomposition step should target the frontend panel or extract shared flywheel candidate helpers.
