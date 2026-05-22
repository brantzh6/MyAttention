# IKE Agent Harness Highest Reasoning Default Result

Date: 2026-04-10
Status: accept_with_changes

## Scope

Tighten the routine automated delivery chain so highest available reasoning / thinking depth is the default expectation rather than an optional preference.

## Verified Current Runtime Truth

### OpenClaw

- current config already uses:
  - `thinkingDefault = high`
- current reasoning-capable routine models include:
  - `qwen3.6-plus`
  - `glm-5`
  - `kimi-k2.5`

### Claude worker

- there is no separate lower-level backend `thinkingDefault` knob in the current local worker wrapper
- the worker now defaults packet metadata to:
  - `reasoning_mode = high`

## Files Changed

- [D:\code\MyAttention\services\api\claude_worker\worker.py](/D:/code/MyAttention/services/api/claude_worker/worker.py)
- [D:\code\MyAttention\scripts\acpx\openclaw_delegate.py](/D:/code/MyAttention/scripts/acpx/openclaw_delegate.py)
- [D:\code\MyAttention\scripts\acpx\run_file_delegation.py](/D:/code/MyAttention/scripts/acpx/run_file_delegation.py)
- [D:\code\MyAttention\docs\PROJECT_AGENT_HARNESS_CONTRACT.md](/D:/code/MyAttention/docs/PROJECT_AGENT_HARNESS_CONTRACT.md)
- [D:\code\MyAttention\docs\IKE_AGENT_HARNESS_REASONING_POLICY_2026-04-09.md](/D:/code/MyAttention/docs/IKE_AGENT_HARNESS_REASONING_POLICY_2026-04-09.md)

## Landed Behavior

- Claude worker `WorkerPacket.reasoning_mode` now defaults to `high`
- Claude worker CLI `start --reasoning-mode` now defaults to `high`
- OpenClaw `openclaw_delegate.py --reasoning-mode` now defaults to `high`
- OpenClaw `run_file_delegation.py --reasoning-mode` now defaults to `high`
- controller docs now explicitly treat highest available automated reasoning as the default routine policy

## Validation

```powershell
python -m unittest services.api.tests.test_claude_worker
python -m compileall D:\code\MyAttention\services\api\claude_worker D:\code\MyAttention\scripts\acpx\openclaw_delegate.py D:\code\MyAttention\scripts\acpx\run_file_delegation.py
python D:\code\MyAttention\scripts\acpx\openclaw_delegate.py --help
python D:\code\MyAttention\scripts\acpx\run_file_delegation.py --help
```

## Controller Judgment

- This does not mean every backend exposes a richer-than-`high` knob.
- It does mean the project default is now explicit:
  - do not run important delegated work below the highest available automated reasoning depth unless intentionally marked otherwise.

## Recommendation

`accept_with_changes`
