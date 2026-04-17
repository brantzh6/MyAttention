# IKE Repository Rename Phase 2 Plan

Date: 2026-04-09

## Goal

Start final rename normalization with the narrowest high-value bucket first.

Phase 2 should not rename the whole repository in one pass.

It should start with:

- service/deployment artifacts
- launch-path references
- local runtime configuration that directly affects controller live proof

## Why This Bucket First

This bucket has:

- high operational value
- narrow file scope
- relatively clear rollback
- direct impact on controller/service truth

It is safer than starting with:

- broad frontend branding
- mixed backend semantic strings
- doc-wide rename sweeps

## Planned Packet Order

### Packet P2-A

Service/deployment artifact normalization

Target types:

- WinSW XML
- Linux systemd units
- macOS plist
- Windows install scripts

Primary outcome:

- old `MyAttention*` service identifiers become `IKE*` equivalents where safe
- launch paths align with the future canonical root model

### Packet P2-B

Local runtime config normalization

Target types:

- `config/runtime/*.toml`
- `infrastructure/docker-compose.yml`

Primary outcome:

- local process and compose assumptions stop hardcoding the old root/name where not required

### Packet P2-C

Controller/delegation script normalization

Target types:

- `scripts/acpx/*.py`
- `scripts/qoder/*.py`
- sync helpers

Primary outcome:

- automation and agent launch scripts stop treating `D:\code\MyAttention` as the only canonical root

## Truthful Non-Goals

Phase 2 will not yet:

- rewrite all docs
- rewrite all backend identity strings
- rewrite all frontend branding text
- cut controller over to `D:\code\IKE`

## Controller Judgment

Recommendation:

- `accept`

This is the next safest move after phase-1 isolation and cutover-readiness cleanup.
