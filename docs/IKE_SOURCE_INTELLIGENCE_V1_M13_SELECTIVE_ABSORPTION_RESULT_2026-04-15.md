# IKE Source Intelligence V1 M13 Selective Absorption Result - 2026-04-15

## Summary

`M13` landed a bounded selective-absorption advisory layer on top of the
existing panel outputs.

The new capability lives first in the reusable internal substrate:

- `D:\code\MyAttention\services\api\feeds\ai_judgment.py`

It is now surfaced on both existing panel routes:

- discovery candidate panel inspect
- source-plan version-change panel inspect

No new route was added.

## What Changed

Added new internal response models:

- `SourceJudgmentSelectiveAbsorptionItem`
- `SourceJudgmentSelectiveAbsorptionAdvice`

Added new substrate helper:

- `derive_selective_absorption_advice(...)`

This helper converts panel output into a bounded controller-facing advisory
shape:

- `ready_to_follow`
- `ready_to_suppress`
- `needs_manual_review`
- `watch_candidates`
- `controller_notes`

Existing panel response models now expose:

- `selective_absorption`

## Why This Solution

This is the smallest useful step above inspect-only panel output.

It does not create workflow or persistence. It only makes the panel result
more actionable for controller review.

It also proves the judgment substrate is moving toward reusable capability
shape rather than remaining route-local aggregation logic.

## Validation Run

```bash
python -m unittest tests.test_ai_judgment_substrate tests.test_feeds_source_discovery_route tests.test_source_plan_versioning_helpers
python -m unittest tests.test_ai_judgment_substrate tests.test_feeds_source_discovery_route tests.test_source_discovery_identity tests.test_source_plan_helpers tests.test_source_discovery_contract tests.test_source_plan_versioning_helpers tests.test_attention_policy_foundation
python -m py_compile D:\code\MyAttention\services\api\feeds\ai_judgment.py D:\code\MyAttention\services\api\routers\feeds.py D:\code\MyAttention\services\api\tests\test_ai_judgment_substrate.py D:\code\MyAttention\services\api\tests\test_feeds_source_discovery_route.py
```

Result:

- `51 tests OK`
- `99 tests OK`
- compile passed

## Known Risks

- this is still advisory only, not workflow or promotion
- advice quality is bounded by current panel insight heuristics
- `selective_absorption` is controller-facing guidance, not canonical truth

## Truth Boundary

- `selective_absorption` is advisory controller guidance only
- it does not persist outcomes
- it does not replace controller review
- it does not automate version or source-plan decisions

## Recommendation

`accept_with_changes`

The remaining `with_changes` is a stop rule, not a code defect:
`M13` should stop at advisory guidance and must not expand into automatic
absorption or workflow.
