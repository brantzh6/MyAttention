# IKE Runtime v0 Packet R1-B1 Coding Brief

## Task ID

`IKE-RUNTIME-R1-B1`

## Goal

Implement the smallest truthful lifecycle proof for:

- `inbox -> ready -> active -> review_pending -> done`

## In Scope

1. Add a narrow lifecycle proof helper if needed.
2. Add or update focused tests proving:
   - task starts in `inbox`
   - controller can move to `ready`
   - legal claim path moves to `active`
   - work can move to `review_pending`
   - controller can move to `done`
   - task events reflect the ordered path
3. Reuse existing runtime state/event logic instead of introducing new objects.

## Out of Scope

- scheduler work
- benchmark integration
- UI
- memory retrieval expansion
- broad service architecture changes

## Likely Touch Points

- [D:\code\MyAttention\services\api\runtime\state_machine.py](/D:/code/MyAttention/services/api/runtime/state_machine.py)
- [D:\code\MyAttention\services\api\runtime\transitions.py](/D:/code/MyAttention/services/api/runtime/transitions.py)
- [D:\code\MyAttention\services\api\tests\test_runtime_v0_task_state_semantics.py](/D:/code/MyAttention/services/api/tests/test_runtime_v0_task_state_semantics.py)
- [D:\code\MyAttention\services\api\tests\test_runtime_v0_events_and_leases.py](/D:/code/MyAttention/services/api/tests/test_runtime_v0_events_and_leases.py)
- or one new focused runtime lifecycle proof test file if that is cleaner

## Required Output

- summary
- files_changed
- why_this_solution
- validation_run
- known_risks
- recommendation

## Required Validation

- live pytest for the lifecycle proof path
- no AST-only claims

## Stop Conditions

- if the proof requires inventing new first-class runtime objects
- if the proof broadens into scheduler/queue/UI work
- if it requires bypassing the review boundary
