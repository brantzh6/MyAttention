# IKE Source Intelligence V1 M1 Discovery Contract Result

Date: 2026-04-12
Status: bounded controller-coded patch

## Purpose

Align the existing `POST /sources/discover` contract with the first real
AI-domain discovery loop without widening into collector, schema, or UI work.

## Files Changed

- [D:\code\MyAttention\services\api\routers\feeds.py](/D:/code/MyAttention/services/api/routers/feeds.py)
- [D:\code\MyAttention\services\api\tests\test_source_discovery_contract.py](/D:/code/MyAttention/services/api/tests/test_source_discovery_contract.py)
- [D:\code\MyAttention\services\api\tests\test_feeds_source_discovery_route.py](/D:/code/MyAttention/services/api/tests/test_feeds_source_discovery_route.py)

## What Changed

### 1. Request contract now carries bounded discovery intent

`SourceDiscoveryRequest` now supports:

- `task_intent`
- `interest_bias`

This makes the discovery path closer to the `Source Intelligence V1 M1` scope
instead of keeping intent only in controller-side docs.

### 2. Response contract now exposes explicit inspect semantics

`SourceDiscoveryResponse` now returns:

- `task_intent`
- `interest_bias`
- `notes`
- `truth_boundary`

This keeps the inspect route more truthful and makes it clearer that discovery
output is planning input, not canonical source truth.

### 3. Candidate output now carries bounded semantic hints

Discovery candidates now expose additional bounded fields:

- `source_nature`
- `temperature`
- `recommended_mode`
- `recommended_execution_strategy`
- `why_relevant`
- `confidence_note`
- `canonical_ref`
- `candidate_endpoints`

These do not replace the existing contract. They add the minimum semantic layer
needed to make discovery results more controller-usable.

### 4. Method-focus reddit thread handling is normalized at community level

When focus is `method`, reddit thread URLs now normalize toward community-level
capture instead of staying thread-level signal identity. This matches the
existing helper expectation and better fits method-oriented discovery.

### 5. Route-level contract is now covered

An isolated router test now verifies that `POST /api/sources/discover` returns
the new bounded fields at the API level, not only through helper tests.

### 6. Source-plan creation now reuses the same intent/bias contract

`SourcePlanCreateRequest` now also accepts:

- `task_intent`
- `interest_bias`

and the create-plan path now maps these fields into the discovery request
instead of silently dropping them. The initial persisted plan metadata also
records the discovery notes and truth boundary that produced the plan.

### 7. Source-plan read path now exposes discovery context

`SourcePlanResponse` now surfaces the persisted discovery context:

- `task_intent`
- `interest_bias`
- `discovery_notes`
- `discovery_truth_boundary`

This keeps the plan object closer to the discovery result that produced it,
instead of forcing controller-side reconstruction from hidden `extra` fields.

### 8. Source-plan route now has isolated write/read proof

An isolated `POST /api/sources/plans` route test now verifies that:

- `task_intent`
- `interest_bias`
- `discovery_notes`
- `discovery_truth_boundary`

survive the create-plan write path and remain visible on the returned plan
response.

## Validation Run

- `python -m unittest tests.test_source_discovery_contract tests.test_source_discovery_identity tests.test_source_plan_helpers`
- `python -m unittest tests.test_source_discovery_contract tests.test_source_discovery_identity tests.test_source_plan_helpers tests.test_feeds_source_discovery_route`
- `python -m py_compile D:\code\MyAttention\services\api\routers\feeds.py D:\code\MyAttention\services\api\tests\test_source_discovery_contract.py`
- `python -m py_compile D:\code\MyAttention\services\api\routers\feeds.py D:\code\MyAttention\services\api\tests\test_source_discovery_contract.py D:\code\MyAttention\services\api\tests\test_feeds_source_discovery_route.py`

## Truth Boundary

- this patch improves contract clarity and candidate semantics
- this patch does not claim research-grade source intelligence
- this patch does not add canonical truth promotion
- this patch does not widen into collector or source-plan governance redesign

## Known Risks

- the response contract is broader, so any external consumers that assume a
  tightly fixed field set should still be smoke-tested
- `interest_bias` is currently derived from `focus` by default; it is not yet a
  separate reasoning system
- this still relies on the existing search/classification path rather than a
  stronger research-grade discovery substrate

## Recommendation

- `accept_with_changes`

Reason:

- the patch is narrow and materially improves the live discovery contract
- but it is still an M1 step, not a completed source-intelligence system
