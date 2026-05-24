# Controller Absorption: delegated lane repair

Date: 2026-05-24
Controller: codex-controller

## reviewed evidence

- Task packet:
  `tasks/codex/delegated_lane_repair_packet_spawn_eperm_2026-05-24.md`
- Result:
  `tasks/codex/delegated_lane_repair_result_spawn_eperm_2026-05-24.md`
- Review:
  `docs/reviews/active/review_for_delegated_lane_repair_spawn_eperm_2026-05-24.md`
- Bridge smoke:
  `ops/bridge/runs/openclaw_codex_20260524_080831.json`
- Smoke output:
  `tasks/codex/openclaw_codex_controller_run_openclaw_codex_20260524_080831.md`

## controller decision

`accept_with_changes`.

The immediate spawn/lock substrate is sufficiently repaired for local
execution and bridge smoke:

- stale detached Codex/ACP/acpx processes were stopped;
- git ref write smoke passed;
- Node child-process spawn smoke passed;
- Claude CLI smoke passed;
- web build passed;
- bridge smoke returned `CODEX_BRIDGE_SMOKE_OK`;
- bridge lease logic now ignores dead detached Codex PIDs.

## accepted finding

The independent review accepted the PID-liveness fix and identified one
required follow-up: persist the untracked bridge/script changes in a scoped ops
repair commit.

## remaining risks

- Global `C:\Users\jiuyou\.codex\skills\.system` remains ACL-broken.
- Codex bridge can run despite the skills warning, but system skills may be
  unavailable to bridge-launched Codex runs.
- Isolated `CODEX_HOME` avoids the broken skills directory but lacks auth and
  returns 401.
- OpenClaw `myattention-coder` identity/session lock EPERM still needs a
  direct post-cleanup validation.

## next action

Create a scoped ops repair save-state branch/commit for the PM validator,
bridge PID-liveness fix, review evidence, and absorption artifacts. Do not mix
this into PR13 or the Package A branch.

