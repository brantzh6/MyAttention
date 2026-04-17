# IKE Repository Rename P2-A4 Windows Uninstaller Result

Date: 2026-04-09
Status: accept_with_changes

## Summary

Normalized the Windows application service uninstall script so it no longer
assumes `MyAttention*` as the only valid application-layer service prefix.

## Files Changed

- `scripts/services/windows/uninstall-app-services.ps1`
- `scripts/services/windows/README.md`

## What Changed

- added `ServicePrefix = "IKE"` to `uninstall-app-services.ps1`
- uninstall service list is now derived from `ServicePrefix`
  - `IKEWatchdog`
  - `IKEWeb`
  - `IKEApi`
- Windows service README now documents both install and uninstall scripts
- README now explicitly records that the uninstall script also defaults to
  `ServicePrefix = IKE`

## Validation

- PowerShell parser validation:
  - `powershell_parse_ok`

## Known Risks

- this is parameterization only
- it does not migrate or remove any currently installed legacy
  `MyAttention*` services unless explicitly invoked with that prefix

## Recommendation

- `accept_with_changes`
