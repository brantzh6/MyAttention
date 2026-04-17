# IKE Source Intelligence V1 - M4 Release-Over-Repository Result

Date: 2026-04-13
Phase: `M4 Same-Repo Release Duplicate Compression In LATEST/FRONTIER`
Status: `materially_landed`

## Scope

Compress one bounded same-repo overlap pattern without widening into a general
ranking redesign.

## Conclusion

`Source Intelligence V1` now suppresses one `LATEST` / `FRONTIER` overlap pattern in the
current discovery path:

1. `repository`
2. `release`
3. same repo
4. `LATEST` or `FRONTIER`

When the `release` candidate is materially competitive, the same-repo
`repository` candidate is removed. `METHOD` remains unchanged, and weak release
candidates do not remove the repository.

## What Was Added

- one narrow overlap-compression helper in
  [D:\code\MyAttention\services\api\routers\feeds.py](/D:/code/MyAttention/services/api/routers/feeds.py)
- focused helper proof in
  [D:\code\MyAttention\services\api\tests\test_source_discovery_identity.py](/D:/code/MyAttention/services/api/tests/test_source_discovery_identity.py)
- focused route proof in
  [D:\code\MyAttention\services\api\tests\test_feeds_source_discovery_route.py](/D:/code/MyAttention/services/api/tests/test_feeds_source_discovery_route.py)

## What The Result Demonstrates

Using the existing discovery path:

1. `LATEST` and `FRONTIER` can prefer `release` over same-repo `repository`
   when release is already materially competitive
2. `METHOD` still keeps the repository baseline object
3. weak release candidates do not suppress the repository
4. the change remains inside the current helper and route surface

## Validation

- `python -m unittest tests.test_source_discovery_identity tests.test_feeds_source_discovery_route tests.test_source_plan_helpers tests.test_source_discovery_contract`
- result:
  - `50 tests OK`
- `python -m py_compile D:\code\MyAttention\services\api\routers\feeds.py D:\code\MyAttention\services\api\tests\test_source_discovery_identity.py D:\code\MyAttention\services\api\tests\test_feeds_source_discovery_route.py`
- result:
  - passed

## Truth Boundary

This result does not claim:

1. broad release ranking superiority
2. repository devaluation across all focuses
3. source-wide event/release lifecycle intelligence
4. research-grade source quality

It only claims:

- one bounded same-repo release duplicate compression heuristic is now active
  in `LATEST` / `FRONTIER` discovery focus

## Controller Judgment

- `accept_with_changes`

## Next Decision Edge

The next slice should not continue repository-vs-release patching by default.

It should choose:

1. one clearly distinct quality/noise family
2. or a higher-value quality-improvement slice above the current reduced-noise
   baseline
