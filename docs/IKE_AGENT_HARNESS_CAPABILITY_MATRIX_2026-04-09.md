# IKE Agent Harness Capability Matrix

Date: 2026-04-09
Status: accept_with_changes

## Purpose

Record the current real execution-capability baseline for the routine automated
delivery chain.

This is not the final hardened policy.
It is the truthful starting point for the next harness-enforcement phase.

## Current Routine Lanes

### Codex / GPT controller

Role:

- controller
- review gate
- acceptance
- brief authoring
- architectural judgment

Current truth:

- not treated as the routine coding lane
- may still perform narrow direct patches when needed

### OpenClaw coder lane

Current configured model:

- `bailian-coding-plan/qwen3.6-plus`

Current thinking baseline:

- `thinkingDefault = high`

Current workspace:

- isolated external workspace
- `D:\code\_agent-runtimes\openclaw-workspaces\myattention-coder`

Expected scope:

- bounded coding
- multi-file implementation
- routine coding packets

### OpenClaw reviewer lane

Current configured model:

- `bailian/qwen3.6-plus`

Current thinking baseline:

- `thinkingDefault = high`

Current workspace:

- isolated external workspace
- `D:\code\_agent-runtimes\openclaw-workspaces\myattention-reviewer`

Expected scope:

- bounded review
- supplemental review
- fast routine review

### OpenClaw kimi review lane

Current configured model:

- `bailian-coding-plan/kimi-k2.5`

Current thinking baseline:

- `thinkingDefault = high`

Current workspace:

- isolated external workspace
- `D:\code\_agent-runtimes\openclaw-workspaces\myattention-kimi-review`

Expected scope:

- long-context review
- synthesis
- difficult review packets

### Claude worker lane

Current default model:

- `qwen3.6-plus`

Current run-root:

- `D:\code\_agent-runtimes\claude-worker\runs`

Current truth:

- coding and review lane is usable
- durable completion reliability is still not fully hardened
- result projection still partially depends on repo-local harness result paths

## Current Capability Truth

### OpenClaw

Current strengths:

- reasoning-capable routine models are explicitly configured
- isolated workspaces are already in place
- high-thinking default is already in place

Current gap:

- repo-level evidence does not yet show a lane-specific tool/capability deny/allow
  matrix comparable to a hardened sandbox policy

### Claude worker

Current strengths:

- external run-root
- durable run artifacts
- coding/review result normalization
- explicit run metadata

Current gap:

- local Claude permission allowlist is still broad
- current local settings include destructive/process/network-capable operations
- this means path isolation is ahead of capability hardening

## Immediate Policy Direction

### What should remain high-reasoning by default

- OpenClaw coding lane
- OpenClaw review lane
- OpenClaw kimi review lane
- Claude worker coding lane
- Claude worker review lane

### What should become more explicit next

1. lane-specific allowed tools
2. lane-specific destructive-command rules
3. write-boundary rules
4. network policy
5. detached completion / finalization requirements

## Controller Judgment

Current execution baseline is strong enough for:

- routine delegated coding
- routine delegated review
- comparison experiments

But not yet strong enough to claim:

- full per-run sandbox enforcement
- narrow hardened capability policy
- unattended closure reliability for every lane
