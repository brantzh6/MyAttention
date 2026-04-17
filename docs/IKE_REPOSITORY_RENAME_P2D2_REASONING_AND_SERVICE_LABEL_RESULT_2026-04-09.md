# IKE Repository Rename P2-D2 Result

Date: 2026-04-09

## Scope

Narrow controller-chain normalization only:

- Claude worker routine default model
- settings/system API display label
- durable reasoning/thinking-depth baseline for automatable lanes

Non-goals:

- runtime project-key migration
- backend object/model rename sweep
- provider-specific reasoning parameter reverse engineering

## Files Changed

- [D:\code\MyAttention\services\api\claude_worker\worker.py](D:/code/MyAttention/services/api/claude_worker/worker.py)
- [D:\code\MyAttention\services\api\routers\settings.py](D:/code/MyAttention/services/api/routers/settings.py)
- [D:\code\MyAttention\docs\PROJECT_AGENT_HARNESS_CONTRACT.md](D:/code/MyAttention/docs/PROJECT_AGENT_HARNESS_CONTRACT.md)
- [D:\code\MyAttention\docs\IKE_AUTOMATED_REASONING_BASELINE_2026-04-09.md](D:/code/MyAttention/docs/IKE_AUTOMATED_REASONING_BASELINE_2026-04-09.md)

## What Changed

- Claude worker default model:
  - `glm-5` -> `qwen3.6-plus`
- settings/system service label:
  - `MyAttention API` -> `IKE API`
- durable controller rule now explicitly records:
  - OpenClaw current agents use `thinkingDefault = high`
  - `qwen3.6-plus`, `glm-5`, and `kimi-k2.5` are currently reasoning-capable in local OpenClaw registry
  - important delegated packets should keep high reasoning / thinking depth by default

## Validation

Executed:

```powershell
python -m unittest services.api.tests.test_claude_worker
python -m compileall services\api\claude_worker\worker.py services\api\routers\settings.py
```

Observed:

- Claude worker suite: `16 passed`
- compile checks: passed

## Risks

- `settings.py` display-name changes were compile-checked only; there is no dedicated settings-router regression slice in this packet.
- This result records the current reasoning baseline but does not prove every provider-side reasoning flag is externally visible or adjustable through the same API.
- runtime project identity still contains `myattention-runtime-mainline`; that is a separate rename packet.

## Recommendation

- `accept_with_changes`
