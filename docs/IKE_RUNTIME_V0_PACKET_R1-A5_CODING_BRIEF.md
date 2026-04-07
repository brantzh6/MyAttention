# IKE Runtime v0 Packet R1-A5 Coding Brief

## Task ID

`IKE-RUNTIME-R1-A5`

## Goal

Close the narrow enforcement gaps that remain after `R1-A1~R1-A4`.

## In Scope

1. Remove or explicitly deprecate the `role=None` legacy `force=True` bypass.
2. Tighten verifier trust semantics around upstream existence checks.
3. Strengthen `ClaimContext` validation semantics where possible without
   expanding runtime scope.
4. Normalize migration-validation test invocation so the packet can be tested
   more repeatably.

## Out of Scope

- adding new runtime objects
- real lifecycle implementation
- scheduler/platform work
- graph memory / retrieval work
- broad refactors across unrelated modules

## Likely Touch Points

- [D:\code\MyAttention\services\api\runtime\transitions.py](/D:/code/MyAttention/services/api/runtime/transitions.py)
- [D:\code\MyAttention\services\api\runtime\state_machine.py](/D:/code/MyAttention/services/api/runtime/state_machine.py)
- [D:\code\MyAttention\services\api\runtime\memory_packets.py](/D:/code/MyAttention/services/api/runtime/memory_packets.py)
- runtime tests only as needed for this narrow scope

## Required Output

- summary
- files_changed
- why_this_solution
- validation_run
- known_risks
- recommendation

## Required Validation

- targeted runtime pytest coverage for:
  - force-path restriction
  - claim validation
  - memory trust boundary
  - migration-validation support

## Stop Conditions

- if the fix requires adding new runtime objects
- if the patch would broaden into R1-B lifecycle work
- if the verifier contract cannot be tightened without architecture change

## Acceptance Bias

Prefer:

- minimal additive hardening
- explicit truth-boundary comments
- smaller but stricter behavior over broader cleverness
