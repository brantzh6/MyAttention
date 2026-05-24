# Result: delegated lane repair for spawn/lock failures

Date: 2026-05-24
Owner lane: nonsandboxed local operator/manual shell lane
Requester: codex-controller

## summary

Partially repaired the delegated execution substrate enough to unblock local
Package A execution and Codex bridge smoke runs.

Completed:

- Cleaned stale detached Codex CLI app-server processes.
- Cleaned stale ACP/acpx Node delegate processes.
- Verified git ref lock/write path works.
- Verified Node child process spawn works.
- Verified Claude CLI spawn works.
- Verified `npm --prefix services/web run build` works.
- Fixed the OpenClaw->Codex bridge lease check so a detached lease with a dead
  `codex_pid` no longer blocks future bridge runs until timeout.
- Verified bridge smoke returns `CODEX_BRIDGE_SMOKE_OK`.

Not fully repaired:

- `C:\Users\jiuyou\.codex\skills\.system` remains ACL-broken.
- A clean isolated `CODEX_HOME` avoids the ACL issue but lacks authentication
  and returns 401.

## what_changed

Process cleanup:

- Stopped stale `codex.exe app-server --listen stdio://` processes under
  `C:\Users\jiuyou\AppData\Local\OpenAI\Codex\bin\...\codex.exe`.
- Stopped stale `@zed-industries/claude-agent-acp`,
  `@anthropic-ai/claude-agent-sdk`, and `acpx` Node processes.
- Preserved the Codex desktop app, OpenClaw gateway, and `/control` web server.

Code change:

- `scripts/ops/openclaw_codex_bridge.py`
  - Added PID liveness check.
  - `running_detached` leases with `codex_pid` now count as active only while
    the PID is still running.

## validation_run

- `git update-ref refs/heads/codex/lane-repair-smoke <HEAD>` and delete:
  passed.
- Node child process smoke:
  passed; printed `NODE_CHILD_SPAWN_OK`.
- Claude CLI smoke:
  passed; printed `CLAUDE_SPAWN_OK`.
- `npm --prefix services/web run build`:
  passed.
- `python -m py_compile scripts\ops\openclaw_codex_bridge.py scripts\ops\validate_openclaw_pm_digest.py`:
  passed.
- `python scripts\ops\openclaw_codex_bridge.py --mode smoke --source codex-controller --reason bridge_smoke_after_pid_liveness --timeout-seconds 180 --lease-seconds 600`:
  passed with result `ops/bridge/runs/openclaw_codex_20260524_080831.json`.
- Smoke output:
  `tasks/codex/openclaw_codex_controller_run_openclaw_codex_20260524_080831.md`
  contains `CODEX_BRIDGE_SMOKE_OK`.

## known_risks

- Codex CLI still logs system skills errors because
  `C:\Users\jiuyou\.codex\skills\.system` cannot be read, moved, reset, or
  taken over by the current process.
- The Codex bridge can run despite that warning, but skills dependent on the
  system skills directory may be unavailable in bridge-launched Codex runs.
- An isolated `CODEX_HOME` is not currently usable for bridge runs because it
  lacks authentication.
- The repair does not solve OpenClaw `myattention-coder` identity/session lock
  EPERM if that is rooted in OpenClaw workspace ACLs.

## recommendation

accept_with_changes

Local execution and bridge smoke are usable again, and the immediate Package A
save-state work is unblocked. Remaining work should be tracked separately:

1. Repair or recreate the global Codex `.system` skills cache with correct ACLs.
2. Validate OpenClaw `myattention-coder` after stale process cleanup.
3. Add a bridge/PM health check for detached lease PID liveness.

