# IKE Platform Neutralization Audit

Date: 2026-04-11
Status: controller audit

## Purpose

Record the current Windows-heavy surfaces that should be reduced before the
development environment moves to Linux and before runtime/harness paths are
treated as stable cross-platform baselines.

## Controller Judgment

The project already has cross-platform intent in several deployment and runtime
documents, but the active harness and local validation chain still contain
meaningful Windows-specific seams.

Current rule:

- Python should be the primary implementation surface for runtime and harness
  behavior
- shell wrappers may remain thin OS adapters
- PowerShell and `.cmd` behavior must not be the canonical contract

## Current Audit Summary

### 1. Active Windows-heavy runtime/harness seams

- `services/api/claude_worker/worker.py`
  - resolves `.cmd` on Windows
  - uses `taskkill` for detached abort
  - currently depends on Windows CLI behavior for real Claude runs
- `scripts/acpx/openclaw_delegate.py`
  - resolves `acpx.cmd` from `%APPDATA%\\npm`
- `scripts/services/windows/*`
  - expected and intentionally Windows-specific

### 2. Cross-platform intent already exists

- deployment design documents already say startup and health checks should be
  cross-platform
- Linux and macOS service templates already exist under `scripts/services`
- documentation already states PowerShell should not be the main
  implementation surface

### 3. Current mismatch

The design direction is cross-platform, but some practical execution paths are
still being proven through Windows-only mechanics.

That mismatch is acceptable temporarily for local development, but it should
not be treated as the long-term runtime or harness baseline.

## Immediate Risk Areas

### Claude worker

- real Windows `claude.cmd` invocation is currently a live gap
- current prompt delivery path is not yet proven as cross-platform stable
- detached finalize semantics are not yet strong enough to claim durable
  completion under owner exit

### Service/process inspection

- Windows-specific process shape work has been necessary for local proof
- those rules must remain clearly scoped as local Windows proof rules, not
  universal runtime semantics

### Delegation wrappers

- OpenClaw / acpx wrapper discovery still assumes Windows npm layout in some
  places
- these should move toward explicit binary configuration or Python-managed
  resolution where possible

## What Must Stay Windows-Specific

These are acceptable OS adapters, not architectural problems by themselves:

- `scripts/services/windows/*`
- WinSW XML templates
- PowerShell install/uninstall wrappers
- narrow Windows-only local service bootstrap guidance

## What Must Become Platform-Neutral

- delegated prompt delivery
- run artifact lifecycle / finalization
- controller-facing harness result projection
- agent binary resolution policy
- process-state truth and status transitions
- validation commands used as canonical acceptance evidence

## P1 Neutralization Queue

1. Treat Python stdin/file-based prompt delivery as the preferred Claude worker
   contract instead of Windows command-line prompt passing.
2. Narrow Windows-specific process management to tiny helper branches only.
3. Make Linux-first validation a formal acceptance layer for harness/runtime
   claims.
4. Separate `local Windows proof workaround` from `cross-platform core` in
   result docs.
5. Keep service templates cross-platform, but keep shell scripts thin.

## Current Recommendation

`accept_with_changes`

Reason:

- cross-platform intent is already strong
- but the live harness/runtime execution path is not yet neutralized enough to
  support a Linux cutover without targeted hardening
