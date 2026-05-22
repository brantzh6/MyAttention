# IKE Repository Rename P2-C1 Delegation Scripts Result

Date: 2026-04-09

## Scope

First narrow phase-2 delegation-script normalization patch:

- qoder task bundle generator
- qoder review bundle generator
- qoder delegate prompt
- acpx/OpenClaw delegate defaults

## Files Changed

- `D:\code\MyAttention\scripts\qoder\create_task_bundle.py`
- `D:\code\MyAttention\scripts\qoder\create_review_bundle.py`
- `D:\code\MyAttention\scripts\qoder\qoder_delegate.py`
- `D:\code\MyAttention\scripts\acpx\openclaw_delegate.py`

## What Changed

### qoder bundle generators

Removed hardcoded references to:

- `D:\code\MyAttention\docs\CURRENT_MAINLINE_HANDOFF.md`
- `D:\code\MyAttention\AGENTS.md`

These are now derived from `--cwd`, so bundle generation can follow the current controller root.

### qoder delegate prompt

The bounded delegate prompt no longer hardcodes `MyAttention`.

It now derives the project name from the working tree path.

### acpx/OpenClaw delegate

Default session name changed from:

- `myattention-coder`

to:

- `ike-coder`

## Validation

- `python -m compileall` for the four scripts passed
- `create_task_bundle.py` dry validation passed
- `create_review_bundle.py` dry validation passed
- temporary validation bundle artifacts were removed after verification

## Truthful Judgment

- recommendation:
  - `accept_with_changes`

## Remaining Work

Still open in the broader rename/cutover track:

- backend/app identity references
- frontend branding/path references
- final controller cutover
