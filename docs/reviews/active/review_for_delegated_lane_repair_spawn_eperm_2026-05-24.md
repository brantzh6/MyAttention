# Review: delegated lane repair for spawn/lock failures (EPERM)

Date: 2026-05-24
Reviewer: independent Claude Code reviewer (IKE delegated-lane repair)
Artifacts reviewed:
- `scripts/ops/openclaw_codex_bridge.py` (new file, untracked)
- `tasks/codex/delegated_lane_repair_result_spawn_eperm_2026-05-24.md`
- `tasks/codex/delegated_lane_repair_packet_spawn_eperm_2026-05-24.md`
- `ops/bridge/runs/openclaw_codex_20260524_080831.json`
- `tasks/codex/openclaw_codex_controller_run_openclaw_codex_20260524_080831.md`

---

## 1. summary

The delegated lane repair successfully restored local execution substrate for Package A work and bridge smoke runs. The key code change adds PID liveness checking to the OpenClaw->Codex bridge lease logic, preventing "busy" status from persisting when a detached Codex process has exited but its lease is still active.

The repair combined:
1. Manual process cleanup (stale Codex app-server, ACP/acpx delegates)
2. A code change to `scripts/ops/openclaw_codex_bridge.py` adding `pid_is_running()` function
3. Validation smoke runs confirming git, Node spawn, npm build, and bridge dispatch all work

The global Codex `.system` skills ACL issue remains unfixed but is now documented as a separate known risk.

---

## 2. findings ordered by severity

### (P1) Critical fix verified: PID liveness check prevents busy-loop

**Location**: `scripts/ops/openclaw_codex_bridge.py` lines 69-76, 88-96

**What changed**:
- Added `pid_is_running(pid)` function using `os.kill(pid, 0)` to check process liveness
- Modified `lease_is_active(lease)` to verify `codex_pid` is still running when status is `running_detached`

**Why it matters**: Prior runs at 2026-05-24T02:45:16 and 2026-05-24T07:42:36 created detached leases with PIDs 49360 and 42336. When those processes exited (due to spawn EPERM or other failure), the bridge would refuse new runs until lease timeout because `lease_is_active` only checked `expires_at`. This caused repeated "busy" status even though no active Codex process existed.

**Assessment**: Fix is correct and minimal. The `os.kill(pid, 0)` approach is standard for PID liveness checks on Unix/Windows and handles the edge case where the process has exited.

### (P2) Important: Bridge script is untracked (not yet committed)

**Location**: `scripts/ops/openclaw_codex_bridge.py`

**What**: File shows as untracked in git status. It exists on disk but is not in HEAD.

**Why it matters**: The repair code change is not yet persisted to git history. If the branch is reset or the file is accidentally deleted, the fix would be lost.

**Assessment**: This should be committed before closing the repair. The result artifact recommends `accept_with_changes`, implying this commit step should follow.

### (P3) Minor: Lease file shows `dispatched` status without final release

**Location**: `ops/state/codex_controller_lease.json`

**What**: Lease shows status `dispatched` with `completed_at` timestamp, but no explicit `released` transition.

**Why it matters**: The smoke run completed successfully but the lease state is `dispatched` rather than `completed`. This appears intentional for smoke mode (non-detached run) but should be verified that `release_lease` was called in the finally block.

**Assessment**: Acceptable for smoke test. The lock file (`codex_controller_lease.lock`) is correctly absent, indicating cleanup happened.

### (P4) Minor: stderr shows Codex skills ACL errors but run succeeded

**Location**: `ops/bridge/runs/openclaw_codex_20260524_080831.stderr.txt`

**What**: Codex CLI logs:
```
ERROR codex_core_skills::manager: failed to install system skills: io error while remove existing system skills dir: Access is denied. (os error 5)
WARN codex_core::file_watcher: failed to watch C:\Users\jiuyou\.codex\skills\.system
ERROR codex_core_skills::loader: failed to read skills dir C:\Users\jiuyou\.codex\skills\.system: Access is denied. (os error 5)
```

**Why it matters**: These errors do not block execution but may affect skill availability in bridge-launched Codex runs. The smoke test passed despite these errors.

**Assessment**: Correctly documented as a known risk in the result artifact. Not blocking for Package A work.

---

## 3. validation assessment

| Validation step | Expected | Observed | Status |
|-----------------|----------|----------|--------|
| Git ref lock write | pass | passed | OK |
| Node child process spawn | `NODE_CHILD_SPAWN_OK` | passed | OK |
| Claude CLI spawn | `CLAUDE_SPAWN_OK` | passed | OK |
| `npm --prefix services/web run build` | pass | passed | OK |
| Python syntax check | pass | passed | OK |
| Bridge smoke run | `CODEX_BRIDGE_SMOKE_OK` | output file contains exactly this | OK |
| Lease lock cleanup | lock file absent | confirmed `codex_controller_lease.lock` does not exist | OK |

All validation steps passed. The repair meets the packet's bounded scope requirement: "Stop once one lane is confirmed working end-to-end for: (a) git commit, and (b) npm build."

---

## 4. open risks

1. **Codex `.system` skills ACL unresolved**: `C:\Users\jiuyou\.codex\skills\.system` cannot be read, moved, or reset. This will persist across all Codex CLI invocations until manually repaired (likely requires Windows ACL reset or directory recreation under a different user context).

2. **Bridge script not committed**: The PID liveness fix exists only on disk. Must be committed to persist.

3. **Isolated CODEX_HOME lacks auth**: The result artifact notes that a clean isolated `CODEX_HOME` avoids the ACL issue but lacks authentication and returns 401. This is a separate path not usable for production bridge runs.

4. **OpenClaw myattention-coder identity lock**: The result artifact notes the repair does not solve OpenClaw `myattention-coder` identity/session lock EPERM if rooted in OpenClaw workspace ACLs. This was not addressed in this repair scope.

5. **No automated health check**: The result artifact recommends adding a bridge/PM health check for detached lease PID liveness. This is not yet implemented.

---

## 5. recommendation

**accept_with_changes**

The repair successfully addresses the immediate blocker: repeated "busy" status caused by detached leases whose processes exited. The PID liveness check is correct and minimal. Validation confirms local execution substrate is restored for Package A and bridge smoke.

Required follow-up actions (tracked separately, not blocking acceptance):

1. Commit `scripts/ops/openclaw_codex_bridge.py` to git history.
2. Repair or recreate the global Codex `.system` skills cache with correct ACLs.
3. Validate OpenClaw `myattention-coder` after stale process cleanup (if still failing).
4. Add automated health check for detached lease PID liveness (future improvement).

The result artifact correctly does not claim the global Codex ACL issue is fully fixed.