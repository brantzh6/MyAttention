# Controller Absorption: OpenClaw PM trigger mechanism review

Date: 2026-05-24
Controller: codex-controller

## reviewed evidence

- `docs/reviews/active/review_for_openclaw_pm_trigger_mechanism_2026-05-24.md`
- `docs/reviews/active/review_for_openclaw_pm_digest_validator_fix_2026-05-24.md`
- `tasks/codex/openclaw_pm_health_incident_2026-05-24.md`
- `ops/pm-runs/latest.json`
- `ops/triggers/openclaw_pm_20260524_153900.json`
- `ops/bridge/runs/openclaw_codex_20260524_074236.json`

## controller decision

`accept_with_changes`.

The mechanism direction is correct:

- OpenClaw `ike-pm` is the primary automatic trigger.
- Codex remains controller.
- Codex app automation is now a health-watch fallback, not a second PM.
- Bridge lease behavior is broadly correct.

The prior critical defect is fixed at the tooling level:

- `scripts/ops/validate_openclaw_pm_digest.py` rejects `decision: quiet` when
  `staleness_minutes >= 240`.
- The latest compliant digest validates.
- The historical bad digest `openclaw_pm_run_20260524_151200.json` is rejected
  as expected.
- Claude Code re-review recommends `accept`.

## absorbed findings

1. F1 threshold defect: fixed for future runs by contract plus executable
   validator.
2. PM must run validator before considering a run complete.
3. Automation-health incidents must not be counted as product/mainline
   progress.
4. PM stall detection must not treat wrapper-only bridge results, failed runner
   dispatch notes, PM digests, triggers, lease updates, or automation-health
   artifacts as qualifying mainline progress.

## remaining risks

- The PM agent still has to comply with the new validator step at runtime.
- Historical invalid PM digests remain as evidence and should not be rewritten.
- Current runner execution remains blocked by host-level `spawn EPERM` / lock
  permission failures.
- Package A remains parked until a genuinely non-sandboxed local operator or
  manual shell lane executes the existing packet.

## validation

- `python scripts\ops\validate_openclaw_pm_digest.py ops\pm-runs\latest.json`
  returned valid.
- `python scripts\ops\validate_openclaw_pm_digest.py ops\pm-runs\history\openclaw_pm_run_20260524_151200.json`
  returned invalid as expected.
- `python -m json.tool` passed for the edited schema and latest PM/trigger
  JSON files.

## recommendation

Accept the OpenClaw PM trigger mechanism fix with the changes above, then move
the next execution step to a non-sandboxed local operator/manual shell lane for
`tasks/codex/control_surface_package_a_boundary_cleanup_packet_2026-05-23.md`.

