# IKE Claude Worker P1 Implementation Task Packet

Date: 2026-04-11
Status: controller task packet

## Goal

Turn the current Claude worker real-run gap into one bounded implementation
task that improves:

- cross-platform prompt delivery
- detached durable finalization

## Write Scope

- [D:\code\MyAttention\services\api\claude_worker\worker.py](/D:/code/MyAttention/services/api/claude_worker/worker.py)
- [D:\code\MyAttention\services\api\tests\test_claude_worker.py](/D:/code/MyAttention/services/api/tests/test_claude_worker.py)

## Preferred Direction

### 1. Prompt delivery

- stop treating Windows command-line prompt passing as the main contract
- prefer a Python-controlled input path for long prompts
- the contract should remain valid on Windows, Linux, and macOS

### 2. Durable finalization

- detached completion must converge once the child has already exited
- `wait` / `fetch` should not remain durably stuck at `running` after child
  exit
- any fallback behavior must remain truthful and auditable

## Minimum Acceptance Proof

One narrow real-run proof should be possible with:

1. `start`
2. full prompt reaches Claude
3. child exits
4. `final.json` exists
5. result projection exists
6. `fetch` no longer shows only a stale `running` snapshot

## Constraints

- no daemon/job supervisor
- no broad provider rewrite
- no fake claim of full sandbox enforcement
- no widening into unrelated harness redesign

## Validation Preference

- focused unit tests in
  [D:\code\MyAttention\services\api\tests\test_claude_worker.py](/D:/code/MyAttention/services/api/tests/test_claude_worker.py)
- one truthful real-run smoke if the environment allows it

## Input Docs

- [D:\code\MyAttention\docs\IKE_CLAUDE_WORKER_REAL_RUN_GAP_2026-04-11.md](/D:/code/MyAttention/docs/IKE_CLAUDE_WORKER_REAL_RUN_GAP_2026-04-11.md)
- [D:\code\MyAttention\docs\IKE_CLAUDE_WORKER_P1_CROSS_PLATFORM_HARDENING_PACKET_2026-04-11.md](/D:/code/MyAttention/docs/IKE_CLAUDE_WORKER_P1_CROSS_PLATFORM_HARDENING_PACKET_2026-04-11.md)
- [D:\code\MyAttention\docs\IKE_CLAUDE_WORKER_P1_CODING_BRIEF_2026-04-11.md](/D:/code/MyAttention/docs/IKE_CLAUDE_WORKER_P1_CODING_BRIEF_2026-04-11.md)
