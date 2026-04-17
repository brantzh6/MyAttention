# IKE Source Intelligence V1 - M6 GitHub Thread Signal Result

Date: 2026-04-14
Phase: `M6 GitHub Repo Thread Signal Classification`
Status: `materially_landed`

## Scope

Improve one bounded source-quality family inside the current discovery path
without widening into a broad collaboration-platform ontology.

## Conclusion

`Source Intelligence V1` now classifies bounded GitHub repo thread pages such
as issues, discussions, and pull requests as `signal` rather than collapsing
them into a plain repo/root object.

## What Was Added

- one narrow GitHub repo-thread classifier in
  [D:\code\MyAttention\services\api\routers\feeds.py](/D:/code/MyAttention/services/api/routers/feeds.py)
- focused helper proof in
  [D:\code\MyAttention\services\api\tests\test_source_discovery_identity.py](/D:/code/MyAttention/services/api/tests/test_source_discovery_identity.py)
- focused route proof in
  [D:\code\MyAttention\services\api\tests\test_feeds_source_discovery_route.py](/D:/code/MyAttention/services/api/tests/test_feeds_source_discovery_route.py)

## What The Result Demonstrates

Using the existing discovery path:

1. GitHub issue pages can now become `signal`
2. GitHub discussion pages can now become `signal`
3. plain repository pages remain on the repository path
4. the change remains inside the current helper and route surface

## Validation

- `python -m unittest tests.test_source_discovery_identity tests.test_feeds_source_discovery_route tests.test_source_plan_helpers tests.test_source_discovery_contract tests.test_attention_policy_foundation`
- result:
  - `68 tests OK`
- `python -m py_compile D:\code\MyAttention\services\api\routers\feeds.py D:\code\MyAttention\services\api\tests\test_source_discovery_identity.py D:\code\MyAttention\services\api\tests\test_feeds_source_discovery_route.py`
- result:
  - passed

## Truth Boundary

This result does not claim:

1. generalized collaboration-platform ontology
2. GitLab / Jira / forum coverage
3. workflow-state intelligence
4. research-grade source quality

It only claims:

- one bounded GitHub repo-thread family is now classified more usefully as
  `signal`

## Controller Judgment

- `accept_with_changes`

## Next Decision Edge

The next slice should not continue patching GitHub page families by default.

It should choose:

1. one clearly distinct quality/noise family
2. or one higher-value move above the current improved object-quality baseline
