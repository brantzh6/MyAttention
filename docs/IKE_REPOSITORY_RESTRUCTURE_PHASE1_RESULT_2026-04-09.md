# IKE Repository Restructure Phase 1 Result

Date: 2026-04-09

## Scope

Phase 1 executed the minimum safe isolation work before any in-place rename:

1. created a pre-migration git checkpoint
2. created a cold filesystem backup
3. created separate runtime/agent backups
4. created a parallel clean project root at `D:\code\IKE`
5. moved OpenClaw agents onto isolated workspaces
6. externalized the default Claude worker run root
7. added and validated a repeatable sync script for the parallel root and isolated workspaces

## What Was Executed

### 1. Git checkpoint

- branch:
  - `codex/pre-ike-restructure-2026-04-09`
- commit:
  - `02aa8a0`
- message:
  - `Checkpoint runtime and restructure baseline`

### 2. Cold backup

- created:
  - `D:\code\_backups\MyAttention-pre-ike-restructure-2026-04-09`
- note:
  - embedded Qdrant lock file `.lock` was excluded because it was held by the running process

### 3. Runtime / agent backups

- created:
  - `D:\code\_agent-runtimes\MyAttention-runtime-2026-04-09`
  - `D:\code\_agent-runtimes\MyAttention-openclaw-2026-04-09`
  - `D:\code\_agent-runtimes\MyAttention-codex-2026-04-09`
  - `D:\code\_agent-runtimes\MyAttention-memory-2026-04-09`

### 4. Parallel project root

- created:
  - `D:\code\IKE`
- copied:
  - project-core source and docs
- excluded:
  - `.git`
  - `.runtime`
  - `.openclaw`
  - `.codex`
  - `.claude`
  - `.qoder`
  - `memory`
  - `.venv`
  - embedded `qdrant`
  - cache/build directories

### 5. OpenClaw workspace isolation

- created isolated workspaces:
  - `D:\code\_agent-runtimes\openclaw-workspaces\myattention-coder`
  - `D:\code\_agent-runtimes\openclaw-workspaces\myattention-reviewer`
  - `D:\code\_agent-runtimes\openclaw-workspaces\myattention-kimi-review`
- rewrote `C:\Users\jiuyou\.openclaw\openclaw.json` workspaces from:
  - `D:\code\MyAttention`
- to:
  - the corresponding isolated workspace paths above

### 6. Claude worker run-root isolation

- changed default `ClaudeWorkerRuntime.run_root` from:
  - repo-local `.runtime\claude-worker\runs`
- to:
  - `D:\code\_agent-runtimes\claude-worker\runs`
- preserved default `result_root` at:
  - repo-local `.runtime\delegation\results`
- reason:
  - move heavy run artifacts out of the repo first without breaking current result/harness integration

### 7. Repeatable sync path

- added:
  - `D:\code\MyAttention\scripts\sync_isolated_workspaces.ps1`
- purpose:
  - sync controller-root project files into:
    - `D:\code\IKE`
    - isolated OpenClaw workspaces
- validation:
  - script executed successfully after excluding the live embedded Qdrant lock path

## Validation

- `python -m unittest tests.test_claude_worker`
  - `16 passed`
- `python -m compileall D:\code\MyAttention\services\api\claude_worker`
  - passed
- `powershell -ExecutionPolicy Bypass -File D:\code\MyAttention\scripts\sync_isolated_workspaces.ps1`
  - passed
- `C:\Users\jiuyou\.openclaw\openclaw.json | ConvertFrom-Json`
  - passed

## Truthful Current State

- OpenClaw agents no longer point at the shared project root in config.
- Claude worker new runs will default outside the repo.
- `D:\code\IKE` now exists as a clean parallel project root.
- legacy OpenClaw session history still exists under `C:\Users\jiuyou\.openclaw\agents\...\sessions`.
- current controller thread still operates in `D:\code\MyAttention`.
- this is not the final rename/cutover.

## Remaining Work

1. decide when controller moves from `D:\code\MyAttention` to `D:\code\IKE`
2. decide whether repo-local `.runtime\delegation\results` should stay project-local or also move out
3. normalize Claude worker result collision / detached completion hardening
4. decide whether old malformed backup directories under `D:\code\_agent-runtimes` should be cleaned up
5. reset or retire stale OpenClaw session state if it interferes with the new isolated workspaces

## Controller Judgment

- recommendation:
  - `accept_with_changes`
- why:
  - the dangerous shared-root workspace pattern has been materially reduced
  - but final project rename/cutover and stale session cleanup are still open
