# IKE Source Intelligence V1 - M6 Plan

Date: 2026-04-14
Phase: `M6 GitHub Repo Thread Signal Classification`
Status: `active`

## Scope

Only improve one narrow quality family:

- GitHub repo issue pages
- GitHub repo discussion pages
- GitHub repo pull-request pages

## Write Surface

- [D:\code\MyAttention\services\api\routers\feeds.py](/D:/code/MyAttention/services/api/routers/feeds.py)
- [D:\code\MyAttention\services\api\tests\test_source_discovery_identity.py](/D:/code/MyAttention/services/api/tests/test_source_discovery_identity.py)
- [D:\code\MyAttention\services\api\tests\test_feeds_source_discovery_route.py](/D:/code/MyAttention/services/api/tests/test_feeds_source_discovery_route.py)

## Planned Change

1. recognize GitHub repo thread pages as `signal`
2. keep plain repo pages on the repository path
3. stay bounded to GitHub in this packet

## Validation

1. helper-level classification proof
2. route-level `/api/sources/discover` proof
3. focused regression run on current source-discovery slices

## Truth Boundary

This slice does not claim generalized forge intelligence.

It only claims that bounded GitHub repo thread pages are more useful as
`signal` than as flat repo/root objects inside the current discovery path.
