# IKE Source Intelligence V1 M1 Claude Send Package

Date: 2026-04-11
Status: controller send package

## Purpose

Provide the shortest package I can hand to Claude Code for the first
`Source Intelligence V1 M1` coding lane.

## What Claude Should Do

Implement one bounded improvement on the existing source-discovery and
source-plan path.

Primary landing area:

- [D:\code\MyAttention\services\api\routers\feeds.py](/D:/code/MyAttention/services/api/routers/feeds.py)

## What Claude Must Not Do

1. Do not create a second source-intelligence subsystem.
2. Do not widen into collector replacement.
3. Do not broaden into UI work.
4. Do not overclaim source quality.
5. Do not rewrite unrelated areas.

## Preferred Test Surface

- [D:\code\MyAttention\services\api\tests\test_source_discovery_identity.py](/D:/code/MyAttention/services/api/tests/test_source_discovery_identity.py)
- [D:\code\MyAttention\services\api\tests\test_source_plan_helpers.py](/D:/code/MyAttention/services/api/tests/test_source_plan_helpers.py)
- [D:\code\MyAttention\services\api\tests\test_source_plan_versioning_helpers.py](/D:/code/MyAttention/services/api/tests/test_source_plan_versioning_helpers.py)
- [D:\code\MyAttention\services\api\tests\test_source_plan_review_issues.py](/D:/code/MyAttention/services/api/tests/test_source_plan_review_issues.py)

## Best Entry Files

- [D:\code\MyAttention\docs\IKE_SOURCE_INTELLIGENCE_V1_M1_DELIVERY_PACK_2026-04-11.md](/D:/code/MyAttention/docs/IKE_SOURCE_INTELLIGENCE_V1_M1_DELIVERY_PACK_2026-04-11.md)
- [D:\code\MyAttention\docs\IKE_SOURCE_INTELLIGENCE_V1_M1_MULTI_AGENT_PACKET_2026-04-11.md](/D:/code/MyAttention/docs/IKE_SOURCE_INTELLIGENCE_V1_M1_MULTI_AGENT_PACKET_2026-04-11.md)

## Direct Delegation Files

- coding brief:
  - [D:\code\MyAttention\.runtime\delegation\source_intelligence_v1_m1_coding_brief.txt](/D:/code/MyAttention/.runtime/delegation/source_intelligence_v1_m1_coding_brief.txt)
- coding context:
  - [D:\code\MyAttention\.runtime\delegation\source_intelligence_v1_m1_coding_context.txt](/D:/code/MyAttention/.runtime/delegation/source_intelligence_v1_m1_coding_context.txt)
- coding prompt:
  - [D:\code\MyAttention\.runtime\delegation\source_intelligence_v1_m1_coding_prompt.txt](/D:/code/MyAttention/.runtime/delegation/source_intelligence_v1_m1_coding_prompt.txt)

## Required Return Format

Claude should return:

1. `summary`
2. `files_changed`
3. `why_this_solution`
4. `validation_run`
5. `known_risks`
6. `recommendation`

## Controller Expectation

Default target:

- `accept_with_changes`

Raise to `accept` only if the patch stays narrow, validation is focused, and
the result clearly improves the existing `feeds.py` path without semantic
drift.
