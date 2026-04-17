# IKE Source Intelligence V1 M1 Refresh Context Result

Date: 2026-04-12
Status: bounded controller-coded patch

## Purpose

Close the next narrow gap after discovery-contract alignment:

- create-plan already preserved discovery context
- refresh still rebuilt discovery requests from only `topic + focus`

This patch makes refresh reuse the same bounded context contract.

## Files Changed

- [D:\code\MyAttention\services\api\routers\feeds.py](/D:/code/MyAttention/services/api/routers/feeds.py)
- [D:\code\MyAttention\services\api\tests\test_source_discovery_contract.py](/D:/code/MyAttention/services/api/tests/test_source_discovery_contract.py)
- [D:\code\MyAttention\services\api\tests\test_source_plan_helpers.py](/D:/code/MyAttention/services/api/tests/test_source_plan_helpers.py)

## What Changed

### 1. Refresh now reconstructs a bounded discovery request from persisted plan context

Added a narrow helper that rebuilds `SourceDiscoveryRequest` from persisted
plan state using:

- `topic`
- `focus`
- `task_intent`
- `interest_bias`
- `limit`

instead of silently dropping the non-topic context during refresh.

### 2. Refresh now persists updated discovery context again

After refresh, the plan metadata now keeps:

- `task_intent`
- `interest_bias`
- `discovery_notes`
- `discovery_truth_boundary`

so refresh no longer weakens the context chain established during plan
creation.

### 3. Focused helper validation now covers the full discovery-context chain

Tests now cover:

- `source plan create request -> discovery request`
- `persisted plan -> discovery request`
- `refresh -> plan.extra context retention`

This keeps the current M1 proof narrow but more complete.

## Validation Run

- `python -m unittest tests.test_source_discovery_contract tests.test_source_discovery_identity tests.test_source_plan_helpers tests.test_feeds_source_discovery_route`
- `python -m py_compile D:\code\MyAttention\services\api\routers\feeds.py D:\code\MyAttention\services\api\tests\test_source_discovery_contract.py D:\code\MyAttention\services\api\tests\test_source_plan_helpers.py D:\code\MyAttention\services\api\tests\test_feeds_source_discovery_route.py`

## Truth Boundary

- this improves the discovery-context continuity of the source-plan lifecycle
- this does not make source intelligence autonomous or research-grade
- this does not add a new source-plan governance subsystem
- this does not claim production-grade refresh quality

## Known Risks

- refresh still depends on the current bounded search/classification path
- plan refresh route itself is not yet covered by a separate isolated router
  test
- persisted metadata continuity is improved, but there is still no broader
  experiment/evaluation layer over source-plan refresh outcomes

## Recommendation

- `accept_with_changes`

Reason:

- the patch is narrow and closes a real continuity gap
- but it remains one M1 lifecycle-hardening step rather than a full milestone
  closure
