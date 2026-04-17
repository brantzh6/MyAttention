# IKE Source Intelligence V1 M1 Version Route Evaluation Proof Result

Date: 2026-04-12
Status: bounded controller-coded proof

## Purpose

Prove that the existing version read surface does not only expose bounded
discovery context summary, but also continues to expose the existing refresh
evaluation evidence:

- `change_summary`
- `evaluation`

This keeps the route aligned with the next `repeated refresh / evaluation`
phase without opening a new comparison API.

## Files Changed

- [D:\code\MyAttention\services\api\tests\test_feeds_source_discovery_route.py](/D:/code/MyAttention/services/api/tests/test_feeds_source_discovery_route.py)
- [D:\code\MyAttention\services\api\routers\feeds.py](/D:/code/MyAttention/services/api/routers/feeds.py)

## What Changed

### 1. Added route-level proof for evaluation visibility

The isolated `GET /api/sources/plans/{plan_id}/versions` route test now proves
that one version item can expose:

- bounded context summary
- `change_summary.summary`
- `evaluation.decision_status`
- `evaluation.gate_signals`

on the same read surface.

### 2. Restored backward compatibility in snapshot helpers

During this proof step, existing helper tests exposed two backward-compatibility
gaps:

- `_snapshot_source_plan` assumed `plan.extra` always existed
- snapshot item normalization assumed `item_type` always existed

Both were corrected with safe defaults.

## Validation Run

- `python -m unittest tests.test_source_discovery_contract tests.test_source_discovery_identity tests.test_source_plan_helpers tests.test_feeds_source_discovery_route tests.test_source_plan_versioning_helpers`
- `python -m py_compile D:\code\MyAttention\services\api\routers\feeds.py D:\code\MyAttention\services\api\tests\test_source_discovery_contract.py D:\code\MyAttention\services\api\tests\test_source_plan_helpers.py D:\code\MyAttention\services\api\tests\test_feeds_source_discovery_route.py D:\code\MyAttention\services\api\tests\test_source_plan_versioning_helpers.py`

## Truth Boundary

- this is route-level proof for existing read-surface visibility
- this does not add comparison or diff APIs
- this does not claim refresh quality is good, only that quality signals remain visible
- this does not promote `Source Intelligence V1 M1` to a finished milestone

## Recommendation

- `accept_with_changes`
