# IKE Automated Reasoning Baseline

Date: 2026-04-09

## Purpose

Record the current default reasoning / thinking-depth baseline for the automatable delivery chain.

This is a controller execution rule, not a model-comparison essay.

## Current Verified Facts

From local OpenClaw config:

- provider model registry marks these as reasoning-capable:
  - `qwen3.6-plus`
  - `glm-5`
  - `kimi-k2.5`
- current OpenClaw defaults:
  - `agents.defaults.thinkingDefault = high`
  - each project agent also currently has:
    - `thinkingDefault = high`

Current project agents:

- `myattention-coder`
  - model: `bailian-coding-plan/qwen3.6-plus`
- `myattention-reviewer`
  - model: `bailian/qwen3.6-plus`
- `myattention-kimi-review`
  - model: `bailian-coding-plan/kimi-k2.5`

From local Claude worker:

- default worker model is now:
  - `qwen3.6-plus`
- worker still allows explicit per-packet model override

## Controller Baseline

Default routine model preference:

- coding:
  - `qwen3.6-plus`
- review:
  - `qwen3.6-plus` or `kimi-k2.5`
- backend/complex multi-file packets:
  - allow explicit `glm-5`

Default thinking-depth baseline:

- keep `high` for:
  - coding with semantic risk
  - review
  - evolution
  - architecture-sensitive analysis
- allow lower depth only for:
  - smoke probes
  - tiny mechanical edits
  - non-semantic operational checks

## Non-Goal

This note does not claim:

- that all provider-side reasoning controls are fully exposed and independently verified
- that `qwen3.6-plus`, `glm-5`, and `kimi-k2.5` are interchangeable
- that routine coding lane comparison is complete

## Recommendation

- `accept`
