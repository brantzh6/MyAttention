# IKE Source Intelligence V1 - M4 Plan

Date: 2026-04-13
Phase: `M4 Same-Repo Release Duplicate Compression In LATEST/FRONTIER`
Status: `active`

## Scope

Only compress one overlap family:

- `repository`
- `release`
- same repo
- `LATEST` / `FRONTIER` only

## Write Surface

- [D:\code\MyAttention\services\api\routers\feeds.py](/D:/code/MyAttention/services/api/routers/feeds.py)
- [D:\code\MyAttention\services\api\tests\test_source_discovery_identity.py](/D:/code/MyAttention/services/api/tests/test_source_discovery_identity.py)
- [D:\code\MyAttention\services\api\tests\test_feeds_source_discovery_route.py](/D:/code/MyAttention/services/api/tests/test_feeds_source_discovery_route.py)

## Planned Change

1. identify same-repo `release` and `repository` overlap
2. apply compression only in `LATEST` and `FRONTIER`
3. keep `METHOD` unchanged because repository remains a primary implementation
   object there
4. keep repository when release is not materially competitive

## Validation

1. helper-level overlap tests
2. route-level proof on `/api/sources/discover`
3. focused regression run on current source-discovery slices

## Truth Boundary

This slice does not claim broad release superiority.

It only claims that inside `LATEST` / `FRONTIER`, a materially competitive
`release` candidate can suppress the same-repo `repository` duplicate.
