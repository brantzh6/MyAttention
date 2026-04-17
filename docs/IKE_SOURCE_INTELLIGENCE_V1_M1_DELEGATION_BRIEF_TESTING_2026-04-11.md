# IKE Source Intelligence V1 M1 Delegation Brief - Testing

## Goal

Validate the bounded `Source Intelligence V1 M1` patch with focused tests only.

## Required Test Surface

Prefer:

- [D:\code\MyAttention\services\api\tests\test_source_discovery_identity.py](/D:/code/MyAttention/services/api/tests/test_source_discovery_identity.py)
- [D:\code\MyAttention\services\api\tests\test_source_plan_helpers.py](/D:/code/MyAttention/services/api/tests/test_source_plan_helpers.py)
- [D:\code\MyAttention\services\api\tests\test_source_plan_versioning_helpers.py](/D:/code/MyAttention/services/api/tests/test_source_plan_versioning_helpers.py)
- [D:\code\MyAttention\services\api\tests\test_source_plan_review_issues.py](/D:/code/MyAttention/services/api/tests/test_source_plan_review_issues.py)

Plus compile/import validation for touched files.

## Test Goal

Confirm:

1. no request/response drift
2. no obvious regression in discovery/source-plan helpers
3. no broad unrelated failures were introduced by the patch

## Output

Return:

1. tests run
2. results
3. failures or blockers
4. recommendation
