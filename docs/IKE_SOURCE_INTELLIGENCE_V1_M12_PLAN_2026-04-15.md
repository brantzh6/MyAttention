# IKE Source Intelligence V1 M12 Plan

Date: 2026-04-15
Status: implementation plan

## Goal

Add one inspect-only dual-model panel route for source-plan version change targets.

## Writeset

- `services/api/routers/feeds.py`
- `services/api/tests/test_feeds_source_discovery_route.py`

## Planned Work

1. Add bounded request/response models for version panel inspect.
2. Reuse the existing version target extraction from `M11`.
3. Reuse the existing panel substrate for:
   - provider-aware default model resolution
   - JSON parse fallback
   - overlap comparison
   - disagreement/consensus insight derivation
4. Add one focused route proof.

## Truth Boundary

- inspect-only
- non-mutating
- no merged canonical version verdict
- disagreement shape is exposed as advisory signal only
