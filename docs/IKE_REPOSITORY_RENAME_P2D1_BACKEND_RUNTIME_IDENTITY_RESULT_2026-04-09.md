# IKE Repository Rename P2-D1 Result

Date: 2026-04-09

## Scope

Narrow backend/runtime identity normalization only:

- API service naming
- runtime health/system surface naming
- container alias compatibility for `ike-*` vs legacy `myattention-*`
- default Qwen coding model alignment to `qwen3.6-plus`

Non-goals:

- database name migration
- notification copy rewrite
- frontend branding sweep
- live service reinstall

## Files Changed

- [D:\code\MyAttention\services\api\config.py](D:/code/MyAttention/services/api/config.py)
- [D:\code\MyAttention\services\api\main.py](D:/code/MyAttention/services/api/main.py)
- [D:\code\MyAttention\services\api\run_service.py](D:/code/MyAttention/services/api/run_service.py)
- [D:\code\MyAttention\services\api\routers\system.py](D:/code/MyAttention/services/api/routers/system.py)
- [D:\code\MyAttention\services\api\tests\test_config_runtime_identity.py](D:/code/MyAttention/services/api/tests/test_config_runtime_identity.py)
- [D:\code\MyAttention\services\api\tests\test_system_runtime_identity.py](D:/code/MyAttention/services/api/tests/test_system_runtime_identity.py)

## What Changed

- `services/api/main.py`
  - `MyAttention API` startup/shutdown/title/root message -> `IKE API`
- `services/api/run_service.py`
  - entrypoint description -> `IKE API service entrypoint`
- `services/api/config.py`
  - coding DashScope default model -> `qwen3.6-plus`
- `services/api/routers/system.py`
  - canonical container identities now use `ike-*`
  - legacy `myattention-*` aliases remain accepted
  - API service display name -> `IKE API`
  - restart endpoint now resolves canonical or legacy container names truthfully

## Validation

Executed:

```powershell
python -m unittest services.api.tests.test_config_runtime_identity services.api.tests.test_system_runtime_identity
python -m compileall services\api\config.py services\api\main.py services\api\run_service.py services\api\routers\system.py services\api\tests\test_config_runtime_identity.py services\api\tests\test_system_runtime_identity.py
python -m unittest services.api.tests.test_routers_ike_v0
```

Observed:

- config/system identity tests: `5 passed`
- compile checks: passed
- targeted router regression slice: `29 passed`

## Risks

- `database_url` still defaults to legacy `myattention` credentials/database for compatibility; this was intentionally not migrated in this packet.
- notification copy and broader backend/product branding still contain legacy `MyAttention` strings.
- `routers/system.py` was rewritten as a clean UTF-8 file to escape prior encoding noise; behavior stayed narrow but should still be considered `accept_with_changes`.

## Recommendation

- `accept_with_changes`
