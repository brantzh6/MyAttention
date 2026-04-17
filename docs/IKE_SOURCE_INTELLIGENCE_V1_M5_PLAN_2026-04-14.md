# IKE Source Intelligence V1 - M5 Plan

Date: 2026-04-14
Phase: `M5 Contextual Media Article Signal Classification`
Status: `active`

## Scope

Only improve one narrow quality family:

- contextual tech-media article pages
- `LATEST` / `FRONTIER`
- classify as `signal`

## Write Surface

- [D:\code\MyAttention\services\api\routers\feeds.py](/D:/code/MyAttention/services/api/routers/feeds.py)
- [D:\code\MyAttention\services\api\tests\test_source_discovery_identity.py](/D:/code/MyAttention/services/api/tests/test_source_discovery_identity.py)
- [D:\code\MyAttention\services\api\tests\test_feeds_source_discovery_route.py](/D:/code/MyAttention/services/api/tests/test_feeds_source_discovery_route.py)

## Planned Change

1. recognize contextual tech-media article pages from a bounded publisher set
   as `signal`
2. keep section/tag/search/about pages outside the rule
3. keep `METHOD` on the older conservative path

## Validation

1. helper-level classification proof
2. route-level `/api/sources/discover` proof
3. focused regression run on current source-discovery slices

## Truth Boundary

This slice does not claim that contextual media is authoritative.

It only claims that concrete article pages from a bounded publisher set are
better treated as `signal` than as flat `domain` entries in
`LATEST` / `FRONTIER`.
