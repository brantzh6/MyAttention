# IKE Source Intelligence V1 M12 Version Panel Result

Date: 2026-04-15
Status: implemented
Recommendation: `accept_with_changes`

## Summary

`M12` lands the panel-inspect counterpart to `M11`.

The project now has:

- `POST /api/sources/plans/{plan_id}/versions/{version_number}/judge/panel/inspect`

This route:

- reads one persisted source-plan version
- reuses bounded version-change targets from `M11`
- runs one bounded dual-lane panel inspect
- returns:
  - `primary_judgments`
  - `secondary_judgments`
  - `panel_summary`
  - `panel_insights`

It does not:

- merge a canonical verdict
- modify source plans or versions
- override persisted version decision status
- persist panel output

## Files Changed

- `services/api/routers/feeds.py`
- `services/api/tests/test_feeds_source_discovery_route.py`

## Validation

```bash
python -m unittest tests.test_feeds_source_discovery_route tests.test_source_plan_versioning_helpers
python -m unittest tests.test_ai_judgment_substrate tests.test_feeds_source_discovery_route tests.test_source_discovery_identity tests.test_source_plan_helpers tests.test_source_discovery_contract tests.test_source_plan_versioning_helpers tests.test_attention_policy_foundation
python -m py_compile D:\code\MyAttention\services\api\routers\feeds.py D:\code\MyAttention\services\api\tests\test_feeds_source_discovery_route.py
```

Result:

- `41 tests OK`
- `95 tests OK`
- compile passed

## Why This Matters

`M12` proves that disagreement-aware panel insight is not locked to the
discovery-candidate surface.

The same AI-driven panel shape now exists on two distinct surfaces:

- discovery candidates
- source-plan version change targets

This strengthens the claim that multi-model judgment is moving toward a real
reusable internal capability, while still staying inside inspect-only
controller boundaries.

## Known Risks

- still inspect-only
- still not voting
- still not workflow
- still route-local rather than a fully extracted generic version-judgment module
- route proof is still bounded even after adding one malformed-secondary fallback case

## Controller Judgment

- code-level: `accept`
- project-level: `accept_with_changes`

Reason for `accept_with_changes`:

- this is the right bounded reuse proof
- but the next step should be review and selective absorption, not immediate
  expansion into automated version decisions
