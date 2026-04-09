# Claude Code Comparison And Hardening Pack

Date: 2026-04-09

## Purpose

This is the single-file controller pack for:

- current `Claude Code` lane status
- current comparison baseline versus `OpenClaw`
- next hardening requirements
- what should be delivered before the lane is upgraded

## Current Truth

`Claude Code` is now a **usable local coding/review substrate**.

It is not yet a fully routine unattended closure lane.

Current truthful label:

- `accept_with_changes`

## What Is Proven

### Proven

- bounded local coding can produce the right patch direction
- bounded local review can produce useful review artifacts
- local worker runtime exists and is test-backed
- core worker operations exist:
  - `start`
  - `wait`
  - `fetch`
  - `abort`
- durable run artifacts exist

### Not Yet Proven

- stable unattended final artifact completion for routine long-running runs
- hardened detached completion semantics
- routine independent delegated closure across all task types

## Current Comparison Baseline

Reference:

- [D:\code\MyAttention\docs\IKE_RUNTIME_OPENCLAW_VS_CLAUDE_CODING_BASELINE_2026-04-08.md](/D:/code/MyAttention/docs/IKE_RUNTIME_OPENCLAW_VS_CLAUDE_CODING_BASELINE_2026-04-08.md)

Current truthful comparison:

### `Claude Code`

Strengths:

- good bounded coding direction
- strong local execution flexibility
- useful local review lane candidate
- avoids OpenClaw transport drift

Current weakness:

- durable completion / `final.json` reliability is still weaker than desired

### `OpenClaw`

Strengths:

- routine API-backed execution path
- model switching across `Qwen3.6 Plus / GLM-5 / Kimi`
- better fit for repeatable packet execution when transport is healthy

Current weakness:

- route / alias / provider / session drift can break the lane

## Current Controller Rule

Use:

- `Claude Code`
  - as a local coding/review substrate
  - as a comparison lane
  - as a fallback when OpenClaw transport quality is suspect

- `OpenClaw`
  - as the normal automatable coding/review chain
  - with latest `Qwen3.6 Plus` preferred for Qwen-backed work

Do not yet claim:

- `Claude Code` has replaced OpenClaw as the default unattended long-task lane

## Required Hardening Work

Reference:

- [D:\code\MyAttention\docs\CLAUDE_WORKER_RUNTIME_HARDENING_REQUIREMENTS_2026-04-08.md](/D:/code/MyAttention/docs/CLAUDE_WORKER_RUNTIME_HARDENING_REQUIREMENTS_2026-04-08.md)

Highest-priority hardening:

1. durable completion reliability
2. detached abort / finalization truth
3. black-box CLI end-to-end tests
4. result collision / auditability safety

Latest additional review findings to absorb:

1. repeated `task_id` must not overwrite prior `.runtime/delegation/results/*.json`
2. detached abort must not claim success before actual child exit is confirmed

## Comparison Standard

When running `OpenClaw vs Claude Code` on the same packet, use these dimensions:

1. success rate
2. timeout rate
3. durable final artifact completion
4. patch boundedness
5. validation quality
6. controller acceptance cost

## Upgrade Condition

`Claude Code` can be upgraded from:

- usable local lane

to:

- routine delegated coding/review lane

only after:

- reliable final artifact completion
- stronger detached finalization truth
- stable end-to-end CLI evidence
- result storage that does not weaken audit history

## Recommended Next Packet Type For Comparison

Use a narrow bounded coding packet with:

- small file set
- non-trivial semantics
- real validation
- no architecture drift risk

Current recommended comparison class:

- runtime narrow hardening packets similar to `R2-G` slices

## Current Controller Recommendation

- continue using `Claude Code` in parallel
- keep hardening it
- do not make it the only main execution lane yet
- continue `OpenClaw vs Claude Code` comparisons using the standard metrics above
