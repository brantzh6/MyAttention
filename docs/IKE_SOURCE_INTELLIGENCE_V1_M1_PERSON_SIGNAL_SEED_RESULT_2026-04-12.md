# IKE Source Intelligence V1 M1 Person Signal Seed Result

Date: 2026-04-12
Status: bounded controller-coded slice

## Purpose

Move `Source Intelligence V1 M1` back from read-surface realism closure into a
small but real discovery-quality improvement.

This slice improves `person/object discovery quality` on the existing
source-discovery path by allowing social `signal` results to seed bounded
`person` candidates, instead of only remaining discussion-like signal entries.

## Files Changed

- [D:\code\MyAttention\services\api\routers\feeds.py](/D:/code/MyAttention/services/api/routers/feeds.py)
- [D:\code\MyAttention\services\api\tests\test_source_discovery_identity.py](/D:/code/MyAttention/services/api/tests/test_source_discovery_identity.py)
- [D:\code\MyAttention\services\api\tests\test_feeds_source_discovery_route.py](/D:/code/MyAttention/services/api/tests/test_feeds_source_discovery_route.py)

## What Changed

### Added person relation hints for social status signals

`_candidate_relation_hints(...)` now emits a related `person` hint when the
current candidate is an `x.com` or `twitter.com` status signal.

Example:

- `x.com/openclaw/status/123456`
  now also seeds
- `x.com/openclaw`

### Added bounded role/follow signal for author-derived person seeds

`_build_related_candidate_seed(...)` now gives `author`-relation person seeds a
conservative `builder` inferred role and a modest follow-score boost.

This is intentionally weaker than the existing `owner -> maintainer` path.

### Preserved parent-signal truthfulness

Author-derived person seeds now retain their parent relation as `signal` in
`related_entities`, instead of flattening the parent into a misleading `domain`
type.

### Covered both `x.com` and `twitter.com` status paths

The seeding path is now proven on both supported social-status URL families.

## Why It Matters

Before this change, a maintainer or builder speaking through a social status
signal would usually remain visible only as a `signal` plus a generic
source-stream relation.

After this change, the same evidence can also surface the actor behind the
signal as a bounded `person` candidate, which is closer to the declared M1 need
to improve `person/object discovery quality`.

## Validation Run

- `python -m unittest tests.test_source_discovery_identity tests.test_source_discovery_contract tests.test_feeds_source_discovery_route tests.test_source_plan_helpers tests.test_source_plan_versioning_helpers`
- `python -m py_compile D:\code\MyAttention\services\api\routers\feeds.py D:\code\MyAttention\services\api\tests\test_source_discovery_identity.py D:\code\MyAttention\services\api\tests\test_feeds_source_discovery_route.py`

Validation result:

- `45 tests OK`
- compile passed

## Truth Boundary

- this improves candidate seeding on the existing discovery path only
- this does not add a new discovery API surface
- this does not prove person discovery is now research-grade
- this does not add cross-source identity resolution
- `x.com/{handle}` or `twitter.com/{handle}` remains a source-local person seed,
  not a canonical cross-source identity
- `author -> builder` is only a conservative focus-bounded heuristic, not a
  maintainer or owner claim
- this does not change top-level source-intelligence strategy

## Recommendation

- `accept_with_changes`
