# IKE Repository Rename P2-A2 WinSW Template Result

Date: 2026-04-09

## Scope

Second narrow phase-2 rename patch:

- normalize Windows WinSW templates
- normalize the Windows service-template README

## Files Changed

- `D:\code\MyAttention\scripts\services\windows\winsw\MyAttentionApi.xml`
- `D:\code\MyAttention\scripts\services\windows\winsw\MyAttentionWeb.xml`
- `D:\code\MyAttention\scripts\services\windows\winsw\MyAttentionWatchdog.xml`
- `D:\code\MyAttention\scripts\services\windows\README.md`

## What Changed

WinSW XML templates now point at the future canonical root and service names:

- `IKEApi`
- `IKEWeb`
- `IKEWatchdog`

Root/path assumptions now use:

- `D:\code\IKE`

The Windows README is now UTF-8, no longer mojibake, and now documents:

- `IKE` application-layer service names
- `D:\code\IKE` as the future default repo root
- `install-app-services.ps1` as the primary install entrypoint

## Validation

- XML parse check passed for all three WinSW templates
- PowerShell parser validation for `install-app-services.ps1` still passed

## Truthful Judgment

- recommendation:
  - `accept_with_changes`

## Remaining Work

Still open in the same bucket:

- Linux systemd unit rename/path normalization
- macOS plist rename/path normalization
- decision on when the Windows installed live services should actually be renamed
