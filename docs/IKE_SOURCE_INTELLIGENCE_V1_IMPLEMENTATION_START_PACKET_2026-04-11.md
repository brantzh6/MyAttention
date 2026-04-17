# IKE Source Intelligence V1 Implementation Start Packet

Date: 2026-04-11
Status: controller start packet

## Purpose

Provide one bounded packet that can be handed to a coding/review lane without
reconstructing the whole Source Intelligence history.

## Strategic Position

This packet implements the first narrow activation step for:

- [D:\code\MyAttention\docs\SOURCE_INTELLIGENCE_ARCHITECTURE.md](/D:/code/MyAttention/docs/SOURCE_INTELLIGENCE_ARCHITECTURE.md)
- [D:\code\MyAttention\docs\SOURCE_INTELLIGENCE_RESEARCH.md](/D:/code/MyAttention/docs/SOURCE_INTELLIGENCE_RESEARCH.md)
- [D:\code\MyAttention\docs\IKE_PROJECT_STRATEGIC_REVIEW_ABSORPTION_2026-04-11.md](/D:/code/MyAttention/docs/IKE_PROJECT_STRATEGIC_REVIEW_ABSORPTION_2026-04-11.md)
- [D:\code\MyAttention\docs\IKE_SOURCE_INTELLIGENCE_V1_M1_SCOPE_2026-04-11.md](/D:/code/MyAttention/docs/IKE_SOURCE_INTELLIGENCE_V1_M1_SCOPE_2026-04-11.md)
- [D:\code\MyAttention\docs\IKE_SOURCE_INTELLIGENCE_V1_M1_CODING_BRIEF_2026-04-11.md](/D:/code/MyAttention/docs/IKE_SOURCE_INTELLIGENCE_V1_M1_CODING_BRIEF_2026-04-11.md)
- [D:\code\MyAttention\docs\IKE_SOURCE_INTELLIGENCE_V1_M1_LANDING_DECISION_2026-04-11.md](/D:/code/MyAttention/docs/IKE_SOURCE_INTELLIGENCE_V1_M1_LANDING_DECISION_2026-04-11.md)
- [D:\code\MyAttention\docs\IKE_SOURCE_INTELLIGENCE_V1_M1_MINIMAL_WRITESET_2026-04-11.md](/D:/code/MyAttention/docs/IKE_SOURCE_INTELLIGENCE_V1_M1_MINIMAL_WRITESET_2026-04-11.md)
- [D:\code\MyAttention\docs\IKE_SOURCE_INTELLIGENCE_V1_M1_IMPLEMENTATION_TASK_PACKET_2026-04-11.md](/D:/code/MyAttention/docs/IKE_SOURCE_INTELLIGENCE_V1_M1_IMPLEMENTATION_TASK_PACKET_2026-04-11.md)

It is not a full implementation plan for all future source intelligence.

## Problem Statement

Current source quality is still too dependent on:

- fixed source lists
- ad hoc search
- manual source addition
- insufficiently explicit source/object classification

This weakens:

- research quality
- person/object discovery
- source-plan quality
- later memory and evolution quality

## M1 Goal

Build one narrow `topic -> candidate source intelligence result` path.

Input:

- topic or target
- optional task intent
- optional interest bias such as:
  - authority
  - frontier
  - community
  - method

Output:

- candidate objects
- candidate endpoints or source handles
- bounded V1 classification
- recommended monitoring mode
- recommended execution strategy
- review notes / confidence notes

## Preferred M1 Shape

The first implementation should prefer a narrow service/helper boundary over a
broad product rewrite.

Suggested minimal shape:

1. one request model
2. one source-discovery/classification helper
3. one inspect-style route or bounded service entry
4. one structured response model
5. focused tests

This keeps the line controller-reviewable and easy to compare across models.

## Minimum Response Shape

At minimum, each candidate should carry:

- `object_name`
- `object_type`
- `source_nature`
- `temperature`
- `recommended_mode`
- `recommended_execution_strategy`
- `why_relevant`
- `confidence_note`

Optional but useful:

- `canonical_ref`
- `candidate_endpoints`
- `authority_signals`
- `frontier_signals`
- `community_signals`

## Scope Rule

Do not try to solve all of these in M1:

- durable schema finalization
- automated promote/demote/retire lifecycle
- full subscription system
- collector replacement
- multi-step agent orchestration
- UI management surface

M1 is only the first trustworthy upstream planning capability.

## Suggested Landing Area

Preferred coding direction:

- keep the first implementation inside the API/runtime-adjacent service layer
  or a similarly narrow backend module
- avoid wiring it directly into every existing feed workflow
- keep the first public surface inspect-style or explicitly non-authoritative

Reason:

- source intelligence is not yet canonical truth
- the first goal is improving planning and candidate quality, not silently
  taking over the whole collector path

## Acceptance Criteria

The first implementation is good enough for `accept_with_changes` or better if
it satisfies all of the following:

1. topic-driven input exists
2. multiple candidate objects/sources can be returned
3. output uses explicit V1 classification instead of raw URL dumping
4. monitoring/execution recommendation is present
5. behavior and claims stay narrow and truthful
6. focused tests exist
7. no broad fetcher rewrite is mixed in

## Validation Expectations

At minimum:

- focused unit tests for the helper or route
- request/response shape validation
- compile or import-level validation for touched modules

If the implementation reaches routing:

- one narrow router test slice

## Known Risks

- V1 may overfit to topic-to-source shortcuts if object modeling is too weak
- LLM-assisted discovery may produce plausible but low-value candidates
- implementers may drift into full source-management system design
- output taxonomy may be too ambitious for the first coding slice

## Recommendation

`accept`

The next step should be one bounded coding packet for `Source Intelligence V1
M1`, not more pure architecture discussion.
