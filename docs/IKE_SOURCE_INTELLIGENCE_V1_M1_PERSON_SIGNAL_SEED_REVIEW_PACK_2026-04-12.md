# IKE Source Intelligence V1 M1 Person Signal Seed Review Pack

Date: 2026-04-12
Status: ready_for_review

## Scope

This pack covers the bounded `social status -> person seed` improvement slice on
the existing source-discovery path.

It does not add new API surface.
It does not add cross-source identity resolution.
It only improves conservative person seeding from structured social status
signals already present in discovery results.

## Included Files

- [D:\code\MyAttention\docs\IKE_SOURCE_INTELLIGENCE_V1_M1_PERSON_SIGNAL_SEED_RESULT_2026-04-12.md](/D:/code/MyAttention/docs/IKE_SOURCE_INTELLIGENCE_V1_M1_PERSON_SIGNAL_SEED_RESULT_2026-04-12.md)
- [D:\code\MyAttention\docs\IKE_SOURCE_INTELLIGENCE_V1_M1_PERSON_SIGNAL_SEED_REVIEW_ABSORPTION_2026-04-12.md](/D:/code/MyAttention/docs/IKE_SOURCE_INTELLIGENCE_V1_M1_PERSON_SIGNAL_SEED_REVIEW_ABSORPTION_2026-04-12.md)
- [D:\code\MyAttention\services\api\routers\feeds.py](/D:/code/MyAttention/services/api/routers/feeds.py)
- [D:\code\MyAttention\services\api\tests\test_source_discovery_identity.py](/D:/code/MyAttention/services/api/tests/test_source_discovery_identity.py)
- [D:\code\MyAttention\services\api\tests\test_feeds_source_discovery_route.py](/D:/code/MyAttention/services/api/tests/test_feeds_source_discovery_route.py)

## What This Slice Now Proves

1. `x.com/.../status/...` can seed a bounded `person` candidate
2. `twitter.com/.../status/...` can seed a bounded `person` candidate
3. author-derived person seeds remain conservative:
   - `builder`, not `maintainer`
   - modest follow-score, not strong escalation
4. the conservative `builder` inference is focus-bounded:
   - allowed under `METHOD/FRONTIER`
   - not escalated under `LATEST`
5. author-derived person seeds preserve truthful parent linkage:
   - `related_entities[*].item_type = signal`

## What This Slice Explicitly Does Not Prove

1. research-grade person discovery
2. canonical actor identity
3. cross-source identity resolution
4. person graph / actor graph semantics
5. a reopened broad Source Intelligence expansion

## Focused Validation

- `python -m unittest tests.test_source_discovery_identity tests.test_source_discovery_contract tests.test_feeds_source_discovery_route tests.test_source_plan_helpers tests.test_source_plan_versioning_helpers`
- `python -m py_compile D:\code\MyAttention\services\api\routers\feeds.py D:\code\MyAttention\services\api\tests\test_source_discovery_identity.py D:\code\MyAttention\services\api\tests\test_feeds_source_discovery_route.py`

Validation result:

- `45 tests OK`
- compile passed

## Controller Judgment

- code-level: eligible for `accept`
- controller/project-level: `accept_with_changes`

Reason:

The slice is bounded and materially improves person/object discovery quality on
the existing path, but it must remain seed-level and must not drift into
identity resolution or broader person-discovery expansion.
