# IKE Source Intelligence V1 M1 Landing Decision

Date: 2026-04-11
Status: controller landing decision

## Purpose

Fix the preferred implementation landing area for `Source Intelligence V1 M1`.

## Current Code Reality

The project already has material source-intelligence code inside:

- [D:\code\MyAttention\services\api\routers\feeds.py](/D:/code/MyAttention/services/api/routers/feeds.py)

This file already contains:

- `SourceDiscoveryFocus`
- `SourceDiscoveryRequest`
- `SourceDiscoveryCandidate`
- `SourceDiscoveryResponse`
- `_candidate_identity`
- `_discovery_queries`
- `_execution_strategy_for_candidate`
- `_review_cadence_for_candidate`
- `POST /sources/discover`
- `POST /sources/plans`
- source-plan refresh/version helpers

## Controller Decision

`Source Intelligence V1 M1` should prefer extending or tightening the existing
`feeds.py` source-discovery/source-plan path.

It should not start by introducing a parallel source-intelligence subsystem in
a disconnected new location unless a very small extraction is clearly needed.

## Why

This is the safer choice because:

1. the project already has working source-discovery semantics
2. tests already exist around discovery identity and source-plan helpers
3. a second parallel implementation would create semantic drift immediately
4. M1 needs bounded activation, not a framework rewrite

## Preferred Shape

Best-first options, in order:

1. narrow enhancement of the existing `discover` / source-plan pathway
2. small helper extraction from `feeds.py` if needed for testability
3. focused router/response adjustment

Avoid:

- creating a second top-level `source_intelligence` stack with duplicated
  models and routing
- broad DB/schema expansion first
- UI-first implementation

## Recommendation

`accept`

The first M1 coding lane should land against the existing
source-discovery/source-plan path, not create a separate competing stack.
