# IKE Flywheel Provenance Discipline Result 2026-04-26

## Summary

This slice strengthens flywheel execution-feedback provenance discipline.

Execution feedback inspect now explicitly returns provenance completeness metadata, including:

- `completeness_status`
- `provided_fields`
- `missing_fields`

The controller packet and notes now also preserve provenance completeness as inspect-only observability context.

## Files Changed

- `services/api/conversation_runtime/contracts.py`
- `services/api/conversation_runtime/execution_feedback.py`
- `services/api/tests/test_flywheel_inspect_route.py`
- `services/web/lib/api-client.ts`
- `services/web/components/evolution/execution-feedback-provenance.tsx`

## Why This Solution

The current mainline is moving from runtime surface readiness to AI-participation loop closure.

At that stage, missing worker provenance is no longer a cosmetic issue.
It directly affects whether a returned worker result is traceable and reusable.

This slice does not try to verify provenance.
It makes provenance quality explicit, review-visible, and test-proven.

## Validation Run

```powershell
cd D:\code\MyAttention
python -m unittest services.api.tests.test_flywheel_inspect_route services.api.tests.test_conversation_runtime_route
```

Result:

- `36` tests passed

```powershell
cd D:\code\MyAttention\services\web
npm run build
```

Result:

- success

## Known Risks

- Provenance is still caller-provided and unverified.
- Completeness improves observability, not truth.
- This slice does not yet integrate with a real worker runtime source of truth.

## Recommendation

`accept`
