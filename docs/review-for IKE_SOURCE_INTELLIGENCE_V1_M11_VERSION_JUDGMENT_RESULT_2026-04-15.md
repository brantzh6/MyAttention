# Review Request: IKE Source Intelligence V1 M11 Version Judgment Result

Please review this bounded packet.

## Scope

Review only:

- `services/api/routers/feeds.py`
- `services/api/tests/test_source_plan_versioning_helpers.py`
- `services/api/tests/test_feeds_source_discovery_route.py`
- `docs/IKE_SOURCE_INTELLIGENCE_V1_M11_VERSION_JUDGMENT_RESULT_2026-04-15.md`

## What Changed

This packet adds one inspect-only route:

- `POST /api/sources/plans/{plan_id}/versions/{version_number}/judge/inspect`

The route reuses the internal AI judgment substrate on top of bounded
source-plan version change targets.

## Review Questions

1. Is the claim boundary honest?
2. Does this prove a second distinct substrate use case without widening into workflow?
3. Are the request/response semantics still inspect-only and non-mutating?
4. Is target extraction bounded and coherent?
5. Are the focused tests sufficient for this slice?

## Response Format

Please return:

- verdict: `accept`, `accept_with_changes`, or `reject`
- findings
- risks
- whether this slice should stop here or immediately continue
