# IKE Source Intelligence V1 M1 Implementation Task Packet

Date: 2026-04-11
Status: controller task packet

## Goal

Deliver one bounded `Source Intelligence V1 M1` backend slice by tightening or
enhancing the existing source-discovery/source-plan path.

## Primary References

- [D:\code\MyAttention\docs\IKE_SOURCE_INTELLIGENCE_V1_IMPLEMENTATION_START_PACKET_2026-04-11.md](/D:/code/MyAttention/docs/IKE_SOURCE_INTELLIGENCE_V1_IMPLEMENTATION_START_PACKET_2026-04-11.md)
- [D:\code\MyAttention\docs\IKE_SOURCE_INTELLIGENCE_V1_M1_SCOPE_2026-04-11.md](/D:/code/MyAttention/docs/IKE_SOURCE_INTELLIGENCE_V1_M1_SCOPE_2026-04-11.md)
- [D:\code\MyAttention\docs\IKE_SOURCE_INTELLIGENCE_V1_M1_CODING_BRIEF_2026-04-11.md](/D:/code/MyAttention/docs/IKE_SOURCE_INTELLIGENCE_V1_M1_CODING_BRIEF_2026-04-11.md)
- [D:\code\MyAttention\docs\IKE_SOURCE_INTELLIGENCE_V1_M1_LANDING_DECISION_2026-04-11.md](/D:/code/MyAttention/docs/IKE_SOURCE_INTELLIGENCE_V1_M1_LANDING_DECISION_2026-04-11.md)
- [D:\code\MyAttention\docs\IKE_SOURCE_INTELLIGENCE_V1_M1_MINIMAL_WRITESET_2026-04-11.md](/D:/code/MyAttention/docs/IKE_SOURCE_INTELLIGENCE_V1_M1_MINIMAL_WRITESET_2026-04-11.md)

## Task Shape

Use the existing:

- `POST /sources/discover`
- `POST /sources/plans`
- source-plan helper path

as the primary landing area.

## Required Constraints

1. Do not create a second parallel source-intelligence subsystem.
2. Do not widen into collector replacement.
3. Keep the patch mostly inside `feeds.py` plus focused tests.
4. Keep response truth boundaries explicit.
5. Do not overclaim source quality.

## Desired Improvement Direction

Improve one or more of the following in a bounded way:

- candidate object richness
- person/object discovery quality
- strategy recommendation clarity
- inspect-style output clarity
- source-plan input/output coherence

## Validation

At minimum, run focused source-discovery/source-plan tests and compile/import
checks for touched files.

## Delivery

Return:

1. `summary`
2. `files_changed`
3. `why_this_solution`
4. `validation_run`
5. `known_risks`
6. `recommendation`

## Recommendation Target

Default target:

- `accept_with_changes`

Raise to `accept` only if the patch stays narrow and clearly improves the
current source-discovery/source-plan path without semantic drift.
