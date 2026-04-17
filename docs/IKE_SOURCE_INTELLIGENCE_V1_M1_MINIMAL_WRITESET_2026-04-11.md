# IKE Source Intelligence V1 M1 Minimal Write Set

Date: 2026-04-11
Status: controller writeset boundary

## Purpose

Keep the first `Source Intelligence V1 M1` coding lane narrow and auditable.

## Preferred Write Set

### Required

- [D:\code\MyAttention\services\api\routers\feeds.py](/D:/code/MyAttention/services/api/routers/feeds.py)

### Likely test files

- [D:\code\MyAttention\services\api\tests\test_source_discovery_identity.py](/D:/code/MyAttention/services/api/tests/test_source_discovery_identity.py)
- [D:\code\MyAttention\services\api\tests\test_source_plan_helpers.py](/D:/code/MyAttention/services/api/tests/test_source_plan_helpers.py)
- [D:\code\MyAttention\services\api\tests\test_source_plan_versioning_helpers.py](/D:/code/MyAttention/services/api/tests/test_source_plan_versioning_helpers.py)
- [D:\code\MyAttention\services\api\tests\test_source_plan_review_issues.py](/D:/code/MyAttention/services/api/tests/test_source_plan_review_issues.py)

### Optional

One new focused test file is acceptable if the current test files become too
mixed.

## Discouraged In M1

- new schema family
- broad changes in `db/models.py`
- broad changes in collector/fetcher modules
- new frontend surface
- multi-file orchestration across unrelated runtime modules

## Acceptable Refactor Boundary

A very small helper extraction from `feeds.py` is acceptable only if:

1. it directly improves testability or boundedness
2. it does not create a second source-intelligence semantics layer
3. it stays within a small file set

## Validation Boundary

Minimum validation should stay focused to source-discovery/source-plan slices,
not whole-project broad suites.

## Recommendation

`accept`

M1 should be treated as a focused `feeds.py`-centric packet unless code
inspection during implementation proves a tiny extraction is necessary.
