# IKE Source Intelligence V1 M11 Plan

Date: 2026-04-15
Status: implementation plan

## Goal

Add one inspect-only route that runs advisory AI judgment over bounded
`source-plan` version changes.

## Writeset

- `services/api/routers/feeds.py`
- `services/api/tests/test_source_plan_versioning_helpers.py`
- `services/api/tests/test_feeds_source_discovery_route.py`

## Planned Work

1. Add bounded request/response models for version-change judgment inspect.
2. Build one helper that extracts judgment targets from persisted version diff/snapshot data.
3. Add one inspect-only route:
   - `POST /api/sources/plans/{plan_id}/versions/{version_number}/judge/inspect`
4. Reuse the existing AI judgment substrate for:
   - default model resolution
   - JSON parse fallback
   - normalized `follow|review|ignore` verdicts
5. Add focused helper and route proofs.

## Truth Boundary

- advisory only
- inspect only
- no canonical decision override
- no persistence
