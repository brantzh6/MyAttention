# IKE Runtime v0 Delegation Backlog

## Purpose

This document turns the runtime implementation packets into controller-ready
delegation order.

It answers:

- which packets are safe to delegate first
- which packets require stricter controller review
- which packets should not run in parallel

## Delegation Rule

For `IKE Runtime v0`, delegation priority is determined by:

1. reversibility
2. semantic clarity
3. write-scope isolation
4. reviewability

Do not optimize for speed by parallelizing semantically coupled packets too
early.

## Recommended Order

### 1. `R0-A` Core Runtime Schema Foundation

Delegate first.

Why:

- narrowest write scope
- high auditability
- establishes canonical objects without yet introducing behavior

Review intensity:

- high

Parallelization:

- do not run against another schema-writing runtime packet

### 2. `R0-B` Compressed Task State Machine Semantics

Delegate second.

Why:

- must align tightly with `R0-A`
- semantically central
- illegal transitions are expensive to reverse later

Review intensity:

- very high

Parallelization:

- do not run in parallel with another packet changing task semantics
- recommended only after `R0-A` schema fields and task-status columns are in
  place or guaranteed by the implementation plan

### 3. `R0-C` Task Event Log and Lease Semantics

Delegate third.

Why:

- depends on task schema and state semantics already being stable enough
- still bounded enough for isolated review

Review intensity:

- high

### 4. `R0-D` WorkContext Snapshot Carrier

Delegate after the state/event foundation.

Why:

- depends on canonical state already existing
- risks second-truth drift if rushed

Review intensity:

- very high on truthfulness

### 5. `R0-E` MemoryPacket Metadata and Acceptance

Delegate after upstream task/decision review semantics are stable.

Why:

- memory trust semantics are easily faked if upstream acceptance logic is weak

Review intensity:

- very high on trust boundaries

### 6. `R0-F` Redis Acceleration and Recovery Rebuild

Delegate last in the first wave.

Why:

- acceleration should follow truth, not define truth

Review intensity:

- high on recovery and rebuild correctness

## Do Not Delegate Yet

These are explicitly not first-wave runtime delegation targets:

- graph-memory structures
- semantic retrieval
- notification/follow-up subsystem
- broad runtime UI
- public runtime APIs
- multi-project orchestration marketplace behavior

## Controller Reminder

Each runtime packet result must be reviewed for:

- fake durability
- hidden canonical state
- illegal transition shortcuts
- delegate self-acceptance
- JSONB misuse
- accidental broadening into future-version scope

Additional controller note:

- run a packet-specific pre-review before executing:
  - `R0-B` compressed state semantics
  - `R0-E` memory trust boundaries

## Ready Briefs

Current packet briefs prepared:

- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R0-A_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R0-A_BRIEF.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R0-B_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R0-B_BRIEF.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R0-C_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R0-C_BRIEF.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R0-D_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R0-D_BRIEF.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R0-E_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R0-E_BRIEF.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R0-F_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R0-F_BRIEF.md)
