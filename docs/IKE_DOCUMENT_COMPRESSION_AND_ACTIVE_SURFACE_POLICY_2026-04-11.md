# IKE Document Compression And Active Surface Policy

Date: 2026-04-11
Status: controller policy

## Purpose

Keep durable documentation growth from turning into controller drag.

The fix is not "write fewer durable documents."

The fix is:

- active-surface compression
- stable index discipline
- explicit archive boundaries

## Problem

The project now correctly writes more durable artifacts than before.

That prevents chat-only memory loss, but it creates a new risk:

- too many documents become operationally "active"
- agents must re-open too much material to continue
- project memory becomes durable but hard to navigate

## Controller Rule

At any point, only a small subset of documents should be treated as the active
surface for continuation.

Everything else should remain durable but subordinate.

## Active Surface Layers

### Layer 1: shortest navigation layer

These are the first-read files:

- [D:\code\MyAttention\docs\CURRENT_MAINLINE_MAP_2026-04-10.md](/D:/code/MyAttention/docs/CURRENT_MAINLINE_MAP_2026-04-10.md)
- [D:\code\MyAttention\docs\CURRENT_MAINLINE_HANDOFF.md](/D:/code/MyAttention/docs/CURRENT_MAINLINE_HANDOFF.md)
- [D:\code\MyAttention\docs\IKE_UNIFIED_TASK_LANDSCAPE_2026-04-11.md](/D:/code/MyAttention/docs/IKE_UNIFIED_TASK_LANDSCAPE_2026-04-11.md)

### Layer 2: active line indexes

Each active line should have one primary index or packet entry.

Examples:

- runtime:
  - [D:\code\MyAttention\docs\CURRENT_RUNTIME_MAINLINE_INDEX_2026-04-10.md](/D:/code/MyAttention/docs/CURRENT_RUNTIME_MAINLINE_INDEX_2026-04-10.md)
- governance:
  - [D:\code\MyAttention\docs\IKE_DELIVERY_GOVERNANCE_INDEX_2026-04-11.md](/D:/code/MyAttention/docs/IKE_DELIVERY_GOVERNANCE_INDEX_2026-04-11.md)
- source intelligence start line:
  - [D:\code\MyAttention\docs\IKE_SOURCE_INTELLIGENCE_V1_IMPLEMENTATION_START_PACKET_2026-04-11.md](/D:/code/MyAttention/docs/IKE_SOURCE_INTELLIGENCE_V1_IMPLEMENTATION_START_PACKET_2026-04-11.md)

### Layer 3: packet/result documents

These remain durable evidence but should not all be treated as first-read
documents.

### Layer 4: archive/reference documents

Research notes, old packets, and historical phase documents remain important,
but should be opened only through an active index or packet.

## Compression Rules

1. New durable docs must link from one active index or packet.
2. No important line should require reading chat history to continue.
3. No active line should require opening many old result docs before the
   current index or packet.
4. If a line accumulates too many "current" documents, create a new compact
   index or consolidation packet.
5. Research documents do not become active-surface documents unless they are
   explicitly promoted.

## Promotion Rule For Documents

A document becomes part of the active surface only if it is one of:

- a current map
- a current handoff
- an active index
- a current implementation packet
- a current policy baseline

Otherwise it is durable support material, not first-read continuation material.

## Archive Rule

Older result documents remain valid evidence, but should be treated as archive
unless one of the current active-surface documents points back to them as still
needed.

## Operational Implication

When continuing the project:

1. start with the shortest map
2. open the active line index or current packet
3. open older results only when the active document says they matter

## Recommendation

`accept`

This policy should be treated as active controller discipline from now on.
