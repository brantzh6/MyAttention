# IKE Source Intelligence V1 - M3 Plan

Date: 2026-04-13
Phase: `M3 Same-Source Generic-Domain Compression Heuristic`
Status: `active`

## Scope

Only compress one obvious same-source noise family inside the current discovery path:

- generic `domain`
- stronger specific object from the same canonical source

## Write Surface

- [D:\code\MyAttention\services\api\routers\feeds.py](/D:/code/MyAttention/services/api/routers/feeds.py)
- [D:\code\MyAttention\services\api\tests\test_source_discovery_identity.py](/D:/code/MyAttention/services/api/tests/test_source_discovery_identity.py)
- [D:\code\MyAttention\services\api\tests\test_feeds_source_discovery_route.py](/D:/code/MyAttention/services/api/tests/test_feeds_source_discovery_route.py)

## Planned Change

1. add one narrow compression helper after candidate scoring and before final
   candidate shaping
2. drop generic `domain` candidates only when:
   - they share the same canonical source-domain as a more specific candidate
   - the more specific candidate is already materially competitive
3. explicitly keep the generic `domain` when the specific candidate is present
   but not materially competitive
4. keep the rule bounded to the active discovery focuses rather than broadening
   into authoritative-source redesign

## Validation

1. helper-level focused tests
2. route-level focused test on `/api/sources/discover`
3. no new API surface

## Truth Boundary

This slice does not claim that the project now has research-grade ranking.

It only claims that one bounded same-source generic-domain compression
heuristic is now active inside the existing discovery path.
