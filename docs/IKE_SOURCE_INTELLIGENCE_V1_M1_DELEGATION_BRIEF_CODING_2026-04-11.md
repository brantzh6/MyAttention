# IKE Source Intelligence V1 M1 Delegation Brief - Coding

## Goal

Implement one bounded `Source Intelligence V1 M1` improvement on the existing
source-discovery/source-plan path.

## Primary Landing Area

- [D:\code\MyAttention\services\api\routers\feeds.py](/D:/code/MyAttention/services/api/routers/feeds.py)

## Constraints

1. Do not create a parallel source-intelligence subsystem.
2. Do not widen into collector replacement.
3. Keep the patch narrow and mostly `feeds.py`-centric.
4. Keep truth-boundary language explicit.
5. Do not overclaim source quality.

## Preferred Improvement Direction

Improve one or more of:

- candidate object richness
- person/object discovery quality
- strategy recommendation clarity
- source-plan output coherence

## Preferred Validation

- focused source-discovery/source-plan tests
- import/compile validation for touched files

## Required Return Format

1. `summary`
2. `files_changed`
3. `why_this_solution`
4. `validation_run`
5. `known_risks`
6. `recommendation`
