# OpenClaw PM Health Incident: quiet digest with stale mainline

Date: 2026-05-24
Reporter: codex-controller
Incident type: automation-health

## summary

The OpenClaw PM automation is running, but the latest PM digest violates the
stall gate. It reports `decision: quiet` while `staleness_minutes` is `265`.
The threshold is `240` minutes, so this run should have triggered controller
action, reported bridge busy/failure, or reported invalid state.

This artifact is automation-health evidence only. It must not update
`last_real_progress_at` and must not be counted as product/mainline progress.

## evidence

- Latest digest: `ops/pm-runs/latest.json`
- Run id: `openclaw_pm_run_20260524_151200`
- Checked at: `2026-05-24T15:12:00+08:00`
- Decision: `quiet`
- Staleness: `265`
- Threshold: `240`
- Invalid evidence sentence: `last_real_progress_at 2026-05-24T10:47:50+08:00 is ~265 minutes old, under 4-hour staleness threshold`

## impacted component

- Primary: `openclaw-ike-pm`
- Secondary: PM run digest validation
- Not impacted directly: Codex controller bridge process invocation

## violated rule

`staleness_minutes >= 240` must not produce `decision: quiet`.

This rule is now written into:

- `ops/agents/openclaw-ike-pm.md`
- `ops/schemas/openclaw_pm_run_digest_v1.schema.json`

## corrective action taken

- Reframed the Codex automation `mainline-stall-watch-local-executor` as
  `openclaw-pm-health-watch`.
- The Codex automation is no longer allowed to execute mainline work, write
  `mainline_auto_continue_result_*.md`, or claim product progress.
- Added a schema guard so PM digests with `staleness_minutes >= 240` cannot
  be valid with `decision: quiet`.
- Added a mechanical stall gate to the OpenClaw PM agent contract.

## recommended owner lane

`openclaw-ike-pm` should rerun the PM check and produce a corrected digest:

- If still stale, emit a trigger or bridge failure/busy state.
- If recent real progress exists, cite the exact non-automation evidence and
  compute `staleness_minutes < 240`.

## validation run

- Manual validation confirmed current latest digest is invalid:
  `LATEST_INVALID quiet_with_staleness_minutes=265 threshold=240`

## stop condition

The incident is closed only when the next PM digest obeys the stall gate and no
longer reports `quiet` for `staleness_minutes >= 240`.

## update 2026-05-24T15:39+08:00

PM still emitted an invalid quiet digest at `2026-05-24T15:12:00+08:00`:

- Digest: `ops/pm-runs/latest.json` / `ops/pm-runs/history/openclaw_pm_run_20260524_151200.json`
- `decision: quiet`
- `staleness_minutes: 265` (threshold `240`)

Controller action needed: notify the OpenClaw PM owner lane to fix the stall
gate enforcement so the next scheduled PM run cannot produce this invalid
combination.
