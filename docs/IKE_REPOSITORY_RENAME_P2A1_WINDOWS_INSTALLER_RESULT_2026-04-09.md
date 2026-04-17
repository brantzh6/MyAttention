# IKE Repository Rename P2-A1 Windows Installer Result

Date: 2026-04-09

## Scope

First narrow phase-2 rename patch:

- parameterize the Windows service installer
- stop treating the old root and old service names as the only valid defaults

## Files Changed

- `D:\code\MyAttention\scripts\services\windows\install-app-services.ps1`

## What Changed

The Windows installer script now:

- defaults `RepoRoot` to:
  - `D:\code\IKE`
- defaults `ServicePrefix` to:
  - `IKE`
- exposes:
  - `BindHost`
  - `ApiPort`
  - `WebPort`
- derives service names from `ServicePrefix` instead of hardcoding:
  - `MyAttentionApi`
  - `MyAttentionWeb`
  - `MyAttentionWatchdog`

This keeps the script usable for the future canonical root without forcing a live service rewrite today.

## Validation

- PowerShell parser validation:
  - `powershell_parse_ok`

## Truthful Judgment

- recommendation:
  - `accept_with_changes`

## Remaining Work

This does not yet rewrite:

- WinSW XML names and paths
- Linux systemd unit names/paths
- macOS plist labels/paths

It is only the first narrow service/deployment normalization step.
