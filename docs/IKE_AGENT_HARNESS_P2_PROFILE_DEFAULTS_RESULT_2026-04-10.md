# IKE Agent Harness P2 Profile Defaults Result

Date: 2026-04-10
Status: accept_with_changes

## Scope

Extend the shared delegated-run metadata vocabulary from:

- `lane`
- `reasoning_mode`

to also include:

- `sandbox_kind`
- `capability_profile`

across Claude worker, OpenClaw wrappers, and qoder bundle/launch scripts.

## Files Changed

- [D:\code\MyAttention\services\api\claude_worker\worker.py](/D:/code/MyAttention/services/api/claude_worker/worker.py)
- [D:\code\MyAttention\services\api\tests\test_claude_worker.py](/D:/code/MyAttention/services/api/tests/test_claude_worker.py)
- [D:\code\MyAttention\scripts\acpx\openclaw_delegate.py](/D:/code/MyAttention/scripts/acpx/openclaw_delegate.py)
- [D:\code\MyAttention\scripts\acpx\run_file_delegation.py](/D:/code/MyAttention/scripts/acpx/run_file_delegation.py)
- [D:\code\MyAttention\scripts\qoder\create_task_bundle.py](/D:/code/MyAttention/scripts/qoder/create_task_bundle.py)
- [D:\code\MyAttention\scripts\qoder\create_review_bundle.py](/D:/code/MyAttention/scripts/qoder/create_review_bundle.py)
- [D:\code\MyAttention\scripts\qoder\qoder_delegate.py](/D:/code/MyAttention/scripts/qoder/qoder_delegate.py)
- [D:\code\MyAttention\scripts\qoder\run_task.py](/D:/code/MyAttention/scripts/qoder/run_task.py)

## Landed Defaults

### Claude worker

- `sandbox_kind = claude_worker_run_root`
- `coding + high -> capability_profile = coding_high_reasoning`
- `review + high -> capability_profile = review_high_reasoning`

### OpenClaw wrappers

- default `sandbox_kind = openclaw_workspace`
- same default profile mapping:
  - `coding + high -> coding_high_reasoning`
  - `review + high -> review_high_reasoning`

### qoder chain

- default `sandbox_kind = qoder_workspace`
- default profile mapping is explicit in bundle/launch entrypoints:
  - task bundle / run task -> `coding_high_reasoning`
  - review bundle -> `review_high_reasoning`

## Validation

```powershell
python -m unittest services.api.tests.test_claude_worker
python -m compileall D:\code\MyAttention\services\api\claude_worker D:\code\MyAttention\scripts\acpx\openclaw_delegate.py D:\code\MyAttention\scripts\acpx\run_file_delegation.py D:\code\MyAttention\scripts\qoder\create_task_bundle.py D:\code\MyAttention\scripts\qoder\create_review_bundle.py D:\code\MyAttention\scripts\qoder\qoder_delegate.py D:\code\MyAttention\scripts\qoder\run_task.py
python D:\code\MyAttention\scripts\acpx\openclaw_delegate.py --help
python D:\code\MyAttention\scripts\acpx\run_file_delegation.py --help
python D:\code\MyAttention\scripts\qoder\create_task_bundle.py --help
python D:\code\MyAttention\scripts\qoder\create_review_bundle.py --help
python D:\code\MyAttention\scripts\qoder\qoder_delegate.py --help
python D:\code\MyAttention\scripts\qoder\run_task.py --help
```

## Controller Judgment

- This is still wrapper-level / packet-level enforcement.
- It is not yet runtime-wide capability enforcement.
- But it now makes the intended capability profile explicit across every major automated delegation lane.

## Recommendation

`accept_with_changes`
