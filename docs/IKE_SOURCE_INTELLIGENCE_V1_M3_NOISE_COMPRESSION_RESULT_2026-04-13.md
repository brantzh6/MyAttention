# IKE Source Intelligence V1 - M3 Noise Compression Result

Date: 2026-04-13
Phase: `M3 Same-Source Generic-Domain Compression Heuristic`
Status: `materially_landed`

## Scope

Compress one bounded same-source source-discovery noise pattern without adding new API
surface or widening into a ranking redesign.

## Conclusion

`Source Intelligence V1` now suppresses one redundant same-source pattern in
the current discovery path:

1. a generic `domain` candidate such as `github.com`
2. a stronger specific candidate from the same source such as
   `github.com/openclaw/openclaw`

When the specific candidate is already materially competitive, the generic
domain entry is removed from the discovery candidate set. When the specific
candidate is clearly weaker, the generic domain remains.

## What Was Added

- one narrow compression helper in
  [D:\code\MyAttention\services\api\routers\feeds.py](/D:/code/MyAttention/services/api/routers/feeds.py)
- focused helper proof in
  [D:\code\MyAttention\services\api\tests\test_source_discovery_identity.py](/D:/code/MyAttention/services/api/tests/test_source_discovery_identity.py)
- focused route proof in
  [D:\code\MyAttention\services\api\tests\test_feeds_source_discovery_route.py](/D:/code/MyAttention/services/api/tests/test_feeds_source_discovery_route.py)

## What The Result Demonstrates

Using the existing discovery path:

1. same-source generic `domain` candidates are no longer allowed to survive by
   default when a stronger, more specific object from that same source already
   exists
2. the current implementation still keeps generic domains when there is no
   same-source specific replacement
3. the current implementation also keeps the generic domain when the specific
   candidate is present but not materially competitive
4. the change remains inside the current route and helper surface

## Validation

- `python -m unittest tests.test_source_discovery_identity tests.test_feeds_source_discovery_route tests.test_source_plan_helpers tests.test_source_discovery_contract`
- result:
  - `46 tests OK`
- `python -m py_compile D:\code\MyAttention\services\api\routers\feeds.py D:\code\MyAttention\services\api\tests\test_source_discovery_identity.py D:\code\MyAttention\services\api\tests\test_feeds_source_discovery_route.py`
- result:
  - passed

## Truth Boundary

This result does not claim:

1. research-grade source quality
2. canonical source truth
3. source-wide ranking optimality
4. cross-source identity resolution
5. generic noise elimination across all candidate families

It only claims:

- one bounded same-source generic-domain compression heuristic is now active
  inside the current discovery path

## Controller Judgment

- `accept_with_changes`

## Next Decision Edge

The next decision should not be more same-pattern generic/specific patching by
default.

It should decide whether the next bounded slice is:

1. another clearly distinct noise-compression family
2. or a quality-improvement slice with explicit value above this reduced-noise
   baseline
