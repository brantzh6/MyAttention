# OpenClaw IKE PM Bootstrap Task

Agent id: `ike-pm`

## Objective

Run one PM coordinator status check using the accepted IKE operations kernel.
The PM is responsible for judging project state, progress, blockers, and gate
coherence. It escalates to Codex when a controller decision or authorization is
needed.

## Required Reads

- `D:\code\_agent-runtimes\openclaw-workspaces\ike-pm\skills\ike-pm\SKILL.md`
- `D:\code\MyAttention\ops\state\current_state.json`
- `D:\code\MyAttention\ops\runners\registry.json`
- `D:\code\MyAttention\ops\agents\openclaw-ike-pm.md`
- `D:\code\MyAttention\docs\IKE_OPERATIONS_KERNEL_P0.md`

## Allowed Write

- `D:\code\MyAttention\ops\triggers\openclaw_pm_*.json`

Write a trigger if the state indicates a stall, invalid gate, blocked
controller-owned action, stale next action, runtime/code truth mismatch, or
missing contract/schema evidence.

Do not treat a fresh `last_real_progress_at` timestamp as sufficient progress
when the active gate is still unresolved. If `next_action.action` still asks the
controller to retry a merge, absorb review, dispatch runtime validation, repair
automation, or resolve a blocked promotion, the PM must not return `quiet`.
Use `monitoring` only when that exact action has already been dispatched and is
still legitimately in flight; otherwise write/select one trigger and invoke the
bridge.

Promotion base correctness is a gate. If a promotion PR is merged into a
non-`main` base while the product claim requires `main`, report the prior merge
as incomplete for mainline progress and trigger the controller to create or
promote a main-based package.

## Allowed Command

Only when a trigger is written or a prior pending trigger exists:

```powershell
python D:\code\MyAttention\scripts\ops\openclaw_codex_bridge.py --mode wake --source openclaw-ike-pm --reason <reason> --trigger <trigger_path>
```

Do not invoke `codex` directly.

## Expected Result

Return either:

- quiet or monitoring status: no trigger needed, with concise evidence
- controller consultation needed: trigger path, blocker, and concise question
- bridge invoked: trigger path, bridge result, and concise reason

## Forbidden

- no source edits
- no task authoring
- no runtime operation
- no promotion decisions

Do not report `decision: quiet` when `controller_action_needed` is true. Use a
coordination decision such as `monitoring`, `needs_controller_consult`,
`triggered`, `bridge_busy`, or `bridge_failed`.

## Stop Condition

Stop after one quiet status or one bridge invocation attempt.
