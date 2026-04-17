# IKE Repository Rename P2-B1 Runtime Config Result

Date: 2026-04-09

## Scope

First narrow phase-2 config normalization patch:

- local runtime config
- local runtime config example
- docker compose identity defaults

## Files Changed

- `D:\code\MyAttention\config\runtime\local-process.local.toml`
- `D:\code\MyAttention\config\runtime\local-process.local.example.toml`
- `D:\code\MyAttention\infrastructure\docker-compose.yml`

## What Changed

### Local process config

Kept current infrastructure service names intact:

- `MyAttentionPostgres`
- `MyAttentionRedis`

But updated application-facing defaults toward the future canonical identity:

- `IKEWeb`
- `IKEWatchdog`
- repo-local log paths now point at:
  - `D:\code\IKE\.runtime\logs\...`

### Local process example config

Updated example service names/log paths to:

- `IKEApi`
- `IKEWeb`
- `IKEWatchdog`
- `D:\code\IKE\.runtime\logs\...`

### Docker compose

Updated compose identity defaults from `myattention` to `ike`:

- container names
- database credentials / db name
- healthcheck user
- default network name

## Validation

- manual config inspection passed
- compose YAML remained structurally valid on inspection

## Truthful Judgment

- recommendation:
  - `accept_with_changes`

## Remaining Work

Still open in the broader rename/cutover track:

- controller/delegation script normalization
- backend/app identity strings
- frontend branding/path references
- final controller cutover
