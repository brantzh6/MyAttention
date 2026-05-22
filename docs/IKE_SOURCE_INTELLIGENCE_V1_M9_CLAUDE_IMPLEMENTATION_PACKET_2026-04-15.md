# IKE Source Intelligence V1 - M9 Claude Implementation Packet

Date: 2026-04-15
Status: controller delegation packet

## Task

Improve the current multi-model panel inspect lane so it is not merely a
dispatch-and-aggregate surface.

The goal is to make panel output more useful for AI-driven review and decision
work by turning agreement and disagreement into structured insight.

## Current Landing Area

- [D:\code\MyAttention\services\api\routers\feeds.py](/D:/code/MyAttention/services/api/routers/feeds.py)
- [D:\code\MyAttention\services\api\tests\test_feeds_source_discovery_route.py](/D:/code/MyAttention/services/api/tests/test_feeds_source_discovery_route.py)

## Current Baseline

The current route is:

- `POST /api/sources/discover/judge/panel/inspect`

It already:

1. reuses the existing discovery path
2. runs two model lanes independently
3. returns primary/secondary judgments separately
4. exposes agreement/disagreement counts

It does **not yet** provide enough insight for controller-level review.

## What To Improve

Keep the route inspect-only, but improve the returned panel structure so it
surfaces more than counts.

Examples of acceptable bounded improvements:

1. per-object panel comparison objects
   - object_key
   - primary verdict
   - secondary verdict
   - agreement/disagreement label
   - disagreement significance
2. bounded panel insight summary
   - consensus candidates
   - divergence candidates
   - likely opportunity candidates
   - uncertainty-heavy candidates
3. honest notes that explain why disagreement may be valuable instead of noisy

## What Not To Do

1. do not add persistence
2. do not write source plans
3. do not auto-follow or auto-subscribe
4. do not create a generic workflow engine
5. do not widen into generalized multi-agent orchestration
6. do not replace the current panel with a hidden merged verdict

## Validation Expectations

Add focused tests only.

Preferred validation:

- `python -m unittest tests.test_feeds_source_discovery_route tests.test_source_discovery_identity tests.test_source_plan_helpers tests.test_source_discovery_contract tests.test_attention_policy_foundation`
- `python -m py_compile D:\code\MyAttention\services\api\routers\feeds.py D:\code\MyAttention\services\api\tests\test_feeds_source_discovery_route.py`

## Required Return Format

Return:

1. `summary`
2. `files_changed`
3. `why_this_solution`
4. `validation_run`
5. `known_risks`
6. `recommendation`

## Controller Recommendation Target

- `accept_with_changes`

Raise to `accept` only if the patch stays narrow and the improved panel output
is clearly more insight-oriented without semantic drift.
