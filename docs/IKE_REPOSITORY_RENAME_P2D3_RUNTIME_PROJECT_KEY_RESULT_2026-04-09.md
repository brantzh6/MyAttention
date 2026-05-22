# IKE Repository Rename P2-D3 Result

Date: 2026-04-09

## Scope

Narrow runtime project identity normalization:

- default visible/runtime bootstrap key
- matching backend router tests

## Files Changed

- [D:\code\MyAttention\services\web\components\settings\ike-workspace-manager.tsx](D:/code/MyAttention/services/web/components/settings/ike-workspace-manager.tsx)
- [D:\code\MyAttention\services\api\tests\test_routers_ike_v0.py](D:/code/MyAttention/services/api/tests/test_routers_ike_v0.py)

## What Changed

- default runtime project key:
  - `myattention-runtime-mainline` -> `ike-runtime-mainline`
- UI bootstrap/import actions now default to the new key
- backend router tests were aligned to the same runtime identity

## Validation

Executed:

```powershell
python -m unittest services.api.tests.test_routers_ike_v0
npx tsc --noEmit
```

Observed:

- router slice: `29 passed`
- frontend type-check: passed

## Risks

- existing persisted runtime projects in local databases may still use the old key until an explicit migration or re-bootstrap path touches them.
- this packet changes the default key for new surface actions; it does not retroactively rename existing DB rows.

## Recommendation

- `accept_with_changes`
