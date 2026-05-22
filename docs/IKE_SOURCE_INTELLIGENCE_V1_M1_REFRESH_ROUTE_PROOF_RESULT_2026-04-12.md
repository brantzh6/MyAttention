# IKE Source Intelligence V1 M1 Refresh Route Proof Result

Date: 2026-04-12
Status: bounded controller-coded patch

## Purpose

Close the next narrow gap after refresh-context continuity:

- helper-level refresh continuity was already proven
- route-level refresh continuity was still missing

This patch adds isolated API proof for `POST /sources/plans/{plan_id}/refresh`.

## Files Changed

- [D:\code\MyAttention\services\api\tests\test_feeds_source_discovery_route.py](/D:/code/MyAttention/services/api/tests/test_feeds_source_discovery_route.py)

## What Changed

### 1. Added isolated refresh route proof

The new route test verifies that `POST /api/sources/plans/{plan_id}/refresh`
returns a plan response that still exposes:

- `task_intent`
- `interest_bias`
- `discovery_notes`
- `discovery_truth_boundary`

### 2. Verified bounded refresh invocation

The route proof also checks that the route forwards:

- `limit`
- `trigger_type`

into the bounded refresh helper invocation.

## Validation Run

- `python -m unittest tests.test_source_discovery_contract tests.test_source_discovery_identity tests.test_source_plan_helpers tests.test_feeds_source_discovery_route`
- `python -m py_compile D:\code\MyAttention\services\api\routers\feeds.py D:\code\MyAttention\services\api\tests\test_source_discovery_contract.py D:\code\MyAttention\services\api\tests\test_source_plan_helpers.py D:\code\MyAttention\services\api\tests\test_feeds_source_discovery_route.py`

## Truth Boundary

- this proves isolated route continuity for refresh
- this does not prove real DB-backed refresh behavior end to end
- this does not prove search-quality improvement
- this does not promote `Source Intelligence V1 M1` to production-grade

## Known Risks

- refresh route is still tested with fake persistence rather than a real DB
- the route proof validates continuity and parameter forwarding, not search
  quality
- there is still no broader experiment/evaluation packet over repeated refresh
  outcomes

## Recommendation

- `accept_with_changes`

Reason:

- the patch stays narrow and closes a real API-level validation gap
- but this is still one focused proof step inside the larger M1 line
