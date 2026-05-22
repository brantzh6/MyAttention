# IKE Runtime v0 Implementation Execution Pack 2026-04-05

## 0. Review / Execution Prompt

Please review and/or execute the current first-wave `IKE Runtime v0` kernel
implementation plan.

Primary document:

- this file: `docs/IKE_RUNTIME_V0_IMPLEMENTATION_EXECUTION_PACK_2026-04-05.md`

Core companion design docs:

- `docs/IKE_RUNTIME_V0_IMPLEMENTATION_READINESS.md`
- `docs/IKE_RUNTIME_V0_DELEGATION_BACKLOG.md`
- `docs/IKE_RUNTIME_V0_FIRST_WAVE_PACKET_INDEX.md`
- `docs/PROJECT_AGENT_HARNESS_CONTRACT.md`

If deeper design challenge is required, also read:

- `docs/IKE_RUNTIME_V0_TASK_STATE_AND_STORAGE_ARCHITECTURE.md`
- `docs/IKE_RUNTIME_V0_DATA_MODEL_AND_TRANSACTION_BOUNDARIES.md`
- `docs/IKE_RUNTIME_V0_ROLE_PERMISSIONS_AND_TRANSITION_MATRIX.md`
- `docs/IKE_RUNTIME_EVOLUTION_ROADMAP.md`

If implementation handoff is required, the first-wave runtime packet materials
already exist in:

- `.runtime/delegation/briefs/`
- `.runtime/delegation/contexts/`
- `.runtime/delegation/results/`

Please focus on:

1. whether first-wave packet order is correct
2. whether any packet still hides future-scope drift
3. whether state/lease/memory trust boundaries are implementation-safe
4. whether any packet should be split further before coding
5. whether any packet is missing a critical stop condition

Please be especially critical about:

- fake durability
- hidden canonical state
- `WorkContext` becoming a second truth source
- `MemoryPacket` gaining trust without upstream review
- Redis becoming truth by accident
- delegate self-acceptance

Desired output:

1. overall verdict
2. top risks in the first-wave execution plan
3. packet order corrections if any
4. packet scope corrections if any
5. first recommended packet to execute
6. what must still be tightened before implementation

## 1. Current Runtime Position

`IKE Runtime v0` is now past pure architecture sketching.

It already has:

- kernel decision
- storage split
- compressed state machine
- role-permission matrix
- transaction boundaries
- recovery model
- long-horizon roadmap
- implementation-readiness checkpoint
- first-wave bounded packets
- concrete `.runtime/delegation` handoff materials

It is still not in coding mode by default.

## 2. First-Wave Goal

The first-wave goal is narrow:

- establish a truthful runtime kernel

It is not:

- a full runtime platform
- a graph-memory system
- a broad orchestration framework
- a runtime UI initiative

## 3. First-Wave Packet Order

1. `R0-A`
   - Core Runtime Schema Foundation
2. `R0-B`
   - Compressed Task State Machine Semantics
3. `R0-C`
   - Task Event Log and Lease Semantics
4. `R0-D`
   - WorkContext Snapshot Carrier
5. `R0-E`
   - MemoryPacket Metadata and Acceptance
6. `R0-F`
   - Redis Acceleration and Recovery Rebuild

## 4. What Is Already Materialized

The following delegate-ready materials already exist:

### R0-A

- [D:\code\MyAttention\.runtime\delegation\briefs\ike-runtime-r0-a-core-schema-glm.md](/D:/code/MyAttention/.runtime/delegation/briefs/ike-runtime-r0-a-core-schema-glm.md)
- [D:\code\MyAttention\.runtime\delegation\contexts\ike-runtime-r0-a-core-schema-glm.md](/D:/code/MyAttention/.runtime/delegation/contexts/ike-runtime-r0-a-core-schema-glm.md)
- [D:\code\MyAttention\.runtime\delegation\results\ike-runtime-r0-a-core-schema-glm.json](/D:/code/MyAttention/.runtime/delegation/results/ike-runtime-r0-a-core-schema-glm.json)

### R0-B

- [D:\code\MyAttention\.runtime\delegation\briefs\ike-runtime-r0-b-task-state-semantics-glm.md](/D:/code/MyAttention/.runtime/delegation/briefs/ike-runtime-r0-b-task-state-semantics-glm.md)
- [D:\code\MyAttention\.runtime\delegation\contexts\ike-runtime-r0-b-task-state-semantics-glm.md](/D:/code/MyAttention/.runtime/delegation/contexts/ike-runtime-r0-b-task-state-semantics-glm.md)
- [D:\code\MyAttention\.runtime\delegation\results\ike-runtime-r0-b-task-state-semantics-glm.json](/D:/code/MyAttention/.runtime/delegation/results/ike-runtime-r0-b-task-state-semantics-glm.json)

