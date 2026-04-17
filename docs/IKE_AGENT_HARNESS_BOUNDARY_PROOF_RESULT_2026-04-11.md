# IKE Agent Harness Boundary Proof Result

Date: 2026-04-11
Status: controller proof result

## Claimed Boundary

The current project claims:

- routine delegated lanes do not need to share the controller root as their
  mutable workspace
- delegated execution now carries a shared metadata vocabulary
- current harness hardening is beyond plain path isolation
- current harness hardening is still not full sandbox enforcement

## Proven Boundary

### 1. OpenClaw workspace isolation is materially real

Observed isolated workspaces:

- `D:\code\_agent-runtimes\openclaw-workspaces\myattention-coder`
- `D:\code\_agent-runtimes\openclaw-workspaces\myattention-reviewer`
- `D:\code\_agent-runtimes\openclaw-workspaces\myattention-kimi-review`

Observed current config in:

- `C:\Users\jiuyou\.openclaw\openclaw.json`

Current configured agent workspaces are those external roots, not
`D:\code\MyAttention`.

### 2. Claude worker default run-root is externally configured

Observed implementation in:

- [worker.py](/D:/code/MyAttention/services/api/claude_worker/worker.py)

Current code sets:

- default root via `_default_claude_worker_root()`
- `ClaudeWorkerRuntime.run_root = default_root / "runs"`

Repository restructure result also records the intended default root as:

- `D:\code\_agent-runtimes\claude-worker\runs`

Observed filesystem state:

- `D:\code\_agent-runtimes\claude-worker\runs` exists

Observed sample artifact run:

- `D:\code\_agent-runtimes\claude-worker\runs\20260411T085746-ddf50d4d`

Observed artifact files in that external run dir:

- `meta.json`
- `events.ndjson`
- `final.json`
- `summary.md`
- `patch.diff`

Important boundary:

- this sample used a fake local launcher/process for artifact-boundary proof
- it proves external artifact landing
- it does not prove live Claude subprocess robustness

### 3. Metadata coverage is materially present across the main automated lanes

Observed metadata fields in code/scripts:

- `lane`
- `reasoning_mode`
- `sandbox_identity`
- `sandbox_kind`
- `capability_profile`
- `write_scope`
- `network_policy`

Material evidence:

- Claude worker:
  - [worker.py](/D:/code/MyAttention/services/api/claude_worker/worker.py)
  - [test_claude_worker.py](/D:/code/MyAttention/services/api/tests/test_claude_worker.py)
- OpenClaw wrappers:
  - [openclaw_delegate.py](/D:/code/MyAttention/scripts/acpx/openclaw_delegate.py)
  - [run_file_delegation.py](/D:/code/MyAttention/scripts/acpx/run_file_delegation.py)
- qoder path:
  - [create_task_bundle.py](/D:/code/MyAttention/scripts/qoder/create_task_bundle.py)
  - [create_review_bundle.py](/D:/code/MyAttention/scripts/qoder/create_review_bundle.py)
  - [qoder_delegate.py](/D:/code/MyAttention/scripts/qoder/qoder_delegate.py)
  - [run_task.py](/D:/code/MyAttention/scripts/qoder/run_task.py)

### 4. Reasoning-default claim is materially backed

Observed in `C:\Users\jiuyou\.openclaw\openclaw.json`:

- `thinkingDefault = high`

Observed in Claude worker code:

- `DEFAULT_REASONING_MODE = "high"`

## Unproven Boundary

The following are still not proven as hard enforcement:

- hard write blocking
- hard network blocking
- per-run sandbox lifecycle isolation
- runtime-bound capability enforcement

Current evidence only supports:

- path/workspace isolation
- externalized run-root configuration
- metadata/audit coverage

It does not support claiming real sandbox enforcement.

It also does not support claiming:

- live Claude subprocess hang-proof execution from this artifact sample alone

## Evidence Checked

Configuration and filesystem:

- `C:\Users\jiuyou\.openclaw\openclaw.json`
- `D:\code\_agent-runtimes\openclaw-workspaces\...`
- `D:\code\_agent-runtimes\claude-worker\runs`
- `D:\code\_agent-runtimes\claude-worker\runs\20260411T085746-ddf50d4d`

Code and tests:

- [worker.py](/D:/code/MyAttention/services/api/claude_worker/worker.py)
- [test_claude_worker.py](/D:/code/MyAttention/services/api/tests/test_claude_worker.py)
- [openclaw_delegate.py](/D:/code/MyAttention/scripts/acpx/openclaw_delegate.py)
- [run_file_delegation.py](/D:/code/MyAttention/scripts/acpx/run_file_delegation.py)
- [create_task_bundle.py](/D:/code/MyAttention/scripts/qoder/create_task_bundle.py)
- [create_review_bundle.py](/D:/code/MyAttention/scripts/qoder/create_review_bundle.py)
- [qoder_delegate.py](/D:/code/MyAttention/scripts/qoder/qoder_delegate.py)
- [run_task.py](/D:/code/MyAttention/scripts/qoder/run_task.py)
- [sync_isolated_workspaces.ps1](/D:/code/MyAttention/scripts/sync_isolated_workspaces.ps1)

Supporting historical result:

- [IKE_REPOSITORY_RESTRUCTURE_PHASE1_RESULT_2026-04-09.md](/D:/code/MyAttention/docs/IKE_REPOSITORY_RESTRUCTURE_PHASE1_RESULT_2026-04-09.md)

## Controller Judgment

- recommendation:
  - `accept_with_changes`

## Why

The harness line can now truthfully claim:

- isolated OpenClaw workspaces
- externalized Claude worker run-root by default
- external artifact landing under the Claude worker external run-root
- shared metadata coverage across Claude/OpenClaw/qoder

But it still cannot truthfully claim:

- enforced write/network blocking
- full sandbox lifecycle enforcement

And the Claude external artifact boundary still needs one fresh sample run
under a live Claude subprocess path if the project later wants stronger
subprocess-level claims than this fake-process artifact proof.

## Next Hardening Step

1. if needed, produce one live Claude subprocess sample under the external root
2. keep distinguishing artifact proof from subprocess robustness proof
3. only then consider stronger claims about execution hardening
