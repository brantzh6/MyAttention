# IKE Source Intelligence V1 M11 Version Judgment Result

Date: 2026-04-15
Status: implemented
Recommendation: `accept_with_changes`

## Summary

`M11` lands the second distinct use case for the internal AI judgment substrate.

The project now has:

- `POST /api/sources/plans/{plan_id}/versions/{version_number}/judge/inspect`

This route:

- reads an existing persisted source-plan version
- extracts a bounded set of refresh/version change targets
- runs inspect-only advisory AI judgment on those targets
- returns normalized `follow|review|ignore` verdicts

It does not:

- change the source plan
- change the source-plan version
- override persisted `evaluation.decision_status`
- persist AI judgments

## Files Changed

- `services/api/routers/feeds.py`
- `services/api/tests/test_source_plan_versioning_helpers.py`
- `services/api/tests/test_feeds_source_discovery_route.py`

## Validation

```bash
python -m unittest tests.test_ai_judgment_substrate tests.test_feeds_source_discovery_route tests.test_source_discovery_identity tests.test_source_plan_helpers tests.test_source_discovery_contract tests.test_source_plan_versioning_helpers tests.test_attention_policy_foundation
python -m py_compile D:\code\MyAttention\services\api\routers\feeds.py D:\code\MyAttention\services\api\tests\test_source_plan_versioning_helpers.py D:\code\MyAttention\services\api\tests\test_feeds_source_discovery_route.py
```

Result:

- `92 tests OK`
- compile passed

## Why This Matters

Before `M11`, `feeds.ai_judgment` was only proven on discovery-candidate inspect routes.

After `M11`, the same substrate is also used on a second surface:

- source-plan refresh/version changes

This materially strengthens the claim that the current substrate is reusable
inside `Source Intelligence V1`, while still staying below generic capability
modularization.

The route judges:

- bounded refresh-change targets

It does **not** judge:

- the source-plan version as a whole
- whether the persisted version decision should be accepted, rejected, or rolled back

## Known Risks

- this is still single-model inspect, not panel judgment
- target extraction is intentionally heuristic and bounded
- this does not yet prove workflow usefulness, only reuse on a second surface

## Controller Judgment

- code-level: `accept`
- project-level: `accept_with_changes`

Reason for `accept_with_changes`:

- the slice is intentionally narrow and inspect-only
- the next step should be review and absorption, not automatic expansion into
  persistence or workflow
