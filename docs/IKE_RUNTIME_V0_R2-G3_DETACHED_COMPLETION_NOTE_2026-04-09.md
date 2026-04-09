# IKE Runtime v0 R2-G3 Detached Completion Note

## Scope

Record the current detached-completion evidence from active local Claude runs.

This is an operational evidence note, not a new runtime feature.

## Current Evidence

The following runs all remain in `running` state and timed out under detached
wait polling:

- `R2-G2` coding run
  - [D:\code\MyAttention\.runtime\claude-worker\runs\20260408T153652-948b3f83](/D:/code/MyAttention/.runtime/claude-worker/runs/20260408T153652-948b3f83)
- thinking armory PDF batch A review
  - [D:\code\MyAttention\.runtime\claude-worker\runs\20260408T155231-cb5e2538](/D:/code/MyAttention/.runtime/claude-worker/runs/20260408T155231-cb5e2538)
- thinking armory PDF batch B review
  - [D:\code\MyAttention\.runtime\claude-worker\runs\20260408T155231-4999aa1d](/D:/code/MyAttention/.runtime/claude-worker/runs/20260408T155231-4999aa1d)

Each currently returns the same detached-wait pattern:
- `status = running`
- `detached_wait.state = timed_out`
- no durable `final.json` payload yet usable for controller acceptance

## Controller Interpretation

This is not proof that the runs are useless.

It is proof that detached completion reliability is still not hardened enough
to support routine unattended controller closure.

## Result

Current truthful runtime/worker interpretation:

- Claude worker remains:
  - usable local lane
  - useful bounded coding/review substrate
- but not yet:
  - routine detached completion lane
  - reliable unattended final-artifact producer

## Follow-Up Pressure

This evidence reinforces the existing hardening requirements in:
- [D:\code\MyAttention\docs\CLAUDE_WORKER_RUNTIME_HARDENING_REQUIREMENTS_2026-04-08.md](/D:/code/MyAttention/docs/CLAUDE_WORKER_RUNTIME_HARDENING_REQUIREMENTS_2026-04-08.md)

Especially:
- durable completion reliability
- detached run discipline
- stronger final-artifact closure guarantees
