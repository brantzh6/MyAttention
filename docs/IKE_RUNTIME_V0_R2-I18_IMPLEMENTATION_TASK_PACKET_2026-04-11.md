# IKE Runtime v0 - R2-I18 Implementation Task Packet

Date: 2026-04-11
Packet: `R2-I18 Controller Acceptance Record Boundary`
Audience: `delegated coding / bounded implementation`
Status: `ready`

## Mission

Implement one narrow durable controller acceptance record boundary above the
current live `controller_confirmation_required` state.

## Required Reading

Read these first, in order:

1. [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-I18_PHASE_JUDGMENT_2026-04-10.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-I18_PHASE_JUDGMENT_2026-04-10.md)
2. [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-I18_PLAN_2026-04-10.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-I18_PLAN_2026-04-10.md)
3. [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R2-I18_CODING_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R2-I18_CODING_BRIEF.md)
4. [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-I18_API_CONTRACT_2026-04-11.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-I18_API_CONTRACT_2026-04-11.md)
5. [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-I18_IDEMPOTENCY_POLICY_2026-04-11.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-I18_IDEMPOTENCY_POLICY_2026-04-11.md)
6. [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-I18_MINIMAL_WRITESET_2026-04-11.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-I18_MINIMAL_WRITESET_2026-04-11.md)

## Exact Goal

Land the smallest implementation that proves:

1. a controller acceptance record can be inspected
2. a controller acceptance record can be explicitly written
3. repeated same-basis confirmation does not create ambiguous truth
4. changed eligible basis supersedes explicitly
5. latest decision can be reflected on the runtime read surface

## Required Constraints

1. no new table unless a hard blocker is discovered
2. prefer `runtime_decisions` as the canonical record
3. append one `runtime_task_events` audit event
4. update/align `runtime_work_contexts.latest_decision_id`
5. inspect must not write
6. record must reject when current truth is not
   `controller_confirmation_required`

## Preferred Files

Preferred write set:

- `services/api/runtime/controller_acceptance.py`
- `services/api/routers/ike_v0.py`
- `services/api/runtime/operational_closure.py` or
  `services/api/runtime/project_surface.py` only if minimally necessary
- focused tests:
  - `services/api/tests/test_routers_ike_v0.py`
  - `services/api/tests/test_runtime_v0_project_surface.py`
  - optional new helper test file

## Required Behavior

### Inspect Route

- read-only
- returns current preflight shape plus latest acceptance record state

### Record Route

- explicit controller action
- requires `controller_id`
- re-checks current preflight truth before writing
- only writes if current state is confirmation-eligible

### Idempotency

- same basis/scope/target/current live shape:
  - reuse existing finalized decision
  - no new row
  - no new event
- changed eligible basis:
  - create new finalized decision
  - set `supersedes_decision_id`
  - append one event
- non-eligible current truth:
  - reject

## Validation Required

Run at least:

```powershell
python -m pytest tests/test_runtime_v0_service_preflight.py tests/test_routers_ike_v0.py tests/test_runtime_v0_project_surface.py <new focused helper tests> -q
python -m compileall runtime routers tests
```

If code lands cleanly, also run one live local proof against canonical
`127.0.0.1:8000`.

## Delivery Format

Return:

1. `summary`
2. `files_changed`
3. `why_this_solution`
4. `validation_run`
5. `known_risks`
6. `recommendation`

## Recommendation Target

Default target:

- `accept_with_changes`

Only upgrade beyond that if the bounded write path, idempotency policy, and
read-surface alignment are all clearly proven.
