# IKE v0 Task Packets

## Purpose

This document defines the first delegation-ready task packets for IKE v0.

It sits between:

- `docs/IKE_V0_DELEGATION_BACKLOG.md`
- the actual brief/context/result bundles under `.runtime/delegation/`

Its role is to freeze:

- who should do what
- which transport should be used
- what the first packets are

## Delegation Strategy

### Recommended role split

- `openclaw-glm`
  - primary coding delegate for bounded implementation slices using write-enabled coding mode
  - preferred current path for unattended bounded backend packets

- `openclaw-kimi`
  - analysis/reasoning/review delegate
  - best fit for semantic review, scope checking, alternative designs, and result critique

- `qoder`
  - secondary coding delegate
  - still useful for bounded coding work, but currently treated as semi-automatic rather than reliable unattended execution

### Role contracts

Project-level delegate contracts:

- coding:
  - [D:\code\MyAttention\.openclaw\agents\openclaw-glm-coding-agent.md](/D:/code/MyAttention/.openclaw/agents/openclaw-glm-coding-agent.md)
- review:
  - [D:\code\MyAttention\.openclaw\agents\openclaw-kimi-review-agent.md](/D:/code/MyAttention/.openclaw/agents/openclaw-kimi-review-agent.md)

### Current practical decision

For immediate IKE v0 work:

- use `openclaw-glm` for the first backend coding packets
- use `openclaw-kimi` for packet review/challenge
- keep `qoder` available for semi-automatic coding work where a human-in-the-loop handoff is acceptable

Reason:

- `openclaw-glm` is now viable for bounded coding packets when restricted with explicit allowed-write paths
- `kimi` is better used for analysis and review than as the primary coder
- `qoder` task launch works, but unattended completion is still not reliable enough to be the default coding path
- therefore the best current combination is:
  - `openclaw-glm` writes bounded code
  - `openclaw-kimi` reviews and analyzes
  - `qoder` remains available as a secondary coding lane

## Packet Rules

Every packet must include:

- one bounded task
- one role
- one result file
- one validation path

Every packet must avoid:

- repo-wide refactors
- broad folder moves
- strategy changes
- silent backend contract changes beyond the packet scope

If a semantic drift or contract mismatch is discovered during review:

- stop
- correct it immediately
- do not continue to later packets until the drift is removed

## First Packet Set

### Packet P1. Shared Envelope Schema Skeleton

Backlog task:

- `V0-A1`

Delegate:

- `openclaw-glm`

Review delegate:

- `openclaw-kimi`

Goal:

- add the minimum shared envelope schema skeleton for v0 objects

Expected outputs:

- schema skeleton location
- common envelope fields
- validation result

### Packet P2. Typed ID Helper Layer

Backlog task:

- `V0-A2`

Delegate:

- `openclaw-glm`

Review delegate:

- `openclaw-kimi`

Goal:

- add typed ID helpers/patterns for v0 object classes

Expected outputs:

- typed ID helper implementation
- tests
- validation result

### Packet P3. Observation Contract Adapter

Backlog task:

- `V0-B1`

Delegate:

- `openclaw-glm`

Review delegate:

- `openclaw-kimi`

Goal:

- wrap current `raw_ingest + feed_items` into explicit `Observation` v0 contract

Expected outputs:

- adapter/schema
- explicit observation shape
- bounded validation

### Packet P4. ResearchTask Schema And Adapter

Backlog task:

- `V0-C1`

Delegate:

- `openclaw-glm`

Review delegate:

- `openclaw-kimi`

Goal:

- map current task substrate into explicit `ResearchTask` v0 contract

Expected outputs:

- schema
- adapter
- state mapping notes

## Execution Rule

Do not launch all packets at once.

Recommended immediate order:

1. `P1`
2. `P2`

Then review.
Then decide whether to launch `P3`.

Reason:

- the first two packets establish the common contract shell
- later packets should build on reviewed contract decisions instead of freehand assumptions

## Review Rule

After each packet:

- the result must be reviewed before the next controller-heavy semantic packet advances
- `openclaw-kimi` review is advisory
- main-controller review is mandatory

## Definition of Success

This packet strategy is working if:

1. implementation begins without broad repo churn
2. coding delegates stay inside bounded slices
3. review delegates surface semantic drift early
4. accepted packets accumulate toward the v0 loop instead of producing disconnected patches

## API Transition Rule

For the first IKE API packets:

- prefer transitional operation-style endpoints
- avoid standard `GET /{type}/{id}` unless durable retrieval is real

This is now a controller decision, not an open question.

Reference:

- `docs/IKE_API_TRANSITION_PRINCIPLES.md`

## Next Milestone Rule

After the current transitional API packets, the next controller-approved
milestone is:

- one real inspectable loop

not:

- more isolated preview endpoints with no chain proof

That means future packets should increasingly support:

- real `ResearchTask` / `Experiment` mapping onto current substrates
- chain artifacts or inspect surfaces
- HarnessCase-backed validation of the full loop

References:

- `docs/IKE_MIGRATION_EXIT_CRITERIA.md`
- `docs/IKE_V0_1_LOOP_PLAN.md`

## Immediate Packet Priority After The Transitional API Seam

The next packet sequence should be:

1. `V0-L1 Shared Envelope Deduplication`
2. `V0-L2 ResearchTask Substrate Wiring`
3. `V0-L3 Experiment Stub Runtime Wiring`
4. `V0-L4 Chain Artifact / Inspect Surface`
5. `V0-L5 Harness Loop Validation`

Recommended delegate split:

- coding:
  - `openclaw-glm`
- analysis/review:
  - `openclaw-kimi`

Controller note:

- these packets should be launched one by one
- do not batch-launch the whole loop
- if semantic drift appears, stop and correct it immediately before the next packet
