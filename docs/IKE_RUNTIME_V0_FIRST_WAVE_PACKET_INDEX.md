# IKE Runtime v0 First-Wave Packet Index

## Purpose

This is the shortest controller-facing index for the first implementation wave
of `IKE Runtime v0`.

Use it when:

- selecting the next runtime packet
- handing runtime work to a coding delegate
- triggering external architecture or implementation review

## Packet Order

1. [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R0-A_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R0-A_BRIEF.md)
   - Core Runtime Schema Foundation
2. [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R0-B_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R0-B_BRIEF.md)
   - Compressed Task State Machine Semantics
3. [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R0-C_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R0-C_BRIEF.md)
   - Task Event Log and Lease Semantics
4. [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R0-D_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R0-D_BRIEF.md)
   - WorkContext Snapshot Carrier
5. [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R0-E_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R0-E_BRIEF.md)
   - MemoryPacket Metadata and Acceptance
6. [D:\code\MyAttention\docs\IKE_RUNTIME_V0_PACKET_R0-F_BRIEF.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_PACKET_R0-F_BRIEF.md)
   - Redis Acceleration and Recovery Rebuild

## Current Controller Guidance

Start with:

- `R0-A`

Do not skip ahead to:

- `R0-D`
- `R0-E`
- `R0-F`

unless the earlier kernel truth model is already implemented and reviewed.

## Review Focus by Packet

### R0-A

- canonical object shape
- schema reversibility
- no hidden future scope

### R0-B

- state semantics
- illegal transition blocking
- no fake completion

### R0-C

- append-only events
- lease expiry correctness
- recovery truthfulness

### R0-D

- no second truth source
- reconstructability

### R0-E

- trust boundaries
- accepted-upstream linkage
- no fake memory trust

### R0-F

- Redis remains acceleration only
- Postgres remains rebuild source

## Required Companion Docs

Reviewers or delegates should read these before implementation:

- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_IMPLEMENTATION_READINESS.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_IMPLEMENTATION_READINESS.md)
- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_DELEGATION_BACKLOG.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_DELEGATION_BACKLOG.md)
- [D:\code\MyAttention\docs\PROJECT_AGENT_HARNESS_CONTRACT.md](/D:/code/MyAttention/docs/PROJECT_AGENT_HARNESS_CONTRACT.md)
