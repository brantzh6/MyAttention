# IKE Repository Restructure Cutover Readiness

Date: 2026-04-09

## Purpose

This note records the first practical cutover-readiness scan after repository-restructure phase 1.

It answers:

- is `D:\code\IKE` now a clean parallel project root
- what still blocks final controller cutover
- what should be normalized before a true rename/switch

## Executed Checks

1. inspected the parallel root contents
2. confirmed OpenClaw config now points at isolated workspaces
3. confirmed Claude worker default run root is now externalized
4. inspected the new root for obvious runtime/build pollution
5. tightened the sync script exclusions
6. removed leaked runtime/build artifacts from `D:\code\IKE`
7. re-ran sync to confirm the clean baseline

## Clean-Root Result

`D:\code\IKE` is now a materially clean project root.

Confirmed absent after cleanup + resync:

- `D:\code\IKE\.runtime`
- `D:\code\IKE\.openclaw`
- `D:\code\IKE\memory`
- `D:\code\IKE\services\api\api.log`
- `D:\code\IKE\services\api\chat_debug.log`
- `D:\code\IKE\services\web\.next`

## Important Fixes Applied

### Sync script hardening

Updated:

- `D:\code\MyAttention\scripts\sync_isolated_workspaces.ps1`

New exclusions now include:

- `services\api\api.log`
- `services\api\chat_debug.log`
- `services\web\.next`

This prevents fresh runtime/build artifacts from being copied into:

- `D:\code\IKE`
- isolated OpenClaw workspaces

### OpenClaw isolation state

Confirmed in:

- `C:\Users\jiuyou\.openclaw\openclaw.json`

Current agent workspaces:

- `D:\code\_agent-runtimes\openclaw-workspaces\myattention-coder`
- `D:\code\_agent-runtimes\openclaw-workspaces\myattention-reviewer`
- `D:\code\_agent-runtimes\openclaw-workspaces\myattention-kimi-review`

### Claude worker isolation state

Confirmed by runtime helper import:

- default run root:
  - `D:\code\_agent-runtimes\claude-worker`

## Remaining Cutover Risks

1. controller thread still runs from `D:\code\MyAttention`
2. repo/docs/code still contain many historical `MyAttention` and `D:\code\MyAttention` references
3. stale OpenClaw session history still exists under:
   - `C:\Users\jiuyou\.openclaw\agents\...\sessions`
4. `.runtime\delegation\results` still remains repo-local for compatibility
5. final rename semantics are not yet normalized across docs, scripts, and route assumptions

## Truthful Judgment

- `D:\code\IKE` is now clean enough to be treated as the future canonical project root candidate
- but final controller cutover should still be treated as `accept_with_changes`
- the next safe step is:
  - normalize hardcoded name/path references
  - then choose a controller cutover point
