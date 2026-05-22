# IKE Source Intelligence V1 M1 Delivery Pack

Date: 2026-04-11
Status: controller delivery pack

## Purpose

Provide one single-file handoff for the first `Source Intelligence V1 M1`
coding lane.

This file exists so another model or engineer can start the bounded packet
without reconstructing the whole strategic context.

## Goal

Deliver one bounded backend improvement on the existing source-discovery and
source-plan path.

## Strategic Position

- `Runtime v0` remains the true active mainline
- `Source Intelligence V1` is the next product-capability start line
- this packet is the first concrete M1 coding slice for that line

## Required Landing Area

Prefer landing on the existing source-discovery/source-plan implementation in:

- [D:\code\MyAttention\services\api\routers\feeds.py](/D:/code/MyAttention/services/api/routers/feeds.py)

Do not start by creating a second parallel source-intelligence subsystem.

## Existing Relevant Behavior

The project already has:

- `SourceDiscoveryFocus`
- `SourceDiscoveryRequest`
- `SourceDiscoveryCandidate`
- `POST /sources/discover`
- `POST /sources/plans`
- source-plan refresh/version helpers
- focused tests around discovery identity and source-plan helpers

## M1 Goal

Improve one or more of the following in a bounded way:

- candidate object richness
- person/object discovery quality
- strategy recommendation clarity
- inspect-style output clarity
- source-plan input/output coherence

## Constraints

1. Do not rewrite the collector/fetcher stack.
2. Do not widen into broad schema design.
3. Keep the patch mostly inside `feeds.py` plus focused tests.
4. Keep truth-boundary language explicit.
5. Do not overclaim source quality or research-grade behavior.

## Preferred Write Set

Primary file:

- [D:\code\MyAttention\services\api\routers\feeds.py](/D:/code/MyAttention/services/api/routers/feeds.py)

Preferred focused tests:

- [D:\code\MyAttention\services\api\tests\test_source_discovery_identity.py](/D:/code/MyAttention/services/api/tests/test_source_discovery_identity.py)
- [D:\code\MyAttention\services\api\tests\test_source_plan_helpers.py](/D:/code/MyAttention/services/api/tests/test_source_plan_helpers.py)
- [D:\code\MyAttention\services\api\tests\test_source_plan_versioning_helpers.py](/D:/code/MyAttention/services/api/tests/test_source_plan_versioning_helpers.py)
- [D:\code\MyAttention\services\api\tests\test_source_plan_review_issues.py](/D:/code/MyAttention/services/api/tests/test_source_plan_review_issues.py)

## Validation

At minimum:

- focused source-discovery/source-plan test execution
- import/compile validation for touched files

## Delivery Format

Return:

1. `summary`
2. `files_changed`
3. `why_this_solution`
4. `validation_run`
5. `known_risks`
6. `recommendation`

## References

- [D:\code\MyAttention\docs\IKE_SOURCE_INTELLIGENCE_V1_IMPLEMENTATION_START_PACKET_2026-04-11.md](/D:/code/MyAttention/docs/IKE_SOURCE_INTELLIGENCE_V1_IMPLEMENTATION_START_PACKET_2026-04-11.md)
- [D:\code\MyAttention\docs\IKE_SOURCE_INTELLIGENCE_V1_M1_SCOPE_2026-04-11.md](/D:/code/MyAttention/docs/IKE_SOURCE_INTELLIGENCE_V1_M1_SCOPE_2026-04-11.md)
- [D:\code\MyAttention\docs\IKE_SOURCE_INTELLIGENCE_V1_M1_CODING_BRIEF_2026-04-11.md](/D:/code/MyAttention/docs/IKE_SOURCE_INTELLIGENCE_V1_M1_CODING_BRIEF_2026-04-11.md)
- [D:\code\MyAttention\docs\IKE_SOURCE_INTELLIGENCE_V1_M1_LANDING_DECISION_2026-04-11.md](/D:/code/MyAttention/docs/IKE_SOURCE_INTELLIGENCE_V1_M1_LANDING_DECISION_2026-04-11.md)
- [D:\code\MyAttention\docs\IKE_SOURCE_INTELLIGENCE_V1_M1_MINIMAL_WRITESET_2026-04-11.md](/D:/code/MyAttention/docs/IKE_SOURCE_INTELLIGENCE_V1_M1_MINIMAL_WRITESET_2026-04-11.md)
- [D:\code\MyAttention\docs\IKE_SOURCE_INTELLIGENCE_V1_M1_IMPLEMENTATION_TASK_PACKET_2026-04-11.md](/D:/code/MyAttention/docs/IKE_SOURCE_INTELLIGENCE_V1_M1_IMPLEMENTATION_TASK_PACKET_2026-04-11.md)
- [D:\code\MyAttention\docs\IKE_SOURCE_INTELLIGENCE_V1_M1_MULTI_AGENT_PACKET_2026-04-11.md](/D:/code/MyAttention/docs/IKE_SOURCE_INTELLIGENCE_V1_M1_MULTI_AGENT_PACKET_2026-04-11.md)
