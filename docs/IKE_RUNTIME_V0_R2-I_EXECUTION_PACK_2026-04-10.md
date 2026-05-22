# IKE Runtime v0 - R2-I Execution Pack

Date: 2026-04-10
Phase: `R2-I First Real Task Lifecycle On Canonical Service`
Status: `candidate execution pack`

## Activation Condition

This pack becomes active only if the controller accepts the current `R2-H`
canonical Windows proof path.

Reference:

- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-H8_CONTROLLER_DECISION_BRIEF_2026-04-10.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-H8_CONTROLLER_DECISION_BRIEF_2026-04-10.md)

## Immediate Objective

Run one narrow, auditable, live-service-adjacent runtime task lifecycle proof
without turning the runtime service into a broad task runner.

## Packet Order

1. [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R2-I1_CODING_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R2-I1_CODING_BRIEF.md)
2. [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R2-I2_REVIEW_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R2-I2_REVIEW_BRIEF.md)
3. [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R2-I3_TEST_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R2-I3_TEST_BRIEF.md)
4. [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R2-I4_EVOLUTION_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R2-I4_EVOLUTION_BRIEF.md)

## Guardrails

Do not:

- add a general task execution framework
- open scheduler/daemon scope
- introduce a second truth source for lifecycle state
- widen UI/runtime integration beyond what the proof requires
- silently convert inspect-style output into durable accepted state

## Suggested Lane Routing

- coding:
  - Claude Code with `glm-5.1` is a strong candidate if the packet becomes
    backend/business-logic heavy
  - otherwise latest `qwen3.6` remains the default routine lane
- review:
  - Claude Code review lane or OpenClaw review lane
- test:
  - controller or bounded delegate

## Success Condition

`R2-I` should close only if all of the following are true:

1. one real lifecycle proof can be run against the current canonical service
   baseline
2. the proof remains runtime-truth-owned and auditable
3. no broad orchestration semantics are implied
4. the resulting state can be inspected from the existing runtime-facing
   surfaces or one new narrow inspect surface
