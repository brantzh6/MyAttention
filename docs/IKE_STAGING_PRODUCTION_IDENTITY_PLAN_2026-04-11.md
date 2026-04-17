# IKE Staging And Production Identity Plan

Date: 2026-04-11
Status: controller implementation baseline

## Purpose

Turn the governance policy into one concrete identity plan for:

- workspace roots
- ports
- service names
- database names
- Redis identity
- Qdrant identity
- runtime artifact roots

## Core Rule

`staging-runtime` and `prod-runtime` must differ at the identity level.

If they share the same root, port, database, cache, or vector namespace, they
are not truly separate environments.

## Recommended Environment Roots

### Controller Dev

- repo root:
  - `D:\code\MyAttention`
- role:
  - controller-dev

### Sandbox Evolution

- OpenClaw workspaces:
  - `D:\code\_agent-runtimes\openclaw-workspaces\...`
- Claude worker runs:
  - `D:\code\_agent-runtimes\claude-worker\runs`
- role:
  - sandbox-evolution

### Staging Runtime

- recommended root:
  - `D:\envs\IKE\staging`
- recommended repo or release payload root:
  - `D:\envs\IKE\staging\app`
- recommended runtime root:
  - `D:\envs\IKE\staging\.runtime`

### Production Runtime

- recommended root:
  - `D:\envs\IKE\prod`
- recommended repo or release payload root:
  - `D:\envs\IKE\prod\app`
- recommended runtime root:
  - `D:\envs\IKE\prod\.runtime`

## Port Policy

### Dev

- API:
  - `8000`
- Web:
  - `3000`

### Staging

- API:
  - `18000`
- Web:
  - `13000`

### Production

- API:
  - `28000`
- Web:
  - `23000`

## Service Naming Policy

### Infrastructure Services

Current legacy local infra names still exist in places:

- `MyAttentionPostgres`
- `MyAttentionRedis`

They should not be reused as the future universal naming pattern.

### Recommended Staging Application Service Names

- `IKEStagingApi`
- `IKEStagingWeb`
- `IKEStagingWatchdog`

### Recommended Production Application Service Names

- `IKEProdApi`
- `IKEProdWeb`
- `IKEProdWatchdog`

## Database Naming Policy

### Development

- DB name:
  - `ike_dev`

### Staging

- DB name:
  - `ike_staging`

### Production

- DB name:
  - `ike_prod`

## Redis Naming Policy

Redis should not be shared across dev, staging, and prod without strong
namespace isolation.

Preferred:

- separate Redis instances or ports

Minimum acceptable fallback:

- separate DB index plus explicit key prefix

Recommended prefixes:

- dev:
  - `ike:dev:`
- staging:
  - `ike:staging:`
- prod:
  - `ike:prod:`

## Qdrant / Vector Identity Policy

Qdrant should also separate environment identity.

Preferred:

- separate Qdrant storage roots or instances

Minimum acceptable fallback:

- collection names must be environment-qualified

Recommended collection prefixes:

- dev:
  - `ike_dev_*`
- staging:
  - `ike_staging_*`
- prod:
  - `ike_prod_*`

## Runtime Artifact Policy

Run artifacts, service logs, and validation artifacts must not be mixed.

### Staging

- `D:\envs\IKE\staging\.runtime\logs`
- `D:\envs\IKE\staging\.runtime\runs`
- `D:\envs\IKE\staging\.runtime\artifacts`

### Production

- `D:\envs\IKE\prod\.runtime\logs`
- `D:\envs\IKE\prod\.runtime\runs`
- `D:\envs\IKE\prod\.runtime\artifacts`

## Config Identity Policy

Each environment must own its own effective config file.

Recommended examples:

- dev:
  - `config/runtime/local-process.local.toml`
- staging:
  - `config/runtime/staging.local.toml`
- prod:
  - `config/runtime/prod.local.toml`

## Immediate Practical Meaning

This plan does not require all infra to be deployed today.

It does require that future setup work stop treating:

- one port set
- one database
- one Redis
- one Qdrant namespace
- one runtime artifact root

as if they were enough for all lifecycle stages.

## Recommendation

Use this identity plan as the default baseline for the next governance
implementation packet:

1. staging local-process profile
2. production local-process profile
3. environment-specific install or deploy scripts

Current config templates:

- [D:\code\MyAttention\config\runtime\staging.local.example.toml](/D:/code/MyAttention/config/runtime/staging.local.example.toml)
- [D:\code\MyAttention\config\runtime\prod.local.example.toml](/D:/code/MyAttention/config/runtime/prod.local.example.toml)
