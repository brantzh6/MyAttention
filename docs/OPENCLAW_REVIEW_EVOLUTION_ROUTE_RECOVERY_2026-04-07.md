# OpenClaw Review/Evolution Route Recovery 2026-04-07

## Summary

The delegated review/evolution lane was not failing because of:

- review brief quality
- evolution packet scope
- timeout budget alone

It was failing because the actual local OpenClaw agent routing had drifted away
from the documented alias map.

The runtime impact was concrete:

- `R1-B2` review timed out without durable output
- `R1-B4` evolution timed out without durable output
- controller fallback had to carry the milestone

## Root Cause

Actual local configuration had drifted to:

- `myattention-kimi-review`
  - `bailian-coding-plan/kimi-k2.5`
- `myattention-reviewer`
  - `bailian-coding-plan/kimi-k2.5`

and both affected session metadata still carried:

- `authProfileOverride = bailian-coding-plan:default`

Observed failure mode:

- OpenClaw session status: `failed`
- OpenClaw session jsonl: `401 Incorrect API key provided`

So the real breakage was:

- local provider/auth route drift
- not packet semantics
- not lifecycle proof semantics

## Corrected Route

The actual corrected local split is now:

- `myattention-kimi-review`
  - `modelstudio/kimi-k2.5`
  - `authProfileOverride = modelstudio:default`

- `myattention-reviewer`
  - `bailian/qwen3.6-plus`
  - `authProfileOverride = bailian:default`

This matches the project alias contract:

- `openclaw-kimi`
  - dedicated review/evolution lane
- `openclaw-reviewer`
  - generic reviewer fallback

## Files Corrected

- `C:\Users\jiuyou\.openclaw\openclaw.json`
- `C:\Users\jiuyou\.openclaw\agents\myattention-kimi-review\sessions\sessions.json`
- `C:\Users\jiuyou\.openclaw\agents\myattention-reviewer\sessions\sessions.json`

## Verification

### Minimal probe

Both lanes now return `OK` through `openclaw_delegate.py` prompt-mode probes:

- `openclaw-kimi`
- `openclaw-reviewer`

### Real packet recovery

With the corrected route, real delegated results were recovered for:

- `R1-B2`
  - [D:\code\MyAttention\.runtime\delegation\results\ike-runtime-r1-b2-lifecycle-review-kimi.json](/D:/code/MyAttention/.runtime/delegation/results/ike-runtime-r1-b2-lifecycle-review-kimi.json)
- `R1-B4`
  - [D:\code\MyAttention\.runtime\delegation\results\ike-runtime-r1-b4-lifecycle-evolution-kimi.json](/D:/code/MyAttention/.runtime/delegation/results/ike-runtime-r1-b4-lifecycle-evolution-kimi.json)

This confirms the lane is again usable for:

- bounded review
- bounded evolution extraction

## Controller Judgment

The previous 2026-04-06 Kimi-fix note should now be treated as incomplete, not
canonical.

The truthful current state is:

- `openclaw-kimi` is healthy again on `modelstudio/kimi-k2.5`
- `openclaw-reviewer` is healthy again as the generic reviewer fallback on
  `bailian/qwen3.6-plus`
- `R1-B` no longer depends on controller fallback because of transport failure

## Prevention Rule

Before relying on a review/evolution lane for a milestone:

1. run a minimal `OK` probe
2. confirm the live provider/model route
3. confirm session metadata does not carry a stale auth override
4. only then run the real packet
