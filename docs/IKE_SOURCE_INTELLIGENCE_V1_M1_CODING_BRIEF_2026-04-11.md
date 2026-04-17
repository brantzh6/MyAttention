# IKE Source Intelligence V1 M1 Coding Brief

Date: 2026-04-11
Status: controller coding brief

## Task

Implement a bounded `Source Intelligence V1 M1` backend slice:

- input: topic-oriented discovery request
- output: structured candidate source/object intelligence result

## Required Constraints

1. Keep the patch narrow.
2. Do not rewrite the existing collector/fetcher stack.
3. Do not introduce a broad source-management subsystem.
4. Keep the first surface inspect-style or explicitly non-authoritative.
5. Make truth boundaries explicit in code and response shape.

## Required Capability

The implementation must support:

- topic-driven input
- multiple candidates
- bounded V1 candidate classification
- explicit monitoring/review/execution recommendation
- explanation/confidence notes

## Suggested Candidate Fields

- `object_name`
- `object_type`
- `source_nature`
- `temperature`
- `recommended_mode`
- `recommended_execution_strategy`
- `why_relevant`
- `confidence_note`

## Preferred Write Set

Prefer a small write set similar to:

- one helper module
- one router module extension or one narrow service entry
- one focused test module
- minimal schema/model additions only if truly required

## Validation

At minimum, run:

- focused unit tests for the helper or route
- request/response validation
- compile or import-level validation for touched modules

If a route is added, also run:

- one focused router test slice

## Non-Goals

- no full source-plan persistence system
- no subscription lifecycle
- no collector replacement
- no UI control surface
- no fake claim of research-grade or canonical source intelligence

## Delivery Format

Return:

1. `summary`
2. `files_changed`
3. `why_this_solution`
4. `validation_run`
5. `known_risks`
6. `recommendation`

## Recommendation Target

Default acceptance target:

- `accept_with_changes`

Raise to `accept` only if the implementation stays narrow, passes focused
validation, and does not overclaim.
