# IKE Repository Rename P2-A3 Linux Mac Templates Result

Date: 2026-04-09

## Scope

Third narrow phase-2 rename patch:

- normalize Linux systemd service templates
- normalize macOS launchd plist templates

## Files Changed

- `D:\code\MyAttention\scripts\services\linux\myattention-api.service`
- `D:\code\MyAttention\scripts\services\linux\myattention-watchdog.service`
- `D:\code\MyAttention\scripts\services\macos\com.myattention.api.plist`
- `D:\code\MyAttention\scripts\services\macos\com.myattention.watchdog.plist`

## What Changed

Linux templates now use:

- service descriptions with `IKE`
- working paths under `/opt/ike`
- log paths under `/var/log/ike`
- watchdog dependency renamed to `ike-api.service`

macOS templates now use:

- `com.ike.api`
- `com.ike.watchdog`
- working/runtime paths under `/opt/ike`

## Validation

- manual systemd file inspection passed
- XML parse check passed for both macOS plist files

## Truthful Judgment

- recommendation:
  - `accept_with_changes`

## Remaining Work

Still open in the broader rename/cutover track:

- decide whether template filenames themselves should later be renamed
- local runtime config normalization
- controller/delegation script normalization
- final controller cutover from `D:\code\MyAttention` to `D:\code\IKE`
