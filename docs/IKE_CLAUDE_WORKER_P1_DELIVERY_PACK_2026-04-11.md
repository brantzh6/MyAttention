# IKE Claude Worker P1 Delivery Pack

Date: 2026-04-11
Status: controller delivery pack

## What This Pack Is For

Use this pack when handing the next Claude worker hardening task to another
coding or review model.

## Task

Close one narrow live harness gap in the local Claude worker:

- full prompt delivery must be trustworthy across platforms
- detached durable finalization must close after owner exit

## Primary Files

- code:
  - [D:\code\MyAttention\services\api\claude_worker\worker.py](/D:/code/MyAttention/services/api/claude_worker/worker.py)
- tests:
  - [D:\code\MyAttention\services\api\tests\test_claude_worker.py](/D:/code/MyAttention/services/api/tests/test_claude_worker.py)

## Required Context

- gap note:
  - [D:\code\MyAttention\docs\IKE_CLAUDE_WORKER_REAL_RUN_GAP_2026-04-11.md](/D:/code/MyAttention/docs/IKE_CLAUDE_WORKER_REAL_RUN_GAP_2026-04-11.md)
- hardening packet:
  - [D:\code\MyAttention\docs\IKE_CLAUDE_WORKER_P1_CROSS_PLATFORM_HARDENING_PACKET_2026-04-11.md](/D:/code/MyAttention/docs/IKE_CLAUDE_WORKER_P1_CROSS_PLATFORM_HARDENING_PACKET_2026-04-11.md)
- coding brief:
  - [D:\code\MyAttention\docs\IKE_CLAUDE_WORKER_P1_CODING_BRIEF_2026-04-11.md](/D:/code/MyAttention/docs/IKE_CLAUDE_WORKER_P1_CODING_BRIEF_2026-04-11.md)
- implementation task packet:
  - [D:\code\MyAttention\docs\IKE_CLAUDE_WORKER_P1_IMPLEMENTATION_TASK_PACKET_2026-04-11.md](/D:/code/MyAttention/docs/IKE_CLAUDE_WORKER_P1_IMPLEMENTATION_TASK_PACKET_2026-04-11.md)
- run note:
  - [D:\code\MyAttention\docs\IKE_SOURCE_INTELLIGENCE_V1_M1_CLAUDE_RUN_20260411T112415-babf2099_NOTE.md](/D:/code/MyAttention/docs/IKE_SOURCE_INTELLIGENCE_V1_M1_CLAUDE_RUN_20260411T112415-babf2099_NOTE.md)

## Required Output Contract

1. `summary`
2. `files_changed`
3. `why_this_solution`
4. `validation_run`
5. `known_risks`
6. `recommendation`

## Acceptance Boundary

Do not claim success unless the change truthfully improves:

- real prompt delivery robustness
- durable finalization after owner exit

## Recommendation

`accept_with_changes`

This pack is ready for bounded coding and review, but the result still needs
controller verification with real-run evidence.
