# OpenClaw Kimi Channel Fix 2026-04-06

## Summary

The `openclaw-kimi` reviewer/evolution channel was failing because the
reviewer agent was configured to use:

- `bailian-coding-plan/kimi-k2.5`

That provider/auth path was returning:

- `401 Incorrect API key provided`

The coding channel remained healthy because it used a different provider/model
path.

## Root Cause

The problem was not:

- prompt shape
- timeout length
- file delegation logic
- review packet structure

The problem was:

- `C:\Users\jiuyou\.openclaw\openclaw.json`
- agent definitions for:
  - `myattention-reviewer`
  - `myattention-kimi-review`

Both reviewer agents were pinned to:

- `bailian-coding-plan/kimi-k2.5`

Historical successful reviewer sessions showed the healthy path was:

- `modelstudio/kimi-k2.5`

## Fix Applied

Changed in:

- `C:\Users\jiuyou\.openclaw\openclaw.json`

Updated:

- `myattention-reviewer`
- `myattention-kimi-review`

From:

- `bailian-coding-plan/kimi-k2.5`

To:

- `modelstudio/kimi-k2.5`

Then reset the reviewer main session entry in:

- `C:\Users\jiuyou\.openclaw\agents\myattention-reviewer\sessions\sessions.json`

so the next run could start from a clean session using the corrected model
route.

## Verification

### Minimal probe

Verified:

- `openclaw-kimi` can now return `OK` through `openclaw_delegate.py --mode exec`

### Real packet recovery

Verified real delegated packets:

- `R1-A2` hardening review
  - output restored at:
    - `D:\code\MyAttention\.runtime\delegation\results\ike-runtime-r1-a2-hardening-review-kimi.json`

- `R1-A4` hardening evolution
  - output restored at:
    - `D:\code\MyAttention\.runtime\delegation\results\ike-runtime-r1-a4-hardening-evolution-kimi.json`

This confirms the Kimi channel is again usable for:

- bounded review
- bounded evolution extraction

## Prevention Rule

Before relying on a delegated reviewer/evolution channel, run a preflight:

1. minimal `OK` probe
2. confirm provider/model route
3. confirm no auth error in session jsonl
4. only then run the real packet

For `openclaw-kimi`, a valid route now means:

- reviewer agent resolves to `modelstudio/kimi-k2.5`

## Controller Judgment

The Kimi multi-agent path is no longer blocked.

Future runtime hardening can again use:

- coding leg via `openclaw-glm`
- review leg via `openclaw-kimi`
- evolution leg via `openclaw-kimi`

Testing still remains a separate concern and should not be collapsed into the
review channel.
