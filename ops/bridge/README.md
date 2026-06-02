# IKE OpenClaw to Codex Bridge

Purpose: let local OpenClaw `ike-pm` actively invoke a bounded Codex controller
run when the project state shows a mainline stall or gate issue.

This replaces the incomplete pattern where OpenClaw only wrote a JSON trigger
that Codex might never read.

## Control Boundary

- OpenClaw `ike-pm` detects stall or invalid gate conditions.
- `ike-pm` may write one trigger JSON under `ops/triggers/`.
- `ike-pm` may call only this bridge script to wake Codex:
  `python scripts/ops/openclaw_codex_bridge.py --mode wake --detached ...`
- The bridge owns Codex process invocation, lease handling, and run metadata.
- Codex remains the controller and promotion decider.

## Lease

The bridge uses:

- `ops/state/codex_controller_lease.json`
- `ops/state/codex_controller_lease.lock`

If the lease is active, the bridge does not start another Codex run. It records
a `busy` bridge result instead.

Cron callers should use `--detached`. Detached dispatch starts the Codex
controller run in the background, records bridge metadata immediately, and keeps
the controller lease active until expiry so later PM checks do not start
duplicate controller runs while the background Codex process is still running.

## Trigger Consumption

Trigger files may contain a `bridge` object after dispatch:

```json
{
  "bridge": {
    "status": "dispatching | dispatched | failed | deferred_busy",
    "run_id": "openclaw_codex_YYYYMMDD_HHMMSS",
    "updated_at": "ISO-8601"
  }
}
```

Trigger schema:

- `ops/schemas/openclaw_pm_trigger_v1.schema.json`

The bridge performs built-in minimum validation before dispatching Codex. Invalid
triggers are marked `failed_invalid_trigger` and Codex is not invoked.

## Escalation

If bridge dispatch is repeatedly deferred, apply this policy:

- 3 consecutive `deferred_busy` bridge results for the same trigger, or
- a trigger older than 12 hours that has not reached `dispatched`

Then `ike-pm` must use reason `controller_bridge_escalation` and preserve the
original trigger evidence. The bridge must still respect the active controller
lease; escalation is a visibility and handoff signal, not permission to start
duplicate Codex runs.

## Codex Prompt

Codex receives `ops/codex/controller_wakeup_prompt.md` plus invocation metadata.
The controller run must perform one bounded action, update project state if real
progress occurs, and stop.

## Non-Goals

- Do not use this bridge for code review.
- Do not use this bridge for runtime service operation.
- Do not let OpenClaw author tasks or decide promotion.
