# IKE Source Intelligence V1 M1 Version Snapshot Context Result

Date: 2026-04-12
Status: bounded controller-coded patch

## Purpose

Close the next narrow continuity gap after refresh-route proof:

- live read paths already expose discovery context
- version snapshots still did not preserve that same context explicitly

This patch makes source-plan history snapshots carry the same bounded discovery
context used by the active read surface.

## Files Changed

- [D:\code\MyAttention\services\api\routers\feeds.py](/D:/code/MyAttention/services/api/routers/feeds.py)
- [D:\code\MyAttention\services\api\tests\test_source_plan_helpers.py](/D:/code/MyAttention/services/api/tests/test_source_plan_helpers.py)

## What Changed

### 1. Snapshot payloads now include discovery context

Source-plan snapshots now preserve:

- `task_intent`
- `interest_bias`
- `discovery_notes`
- `discovery_truth_boundary`

### 2. Initial version snapshots now record the same context

The first source-plan version snapshot created during plan creation now carries
the discovery context instead of storing only:

- topic
- focus
- objective
- items

### 3. Refresh-version snapshots now inherit context naturally

Because refresh snapshots are built from the live plan object, and the live plan
already carries persisted discovery context, the refresh version history now
stays aligned with:

- create-plan write path
- active read path
- refresh read path

## Validation Run

- `python -m unittest tests.test_source_discovery_contract tests.test_source_discovery_identity tests.test_source_plan_helpers tests.test_feeds_source_discovery_route`
- `python -m py_compile D:\code\MyAttention\services\api\routers\feeds.py D:\code\MyAttention\services\api\tests\test_source_discovery_contract.py D:\code\MyAttention\services\api\tests\test_source_plan_helpers.py D:\code\MyAttention\services\api\tests\test_feeds_source_discovery_route.py`

## Truth Boundary

- this improves historical continuity for source-plan context
- this does not add a new versioning subsystem
- this does not claim stronger search quality or evaluation quality
- this does not yet add a dedicated version-read API for discovery context diffing

## Known Risks

- version snapshots now contain more metadata, so future snapshot consumers
  should avoid assuming a minimal fixed shape
- there is still no dedicated test over the serialized `SourcePlanVersion`
  response surface
- context is preserved, but no higher-level controller experiment yet evaluates
  whether refreshes improved or degraded plan quality

## Recommendation

- `accept_with_changes`

Reason:

- the patch is narrow and fixes a real continuity gap in plan history
- but it remains one bounded hardening step inside the larger `M1` line
