# IKE Runtime v0 - R2-I18 Design Review Pack

Date: 2026-04-11
Status: `review-ready`
Scope: `R2-I18 design only`

## Review Prompt

Review this packet as a narrow runtime design review for one durable controller
acceptance record boundary above the current live
`controller_confirmation_required` state.

Focus on:

1. whether the proposed landing on `runtime_decisions` +
   `runtime_task_events` + `runtime_work_contexts.latest_decision_id` is the
   narrowest truthful choice
2. whether inspect and record semantics are sufficiently separated
3. whether the idempotency/supersession policy avoids ambiguous truth for
   repeated confirmations
4. whether the proposed API contract overstates runtime capability or drifts
   into a generic approval framework

Please prioritize:

- semantic honesty
- truth-source discipline
- auditability
- avoidance of approval-system sprawl

Please return:

1. findings first, ordered by severity
2. validation gaps
3. recommendation:
   - `accept`
   - `accept_with_changes`
   - `reject`

## Documents Under Review

- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-I18_PHASE_JUDGMENT_2026-04-10.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-I18_PHASE_JUDGMENT_2026-04-10.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-I18_PLAN_2026-04-10.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-I18_PLAN_2026-04-10.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R2-I18_CODING_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R2-I18_CODING_BRIEF.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-I18_API_CONTRACT_2026-04-11.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-I18_API_CONTRACT_2026-04-11.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-I18_IDEMPOTENCY_POLICY_2026-04-11.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-I18_IDEMPOTENCY_POLICY_2026-04-11.md)

## Current Design Summary

The next packet is intentionally narrow:

- no new table by default
- no general approval subsystem
- one inspect route
- one explicit record route
- one durable `runtime_decisions` record for scope
  `canonical_service_acceptance`
- one append-only `runtime_task_events` audit event
- one work-context reflection via `latest_decision_id`

## Key Guardrails

1. inspect must not write
2. record must be explicit
3. record only allowed when current live truth is
   `controller_confirmation_required`
4. repeated same-basis confirm should no-op
5. changed eligible basis should supersede explicitly
6. stale/non-eligible current truth should reject

## Current Recommendation

- `accept_with_changes`

Reason:

- the design is now narrow and grounded in existing canonical runtime
  structures
- but it still needs external critique before turning into implementation
