# Controller Absorption: /control live ops-state adapter fix

Task ID: control_live_ops_state_adapter_fix_absorption_2026_05_27
Controller: codex-controller
Date: 2026-05-27
Decision: accept_for_pr_promotion

## Inputs

- Coding worker result: tasks/codex/control_live_ops_state_adapter_fix_result_2026-05-27.md
- Local reviewer result: tasks/codex/control_live_ops_state_adapter_fix_review_result_2026-05-27.md
- Runtime operator result: tasks/codex/control_live_ops_state_pre_pr_runtime_validation_result_2026-05-27.md

## Controller Decision

Accept the adapter fix for PR promotion.

The implementation is scoped to services/web/lib/control-surface/ops-state-adapter.ts and fixes the observed runtime gap: Next standalone execution can now resolve the repository root and read ops/state/current_state.json plus ops/pm-runs/latest.json. Local review accepted the code shape with a validation requirement. ike-operator then validated the built standalone runtime and confirmed /control renders file_derived provenance, Ops State Sync, and PM Watch Digest instead of static fallback.

## Quality Gate

- Scoped diff: passed.
- Local review: accept_with_changes, validation required.
- Runtime validation: accept.
- Promotion path: open GitHub PR for this bounded fix, then trigger GitHub/Codex review because it is a main-bound change.

## Next Gate

After merge, route post-merge runtime validation through ike-operator and then run the integrated AI chat -> evolution -> /control product smoke.
