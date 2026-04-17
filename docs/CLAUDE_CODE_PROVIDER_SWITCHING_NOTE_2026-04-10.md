# Claude Code Provider Switching Note

Date: 2026-04-10
Status: active operator note

## Purpose

Record the current Claude Code provider switching method and the current model
selection guidance so this operational detail does not remain only in chat
history.

## Current Practical Guidance

Default routine Claude Code use should still prefer:

- latest `qwen3.6`

But the current Claude Code setup now also supports a stronger
backend/business-logic lane:

- `glm-5.1` coding plan

This lane should be considered for:

- high-difficulty backend tasks
- heavier business-logic implementation
- multi-file server-side coding where stronger reasoning is useful

## Provider Lookup

Configured Claude Code providers can be listed with:

```powershell
C:\Users\jiuyou\.claude\skills\cc-switch --app claude provider list
```

## Known Provider Guidance

### `bailian-cp`

Current meaning:

- primary provider family for routine switching
- includes `glm-5`
- can switch at runtime between:
  - `qwen3.6`
  - `kimi`

Use this when:

- the task can stay on the normal automatable Claude Code lane
- you want routine model switching without changing to the isolated
  `glm-5.1` provider

### `zhipu-cp`

Current meaning:

- dedicated `glm-5.1` lane

Use this when:

- the task is a harder backend or business-logic coding packet
- you explicitly want the `glm-5.1` coding-plan lane

Important constraint:

- this provider must be switched manually before launching Claude Code

## Provider Switch Commands

Switch back to the default provider:

```powershell
C:\Users\jiuyou\.claude\skills\cc-switch --app claude provider switch default
```

Switch to the current `zhipu-cp` provider by id:

```powershell
C:\Users\jiuyou\.claude\skills\cc-switch --app claude provider switch f312d0a2-eb60-47d5-af53-67e55a516675
```

Then launch Claude Code.

## Controller Working Rule

When shaping delegated Claude Code packets:

1. default to latest `qwen3.6` for routine coding/review packets
2. consider `glm-5.1` after manual provider switch for harder backend and
   business-logic implementation
3. keep `kimi` available as an alternate routine lane when useful
4. record the chosen lane/model in the task brief when the model choice is
   part of the risk-control strategy

## Truth Boundary

This note records operator workflow only.

It does not mean:

- provider switching is already automated by the controller
- Claude Code has become the main controller
- model quality differences have already been benchmarked enough to rewrite the
  broader routing policy
