# IKE Claude Worker P1 Cross-Platform Hardening Packet

Date: 2026-04-11
Status: controller packet

## Goal

Close one narrow but important harness gap in the local Claude worker:

- real prompt delivery must be cross-platform trustworthy
- detached durable finalization must close after owner exit

## Why Now

The first real coding run exposed two live weaknesses:

1. the intended multi-line task packet was not fully delivered to the Claude
   session
2. the run remained durably `running` after the child was already gone

These are no longer theoretical hardening items.

## Scope

- `services/api/claude_worker/worker.py`
- `services/api/tests/test_claude_worker.py`
- narrow doc/result updates only if needed

## Required Outcome

One truthful end-to-end harness proof for a real run should become possible:

- `start`
- full prompt reaches Claude
- child exits
- `final.json` exists
- result projection exists

## Non-Goals

- no broad daemon/job supervisor
- no new orchestration framework
- no fake claim of full sandbox enforcement
- no broad provider abstraction rewrite

## Acceptance Boundary

This packet is successful only if:

- prompt delivery no longer depends on fragile Windows CLI prompt passing
- real-run completion can durably finalize
- the result can be fetched without remaining stuck at `running`

## Inputs

- [D:\code\MyAttention\docs\IKE_CLAUDE_WORKER_REAL_RUN_GAP_2026-04-11.md](/D:/code/MyAttention/docs/IKE_CLAUDE_WORKER_REAL_RUN_GAP_2026-04-11.md)
- [D:\code\MyAttention\docs\IKE_PLATFORM_NEUTRALIZATION_AUDIT_2026-04-11.md](/D:/code/MyAttention/docs/IKE_PLATFORM_NEUTRALIZATION_AUDIT_2026-04-11.md)
- [D:\code\MyAttention\docs\IKE_LINUX_CUTOVER_READINESS_2026-04-11.md](/D:/code/MyAttention/docs/IKE_LINUX_CUTOVER_READINESS_2026-04-11.md)

## Recommendation

`accept_with_changes`

This is the correct next narrow hardening move before claiming the Claude
worker as a stronger production-grade harness lane.
