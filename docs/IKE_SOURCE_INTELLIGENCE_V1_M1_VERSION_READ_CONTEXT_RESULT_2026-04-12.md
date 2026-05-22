# IKE Source Intelligence V1 M1 Version Read Context Result

Date: 2026-04-12
Status: bounded controller-coded patch

## Purpose

Close the next narrow gap after version-snapshot continuity:

- snapshots already preserve discovery context
- version read responses still did not surface that context

This patch exposes a snapshot-derived bounded context summary on the existing
version response.

## Files Changed

- [D:\code\MyAttention\services\api\routers\feeds.py](/D:/code/MyAttention/services/api/routers/feeds.py)
- [D:\code\MyAttention\services\api\tests\test_source_plan_helpers.py](/D:/code/MyAttention/services/api/tests/test_source_plan_helpers.py)

## What Changed

### 1. SourcePlanVersionResponse now exposes bounded context summary

Version responses now include:

- `topic`
- `focus`
- `task_intent`
- `interest_bias`
- `discovery_notes`
- `discovery_truth_boundary`

These fields are:

- version-scoped summary
- snapshot-derived
- bounded
- non-comparative
- non-quality-claiming

### 2. Version serialization reads from plan_snapshot

The existing serializer now reads the new context summary from the stored
`plan_snapshot` instead of leaving that information hidden in version payload
storage only.

## Validation Run

- `python -m unittest tests.test_source_discovery_contract tests.test_source_discovery_identity tests.test_source_plan_helpers tests.test_feeds_source_discovery_route`
- `python -m py_compile D:\code\MyAttention\services\api\routers\feeds.py D:\code\MyAttention\services\api\tests\test_source_discovery_contract.py D:\code\MyAttention\services\api\tests\test_source_plan_helpers.py D:\code\MyAttention\services\api\tests\test_feeds_source_discovery_route.py`

## Truth Boundary

- this improves version-read visibility only
- this does not create a new version API family
- this does not add diffing or comparison semantics
- this does not claim stronger source-intelligence quality

## Known Risks

- version response shape is broader, so consumers assuming a minimal response
  should still be reviewed
- this still surfaces only a summary, not a full structured discovery packet
- downstream consumers must not reinterpret these fields as version quality
  rating or diff/comparison semantics

## Recommendation

- `accept_with_changes`

Reason:

- the patch stays narrow and completes a real read-surface gap
- but it is still one bounded `M1` continuity step rather than a final line closure
