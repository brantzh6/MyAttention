# IKE Agent Harness Reasoning Policy

Date: 2026-04-09
Status: accept_with_changes

## Purpose

Lock down the controller rule for reasoning / thinking-depth selection across the routine automated delivery chain.

This is not a model-quality ranking.
It is a dispatch policy for keeping important delegated work at the highest available automated reasoning depth by default.

## Current Reasoning-Capable Automated Pool

- `OpenClaw / qwen3.6-plus`
- `OpenClaw / glm-5`
- `OpenClaw / kimi-k2.5`
- `Claude worker / qwen3.6-plus`
- `Claude worker / glm-5`
- `Claude worker / kimi-k2.5`

## Default Controller Rule

Routine automated lanes should not leave reasoning mode implicit for important packets.

Default:

- coding:
  - `high`
- review:
  - `high`
- evolution:
  - `high`
- testing:
  - `high`

Controller interpretation:

- `high` is the default for normal delegated work
- lower modes are exceptions, not the baseline

## When To Force High

Use `high` reasoning / thinking depth for:

- multi-file coding packets
- semantic-boundary changes
- runtime truth / state-machine / review-provenance work
- review packets
- evolution packets
- comparison packets intended to judge lane quality
- research packets where synthesis matters more than extraction speed

## When Medium Is Enough

Use `medium` for:

- bounded test fixes
- compile/test/validation helpers
- low-risk visible identity normalization
- narrow adapter or route-surface work where semantics are already settled

## When Low Is Acceptable

Use `low` only for:

- mechanical probes
- metadata inspection
- repeatable smoke checks
- trivial output formatting tasks

Do not use `low` for coding, review, testing, or evolution packets that can affect controller judgment.

## Model-Specific Practical Preference

### OpenClaw

- routine coding:
  - prefer latest `qwen3.6-plus`
- backend / deeper engineering packets:
  - `glm-5` remains valid in parallel
- review / synthesis:
  - `kimi-k2.5` remains valid for long-context review

### Claude worker

- default local routine model:
  - `qwen3.6-plus`
- switch explicitly to:
  - `glm-5` for backend-heavy engineering packets
  - `kimi-k2.5` for long-context review/synthesis packets

## Controller Discipline

- Reasoning mode should be explicit in important delegated packets.
- Do not silently downshift a packet from `high` to `medium` just to save time or tokens.
- If a packet is intentionally cheapened for probe purposes, mark it as a probe and do not compare it against a full-quality lane result.

## Recommendation

`accept_with_changes`
