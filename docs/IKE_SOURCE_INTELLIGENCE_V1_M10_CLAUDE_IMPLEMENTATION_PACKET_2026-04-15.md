# IKE Source Intelligence V1 - M10 Claude Implementation Packet

Date: 2026-04-15
Status: controller delegation packet

## Task

Refactor the current AI judgment / panel inspect kernel into a more reusable
internal module without changing external route behavior.

## Current Landing Area

- [D:\code\MyAttention\services\api\routers\feeds.py](/D:/code/MyAttention/services/api/routers/feeds.py)
- [D:\code\MyAttention\services\api\tests\test_feeds_source_discovery_route.py](/D:/code/MyAttention/services/api/tests/test_feeds_source_discovery_route.py)
- [D:\code\MyAttention\services\api\feeds](/D:/code/MyAttention/services/api/feeds)

## Goal

Take the current route-local judgment kernel and move the generic parts toward a
capability-shaped internal substrate.

Examples of acceptable bounded extraction:

1. provider-aware default model resolution
2. JSON parsing / fence stripping / malformed fallback
3. judgment normalization
4. verdict-overlap comparison
5. disagreement / consensus insight derivation

Possible landing shape:

- a new internal module under `services/api/feeds/`

## Hard Constraints

1. keep route contracts unchanged
2. do not add persistence
3. do not add workflow behavior
4. do not widen semantics
5. do not rename public response fields
6. do not break existing focused tests

## Validation Expectations

- `python -m unittest tests.test_feeds_source_discovery_route tests.test_source_discovery_identity tests.test_source_plan_helpers tests.test_source_discovery_contract tests.test_attention_policy_foundation`
- `python -m py_compile D:\code\MyAttention\services\api\routers\feeds.py D:\code\MyAttention\services\api\tests\test_feeds_source_discovery_route.py`

## Required Return Format

Return:

1. `summary`
2. `files_changed`
3. `why_this_solution`
4. `validation_run`
5. `known_risks`
6. `recommendation`

## Controller Recommendation Target

- `accept_with_changes`

Raise to `accept` only if:

- the extraction is clean
- route semantics are unchanged
- the new internal shape is genuinely more reusable
