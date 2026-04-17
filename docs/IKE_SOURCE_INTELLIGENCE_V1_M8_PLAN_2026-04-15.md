# IKE Source Intelligence V1 - M8 Plan

Date: 2026-04-15
Phase: `M8 AI Judgment Panel Inspect`
Status: `planned_and_landed`

## Goal

Land one bounded dual-lane inspect route above the existing `M7` AI judgment
lane.

## Minimal Writeset

- [D:\code\MyAttention\services\api\routers\feeds.py](/D:/code/MyAttention/services/api/routers/feeds.py)
- [D:\code\MyAttention\services\api\tests\test_feeds_source_discovery_route.py](/D:/code/MyAttention/services/api/tests/test_feeds_source_discovery_route.py)

## Plan

1. add a panel inspect request/response contract
2. run two bounded lane calls on the same candidate subset
3. compare verdict overlap without producing a merged decision
4. expose agreement/disagreement shape only
5. keep asymmetric lane failure visible and non-stable
6. stop before any persistence or workflow expansion

## Validation

- `python -m unittest tests.test_feeds_source_discovery_route tests.test_source_discovery_identity tests.test_source_plan_helpers tests.test_source_discovery_contract tests.test_attention_policy_foundation`
- `python -m py_compile D:\code\MyAttention\services\api\routers\feeds.py D:\code\MyAttention\services\api\tests\test_feeds_source_discovery_route.py`

## Controller Boundary

This packet is valid only if it remains:

- inspect-only
- non-persistent
- non-merging
- bounded to exactly one dual-lane verdict-overlap comparison surface
