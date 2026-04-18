# IKE AI-Native Direction Design Review Pack

Date: 2026-04-18
Status: controller review pack

## Purpose

Provide one compact package for reviewing the next IKE direction step as a
single design story:

1. `Conversation Runtime Phase 0`
2. `Worker Skill / Harness Integration`

The point is to make the next direction explicit before implementation starts.

This pack is not an implementation result.

## Stable Framing

Before reviewing this packet, keep these four layers fixed:

1. project vision remains unchanged:
   - IKE is an AI-driven evolution system
2. current design expression is layered:
   - information brain
   - knowledge brain
   - evolution brain
   - world model as a cross-cutting layer
   - thinking tools / scientific methodology as a cross-cutting layer
3. current architecture is staged:
   - `Runtime v0` is accepted substrate
   - `Source Intelligence V1` is proven substrate above runtime
4. implementation path may change:
   - the next path is now a bounded conversation-to-object entry slice
   - plus a worker-skill support track that IKE harness loads and governs

## Why This Pack Exists

The project has two adjacent missing bridges:

- conversation to typed candidate objects
- worker implementation to harness-governed skill

Both bridges sit above the already-proven substrate:

- `Source Intelligence V1 M1-M13`
- `feeds.ai_judgment.py`
- selective absorption advisory
- `Runtime v0`
- `claude-worker` as the first concrete worker implementation

The next step should extend those substrates rather than create parallel
systems.

## Current Controller Judgment

### Direction A - Conversation Runtime Phase 0

The next bounded packet should be:

`Conversation -> SourceCandidate + CorrectionEvent`

Why these two object families:

- `SourceCandidate` proves conversation can produce discovery material
- `CorrectionEvent` proves conversation can produce calibration/correction
  material

Both remain:

- candidate-only
- inspect/review only
- non-canonical until reviewed

### Direction B - Worker Skill / Harness Integration

The worker should be treated as a versioned skill that the IKE harness can
load, validate, execute, and audit.

The first concrete implementation is `claude-worker`.

The worker track also needs a uniform model-switching contract so all workers
can expose the same multi-model selection surface to IKE.

## Proposed Phase 0 Shapes

### Conversation Runtime Phase 0

#### Input

- one bounded conversation segment

#### Minimal classification

- `source_hint`
- `correction`
- `other`

#### Minimal outputs

- `SourceCandidate`
- `CorrectionEvent`

#### Required reuse

- existing source-intelligence candidate path
- existing AI judgment substrate where applicable
- existing selective absorption advisory shape where applicable
- existing runtime trust semantics

#### Required truth boundary

- raw conversation is not truth
- raw conversation is not memory
- raw conversation is not direct source state
- raw conversation is not direct correction truth

### Worker Skill / Harness Integration

#### Required skill shape

- identity
- version/ref
- supported execution modes
- provider/model requirements
- model switching interface
- prompt delivery policy
- artifact/result schema
- trust level
- validation hooks
- stop conditions

#### Required harness duties

1. fetch the skill from a versioned source
2. validate the contract before execution
3. inject execution context
4. collect durable artifacts
5. enforce trust boundaries
6. validate model/provider selection
7. hand the result back to controller review

#### Required trust boundary

The worker may execute tasks.

It may not redefine:

- project priorities
- acceptance criteria
- runtime truth
- AI evolution direction

## Explicit Non-Goals

This package is not:

- a generic chat product shell
- a full conversation runtime
- a multi-agent runtime rollout
- a workflow automation system
- a memory-packet promotion engine
- a generic approval/voting platform
- a worker marketplace
- a multi-agent orchestration protocol

## Files In This Review

### Direction baseline

- [IKE_AI_Native_Multi_Brain_Conversation_Runtime_Plan_v0.2_EN.md](/D:/code/MyAttention/docs/IKE_AI_Native_Multi_Brain_Conversation_Runtime_Plan_v0.2_bundle/ike_ai_native_conversation_runtime_v02/md/IKE_AI_Native_Multi_Brain_Conversation_Runtime_Plan_v0.2_EN.md)
- [IKE_AI_NATIVE_CONVERSATION_RUNTIME_V02_REVIEW_ABSORPTION_2026-04-18.md](/D:/code/MyAttention/docs/IKE_AI_NATIVE_CONVERSATION_RUNTIME_V02_REVIEW_ABSORPTION_2026-04-18.md)
- [IKE_VISION_DESIGN_ARCHITECTURE_PATH_ALIGNMENT_2026-04-17.md](/D:/code/MyAttention/docs/IKE_VISION_DESIGN_ARCHITECTURE_PATH_ALIGNMENT_2026-04-17.md)

### Conversation runtime packet

- [IKE_CONVERSATION_RUNTIME_P0_PHASE_JUDGMENT_2026-04-18.md](/D:/code/MyAttention/docs/IKE_CONVERSATION_RUNTIME_P0_PHASE_JUDGMENT_2026-04-18.md)
- [IKE_CONVERSATION_RUNTIME_P0_PLAN_2026-04-18.md](/D:/code/MyAttention/docs/IKE_CONVERSATION_RUNTIME_P0_PLAN_2026-04-18.md)
- [IKE_CONVERSATION_RUNTIME_P0_EXECUTION_PACKET_2026-04-18.md](/D:/code/MyAttention/docs/IKE_CONVERSATION_RUNTIME_P0_EXECUTION_PACKET_2026-04-18.md)

### Worker skill packet

- [IKE_WORKER_SKILL_CONTRACT_2026-04-18.md](/D:/code/MyAttention/docs/IKE_WORKER_SKILL_CONTRACT_2026-04-18.md)
- [IKE_WORKER_SKILL_PHASE_JUDGMENT_2026-04-18.md](/D:/code/MyAttention/docs/IKE_WORKER_SKILL_PHASE_JUDGMENT_2026-04-18.md)
- [IKE_WORKER_SKILL_PHASE0_PLAN_2026-04-18.md](/D:/code/MyAttention/docs/IKE_WORKER_SKILL_PHASE0_PLAN_2026-04-18.md)
- [IKE_WORKER_MODEL_SWITCHING_STANDARD_2026-04-18.md](/D:/code/MyAttention/docs/IKE_WORKER_MODEL_SWITCHING_STANDARD_2026-04-18.md)
- [IKE_WORKER_SKILL_IMPORT_AND_VALIDATION_SPEC_2026-04-18.md](/D:/code/MyAttention/docs/IKE_WORKER_SKILL_IMPORT_AND_VALIDATION_SPEC_2026-04-18.md)

### Implementation reference

- [D:\code\claude-worker\README.md](/D:/code/claude-worker/README.md)

## What Reviewers Should Judge

1. Is the direction shift correct?
2. Is Phase 0 narrow enough?
3. Is `SourceCandidate + CorrectionEvent` the right first pair?
4. Is the worker-skill contract the right abstraction?
5. Is `claude-worker` a valid first implementation?
6. Is model switching standardized across workers?
7. Is substrate reuse specified clearly enough?
8. Is the trust boundary explicit and strong enough?
9. Should this direction packet be:
   - `accept`
   - `accept_with_changes`
   - `reject`