### R0-C

- [D:\code\MyAttention\.runtime\delegation\briefs\ike-runtime-r0-c-events-leases-glm.md](/D:/code/MyAttention/.runtime/delegation/briefs/ike-runtime-r0-c-events-leases-glm.md)
- [D:\code\MyAttention\.runtime\delegation\contexts\ike-runtime-r0-c-events-leases-glm.md](/D:/code/MyAttention/.runtime/delegation/contexts/ike-runtime-r0-c-events-leases-glm.md)
- [D:\code\MyAttention\.runtime\delegation\results\ike-runtime-r0-c-events-leases-glm.json](/D:/code/MyAttention/.runtime/delegation/results/ike-runtime-r0-c-events-leases-glm.json)

### R0-D

- [D:\code\MyAttention\.runtime\delegation\briefs\ike-runtime-r0-d-work-context-glm.md](/D:/code/MyAttention/.runtime/delegation/briefs/ike-runtime-r0-d-work-context-glm.md)
- [D:\code\MyAttention\.runtime\delegation\contexts\ike-runtime-r0-d-work-context-glm.md](/D:/code/MyAttention/.runtime/delegation/contexts/ike-runtime-r0-d-work-context-glm.md)
- [D:\code\MyAttention\.runtime\delegation\results\ike-runtime-r0-d-work-context-glm.json](/D:/code/MyAttention/.runtime/delegation/results/ike-runtime-r0-d-work-context-glm.json)

### R0-E

- [D:\code\MyAttention\.runtime\delegation\briefs\ike-runtime-r0-e-memory-packets-glm.md](/D:/code/MyAttention/.runtime/delegation/briefs/ike-runtime-r0-e-memory-packets-glm.md)
- [D:\code\MyAttention\.runtime\delegation\contexts\ike-runtime-r0-e-memory-packets-glm.md](/D:/code/MyAttention/.runtime/delegation/contexts/ike-runtime-r0-e-memory-packets-glm.md)
- [D:\code\MyAttention\.runtime\delegation\results\ike-runtime-r0-e-memory-packets-glm.json](/D:/code/MyAttention/.runtime/delegation/results/ike-runtime-r0-e-memory-packets-glm.json)

### R0-F

- [D:\code\MyAttention\.runtime\delegation\briefs\ike-runtime-r0-f-redis-rebuild-glm.md](/D:/code/MyAttention/.runtime/delegation/briefs/ike-runtime-r0-f-redis-rebuild-glm.md)
- [D:\code\MyAttention\.runtime\delegation\contexts\ike-runtime-r0-f-redis-rebuild-glm.md](/D:/code/MyAttention/.runtime/delegation/contexts/ike-runtime-r0-f-redis-rebuild-glm.md)
- [D:\code\MyAttention\.runtime\delegation\results\ike-runtime-r0-f-redis-rebuild-glm.json](/D:/code/MyAttention/.runtime/delegation/results/ike-runtime-r0-f-redis-rebuild-glm.json)

## 5. Current Controller Judgment

The most appropriate first execution packet remains:

- `R0-A Core Runtime Schema Foundation`

The highest-risk semantic packet remains:

- `R0-B Compressed Task State Machine Semantics`

The packet most likely to drift into fake capability if rushed remains:

- `R0-E MemoryPacket Metadata and Acceptance`

## 6. Current Non-Negotiable Guardrails

The first-wave runtime build must preserve:

- Postgres as truth
- Redis as acceleration only
- `WorkContext` as reconstructable carrier, not second truth
- `MemoryPacket` as candidate/trusted snapshot, not autonomous truth
- controller review gate over reviewable work

## 6.1 Global Stop Conditions

Any first-wave runtime packet should stop and escalate to the controller if it
discovers:

1. required writes outside `allowed_files`
2. the current schema foundation is insufficient for the packet truthfully
3. a new first-class object is required
4. a packet requires task-state semantics that conflict with `R0-B`
5. Redis must store non-rebuildable canonical data
6. `MemoryPacket` trust would need to bypass controller review
7. `WorkContext` would need to store non-derivable canonical state

## 7. Immediate Next Step

If execution begins, start with:

- `R0-A`

Before `R0-B` and `R0-E` execute, run a controller pre-review on:

- compressed transition matrix completeness
- `MemoryPacket` trust-boundary completeness

If review continues before execution, review this first:

- packet order
- state/lease semantics
- memory trust boundaries

Do not start with:

- UI
- public APIs
- graph memory
- semantic retrieval
- notification mesh
