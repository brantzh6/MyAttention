# IKE Source Intelligence V1 - M7 Plan

Date: 2026-04-14
Phase: `M7 AI-Assisted Candidate Judgment Inspect`
Status: `planned_and_landed`

## Goal

Land one inspect-only AI judgment lane above the existing `M1 -> M6`
discovery-path improvements.

## Minimal Writeset

- [D:\code\MyAttention\services\api\routers\feeds.py](/D:/code/MyAttention/services/api/routers/feeds.py)
- [D:\code\MyAttention\services\api\tests\test_feeds_source_discovery_route.py](/D:/code/MyAttention/services/api/tests/test_feeds_source_discovery_route.py)

## Plan

1. expose a bounded `judge/inspect` route on top of the existing discovery path
2. reuse the existing candidate payload and bounded prompt builder
3. normalize returned JSON into reviewable verdicts
4. prove route behavior with focused tests only
5. stop before persistence or workflow expansion

## Validation

- `python -m unittest tests.test_feeds_source_discovery_route tests.test_source_discovery_identity tests.test_source_plan_helpers tests.test_source_discovery_contract tests.test_attention_policy_foundation`
- `python -m py_compile D:\code\MyAttention\services\api\routers\feeds.py D:\code\MyAttention\services\api\tests\test_feeds_source_discovery_route.py`

## Controller Boundary

This packet is valid only if it remains:

- inspect-only
- advisory
- bounded to existing discovery candidates
- free of any truth mutation
