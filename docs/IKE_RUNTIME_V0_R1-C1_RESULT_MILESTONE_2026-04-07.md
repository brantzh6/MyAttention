# IKE Runtime v0 R1-C1 Result Milestone

## Purpose

This milestone records the truthful outcome of `R1-C1` truth-layer coding.

`R1-C1` was intended to do three narrow things:

1. remove executable dependence on legacy `allow_claim=True`
2. move delegate-claim proof toward a runtime-owned adapter boundary
3. preserve the existing lifecycle proof shape without broader runtime expansion

## Actual Outcome

`R1-C1` is now materially implemented in the runtime codebase.

Changed implementation areas:

- [D:\code\MyAttention\services\api\runtime\state_machine.py](/D:/code/MyAttention/services/api/runtime/state_machine.py)
- [D:\code\MyAttention\services\api\runtime\transitions.py](/D:/code/MyAttention/services/api/runtime/transitions.py)
- [D:\code\MyAttention\services\api\runtime\leases.py](/D:/code/MyAttention/services/api/runtime/leases.py)

Changed test alignment:

- [D:\code\MyAttention\services\api\tests\test_runtime_v0_events_and_leases.py](/D:/code/MyAttention/services/api/tests/test_runtime_v0_events_and_leases.py)
- [D:\code\MyAttention\services\api\tests\test_runtime_v0_lifecycle_proof.py](/D:/code/MyAttention/services/api/tests/test_runtime_v0_lifecycle_proof.py)
- [D:\code\MyAttention\services\api\tests\test_runtime_v0_state_machine.py](/D:/code/MyAttention/services/api/tests/test_runtime_v0_state_machine.py)
- [D:\code\MyAttention\services\api\tests\test_runtime_v0_task_state_semantics.py](/D:/code/MyAttention/services/api/tests/test_runtime_v0_task_state_semantics.py)

## Controller Judgment

Current judgment: `accept_with_changes`

What is now true:

- delegate `ready -> active` no longer succeeds through executable `allow_claim=True`
- `ClaimContext` is the only satisfying path for CLAIM_REQUIRED transitions
- `TransitionRequest` now carries `claim_context`
- runtime now has an explicit `ClaimVerifier` adapter boundary
- narrow lifecycle/state/event proof remains intact

What is not yet complete:

- `ClaimVerifier` is not yet wired to a Postgres-backed truth implementation
- `allow_claim` still exists as a deprecated compatibility parameter in the pure-logic API surface
- the wider runtime DB-backed test sweep is still blocked by missing fixture/environment support

## Validation

Controller-side narrow validation:

- `PYTHONPATH=D:\code\MyAttention\services\api python -m pytest services/api/tests/test_runtime_v0_state_machine.py services/api/tests/test_runtime_v0_task_state_semantics.py services/api/tests/test_runtime_v0_events_and_leases.py services/api/tests/test_runtime_v0_lifecycle_proof.py -q`
- Result: `256 passed`

Controller-side wider runtime sweep:

- `PYTHONPATH=D:\code\MyAttention\services\api python -m pytest <all test_runtime_v0*.py> -q`
- Result: `417 passed, 35 errors`

Truthful interpretation of the wider errors:

- current failures are in schema-foundation DB tests
- the failing cause is missing `db_session` fixture/environment support
- this is a real runtime testing gap
- it is not currently proven to be caused by the `R1-C1` code changes themselves

## Recommended Next Step

Do not reopen truth-layer design.

Proceed with:

1. `R1-C2` review
2. `R1-C3` testing-lane alignment for DB-backed runtime tests
3. `R1-C4` method/evolution absorption
