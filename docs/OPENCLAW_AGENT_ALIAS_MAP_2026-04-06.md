# OpenClaw Agent Alias Map 2026-04-06

## Purpose

This note records the intended alias-to-agent mapping for local OpenClaw
delegation in `D:\code\MyAttention`.

It exists to prevent semantic drift where alias names suggest one model or
role while actually routing to another.

## Canonical Alias Map

- `openclaw-coder`
  - compatibility/coder entry
  - routes to local command:
    - `openclaw-myattention-coder.cmd`
  - underlying OpenClaw agent:
    - `myattention-coder`
  - current model:
    - `bailian/qwen3.6-plus`

- `openclaw-qwen`
  - legacy compatibility alias
  - currently routes to the same entry as:
    - `openclaw-coder`
  - important:
    - name is historical only
    - it is not guaranteed to be backed by a Qwen model

- `openclaw-glm`
  - dedicated coding ACP session
  - routes to:
    - `agent:myattention-glm-coder:main`
  - underlying OpenClaw agent:
    - `myattention-glm-coder`

- `openclaw-kimi`
  - dedicated Kimi review/evolution ACP session
  - routes to:
    - `agent:myattention-kimi-review:main`
  - underlying OpenClaw agent:
    - `myattention-kimi-review`
  - current model:
    - `modelstudio/kimi-k2.5`

- `openclaw-kimi-review`
  - explicit alias for the same route as:
    - `openclaw-kimi`

- `openclaw-reviewer`
  - generic reviewer ACP session
  - routes to:
    - `agent:myattention-reviewer:main`
  - underlying OpenClaw agent:
    - `myattention-reviewer`
  - current model:
    - `bailian/qwen3.6-plus`

## Operational Guidance

- Prefer:
  - `openclaw-glm` for bounded coding packets
  - `openclaw-kimi` for bounded review/evolution packets
- Keep:
  - `openclaw-reviewer` as a generic reviewer fallback on `qwen3.6-plus`
- Treat:
  - `openclaw-qwen` as legacy compatibility only
- Prefer:
  - `openclaw-coder` when the goal is “generic coder entry” on `qwen3.6-plus`

## Preflight Rule

Before relying on a changed alias map for important packet execution:

1. run a minimal `OK` probe
2. confirm the alias resolves to the intended agent/session
3. confirm the session uses the intended provider/model route

## Controller Judgment

The alias layer should describe actual execution roles, not old historical
model names. Compatibility aliases may remain, but canonical usage should
prefer semantically accurate names with a clear split between:

- primary lanes:
  - `openclaw-glm`
  - `openclaw-kimi`
- backup lanes:
  - `openclaw-coder`
  - `openclaw-reviewer`
