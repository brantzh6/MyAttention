# Controller Absorption: OpenClaw PM Trigger / Codex Controller Boundary - 2026-05-25

Date: 2026-05-25T00:23:00+08:00
Controller: Codex
Review lane: myattention-kimi-review

## Inputs

- Protocol files:
  - `ops/agents/openclaw-ike-pm.md`
  - `ops/codex/controller_wakeup_prompt.md`
  - `ops/schemas/openclaw_pm_trigger_v1.schema.json`
- Review packet:
  - `tasks/codex/openclaw_pm_trigger_controller_boundary_review_packet_2026-05-25.md`
- Review artifact:
  - `docs/reviews/active/review_for_openclaw_pm_trigger_controller_boundary_2026-05-25.md`
- Validation:
  - `python -m json.tool ops\schemas\openclaw_pm_trigger_v1.schema.json`
  - `python scripts\ops\validate_openclaw_pm_digest.py ops\pm-runs\latest.json`
  - `python scripts\ops\check_controller_gate.py --claim accepted_project_truth`

## Decision

Accepted.

OpenClaw PM is now explicitly defined as a wakeup trigger and evidence source,
not as a controller or binding task planner. Codex remains responsible for
project plan, progress, quality, gate decisions, and mainline movement.

## Absorbed Rule

When OpenClaw PM wakes Codex:

1. Treat the trigger as evidence and wakeup context only.
2. Treat `requested_controller_action` as advisory.
3. Reconcile the trigger with `ops/state/current_state.json`, mainline
   priorities, runtime truth, review state, and dirty-tree gates.
4. If PM advice is stale or too narrow, record that and choose the correct
   bounded controller action.
5. PM/delegate forbidden actions must not block controller-owned work such as
   task authoring, review absorption, promotion decision, runtime-operator
   dispatch, or bounded source edits when gates allow them.

## Remaining Follow-Ups

- Future PM triggers should use advisory language and avoid imperative
  controller instructions.
- A future PM run should be observed to confirm the new prompt wording is
  followed.
- Dirty-tree containment remains the next state-management blocker before
  additional product coding or promotion packaging.

## Recommendation

`accept`
